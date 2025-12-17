from __future__ import annotations

"""入参测试-生成队列

职责：
- 串行派发“测试数据生成”任务：调用 Autobot 的 runWorkflow，并在约 100s 后拉取 getWorkflowResult，入库 details/raw。
- 控制节奏与去抖：按 paramTest.runIntervalSec 控制派发间隔；按 paramTest.dedupeTTLsec 对 (domain|path) 去抖避免重复入队。
- 复用窗口：在生成链路内检测 in_progress 复用窗口，防止同接口短期重复创建任务。
- 失败处理：runWorkflow 失败直接标记任务 failed；getWorkflowResult 未完成不重试，依赖轮询兜底。

边界：
- 不承担“重放执行”职责；生成完成后的执行通过独立的 param_test_executor_queue 处理。
- notify 阶段不直接使用本队列（可通过配置扩展），当前默认仅用于需要顺序节流的生成场景。
"""

import os
import time
import asyncio
from typing import Any, Dict, Optional, Tuple
import logging

_logger = logging.getLogger("sensitive_check_local")

_queue: Optional[asyncio.Queue[Tuple[Dict[str, Any], Dict[str, Any]]]] = None
_worker_task: Optional[asyncio.Task] = None
_rate_window: list[float] = []
_rate_lock = asyncio.Lock()
_dedupe_marks: Dict[str, float] = {}
_dedupe_lock = asyncio.Lock()

def _rate_per_minute() -> int:
    try:
        v = int(os.getenv("AUTOBOTS_RUN_RATE_PER_MIN", "3") or 3)
        return v if v > 0 else 3
    except Exception:
        return 3

async def _rate_allow() -> bool:
    async with _rate_lock:
        now = time.time()
        window = [t for t in _rate_window if now - t < 60]
        max_per_min = _rate_per_minute()
        if len(window) >= max_per_min:
            _rate_window[:] = window
            try:
                _logger.info("[param-test-throttler] rate_limited window_count=%s max=%s", len(window), max_per_min)
            except Exception:
                pass
            return False
        window.append(now)
        _rate_window[:] = window
        try:
            _logger.info("[param-test-throttler] rate_allow window_count=%s max=%s", len(window), max_per_min)
        except Exception:
            pass
        return True

async def _sleep_until_allow() -> None:
    # If allowed now, return immediately; else sleep until next slot free
    async with _rate_lock:
        now = time.time()
        window = [t for t in _rate_window if now - t < 60]
        _rate_window[:] = window
        max_per_min = _rate_per_minute()
        if len(window) < max_per_min:
            return
        # Next available time: when the oldest timestamp leaves the 60s window
        oldest = min(window) if window else now
        remain = max(0.0, 60.0 - (now - oldest))
    try:
        # small jitter to avoid burst on boundary
        await asyncio.sleep(remain + 0.5)
    except Exception:
        pass

async def _worker() -> None:
    global _queue
    from .param_test import handle_flow_item  # local import to avoid cycles
    # 读取配置的顺序间隔（秒），默认 20s
    try:
        from .config import load_config
        cfg = load_config()
        run_interval_sec = int((((cfg or {}).get("paramTest") or {}).get("runIntervalSec") or 20))
    except Exception:
        run_interval_sec = 20
    try:
        _logger.info("[param-test-throttler] worker start interval=%ss", run_interval_sec)
    except Exception:
        pass
    while True:
        try:
            if _queue is None:
                await asyncio.sleep(0.5)
                continue
            item, ctx = await _queue.get()
            # 顺序节流：每条间隔固定秒数
            try:
                _logger.info("【入参测试问题排查】生成队列派发待执行 after=%ss domain=%s path=%s", run_interval_sec, item.get("domain"), item.get("path"))
            except Exception:
                pass
            try:
                await asyncio.sleep(run_interval_sec)
            except Exception:
                pass
            # call handle_flow_item with rate-limit disabled
            try:
                _logger.info("【入参测试问题排查】生成队列派发执行 domain=%s path=%s", item.get("domain"), item.get("path"))
            except Exception:
                pass
            try:
                await handle_flow_item(item, ctx, apply_rate_limit=False)
            except Exception as e:
                try:
                    _logger.error("[param-test-throttler] dispatch error: %s", str(e))
                except Exception:
                    pass
        except asyncio.CancelledError:
            break
        except Exception:
            try:
                _logger.warning("[param-test-throttler] worker loop error", exc_info=False)
            except Exception:
                pass
            await asyncio.sleep(0.5)
    try:
        _logger.info("[param-test-throttler] worker stop")
    except Exception:
        pass

async def start_throttler() -> None:
    global _queue, _worker_task
    if _queue is None:
        _queue = asyncio.Queue(maxsize=1000)
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_worker())

async def stop_throttler() -> None:
    global _worker_task
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except Exception:
            pass
    _worker_task = None

async def enqueue_param_test(item: Dict[str, Any], ctx: Dict[str, Any], force: bool = False) -> None:
    global _queue
    if _queue is None:
        await start_throttler()
    try:
        # 尝试从实时队列最近快照补全 interfaceId，仅用于绑定，不涉及数据复用
        try:
            from .realtime_queue import get_realtime_queue
            q = get_realtime_queue()
            if q is not None and hasattr(q, "get_last_item"):
                dom = str(item.get("domain") or "").strip().lower()
                pth = str(item.get("path") or "/")
                last = q.get_last_item(dom, pth)
                if isinstance(last, dict) and last.get("interfaceId") is not None and (item.get("interfaceId") is None):
                    item["interfaceId"] = last.get("interfaceId")
                    try:
                        _logger.info("【精确绑定】生成队列补全 interfaceId=%s domain=%s path=%s", str(item.get("interfaceId")), dom, pth)
                    except Exception:
                        pass
                else:
                    try:
                        _logger.info("【精确绑定】生成队列保留 interfaceId=%s domain=%s path=%s", str(item.get("interfaceId")), dom, pth)
                    except Exception:
                        pass
        except Exception:
            pass
        # 取消复用窗口与TTL去抖拦截：每次请求均入队
        await _queue.put((item, ctx))
        try:
            _logger.info("[param-test-throttler] enqueued domain=%s path=%s", item.get("domain"), item.get("path"))
        except Exception:
            pass
    except Exception as e:
        try:
            _logger.error("[param-test-throttler] enqueue failed: %s", str(e))
        except Exception:
            pass
