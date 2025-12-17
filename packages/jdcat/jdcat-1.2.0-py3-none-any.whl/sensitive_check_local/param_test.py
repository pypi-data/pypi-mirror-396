from __future__ import annotations

import os
import json
import time
import asyncio
from typing import Any, Dict, List, Optional
import httpx
from . import autobot_config as _ac
import logging

from .backend_client import (
    BackendAPI,
    build_backend_api_from_context,
    param_test_create,
    param_test_list,
    param_test_complete,
    param_test_fail,
    param_test_details_batch,
    param_test_details_raw,
    project_domain_by_host,
)

_rate_window: List[float] = []
_rate_lock = asyncio.Lock()
_logger = logging.getLogger("sensitive_check_local")
_retry_marks: set[str] = set()
_executed_once: set[int] = set()
_origin_items: Dict[str, Dict[str, Any]] = {}

async def _rate_limit_allow(max_per_minute: int = 3) -> bool:
    async with _rate_lock:
        now = time.time()
        window = [t for t in _rate_window if now - t < 60]
        if len(window) >= max_per_minute:
            _rate_window[:] = window
            try:
                _logger.info("[param-test] rate_limited window_count=%s", len(window))
            except Exception:
                pass
            return False
        window.append(now)
        _rate_window[:] = window
        try:
            _logger.info("[param-test] rate_allow window_count=%s", len(window))
        except Exception:
            pass
        return True

def _env(name: str, default: Optional[str] = None) -> str:
    v = os.getenv(name)
    return v if v is not None else (default or "")

def _build_autobots_headers() -> Dict[str, str]:
    agent_id = _ac.AGENT_ID or _env("AUTOBOTS_AGENT_ID")
    token = _ac.TOKEN or _env("AUTOBOTS_TOKEN")
    return {
        "autobots-agent-id": agent_id,
        "autobots-token": token,
        "Content-Type": "application/json",
    }

def _autobot_auth_ready() -> bool:
    aid_code = _ac.AGENT_ID
    tok_code = _ac.TOKEN
    aid_env = _env("AUTOBOTS_AGENT_ID")
    tok_env = _env("AUTOBOTS_TOKEN")
    src = "code" if (aid_code and tok_code) else ("env" if (aid_env and tok_env) else "missing")
    try:
        _logger.info("【autobot】鉴权检查 source=%s agentId=%s token_len=%s", src, (aid_code or aid_env or ""), len((tok_code or tok_env or "")))
    except Exception:
        pass
    return (aid_code and tok_code) or (aid_env and tok_env)

async def _autobots_run_workflow(body: Dict[str, Any]) -> Dict[str, Any]:
    url = _ac.RUN_URL or _env("AUTOBOTS_RUN_URL", "http://autobots-bk.jd.local/autobots/api/v1/runWorkflow")
    async with httpx.AsyncClient(timeout=15.0) as cli:
        try:
            bp = json.dumps(body, ensure_ascii=False)
            bp = (bp[:500] + "...") if len(bp) > 500 else bp
        except Exception:
            bp = str(body)[:500]
        hdr = _build_autobots_headers()
        try:
            log_hdr = dict(hdr)
            tok = str(log_hdr.get("autobots-token") or "")
            if tok:
                log_hdr["autobots-token"] = f"***({len(tok)})"
            _logger.info("【入参测试状态】runWorkflow 请求 | url=%s | headers=%s | body=%s", url, json.dumps(log_hdr, ensure_ascii=False), bp)
        except Exception:
            _logger.info(f"【autobot-请求】runWorkflow url={url} body={bp}")
        resp = await cli.post(url, headers=hdr, json=body)
        raw = resp.text
        status = resp.status_code
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            data = {}
        try:
            rp = str(raw or "")
            rp = (rp[:500] + "...") if len(rp) > 500 else rp
            _logger.info(f"【autobot】生成-响应 http={status} preview={rp}")
        except Exception:
            pass
        return {"_raw": raw, "_status": status, "data": data}

