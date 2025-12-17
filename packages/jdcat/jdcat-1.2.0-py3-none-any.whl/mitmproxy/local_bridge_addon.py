# -*- coding: utf-8 -*-
"""
Mitmproxy local bridge addon (minimal, non-blocking local notify + optional upload)

Features (Phase B.2 + C.1 minimal loop):
- On each captured flow (response event), immediately POST a lightweight local notify to LOCAL_NOTIFY_URL (/notify).
  Payload: { flowId, method, url, status, sessionId?, ts }
- After upload to remote ingest finishes (single or batch-like with array of one), POST a local notify with type=upload
  Payload: { flowId, uploaded: true/false, error?: string }

Notes:
- This file intentionally keeps event body small to reduce overhead.
- All local notify errors are ignored (debug print only); they must not block capture or remote ingest.
- Non-blocking by ThreadPoolExecutor to avoid mitmproxy main loop blocking.

Environment variables:
- LOCAL_NOTIFY_URL: e.g., http://127.0.0.1:17866/notify
- INGEST_URL: remote ingest endpoint (e.g., http://localhost:8008/api/traffic/ingest/batch)
- INGEST_KEY: API key for remote ingest (X-INGEST-KEY)
- SESSION_ID: optional current capture session id for tagging

Usage:
  mitmdump -s sensitive-check-local/mitmproxy/local_bridge_addon.py --ssl-insecure -p 8080
"""

import os
import json
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional
from collections import OrderedDict
import hashlib
import base64
from urllib.parse import urlsplit, parse_qsl, urlencode

# Avoid heavy deps: use standard library HTTP client
import urllib.request
import urllib.error

try:
    from mitmproxy import http  # type: ignore
except Exception:  # pragma: no cover
    http = None  # allow basic import check outside mitmproxy runtime

# optional toml reader for config toggle (py3.11+)
try:
    import tomllib as _tomli  # type: ignore
except Exception:  # pragma: no cover
    _tomli = None  # fallback to env only


# ---- Dedup configuration ----
TTL_SECONDS = int(os.getenv("DEDUP_TTL_SECONDS", "60"))
MAX_ENTRIES = int(os.getenv("DEDUP_MAX_ENTRIES", "10000"))


class DedupStore:
    """
    Per-session LRU + TTL store.
    Key: signature string (hash)
    Value: last-seen timestamp (seconds)
    """
    def __init__(self, max_entries: int = MAX_ENTRIES, ttl_seconds: int = TTL_SECONDS) -> None:
        self.max_entries = int(max_entries)
        self.ttl_seconds = int(ttl_seconds)
        self._data: "OrderedDict[str, float]" = OrderedDict()
        self._lock = threading.Lock()

    def _evict_expired_unlocked(self, now: float) -> None:
        ttl = float(self.ttl_seconds)
        # Fast path: pop from oldest while expired
        keys_to_delete = []
        for k, ts in list(self._data.items()):
            if now - ts > ttl:
                keys_to_delete.append(k)
            else:
                # OrderedDict: once we hit a fresh one, break to keep O(k) where k=expired prefix
                break
        for k in keys_to_delete:
            self._data.pop(k, None)

    def seen_or_add(self, key: str) -> bool:
        """
        Atomically check-then-record.
        Returns True if this key was seen within TTL (skip), else False and record it.
        """
        now = time.time()
        with self._lock:
            # prune expired
            self._evict_expired_unlocked(now)
            # hit?
            if key in self._data:
                ts = self._data.get(key, 0.0)
                if now - ts <= self.ttl_seconds:
                    # hit within TTL -> move to end as MRU and return hit
                    try:
                        self._data.move_to_end(key)
                    except Exception:
                        pass
                    self._data[key] = now
                    return True
                else:
                    # expired -> treat as miss, overwrite timestamp
                    try:
                        self._data.pop(key, None)
                    except Exception:
                        pass
            # capacity guard
            while len(self._data) >= self.max_entries:
                try:
                    self._data.popitem(last=False)
                except Exception:
                    break
            self._data[key] = now
            return False


