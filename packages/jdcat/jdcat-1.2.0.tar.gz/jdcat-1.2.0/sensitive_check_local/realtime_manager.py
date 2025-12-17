from __future__ import annotations

"""实时管理器模块。

本模块提供"内存队列 + 定时批处理"的最小稳定实现，用于实时数据处理和批量转发。

主要功能：
- 提供基于 collections.deque 的内存队列，具备 ring buffer 行为（队列满时淘汰最旧元素）
- 实现标准元素映射，将通知数据转换为统一格式
- 提供完整的队列操作API：初始化、入队、出队、批量处理、清空和统计
- 支持协程安全的并发操作，保证队列操作的原子性

技术特点：
- 使用 asyncio.Lock 保证队列操作的原子性和并发安全
- 提供显式的队列容量控制和溢出处理机制
- 实现统一的数据格式转换和编码处理
- 严格遵循最小可用原则，避免过度兜底

配置约束：
- 默认参数来源于 config.load_config() 的 realtime.* 字段
- 字段命名统一使用驼峰格式
- 队列容量默认为1000，可通过配置调整
"""

import time
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from collections import deque
from urllib.parse import urlparse
import json

# 全局 ring buffer 队列（不使用 maxlen，避免隐式丢弃；显式使用 popleft 计数与日志）
_queue: deque[Dict[str, Any]] | None = None
_max_queue_size: int = 1000

# 统计
_enqueue_count: int = 0
_discard_count: int = 0

# 原子性锁：入队/出队/清空等变更操作需要在同一协程锁内保证 FIFO 丢弃与追加的原子性
_queue_lock = asyncio.Lock()

# 模块级 logger
_logger = logging.getLogger("sensitive_check_local.realtime_manager")

# 文本长度上限（旧逻辑使用，敏感上报改造后不再用于截断原文）
TEXT_LIMIT = 64 * 1024

def safe_to_text(v: Any, limit: int = TEXT_LIMIT) -> str:
    """
    安全转换为文本：
    - None → ""
    - bytes → utf-8（失败则 replace）
    - 非字符串 → str(v)
    - 最终按 limit 截断
    """
    try:
        if v is None:
            s = ""
        elif isinstance(v, bytes):
            try:
                s = v.decode("utf-8", errors="replace")
            except Exception:
                s = str(v)
        elif isinstance(v, str):
            s = v
        else:
            s = str(v)
        return s[:limit] if len(s) > limit else s
    except Exception:
        return ""

def to_str_no_limit(v: Any) -> str:
    """
    安全转换为字符串（不截断）：
    - None → ""
    - bytes → utf-8（失败则 replace）
    - 其他 → str(v)
    """
    try:
        if v is None:
            return ""
        if isinstance(v, bytes):
            try:
                return v.decode("utf-8", errors="replace")
            except Exception:
                return str(v)
        if isinstance(v, str):
            return v
        return str(v)
    except Exception:
        return ""

def try_b64_to_utf8(s: Any, limit: int = TEXT_LIMIT) -> str:
    """
    内部尝试从 base64 恢复 UTF-8 文本；失败返回空串。
    仅用于“从 base64 恢复文本”，不保留/传输 base64。
    """
    if s is None:
        return ""
    try:
        import base64
        raw = str(s)
        decoded = base64.b64decode(raw, validate=False)
        text = decoded.decode("utf-8", errors="replace")
        return text[:limit] if len(text) > limit else text
    except Exception:
        return ""

def try_b64_to_utf8_no_limit(s: Any) -> str:
    """
    从 base64 恢复 UTF-8 文本（不截断）；失败返回空串。
    """
    if s is None:
        return ""
    try:
        import base64
        raw = str(s)
        decoded = base64.b64decode(raw, validate=False)
        return decoded.decode("utf-8", errors="replace")
    except Exception:
        return ""