async def _autobots_get_result(body: Dict[str, Any]) -> Dict[str, Any]:
    url = _ac.RESULT_URL or _env("AUTOBOTS_RESULT_URL", "http://autobots-bk.jd.local/autobots/api/v1/getWorkflowResult")
    async with httpx.AsyncClient(timeout=15.0) as cli:
        try:
            bp = json.dumps(body, ensure_ascii=False)
            bp = (bp[:500] + "...") if len(bp) > 500 else bp
        except Exception:
            bp = str(body)[:500]
        _logger.info(f"【autobot】拉取-请求 url={url} body={bp}")
        resp = await cli.post(url, headers=_build_autobots_headers(), json=body)
        raw = resp.text
        status = resp.status_code
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            data = {}
        try:
            rp = str(raw or "")
            rp = (rp[:500] + "...") if len(rp) > 500 else rp
            _logger.info(f"【autobot-响应】getWorkflowResult http={status} preview={rp}")
        except Exception:
            pass
        return {"_raw": raw, "_status": status, "data": data}

def _extract_query_body(item: Dict[str, Any]) -> Dict[str, Any]:
    q = item.get("query") or {}
    b = item.get("requestBody") or item.get("body") or {}
    if not isinstance(q, dict):
        try:
            q = json.loads(q)
        except Exception:
            q = {}
    if not isinstance(b, dict):
        try:
            b = json.loads(b)
        except Exception:
            b = {}
    return {"query": q, "requestBody": b}

def _compute_japi_path(domain: str, path: str, exclude_prefix: Optional[str]) -> str:
    try:
        p = path or "/"
        if not p.startswith("/"):
            p = "/" + p
        if not exclude_prefix:
            return p
        from urllib.parse import urlparse
        ex = urlparse(str(exclude_prefix))
        # 优先按URL前缀匹配（带域名）
        if ex.netloc:
            ex_path = ex.path or "/"
            if not ex_path.endswith("/"):
                # 保证作为前缀目录
                ex_path = ex_path
            if domain == ex.netloc and p.startswith(ex_path):
                rest = p[len(ex_path):]
                return ("/" + rest) if not rest.startswith("/") else (rest or "/")
        # 兼容：exclude_prefix为完整http://domain/prefix 字符串但解析失败时
        try:
            prefix_raw = str(exclude_prefix)
            # 去掉scheme，仅按 domain+path 比较
            if "://" in prefix_raw:
                prefix_raw = prefix_raw.split("://", 1)[1]
            # 组装当前完整 host+path
            full_host_path = f"{domain}{p}"
            if full_host_path.startswith(prefix_raw):
                rest = full_host_path[len(prefix_raw):]
                return ("/" + rest) if not rest.startswith("/") else (rest or "/")
        except Exception:
            pass
        return p
    except Exception:
        return path or "/"

