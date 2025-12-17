from __future__ import annotations

import json
import time
import asyncio
import logging
from typing import Any, Dict
from urllib import request as _urlreq, error as _urlerr

from .backend_client import BackendAPI, BackendAPIError

# 模块：京ME发送器
# 说明：负责从后端获取TeamToken与发送配置，并构造互动卡片请求进行发送
_logger = logging.getLogger("sensitive_check_local")

_cached_app_token: Dict[str, Any] = {"token": None, "expiresAt": 0}
_cached_team_token: Dict[str, Any] = {"token": None, "expiresAt": 0}
_SAFETY_MS_APP = 5000
_SAFETY_MS_TEAM = 5000


def _post_json_blocking(url: str, payload_str: str, timeout: float, headers: dict | None = None) -> tuple[int, str]:
    """阻塞式JSON POST请求（用于京ME发送）"""
    _headers = {"Content-Type": "application/json"}
    try:
        if headers:
            _headers.update({str(k): str(v) for k, v in headers.items() if str(k).strip() and str(v).strip()})
    except Exception:
        pass
    req = _urlreq.Request(url=url, data=payload_str.encode("utf-8"), headers=_headers, method="POST")
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
    except Exception as e:
        return 599, str(e)


async def fetch_team_token(backend: BackendAPI) -> Dict[str, Any]:
    now_ms = int(time.time() * 1000)
    if _cached_team_token.get("token") and now_ms < int(_cached_team_token.get("expiresAt") or 0) - _SAFETY_MS_TEAM:
        try:
            _logger.info("[通知] 使用缓存的TeamToken，过期时间=%s", _cached_team_token.get("expiresAt"))
        except Exception:
            pass
        return {"token": _cached_team_token.get("token"), "expiresAt": _cached_team_token.get("expiresAt")}
    cfg = await fetch_send_config(backend)
    app_key = str(cfg.get("appKey") or "").strip()
    app_secret = str(cfg.get("appSecret") or "").strip()
    app_token_url = str(cfg.get("appTokenUrl") or "").strip()
    team_token_url = str(cfg.get("teamTokenUrl") or "").strip()
    open_team_id = str(cfg.get("openTeamId") or "").strip()
    timeout_sec = float(cfg.get("readTimeout") or 10.0)
    loop = asyncio.get_running_loop()
    try:
        _logger.info("[通知] 拉取配置用于获取Token openTeamId=%s appTokenUrl=%s teamTokenUrl=%s", open_team_id, app_token_url, team_token_url)
    except Exception:
        pass
    if not (_cached_app_token.get("token") and now_ms < int(_cached_app_token.get("expiresAt") or 0) - _SAFETY_MS_APP):
        app_req = json.dumps({"appKey": app_key, "appSecret": app_secret}, ensure_ascii=False)
        status1, resp1 = await loop.run_in_executor(None, _post_json_blocking, app_token_url, app_req, timeout_sec, None)
        if status1 != 200:
            try:
                _logger.error("[通知] 获取AppToken失败 status=%s 响应预览=%s", status1, resp1[:200] if isinstance(resp1, str) else resp1)
            except Exception:
                pass
            raise BackendAPIError(f"get app token failed: HTTP {status1}")
        try:
            app_data = json.loads(resp1)
        except Exception:
            app_data = {}
        app_access_token = str(((app_data.get("data") or {}).get("appAccessToken") or "")).strip()
        exp_in_app = int(((app_data.get("data") or {}).get("expireIn") or 0))
        _cached_app_token["token"] = app_access_token
        _cached_app_token["expiresAt"] = now_ms + max(0, exp_in_app * 1000)
        try:
            _logger.info("[通知] 获取AppToken成功，过期时间=%s", _cached_app_token.get("expiresAt"))
        except Exception:
            pass
    else:
        app_access_token = str(_cached_app_token.get("token") or "")
        try:
            _logger.info("[通知] 使用缓存的AppToken，过期时间=%s", _cached_app_token.get("expiresAt"))
        except Exception:
            pass
    team_req = json.dumps({"appAccessToken": app_access_token, "openTeamId": open_team_id}, ensure_ascii=False)
    status2, resp2 = await loop.run_in_executor(None, _post_json_blocking, team_token_url, team_req, timeout_sec, None)
    if status2 != 200:
        try:
            _logger.error("[通知] 获取TeamToken失败 status=%s 响应预览=%s", status2, resp2[:200] if isinstance(resp2, str) else resp2)
        except Exception:
            pass
        raise BackendAPIError(f"get team token failed: HTTP {status2}")
    try:
        team_data = json.loads(resp2)
    except Exception:
        team_data = {}
    tok = str(((team_data.get("data") or {}).get("teamAccessToken") or "")).strip()
    exp_in = int(((team_data.get("data") or {}).get("expireIn") or 0))
    expires_at = int(time.time() * 1000) + max(0, exp_in * 1000)
    _cached_team_token["token"] = tok
    _cached_team_token["expiresAt"] = expires_at
    try:
        _logger.info("[通知] 获取TeamToken成功，过期时间=%s", expires_at)
    except Exception:
        pass
    return {"token": tok, "expiresAt": expires_at}


