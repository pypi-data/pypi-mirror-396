from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple
import asyncio
import logging
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from .backend_client import (
    build_backend_api_from_context,
    param_test_result_check_by_interface_id,
    param_test_tasks_latest,
    param_test_details_list,
    param_test_result_ingest,
    realtime_ignore_detail,
)
from .realtime_manager import fix_headers_field, to_str_no_limit
from .realtime_queue import RealtimeQueue
from .assertion_queue import AssertionQueue

_logger = logging.getLogger("sensitive_check_local")

_rate_marks: List[float] = []
_rate_lock = asyncio.Lock()
_pt_reenqueued: set = set()

async def _throttle(max_per_sec: int = 3) -> None:
    async with _rate_lock:
        now = asyncio.get_event_loop().time()
        window = [t for t in _rate_marks if (now - t) < 1.0]
        _rate_marks[:] = window
        wait = 0.0
        if len(window) >= max_per_sec:
            oldest = window[0]
            wait = max(0.0, 1.0 - (now - oldest))
        if wait > 0:
            try:
                _logger.info("【入参测试】节流 wait=%.3fs", wait)
            except Exception:
                pass
        if wait > 0:
            await asyncio.sleep(wait)
        now2 = asyncio.get_event_loop().time()
        _rate_marks.append(now2)

def _digits_only(val: Any) -> Optional[int]:
    try:
        s = str(val)
        ds = "".join([c for c in s if c.isdigit()])
        if not ds:
            return None
        return int(ds)
    except Exception:
        return None


def _parse_parameter_value_json(s: Optional[str]) -> Any:
    if s is None:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s


def _walk_set(obj: Any, path_tokens: List[str], value: Any, delete: bool) -> Any:
    if not isinstance(obj, dict):
        obj = {}
    if not path_tokens:
        return obj
    cur = obj
    for i, t in enumerate(path_tokens):
        is_last = (i == len(path_tokens) - 1)
        if '[' in t and t.endswith(']'):
            key = t.split('[', 1)[0]
            try:
                idx = int(t[t.find('[') + 1:-1])
            except Exception:
                idx = 0
            if not isinstance(cur, dict):
                # 强制修正为对象容器
                return obj
            arr = cur.get(key)
            if not isinstance(arr, list):
                arr = []
                cur[key] = arr
            while len(arr) <= idx:
                arr.append({} if not is_last else None)
            if is_last:
                if delete:
                    if 0 <= idx < len(arr):
                        del arr[idx]
                else:
                    arr[idx] = value
                return obj
            # 继续深入
            if not isinstance(arr[idx], dict):
                arr[idx] = {}
            cur = arr[idx]
        else:
            if not isinstance(cur, dict):
                return obj
            if is_last:
                if delete:
                    cur.pop(t, None)
                else:
                    cur[t] = value
                return obj
            nxt = cur.get(t)
            if not isinstance(nxt, dict):
                nxt = {}
                cur[t] = nxt
            cur = nxt
    return obj