async def handle_flow_item(item: Dict[str, Any], ctx: Dict[str, Any], *, apply_rate_limit: bool = True) -> Optional[Dict[str, Any]]:
    api = build_backend_api_from_context(ctx)
    domain = str(item.get("domain") or "").strip().lower()
    path = str(item.get("path") or "/")
    api_key = f"{domain}{path}"
    try:
        _logger.info("[param-test] handle_flow_item domain=%s path=%s", domain, path)
    except Exception:
        pass

    # 取消复用窗口拦截：每次请求均尝试生成

    # 取消已完成窗口拦截：每次请求均尝试生成

    # 读取域名配置
    app_code = None
    exclude_prefix = None
    try:
        pd = await project_domain_by_host(api, int(ctx.get("project_id")), domain)
        if isinstance(pd, dict) and isinstance(pd.get("data"), dict):
            row = pd["data"]
            app_code = row.get("japiAppCode")
            exclude_prefix = row.get("excludePrefix")
        else:
            raise RuntimeError("byDomain empty")
    except Exception:
        try:
            _logger.warning("[param-test] domain_map byDomain failed domain=%s, try list", domain)
        except Exception:
            pass
        try:
            lst = await project_domains_list(api, int(ctx.get("project_id")), domain)
            if isinstance(lst, dict) and isinstance(lst.get("data"), dict):
                items = lst["data"].get("list") or []
                for it in items:
                    if str(it.get("domain") or "").strip().lower() == domain:
                        app_code = it.get("japiAppCode")
                        exclude_prefix = it.get("excludePrefix")
                        _logger.info("[param-test] domain_map via list hit appCode=%s excludePrefix=%s", app_code, exclude_prefix)
                        break
        except Exception:
            try:
                _logger.warning("[param-test] domain_map list failed domain=%s", domain)
            except Exception:
                pass
    # excludePrefix 回退：若未配置且路径包含 /console/，按规则拼接
    try:
        if not exclude_prefix and path.startswith("/console/"):
            exclude_prefix = f"http://{domain}/console"
            _logger.info("[param-test] excludePrefix fallback=%s", exclude_prefix)
    except Exception:
        pass

    ts13 = str(int(time.time() * 1000))
    erp = await _resolve_erp(ctx, api)
    workflow_id = _env("AUTOBOTS_WORKFLOW_ID", "49039")
    original = _extract_query_body(item)
    path_val = _compute_japi_path(domain, path, exclude_prefix)
    try:
        _logger.info("[param-test] japiPath from domain=%s path=%s excludePrefix=%s -> %s", domain, path, exclude_prefix, path_val)
    except Exception:
        pass
    # 缓存本次生成对应的原始流量（按 traceId 1:1）
    try:
        _origin_items[ts13] = dict(item)
    except Exception:
        pass

    # appCode 必填校验
    if not (app_code and str(app_code).strip()):
        if getattr(_ac, "APP_CODE_DEFAULT", ""):
            app_code = _ac.APP_CODE_DEFAULT
            try:
                _logger.info("[param-test] appCode fallback=%s", app_code)
            except Exception:
                pass
        else:
            try:
                _logger.error("[param-test] missing appCode for domain=%s, skip runWorkflow", domain)
            except Exception:
                pass
            try:
                try:
                    from .config import load_config
                    cfg_force = bool(((load_config() or {}).get("paramTest") or {}).get("forceNew", True))
                except Exception:
                    cfg_force = True
                import os, re
                rt_tid_raw = (ctx.get("task_id") or ctx.get("taskId") or os.getenv("TASK_ID") or "")
                try:
                    rt_tid_num = int(re.sub(r"[^0-9]", "", str(rt_tid_raw))) if str(rt_tid_raw).strip() else None
                except Exception:
                    rt_tid_num = None
                task_payload = {
                    "projectId": int(ctx.get("project_id")),
                    "apiDomain": domain,
                    "apiPath": path,
                    "apiKey": api_key,
                    "traceId": ts13,
                    "erp": erp,
                    "workflowId": workflow_id,
                    "status": "failed",
                    "failReason": "missing japiAppCode",
                    "japiAppCode": app_code,
                    "excludePrefix": exclude_prefix,
                    "requestQuery": json.dumps(original.get("query"), ensure_ascii=False),
                    "requestBody": json.dumps(original.get("requestBody"), ensure_ascii=False),
                    "forceNew": cfg_force,
                    "rtTaskId": rt_tid_num,
                }
                await param_test_create(api, task_payload)
            except Exception:
                pass
            return {"skipped": True, "reason": "missing_appCode"}
        try:
            _logger.error("[param-test] missing appCode for domain=%s, skip runWorkflow", domain)
        except Exception:
            pass
        try:
            import os, re
            rt_tid_raw2 = (ctx.get("task_id") or ctx.get("taskId") or os.getenv("TASK_ID") or "")
            try:
                rt_tid_num2 = int(re.sub(r"[^0-9]", "", str(rt_tid_raw2))) if str(rt_tid_raw2).strip() else None
            except Exception:
                rt_tid_num2 = None
            task_payload = {
                "projectId": int(ctx.get("project_id")),
                "apiDomain": domain,
                "apiPath": path,
                "apiKey": api_key,
                "traceId": ts13,
                "erp": erp,
                "workflowId": workflow_id,
                "status": "failed",
                "failReason": "missing japiAppCode",
                "japiAppCode": app_code,
                "excludePrefix": exclude_prefix,
                "requestQuery": json.dumps(original.get("query"), ensure_ascii=False),
                "requestBody": json.dumps(original.get("requestBody"), ensure_ascii=False),
                "forceNew": True,
                "rtTaskId": rt_tid_num2,
            }
            await param_test_create(api, task_payload)
        except Exception:
            pass
        return {"skipped": True, "reason": "missing_appCode"}

    run_body = {
        "traceId": ts13,
        "erp": erp,
        "workflowId": workflow_id,
        "extParams": {
            "japiData": {
                "appCode": app_code or "",
                "path": path_val,
            },
            "originalParameters": original,
        },
    }

    try:
        if not _autobot_auth_ready():
            raise RuntimeError("autobot auth missing: set AUTOBOTS_AGENT_ID/AUTOBOTS_TOKEN")
        _logger.info("[param-test] runWorkflow start traceId=%s apiKey=%s", ts13, api_key)
        run_resp = await _autobots_run_workflow(run_body)
        try:
            preview = str(run_resp.get("_raw") or "")
            preview = (preview[:300] + "...") if len(preview) > 300 else preview
        except Exception:
            preview = ""
        _logger.info("[param-test] runWorkflow done traceId=%s http=%s status=%s preview=%s",
                     ts13,
                     str(run_resp.get("_status")),
                     (run_resp.get("data") or {}).get("status"),
                     preview)
        # 如果业务code非200，认为生成失败
        try:
            code = (run_resp.get("data") or {}).get("code")
            if code is not None and int(code) != 200:
                raise RuntimeError(f"autobot runWorkflow code={code}")
        except Exception:
            pass
    except Exception as e:
        try:
            _logger.error("[param-test] runWorkflow error traceId=%s err=%s", ts13, str(e))
        except Exception:
            pass
        # 记录失败任务，便于排查
        try:
            started_time = time.strftime("%Y-%m-%d %H:%M:%S")
            try:
                from .config import load_config
                cfg_force2 = bool(((load_config() or {}).get("paramTest") or {}).get("forceNew", True))
            except Exception:
                cfg_force2 = True
            import os, re
            rt_tid_raw3 = (ctx.get("task_id") or ctx.get("taskId") or os.getenv("TASK_ID") or "")
            try:
                rt_tid_num3 = int(re.sub(r"[^0-9]", "", str(rt_tid_raw3))) if str(rt_tid_raw3).strip() else None
            except Exception:
                rt_tid_num3 = None
            task_payload = {
                "projectId": int(ctx.get("project_id")),
                "apiDomain": domain,
                "apiPath": path,
                "apiKey": api_key,
                "traceId": ts13,
                "erp": erp,
                "workflowId": workflow_id,
                "status": "failed",
                "failReason": str(e),
                "japiAppCode": app_code,
                "excludePrefix": exclude_prefix,
                "requestQuery": json.dumps(original.get("query"), ensure_ascii=False),
                "requestBody": json.dumps(original.get("requestBody"), ensure_ascii=False),
                "forceNew": cfg_force2,
                "rtTaskId": rt_tid_num3,
            }
            _logger.info("[param-test] createTask(start failed) traceId=%s apiKey=%s", ts13, api_key)
            await param_test_create(api, task_payload)
        except Exception:
            pass
        return {"error": f"runWorkflow failed: {e}"}

    # 复用原任务：若传入 paramTaskId，则复用原 taskId，避免新增记录
    task_id = None
    try:
        ptid = item.get("paramTaskId")
        if isinstance(ptid, int) and ptid > 0:
            task_id = int(ptid)
            _logger.info("[param-test] reuse existing taskId=%s for retry domain=%s path=%s", str(task_id), domain, path)
    except Exception:
        task_id = None
    # 上报任务 in_progress（仅当未复用原任务时创建新任务）
    if task_id is None:
        try:
            started_time = time.strftime("%Y-%m-%d %H:%M:%S")
            try:
                from .config import load_config
                cfg_force3 = bool(((load_config() or {}).get("paramTest") or {}).get("forceNew", True))
            except Exception:
                cfg_force3 = True
            import os, re
            rt_tid_raw4 = (ctx.get("task_id") or ctx.get("taskId") or os.getenv("TASK_ID") or "")
            try:
                rt_tid_num4 = int(re.sub(r"[^0-9]", "", str(rt_tid_raw4))) if str(rt_tid_raw4).strip() else None
            except Exception:
                rt_tid_num4 = None
            task_payload = {
                "projectId": int(ctx.get("project_id")),
                "apiDomain": domain,
                "apiPath": path,
                "apiKey": api_key,
                "traceId": ts13,
                "erp": erp,
                "workflowId": workflow_id,
                "status": "in_progress",
                "startedTime": started_time,
                "japiAppCode": app_code,
                "excludePrefix": exclude_prefix,
                "requestQuery": json.dumps(original.get("query"), ensure_ascii=False),
                "requestBody": json.dumps(original.get("requestBody"), ensure_ascii=False),
                "forceNew": cfg_force3,
                "rtTaskId": rt_tid_num4,
                "interfaceId": item.get("interfaceId"),
            }
            _logger.info("[param-test] createTask start traceId=%s apiKey=%s", ts13, api_key)
            create_resp = await param_test_create(api, task_payload)
            if isinstance(create_resp, dict) and isinstance(create_resp.get("data"), dict):
                task_id = create_resp["data"].get("id")
            _logger.info("[param-test] createTask done id=%s traceId=%s", str(task_id), ts13)
        except Exception as e:
            try:
                _logger.error("[param-test] createTask error traceId=%s err=%s", ts13, str(e))
            except Exception:
                pass
            return {"error": f"createTask failed: {e}"}

    # 首次拉取：100s 后
    async def _fetch_once():
        try:
            await asyncio.sleep(100)
            _logger.info("[param-test] getWorkflowResult start traceId=%s", ts13)
            get_body = {"traceId": ts13, "erp": erp, "workflowId": workflow_id}
            res = await _autobots_get_result(get_body)
            await _handle_result(api, task_id, res, row={"apiDomain": domain, "apiPath": path, "traceId": ts13}, ctx=ctx)
            _logger.info("[param-test] getWorkflowResult done traceId=%s", ts13)
        except Exception as ex:
            try:
                await param_test_fail(api, int(task_id), str(ex))
            except Exception:
                pass
    asyncio.create_task(_fetch_once())

    return {"ok": True, "taskId": task_id, "traceId": ts13}