def pretty_json_maybe(s: str, limit: int = TEXT_LIMIT) -> str:
    """
    尝试 JSON pretty；失败则返回原文本（均按 limit 截断）
    """
    txt = safe_to_text(s, limit=limit)
    try:
        import json
        obj = json.loads(txt)
        pretty = json.dumps(obj, ensure_ascii=False, indent=2)
        return pretty[:limit] if len(pretty) > limit else pretty
    except Exception:
        return txt[:limit] if len(txt) > limit else txt

def detect_content_type(headers: Dict[str, Any]) -> str:
    """
    从 headers 中提取 Content-Type（大小写不敏感），返回标准化的小写字符串；缺省返回空串。
    """
    try:
        if not isinstance(headers, dict):
            return ""
        for k, v in headers.items():
            if str(k).lower().strip() == "content-type":
                return str(v or "").lower().strip()
        return ""
    except Exception:
        return ""

def classify_content_type(ct: str) -> str:
    """
    按约定分类 Content-Type：json/form/text/multipart/binary/unknown
    """
    s = (ct or "").lower().strip()
    if not s:
        return "unknown"
    if "application/json" in s:
        return "json"
    if "application/x-www-form-urlencoded" in s:
        return "form"
    if s.startswith("text/"):
        return "text"
    if "multipart/form-data" in s:
        return "multipart"
    if "application/octet-stream" in s:
        return "binary"
    # 其它常见可视为文本的类型（如 xml、csv）
    if "application/xml" in s or "text/xml" in s or "text/csv" in s:
        return "text"
    return "unknown"

def extract_body_fields(
    text_src: Any,
    b64_src: Any,
    headers: Dict[str, Any]
) -> Tuple[str, str, str]:
    """
    根据 Content-Type 提取原文：优先原始文本；必要时从 base64 恢复；失败则以 base64 上报。
    返回 (body_text, body_base64, encoding_label)，其中 encoding_label ∈ {"utf8", "base64"}
    不进行任何长度截断。
    """
    ct = classify_content_type(detect_content_type(headers))
    text_raw = to_str_no_limit(text_src)
    b64_raw = to_str_no_limit(b64_src)

    # 文本型：直接使用文本；若文本缺失则尝试从base64恢复
    if ct in ("json", "form", "text"):
        if text_raw:
            return text_raw, "", "utf8"
        # 文本缺失：尝试恢复
        recovered = try_b64_to_utf8_no_limit(b64_raw)
        if recovered:
            return recovered, "", "utf8"
        # 恢复失败：以base64上报
        return "", b64_raw, "base64"

    # 非文本型（multipart/binary/unknown）：尝试恢复为utf8，否则base64
    if text_raw:
        # 某些源可能仍提供文本，尊重原文
        return text_raw, "", "utf8"
    recovered = try_b64_to_utf8_no_limit(b64_raw)
    if recovered:
        return recovered, "", "utf8"
    return "", b64_raw, "base64"

def fix_headers_field(raw: Any) -> Dict[str, Any]:
    """
    将 headers 字段稳健规范为字典对象。
    - raw 为 dict：返回其浅拷贝（或原对象）
    - raw 为字符串：尝试 json.loads；若结果为 dict 返回，否则返回 {}
    - raw 为 None、list、数值或其它类型：返回 {}
    - 捕获 JSONDecodeError，回退 {}
    日志：
    - 仅输出类型信息（DEBUG），不输出任何 headers 明文内容与值。
      示例：fix_headers_field: input_type=<type> output_is_dict=<bool>
    """
    result: Dict[str, Any] = {}
    try:
        if isinstance(raw, dict):
            # 保持原对象或浅拷贝，避免副作用
            result = dict(raw)
        elif isinstance(raw, str):
            try:
                obj = json.loads(raw) if raw.strip() else {}
                result = obj if isinstance(obj, dict) else {}
            except json.JSONDecodeError:
                result = {}
        else:
            result = {}
    except Exception:
        result = {}
    try:
        _logger.debug("fix_headers_field: input_type=%s output_is_dict=%s", type(raw).__name__, isinstance(result, dict))
    except Exception:
        pass
    return result
