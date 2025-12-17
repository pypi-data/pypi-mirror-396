from __future__ import annotations

"""入参测试-重放执行队列

职责：
- 在“测试数据生成完成”后，串行触发入参重放执行：基于最近一次流量快照 (RealtimeQueue.get_last_item)，调用 execute_param_tests。
- 控制派发节奏：按 paramTest.executeIntervalSec 间隔派发，避免与业务流量竞争。
- 读写策略：
  - 若无法获取最近流量快照则跳过并记录，避免空跑。
  - 执行成功后清理对应 (domain|path) 的 last_item，防止重复重放。

边界：
- 与“生成队列 (param_test_throttler)”完全分离，仅处理执行阶段；不参与 runWorkflow 或 details/raw 入库。
- 目前不做 TTL 去抖（可按需要在后续加 executeDedupeTTLsec）。
"""

import asyncio
import logging
from typing import Any, Dict, Optional, Tuple

_logger = logging.getLogger("sensitive_check_local")

_queue: Optional[asyncio.Queue[Tuple[Dict[str, Any], Dict[str, Any]]]] = None
_worker_task: Optional[asyncio.Task] = None

async def _worker() -> None:
    global _queue
    try:
        from .config import load_config
        cfg = load_config() or {}
        interval_sec = int((((cfg.get("paramTest") or {}).get("executeIntervalSec")) or 20))
    except Exception:
        interval_sec = 20
    while True:
        try:
            if _queue is None:
                await asyncio.sleep(0.5)
                continue
            item, ctx = await _queue.get()
            try:
                _logger.info("【入参测试问题排查】执行队列派发 after=%ss domain=%s path=%s ctx.task_id=%s", interval_sec, item.get("domain"), item.get("path"), (ctx or {}).get("task_id"))
            except Exception:
                pass
            try:
                await asyncio.sleep(interval_sec)
            except Exception:
                pass
            try:
                from .realtime_queue import get_realtime_queue
                from .param_test_execute import execute_param_tests
                q = get_realtime_queue()
                payload = item if (item.get("method") or item.get("url") or item.get("requestBody") or item.get("requestHeaders")) else None
                if payload is None:
                    _logger.info("【入参测试问题排查】执行队列无可用流量，跳过 domain=%s path=%s", item.get("domain"), item.get("path"))
                else:
                    ret = await execute_param_tests(q, payload)
                    try:
                        ok = bool(ret and ret.get('ok'))
                        cnt = int(ret.get('count') or 0) if ret else 0
                    except Exception:
                        ok, cnt = False, 0
                    if ok and cnt > 0:
                        try:
                            _logger.info("【入参测试问题排查】执行成功 payload来源=入队项 domain=%s path=%s count=%s", item.get("domain"), item.get("path"), cnt)
                        except Exception:
                            pass
                    else:
                        _logger.info("【入参测试问题排查】执行未产生结果，不清理最近流量 domain=%s path=%s ret=%s", item.get("domain"), item.get("path"), str(ret))
            except Exception as e:
                try:
                    _logger.error("【入参测试状态】执行队列派发异常: %s", str(e))
                except Exception:
                    pass
        except asyncio.CancelledError:
            break
        except Exception:
            try:
                _logger.warning("【入参测试状态】执行队列循环错误", exc_info=False)
            except Exception:
                pass
            await asyncio.sleep(0.5)
    try:
        _logger.info("【入参测试状态】执行队列worker停止")
    except Exception:
        pass

async def start_executor_queue() -> None:
    global _queue, _worker_task
    if _queue is None:
        _queue = asyncio.Queue(maxsize=1000)
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_worker())

async def stop_executor_queue() -> None:
    global _worker_task
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except Exception:
            pass
    _worker_task = None

async def enqueue_execute(item: Dict[str, Any], ctx: Dict[str, Any]) -> None:
    global _queue
    if _queue is None:
        await start_executor_queue()
    try:
        await _queue.put((item, ctx))
        try:
            _logger.info("【入参测试状态】执行队列入队 domain=%s path=%s", item.get("domain"), item.get("path"))
        except Exception:
            pass
    except Exception as e:
        try:
            _logger.error("【入参测试状态】执行队列入队失败: %s", str(e))
        except Exception:
            pass
