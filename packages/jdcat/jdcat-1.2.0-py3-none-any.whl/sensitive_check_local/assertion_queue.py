from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

import httpx
import logging

from .backend_client import BackendAPI, param_test_result_check_by_interface_id, param_test_result_list, param_test_list
from .config import load_config

AUTOBOTS_URL = "http://autobots-bk.jd.local/autobots/api/v1/searchAiRequest"
_logger = logging.getLogger("sensitive_check_local")

# 固定头（按需求写死在代码中）
FIXED_HEADERS = {
    "autobots-agent-id": "57608",
    "autobots-token": "6d30ef7483ac48c9b82741f897ad2afa",
    "Content-Type": "application/json; charset=utf-8",
}

class AssertionQueue:
    def __init__(self):
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._worker_tasks: List[asyncio.Task] = []
        self._worker_count: int = 1

    async def start(self):
        if not self._worker_tasks:
            try:
                cfg = load_config() or {}
                cnt = int((((cfg.get("paramTest") or {}).get("assertionWorkerCount")) or 1))
            except Exception:
                cnt = 1
            self._worker_count = cnt if cnt > 0 else 1
            for _ in range(self._worker_count):
                self._worker_tasks.append(asyncio.create_task(self._worker()))

    async def enqueue_interface(self, api: BackendAPI, interface_id: int, erp: Optional[str] = None):
        try:
            try:
                if _logger.isEnabledFor(logging.DEBUG):
                    _logger.debug("【入参断言】入队接口 interfaceId=%s", str(interface_id))
            except Exception:
                pass
            data = await param_test_result_check_by_interface_id(api, int(interface_id))
            payload = (data.get("data") or data) if isinstance(data, dict) else {}
            rows: List[Dict[str, Any]] = (payload.get("list") or [])
            try:
                if _logger.isEnabledFor(logging.DEBUG):
                    _logger.debug("【入参断言】待断言用例数 count=%s", len(rows))
            except Exception:
                pass
            # Fallback：按任务维度拉取后过滤 domain+path
            if not rows:
                pass
            for r in rows:
                # 构造断言所需最小上下文
                item = {
                    "id": int(r.get("id")),
                    "ssRtTaskId": int(r.get("ssRtTaskId")) if r.get("ssRtTaskId") is not None else None,
                    "taskId": r.get("taskId"),
                    "caseDescription": r.get("caseDescription") or "",
                    "expectedResult": r.get("expectedResult") or "",
                    "responseBody": r.get("responseBody") or "",
                    "requestUrl": r.get("requestUrl") or "",
                    "erp": erp,
                }
                await self._queue.put({"api": api, "payload": item})
                try:
                    if _logger.isEnabledFor(logging.DEBUG):
                        _logger.debug("【入参断言】已入队 rid=%s case=%s", item["id"], (item.get("caseDescription") or "")[:100])
                except Exception:
                    pass
        except Exception:
            # 静默处理，避免阻断主流程
            pass

    async def _worker(self):
        session = httpx.AsyncClient(timeout=15.0)
        try:
            try:
                cfg = load_config() or {}
                interval_sec = int((((cfg.get("paramTest") or {}).get("assertionIntervalSec")) or 5))
            except Exception:
                interval_sec = 5
            while True:
                pack = await self._queue.get()
                api: BackendAPI = pack.get("api")
                item: Dict[str, Any] = pack.get("payload") or {}
                try:
                    try:
                        if _logger.isEnabledFor(logging.DEBUG):
                            _logger.debug("【入参断言】开始处理 rid=%s", str(item.get("id")))
                    except Exception:
                        pass
                    await self._process_one(session, api, item)
                except Exception:
                    # 单条失败不影响后续处理
                    try:
                        _logger.warning("【入参断言】处理失败 rid=%s", str(item.get("id")))
                    except Exception:
                        pass
                await asyncio.sleep(interval_sec)
        finally:
            try:
                await session.aclose()
            except Exception:
                pass

    async def _process_one(self, session: httpx.AsyncClient, api: BackendAPI, item: Dict[str, Any]):
        rid = int(item.get("id"))
        ss_rt_task_id = item.get("ssRtTaskId")
        # 提取域名与路径以便任务维度回退解析ERP
        domain = ""
        path = ""
        try:
            from urllib.parse import urlsplit
            u = str(item.get("requestUrl") or "")
            p = urlsplit(u)
            domain = p.netloc
            path = p.path or "/"
        except Exception:
            pass
        erp = item.get("erp")
        if not erp:
            erp = await _resolve_rt_task_erp(api, ss_rt_task_id, domain, path, item.get("taskId"))
        try:
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("【入参断言】解析ERP rid=%s ssRtTaskId=%s erp=%s", rid, str(ss_rt_task_id), str(erp or ""))
        except Exception:
            pass
        # 构造 keyword 字符串
        keyword_obj = {
            "caseDescription": item.get("caseDescription") or "",
            "expectedResult": item.get("expectedResult") or "",
            "responseBody": item.get("responseBody") or "",
        }
        keyword_str = json.dumps(keyword_obj, ensure_ascii=False)
        ts13 = str(int(time.time() * 1000))
        if not erp:
            try:
                _logger.warning("【入参断言】ERP缺失，跳过断言 rid=%s", rid)
            except Exception:
                pass
            return
        body = {
            "traceId": ts13,
            "reqId": ts13,
            "erp": str(erp),
            "keyword": keyword_str,
        }

        # 第一次：触发生成
        try:
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("【入参断言】触发生成 rid=%s body.preview=%s", rid, json.dumps(body, ensure_ascii=False)[:200])
        except Exception:
            pass
        _ = await _post_autobots(session, body)
        # 后续：按配置最多尝试查询 N 次，期间若拿到结果则提前完成
        try:
            cfg = load_config() or {}
            delay_sec = int((((cfg.get("paramTest") or {}).get("assertionCheckDelaySec")) or 20))
        except Exception:
            delay_sec = 20
        try:
            cfg2 = load_config() or {}
            max_attempts = int((((cfg2.get("paramTest") or {}).get("assertionCheckMaxAttempts")) or 5))
        except Exception:
            max_attempts = 5
        data = {}
        for i in range(max(1, max_attempts)):
            try:
                if _logger.isEnabledFor(logging.DEBUG):
                    _logger.debug("【入参断言】等待生成 rid=%s sleep=%ss attempt=%s/%s", rid, delay_sec, i + 1, max_attempts)
            except Exception:
                pass
            await asyncio.sleep(delay_sec)
            try:
                if _logger.isEnabledFor(logging.DEBUG):
                    _logger.debug("【入参断言】查询结果 rid=%s attempt=%s/%s", rid, i + 1, max_attempts)
            except Exception:
                pass
            resp = await _post_autobots(session, body)
            if not isinstance(resp, dict):
                data = {}
            else:
                data = resp.get("data") or {}
                if (resp.get("code") and int(resp.get("code")) != 200) and not data:
                    try:
                        _logger.warning("【入参断言】外部断言查询失败 | rid=%s | code=%s | msg=%s attempt=%s/%s", rid, resp.get("code"), resp.get("msg"), i + 1, max_attempts)
                    except Exception:
                        pass
                    data = {}
            status = str(data.get("status") or "").lower()
            if status == "finished":
                break
        if str(data.get("status") or "").lower() != "finished":
            try:
                if _logger.isEnabledFor(logging.DEBUG):
                    _logger.debug("【入参断言】最终未完成 rid=%s status=%s attempts=%s", rid, str(data.get("status") or ""), max_attempts)
            except Exception:
                pass
            return
        response_all = str(data.get("responseAll") or "")
        try:
            parsed = json.loads(response_all)
        except Exception:
            parsed = {}
        passed = bool(parsed.get("passed"))
        risk = str(parsed.get("risk") or "")
        reason = str(parsed.get("reason") or "")
        try:
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("【入参断言】解析结果 rid=%s passed=%s risk=%s reason.preview=%s", rid, str(passed), risk, reason[:120])
        except Exception:
            pass

        # 回写数据库
        await _update_assertion(api, rid, passed, risk, reason)