def _now_ms() -> int:
    return int(time.time() * 1000)

def _safe_int(v: Any, default: int) -> int:
    try:
        return int(v)
    except Exception:
        return default

def _extract_domain_path(url: str) -> Tuple[str, str]:
    try:
        p = urlparse(url or "")
        domain = p.netloc or ""
        path = p.path or "/"
        return domain, path
    except Exception:
        return "", ""

def _has_internal_header(headers: Dict[str, Any]) -> bool:
    """
    检测是否存在内部回放标记头（大小写不敏感）
    - 仅判断是否存在 'x-ss-internal' 头即可视为内部；值不强校验
    - 可选地校验值等于 'permission-test'，但不影响最终 present 判定
    """
    try:
        if not isinstance(headers, dict):
            return False
        keys = {str(k).lower().strip() for k in headers.keys() if str(k).strip()}
        if "x-ss-internal" in keys:
            # 可选校验值（不影响 present 判定）
            try:
                v = headers.get("X-SS-Internal", headers.get("x-ss-internal", headers.get("X-ss-internal")))
                if isinstance(v, (list, tuple)):
                    v0 = (str(v[0]).strip().lower() if v else "")
                else:
                    v0 = (str(v).strip().lower() if v is not None else "")
                _ = (v0 == "permission-test")  # 不使用该值，仅保证兼容
            except Exception:
                pass
            return True
        return False
    except Exception:
        return False

def init_from_config(cfg: Dict[str, Any] | None) -> None:
    """从配置初始化内存队列。
    
    根据传入的配置对象初始化或重置内存队列的容量。如果队列已存在，
    会保留尽可能多的最新元素，并在必要时丢弃最旧的元素。
    
    参数:
        cfg: 包含队列配置的字典对象，结构为 {"realtime": {"maxQueueSize": int}}
             如果为 None 或不包含必要配置，则使用默认值 1000
    
    返回:
        None
    
    行为:
        - 首次调用时创建新队列
        - 重复调用时根据新容量重建队列
        - 容量变更时保留最新的元素，丢弃最旧的元素
        - 无效配置时使用默认值 1000
    """
    global _queue, _max_queue_size
    max_size = 1000
    try:
        rt = (cfg or {}).get("realtime") or {}
        max_size = _safe_int(rt.get("maxQueueSize"), 1000)
    except Exception:
        max_size = 1000
    if max_size <= 0:
        max_size = 1000

    if _queue is None:
        # 初始化为普通 deque（不设置 maxlen），由 enqueue 显式控制丢弃与计数
        _queue = deque()
        _max_queue_size = max_size
        return

    if _max_queue_size == max_size:
        return

    # 需要重建不同容量的 deque，尽可能保留新容量范围内的最新元素
    old = list(_queue)
    new_q: deque[Dict[str, Any]] = deque()
    # 取末尾最近的 max_size 个
    kept = old[-max_size:] if len(old) > max_size else old
    for x in kept:
        new_q.append(x)

    _queue = new_q
    _max_queue_size = max_size

