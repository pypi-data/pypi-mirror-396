from __future__ import annotations

import json
import socket
import time
from urllib import request as _urlreq, error as _urlerr
from typing import Any, Dict, List, Tuple

_HELPER_HOST = "127.0.0.1"
_HELPER_PORT = 17901
_BASE = f"http://{_HELPER_HOST}:{_HELPER_PORT}"

_DEFAULT_TIMEOUT = 1.0  # seconds


class RootHelperError(RuntimeError):
    pass


def _http_get(path: str, timeout: float = _DEFAULT_TIMEOUT) -> Tuple[int, str]:
    req = _urlreq.Request(url=_BASE + path, method="GET")
    try:
        with _urlreq.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            body = resp.read()
            body_txt = body.decode("utf-8", errors="ignore") if isinstance(body, (bytes, bytearray)) else str(body)
            return status, body_txt
    except _urlerr.HTTPError as e:
        try:
            b = e.read()
            body_txt = b.decode("utf-8", errors="ignore") if isinstance(b, (bytes, bytearray)) else str(b)
        except Exception:
            body_txt = str(e)
        return int(getattr(e, "code", 500) or 500), body_txt
    except (socket.timeout, _urlerr.URLError, ConnectionError) as e:
        return 599, str(e)
    except Exception as e:
        return 599, str(e)


def _http_post_json(path: str, payload: Dict[str, Any], timeout: float = _DEFAULT_TIMEOUT) -> Tuple[int, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = _urlreq.Request(url=_BASE + path, data=data, headers=headers, method="POST")
    try:
        with _urlreq.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            body = resp.read()
            body_txt = body.decode("utf-8", errors="ignore") if isinstance(body, (bytes, bytearray)) else str(body)
            return status, body_txt
    except _urlerr.HTTPError as e:
        try:
            b = e.read()
            body_txt = b.decode("utf-8", errors="ignore") if isinstance(b, (bytes, bytearray)) else str(b)
        except Exception:
            body_txt = str(e)
        return int(getattr(e, "code", 500) or 500), body_txt
    except (socket.timeout, _urlerr.URLError, ConnectionError) as e:
        return 599, str(e)
    except Exception as e:
        return 599, str(e)


def health(timeout: float = _DEFAULT_TIMEOUT) -> bool:
    """
    Root Helper 健康检查：GET /health，返回 {"ok": true} 视为就绪
    """
    code, body = _http_get("/health", timeout=timeout)
    if code != 200:
        return False
    try:
        obj = json.loads(body)
        return bool(obj.get("ok", False))
    except Exception:
        return False


def wait_for_helper(timeout: float = 8.0, interval: float = 0.5) -> bool:
    """
    在给定的时间窗口内轮询 /health，等待 Root Helper 就绪。
    - timeout: 最大等待秒数（默认 8s）
    - interval: 轮询间隔（默认 0.5s）
    返回 True 表示已就绪；False 表示最终仍不可达。
    """
    deadline = time.time() + max(0.0, float(timeout))
    itv = max(0.05, float(interval))
    while time.time() < deadline:
        if health(timeout=_DEFAULT_TIMEOUT):
            return True
        time.sleep(itv)
    # 最后再做一次短超时探测
    return health(timeout=_DEFAULT_TIMEOUT)


def health_retry(timeout: float = 5.0, interval: float = 0.5) -> bool:
    """
    简化封装：对 /health 进行短期重试（默认 5s 窗口）
    """
    return wait_for_helper(timeout=timeout, interval=interval)


def enable(host: str, port: int, services: List[str], bypass: List[str] | None = None, timeout: float = _DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    启用系统代理（Root Helper 端）。默认使用短超时，等待行为由上层通过 wait_for_helper 控制。
    """
    if not host or not port or not services:
        raise RootHelperError("invalid enable arguments")
    payload = {
        "host": str(host),
        "port": int(port),
        "services": [str(s).strip() for s in services if str(s).strip()],
        "bypass": [str(b).strip() for b in (bypass or []) if str(b).strip()],
    }
    code, body = _http_post_json("/enable", payload, timeout=timeout)
    if code != 200:
        raise RootHelperError(f"helper enable failed: http={code} body={body[:200]}")
    try:
        obj = json.loads(body)
    except Exception:
        obj = {}
    if not obj.get("ok"):
        raise RootHelperError(f"helper enable failed: {body[:200]}")
    return obj


def restore(services: List[str], timeout: float = _DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    恢复系统代理（Root Helper 端）。默认使用短超时，等待行为由上层通过 wait_for_helper 控制。
    """
    if not services:
        raise RootHelperError("invalid restore arguments")
    payload = {"services": [str(s).strip() for s in services if str(s).strip()]}
    code, body = _http_post_json("/restore", payload, timeout=timeout)
    if code != 200:
        raise RootHelperError(f"helper restore failed: http={code} body={body[:200]}")
    try:
        obj = json.loads(body)
    except Exception:
        obj = {}
    if not obj.get("ok"):
        raise RootHelperError(f"helper restore failed: {body[:200]}")
    return obj