async def _handle_result(api: BackendAPI, task_id: int, res: Dict[str, Any], row: Optional[Dict[str, Any]] = None, ctx: Optional[Dict[str, Any]] = None) -> None:
    try:
        payload = res.get("data") or {}
        inner = payload.get("data") or payload
        status = str(inner.get("status") or "")
        if status != "finished":
            try:
                _logger.warning("[param-test] result not finished taskId=%s status=%s", str(task_id), status)
            except Exception:
                pass
            # 不更新失败状态，由轮询协程根据 started_time 与阈值判定
            return
        raw = inner.get("responseAll") or ""
        if not str(raw).strip():
            _logger.warning("[param-test] detailsRaw skipped empty responseAll taskId=%s", str(task_id))
            try:
                await param_test_fail(api, int(task_id), "empty responseAll")
            except Exception:
                pass
            return
        _logger.info("[param-test] detailsRaw start taskId=%s", str(task_id))
        await param_test_details_raw(api, int(task_id), str(raw))
        _logger.info("[param-test] detailsRaw done taskId=%s", str(task_id))
        try:
            det = await param_test_details_list(api, int(task_id))
            dl = (det.get('data') or {}).get('list') or []
            _logger.info("[param-test] details verify count=%s taskId=%s", len(dl), str(task_id))
        except Exception:
            _logger.info("[param-test] details verify failed taskId=%s", str(task_id))
        try:
            if not dl:
                try:
                    await param_test_fail(api, int(task_id), "details empty")
                except Exception:
                    pass
                return
        except Exception:
            pass
        # 有明细时再标记完成
        try:
            await param_test_complete(api, int(task_id))
        except Exception:
            pass
        # 轮询完成后，按配置触发一次入参测试（按接口维度），触发前进行二次检查
        try:
            try:
                from .config import load_config
                cfg = load_config() or {}
                pconf = (cfg.get("paramTest") or {})
                en = pconf.get("triggerAfterCompleteEnable")
                if en is not None and not bool(en):
                    return
                dval = pconf.get("triggerAfterCompleteDelaySec")
                delay_sec = int(dval) if dval is not None else 20
            except Exception:
                delay_sec = 20
            await asyncio.sleep(max(0, delay_sec))
            from .param_test_throttler import enqueue_param_test
            api_domain = (row or {}).get("apiDomain") or (row or {}).get("api_domain") or ""
            api_path = (row or {}).get("apiPath") or (row or {}).get("api_path") or "/"
            t13 = str((row or {}).get("traceId") or "")
            origin = None
            try:
                origin = _origin_items.get(t13)
            except Exception:
                origin = None
            base_item = {"domain": str(api_domain).strip().lower(), "path": str(api_path) or "/", "source": "post_complete", "paramTaskId": int(task_id) if task_id else None}
            item = dict(origin) if isinstance(origin, dict) else base_item
            for k, v in base_item.items():
                if item.get(k) is None:
                    item[k] = v
            if ctx is None:
                ctx = {}
            # 保证必要上下文字段存在
            run_ctx = {
                "user_id": ctx.get("user_id"),
                "project_id": ctx.get("project_id"),
                "client_id": ctx.get("client_id"),
            }
            # 独立队列触发：统一走专用入参测试队列，不进行任何复用检查
            try:
                if isinstance(task_id, int) and task_id in _executed_once:
                    _logger.info("【入参测试问题排查】跳过重复派发 post_complete taskId=%s", str(task_id))
                    return
                if isinstance(task_id, int):
                    _executed_once.add(task_id)
            except Exception:
                pass
            _logger.info("【入参测试状态】post_complete触发执行入队 domain=%s path=%s taskId=%s", item.get("domain"), item.get("path"), str(task_id))
            from .param_test_executor_queue import enqueue_execute
            await enqueue_execute(item, run_ctx)
        except Exception:
            pass
    except Exception as e:
        try:
            _logger.error("[param-test] handle_result error taskId=%s err=%s", str(task_id), str(e))
        except Exception:
            pass
        await param_test_fail(api, int(task_id), str(e))