async def enqueue(item: Dict[str, Any]) -> bool:
    """将元素添加到内存队列中。
    
    将标准化元素添加到队列尾部，当队列已满时自动丢弃最旧元素（FIFO）。
    使用协程锁确保队列操作的原子性，防止并发访问导致的竞争问题。
    
    参数:
        item: 要入队的元素字典，必须包含标准字段。如果元素中缺少 occurMs 字段，
              会自动添加当前时间戳作为该字段的值。
    
    返回:
        bool: 入队成功返回 True，失败返回 False
    
    行为:
        - 队列满时自动丢弃最旧元素并记录警告日志
        - 自动补充或规范化 occurMs 字段（保证为整数类型）
        - 使用协程锁保证"丢弃+追加"操作的原子性
        - 入队成功时递增 _enqueue_count 计数器
    
    异常:
        - 捕获所有异常并返回 False，不中断服务
    """
    global _queue, _enqueue_count, _discard_count
    if _queue is None:
        # 惰性初始化为默认大小（不使用 maxlen）
        _queue = deque()
    try:
        async with _queue_lock:
            if len(_queue) >= (_max_queue_size or 1000):
                # 显式丢弃队头（最旧）
                try:
                    _queue.popleft()
                except Exception:
                    # 在异常情况下（理论上不应发生），继续入队以保证最小可用
                    pass
                _discard_count += 1
                # 每次丢弃打印 warn 日志
                try:
                    _logger.warning("RealtimeQueue overflow: size=%d, discardCount=%d", len(_queue), _discard_count)
                except Exception:
                    pass
            # occurMs 补齐：在入队临界区内完成，保证"填充+入队"一体化
            # 修复：优先保留原有occurMs，仅在缺失时补齐，确保幂等机制正常工作
            try:
                occ_raw = item.get("occurMs")
                # 支持字符串和数字类型的occurMs
                if occ_raw is not None and str(occ_raw).strip():
                    occ_int = int(occ_raw) if isinstance(occ_raw, (int, float)) else int(str(occ_raw).strip())
                else:
                    occ_int = 0
            except Exception:
                occ_int = 0
            if occ_int <= 0:
                occ_int = _now_ms()
                try:
                    item["occurMs"] = int(occ_int)
                    _logger.debug("[realtime-manager] occurMs generated: flowId=%s occurMs=%d", item.get("flowId"), occ_int)
                except Exception:
                    # 兜底：若赋值异常，不阻塞入队
                    pass
            else:
                try:
                    # 确保occurMs为整数类型
                    item["occurMs"] = int(occ_int)
                    _logger.debug("[realtime-manager] occurMs preserved: flowId=%s occurMs=%d", item.get("flowId"), occ_int)
                except Exception:
                    pass
            _queue.append(item)
            _enqueue_count += 1
        return True
    except Exception:
        return False

def size() -> int:
    """获取当前队列元素数量（非协程安全）。
    
    返回:
        int: 当前队列中的元素数量，队列不存在时返回0
    
    注意:
        此函数不使用协程锁，在并发环境下可能不准确，
        仅用于简单状态检查。生产环境应使用 get_queue_size()。
    """
    try:
        return len(_queue) if _queue is not None else 0
    except Exception:
        return 0

async def get_queue_size() -> int:
    """获取当前队列元素数量（协程安全）。
    
    以协程安全的方式获取当前队列中的元素数量，使用协程锁
    确保在并发环境下读取的准确性。
    
    返回:
        int: 当前队列中的元素数量，队列不存在时返回0
    
    异常:
        捕获所有异常并返回0，不中断服务
    """
    try:
        async with _queue_lock:
            return len(_queue) if _queue is not None else 0
    except Exception:
        return 0

async def get_discard_count() -> int:
    """协程安全只读：累计丢弃数量"""
    try:
        # 只读统计无需持锁，但为避免读写竞争，这里保持与其他操作一致
        async with _queue_lock:
            return int(_discard_count)
    except Exception:
        return int(_discard_count)

async def pop_batch(n: int) -> List[Dict[str, Any]]:
    """批量弹出队列元素（协程安全）。
    
    以先进先出（FIFO）的顺序从队列中弹出最多 n 个元素。
    使用协程锁确保与入队/清空操作的原子性，防止并发访问导致的竞争问题。
    
    参数:
        n: 要弹出的最大元素数量，如果 n<=0 则返回空列表
    
    返回:
        List[Dict[str, Any]]: 弹出的元素列表，按照队列顺序排列（最早入队的元素在前）
    
    行为:
        - 使用协程锁保证操作的原子性
        - 弹出的元素数量为 min(n, 当前队列长度)
        - 队列为空或 n<=0 时返回空列表
    
    异常:
        - 捕获所有异常并尽力返回已弹出的部分元素，不中断服务
    """
    global _queue
    if _queue is None or n <= 0:
        return []
    out: List[Dict[str, Any]] = []
    try:
        async with _queue_lock:
            m = min(n, len(_queue))
            for _ in range(m):
                out.append(_queue.popleft())
    except Exception:
        # 如果期间发生异常，尽力返回已弹出的部分
        pass
    return out