async def _resolve_rt_task_erp(api: BackendAPI, ss_rt_task_id: Optional[int], domain: Optional[str], path: Optional[str], task_id: Optional[int]) -> Optional[str]:
    # 优先：参数测试任务列表（包含erp），按接口apiKey过滤
    try:
        api_key = (str(domain or "") + str(path or ""))
        if api_key:
            lst = await param_test_list(api, {"page": 1, "pageSize": 1, "status": "completed", "apiKey": api_key})
            payload = (lst.get("data") or lst) if isinstance(lst, dict) else {}
            rows = (payload.get("list") or [])
            if rows:
                erp = rows[0].get("erp")
                if erp:
                    return str(erp)
    except Exception:
        pass

    # 次级：尝试实时任务详情（若后端支持按id查询）
    try:
        if ss_rt_task_id is not None:
            data = await api._request("GET", f"/api/realtime/tasks/detail?id={int(ss_rt_task_id)}")
            row = (data.get("data") or {}).get("row") or (data.get("row") or {})
            created_by = row.get("createdBy")
            if created_by:
                return str(created_by)
    except Exception:
        pass

    # 兜底：返回示例账号或空（保证外部接口入参完整）
    return None


async def _post_autobots(session: httpx.AsyncClient, body: Dict[str, Any]) -> Dict[str, Any]:
    try:
        try:
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("【入参断言】外部断言请求 | url=%s | headersKeys=%s | body=%s",
                              AUTOBOTS_URL,
                              list(FIXED_HEADERS.keys()),
                              json.dumps(body, ensure_ascii=False))
        except Exception:
            pass

        resp = await session.post(AUTOBOTS_URL, headers=FIXED_HEADERS, json=body)
        status = resp.status_code
        text = None
        try:
            data = resp.json()
            preview = json.dumps(data, ensure_ascii=False)
            if len(preview) > 2000:
                preview = preview[:2000] + "..."
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("【入参断言】外部断言响应 | status=%s | body=%s", status, preview)
            return data
        except Exception:
            try:
                text = resp.text
                if text is not None and len(text) > 2000:
                    text = text[:2000] + "..."
                _logger.warning("【入参断言】外部断言响应非JSON | status=%s | body=%s", status, text or "<empty>")
            except Exception:
                _logger.warning("【入参断言】外部断言响应读取失败 | status=%s", status)
            return {}
    except Exception:
        try:
            _logger.warning("【入参断言】外部断言接口调用异常")
        except Exception:
            pass
        return {}


async def _update_assertion(api: BackendAPI, rid: int, passed: bool, risk: str, reason: str) -> None:
    payload = {
        "passed": bool(passed),
        "risk": str(risk or ""),
        "actualResult": str(reason or ""),
    }
    try:
        try:
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("【入参断言】写回后端 | rid=%s | path=%s | body=%s",
                              rid,
                              f"/api/param-test/results/{int(rid)}/assertion",
                              json.dumps(payload, ensure_ascii=False))
        except Exception:
            pass
        resp = await api._request("POST", f"/api/param-test/results/{int(rid)}/assertion", json_body=payload)
        try:
            preview = json.dumps(resp, ensure_ascii=False)
            if len(preview) > 2000:
                preview = preview[:2000] + "..."
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("【入参断言】后端写库响应 | rid=%s | body=%s", rid, preview)
        except Exception:
            pass
    except Exception:
        try:
            _logger.warning("【入参断言】写回后端失败 rid=%s", rid)
        except Exception:
            pass