def _http_post_json(url: str, data: Any, timeout: float = 2.0, headers: Optional[Dict[str, str]] = None) -> tuple[int, str]:
    """
    发送 JSON 格式的 HTTP POST 请求并处理响应。
    
    功能特点：
    - 使用标准库 urllib 实现，避免引入外部依赖
    - 自动将数据序列化为 JSON 并设置正确的 Content-Type
    - 支持自定义请求头，用于身份认证和数据隔离
    - 统一的错误处理和响应解析
    
    请求处理：
    - 将输入数据序列化为 JSON 并编码为 UTF-8 字节
    - 设置 Content-Type: application/json 请求头
    - 应用所有自定义请求头（如有）
    - 设置超时保护，避免长时间阻塞
    
    响应处理：
    - 读取响应体并尝试解码为 UTF-8 文本
    - 提取 HTTP 状态码，默认为 200
    - 返回状态码和响应文本的元组
    
    错误处理：
    - 捕获 HTTP 错误并尝试读取错误响应体
    - 将 HTTP 错误转换为 RuntimeError，包含状态码和错误文本
    - 确保错误信息包含足够的上下文用于调试
    
    参数:
        url: 目标 URL
        data: 要发送的数据对象，将被序列化为 JSON
        timeout: 请求超时时间（秒），默认 2.0 秒
        headers: 可选的自定义请求头字典
        
    返回:
        包含 (状态码, 响应文本) 的元组
        
    异常:
        RuntimeError: 当 HTTP 请求失败时，包含状态码和错误响应
    """
    req = urllib.request.Request(url, method="POST")
    body = json.dumps(data).encode("utf-8")
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, body, timeout=timeout) as resp:
            b = resp.read()
            body_txt = b.decode("utf-8", errors="ignore") if isinstance(b, (bytes, bytearray)) else str(b)
            return getattr(resp, "status", 200), body_txt
    except urllib.error.HTTPError as e:
        try:
            eb = e.read()
            err_txt = eb.decode("utf-8", errors="ignore") if isinstance(eb, (bytes, bytearray)) else str(eb)
        except Exception:
            err_txt = str(e)
        # propagate with status and body for observability
        raise RuntimeError(f"http {getattr(e, 'code', 500)} {err_txt}")


