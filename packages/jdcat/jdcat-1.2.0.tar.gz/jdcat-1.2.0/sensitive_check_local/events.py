"""
Event tracking and SSE broadcasting for sensitive-check-local.

Maintains in-memory flow status and last event timestamp.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, Optional, Set

# Flow status map: flowId -> "pending" | "ok" | "fail"
_seen: Dict[str, str] = {}
_last_event_ts: Optional[int] = None

# SSE subscribers: each subscriber owns an asyncio.Queue[str]
_subscribers: Set[asyncio.Queue[str]] = set()
_lock = asyncio.Lock()

def _now_ms() -> int:
    return int(time.time() * 1000)

def pending_count() -> int:
    return sum(1 for v in _seen.values() if v == "pending")

def last_event_ts() -> Optional[int]:
    return _last_event_ts

def get_status_fields() -> Dict[str, Any]:
    return {"queueSize": pending_count(), "lastEventTs": _last_event_ts}

def apply_event(event: Dict[str, Any]) -> None:
    """
    Update in-memory status based on incoming event.
    Expected shapes:
      { "type": "flow", "data": { "flowId": "id", ... , "ts": 123 } }
      { "type": "upload", "data": { "flowId": "id", "uploaded": true|false, "ts": 123 } }
    Also compatible with {"event": "...", "payload": {...}}.
    """
    global _last_event_ts
    if not isinstance(event, dict):
        return
    etype = event.get("type") or event.get("event")
    payload = event.get("data") or event.get("payload") or {}
    if not isinstance(payload, dict):
        payload = {}
    ts = payload.get("ts") or event.get("ts") or _now_ms()
    fid = payload.get("flowId")
    if etype == "flow":
        if isinstance(fid, str) and fid and fid not in _seen:
            _seen[fid] = "pending"
        _last_event_ts = ts
    elif etype == "upload":
        if isinstance(fid, str) and fid in _seen:
            uploaded = bool(payload.get("uploaded"))
            _seen[fid] = "ok" if uploaded else "fail"
        _last_event_ts = ts
    else:
        # ignore unknown types but still update last seen timestamp
        _last_event_ts = ts

async def broadcast(event: Dict[str, Any]) -> None:
    """
    Broadcast event to all SSE subscribers.
    Serialization is JSON with fields:
      { "type": ..., "data": ... }
    """
    if not isinstance(event, dict):
        return
    try:
        payload = json.dumps(event, ensure_ascii=False)
    except Exception:
        # Fallback to minimal structure
        payload = json.dumps({"type": "unknown"})
    # Copy subscribers under lock to avoid mutation during iteration
    async with _lock:
        targets = list(_subscribers)
    to_remove: list[asyncio.Queue[str]] = []
    for q in targets:
        try:
            q.put_nowait(payload)
        except Exception:
            to_remove.append(q)
    if to_remove:
        async with _lock:
            for q in to_remove:
                _subscribers.discard(q)

async def subscribe() -> asyncio.Queue[str]:
    """
    Register a new SSE subscriber and return its queue.
    The caller must ensure to call unsubscribe() on disconnect.
    """
    q: asyncio.Queue[str] = asyncio.Queue(maxsize=512)
    async with _lock:
        _subscribers.add(q)
    return q

def unsubscribe(q: asyncio.Queue[str]) -> None:
    try:
        # best-effort removal; no await
        if q is None:
            return
        # Drain queue to help GC
        try:
            while not q.empty():
                q.get_nowait()
        except Exception:
            pass
        # Remove from subscribers
        # No lock needed for discard; at-most a race leading to benign miss
        _subscribers.discard(q)
    except Exception:
        pass

def reset() -> None:
    """
    Clear all in-memory states. Intended for /stop or tests.
    """
    global _last_event_ts
    _seen.clear()
    _last_event_ts = None
    # Do not touch subscribers here.
# ==== Permission testing events callbacks (basic) ====
# 说明：
# - 提供执行阶段事件回调：on_claimed、on_detail_fetched、on_case_generated、on_request_replayed、
#   on_analyzed、on_progress_sent、on_results_sent、on_completed
# - 环境变量 SENSITIVE_LOCAL_EVENTS=stdout|off 控制输出（默认 stdout）
# - 统一脱敏：不输出完整 token/headers/响应体；敏感字段替换为 "***"

import os
import json
from typing import Any, Dict

_MODE = os.getenv("SENSITIVE_LOCAL_EVENTS", "stdout").strip().lower()

def _emit(event: str, data: Dict[str, Any]) -> None:
    if _MODE != "stdout":
        return
    safe: Dict[str, Any] = {}
    try:
        for k, v in (data or {}).items():
            lk = str(k).lower()
            if lk in ("authorization", "cookie", "set-cookie", "token", "x-token", "access-token"):
                safe[str(k)] = "***"
            else:
                safe[str(k)] = v
        print(json.dumps({"event": event, "data": safe}, ensure_ascii=False))
    except Exception:
        try:
            print(json.dumps({"event": event, "data": "unserializable"}, ensure_ascii=False))
        except Exception:
            # 最后兜底输出
            print(f'{{"event":"{event}","data":"unserializable"}}')

def on_claimed(data: Dict[str, Any]) -> None:
    _emit("on_claimed", data)

def on_detail_fetched(data: Dict[str, Any]) -> None:
    _emit("on_detail_fetched", data)

def on_case_generated(data: Dict[str, Any]) -> None:
    _emit("on_case_generated", data)

def on_request_replayed(data: Dict[str, Any]) -> None:
    _emit("on_request_replayed", data)

def on_analyzed(data: Dict[str, Any]) -> None:
    _emit("on_analyzed", data)

def on_progress_sent(data: Dict[str, Any]) -> None:
    _emit("on_progress_sent", data)

def on_results_sent(data: Dict[str, Any]) -> None:
    _emit("on_results_sent", data)

def on_completed(data: Dict[str, Any]) -> None:
    _emit("on_completed", data)