async def flush_all() -> List[Dict[str, Any]]:
    """清空队列并返回所有元素（协程安全）。
    
    弹出并返回队列中的所有剩余元素，同时清空队列。
    使用协程锁确保与入队/出队操作的原子性，防止并发访问导致的竞争问题。
    
    返回:
        List[Dict[str, Any]]: 队列中所有元素的列表，按照队列顺序排列（最早入队的元素在前）
                             如果队列为空或不存在，则返回空列表
    
    行为:
        - 使用协程锁保证操作的原子性
        - 清空队列并返回所有元素
        - 队列为空或不存在时返回空列表
    
    异常:
        - 捕获所有异常并尽力返回已弹出的部分元素，不中断服务
    """
    global _queue
    if _queue is None:
        return []
    out: List[Dict[str, Any]] = []
    try:
        async with _queue_lock:
            while _queue:
                out.append(_queue.popleft())
    except Exception:
        pass
    return out

def get_discard_stats() -> Dict[str, int]:
    """获取队列统计信息（非协程安全）。
    
    返回队列的统计信息，包括入队总数、丢弃总数和最大队列容量。
    此函数主要用于兼容历史接口，新代码应优先使用 get_queue_size 和
    get_discard_count 函数获取队列状态。
    
    返回:
        Dict[str, int]: 包含以下键的字典：
            - enqueueCount: 累计入队元素总数
            - discardCount: 累计丢弃元素总数（队列满时）
            - maxQueueSize: 当前队列最大容量设置
    
    注意:
        此函数不使用协程锁，在并发环境下可能不准确。
        生产环境应优先使用 get_queue_size 和 get_discard_count。
    """
    return {"enqueueCount": _enqueue_count, "discardCount": _discard_count, "maxQueueSize": _max_queue_size}