def _apply_param_to_request(original_request: Dict[str, Any], parameter_path: str, parameter_value_json: Optional[str], is_loss: bool) -> Dict[str, Any]:
    method = str(original_request.get('method') or 'GET').upper()
    url = str(original_request.get('url') or '')
    headers = fix_headers_field(original_request.get('headers')) or {}
    body = original_request.get('request_body')

    tokens = [t for t in str(parameter_path or '').split('.') if t]
    if not tokens:
        return {
            'method': method,
            'url': url,
            'headers': headers,
            'request_body': body,
        }
    area = tokens[0]
    rest = tokens[1:]
    if area == 'query':
        try:
            parsed = urlsplit(url)
            q = dict(parse_qsl(parsed.query, keep_blank_values=True))
            if not rest:
                return {
                    'method': method,
                    'url': url,
                    'headers': headers,
                    'request_body': body,
                }
            key = rest[0]
            if is_loss:
                if key in q:
                    del q[key]
            else:
                val = _parse_parameter_value_json(parameter_value_json)
                q[key] = '' if val is None else str(val)
            new_query = urlencode(list(q.items()), doseq=True)
            new_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))
            return {
                'method': method,
                'url': new_url,
                'headers': headers,
                'request_body': body,
            }
        except Exception:
            return {
                'method': method,
                'url': url,
                'headers': headers,
                'request_body': body,
            }
    if area == 'requestBody':
        try:
            rest2 = list(rest)
            try:
                if rest2 and str(rest2[0]).lower() in ("req", "rqe"):
                    rest2 = rest2[1:]
            except Exception:
                pass
            # 1) JSON 体：按路径逐层创建并替换/删除
            if isinstance(body, (dict, list)):
                base = body if isinstance(body, dict) else {}
                val = _parse_parameter_value_json(parameter_value_json)
                # 主路径操作
                _walk_set(base, rest2, val, bool(is_loss))
                # Fallback：当主路径首段不存在，但顶层存在末段键时，对顶层键也进行同样的操作
                try:
                    if rest2:
                        first = rest2[0]
                        last = rest2[-1]
                        has_container = isinstance(base.get(first), (dict, list)) or (first in base)
                        has_top_last = last in base
                        if not has_container and has_top_last:
                            if bool(is_loss):
                                base.pop(last, None)
                            else:
                                base[last] = val
                except Exception:
                    pass
                return {
                    'method': method,
                    'url': url,
                    'headers': headers,
                    'request_body': base,
                }
            s = to_str_no_limit(body)
            # 尝试 JSON
            obj = None
            try:
                tmp = json.loads(s or '{}')
                obj = tmp if isinstance(tmp, dict) else {}
            except Exception:
                obj = None
            if isinstance(obj, dict):
                val = _parse_parameter_value_json(parameter_value_json)
                _walk_set(obj, rest2, val, bool(is_loss))
                # Fallback 顶层末段键
                try:
                    if rest2:
                        last = rest2[-1]
                        if last in obj or not isinstance(obj.get(rest2[0]), (dict, list)):
                            if bool(is_loss):
                                obj.pop(last, None)
                            else:
                                obj[last] = val
                except Exception:
                    pass
                return {
                    'method': method,
                    'url': url,
                    'headers': headers,
                    'request_body': obj,
                }
            # 2) 表单体：顶层 key 使用 rest 合并为单键
            if isinstance(s, str) and ('=' in s or '&' in s):
                pairs = dict(parse_qsl(s, keep_blank_values=True))
                key = '.'.join(rest2) if rest2 else ''
                if key:
                    if bool(is_loss):
                        pairs.pop(key, None)
                    else:
                        val = _parse_parameter_value_json(parameter_value_json)
                        pairs[key] = '' if val is None else str(val)
                # Fallback 顶层末段键
                if rest2:
                    last = rest2[-1]
                    if bool(is_loss):
                        pairs.pop(last, None)
                    else:
                        val = _parse_parameter_value_json(parameter_value_json)
                        pairs[last] = '' if val is None else str(val)
                new_text = urlencode(list(pairs.items()))
                return {
                    'method': method,
                    'url': url,
                    'headers': headers,
                    'request_body': new_text,
                }
            # 3) 其他：回退为 JSON 设置顶层键
            base = {}
            val = _parse_parameter_value_json(parameter_value_json)
            _walk_set(base, rest2, val, bool(is_loss))
            return {
                'method': method,
                'url': url,
                'headers': headers,
                'request_body': base,
            }
        except Exception:
            return {
                'method': method,
                'url': url,
                'headers': headers,
                'request_body': body,
            }
    return {
        'method': method,
        'url': url,
        'headers': headers,
        'request_body': body,
    }


