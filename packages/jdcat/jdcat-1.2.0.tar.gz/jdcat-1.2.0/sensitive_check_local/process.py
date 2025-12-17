"""
Runtime state and process control for sensitive-check-local with real mitmdump management.

Provides:
- start_capture(): validate mitmdump, check port, assemble env, spawn process
- stop_capture(): graceful shutdown with SIGTERM then SIGKILL fallback
- status(): current runtime state
- set_proxy_enabled(): allow API layer to reflect proxy state in /status
"""
from __future__ import annotations

import os
import shutil
import signal
import socket
import subprocess
import time
import uuid
import platform
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, List

from .config import load_config
from .backend_client import BackendAPI, BackendAPIError, build_backend_api_from_context
from .cert_manager import setup_certificate_environment
from .packaging_utils import find_mitmdump_executable


def _analyze_test_result_for_remark(response_a, response_b):
    """
    对齐老工具：分析测试结果，返回(测试结果, 风险等级, 备注)
    这个函数复制自老工具的 _analyze_test_result 方法
    """
    # 检查响应是否存在
    if not response_a or not response_b:
        return "测试失败", "无", "缺少响应数据"
    
    original_status = response_a.get('status_code')
    modified_status = response_b.get('status_code')
    
    # 状态码比较
    if original_status == modified_status:
        if original_status == 200:
            # 需要进一步比较响应内容
            original_body = str(response_a.get('response_body', ''))
            modified_body = str(response_b.get('response_body', ''))

            if original_body == modified_body:
                return "可能存在越权", "高风险", "不同身份返回相同内容"
            else:
                return "正常", "低风险", "不同身份返回不同内容"
        else:
            return "正常", "低风险", f"两个身份都返回{original_status}"
    else:
        # 状态码不同
        if original_status == 200 and modified_status != 200:
            return "正常", "低风险", "测试身份被正确拒绝"
        else:
            return "需人工确认", "中风险", f"原始:{original_status}, 测试:{modified_status}"


@dataclass
class RuntimeState:
    running: bool = False
    pid: Optional[int] = None
    port: Optional[int] = None
    sessionId: Optional[str] = None
    lastError: Optional[str] = None
    proxyEnabled: bool = False
    startedAt: Optional[int] = None
    # whether request de-duplication is enabled for current session
    dedupEnabled: bool = False


_state: RuntimeState = RuntimeState()
_proc: Optional[subprocess.Popen] = None


def _coerce_port(value: Any) -> Optional[int]:
    """
    将输入值规范化为有效的端口号。
    
    将输入值转换为整数并验证是否在有效端口范围内（1-65535）。
    如果转换失败或值超出范围，则返回 None。
    
    参数:
        value: 任意类型的输入值，将尝试转换为整数端口号
        
    返回:
        Optional[int]: 有效的端口号整数，如果输入无效则返回 None
        
    异常:
        不抛出异常，转换失败时返回 None
    """
    if value is None:
        return None
    try:
        i = int(value)
        if 1 <= i <= 65535:
            return i
    except Exception:
        pass
    return None


def _now_ms() -> int:
    """
    获取当前时间的毫秒级时间戳。
    
    将当前系统时间转换为毫秒级时间戳（Unix 时间戳 × 1000）。
    
    返回:
        int: 当前时间的毫秒级时间戳
    """
    return int(time.time() * 1000)