async def poll_overdue_and_fetch(ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        api = build_backend_api_from_context(ctx)
        import datetime
        end = datetime.datetime.now()
        start = end - datetime.timedelta(minutes=90)
        q = {
            "page": 1,
            "pageSize": 100,
            "status": "in_progress",
            "dateStart": start.strftime("%Y-%m-%d %H:%M:%S"),
            "dateEnd": end.strftime("%Y-%m-%d %H:%M:%S"),
        }
        resp = await param_test_list(api, q)
        rows = []
        if isinstance(resp, dict) and isinstance(resp.get("data"), dict):
            rows = resp["data"].get("list") or []
        try:
            _logger.info("[param-test] poll_overdue list count=%s", len(rows))
        except Exception:
            pass
        for r in rows:
            try:
                ts = str(r.get("traceId") or "")
                erp = str(r.get("erp") or "")
                wf = str(r.get("workflowId") or "")
                task_id = int(r.get("id"))
                _logger.info("[param-test] poll fetch traceId=%s taskId=%s", ts, str(task_id))
                res = await _autobots_get_result({"traceId": ts, "erp": erp, "workflowId": wf})
                # 若已完成，正常处理；否则根据 started_time 超过1小时才置失败
                payload = res.get("data") or {}
                inner = payload.get("data") or payload
                status = str(inner.get("status") or "")
                if status == "finished":
                    await _handle_result(api, task_id, res, row=r, ctx=ctx)
                    continue
                # 解析 startedTime
                started_str = r.get("startedTime") or r.get("started_time") or ""
                import datetime as _dt
                started_dt = None
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                    try:
                        started_dt = _dt.datetime.strptime(str(started_str), fmt)
                        break
                    except Exception:
                        continue
                if started_dt is None:
                    try:
                        started_dt = _dt.datetime.fromisoformat(str(started_str))
                    except Exception:
                        started_dt = None
                if started_dt is None:
                    _logger.warning("[param-test] poll unable to parse startedTime taskId=%s raw=%s", str(task_id), str(started_str))
                    continue
                age_sec = (end - started_dt).total_seconds()
                try:
                    from .config import load_config
                    cfg = load_config() or {}
                    timeout_sec = int((((cfg.get("paramTest") or {}).get("runningTimeoutSec")) or 3600))
                except Exception:
                    timeout_sec = 3600
                if age_sec >= timeout_sec:
                    await param_test_fail(api, int(task_id), f"autobot status={status}, running timeout")
                else:
                    _logger.info("[param-test] task still running taskId=%s age_sec=%.0f", str(task_id), age_sec)
            except Exception:
                try:
                    _logger.warning("[param-test] poll fetch error taskId=%s", str(r.get("id")))
                except Exception:
                    pass
                continue
        return {"ok": True, "count": len(rows)}
    except Exception as e:
        try:
            _logger.error("[param-test] poll_overdue error err=%s", str(e))
        except Exception:
            pass
        return {"error": str(e)}
async def _resolve_erp(ctx: Dict[str, Any], api: BackendAPI) -> str:
    try:
        v = str((ctx.get("erp_username") or os.getenv("ERP_USERNAME") or "")).strip()
        if v:
            return v
        try:
            cu = await api._request("GET", "/api/user/username")
            payload = (cu.get("data") or cu) if isinstance(cu, dict) else {}
            v2 = str(payload.get("username") or "").strip()
            if v2:
                ctx["erp_username"] = v2
                return v2
        except Exception:
            pass
        return ""
    except Exception:
        return ""