async def fetch_send_config(backend: BackendAPI) -> Dict[str, Any]:
    """获取京ME发送配置并打印关键字段"""
    data = await backend._request("GET", "/api/jingme/send-config")
    payload = data.get("data") or data
    try:
        preview = {k: payload.get(k) for k in ["appId","tenantId","robotId","sendJUEMsgUrl","templateCardId","templateCardVersion"]}
        _logger.info("[通知] 获取发送配置=%s", json.dumps(preview, ensure_ascii=False))
    except Exception:
        pass
    return payload


async def send_interactive_card(backend: BackendAPI,
                                erp: str,
                                variables: Dict[str, Any],
                                template_card_id: str,
                                template_card_version: str,
                                team_token_info: Dict[str, Any] | None = None) -> Dict[str, Any]:
    token_info = team_token_info or await fetch_team_token(backend)
    token = str(token_info.get("token") or "").strip()
    if not token:
        raise BackendAPIError("missing team token")

    cfg = await fetch_send_config(backend)
    send_url = str(cfg.get("sendJUEMsgUrl") or "").strip()
    app_id = str(cfg.get("appId") or "").strip()
    tenant_id = str(cfg.get("tenantId") or "").strip()
    robot_id = str(cfg.get("robotId") or "").strip()
    timeout_sec = float(cfg.get("readTimeout") or 10.0)

    req_id = __import__("uuid").uuid4().hex
    date_time = int(time.time() * 1000)

    payload = {
        "appId": app_id,
        "erp": erp,
        "tenantId": tenant_id,
        "requestId": req_id,
        "dateTime": date_time,
        "params": {
            "robotId": robot_id,
            "data": {
                "reload": False,
                "cardData": {
                    "templateCardId": template_card_id,
                    "templateCardVersion": template_card_version,
                    "templateCardVariable": variables or {}
                },
                "forward": {"reload": False}
            }
        }
    }

    body_str = json.dumps(payload, ensure_ascii=False)
    headers = {"Authorization": f"Bearer {token}"}
    loop = asyncio.get_running_loop()
    try:
        keys = list((variables or {}).keys())
        _logger.info("[通知] 发送京ME互动卡片 erp=%s 卡片ID=%s 版本=%s 变量数量=%s 变量键=%s 目标URL=%s", erp, template_card_id, template_card_version, len(keys), keys[:10], send_url)
    except Exception:
        pass
    status, resp_txt = await loop.run_in_executor(None, _post_json_blocking, send_url, body_str, timeout_sec, headers)
    if status != 200:
        _logger.error("[通知] 发送失败 status=%s 响应=%s", status, resp_txt[:300] if isinstance(resp_txt, str) else resp_txt)
        raise BackendAPIError(f"send JUEMsg failed: HTTP {status}")
    try:
        data = json.loads(resp_txt)
    except Exception:
        data = {"success": True}
    try:
        _logger.info("[通知] 发送结果=%s", json.dumps(data, ensure_ascii=False)[:300])
    except Exception:
        pass
    return data