def _is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """
    检查指定端口在指定主机上是否可用（未被占用）。
    
    通过尝试在指定主机和端口上绑定套接字来检测端口是否被占用。
    如果绑定成功，则表示端口可用；如果绑定失败，则表示端口已被占用。
    
    参数:
        port: 要检查的端口号
        host: 要检查的主机地址，默认为 "127.0.0.1"（本地回环地址）
        
    返回:
        bool: 如果端口可用则返回 True，否则返回 False
        
    异常:
        不抛出异常，绑定失败时返回 False
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        return True
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def _build_env(cfg: Dict[str, Any], session_id: str) -> Dict[str, str]:
    """
    构建 mitmdump 进程的环境变量配置。
    
    该函数整合多个来源的配置信息，构建完整的环境变量字典，用于启动 mitmdump 进程。
    主要功能包括：
    1. 身份隔离：设置 USER_ID、PROJECT_ID、TASK_ID、SESSION_ID 等身份标识
    2. 证书配置：通过 setup_certificate_environment 设置 HTTPS 证书相关环境变量
    3. 数据收集配置：设置 INGEST_URL、INGEST_KEY 等数据收集端点
    4. 流量过滤：设置 TARGET_DOMAINS、FILTER_REGEX 等流量过滤规则
    5. 去重配置：设置 DEDUP 环境变量控制请求去重功能
    
    配置优先级：
    - 运行时环境变量 > 传入的配置参数(cfg) > 配置文件(merged)
    
    参数:
        cfg: 包含配置参数的字典，通常来自 API 请求
        session_id: 当前会话的唯一标识符
        
    返回:
        Dict[str, str]: 包含所有环境变量的字典，用于启动 mitmdump 进程
        
    环境变量说明:
        USER_ID: 用户标识，用于数据隔离
        PROJECT_ID: 项目标识，用于数据隔离
        TASK_ID: 任务标识，用于数据隔离
        SESSION_ID: 会话标识，用于数据隔离
        INGEST_URL: 数据收集端点 URL
        INGEST_KEY: 数据收集认证密钥
        TARGET_DOMAINS: 目标域名列表，逗号分隔
        DEDUP: 是否启用请求去重功能
        FILTER_REGEX: 请求过滤正则表达式
        LOCAL_NOTIFY_URL: 本地通知 URL
    """
    env = os.environ.copy()
    
    # Setup certificate environment variables for mitmproxy
    try:
        cert_env_vars = setup_certificate_environment()
        env.update(cert_env_vars)
    except Exception as e:
        # Log but don't fail - certificate setup is optional
        print(f"Warning: Certificate setup failed: {e}")
    
    merged = load_config()
    
    # DEBUG: Print configuration debugging information
    print(f"[DEBUG] 环境构建: cfg键={list(cfg.keys())}")
    print(f"[DEBUG] 环境构建: merged键={list(merged.keys())}")
    
    ingest_url = cfg.get("ingestUrl") or merged.get("ingest_url")
    ingest_key = cfg.get("ingestKey") or merged.get("ingest_key")
    
    # DEBUG: Print ingest configuration values
    print(f"[DEBUG] 环境构建: cfg.ingestUrl={cfg.get('ingestUrl')}")
    print(f"[DEBUG] 环境构建: merged.ingest_url={merged.get('ingest_url')}")
    print(f"[DEBUG] 环境构建: 最终ingest_url={ingest_url}")
    print(f"[DEBUG] 环境构建: 最终ingest_key={'***' if ingest_key else 'None'}")
    
    target_domains = cfg.get("targetDomains") or []
    if isinstance(target_domains, str):
        # allow newline or comma separated text
        parts = []
        for seg in target_domains.replace("\r", "\n").split("\n"):
            seg = seg.strip()
            if not seg:
                continue
            parts.extend([x.strip() for x in seg.split(",") if x.strip()])
        td_list = parts
    elif isinstance(target_domains, list):
        td_list = [str(x).strip() for x in target_domains if str(x).strip()]
    else:
        td_list = []
    # normalize dedup toggle with backward-compatible keys; API will also canonicalize to deduplicate
    dedup_bool = bool(cfg.get("deduplicate") or cfg.get("enableDedup") or cfg.get("dedup"))
    filter_regex = cfg.get("filterRegex") or ""
    env["LOCAL_NOTIFY_URL"] = "http://127.0.0.1:17866/notify"  # 本地服务自身是在localhost启动的，这里保留127.0.0.1
    
    # DEBUG: Environment variable setting
    if ingest_url:
        env["INGEST_URL"] = str(ingest_url)
        print(f"[DEBUG] 环境构建: 设置INGEST_URL={ingest_url}")
    else:
        print(f"[DEBUG] 环境构建: 跳过设置INGEST_URL，未配置")
        
    if ingest_key:
        env["INGEST_KEY"] = str(ingest_key)
        print(f"[DEBUG] 环境构建: 设置INGEST_KEY=***")
    else:
        print(f"[DEBUG] 环境构建: 跳过设置INGEST_KEY，未配置")

    # identity fields for isolation/auditing (prefer cfg camelCase, fallback merged snake_case)
    user_id = cfg.get("userId") if "userId" in cfg else merged.get("user_id")
    project_id = cfg.get("projectId") if "projectId" in cfg else merged.get("project_id")
    # 优先使用运行时环境变量（/start接口更新的值），然后才是配置文件
    task_id = os.environ.get("TASK_ID")
    config_task_id = cfg.get("taskId") if "taskId" in cfg else merged.get("task_id")
    if not task_id or str(task_id).strip() == "":
        task_id = config_task_id

    # 同样处理其他身份字段，确保一致性
    runtime_user_id = os.environ.get("USER_ID")
    if runtime_user_id and str(runtime_user_id).strip() != "":
        user_id = runtime_user_id
    
    runtime_project_id = os.environ.get("PROJECT_ID")
    if runtime_project_id and str(runtime_project_id).strip() != "":
        project_id = runtime_project_id


    if user_id is not None and str(user_id).strip() != "":
        env["USER_ID"] = str(user_id)
    if project_id is not None and str(project_id).strip() != "":
        env["PROJECT_ID"] = str(project_id)
    if task_id is not None and str(task_id).strip() != "":
        env["TASK_ID"] = str(task_id)

    env["SESSION_ID"] = session_id
    env["TARGET_DOMAINS"] = ",".join(td_list)
    env["DEDUP"] = "true" if dedup_bool else "false"
    if filter_regex:
        env["FILTER_REGEX"] = str(filter_regex)
    return env


def start_capture(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Start mitmdump with given config. Does not touch system proxy.
    """
    global _state, _proc
    # validate mitmdump using enhanced finder
    mitmdump_path = find_mitmdump_executable()
    if not mitmdump_path:
        _state.lastError = "mitmdump not found. Please install mitmproxy (pip install mitmproxy or brew install mitmproxy)."
        return {"ok": False, "error": _state.lastError}
    # validate port
    port = _coerce_port(cfg.get("port"))
    if not port:
        _state.lastError = "invalid or missing port"
        return {"ok": False, "error": _state.lastError}
    if not _is_port_available(port):
        _state.lastError = f"port {port} is already in use"
        return {"ok": False, "error": _state.lastError}
    # prepare session
    session_id = cfg.get("sessionId") or _state.sessionId or f"sess-{uuid.uuid4().hex}"
    # normalize dedup toggle (compatible keys)
    dedup_bool = bool(cfg.get("deduplicate") or cfg.get("enableDedup") or cfg.get("dedup"))
    env = _build_env(cfg, session_id)
    # command
    plugin_path = Path(__file__).resolve().parent.parent / "mitmproxy" / "local_bridge_addon.py"
    if not plugin_path.exists():
        # fallback to repository path for backward compatibility
        plugin_path = Path(__file__).resolve().parents[2] / "tools" / "mitmproxy" / "local_bridge_addon.py"
    addon_path = str(plugin_path)
    cmd: List[str] = [mitmdump_path, "-s", addon_path, "--ssl-insecure", "-p", str(port)]
    # spawn
    try:
        creationflags = 0
        preexec_fn = None
        if platform.system() != "Windows":
            preexec_fn = os.setsid  # new process group
        else:
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
        # enable stdout/stderr passthrough when SCL_DEBUG is set (to see addon prints)
        debug = str(os.environ.get("SCL_DEBUG", "")).strip().lower() in ("1", "true", "yes", "on")
        out_stream = None if debug else subprocess.DEVNULL
        err_stream = None if debug else subprocess.DEVNULL

        _proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=out_stream,
            stderr=err_stream,
            preexec_fn=preexec_fn,  # type: ignore[arg-type]
            creationflags=creationflags,
        )
        _state.running = True
        _state.pid = _proc.pid
        _state.port = port
        _state.sessionId = session_id
        _state.lastError = None
        _state.startedAt = _now_ms()
        _state.dedupEnabled = bool(dedup_bool)
        return {"ok": True, "running": True, "sessionId": session_id, "port": port}
    except Exception as e:
        _state.running = False
        _state.pid = None
        _state.port = None
        _state.sessionId = None
        _state.lastError = str(e)
        return {"ok": False, "error": _state.lastError}


def _terminate_process_tree(proc: subprocess.Popen, timeout: float = 5.0) -> None:
    try:
        if platform.system() == "Windows":
            proc.terminate()
        else:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                proc.terminate()
        try:
            proc.wait(timeout=timeout)
        except Exception:
            # force kill
            try:
                if platform.system() == "Windows":
                    proc.kill()
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass
    except Exception:
        pass


def stop_capture() -> Dict[str, Any]:
    """
    Stop mitmdump process gracefully. Does not touch system proxy.
    """
    global _state, _proc
    if _proc is not None:
        try:
            _terminate_process_tree(_proc, timeout=5.0)
        finally:
            _proc = None
    _state.running = False
    _state.pid = None
    _state.port = None
    _state.sessionId = None
    _state.lastError = None
    _state.startedAt = None
    _state.dedupEnabled = False
    return {"ok": True, "running": False}


def status() -> Dict[str, Any]:
    return asdict(_state)


def set_proxy_enabled(enabled: bool) -> None:
    global _state
    _state.proxyEnabled = bool(enabled)

def set_last_error(message: Optional[str]) -> None:
    global _state
    _state.lastError = message