class LocalNotifier:
    def __init__(self) -> None:
        self.url = os.getenv("LOCAL_NOTIFY_URL", "").strip()
        self.enabled = bool(self.url)
        # small pool; minimize thread overhead
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="local-notify")

    def notify(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        异步发送事件通知到本地服务，采用非阻塞策略确保不影响主流程。
        
        事件结构设计：
        - 统一包装为 {"type": event_type, "payload": payload} 格式
        - 支持多种事件类型：flow（基础流量）、flow_ext（增强流量）、upload（上传结果）
        
        异步策略：
        - 使用 ThreadPoolExecutor 实现异步处理，避免阻塞 mitmproxy 主循环
        - 采用 fire-and-forget 模式，不等待响应结果
        - 线程池大小固定为 2，减少资源开销
        
        错误处理：
        - 所有通知错误被捕获并仅打印调试信息，绝不抛出异常
        - 通知失败不会影响后续流程，确保核心捕获和上传功能不受影响
        - 即使本地服务不可用，也不会阻断主流程
        
        参数:
            event_type: 事件类型标识符，如 "flow"、"flow_ext"、"upload"
            payload: 事件负载数据，包含具体事件信息的字典
        """
        if not self.enabled:
            return
        event = {
            "type": event_type,
            "payload": payload,
        }
        # fire-and-forget
        self.executor.submit(self._send_safe, event)

    def _send_safe(self, event: Dict[str, Any]) -> None:
        """
        安全发送事件通知到本地服务，确保所有异常被捕获且不影响主流程。
        
        实现细节：
        - 使用 _http_post_json 函数发送 JSON 格式的事件数据
        - 设置较短的超时时间（1.5秒）避免长时间阻塞
        - 捕获所有可能的异常，包括网络错误、超时、服务不可用等
        
        错误处理策略：
        - 所有异常仅打印调试日志，不会抛出到上层
        - 使用统一的日志前缀 "[local_bridge]" 便于问题排查
        - 即使通知失败也不会重试，避免资源浪费和延迟累积
        
        参数:
            event: 包含 type 和 payload 的事件字典，将被序列化为 JSON 发送
        """
        try:
            _http_post_json(self.url, event, timeout=1.5)
        except Exception as e:
            # debug only; never raise
            print(f"[local_bridge] debug: local notify failed: {e}")


class RemoteIngestUploader:
    def __init__(self) -> None:
        self.url = os.getenv("INGEST_URL", "").strip()
        self.key = os.getenv("INGEST_KEY", "").strip()
        # identity for isolation & auditing
        self.user_id = os.getenv("USER_ID", "").strip()
        self.project_id = os.getenv("PROJECT_ID", "").strip()
        self.task_id = os.getenv("TASK_ID", "").strip()
        self.enabled = bool(self.url)
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="remote-ingest")
        
        # DEBUG: Enhanced logging for configuration debugging
        try:
            masked = "yes" if self.key else "no"
            print(f"[local_bridge] ingest config url={self.url} key_set={masked} user_id={self.user_id} project_id={self.project_id} task_id={self.task_id}")
        except Exception as e:
            print(f"[DEBUG] RemoteIngestUploader.__init__: logging failed: {e}")

    def upload_async(self, dto: Dict[str, Any], flow_id: str, on_done):
        """
        异步上传流量数据到远程服务，支持批量或单条上传，并通过回调通知结果。
        
        上传策略：
        - 自动检测 URL 路径决定批量或单条上传模式（URL 包含 "/batch" 则使用批量模式）
        - 批量模式下将单条数据包装为数组 [dto]，单条模式直接发送 dto
        - 使用 ThreadPoolExecutor 实现异步处理，避免阻塞主线程
        - 固定超时时间为 5 秒，平衡响应速度和可靠性
        
        身份认证与隔离：
        - 支持通过 X-INGEST-KEY 进行 API 认证
        - 自动注入身份标识头（X-USER-ID、X-PROJECT-ID、X-TASK-ID）实现数据隔离
        - 所有身份信息从环境变量获取，确保安全性和一致性
        
        回调契约：
        - 上传完成后通过 on_done(flow_id, success, error) 回调通知结果
        - 成功时 success=True, error=None
        - 失败时 success=False, error=错误信息
        - 即使远程服务未配置，也会模拟回调（success=False）确保流程完整性
        
        异常处理：
        - 捕获所有上传异常并通过回调传递错误信息
        - HTTP 错误会包含状态码和响应内容片段
        - 网络或其他异常会转换为字符串传递
        - 回调执行异常被捕获并记录，不影响主流程
        
        参数:
            dto: 要上传的数据对象
            flow_id: 流量标识符，用于关联上传结果
            on_done: 上传完成回调函数，签名为 on_done(flow_id, success, error)
        """
        if not self.enabled:
            # simulate success=false without blocking
            def _cb():
                try:
                    on_done(flow_id, False, "INGEST_URL not set")
                except Exception as e:
                    print(f"[local_bridge] debug: on_done callback error: {e}")
            self.executor.submit(_cb)
            return
        # batch if /batch in url, else single
        is_batch = "/batch" in self.url

        def _send():
            try:
                headers = {}
                if self.key:
                    headers["X-INGEST-KEY"] = self.key
                # inject identity headers if provided
                if self.user_id:
                    headers["X-USER-ID"] = self.user_id
                if self.project_id:
                    headers["X-PROJECT-ID"] = self.project_id
                if self.task_id:
                    headers["X-TASK-ID"] = self.task_id
                payload = [dto] if is_batch else dto
                status, resp_txt = _http_post_json(self.url, payload, timeout=5.0, headers=headers)
                ok = 200 <= status < 300
                err = None if ok else f"http {status} {resp_txt[:256]}"
                on_done(flow_id, ok, err)
            except Exception as e:
                on_done(flow_id, False, str(e))

        self.executor.submit(_send)


class LocalBridgeAddon:
    def __init__(self) -> None:
        self.notifier = LocalNotifier()
        self.uploader = RemoteIngestUploader()
        self.session_id = os.getenv("SESSION_ID") or None
        self.filter_xhr_only = self._load_filter_toggle()
        # dedup toggle from env (canonicalized in API/process)
        self.dedup_enabled = str(os.getenv("DEDUP", "false")).strip().lower() in ("1", "true", "yes", "on")
        # dedup mode: how to compose signature key. options:
        # - url_no_query (default): 按URL(不含query)去重 -> host+path
        # - method_host_path: 方法+主机+路径（忽略query/body）
        # - method_host_path_query: 包含规范化后的query
        # - method_host_path_body: 包含请求体hash
        # - all: 同时包含query与body
        self.dedup_mode = (os.getenv("DEDUP_MODE", "url_no_query") or "url_no_query").strip().lower()
        # domain allowlist (comma or newline separated)
        raw_targets = os.getenv("TARGET_DOMAINS", "") or ""
        self.target_domains = self._parse_targets(raw_targets)
        # optional url regex filter
        self.filter_regex = None
        try:
            import re as _re
            regex = os.getenv("FILTER_REGEX", "")
            if regex and regex.strip():
                self.filter_regex = _re.compile(regex.strip())
        except Exception:
            self.filter_regex = None
        # per-session stores
        self._dedup_stores: Dict[str, DedupStore] = {}

        # stats for observability
        self._stat_lock = threading.Lock()
        self._stat_total = 0
        self._stat_kept_api = 0
        self._stat_filtered_static = 0

        # startup log for dedup
        try:
            print(f"[local_bridge] dedup-enabled:{str(self.dedup_enabled).lower()}, mode={getattr(self, 'dedup_mode', 'url_no_query')}, sessionId={self.session_id}")
        except Exception:
            pass

        try:
            if self.target_domains:
                print(f"[local_bridge] target_domains={self.target_domains}")
            if self.filter_regex:
                print(f"[local_bridge] filter_regex set")
        except Exception:
            pass

        self._start_stat_reporter()

    # config loader: env CAPTURE_FILTER_XHR_ONLY has priority, fallback pyproject.toml, default True
    def _load_filter_toggle(self) -> bool:
        v = os.getenv("CAPTURE_FILTER_XHR_ONLY")
        if v is not None:
            return str(v).strip().lower() not in ("0", "false", "no", "off")
        # try pyproject.toml
        try:
            if _tomli is None:
                return True
            base = os.getcwd()
            pyp = os.path.join(base, "pyproject.toml")
            if not os.path.isfile(pyp):
                # try project root one level up when running under tools dir
                parent = os.path.dirname(base)
                cand = os.path.join(parent, "pyproject.toml")
                pyp = cand if os.path.isfile(cand) else pyp
            if os.path.isfile(pyp):
                with open(pyp, "rb") as f:
                    data = _tomli.load(f)
                tool = data.get("tool", {}) if isinstance(data, dict) else {}
                sec = tool.get("sensitive_check_local", {}) if isinstance(tool, dict) else {}
                val = sec.get("capture.filter_xhr_only", True)
                return bool(val)
        except Exception:
            pass
        return True

    def _get_req_header(self, flow: Any, name: str) -> Optional[str]:
        try:
            return flow.request.headers.get(name) if (flow and flow.request) else None
        except Exception:
            return None

    def _get_resp_header(self, flow: Any, name: str) -> Optional[str]:
        try:
            return flow.response.headers.get(name) if (flow and flow.response) else None
        except Exception:
            return None

    def _is_api_like(self, flow: Any, method: str, url: str) -> bool:
        xr = (self._get_req_header(flow, "x-requested-with") or "").lower() == "xmlhttprequest"
        sfm = (self._get_req_header(flow, "sec-fetch-mode") or "").lower()
        sfd = (self._get_req_header(flow, "sec-fetch-dest") or "").lower()
        accept = (self._get_req_header(flow, "accept") or "").lower()
        req_ct = (self._get_req_header(flow, "content-type") or "").lower()
        resp_ct = (self._get_resp_header(flow, "content-type") or "").lower()
        cond_fetch = (sfm in ("cors", "same-origin") and sfd == "empty")
        cond_accept_json = "application/json" in accept
        cond_req_json_method = (method.upper() in ("POST", "PUT", "PATCH")) and ("application/json" in req_ct)
        cond_resp_json = "application/json" in resp_ct
        # 任一命中则认为是API
        return xr or cond_fetch or cond_accept_json or cond_req_json_method or cond_resp_json

    def _is_static_by_url(self, url: str) -> bool:
        lower = (url or "").split("?")[0].lower()
        exts = (
            ".js", ".mjs", ".css", ".map",
            ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
            ".woff", ".woff2", ".ttf", ".eot", ".otf",
            ".mp4", ".webm", ".avi", ".mov",
            ".mp3", ".wav", ".flac",
            ".pdf", ".zip", ".rar", ".7z"
        )
        return any(lower.endswith(x) for x in exts)

    def _is_static_by_ct(self, ct: Optional[str]) -> bool:
        if not ct:
            return False
        ct = ct.lower()
        if ct.startswith("image/"):
            return True
        if ct.startswith("text/css"):
            return True
        if ct.startswith("application/javascript") or ct.startswith("text/javascript"):
            return True
        if ct.startswith("font/"):
            return True
        if ct.startswith("video/") or ct.startswith("audio/"):
            return True
        if ct.startswith("application/octet-stream"):
            return True
        return False

    def _should_keep(self, flow: Any, method: str, url: str) -> bool:
        # 先按“过滤判定”剔除静态，再按“保留判定”兜底保留 API；若两者均不命中则丢弃
        ct = self._get_resp_header(flow, "content-type")
        is_static = self._is_static_by_url(url) or self._is_static_by_ct(ct)
        if is_static:
            return False
        keep = self._is_api_like(flow, method, url)
        return bool(keep)

    # helpers: target domains parsing and match
    def _parse_targets(self, s: str) -> list[str]:
        try:
            items = []
            for line in s.replace(",", "\n").splitlines():
                v = (line or "").strip().lower()
                if v:
                    items.append(v)
            return items
        except Exception:
            return []

    def _host_in_targets(self, host: str) -> bool:
        if not self.target_domains:
            return True
        try:
            h = (host or "").strip().lower()
            if not h:
                return False
            for pat in self.target_domains:
                # suffix match (allow subdomains)
                if h == pat or h.endswith("." + pat):
                    return True
            return False
        except Exception:
            return False

    # helpers: dedup session store + signature normalization
    def _get_store(self) -> DedupStore:
        sid = self.session_id or "default"
        s = self._dedup_stores.get(sid)
        if not s:
            s = DedupStore(MAX_ENTRIES, TTL_SECONDS)
            self._dedup_stores[sid] = s
        return s

    def _norm_query(self, query: str) -> str:
        try:
            pairs = parse_qsl(query or "", keep_blank_values=True)
            pairs.sort(key=lambda kv: (kv[0], kv[1]))
            return urlencode(pairs, doseq=True)
        except Exception:
            return ""

    def _hash_bytes(self, b: bytes) -> str:
        try:
            return hashlib.sha256(b).hexdigest()
        except Exception:
            try:
                return f"len={len(b or b'')}"
            except Exception:
                return "len=?"

    def _stable_json_dumps(self, obj: Any) -> str:
        try:
            return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        except Exception:
            return ""

    def _norm_body_hash(self, flow: Any) -> str:
        try:
            req = flow.request if (flow and flow.request) else None
            if not req:
                return self._hash_bytes(b"")
            raw = getattr(req, "raw_content", None)
            if raw is None:
                try:
                    txt = req.get_text(strict=False) or ""
                    raw = txt.encode("utf-8", errors="ignore")
                except Exception:
                    raw = b""
            ct = (req.headers.get("content-type") or "").lower()
            if "application/json" in ct:
                try:
                    js = json.loads(raw.decode("utf-8", errors="ignore"))
                    s = self._stable_json_dumps(js)
                    return self._hash_bytes(s.encode("utf-8"))
                except Exception:
                    pass
            return self._hash_bytes(raw)
        except Exception:
            return self._hash_bytes(b"")

    def _make_signature_key(self, flow: Any, method: str, url: str) -> tuple[str, str, str]:  # key, METHOD, path
        try:
            parts = urlsplit(url or "")
            host = parts.netloc.lower()
            path = parts.path or "/"
            qn = self._norm_query(parts.query or "")
            m = (method or "").upper()
            bh = self._norm_body_hash(flow)
            mode = getattr(self, "dedup_mode", "url_no_query")
            if mode == "url_no_query":
                # 简化为“按URL(不含query)去重”，不考虑方法与请求体
                core = [host, path]
            elif mode == "method_host_path":
                core = [m, host, path]
            elif mode == "method_host_path_query":
                core = [m, host, path, qn]
            elif mode == "method_host_path_body":
                core = [m, host, path, bh]
            else:  # "all" 或未知 -> 最保守（包含query与body）
                core = [m, host, path, qn, bh]
            sig = "|".join(core)
            return hashlib.sha256(sig.encode("utf-8")).hexdigest(), m, path
        except Exception:
            base = f"{method}|{url}"
            return hashlib.sha256(base.encode("utf-8")).hexdigest(), (method or "").upper(), "/"

    # mitmproxy hook: called when a server response has been received
    def response(self, flow: Any) -> None:
        try:
            flow_id = str(getattr(flow, "id", "")) or self._gen_flow_id()
            method = (flow.request.method if flow and flow.request else None) or ""
            url = (flow.request.pretty_url if flow and flow.request else None) or ""
            status = flow.response.status_code if (flow and flow.response) else None
            # Extract host
            try:
                host = url.split('/')[2] if '://' in url else ''
            except Exception:
                host = ''

            # 0) Apply user target domain allowlist first
            if host and not self._host_in_targets(host):
                return

            # 0.1) optional url regex filter
            if self.filter_regex is not None:
                try:
                    if not self.filter_regex.search(url or ""):
                        return
                except Exception:
                    pass

            # Ignore noisy system domains to reduce log interference (only when not in target allowlist)
            ignore_cfg = os.getenv("IGNORE_HOST_SUFFIXES", "icloud.com,apple.com,google.com,clients.google.com,gstatic.com,googleapis.com,googleusercontent.com,cdn.apple.com,itunes.apple.com").split(',')
            if host:
                h = host.strip().lower()
                # Only consider ignoring noise when current host is NOT in user target allowlist
                if not self._host_in_targets(h):
                    for suf in [s.strip().lower() for s in ignore_cfg if s.strip()]:
                        if suf and (h.endswith(suf)):
                            return
                # also skip backend ingest self-traffic
                if (h in ("aqapi.jdtest.local:8008","localhost:8008", "127.0.0.1:8008")) and ("/api/traffic/ingest" in (url or "")):
                    return
            ts_ms = int(time.time() * 1000)

            # Stats & filtering
            ct = self._get_resp_header(flow, "content-type")
            is_static = self._is_static_by_url(url) or self._is_static_by_ct(ct)
            is_api = self._is_api_like(flow, method, url)

            with self._stat_lock:
                self._stat_total += 1

            if self.filter_xhr_only:
                if is_static:
                    with self._stat_lock:
                        self._stat_filtered_static += 1
                    return  # drop static
                if not is_api:
                    # neither matched - drop
                    return
                # kept api
                with self._stat_lock:
                    self._stat_kept_api += 1
            else:
                # no-filter mode: do not drop anything, but record counters for observability
                if is_static:
                    with self._stat_lock:
                        self._stat_filtered_static += 1
                if is_api:
                    with self._stat_lock:
                        self._stat_kept_api += 1

            # Dedup check right before notify/upload
            if self.dedup_enabled:
                try:
                    sig_key, mU, pth = self._make_signature_key(flow, method, url)
                    hit = self._get_store().seen_or_add(sig_key)
                    if hit:
                        # hit -> skip further processing
                        print(f"[local_bridge] dedup-skipped key={sig_key} method={mU} path={pth}")
                        return
                    else:
                        print(f"[local_bridge] dedup-store key={sig_key} method={mU} path={pth}")
                except Exception as _e:
                    # on any error, continue without skipping
                    print(f"[local_bridge] debug: dedup error: {_e}")

            # 1) local notify: flow (non-blocking)
            # 改为携带 headers 与文本体，方便本地服务统一“文本优先”并写入数据库
            # 注意：保持非阻塞，避免影响 mitmproxy 主循环
            try:
                # 先构造 headers
                simple_req_headers: Dict[str, str] = {}
                simple_resp_headers: Dict[str, str] = {}
                try:
                    if flow and flow.request and getattr(flow.request, "headers", None):
                        # 使用单值映射，避免依赖下方 _headers_to_dict 的局部定义顺序
                        for k in flow.request.headers.keys():
                            simple_req_headers[k] = flow.request.headers.get(k)
                except Exception:
                    simple_req_headers = {}
                try:
                    if flow and flow.response and getattr(flow.response, "headers", None):
                        for k in flow.response.headers.keys():
                            simple_resp_headers[k] = flow.response.headers.get(k)
                except Exception:
                    simple_resp_headers = {}

                # 文本体优先：尝试直接获取文本；失败时回退到原始字节的 UTF-8 忽略错误解码
                def _safe_get_text_req() -> str:
                    try:
                        if flow and flow.request:
                            txt = flow.request.get_text(strict=False)
                            if isinstance(txt, str) and txt:
                                return txt
                            raw = getattr(flow.request, "raw_content", None)
                            if isinstance(raw, (bytes, bytearray)):
                                return raw.decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                    return ""

                def _safe_get_text_resp() -> str:
                    try:
                        if flow and flow.response:
                            txt = flow.response.get_text(strict=False)
                            if isinstance(txt, str) and txt:
                                return txt
                            raw = getattr(flow.response, "raw_content", None)
                            if isinstance(raw, (bytes, bytearray)):
                                return raw.decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                    return ""

                req_txt = _safe_get_text_req()
                resp_txt = _safe_get_text_resp()

                self.notifier.notify(
                    "flow",
                    {
                        "flowId": flow_id,
                        "method": method,
                        "url": url,
                        "status": status if status is not None else -1,
                        "sessionId": self.session_id,
                        "ts": ts_ms,
                        # 额外增强字段：headers 与文本体
                        "requestHeaders": simple_req_headers,
                        "responseHeaders": simple_resp_headers,
                        "requestBody": req_txt,
                        "responseBody": resp_txt,
                    },
                )
                try:
                    print(f"[param-test] enqueue host={host} path={urlsplit(url or '').path}")
                    from ..sensitive_check_local.param_test_throttler import enqueue_param_test
                    dom = host
                    pth = urlsplit(url or "").path or "/"
                    item = {
                        "domain": dom or "",
                        "path": pth,
                        "query": json.loads(query_json) if query_json else {},
                        "requestBody": req_txt,
                    }
                    uid = getattr(self.uploader, "user_id", None)
                    pid = getattr(self.uploader, "project_id", None)
                    import uuid
                    ctx = {"user_id": str(uid or ""), "project_id": str(pid or ""), "client_id": uuid.uuid4().hex}
                    asyncio.create_task(enqueue_param_test(item, ctx))
                except Exception:
                    pass
            except Exception as _e:
                # 不影响后续远端上传与 flow_ext 通知
                print(f"[local_bridge] debug: flow notify error: {_e}")

            # 2) optional remote upload (extended dto for headers/bodies/query etc.)
            # startedAt
            started_at = None
            try:
                t0 = getattr(flow.request, "timestamp_start", None)
                if t0:
                    started_at = datetime.fromtimestamp(float(t0)).isoformat(timespec="seconds")
            except Exception:
                started_at = None

            # finishedAt for duration
            duration_ms = None
            try:
                t0 = getattr(flow.request, "timestamp_start", None)
                t1 = getattr(flow.response, "timestamp_end", None)
                if t0 and t1:
                    duration_ms = int(max(0.0, (float(t1) - float(t0)) * 1000.0))
            except Exception:
                duration_ms = None

            # URL parts
            try:
                parts = urlsplit(url or "")
                scheme = parts.scheme or None
                host = parts.hostname or (parts.netloc or None)
                port = parts.port
                path = parts.path or "/"
                query = parts.query or ""
            except Exception:
                scheme = None
                host = None
                port = None
                path = "/"
                query = ""

            # request/response headers
            def _headers_to_dict(hdrs) -> Dict[str, str]:
                try:
                    d: Dict[str, str] = {}
                    for k, v in (hdrs.items(multi=True) if hdrs is not None else []):
                        if k in d:
                            d[k] = f"{d[k]}, {v}"
                        else:
                            d[k] = v
                    return d
                except Exception:
                    try:
                        return dict(hdrs or {})
                    except Exception:
                        return {}

            req_headers: Dict[str, str] = {}
            resp_headers: Dict[str, str] = {}
            try:
                req_headers = _headers_to_dict(flow.request.headers if (flow and flow.request) else None)
            except Exception:
                req_headers = {}
            try:
                resp_headers = _headers_to_dict(flow.response.headers if (flow and flow.response) else None)
            except Exception:
                resp_headers = {}

            # request/response bodies (base64)
            def _get_raw_req() -> bytes:
                try:
                    if not (flow and flow.request):
                        return b""
                    raw = getattr(flow.request, "raw_content", None)
                    if raw is None:
                        try:
                            txt = flow.request.get_text(strict=False) or ""
                            raw = txt.encode("utf-8", errors="ignore")
                        except Exception:
                            raw = b""
                    return raw or b""
                except Exception:
                    return b""

            def _get_raw_resp() -> bytes:
                try:
                    if not (flow and flow.response):
                        return b""
                    raw = getattr(flow.response, "raw_content", None)
                    if raw is None:
                        try:
                            txt = flow.response.get_text(strict=False) or ""
                            raw = txt.encode("utf-8", errors="ignore")
                        except Exception:
                            raw = b""
                    return raw or b""
                except Exception:
                    return b""

            req_b64 = ""
            resp_b64 = ""
            try:
                rb = _get_raw_req()
                if rb:
                    req_b64 = base64.b64encode(rb).decode("ascii")
            except Exception:
                req_b64 = ""
            try:
                sb = _get_raw_resp()
                if sb:
                    resp_b64 = base64.b64encode(sb).decode("ascii")
            except Exception:
                resp_b64 = ""

            # 1.1) 同步增强：在构造 dto 之前，确保 flow 已携带文本体（上方已处理），此处不再重复

            # meta (add identity hints if available)
            meta_obj: Dict[str, Any] = {
                "addon": "local_bridge_addon",
                "pid": os.getpid(),
                "session_id": self.session_id,
            }
            try:
                if getattr(self.uploader, "user_id", None):
                    meta_obj["user_id"] = self.uploader.user_id
                if getattr(self.uploader, "project_id", None):
                    meta_obj["project_id"] = self.uploader.project_id
                if getattr(self.uploader, "task_id", None):
                    meta_obj["task_id"] = self.uploader.task_id
            except Exception:
                pass

            # identity must come explicitly from environment; do not infer from captured headers to avoid silent mismatches

            # do not derive project_id from URL query; require explicit environment or /start body

            # Convert query string to JSON format if it exists
            query_json = ""
            if query:
                try:
                    # Parse query string into dict and convert to JSON
                    query_dict = dict(parse_qsl(query, keep_blank_values=True))
                    query_json = json.dumps(query_dict, ensure_ascii=False, separators=(",", ":"))
                except Exception:
                    query_json = ""

            dto: Dict[str, Any] = {
                "flowId": flow_id,
                "startedAt": started_at or datetime.now().isoformat(timespec="seconds"),
                "method": method,
                "url": url,
                "scheme": scheme,
                "host": host,
                "port": port,
                "path": path,
                "query": query_json,  # send as JSON string
                # legacy + current
                "status": status,
                "responseStatus": status,
                "durationMs": duration_ms,
                # headers/bodies
                "requestHeaders": req_headers,
                "requestBody": req_b64,          # send base64 with key expected by DTO
                "responseHeaders": resp_headers,
                "responseBody": resp_b64,        # send base64 with key expected by DTO
                # misc
                "tags": ["mitmproxy", "local"],
                "meta": meta_obj,
            }

            # 1.5) local notify: flow_ext (non-blocking, fire-and-forget)
            # TODO: add switch and rate-limit for 'flow_ext' in future (do not implement now)
            try:
                payload_ext: Dict[str, Any] = {
                    "flowId": flow_id,
                    "method": method,
                    "url": url,
                    "status": status if status is not None else -1,
                    "sessionId": self.session_id,
                    "ts": ts_ms,
                    "durationMs": duration_ms if duration_ms is not None else 0,
                    "startedAt": started_at or datetime.now().isoformat(timespec="seconds"),
                    "query": query_json,
                    "requestHeaders": req_headers,
                    "responseHeaders": resp_headers,
                    "requestBodyBase64": req_b64,
                    "responseBodyBase64": resp_b64,
                }
                self.notifier.notify("flow_ext", payload_ext)
                try:
                    print(f"[local_bridge] notify flow_ext: req_b64_len={len(req_b64)} resp_b64_len={len(resp_b64)} hdrs=({len(req_headers)},{len(resp_headers)})")
                except Exception:
                    pass
            except Exception as _e:
                # never break flow; just debug summary
                print(f"[local_bridge] debug: flow_ext notify error: {_e}")

            def _on_done(fid: str, uploaded: bool, error: Optional[str]):
                # local notify: upload result
                self.notifier.notify(
                    "upload",
                    {
                        "flowId": fid,
                        "uploaded": bool(uploaded),
                        **({"error": error} if error else {}),
                    },
                )

            # fire-and-forget upload
            self.uploader.upload_async(dto, flow_id, _on_done)

        except Exception as e:
            # never break mitmproxy flow
            print(f"[local_bridge] debug: addon error: {e}")

    @staticmethod
    def _gen_flow_id() -> str:
        # fallback in case mitmproxy flow.id is missing
        return f"f-{int(time.time() * 1000)}-{os.getpid()}"

    def _start_stat_reporter(self) -> None:
        def _loop():
            while True:
                time.sleep(30.0)
                try:
                    with self._stat_lock:
                        total = self._stat_total
                        kept = self._stat_kept_api
                        filtered = self._stat_filtered_static
                        # reset window
                        self._stat_total = 0
                        self._stat_kept_api = 0
                        self._stat_filtered_static = 0
                    # INFO级简要计数日志（非敏感）
                    print(f"[local_bridge][stats] window=30s total_flows={total} kept_api={kept} filtered_static={filtered} xhr_only={self.filter_xhr_only}")
                except Exception as e:
                    print(f"[local_bridge] debug: stat reporter error: {e}")
        t = threading.Thread(target=_loop, name="stats-reporter", daemon=True)
        t.start()


# Register addon
addons = [LocalBridgeAddon()]