async def execute_param_tests(queue: RealtimeQueue, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        ctx = queue._context or {}
        cfg = ctx.get("paramTest") or ctx.get("param_test") or {}
        en = bool(cfg.get("enabled"))
        allow = set([str(x).strip().upper() for x in (cfg.get("methods") or []) if str(x).strip()])
        m0 = str(item.get('method') or 'GET').strip().upper()
        if not en or (allow and m0 not in allow):
            return None
        api = None
        try:
            api = build_backend_api_from_context(ctx)
        except Exception as e:
            try:
                hdrs = fix_headers_field(item.get('requestHeaders')) or {}
                pid = str(hdrs.get('Project-Id') or hdrs.get('Project-ID') or '0')
                uid = str(hdrs.get('User-Id') or hdrs.get('User-ID') or (ctx.get('user_id') or ctx.get('userId') or '0'))
                cid = str(ctx.get('client_id') or ctx.get('clientId') or 'param-test-local')
                fallback = {'project_id': pid, 'user_id': uid, 'client_id': cid, 'task_id': ctx.get('task_id') or ctx.get('taskId')}
                _logger.info("【入参测试问题排查】上下文缺失，使用回退上下文 project_id=%s user_id=%s client_id=%s task_id=%s", pid, uid, cid, fallback.get('task_id'))
                api = build_backend_api_from_context(fallback)
                ctx = fallback
            except Exception as ex:
                _logger.error("【入参测试】构建后端客户端失败 err=%s", str(ex))
                return None
        u = str(item.get('url') or '')
        p = urlsplit(u)
        domain = p.netloc
        path = p.path or '/'
        # 提取任务ID：优先 item.taskId，其次上下文，再次从请求头 Task-Id/Task-ID 提取
        hdrs_for_id = fix_headers_field(item.get('requestHeaders')) or {}
        rt_task_id = (
            item.get('taskId') or
            ctx.get('task_id') or ctx.get('taskId') or
            hdrs_for_id.get('Task-Id') or hdrs_for_id.get('Task-ID')
        )
        if not rt_task_id:
            try:
                _logger.info("【入参测试问题排查】缺少实时任务ID，跳过执行 url=%s headers.keys=%s", u, list(hdrs_for_id.keys())[:20])
            except Exception:
                pass
            return None

        rt_num = _digits_only(rt_task_id)
        iid = None
        try:
            iid = item.get('interfaceId')
            if not iid:
                # 尝试从最近快照获取
                key = f"{domain}|{path}"
                entry = getattr(queue, '_last_items', {}).get(key)
                if isinstance(entry, dict):
                    iid = (entry.get('item') or {}).get('interfaceId')
        except Exception:
            iid = None
        if iid:
            try:
                _logger.info("【精确绑定】调用后端 results/check interfaceId=%s", str(iid))
            except Exception:
                pass
            chk = await param_test_result_check_by_interface_id(api, int(iid))
        else:
            chk = {'data': {'list': []}}
        data = (chk.get('data') or {}) if isinstance(chk, dict) else {}
        exists = data.get('list') or []
        try:
            _logger.info("【入参测试问题排查】results/check 返回 count=%s interfaceId=%s", len(exists), str(iid or ''))
        except Exception:
            pass
        # 取消结果窗口跳过：即使存在旧结果也继续生成新结果

        try:
            ig = await realtime_ignore_detail(api, domain, path, str(item.get('method') or 'GET'))
            igd = ig.get('data') if isinstance(ig, dict) else {}
            if isinstance(igd, dict) and igd:
                _logger.info("【入参测试问题排查】接口被忽略，跳过 domain=%s path=%s", domain, path)
                return {'skipped': True, 'reason': 'ignored'}
        except Exception:
            pass

        # 仅使用“本次生成任务”的ID（post_complete透传），不进行任何窗口复用
        valid_tid = None
        try:
            ptid = item.get('paramTaskId')
            if ptid is not None:
                valid_tid = int(ptid)
        except Exception:
            valid_tid = None
        if not valid_tid:
            _logger.info("【入参测试问题排查】无有效测试数据（仅接受本次taskId透传），等待生成完成 domain=%s path=%s", domain, path)
            return None
        try:
            _logger.info("【入参测试问题排查】拉取明细调用 details?taskId=%s domain=%s path=%s", str(valid_tid), domain, path)
        except Exception:
            pass
        det = await param_test_details_list(api, int(valid_tid))
        dl = (det.get('data') or {}).get('list') or []
        try:
            _logger.info("【入参测试问题排查】拉取明细返回 count=%s taskId=%s", len(dl), str(valid_tid))
        except Exception:
            pass
        if not dl:
            _logger.warning("【入参测试问题排查】details 为空，交由轮询器处理 domain=%s path=%s taskId=%s", domain, path, str(valid_tid))
            return None

        original_request = {
            'method': item.get('method', 'GET'),
            'url': u,
            'headers': item.get('requestHeaders', {}) or {},
            'request_body': item.get('requestBody', '') or ''
        }
        try:
            _logger.info("【入参测试】原始请求 method=%s url=%s", str(original_request.get('method')), str(original_request.get('url')))
            _logger.info("【入参测试】原始请求 headers.keys=%s", list((original_request.get('headers') or {}).keys())[:20])
            _logger.info("【入参测试】原始请求 body.preview=%s", to_str_no_limit(original_request.get('request_body'))[:200])
        except Exception:
            pass

        results: List[Dict[str, Any]] = []
        for d in dl:
            pid = d.get('parameterPath') or d.get('parameter_path')
            is_loss = bool(d.get('isLose') if 'isLose' in d else d.get('is_lose'))
            pvj = d.get('parameterValueJson') or d.get('parameter_value_json')
            try:
                _logger.info("【入参测试】场景参数 path=%s isLose=%s valueJson.preview=%s", str(pid), str(is_loss), str(pvj)[:200])
            except Exception:
                pass
            mod_req = _apply_param_to_request(original_request, str(pid or ''), pvj, is_loss)
            try:
                _logger.info("【入参测试】参数替换前后对比 url(before)=%s url(after)=%s", u, str(mod_req.get('url')))
                _logger.info("【入参测试】参数替换前后对比 body.before.preview=%s", to_str_no_limit(original_request.get('request_body'))[:200])
                _logger.info("【入参测试】参数替换前后对比 body.after.preview=%s", to_str_no_limit(mod_req.get('request_body'))[:200])
            except Exception:
                pass
            try:
                _logger.info("【入参测试】即将重放 method=%s url=%s", str(mod_req.get('method')), str(mod_req.get('url')))
                _logger.info("【入参测试】即将重放 headers.keys=%s", list((mod_req.get('headers') or {}).keys())[:20])
                _logger.info("【入参测试】即将重放 body.preview=%s", to_str_no_limit(mod_req.get('request_body'))[:200])
            except Exception:
                pass
            await _throttle(3)
            try:
                rsp = await queue._send_modified_request(mod_req)
            except Exception as send_err:
                _logger.error("【入参测试问题排查】重放发送异常 err=%s url=%s", str(send_err), str(mod_req.get('url')))
                rsp = {'status': 0, 'text': '', 'headers': {}}
            try:
                _logger.info("【入参测试】重放请求 method=%s url=%s", str(mod_req.get('method')), str(mod_req.get('url')))
                _logger.info("【入参测试】重放返回 status=%s body.preview=%s", str(rsp.get('status')), to_str_no_limit(rsp.get('text'))[:300])
            except Exception:
                pass
            rsp_text = to_str_no_limit(rsp.get('text'))
            if (rsp.get('status') or 0) == 0 and not rsp_text:
                rsp_text = "error: request failed or timeout"
            iso_now = __import__('datetime').datetime.now().astimezone().isoformat(timespec='milliseconds')
            results.append({
                'taskId': d.get('taskId'),
                'caseId': d.get('caseId'),
                'parameterPath': d.get('parameterPath'),
                'caseDescription': d.get('caseDescription'),
                'expectedResult': d.get('expectedResult'),
                'parameterValue': d.get('parameterValue'),
                'isLose': d.get('isLose'),
                'parameterValueType': d.get('parameterValueType'),
                'parameterValueJson': d.get('parameterValueJson'),
                'ssRtTaskId': int(rt_num) if rt_num is not None else 0,
                'requestUrl': mod_req.get('url'),
                'requestMethod': mod_req.get('method'),
                'requestQuery': urlsplit(mod_req.get('url')).query,
                'requestHeaders': json.dumps(fix_headers_field(mod_req.get('headers')) or {}, ensure_ascii=False),
                'requestBody': to_str_no_limit(mod_req.get('request_body')),
                'responseBody': rsp_text,
                'updatedTime': iso_now,
                'passed': 0,
            })
        if results:
            try:
                _logger.info("【入参测试】批量入库 count=%s", len(results))
            except Exception:
                pass
            try:
                await param_test_result_ingest(api, results)
            except Exception as ingest_err:
                try:
                    _logger.error("【入参测试问题排查】结果入库失败 err=%s count=%s rtTaskId=%s domain=%s path=%s", str( ingest_err ), len(results), str(rt_num), domain, path)
                except Exception:
                    pass
                return None
            # 入库后触发断言队列
            try:
                _logger.info("【入参测试问题排查】结果已入库，触发断言队列 rtTaskId=%s domain=%s path=%s count=%s", str(rt_num), domain, path, len(results))
                aq = getattr(queue, "_assertion_queue", None)
                if aq is None:
                    aq = AssertionQueue()
                    setattr(queue, "_assertion_queue", aq)
                    await aq.start()
                # 传递实时上下文中的ERP（username），避免外部断言接口缺参
                erp_ctx = None
                try:
                    erp_ctx = (queue._context or {}).get("erp_username")
                except Exception:
                    erp_ctx = None
                if iid:
                    await aq.enqueue_interface(api, int(iid), erp=erp_ctx)
            except Exception:
                pass
        return {'ok': True, 'count': len(results)}
    except Exception:
        return None