# Backward-compatible function names used by API layer
def start(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return start_capture(cfg)


def stop() -> Dict[str, Any]:
    return stop_capture()


def ensure_started(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return start_capture(cfg)


def ensure_stopped() -> Dict[str, Any]:
    return stop_capture()


def get_status() -> Dict[str, Any]:
    return status()
# ==== Permission testing executor skeleton ====
# 说明：
# - 骨架实现 claim → detail → generate → modify → replay → analyze → progress/results → complete
# - 并发与速率控制（基础版）：并发=REPLAY_CONCURRENCY(default=2)，速率=REPLAY_RPS(default=5/秒)
# - 上报策略（基础版）：每20条或每2秒进行批量 results 上报；阶段性 progress 上报
# - 判定与风险映射后续对齐老工具（挂钩位已预留）
# - 严禁从 body/query 兜底 projectId/userId；统一从上下文与 Header 注入（由 BackendAPI 统一实现）

import os
import time
import asyncio
from typing import Any, Dict, List, Optional, Tuple

from .backend_client import BackendAPI, BackendAPIError, build_backend_api_from_context
from . import events
from .request_modifier_local import modify_request_with_identity
from .analysis_local import compare_responses, detect_privilege_escalation, map_excel_risk_level, build_evidence

# 环境变量参数（基础）
_REPLAY_CONCURRENCY = int(os.getenv("REPLAY_CONCURRENCY", "2"))
_REPLAY_RPS = float(os.getenv("REPLAY_RPS", "5"))
_REPORT_BATCH_SIZE = int(os.getenv("REPORT_BATCH_SIZE", "20"))
_REPORT_BATCH_INTERVAL_SEC = float(os.getenv("REPORT_BATCH_INTERVAL_SEC", "2.0"))
_FAIL_RATIO_ABORT = float(os.getenv("FAIL_RATIO_ABORT", "0.2"))  # 整体错误超过阈值中止（默认20%）
# 跟随重定向默认关闭（对齐老工具）；可由前端通过 ctx.follow_redirects 开启
_FOLLOW_REDIRECTS = str(os.getenv("FOLLOW_REDIRECTS", "false")).strip().lower() in ("1", "true", "yes", "on")

def _now_ms() -> int:
    return int(time.time() * 1000)

def _is_get_or_post(m: str) -> bool:
    try:
        return str(m or "").upper() in ("GET", "POST")
    except Exception:
        return False

def _safe_preview(s: Optional[str], max_len: int = 80) -> str:
    if s is None:
        return ""
    try:
        s = str(s)
        return s if len(s) <= max_len else s[:max_len] + "..."
    except Exception:
        return ""

def _minimize_headers(h: Dict[str, Any]) -> Dict[str, Any]:
    # 测试环境不需要脱敏，直接返回完整headers
    return dict(h or {})

async def _progress(api: BackendAPI, task_id: str, current: int, total: int, message: str) -> None:
    import logging
    logger = logging.getLogger("sensitive_check_local")
    
    try:
        logger.info(f"[PROGRESS] 📊 上报进度: task_id={task_id}, current={current}, total={total}, message='{message}'")
        result = await api.progress(task_id, current, total, message)
        logger.info(f"[PROGRESS] ✅ 进度上报成功: {result}")
        events.on_progress_sent({"task_id": task_id, "current": current, "total": total, "message": message})
    except Exception as e:
        logger.error(f"[PROGRESS] ❌ 进度上报失败: task_id={task_id}, error={e}", exc_info=True)
        # 不兜底，按规则：错误可暴露
        raise

async def _send_results(api: BackendAPI, task_id: str, buf: List[Dict[str, Any]]) -> None:
    if not buf:
        return
    try:
        await api.results(task_id, buf)
        events.on_results_sent({"task_id": task_id, "count": len(buf)})
    except Exception:
        pass
    finally:
        buf.clear()

def _generate_basic_cases(records: List[Dict[str, Any]], identities: List[Dict[str, Any]], strategies: List[str]) -> List[Dict[str, Any]]:
    """
    依据后端 detail.strategies 生成用例（对齐老工具逻辑，避免用例数膨胀）：
    - 仅保留 GET/POST
    - 规则：
      • horizontal: 同角色且 identity_user_id 与 record.user_id 不同（避免重复组合）
      • vertical: 角色不同（若记录无角色，保守生成，由分析阶段补充判定）
      • role: 按角色维度生成（不比较 userId）
      • token: 身份包含 tokens/cookies/授权头时生成
      • param: 请求存在 query 或 body 时生成，基于 custom_params 覆盖
    """
    strategies = [str(x).strip().lower() for x in (strategies or [])]
    include_horizontal = "horizontal" in strategies
    include_vertical = "vertical" in strategies
    include_role = any(x in strategies for x in ("role", "role_access"))
    include_token = any(x in strategies for x in ("token", "token_operation"))
    include_param = any(x in strategies for x in ("param", "parameter_tamper", "param_tamper"))

    cases: List[Dict[str, Any]] = []
    if not isinstance(records, list) or not isinstance(identities, list):
        return cases

    # 按角色分组身份，对齐老工具逻辑
    users_by_role = {}
    for ident in identities:
        role = str(ident.get("role") or "").strip().lower()
        if role not in users_by_role:
            users_by_role[role] = []
        users_by_role[role].append(ident)

    for r in records:
        method = str(r.get("method") or "").upper()
        url = str(r.get("url") or "")
        if not _is_get_or_post(method) or not url:
            continue
        source_user = str(r.get("user_id") or "")

        # 水平越权：对齐老工具逻辑，生成两个身份的对比测试
        if include_horizontal:
            for role, role_users in users_by_role.items():
                if len(role_users) >= 2:
                    # 对齐老工具：生成身份对，每对生成一个测试用例
                    for i in range(len(role_users) - 1):
                        identity_a = role_users[i]
                        identity_b = role_users[i + 1]
                        
                        try:
                            # 生成身份A的请求
                            request_a = modify_request_with_identity(
                                {
                                    "method": method,
                                    "url": url,
                                    "headers": r.get("headers") or {},
                                    "request_body": r.get("request_body"),
                                },
                                identity_a,
                                source_user_id=None,  # 不依赖原始用户身份
                            )
                            
                            # 生成身份B的请求
                            request_b = modify_request_with_identity(
                                {
                                    "method": method,
                                    "url": url,
                                    "headers": r.get("headers") or {},
                                    "request_body": r.get("request_body"),
                                },
                                identity_b,
                                source_user_id=None,  # 不依赖原始用户身份
                            )
                            
                            cases.append({
                                "record": r,
                                "strategy": "horizontal",
                                "test_type": "horizontal_escalation",
                                "identity_a": identity_a,
                                "identity_b": identity_b,
                                "request_a": request_a,
                                "request_b": request_b,
                                "description": f"测试相同角色'{role}'的用户 {identity_a.get('identity_user_id')} 和 {identity_b.get('identity_user_id')} 访问结果是否一致",
                            })
                        except Exception:
                            continue
                        break  # 每个请求每个角色只生成一个水平越权测试用例

        # 垂直越权：对齐老工具逻辑，测试低权限角色访问高权限角色的功能
        if include_vertical:
            # 定义角色等级，数字越大权限越高
            role_levels = {
                'guest': 1,
                'user': 2,
                'member': 2,  # 与user同级
                'operator': 3,
                'admin': 4,
                'super_admin': 5
            }
            
            # 找出所有角色对
            available_roles = list(users_by_role.keys())
            if len(available_roles) >= 2:
                for high_role in available_roles:
                    high_level = role_levels.get(high_role, 0)
                    for low_role in available_roles:
                        low_level = role_levels.get(low_role, 0)
                        # 只测试低权限角色访问高权限角色的资源
                        if low_level < high_level and users_by_role[low_role] and users_by_role[high_role]:
                            low_user = users_by_role[low_role][0]  # 取第一个低权限用户
                            high_user = users_by_role[high_role][0]  # 取第一个高权限用户
                            
                            try:
                                # 生成低权限用户的请求
                                request_low = modify_request_with_identity(
                                    {
                                        "method": method,
                                        "url": url,
                                        "headers": r.get("headers") or {},
                                        "request_body": r.get("request_body"),
                                    },
                                    low_user,
                                    source_user_id=None,  # 不依赖原始用户身份
                                )
                                
                                # 生成高权限用户的请求
                                request_high = modify_request_with_identity(
                                    {
                                        "method": method,
                                        "url": url,
                                        "headers": r.get("headers") or {},
                                        "request_body": r.get("request_body"),
                                    },
                                    high_user,
                                    source_user_id=None,  # 不依赖原始用户身份
                                )
                                
                                cases.append({
                                    "record": r,
                                    "strategy": "vertical",
                                    "test_type": "vertical_escalation",
                                    "identity_a": low_user,  # 低权限身份
                                    "identity_b": high_user,  # 高权限身份
                                    "request_a": request_low,
                                    "request_b": request_high,
                                    "description": f"测试低权限角色'{low_role}'的用户 {low_user.get('identity_user_id')} 是否能访问高权限角色'{high_role}'的功能",
                                })
                            except Exception:
                                continue
                            break  # 每个请求每个角色对只生成一个垂直越权测试用例

        # 其他策略保持原逻辑（这些不会造成大量膨胀）
        if include_role or include_token or include_param:
            for ident in identities:
                role = str(ident.get("role") or "").strip().lower()
                target_uid = str(ident.get("identity_user_id") or ident.get("user_id") or "")

                # 策略筛选
                selected = False
                if include_role:
                    selected = True
                if include_token and (ident.get("tokens") or ident.get("tokens_json") or ident.get("cookies") or ident.get("cookies_json")):
                    selected = True
                if include_param and (r.get("query") or r.get("request_body")):
                    selected = True

                if not selected:
                    continue

                try:
                    modified = modify_request_with_identity(
                        {
                            "method": method,
                            "url": url,
                            "headers": r.get("headers") or {},
                            "request_body": r.get("request_body"),
                        },
                        ident,
                        source_user_id=source_user if source_user else None,
                    )
                    strategy_parts = []
                    if include_role:
                        strategy_parts.append("role")
                    if include_token:
                        strategy_parts.append("token")
                    if include_param:
                        strategy_parts.append("param")
                    
                    cases.append({
                        "record": r,
                        "identity": ident,
                        "strategy": ",".join(strategy_parts),
                        "modified": modified,
                    })
                except Exception:
                    continue
    return cases

def _analyze_basic(original: Dict[str, Any], modified_resp: Dict[str, Any]) -> Tuple[bool, str]:
    """
    对齐老工具判定口径的简化版：
    - 若原始响应非200且修改后为200 → 高风险(HIGH)
    - 若均为200且响应体文本摘要一致（表示不同身份获得相同数据）→ 高风险(HIGH)
    - 其他：修改后200 → 中风险(MEDIUM)；否则低风险(LOW)
    """
    orig_status = int(original.get("response_status") or 0)
    mod_status = int(modified_resp.get("status") or 0)
    if orig_status != 200 and mod_status == 200:
        return True, "HIGH"
    if orig_status == 200 and mod_status == 200:
        o_body = _safe_preview(original.get("response_body"), 256)
        m_body = _safe_preview(modified_resp.get("text") or modified_resp.get("body"), 256)
        if o_body and m_body and o_body == m_body:
            return True, "HIGH"
    if mod_status == 200:
        return True, "MEDIUM"
    return False, "LOW"

async def run_permission_task(ctx: Dict[str, Any]) -> bool:
    """
    执行器入口（异步）：
    1) claim → 2) detail → 3) generate → 4) modify/replay → 5) analyze → 6) progress/results → 7) complete
    返回：True|False（表示整体成功与否）
    """
    import logging
    logger = logging.getLogger("sensitive_check_local")
    
    logger.info("=" * 80)
    logger.info("🚀 [PERMISSION-TASK] 开始执行越权测试核心流程")
    logger.info("=" * 80)
    
    task_id = str(ctx.get("task_id") or "").strip()
    client_id = str(ctx.get("client_id") or "").strip()
    project_id = str(ctx.get("project_id") or "").strip()
    user_id = str(ctx.get("user_id") or "").strip()
    
    logger.info(f"[PERMISSION-TASK] 📋 任务参数:")
    logger.info(f"[PERMISSION-TASK]   - task_id: {task_id}")
    logger.info(f"[PERMISSION-TASK]   - client_id: {client_id[:8] if client_id else 'None'}***")
    logger.info(f"[PERMISSION-TASK]   - project_id: {project_id}")
    logger.info(f"[PERMISSION-TASK]   - user_id: {user_id[:6] if user_id else 'None'}***")
    
    if not task_id or not client_id:
        logger.error(f"[PERMISSION-TASK] ❌ 关键参数缺失: task_id={bool(task_id)}, client_id={bool(client_id)}")
        return False

    logger.info(f"[PERMISSION-TASK] 🔧 构建后端API客户端...")
    try:
        api = build_backend_api_from_context(ctx)
        logger.info(f"[PERMISSION-TASK] ✅ API客户端构建成功")
        # 允许在 claim 409 冲突时预取 detail 并继续后续流程
        detail_res: Optional[Dict[str, Any]] = None
    except Exception as e:
        logger.error(f"[PERMISSION-TASK] ❌ API客户端构建失败: {e}", exc_info=True)
        return False

    # 1) claim
    logger.info(f"[PERMISSION-TASK] 📝 步骤1: 开始认领任务...")
    try:
        logger.info(f"[PERMISSION-TASK] 发起认领请求: task_id={task_id}, client_id={client_id[:8]}***")
        claim_res = await api.claim(task_id, client_id=client_id)
        logger.info(f"[PERMISSION-TASK] 认领响应: {claim_res}")
        
        events.on_claimed({"task_id": task_id, "result": claim_res})
        
        # 认领失败理由（后端约定）：already_assigned/forbidden/invalid
        reason = str(claim_res.get("reason") or "").strip().lower()
        success_flag = bool(claim_res.get("success") if "success" in claim_res else (not reason))
        
        if not success_flag:
            logger.error(f"[PERMISSION-TASK] ❌ 任务认领失败: reason={reason}")
            # 失败即终止并 complete(false)
            try:
                logger.info(f"[PERMISSION-TASK] 发送任务完成状态(失败)...")
                await api.complete(task_id, False)
            except Exception as complete_e:
                logger.error(f"[PERMISSION-TASK] 发送完成状态失败: {complete_e}")
            events.on_completed({"task_id": task_id, "success": False, "reason": reason or "claim_failed"})
            return False
        else:
            logger.info(f"[PERMISSION-TASK] ✅ 任务认领成功")
            
    except BackendAPIError as e:
        logger.error(f"[PERMISSION-TASK] ❌ 认领API错误: status_code={e.status_code}, message={e.message}")
        # 对 409 冲突（可能已被本客户端或他端认领/运行）进行幂等处理：尝试拉取 detail 继续执行
        if int(e.status_code or 0) == 409:
            logger.warning("[PERMISSION-TASK] claim_conflict: 尝试直接拉取 detail 并继续执行")
            try:
                detail_res = await api.detail(task_id)
                # 不标记失败，不 complete，直接进入 detail 阶段
            except Exception as ie:
                logger.error(f"[PERMISSION-TASK] claim_conflict 后获取 detail 失败: {ie}")
                try:
                    await api.complete(task_id, False)
                except Exception:
                    pass
                events.on_completed({"task_id": task_id, "success": False, "reason": "claim_conflict_detail_failed"})
                return False
        else:
            try:
                await api.complete(task_id, False)
            except Exception:
                pass
            events.on_completed({"task_id": task_id, "success": False, "reason": f"claim_error:{e.status_code}"})
            return False
    except Exception as e:
        logger.error(f"[PERMISSION-TASK] ❌ 认领异常: {e}", exc_info=True)
        try:
            await api.complete(task_id, False)
        except Exception:
            pass
        events.on_completed({"task_id": task_id, "success": False, "reason": "claim_exception"})
        return False

    # 2) detail
    try:
        if detail_res is None:
            detail_res = await api.detail(task_id)
        events.on_detail_fetched({"task_id": task_id})
        # 后端统一响应为 { code, message, data, ... }，需要解包 data
        payload = detail_res.get("data") or detail_res
        records: List[Dict[str, Any]] = payload.get("capture_records") or payload.get("records") or []
        if not isinstance(records, list) or not records:
            # 权限不足或缺失
            try:
                await api.complete(task_id, False)
            except Exception:
                pass
            events.on_completed({"task_id": task_id, "success": False, "reason": "detail_missing"})
            return False
    except BackendAPIError as e:
        try:
            await api.complete(task_id, False)
        except Exception:
            pass
        events.on_completed({"task_id": task_id, "success": False, "reason": f"detail_error:{e.status_code}"})
        return False
    except Exception:
        try:
            await api.complete(task_id, False)
        except Exception:
            pass
        events.on_completed({"task_id": task_id, "success": False, "reason": "detail_exception"})
        return False

    total = len(records)
    await _progress(api, task_id, 0, total, "detail_fetched")

    # 3) generate（解包 identities 与 strategies，并规范化身份字段）
    payload = detail_res.get("data") or detail_res
    identities_raw: List[Dict[str, Any]] = payload.get("identities") or payload.get("permission_identities") or []
    backend_strategies: List[str] = payload.get("strategies") or []
    # 前端优先：从 ctx.strategies 覆盖（仅允许 horizontal/vertical），否则使用后端下发
    ctx_strategies_raw = (ctx or {}).get("strategies")
    resolved: List[str] = []
    if isinstance(ctx_strategies_raw, str):
        parts = [x.strip().lower() for x in ctx_strategies_raw.replace(",", " ").split() if x.strip()]
        resolved = [x for x in parts if x in ("horizontal", "vertical")]
    elif isinstance(ctx_strategies_raw, list):
        resolved = [str(x).strip().lower() for x in ctx_strategies_raw if str(x).strip().lower() in ("horizontal", "vertical")]
    # 若前端未提供或为空，则回退到后端下发（保持后端的完整策略能力）
    strategies: List[str] = resolved if resolved else [str(x).strip().lower() for x in backend_strategies if str(x).strip()]
    identities: List[Dict[str, Any]] = []
    # 获取当前登录用户ID，用于过滤身份列表
    current_user_id = str(user_id or "").strip()
    logger.info(f"[PERMISSION-TASK] 🔍 当前登录用户ID: {current_user_id[:6] if current_user_id else 'None'}***")
    
    for ident in identities_raw:
        if not isinstance(ident, dict):
            continue
        
        # 获取身份的用户ID（优先使用 identity_user_id，其次 user_id）
        ident_user_id = str(ident.get("identityUserId") or ident.get("identity_user_id") or
                           ident.get("userId") or ident.get("user_id") or "").strip()
        
        # 排除当前登录用户，避免用户测试自己的资源
        if current_user_id and ident_user_id == current_user_id:
            logger.info(f"[PERMISSION-TASK] ⚠️ 跳过当前登录用户身份: {ident_user_id[:6]}*** (role: {ident.get('role')})")
            continue
            
        # 关键修复：正确处理JSON字符串格式的身份数据
        headers_data = ident.get("headers") or ident.get("headersJson") or ident.get("headers_json")
        cookies_data = ident.get("cookies") or ident.get("cookiesJson") or ident.get("cookies_json")
        tokens_data = ident.get("tokens") or ident.get("tokensJson") or ident.get("tokens_json")
        custom_params_data = ident.get("customParams") or ident.get("custom_params") or ident.get("customParamsJson") or ident.get("custom_params_json")
        
        # 添加调试日志，输出原始身份数据
        logger.info(f"[PERMISSION-TASK] 🔍 处理身份: {ident_user_id[:6]}*** (role: {ident.get('role')})")
        logger.info(f"[PERMISSION-TASK] 原始headers数据类型: {type(headers_data)}, 内容: {str(headers_data)[:100]}...")
        logger.info(f"[PERMISSION-TASK] 原始cookies数据类型: {type(cookies_data)}, 内容: {str(cookies_data)[:100]}...")
        
        identities.append({
            "id": ident.get("id"),
            "project_id": ident.get("projectId") or ident.get("project_id"),
            "user_id": str(ident.get("userId") or ident.get("user_id") or ""),
            "identity_user_id": str(ident.get("identityUserId") or ident.get("identity_user_id") or ""),
            "role": ident.get("role"),
            "headers_json": headers_data,  # 保持原始数据，让身份替换函数处理JSON解析
            "cookies_json": cookies_data,
            "tokens_json": tokens_data,
            "custom_params_json": custom_params_data,
        })

    if not isinstance(identities, list) or len(identities) < 2:
        try:
            await api.complete(task_id, False)
        except Exception:
            pass
        events.on_completed({"task_id": task_id, "success": False, "reason": "identities_insufficient"})
        return False

    # 策略必填：若前端与后端均未提供，终止任务，避免默认兜底引发误解
    if not strategies:
        try:
            await api.complete(task_id, False)
        except Exception:
            pass
        events.on_completed({"task_id": task_id, "success": False, "reason": "strategies_missing"})
        return False
    cases = _generate_basic_cases(records, identities, strategies)
    # 将总进度切换为用例总数，避免出现 current > total 的情况
    total = len(cases)
    events.on_case_generated({"task_id": task_id, "count": total})
    await _progress(api, task_id, 0, total, "cases_generated")
    
    logger.info(f"[PERMISSION-TASK] 📊 步骤3: 生成测试用例完成")
    logger.info(f"[PERMISSION-TASK]   - 原始记录数: {len(records)}")
    logger.info(f"[PERMISSION-TASK]   - 身份数: {len(identities)}")
    logger.info(f"[PERMISSION-TASK]   - 策略数: {len(strategies)} / {strategies}")
    logger.info(f"[PERMISSION-TASK]   - 生成用例数: {total}")

    # 4/5) modify & replay（基础并发与速率控制）
    logger.info(f"[PERMISSION-TASK] 🔄 步骤4-5: 开始修改并回放测试")
    logger.info(f"[PERMISSION-TASK]   - 并发数: {max(1, _REPLAY_CONCURRENCY)}")
    logger.info(f"[PERMISSION-TASK]   - 限速RPS: {_REPLAY_RPS}")
    # 跟随重定向：默认关闭，可由前端在 /local/tasks/start 传入 follow_redirects 开启
    follow_redirects = bool((ctx or {}).get("follow_redirects")) if (ctx and ("follow_redirects" in ctx)) else _FOLLOW_REDIRECTS
    logger.info(f"[PERMISSION-TASK]   - 跟随重定向: {follow_redirects}")
    
    sem = asyncio.Semaphore(max(1, _REPLAY_CONCURRENCY))
    last_sent_ms = _now_ms()
    result_buf: List[Dict[str, Any]] = []
    fail_count = 0
    done_count = 0

    async def _execute_http_request(request_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个HTTP请求并返回响应（对齐老工具逻辑）"""
        import logging
        logger = logging.getLogger("sensitive_check_local")
        
        method = str(request_config.get("method") or "GET").upper()
        url = str(request_config.get("url") or "")
        headers = dict(request_config.get("headers") or {})
        body = request_config.get("request_body")
        cookies = request_config.get("cookies") or {}
        
        logger.info(f"[HTTP-REQUEST] 执行请求: {method} {url}")
        logger.debug(f"[HTTP-REQUEST] Headers: {list(headers.keys())}")
        logger.debug(f"[HTTP-REQUEST] Cookies: {list(cookies.keys())}")
        
        response = {"status": 0, "text": ""}
        
        try:
            import httpx
            import json
            
            # 对齐老工具：处理headers中的中文字符编码问题
            processed_headers = {}
            for key, value in headers.items():
                if isinstance(value, str):
                    try:
                        # 检查是否包含非ASCII字符
                        value.encode('ascii')
                        processed_headers[key] = value
                    except UnicodeEncodeError:
                        # 包含中文字符，跳过该header或进行URL编码
                        if key.lower() in ['cookie', 'set-cookie']:
                            # Cookie header需要URL编码处理
                            from urllib.parse import quote
                            processed_headers[key] = quote(value, safe='=;, ')
                            logger.debug(f"Header {key} 包含中文字符，已进行URL编码")
                        else:
                            # 其他headers包含中文字符时，记录警告并跳过
                            logger.warning(f"跳过包含中文字符的Header: {key}")
                            continue
                else:
                    processed_headers[key] = str(value)
            
            # 对齐老工具：处理cookies中的中文字符编码问题
            processed_cookies = {}
            for key, value in cookies.items():
                if isinstance(value, str):
                    try:
                        # 检查是否包含非ASCII字符
                        value.encode('ascii')
                        processed_cookies[key] = value
                    except UnicodeEncodeError:
                        # 包含中文字符，需要URL编码
                        from urllib.parse import quote
                        processed_cookies[key] = quote(value, safe='')
                        logger.debug(f"Cookie {key} 包含中文字符，已进行URL编码")
                else:
                    processed_cookies[key] = value
            
            # 对齐老工具：准备基础参数（移除冗余的kwargs构建）
            # 检查是否已有Cookie header
            has_cookie_header = any(key.lower() == 'cookie' for key in processed_headers.keys())
            
            # 处理cookies参数（与老工具逻辑完全一致）
            final_cookies = None
            if not has_cookie_header and processed_cookies:
                # 如果没有Cookie header但有cookies数据，使用cookies参数
                final_cookies = processed_cookies
                logger.debug("使用cookies参数")
            elif has_cookie_header:
                # 如果已有Cookie header，确保其正确编码
                logger.debug("使用现有的Cookie header，跳过cookies参数")
            
            # 对齐老工具：处理请求体
            final_json = None
            final_data = None
            
            if body and method in ['POST', 'PUT', 'PATCH']:
                content_type = processed_headers.get('Content-Type', '').lower()
                if 'application/json' in content_type:
                    try:
                        if isinstance(body, str):
                            final_json = json.loads(body)
                        else:
                            final_json = body
                        # 确保JSON请求使用UTF-8编码
                        if 'charset' not in content_type:
                            processed_headers['Content-Type'] = content_type + '; charset=utf-8'
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"请求体JSON解析失败: {e}, 使用原始数据")
                        # 确保使用UTF-8编码处理中文字符
                        if isinstance(body, str):
                            final_data = body.encode('utf-8')
                            if 'charset' not in content_type:
                                processed_headers['Content-Type'] = content_type + '; charset=utf-8'
                        else:
                            final_data = body
                else:
                    # 确保使用UTF-8编码处理中文字符
                    if isinstance(body, str):
                        final_data = body.encode('utf-8')
                        # 为非JSON请求添加UTF-8编码声明
                        if content_type and 'charset' not in content_type:
                            processed_headers['Content-Type'] = content_type + '; charset=utf-8'
                        elif not content_type:
                            processed_headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
                    else:
                        final_data = body
            
            # 对齐老工具：使用httpx.AsyncClient的统一请求方式
            client_kwargs = {
                'timeout': httpx.Timeout(10.0),
                'verify': False,  # 对齐老工具：忽略SSL证书验证
                'follow_redirects': follow_redirects
            }
            
            # 准备请求参数（不包含client配置参数）
            request_kwargs = {
                'headers': processed_headers,
            }
            
            # 添加cookies（如果存在）
            if final_cookies:
                request_kwargs['cookies'] = final_cookies
            
            # 添加请求体（如果存在）
            if final_json is not None:
                request_kwargs['json'] = final_json
            elif final_data is not None:
                request_kwargs['data'] = final_data
            
            async with httpx.AsyncClient(**client_kwargs) as client:
                # 对齐老工具：使用统一的request方法
                resp = await client.request(method, url, **request_kwargs)
                
                # 构造响应数据（严格对齐老工具字段名）
                response = {
                    'status_code': int(getattr(resp, "status_code", 0) or 0),
                    'headers': dict(resp.headers),
                    'response_body': resp.text,
                    'response_time': 0,  # httpx没有直接的elapsed属性
                    'url': str(resp.url),
                    'cookies': dict(resp.cookies)
                }
                
        except Exception as e:
            logger.error(f"HTTP请求失败: {e}")
            # 对齐老工具：错误响应格式
            response = {
                'status_code': 0,
                'headers': {},
                'response_body': f"error: {e}",
                'response_time': 0,
                'url': url,
                'cookies': {}
            }
        
        return response

    async def _replay_one(case: Dict[str, Any]) -> None:
        nonlocal done_count, fail_count, result_buf, last_sent_ms
        
        # 检查用例结构：新逻辑（双身份对比）vs 旧逻辑（单身份）
        if "identity_a" in case and "identity_b" in case:
            # 新逻辑：双身份对比测试
            await _replay_dual_identity_case(case)
        else:
            # 旧逻辑：单身份测试（兼容性保留）
            await _replay_single_identity_case(case)

    async def _replay_dual_identity_case(case: Dict[str, Any]) -> None:
        """双身份对比测试（对齐老工具逻辑）"""
        import json
        nonlocal done_count, fail_count, result_buf, last_sent_ms
        
        record = case.get("record") or {}
        strategy = case.get("strategy") or ""
        test_type = case.get("test_type") or ""
        identity_a = case.get("identity_a") or {}
        identity_b = case.get("identity_b") or {}
        request_a = case.get("request_a") or {}
        request_b = case.get("request_b") or {}
        
        logger.info("=" * 60)
        logger.info(f"🔄 [REPLAY] 开始双身份对比测试 第 {done_count + 1} 条")
        logger.info("=" * 60)
        logger.info(f"[REPLAY] 📋 原始记录信息:")
        logger.info(f"[REPLAY]   - Record ID: {record.get('id', 'N/A')}")
        logger.info(f"[REPLAY]   - 策略: {strategy}")
        logger.info(f"[REPLAY]   - 测试类型: {test_type}")
        logger.info(f"[REPLAY] 👤 身份A: {identity_a.get('identity_user_id', 'unknown')} (角色: {identity_a.get('role', 'unknown')})")
        logger.info(f"[REPLAY] 👤 身份B: {identity_b.get('identity_user_id', 'unknown')} (角色: {identity_b.get('role', 'unknown')})")

        # 限速
        await asyncio.sleep(max(0.0, 1.0 / max(_REPLAY_RPS, 0.001)))

        # 执行两个请求
        logger.info(f"[REPLAY] 📤 执行身份A请求...")
        response_a = await _execute_http_request(request_a)
        
        await asyncio.sleep(max(0.0, 1.0 / max(_REPLAY_RPS, 0.001)))  # 限速
        
        logger.info(f"[REPLAY] 📤 执行身份B请求...")
        response_b = await _execute_http_request(request_b)

        logger.info(f"[REPLAY] 📥 身份A响应: status={response_a['status_code']} body={response_a['response_body']}")
        logger.info(f"[REPLAY] 📥 身份B响应: status={response_b['status_code']} body={response_b['response_body']}")

        # 分析（对比两个响应）
        compare = compare_responses(
            {"status": response_a["status_code"], "text": response_a["response_body"], "headers": {}},
            {"status": response_b["status_code"], "text": response_b["response_body"], "headers": {}},
        )
        
        detector = detect_privilege_escalation(
            original_identity_role=identity_b.get("role"),
            target_identity_role=identity_a.get("role"),
            original_user_id=str(identity_b.get("identity_user_id") or identity_b.get("user_id") or ""),
            target_user_id=str(identity_a.get("identity_user_id") or identity_a.get("user_id") or ""),
        )
        
        # 对齐老工具逻辑：如果两个响应一致，说明存在越权风险
        content_similarity = float(compare.get("content_similarity") or 0.0)
        status_a, status_b = response_a["status_code"], response_b["status_code"]
        
        # 风险判定逻辑
        if status_a == 200 and status_b == 200 and content_similarity > 0.8:
            risk = "HIGH"
            is_vuln = True
        elif status_a == 200 and status_b != 200:
            risk = "MEDIUM"
            is_vuln = True
        elif status_a != 200 and status_b == 200:
            risk = "LOW"
            is_vuln = False
        else:
            risk = "LOW"
            is_vuln = False

        evidence = build_evidence(response_a, response_b, compare, detector)

        logger.info(f"[REPLAY] 🔍 漏洞分析结果: {'✅ 是' if is_vuln else '❌ 否'} / 风险={risk} / 相似度={round(content_similarity, 4)} / 类型={test_type}")
        logger.info(f"[REPLAY]   - 分析依据: 身份A状态({status_a}) vs 身份B状态({status_b}) / 内容相似度={round(content_similarity, 4)}")
        
        # 对齐老工具：生成备注信息
        test_result_text, risk_level_text, remark_text = _analyze_test_result_for_remark(response_a, response_b)

        # 构造结果
        _conf_map = {"high": 0.90, "medium": 0.60, "low": 0.30}
        _conf_str = str(detector.get("confidence") or "").lower()
        _conf_num = _conf_map.get(_conf_str, 0.30)
        
        body_a = request_a.get("request_body")
        _request_body_full = ""
        try:
            if isinstance(body_a, (dict, list)):
                import json as _json
                _request_body_full = _json.dumps(body_a, ensure_ascii=False)
            else:
                _request_body_full = str(body_a or "")
        except Exception:
            _request_body_full = str(body_a or "")
        
        # 构建Excel兼容的完整测试结果，对齐老工具所有字段
        result_item = {
            "id": record.get("id"),
            "index": record.get("index"),
            "method": str(request_a.get("method") or "GET").upper(),
            "url": str(request_a.get("url") or ""),
            "requestHeadersPreview": _minimize_headers(request_a.get("headers") or {}),
            "requestBodyPreview": _safe_preview(body_a, 128),
            "request_body": _request_body_full,
            # 响应（使用身份A和身份B的响应）
            "original_status": response_b["status_code"],  # 身份B作为"原始"
            "modified_status": response_a["status_code"],  # 身份A作为"修改后"
            
            # 新增：使用更直观的字段名
            "identity1_body": response_a["response_body"],  # 身份1的响应体
            "identity2_body": response_b["response_body"],  # 身份2的响应体
            # 判定与映射
            "isVulnerable": bool(is_vuln),
            "risk_level": str(risk).lower(),
            "content_similarity": round(content_similarity, 4),
            "privilege_type": test_type,
            "confidence": _conf_num,
            "confidenceLevel": _conf_str,
            "evidence_json": json.dumps(evidence, ensure_ascii=False),
            # 策略与类型
            "strategy": strategy,
            "test_type": test_type,
            # 身份字段
            "identity_1": str(identity_a.get("identity_user_id") or identity_a.get("user_id") or ""),
            "identity_2": str(identity_b.get("identity_user_id") or identity_b.get("user_id") or ""),
            # 结果摘要
            "result_summary": remark_text,  # 对齐老工具：使用备注信息
            
            # === 新增：Excel兼容的完整字段，对齐老工具 ===
            # 身份详细信息（不截断）
            "identity_1_info": json.dumps({
                "id": identity_a.get("id"),
                "user_id": str(identity_a.get("identity_user_id") or identity_a.get("user_id") or ""),
                "role": identity_a.get("role"),
                "username": identity_a.get("username", f"用户{identity_a.get('identity_user_id', 'Unknown')}"),
                "description": f"{identity_a.get('role', 'Unknown')}角色用户"
            }, ensure_ascii=False),
            "identity_2_info": json.dumps({
                "id": identity_b.get("id"),
                "user_id": str(identity_b.get("identity_user_id") or identity_b.get("user_id") or ""),
                "role": identity_b.get("role"),
                "username": identity_b.get("username", f"用户{identity_b.get('identity_user_id', 'Unknown')}"),
                "description": f"{identity_b.get('role', 'Unknown')}角色用户"
            }, ensure_ascii=False),
            
            # 完整请求信息（不截断）
            "request_url_full": str(request_a.get("url") or ""),
            "request_method": str(request_a.get("method") or "GET").upper(),
            "request_body_full": _request_body_full,
            
            # 完整请求头信息（两个身份的请求头）- 对齐数据库字段名
            "identity_1_headers_full": json.dumps(dict(request_a.get("headers") or {}), ensure_ascii=False),
            "identity_2_headers_full": json.dumps(dict(request_b.get("headers") or {}), ensure_ascii=False),
            
            # 完整响应信息（不截断）
            "identity_1_response_status": response_a["status_code"],
            "identity_2_response_status": response_b["status_code"],
            "identity_1_response_body_full": response_a["response_body"],
            "identity_2_response_body_full": response_b["response_body"],
            "identity_1_response_headers": json.dumps(response_a.get("headers", {}), ensure_ascii=False),
            "identity_2_response_headers": json.dumps(response_b.get("headers", {}), ensure_ascii=False),
            
            # 测试结果描述（对齐Excel格式）
            "test_result_description": "存在越权" if is_vuln else "正常",
            "risk_level_chinese": {
                "high": "高风险",
                "medium": "中风险",
                "low": "低风险"
            }.get(str(risk).lower(), "低风险"),
            "remark": f"身份A({identity_a.get('role', 'Unknown')})状态:{response_a['status_code']}, 身份B({identity_b.get('role', 'Unknown')})状态:{response_b['status_code']}, 相似度:{round(content_similarity, 4)}",
            
            # Excel兼容的完整数据结构
            "excel_compatible_data": json.dumps({
                "序号": record.get("index", 0),
                "测试URL": str(request_a.get("url") or ""),
                "请求方式": str(request_a.get("method") or "GET").upper(),
                "请求体": _request_body_full,
                "测试账号1": f"{identity_a.get('role', 'Unknown')}用户{identity_a.get('identity_user_id', 'Unknown')}",
                "测试账号2": f"{identity_b.get('role', 'Unknown')}用户{identity_b.get('identity_user_id', 'Unknown')}",
                "测试账号1请求头": json.dumps(dict(request_a.get("headers") or {}), ensure_ascii=False),
                "测试账号2请求头": json.dumps(dict(request_b.get("headers") or {}), ensure_ascii=False),
                "测试账号1响应状态": response_a["status_code"],
                "测试账号2响应状态": response_b["status_code"],
                "测试账号1响应体": response_a["response_body"],
                "测试账号2响应体": response_b["response_body"],
                "测试结果": "存在越权" if is_vuln else "正常",
                "风险等级": {
                    "high": "高风险",
                    "medium": "中风险",
                    "low": "低风险"
                }.get(str(risk).lower(), "低风险"),
                "备注": f"策略:{strategy}, 类型:{test_type}, 相似度:{round(content_similarity, 4)}"
            }, ensure_ascii=False)
        }
        result_buf.append(result_item)

    async def _replay_single_identity_case(case: Dict[str, Any]) -> None:
        """单身份测试（兼容旧逻辑）"""
        nonlocal done_count, fail_count, result_buf, last_sent_ms
        
        record = case["record"]
        mod = case["modified"]
        method = str(mod.get("method") or "GET").upper()
        url = str(mod.get("url") or "")
        headers = dict(mod.get("headers") or {})
        body = mod.get("body")
    
        logger.info("=" * 60)
        logger.info(f"🔄 [REPLAY] 开始单身份测试 第 {done_count + 1} 条")
        logger.info("=" * 60)
        
        # 限速
        await asyncio.sleep(max(0.0, 1.0 / max(_REPLAY_RPS, 0.001)))
    
        # 执行请求
        orig_resp = {
            "status": int(record.get("response_status") or 0),
            "text": _safe_preview(record.get("response_body"), 1024),
        }
        modified_resp = await _execute_http_request({"method": method, "url": url, "headers": headers, "request_body": body})

        logger.info(f"[REPLAY] 📥 原始响应: status={orig_resp['status']} body={orig_resp['text']}")
        logger.info(f"[REPLAY] 📤 修改后响应: status={modified_resp['status']} body={modified_resp['text']}")
    
        # 分析
        compare = compare_responses(
            {"status": orig_resp["status"], "text": orig_resp["text"], "headers": record.get("response_headers") or {}},
            {"status": modified_resp["status"], "text": modified_resp["text"], "headers": headers},
        )
        detector = detect_privilege_escalation(
            original_identity_role=None,
            target_identity_role=(case.get("identity") or {}).get("role"),
            original_user_id=str(record.get("user_id") or ""),
            target_user_id=str((case.get("identity") or {}).get("identity_user_id") or (case.get("identity") or {}).get("user_id") or ""),
        )
        risk = map_excel_risk_level(orig_resp["status"], modified_resp["status"], float(compare.get("content_similarity") or 0.0))
        evidence = build_evidence(orig_resp, modified_resp, compare, detector)
        is_vuln = bool(risk in ("HIGH", "MEDIUM"))

        # 构造结果（保持原有逻辑）
        _conf_map = {"high": 0.90, "medium": 0.60, "low": 0.30}
        _conf_str = str(detector.get("confidence") or "").lower()
        _conf_num = _conf_map.get(_conf_str, 0.30)
        _target_uid = str((case.get("identity") or {}).get("identity_user_id") or (case.get("identity") or {}).get("user_id") or "")
        _request_body_full = ""
        try:
            if isinstance(body, (dict, list)):
                import json as _json
                _request_body_full = _json.dumps(body, ensure_ascii=False)
            else:
                _request_body_full = str(body or "")
        except Exception:
            _request_body_full = str(body or "")
        
        result_item = {
            "id": record.get("id"),
            "index": record.get("index"),
            "method": method,
            "url": url,
            "requestHeadersPreview": _minimize_headers(headers),
            "requestBodyPreview": _safe_preview(body, 128),
            "request_body": _request_body_full,
            "original_status": orig_resp["status"],
            "modified_status": modified_resp["status"],
            
            # 新增：使用更直观的字段名（单身份测试）
            "identity1_body": modified_resp["text"],  # 修改后的响应体
            "identity2_body": orig_resp["text"],     # 原始响应体
            "isVulnerable": bool(is_vuln),
            "risk_level": str(risk).lower(),
            "content_similarity": round(float(compare.get("content_similarity") or 0.0), 4),
            "privilege_type": detector.get("type"),
            "confidence": _conf_num,
            "confidenceLevel": _conf_str,
            "evidence_json": json.dumps(evidence, ensure_ascii=False),
            "strategy": case.get("strategy"),
            "test_type": detector.get("type"),
            "identity_1": _target_uid,
            "identity_2": str(record.get("user_id") or ""),
            "result_summary": f"risk={str(risk).lower()}, type={detector.get('type')}, similarity={round(float(compare.get('content_similarity') or 0.0), 4)}",
        }
        result_buf.append(result_item)
        events.on_analyzed({"task_id": task_id, "is_vuln": bool(is_vuln), "risk": risk})
        done_count += 1
    
        if modified_resp["status"] >= 400 or modified_resp["status"] == 0:
            fail_count += 1
            logger.warning(f"[REPLAY] ⚠️ 请求失败: 状态码 {modified_resp['status']}")
    
        logger.info(f"[REPLAY] ✅ 回放完成 ({done_count}/{total})")
        logger.info("=" * 60)
    
        # 批量上报与进度
        now_ms = _now_ms()
        if len(result_buf) >= _REPORT_BATCH_SIZE or (now_ms - last_sent_ms) >= int(_REPORT_BATCH_INTERVAL_SEC * 1000):
            await _send_results(api, task_id, result_buf)
            last_sent_ms = now_ms
        await _progress(api, task_id, done_count, total, f"replayed_{done_count}/{total}")

    async def _worker(case: Dict[str, Any]) -> None:
        async with sem:
            await _replay_one(case)

    tasks = [asyncio.create_task(_worker(c)) for c in cases]
    await asyncio.gather(*tasks, return_exceptions=False)
    # 发送剩余结果
    await _send_results(api, task_id, result_buf)

    # 6) finish - 添加统计日志
    logger.info(f"[PERMISSION-TASK] 📊 步骤6: 回放完成统计")
    logger.info(f"[PERMISSION-TASK]   - 成功回放: {len(result_buf)} 条")
    logger.info(f"[PERMISSION-TASK]   - 失败回放: {fail_count} 条")
    logger.info(f"[PERMISSION-TASK]   - 总计处理: {len(result_buf) + fail_count} 条")
    
    # 统计漏洞发现情况
    vulnerability_count = sum(1 for result in result_buf if result.get('isVulnerable', False))
    logger.info(f"[PERMISSION-TASK]   - 发现漏洞: {vulnerability_count} 条")
    
    # 失败策略：整体错误数超过阈值中止
    abort = (total > 0) and (fail_count / max(total, 1.0) > _FAIL_RATIO_ABORT)
    success = not abort
    try:
        await api.complete(task_id, success)
    except Exception:
        success = False
    events.on_completed({"task_id": task_id, "success": success})
    
    # 最终总结日志
    if success:
        logger.info(f"[PERMISSION-TASK] ✅ 越权测试任务完成: {task_id}")
    else:
        logger.info(f"[PERMISSION-TASK] ❌ 越权测试任务失败: {task_id} (失败率过高: {fail_count}/{total})")
    
    logger.info(f"[PERMISSION-TASK] ═══════════════════════════════════════════")
    
    try:
        await api.close()
    except Exception:
        pass
    return success