def map_notify_to_item(body: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    将 /notify body 映射为队列元素标准结构（文本优先 + 停止 base64）
    输出字段：
    {
      flowId, sessionId, method, url, domain, path,
      requestHeaders, responseHeaders,
      requestBody, responseBody,
      responseStatus, durationMs, occurMs, meta
    }
    """
    import json

    b = body or {}
    type_str = str(b.get("type") or "").strip().lower()
    payload_obj = (b.get("payload") or {}) if isinstance(b.get("payload"), dict) else {}


    # 默认分支：兼容旧 flow 事件（保持既有逻辑不变）
    # 基本字段
    flow_id = b.get("flowId") or b.get("id") or f"local-{_now_ms()}"
    session_id = b.get("sessionId") or b.get("session_id")
    # 方法字段回退：顶层 → payload → 默认 GET
    method = b.get("method") or payload_obj.get("method") or "GET"
    # URL字段回退：顶层 → payload → 空串，并记录来源
    url_src = "top"
    url = b.get("url") or b.get("requestUrl")
    if not url:
        url = payload_obj.get("url") or payload_obj.get("requestUrl") or ""
        url_src = "payload" if url else "none"
    domain, path = _extract_domain_path(str(url))

    # headers 修复为 dict（先尽量解析，再统一规范为 dict）
    request_headers_raw = b.get("requestHeaders")
    response_headers_raw = b.get("responseHeaders")
    # 兼容 flow 事件：如 headers 位于 payload 内，则回退读取
    if not request_headers_raw:
        try:
            request_headers_raw = payload_obj.get("requestHeaders")
        except Exception:
            request_headers_raw = None
    if not response_headers_raw:
        try:
            response_headers_raw = payload_obj.get("responseHeaders")
        except Exception:
            response_headers_raw = None

    if isinstance(request_headers_raw, dict):
        request_headers = request_headers_raw
    elif isinstance(request_headers_raw, str):
        try:
            request_headers = json.loads(request_headers_raw) if request_headers_raw.strip() else {}
        except (json.JSONDecodeError, AttributeError):
            request_headers = {}
    else:
        request_headers = {}

    if isinstance(response_headers_raw, dict):
        response_headers = response_headers_raw
    elif isinstance(response_headers_raw, str):
        try:
            response_headers = json.loads(response_headers_raw) if response_headers_raw.strip() else {}
        except (json.JSONDecodeError, AttributeError):
            response_headers = {}
    else:
        response_headers = {}

    # 统一调用助手，确保为 dict
    request_headers = fix_headers_field(request_headers)
    response_headers = fix_headers_field(response_headers)

    # 原文保留（不做格式化与截断），从多源提取 + Content-Type 兜底
    req_text_src = ((b.get("request") or {}) if isinstance(b.get("request"), dict) else {}).get("text") \
        or b.get("requestBody") \
        or payload_obj.get("requestBody")
    req_b64_src = ((b.get("request") or {}) if isinstance(b.get("request"), dict) else {}).get("content") \
        or b.get("requestBodyBase64") \
        or payload_obj.get("requestBodyBase64") \
        or ""

    resp_text_src = ((b.get("response") or {}) if isinstance(b.get("response"), dict) else {}).get("text") \
        or b.get("responseBody") \
        or payload_obj.get("responseBody")
    resp_b64_src = ((b.get("response") or {}) if isinstance(b.get("response"), dict) else {}).get("content") \
        or b.get("responseBodyBase64") \
        or payload_obj.get("responseBodyBase64") \
        or ""

    rb_text, rb_b64, rb_enc = extract_body_fields(req_text_src, req_b64_src, request_headers)
    sb_text, sb_b64, sb_enc = extract_body_fields(resp_text_src, resp_b64_src, response_headers)

    # 其他数值字段
    response_status = b.get("responseStatus") or b.get("status") or payload_obj.get("status") or 200
    duration_ms = b.get("durationMs") or 0
    occur_ms = b.get("occurMs") or b.get("ts") or _now_ms()

    # meta 注入（包含 session_id 与 internal 标记）
    meta = b.get("meta") or {}
    try:
        if session_id and "session_id" not in meta:
            meta["session_id"] = session_id
    except Exception:
        pass
    try:
        internal_flag = _has_internal_header(request_headers)
        meta["internal"] = bool(internal_flag)
    except Exception:
        try:
            meta["internal"] = False
        except Exception:
            pass

    # 统一元信息日志（不打印明文，仅打印键数量）
    # 降敏摘要日志：标记 URL 来源 + 方法/域名/路径
    try:
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug("[mapping] url_src=%s method=%s domain=%s path=%s",
                         url_src, str(method or ""), str(domain or ""), str(path or ""))
    except Exception:
        pass
    try:
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug("[mapping] req_hdrs=%d resp_hdrs=%d",
                         (len(request_headers) if isinstance(request_headers, dict) else 0),
                         (len(response_headers) if isinstance(response_headers, dict) else 0))
    except Exception:
        pass

    # 解析 query
    try:
        from urllib.parse import urlparse
        _p = urlparse(str(url or ""))
        query = _p.query or ""
    except Exception:
        query = ""

    # 标准 item（保留原文 + 可选 base64）
    item = {
        "flowId": flow_id,
        "sessionId": session_id,
        "method": method,
        "url": url,
        "domain": domain,
        "path": path,
        "requestHeaders": fix_headers_field(request_headers),
        "responseHeaders": fix_headers_field(response_headers),
        "requestBody": rb_text,
        "requestBodyBase64": rb_b64,
        "responseBody": sb_text,
        "responseBodyBase64": sb_b64,
        "responseStatus": response_status,
        "durationMs": duration_ms,
        "occurMs": occur_ms,
        "query": query,
        "meta": meta,
        "encoding": {"request": rb_enc, "response": sb_enc},
    }
    return item
