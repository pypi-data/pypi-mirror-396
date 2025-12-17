from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List

from .backend_client import build_backend_api_from_context, BackendAPIError
from .jingme_sender import send_interactive_card


# 模块：通知调度器
# 说明：定期从后端拉取待通知项并调用京ME发送器进行发送，然后回写结果
_logger = logging.getLogger("sensitive_check_local")


async def run_once(context: Dict[str, Any]) -> Dict[str, Any]:
    backend = build_backend_api_from_context(context)
    # 拉取配置（用于频率控制，当前仅日志）
    try:
        cfg_resp = await backend._request("GET", "/api/realtime/notify/config")
        cfg = cfg_resp.get("data") or cfg_resp
        _logger.info("[通知] 拉取批次通知配置=%s", json.dumps(cfg, ensure_ascii=False)[:300])
    except Exception as e:
        _logger.warning("[通知] 获取配置失败: %s", e)
        cfg = {}

    # 拉取待通知
    try:
        pending_resp = await backend._request("GET", "/api/realtime/notify/pending")
        items: List[Dict[str, Any]] = pending_resp.get("data") or []
        try:
            _logger.info("[通知] 待通知项数量=%s", len(items))
        except Exception:
            pass
    except BackendAPIError as e:
        _logger.error("[notify] pull pending failed: %s", e)
        return {"ok": False, "error": str(e)}

    results: List[Dict[str, Any]] = []
    seen: set[str] = set()
    token_info: Dict[str, Any] | None = None
    if items:
        try:
            token_info = await send_interactive_card.__globals__["fetch_team_token"](backend)
        except Exception as e:
            _logger.error("[通知] 预取TeamToken失败: %s", e)
            token_info = None
    for it in items:
        try:
            dedup = str(it.get("dedupKey") or "")
            if dedup:
                if dedup in seen:
                    _logger.info("[通知] 跳过重复项 dedupKey=%s", dedup)
                    continue
                seen.add(dedup)
            erp = (it.get("recipients") or [""])[0]
            vars_ = it.get("variables") or {}
            try:
                _logger.info("[通知] 准备发送项 id=%s erp=%s 项目=%s 任务=%s", it.get("id"), erp, it.get("projectName"), it.get("taskName"))
            except Exception:
                pass
            # 模板固定为 Java 端常量（dbc6fhteo03UvYG9CXcpr / 0.0.8），与服务端保持一致
            card_id = vars_.get("templateCardId") or "dbc6fhteo03UvYG9CXcpr"
            card_ver = vars_.get("templateCardVersion") or "0.0.8"
            try:
                _logger.info("[通知] 待发送项 erp=%s 任务=%s 时间窗=[%s,%s] 变量键=%s", erp, it.get("taskId"), it.get("windowStartMs"), it.get("windowEndMs"), list(vars_.keys())[:10])
            except Exception:
                pass
            send_res = await send_interactive_card(backend, erp, vars_, card_id, card_ver, token_info)
            results.append({
                "id": it.get("id"),
                "status": "SUCCESS",
                "errorMsg": None,
                "projectId": it.get("projectId"),
                "taskId": it.get("taskId"),
                "windowStartMs": it.get("windowStartMs"),
                "windowEndMs": it.get("windowEndMs"),
                "creatorUserId": it.get("creatorUserId"),
            })
        except Exception as e:
            _logger.error("[notify] send failed: %s", e)
            results.append({
                "id": it.get("id"),
                "status": "FAILED",
                "errorMsg": str(e),
                "projectId": it.get("projectId"),
                "taskId": it.get("taskId"),
                "windowStartMs": it.get("windowStartMs"),
                "windowEndMs": it.get("windowEndMs"),
                "creatorUserId": it.get("creatorUserId"),
            })

    # 回写结果
    try:
        ack_payload = {"items": results}
        ack_resp = await backend._request("POST", "/api/realtime/notify/ack", json_body=ack_payload)
        _logger.info("[通知] 回写ack响应=%s", json.dumps(ack_resp, ensure_ascii=False)[:300])
    except BackendAPIError as e:
        _logger.error("[通知] 回写ack失败: %s", e)

    return {"ok": True, "count": len(results)}


async def run_scheduler(context: Dict[str, Any], interval_sec: int = 30):
    while True:
        try:
            res = await run_once(context)
            _logger.info("[通知] 本轮发送结果=%s", res)
        except Exception as e:
            _logger.error("[通知] 调度器异常: %s", e)
        await asyncio.sleep(max(1, int(interval_sec)))