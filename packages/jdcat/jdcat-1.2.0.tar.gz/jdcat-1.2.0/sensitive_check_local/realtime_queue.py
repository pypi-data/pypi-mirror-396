"""
实时检测队列管理模块
负责：队列管理、批处理调度、越权检测、后端上报
"""
from __future__ import annotations

import asyncio
import json
import time
import logging
from typing import Any, Dict, List, Optional, Tuple
from collections import deque
from urllib.parse import urlparse
import base64
import importlib
try:
    # 动态加载 httpx，避免静态导入在未安装环境下产生 IDE 诊断错误
    httpx = importlib.import_module("httpx")
except Exception:
    # 在缺失 httpx 的环境下，后续网络请求将被安全地降级处理
    httpx = None
# httpx 异常别名兼容处理（不同版本可能不存在 NetworkError/TimeoutException）
HTTPXTimeout = getattr(httpx, "TimeoutException", getattr(httpx, "ReadTimeout", Exception))
HTTPXNetworkError = getattr(httpx, "NetworkError", getattr(httpx, "TransportError", Exception))
from .realtime_manager import safe_to_text, TEXT_LIMIT, fix_headers_field, to_str_no_limit

from .request_modifier_local import modify_request_with_identity
from .analysis_local import compare_responses, map_excel_risk_level
from .backend_client import BackendAPIError, BackendAPI, build_backend_api_from_context

logger = logging.getLogger(__name__)


def _has_internal_header(headers: Any) -> bool:
    """
    检测是否存在内部回放标记头（大小写不敏感）
    - 仅判断是否存在 'x-ss-internal' 头即可视为内部；值不强校验
    """
    try:
        if isinstance(headers, dict):
            keys = {str(k).lower().strip() for k in headers.keys() if str(k).strip()}
            return "x-ss-internal" in keys
        if isinstance(headers, str):
            try:
                obj = json.loads(headers) if headers.strip() else {}
                if isinstance(obj, dict):
                    keys = {str(k).lower().strip() for k in obj.keys() if str(k).strip()}
                    return "x-ss-internal" in keys
            except Exception:
                return False
        return False
    except Exception:
        return False

def _headers_to_dict_maybe(h: Any) -> Dict[str, Any]:
    """
    将 headers 规范化为 dict：
    - dict: 复制后返回
    - JSON 字符串: 解析为 dict，失败返回 {}
    - 其他: 返回 {}
    """
    if isinstance(h, dict):
        return dict(h)
    if isinstance(h, str):
        s = h.strip()
        if not s:
            return {}
        try:
            obj = json.loads(s)
            if isinstance(obj, dict):
                return dict(obj)
            return {}
        except Exception:
            return {}
    return {}

class RealtimeQueue:
    """实时检测队列管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        # 队列配置
        self.max_queue_size = config.get("realtime", {}).get("maxQueueSize", 1000)
        self.batch_interval_sec = config.get("realtime", {}).get("batchIntervalSec", 10)
        self.batch_size = config.get("realtime", {}).get("batchSize", 5)
        self.final_flush_on_stop = config.get("realtime", {}).get("finalFlushOnStop", True)
        
        # 队列存储
        self._queue: deque = deque()
        self._queue_lock = asyncio.Lock()
        
        # 调度器状态
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running = False
        
        # 上下文信息
        self._context: Optional[Dict[str, Any]] = None
        self._backend_base_url: Optional[str] = None
        
        # 统计信息
        self._dropped_count = 0
        self._processed_count = 0

        # 内部回放过滤统计（按批次窗口复位）
        self._filtered_internal_count: int = 0
        self._filtered_internal_examples: List[Tuple[str, str]] = []

        # 一次性内部跳过标记（one-shot）
        self._pending_internal_key: Optional[str] = None
        # 最近一次聚合项缓存（按 domain|path）
        self._last_items: Dict[str, Dict[str, Any]] = {}

        
    async def start_scheduler(self, context: Dict[str, Any], backend_base_url: str):
        """启动批处理调度器"""
        if self._running:
            # 当已运行时，仅更新上下文与后端地址
            self._context = context
            self._backend_base_url = backend_base_url
            logger.info("[realtime-queue] context updated while running")
            return
            
        self._context = context
        self._backend_base_url = backend_base_url
        self._running = True
        
        # 启动调度器任务
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info(f"Realtime scheduler started with interval={self.batch_interval_sec}s, batch_size={self.batch_size}")

    def update_context(self, context: Dict[str, Any], backend_base_url: Optional[str] = None):
        self._context = context
        if backend_base_url:
            self._backend_base_url = backend_base_url
        try:
            logger.info("[realtime-queue] context updated: keys=%s", list(context.keys()))
        except Exception:
            pass
        
    async def stop_scheduler(self):
        """停止调度器并执行最终冲刷"""
        if not self._running:
            return
            
        self._running = False
        
        # 取消调度器任务
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            self._scheduler_task = None
            
        # 执行最终冲刷
        if self.final_flush_on_stop:
            await self._final_flush()
        try:
            self._last_items.clear()
        except Exception:
            pass
            
        logger.info(f"Realtime scheduler stopped. Processed: {self._processed_count}, Dropped: {self._dropped_count}")
        
    async def enqueue(self, flow_data: Dict[str, Any]):
        """将流量数据加入队列"""
        # 兜底过滤：内部回放请求不入队（仅输出最小元信息日志）
        try:
            meta = (flow_data.get("meta") or {}) if isinstance(flow_data, dict) else {}
            internal_flag = bool((meta or {}).get("internal", False))
            hdr_present = _has_internal_header((flow_data or {}).get("requestHeaders", {}) if isinstance(flow_data, dict) else {})
            if internal_flag or hdr_present:
                try:
                    parsed = urlparse(str((flow_data or {}).get("url", "") or ""))
                    dom = parsed.netloc
                    pth = parsed.path or "/"
                except Exception:
                    dom, pth = "", ""
                # 记录过滤统计
                self._filtered_internal_count += 1
                if len(self._filtered_internal_examples) < 3:
                    self._filtered_internal_examples.append((dom, pth))
                logger.info("[realtime-queue] filtered internal replay: domain=%s path=%s has_internal_hdr=%s", dom, pth, bool(hdr_present))
                return
        except Exception:
            # 异常情况下为安全起见，不入队
            return
        async with self._queue_lock:
            # 检查队列是否已满
            if len(self._queue) >= self.max_queue_size:
                # 丢弃最旧的元素
                self._queue.popleft()
                self._dropped_count += 1
                
            # 添加/保留时间戳：优先保留已有 occurMs，仅在缺失或非法时补齐（避免批次内重复上报）
            try:
                occ = flow_data.get("occurMs")
                occ_int = int(occ) if isinstance(occ, (int, float)) else (int(str(occ).strip()) if (occ is not None and str(occ).strip()) else 0)
            except Exception:
                occ_int = 0
            if occ_int <= 0:
                occ_int = int(time.time() * 1000)
                flow_data["occurMs"] = occ_int
                logger.debug(f"[realtime-queue] occurMs generated: {occ_int}")
            else:
                flow_data["occurMs"] = occ_int
                logger.debug(f"[realtime-queue] occurMs preserved: {occ_int}")
            self._queue.append(flow_data)
            try:
                p = urlparse(flow_data.get("url", "") or "")
                dom = (p.netloc.split(":")[0] if ":" in (p.netloc or "") else (p.netloc or "")).lower().strip()
                pth = p.path or "/"
                key = f"{dom}|{pth}"
                self._last_items[key] = {"item": dict(flow_data), "ts": time.time()}
                logger.info("【入参测试问题排查】最近流量快照更新 domain=%s path=%s occMs=%s", dom, pth, flow_data.get("occurMs"))
            except Exception:
                pass
            
    def get_queue_size(self) -> int:
        """获取当前队列大小"""
        return len(self._queue)
        
    def is_running(self) -> bool:
        """检查调度器是否运行中"""
        return self._running
        
    async def _scheduler_loop(self):
        """调度器主循环"""
        try:
            while self._running:
                await asyncio.sleep(self.batch_interval_sec)
                if not self._running:
                    break
                    
                # 处理一批数据
                await self._process_batch()
                
        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
            
    async def _process_batch(self):
        """处理一批队列数据"""
        batch = []
        
        # 从队列中取出一批数据
        async with self._queue_lock:
            for _ in range(min(self.batch_size, len(self._queue))):
                if self._queue:
                    batch.append(self._queue.popleft())
                    
        if not batch:
            return
            
        logger.info(f"Processing batch of {len(batch)} items")
        # 统计本批次唯一键分布（domain|path|method|occurMs），定位重复上报来源
        try:
            uniq_map: Dict[str, int] = {}
            for it in batch:
                try:
                    p = urlparse(it.get("url", "") or "")
                    domain = (p.netloc.split(":")[0] if ":" in (p.netloc or "") else (p.netloc or "")).lower().strip()
                    path = p.path or "/"
                    method = str(it.get("method", "GET")).upper()
                    occur_ms = it.get("occurMs")
                    key = f"{domain}|{path}|{method}|{occur_ms}"
                except Exception:
                    key = f"||/|GET|{it.get('occurMs')}"
                uniq_map[key] = uniq_map.get(key, 0) + 1
            dup_preview = {k: v for k, v in uniq_map.items() if v > 1}
            # 仅打印统计与最多5条重复示例，不含明文内容；追加内部过滤统计摘要（最多3条示例）
            logger.info(
                "[realtime-queue] batch uniqueKeys=%s duplicates=%s preview=%s filtered_internal_count=%s filtered_examples=%s",
                len(uniq_map),
                len(dup_preview),
                list(dup_preview.items())[:5],
                self._filtered_internal_count,
                self._filtered_internal_examples[:3]
            )
            # 窗口复位内部过滤统计
            self._filtered_internal_count = 0
            self._filtered_internal_examples.clear()
        except Exception:
            pass
        
        try:
            # 处理批次数据
            results = []
            for item in batch:
                # 越权前置诊断（降敏，仅结构化摘要）
                try:
                    self._log_permission_pre_diagnose(item)
                except Exception:
                    pass

                item_results = await self._process_single_item(item)
                results.extend(item_results)
                
            # 直接上报（不进行批次内去重）
            if results:
                await self._batch_report_to_backend(results)
                
            self._processed_count += len(batch)
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")

    def _log_permission_pre_diagnose(self, item: Dict[str, Any]) -> None:
        """
        越权前置诊断日志（降敏）：
        - identities 总数
        - 每个 identity 的 headers/cookies/tokens 键名列表与数量（仅键名）
        - 是否配置 horizontalUserId/verticalUserId（布尔）
        - 原始请求的 domain/path/method 摘要
        """
        ctx = self._context or {}
        idents: List[Dict[str, Any]] = (ctx.get("identities") or [])
        ids_summary: List[Dict[str, Any]] = []

        def _dict_like_keys(obj: Any) -> List[str]:
            if isinstance(obj, dict):
                return [str(k) for k in obj.keys() if str(k).strip()]
            if isinstance(obj, str):
                s = obj.strip()
                if not s:
                    return []
                try:
                    j = json.loads(s)
                    if isinstance(j, dict):
                        return [str(k) for k in j.keys() if str(k).strip()]
                except Exception:
                    return []
            return []

        for i, ident in enumerate(idents):
            h_raw = ident.get("headers_json") or ident.get("headersJson") or ident.get("headers") or {}
            c_raw = ident.get("cookies_json") or ident.get("cookiesJson") or ident.get("cookies") or {}
            t_raw = ident.get("tokens_json") or ident.get("tokensJson") or ident.get("tokens") or {}
            h_keys = _dict_like_keys(h_raw)
            c_keys = _dict_like_keys(c_raw)
            t_keys = _dict_like_keys(t_raw)
            ids_summary.append({
                "idx": i,
                "headers_keys": h_keys[:50],
                "headers_count": len(h_keys),
                "cookies_keys": c_keys[:50],
                "cookies_count": len(c_keys),
                "tokens_keys": t_keys[:50],
                "tokens_count": len(t_keys),
            })

        has_horizontal = any(bool((ident or {}).get("horizontalUserId")) for ident in idents)
        has_vertical = any(bool((ident or {}).get("verticalUserId")) for ident in idents)

        try:
            parsed = urlparse(item.get("url", "") or "")
            dom = parsed.netloc
            pth = parsed.path or "/"
        except Exception:
            dom, pth = "", "/"
        method = str(item.get("method", "GET")).upper()

        logger.info(
            "[permission-diagnose] identities_total=%s hv_flags={'horizontal': %s, 'vertical': %s} request={'domain': '%s', 'path': '%s', 'method': '%s'} identities_summary=%s",
            len(idents),
            bool(has_horizontal),
            bool(has_vertical),
            dom,
            pth,
            method,
            ids_summary[:10]  # 控制体量
        )
            
    async def _process_single_item(self, item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理单个流量项目，返回“聚合后的”单条 item 列表（含 checks）"""
        if not self._context:
            return []
        
        try:
            # 检查域名是否匹配（域名过滤）
            if not self._should_process_item(item):
                return []
            
            # 聚合越权检测结果
            permission_checks = await self._perform_permission_tests(item)
            
            # 构造与后端 DTO 对齐的单条 item（保留原文与 base64，不截断）
            parsed = urlparse(item.get("url", "") or "")
            req_text = to_str_no_limit(item.get("requestBody"))
            resp_text = to_str_no_limit(item.get("responseBody"))
            req_b64 = to_str_no_limit(item.get("requestBodyBase64"))
            resp_b64 = to_str_no_limit(item.get("responseBodyBase64"))
            # headers 强制为 dict（统一调用助手修复）
            req_hdrs = fix_headers_field(item.get("requestHeaders"))
            resp_hdrs = fix_headers_field(item.get("responseHeaders"))

            ctx = self._context or {}
            aggregated_item = {
                "taskId": ctx.get("task_id"),
                "projectId": ctx.get("project_id") or ctx.get("projectId"),
                "domain": parsed.netloc,
                "path": parsed.path,
                "method": item.get("method", "GET"),
                "occurMs": item.get("occurMs"),
                "capturedAt": item.get("occurMs"),
                "statusCode": int(item.get("responseStatus") or 0),
                "requestMs": int(item.get("durationMs") or 0),
                "requestHeaders": req_hdrs,
                "responseHeaders": resp_hdrs,
                "requestBody": req_text,
                "requestBodyBase64": req_b64,
                "responseBody": resp_text,
                "responseBodyBase64": resp_b64,
                "url": item.get("url", ""),
                "query": item.get("query", ""),
                "checks": {
                    "sensitive": self._build_sensitive_check_result(item),
                    "horizontal": permission_checks.get("horizontal"),
                    "vertical": permission_checks.get("vertical")
                }
            }

            try:
                parsed = urlparse(item.get("url", "") or "")
                dom = (parsed.netloc.split(":")[0] if ":" in (parsed.netloc or "") else (parsed.netloc or "")).lower().strip()
                pth = parsed.path or "/"
                key = f"{dom}|{pth}"
                self._last_items[key] = {"item": dict(aggregated_item), "ts": time.time()}
            except Exception:
                pass

            pass
            
            # 返回“聚合项”列表（每个入队元素最多1条）
            return [aggregated_item]
        
        except Exception as e:
            logger.error(f"Error processing item: {e}")
            return []

    def get_last_item(self, domain: str, path: str) -> Optional[Dict[str, Any]]:
        try:
            dom = str(domain or "").strip().lower()
            pth = str(path or "/")
            key = f"{dom}|{pth}"
            entry = self._last_items.get(key)
            if not isinstance(entry, dict):
                return None
            now = time.time()
            ttl = 600
            try:
                from .config import load_config
                cfg = load_config() or {}
                ttl = int((((cfg.get("paramTest") or {}).get("lastItemTTLsec")) or 600))
            except Exception:
                ttl = 600
            ts = entry.get("ts")
            try:
                tsf = float(ts) if ts is not None else 0.0
            except Exception:
                tsf = 0.0
            if tsf > 0 and (now - tsf) > ttl:
                try:
                    del self._last_items[key]
                except Exception:
                    pass
                return None
            return entry.get("item")
        except Exception:
            return None

    def pop_last_item(self, domain: str, path: str) -> None:
        try:
            dom = str(domain or "").strip().lower()
            pth = str(path or "/")
            key = f"{dom}|{pth}"
            if key in self._last_items:
                del self._last_items[key]
        except Exception:
            pass

    def cache_last_item(self, item: Dict[str, Any]) -> None:
        try:
            u = str(item.get("url") or "")
            dom = str(item.get("domain") or "").strip().lower()
            pth = str(item.get("path") or "/")
            if u:
                try:
                    p = urlparse(u)
                    dom = (p.netloc.split(":")[0] if ":" in (p.netloc or "") else (p.netloc or "")).lower().strip() or dom
                    pth = p.path or pth or "/"
                except Exception:
                    pass
            key = f"{dom}|{pth}"
            if not dom:
                return
            if key not in self._last_items:
                self._last_items[key] = {"item": dict(item), "ts": time.time()}
        except Exception:
            pass
        
    def _should_process_item(self, item: Dict[str, Any]) -> bool:
        """检查是否应该处理此项目（域名过滤）"""
        if not self._context or not self._context.get("project_lines"):
            logger.warning(f"Context missing or no project_lines configured: context={bool(self._context)}")
            return False

        url = item.get("url", "")
        if not url:
            logger.warning(f"Item missing URL: {item}")
            return False

        try:
            parsed = urlparse(url)
            netloc = parsed.netloc

            # 规范化域名：去除端口号并转为小写
            domain = (netloc.split(':')[0] if ':' in netloc else netloc).lower().strip()
            if not domain:
                logger.warning(f"Failed to extract domain from URL: {url} (netloc={netloc})")
                return False

            # 检查域名是否匹配配置的项目域名列表（支持多种匹配方式）
            project_lines = self._context["project_lines"]
            for i, project_line in enumerate(project_lines):
                domains = project_line.get("domains", []) or []
                normalized_domains = [str(d).lower().strip() for d in domains if str(d).strip()]
                
                for config_domain in normalized_domains:
                    # 1. 精确匹配
                    if domain == config_domain:
                        logger.debug(f"Domain {domain} exact matched in project_line[{i}]: {config_domain}")
                        return True
                    
                    # 2. 通配符匹配 (*.example.com)
                    if config_domain.startswith('*.'):
                        suffix = config_domain[2:]  # 去掉 '*.'
                        if domain.endswith('.' + suffix) or domain == suffix:
                            logger.debug(f"Domain {domain} wildcard matched in project_line[{i}]: {config_domain}")
                            return True
                    
                    # 3. 子域名包含匹配
                    if ('.' + domain) in ('.' + config_domain) or domain.endswith('.' + config_domain):
                        logger.debug(f"Domain {domain} suffix matched in project_line[{i}]: {config_domain}")
                        return True
                    
                    if ('.' + config_domain) in ('.' + domain) or config_domain.endswith('.' + domain):
                        logger.debug(f"Domain {domain} prefix matched in project_line[{i}]: {config_domain}")
                        return True

            # 记录未匹配的详细信息
            all_configured_domains = []
            for project_line in project_lines:
                domains = project_line.get("domains", []) or []
                all_configured_domains.extend([str(d).lower().strip() for d in domains if str(d).strip()])
            
            logger.info(f"Domain {domain} not matched against configured domains: {all_configured_domains}")

        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")

        return False

    # 公有辅助：供入队前快速判定（api.notify使用）
    def should_accept_item(self, item: Dict[str, Any]) -> bool:
        """
        公有方法：是否接受该流量项进入实时队列
        - 内部回放请求（携带 X-SS-Internal）直接拒绝
        - 其余走域名过滤
        - 失败或异常时保守返回 False，避免非目标域名挤占队列
        """
        try:
            # 1) 内部回放标记（meta.internal）
            meta = (item.get("meta") or {}) if isinstance(item, dict) else {}
            internal_flag = bool((meta or {}).get("internal", False))

            # 2) 兜底：检测请求头是否包含 x-ss-internal（大小写不敏感）
            has_internal_hdr = _has_internal_header((item or {}).get("requestHeaders", {}) if isinstance(item, dict) else {})

            if internal_flag or has_internal_hdr:
                try:
                    parsed = urlparse(str((item or {}).get("url", "") or ""))
                    dom = parsed.netloc
                    pth = parsed.path or "/"
                except Exception:
                    dom, pth = "", ""
                # 记录过滤统计
                self._filtered_internal_count += 1
                if len(self._filtered_internal_examples) < 3:
                    self._filtered_internal_examples.append((dom, pth))
                logger.info("[realtime-queue] filtered internal replay: domain=%s path=%s has_internal_hdr=%s", dom, pth, bool(has_internal_hdr))
                return False

            # 3) 正常域名过滤
            return self._should_process_item(item)
        except Exception:
            return False

    def get_accepted_domains(self) -> List[str]:
        """
        公有方法：返回当前上下文配置的可接受域名（小写、去空格）
        便于调试或外部快速展示
        """
        doms: List[str] = []
        try:
            lines = (self._context or {}).get("project_lines") or []
            for line in lines:
                if isinstance(line, dict):
                    ds = line.get("domains", []) or []
                    doms.extend([str(d).lower().strip() for d in ds if str(d).strip()])
        except Exception:
            pass
        # 去重
        return list(dict.fromkeys(doms))
        
    async def _perform_permission_tests(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """执行越权检测并聚合为 checks 结构（horizontal/vertical）
        B1：完整身份透传。每条 identity 的 headers_json/cookies_json/tokens_json/custom_params 等原样透传，
        并在调用前按分支设置 identity_user_id。
        """
        ctx = self._context or {}
        if not ctx.get("identities"):
            return {"horizontal": None, "vertical": None}
        
        strategies = ctx.get("strategies", ["horizontal", "vertical"])
        identities = ctx.get("identities", [])
        
        # 构造原始请求/响应
        original_request = {
            "method": item.get("method", "GET"),
            "url": item.get("url", ""),
            "headers": item.get("requestHeaders", {}) or {},
            "request_body": item.get("requestBody", "") or ""
        }
        original_response = {
            "status": item.get("responseStatus", 0),
            "response_body": item.get("responseBody", "") or "",
            "response_headers": item.get("responseHeaders", {}) or {}
        }

        # 实时-越权：开始越权身份替换时打印原始请求完整信息（header、url、params、requestbody）
        try:
            p = urlparse(original_request.get("url") or "")
            params_map: Dict[str, Any] = {}
            try:
                import urllib.parse as _up
                params_map = dict(_up.parse_qsl(p.query or "", keep_blank_values=True))
            except Exception:
                params_map = {}

            logger.info("实时-越权 | 原始请求完整信息 | method=%s url=%s",
                        original_request.get("method"), original_request.get("url"))
            logger.info("实时-越权 | 原始请求完整信息 | headers=%s",
                        fix_headers_field(original_request.get("headers")))
            logger.info("实时-越权 | 原始请求完整信息 | params=%s", params_map)
            logger.info("实时-越权 | 原始请求完整信息 | requestBody=%s",
                        to_str_no_limit(original_request.get("request_body")))
        except Exception:
            pass
        
        # 聚合结果：收集同类的所有 evidence，并计算最高风险等级
        evidence_lists: Dict[str, List[Dict[str, Any]]] = {"horizontal": [], "vertical": []}
        agg_risk: Dict[str, str] = {"horizontal": "NONE", "vertical": "NONE"}
        priority = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}

        def update_best(kind: str, res: Optional[Dict[str, Any]]):
            if not res:
                return
            # 追加证据到列表
            ev = res.get("evidence")
            if isinstance(ev, dict):
                evidence_lists[kind].append(ev)
            elif ev is not None:
                # 兼容非 dict 的情况，统一包装为对象
                try:
                    evidence_lists[kind].append({"_": ev})
                except Exception:
                    pass
            # 聚合风险等级（取最大）
            rl = str(res.get("riskLevel") or "NONE").upper()
            try:
                cur_score = priority.get(agg_risk.get(kind, "NONE"), 0)
                new_score = priority.get(rl, 0)
                if new_score > cur_score:
                    agg_risk[kind] = rl
            except Exception:
                pass
        
        # 对每个身份配置执行测试并聚合（完整身份对象透传）
        # 实时-越权：要替换的身份A/B的请求头信息（只记录前两个可用身份）
        try:
            _labels = ["A", "B"]
            _logged = 0
            for _ident in identities:
                if _logged >= 2:
                    break
                if not (_ident.get("horizontalUserId") or _ident.get("verticalUserId")):
                    continue
                _hdrs = _ident.get("headers_json") or _ident.get("headersJson") or _ident.get("headers") or {}
                logger.info("实时-越权 | 要替换的身份%s的请求头信息：%s", _labels[_logged], fix_headers_field(_hdrs))
                _logged += 1
        except Exception:
            pass

        # 执行具体测试（仅当存在至少两个可用身份时才进行越权检测；A/B 均为回放请求）
        # 水平越权：选取前两个具有 horizontalUserId 的身份作为 A/B
        if "horizontal" in strategies:
            try:
                idents_h = [i for i in identities if i.get("horizontalUserId")]
            except Exception:
                idents_h = []
            if len(idents_h) >= 2:
                identityA = dict(idents_h[0] or {})
                identityB = dict(idents_h[1] or {})
                identityA["identity_user_id"] = identityA.get("horizontalUserId")
                identityB["identity_user_id"] = identityB.get("horizontalUserId")
                r_h_pair = await self._test_pair_identities(
                    original_request, original_response,
                    identityA, identityB, "horizontal", item
                )
                update_best("horizontal", r_h_pair)
            else:
                try:
                    logger.info("实时-越权 | 跳过水平越权检测：可用身份不足（%s）", len(idents_h))
                except Exception:
                    pass

        # 垂直越权：选取前两个具有 verticalUserId 的身份作为 A/B
        if "vertical" in strategies:
            try:
                idents_v = [i for i in identities if i.get("verticalUserId")]
            except Exception:
                idents_v = []
            if len(idents_v) >= 2:
                identityA = dict(idents_v[0] or {})
                identityB = dict(idents_v[1] or {})
                identityA["identity_user_id"] = identityA.get("verticalUserId")
                identityB["identity_user_id"] = identityB.get("verticalUserId")
                r_v_pair = await self._test_pair_identities(
                    original_request, original_response,
                    identityA, identityB, "vertical", item
                )
                update_best("vertical", r_v_pair)
            else:
                try:
                    logger.info("实时-越权 | 跳过垂直越权检测：可用身份不足（%s）", len(idents_v))
                except Exception:
                    pass
        # 输出聚合结构：evidence 为数组，riskLevel 为最高级别
        result: Dict[str, Optional[Dict[str, Any]]] = {"horizontal": None, "vertical": None}
        for kind in ("horizontal", "vertical"):
            if evidence_lists[kind]:
                result[kind] = {
                    "riskLevel": agg_risk.get(kind, "NONE"),
                    "evidence": evidence_lists[kind]
                }
            else:
                result[kind] = None
        return result
        
    async def _test_with_identity(self, original_request: Dict[str, Any],
                                 original_response: Dict[str, Any],
                                 identity: Dict[str, Any], test_type: str,
                                 item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用指定身份执行一次回放请求（内部辅助函数）
        - 当前越权检测仅进行 A/B 双身份对比，单身份结果不参与上报
        - B1：完整身份透传，移除仅字符串 userId 的构造
        - 兼容旧 context：若缺少 identity_user_id，尝试从 user_id/uid/custom_params.userId 回填
        - B2（可选扩展）：未来可基于 identity_user_id 拉取身份详情并合并（本次不实现）
        """
        try:
            # 兼容旧 context：确保 identity_user_id 存在（不抛错）
            identity = dict(identity or {})
            identity_user_id = identity.get("identity_user_id")
            if not identity_user_id:
                try:
                    identity_user_id = identity.get("user_id") or identity.get("uid")
                    if not identity_user_id:
                        cp = identity.get("custom_params") or identity.get("customParams") or {}
                        if isinstance(cp, dict):
                            identity_user_id = cp.get("userId") or cp.get("uid") or cp.get("user_id")
                except Exception:
                    identity_user_id = None
                if identity_user_id:
                    identity["identity_user_id"] = identity_user_id

            # 修改请求（完整身份对象）
            modified_request = modify_request_with_identity(original_request, identity)

            # 实时-越权：使用身份替换后的完整请求信息（header、url、params、requestbody）
            try:
                mp = urlparse(modified_request.get("url") or "")
                _params_map: Dict[str, Any] = {}
                try:
                    import urllib.parse as _up
                    _params_map = dict(_up.parse_qsl(mp.query or "", keep_blank_values=True))
                except Exception:
                    _params_map = {}
                _body_text = to_str_no_limit(modified_request.get("request_body", modified_request.get("body", "")))
                logger.info(
                    "实时-越权 | 使用身份替换后的完整请求信息 | type=%s identityUserId=%s method=%s url=%s",
                    test_type, identity.get("identity_user_id"), modified_request.get("method"), modified_request.get("url")
                )
                logger.info("实时-越权 | 使用身份替换后的完整请求信息 | headers=%s",
                            fix_headers_field(modified_request.get("headers")))
                logger.info("实时-越权 | 使用身份替换后的完整请求信息 | params=%s", _params_map)
                logger.info("实时-越权 | 使用身份替换后的完整请求信息 | requestBody=%s", _body_text)
            except Exception:
                pass

            # 发送修改后的请求
            modified_response = await self._send_modified_request(modified_request)

            # 实时-越权：使用身份发送请求后的完整返回结果（response code、response body）
            try:
                logger.info(
                    "实时-越权 | 使用身份发送请求后的完整返回结果 | type=%s identityUserId=%s status=%s",
                    test_type, identity.get("identity_user_id"), modified_response.get("status")
                )
                logger.info("实时-越权 | 使用身份发送请求后的完整返回结果 | responseBody=%s",
                            to_str_no_limit(modified_response.get("text", "")))
            except Exception:
                pass
            
            # 比较响应
            comparison = compare_responses(original_response, modified_response)
            
            # 映射风险等级
            try:
                orig_status, mod_status = comparison.get("status_diff", (0, 0))
                similarity = float(comparison.get("content_similarity", 0.0))
            except Exception:
                orig_status, mod_status, similarity = 0, 0, 0.0
            risk_level = map_excel_risk_level(orig_status, mod_status, similarity)
            
            # 安全的 Base64 编码（统一为字符串输入）
            def _safe_b64(v: Any) -> str:
                try:
                    # dict/list 使用 JSON 序列化，保持可解析性
                    if isinstance(v, (dict, list)):
                        s = json.dumps(v, ensure_ascii=False)
                    else:
                        s = to_str_no_limit(v)
                    if s is None:
                        return ""
                    if not isinstance(s, str):
                        s = str(s)
                    if s == "":
                        return ""
                    return base64.b64encode(s.encode("utf-8")).decode("ascii")
                except Exception:
                    return ""

            # 构造检测结果（保持最小侵入，供聚合器使用）
            result = {
                "taskId": (self._context or {}).get("task_id"),
                "domain": urlparse(item.get("url", "")).netloc,
                "path": urlparse(item.get("url", "")).path,
                "method": item.get("method", "GET"),
                "occurMs": item.get("occurMs"),
                "checkType": test_type,
                "riskLevel": risk_level,
                "evidence": {
                    "originalStatus": original_response.get("status"),
                    "modifiedStatus": modified_response.get("status"),
                    "contentSimilarity": comparison.get("content_similarity", 0.0),
                    "grantedAccess": comparison.get("granted_access", False),
                    "sameContent": comparison.get("same_content", False),
   
                    "originalRequestHeaders": fix_headers_field(original_request.get("headers")),
                    "originalResponseHeaders": fix_headers_field(original_response.get("response_headers")),
                    # 兼容后端候选字段：reqHeadersA/respHeadersA/requestHeadersA
                    "reqHeadersA": fix_headers_field(original_request.get("headers")),
                    "respHeadersA": fix_headers_field(original_response.get("response_headers")),
                    "requestHeadersA": fix_headers_field(original_request.get("headers")),
                    "requestBodyABase64": _safe_b64(original_request.get("request_body", original_request.get("body", ""))),
                    "responseBodyABase64": _safe_b64(original_response.get("text", "")),
                    # B 侧（使用B身份后的请求/响应）
                    "modifiedRequestHeaders": fix_headers_field(modified_request.get("headers")),
                    "modifiedResponseHeaders": fix_headers_field(modified_response.get("headers")),
                    # 兼容后端候选字段：reqHeadersB/respHeadersB/requestHeadersB
                    "reqHeadersB": fix_headers_field(modified_request.get("headers")),
                    "respHeadersB": fix_headers_field(modified_response.get("headers")),
                    "requestHeadersB": fix_headers_field(modified_request.get("headers")),
                    "requestBodyBBase64": _safe_b64(modified_request.get("request_body", modified_request.get("body", ""))),
                    "responseBodyBBase64": _safe_b64(modified_response.get("text", ""))
                },
                "executedAt": int(time.time() * 1000),
                "requestHeaders": item.get("requestHeaders", {}),
                "responseHeaders": item.get("responseHeaders", {}),
                "requestBodyBase64": item.get("requestBodyBase64", ""),
                "responseBodyBase64": item.get("responseBodyBase64", "")
            }

            # 实时-越权：该接口的越权检测结果信息
            try:
                logger.info(
                    "实时-越权 | 该接口越权检测结果 | type=%s identityUserId=%s riskLevel=%s evidence=%s",
                    test_type, identity.get("identity_user_id"), risk_level,
                    json.dumps(result.get("evidence", {}), ensure_ascii=False)
                )
            except Exception:
                pass
            return result
            
        except Exception as e:
            logger.error(f"Permission test error for {test_type}: {e}")
            return None

    async def _test_pair_identities(self, original_request: Dict[str, Any],
                                    original_response: Dict[str, Any],
                                    identityA: Dict[str, Any], identityB: Dict[str, Any],
                                    test_type: str, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用两个身份执行越权对比（A/B均为回放请求），并构造成 A/B 证据结构。
        - A：identityA 替换后的回放请求/响应
        - B：identityB 替换后的回放请求/响应
        风险评估：比较 A vs B 两次回放的结果（状态码与内容相似度）
        """
        try:
            # 构造并发送 A/B 两侧回放请求
            mod_req_A = modify_request_with_identity(original_request, dict(identityA or {}))
            mod_rsp_A = await self._send_modified_request(mod_req_A)

            mod_req_B = modify_request_with_identity(original_request, dict(identityB or {}))
            mod_rsp_B = await self._send_modified_request(mod_req_B)

            # 打印两侧请求/响应摘要日志
            try:
                logger.info("实时-越权 | A侧回放 | headers=%s", fix_headers_field(mod_req_A.get("headers")))
                logger.info("实时-越权 | A侧回放 | status=%s", mod_rsp_A.get("status"))
                logger.info("实时-越权 | B侧回放 | headers=%s", fix_headers_field(mod_req_B.get("headers")))
                logger.info("实时-越权 | B侧回放 | status=%s", mod_rsp_B.get("status"))
            except Exception:
                pass

            # 比较 A/B 两侧响应
            comparison = compare_responses(mod_rsp_A, mod_rsp_B)
            try:
                statusA, statusB = comparison.get("status_diff", (0, 0))
                similarity = float(comparison.get("content_similarity", 0.0))
            except Exception:
                statusA, statusB, similarity = 0, 0, 0.0
            risk_level = map_excel_risk_level(statusA, statusB, similarity)

            # 安全 Base64
            def _safe_b64(v: Any) -> str:
                try:
                    if isinstance(v, (dict, list)):
                        s = json.dumps(v, ensure_ascii=False)
                    else:
                        s = to_str_no_limit(v)
                    if s is None:
                        return ""
                    if not isinstance(s, str):
                        s = str(s)
                    if s == "":
                        return ""
                    return base64.b64encode(s.encode("utf-8")).decode("ascii")
                except Exception:
                    return ""

            result = {
                "taskId": (self._context or {}).get("task_id"),
                "domain": urlparse(item.get("url", "")).netloc,
                "path": urlparse(item.get("url", "")).path,
                "method": item.get("method", "GET"),
                "occurMs": item.get("occurMs"),
                "checkType": test_type,
                "riskLevel": risk_level,
                "evidence": {
                    # 身份与状态补充（A/B身份对比场景）
                    "identity1": identityA.get("identity_user_id"),
                    "identity2": identityB.get("identity_user_id"),
                    "identity1Status": mod_rsp_A.get("status"),
                    "identity2Status": mod_rsp_B.get("status"),
                    # 对比摘要
                    "statusA": statusA,
                    "statusB": statusB,
                    "contentSimilarity": comparison.get("content_similarity", 0.0),
                    "sameContent": comparison.get("same_content", False),
                    "grantedAccess": comparison.get("granted_access", False),
                    # A侧：使用A身份替换后的回放请求/响应
                    "reqHeadersA": fix_headers_field(mod_req_A.get("headers")),
                    "respHeadersA": fix_headers_field(mod_rsp_A.get("headers")),
                    "requestHeadersA": fix_headers_field(mod_req_A.get("headers")),
                    "requestBodyABase64": _safe_b64(mod_req_A.get("request_body", mod_req_A.get("body", ""))),
                    "responseBodyABase64": _safe_b64(mod_rsp_A.get("text", "")),
                    # B侧：使用B身份替换后的回放请求/响应
                    "reqHeadersB": fix_headers_field(mod_req_B.get("headers")),
                    "respHeadersB": fix_headers_field(mod_rsp_B.get("headers")),
                    "requestHeadersB": fix_headers_field(mod_req_B.get("headers")),
                    "requestBodyBBase64": _safe_b64(mod_req_B.get("request_body", mod_req_B.get("body", ""))),
                    "responseBodyBBase64": _safe_b64(mod_rsp_B.get("text", ""))
                },
                "executedAt": int(time.time() * 1000),
                "requestHeaders": item.get("requestHeaders", {}),
                "responseHeaders": item.get("responseHeaders", {}),
                "requestBodyBase64": item.get("requestBodyBase64", ""),
                "responseBodyBase64": item.get("responseBodyBase64", "")
            }

            try:
                logger.info(
                    "实时-越权 | A/B身份对比 | riskLevel=%s evidencePreviewKeys=%s",
                    risk_level, list(result.get("evidence", {}).keys())
                )
            except Exception:
                pass

            return result
        except Exception as e:
            logger.error(f"Permission pair test error for {test_type}: {e}")
            return None
            
    async def _send_modified_request(self, modified_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送修改后的请求
        - headers 强制规范化为 dict（使用 fix_headers_field）
        - 不覆盖已有非空 X-SS-Internal（大小写不敏感）
        - 若缺失或为空，则注入 X-SS-Internal: permission-test
        - 日志：输出 "[HTTP-REQUEST] inject_internal_hdr=true/false"（不含明文值）
        """
        try:
            method = modified_request.get("method", "GET")
            url = modified_request.get("url", "")
            headers = dict(fix_headers_field(modified_request.get("headers")) or {})
            body = modified_request.get("request_body", modified_request.get("body", ""))

            # 发送前判空：method/url 不能为空
            if not str(method).strip() or not str(url).strip():
                try:
                    logger.warning("[HTTP-REQUEST] skip send: invalid method/url | method=%s url=%s", method, url)
                except Exception:
                    pass
                return {"status": 0, "text": "", "headers": {}}

            # 一次性内判标记：记录下一条相同 domain|path 的flow事件应跳过（无时间窗）
            try:
                p = urlparse(url or "")
                dom = (p.netloc.split(":")[0] if ":" in (p.netloc or "") else (p.netloc or "")).lower().strip()
                pth = p.path or "/"
                key = f"{dom}|{pth}"
                self._pending_internal_key = key
                logger.info("[realtime-queue] one_shot_mark key=%s", key)
            except Exception:
                pass
    
            # 大小写不敏感检测是否已有非空内部标头
            present_non_empty = False
            for k, v in list(headers.items()):
                if str(k).lower().strip() == "x-ss-internal":
                    if str(v).strip():
                        present_non_empty = True
                    break
    
            # 发送前清理可能导致错误的长度头，由客户端自动计算
            try:
                for k in list(headers.keys()):
                    if str(k).lower().strip() == "content-length":
                        headers.pop(k, None)
                for k in list(headers.keys()):
                    kl = str(k).lower().strip()
                    if kl in ("if-none-match", "if-modified-since", "if-range"):
                        headers.pop(k, None)
                headers.setdefault("Cache-Control", "no-cache")
            except Exception:
                pass

            injected = False
            if not present_non_empty:
                headers["X-SS-Internal"] = "permission-test"
                injected = True
    
            # 仅输出是否注入的布尔摘要，避免敏感信息泄露
            try:
                logger.info("[HTTP-REQUEST] inject_internal_hdr=%s", "true" if injected else "false")
            except Exception:
                pass
    
            # httpx 可用时走异步客户端；不可用时使用 urllib 进行同步请求并通过线程池适配
            import os
            try:
                timeout_sec = float(os.getenv("REPLAY_TIMEOUT_SEC", "20"))
            except Exception:
                timeout_sec = 20.0
            if httpx is not None:
                async with httpx.AsyncClient(timeout=timeout_sec) as client:
                    # 修复：当 body 为 dict/list（JSON）时，使用 json 参数而不是 content，避免类型错误
                    if isinstance(body, (dict, list)):
                        response = await client.request(
                            method=method,
                            url=url,
                            headers=headers,
                            json=body
                        )
                    else:
                        response = await client.request(
                            method=method,
                            url=url,
                            headers=headers,
                            content=body
                        )
                    return {
                        "status": response.status_code,
                        "text": response.text,
                        "headers": dict(response.headers)
                    }
            else:
                import urllib.request
                import urllib.error

                def _sync_request() -> Dict[str, Any]:
                    try:
                        data_bytes: Optional[bytes] = None
                        hdrs = dict(headers or {})
                        # JSON 体统一转字符串并设置 Content-Type
                        if isinstance(body, (dict, list)):
                            text = json.dumps(body, ensure_ascii=False)
                            data_bytes = text.encode("utf-8")
                            if "Content-Type" not in {k.title(): k for k in hdrs}.keys():
                                hdrs["Content-Type"] = "application/json; charset=utf-8"
                        elif isinstance(body, (bytes, bytearray)):
                            data_bytes = bytes(body)
                        elif isinstance(body, str):
                            if body:
                                data_bytes = body.encode("utf-8")
                        req = urllib.request.Request(url=url, data=data_bytes, headers=hdrs, method=method)
                        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                            status = getattr(resp, "status", 0)
                            # 解析响应头
                            try:
                                resp_headers = dict(resp.getheaders())
                            except Exception:
                                try:
                                    resp_headers = dict(resp.headers.items())
                                except Exception:
                                    resp_headers = {}
                            # 解码响应体
                            raw = resp.read() or b""
                            ctype = "";
                            try:
                                ctype = resp_headers.get("Content-Type") or resp.headers.get("Content-Type") or ""
                            except Exception:
                                pass
                            charset = "utf-8"
                            if isinstance(ctype, str) and "charset=" in ctype:
                                try:
                                    charset = ctype.split("charset=")[-1].strip()
                                except Exception:
                                    charset = "utf-8"
                            try:
                                text = raw.decode(charset, errors="replace")
                            except Exception:
                                text = raw.decode("utf-8", errors="replace")
                            return {"status": status, "text": text, "headers": resp_headers}
                    except urllib.error.HTTPError as e:
                        try:
                            body_bytes = e.read() or b""
                            text = body_bytes.decode("utf-8", errors="replace")
                        except Exception:
                            text = ""
                        return {"status": e.code or 0, "text": text, "headers": dict(e.headers or {})}
                    except Exception as e:
                        logger.error(f"HTTP request fallback error: {e}")
                        msg = str(e) if str(e) else "error: request failed or timeout"
                        return {"status": 0, "text": msg, "headers": {}}

                # 在线程池中执行同步请求，避免阻塞事件循环
                return await asyncio.to_thread(_sync_request)
        except HTTPXTimeout as e:
            try:
                logger.error(f"HTTP request timeout after {timeout_sec}s: {e}")
            except Exception:
                pass
            return {"status": 0, "text": f"timeout after {timeout_sec}s: {e}", "headers": {}}
        except HTTPXNetworkError as e:
            try:
                logger.error(f"HTTP network error: {e}")
            except Exception:
                pass
            return {"status": 0, "text": str(e), "headers": {}}
        except Exception as e:
            logger.error(f"Error sending modified request: {e}")
            msg = str(e) if str(e) else "error: request failed or timeout"
            return {"status": 0, "text": msg, "headers": {}}
            
    def _build_sensitive_check_result(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """构造敏感检测结果（保留原文、证据片段与样例；由后端执行具体检测）"""
        try:
            ctx = self._context or {}
            parsed = urlparse(item.get("url", "") or "")
            req_text = to_str_no_limit(item.get("requestBody"))
            resp_text = to_str_no_limit(item.get("responseBody"))
            req_b64 = to_str_no_limit(item.get("requestBodyBase64"))
            resp_b64 = to_str_no_limit(item.get("responseBodyBase64"))

            evidence: Dict[str, Any] = {
                "requestFragment": req_text or "",
                "responseFragment": resp_text or "",
                "metadata": {
                    "requestEncoding": (item.get("encoding", {}) or {}).get("request") or ("base64" if req_b64 else "utf8"),
                    "responseEncoding": (item.get("encoding", {}) or {}).get("response") or ("base64" if resp_b64 else "utf8"),
                }
            }

            samples: List[str] = []
            try:
                samples.extend(self._collect_json_samples(req_text, max_samples=50))
            except Exception:
                pass
            try:
                samples.extend(self._collect_json_samples(resp_text, max_samples=50))
            except Exception:
                pass
            if samples:
                evidence["samples"] = samples[:50]

            return {
                "taskId": ctx.get("task_id"),
                "projectId": ctx.get("project_id") or ctx.get("projectId"),
                "domain": parsed.netloc,
                "path": parsed.path,
                "method": item.get("method", "GET"),
                "occurMs": item.get("occurMs"),
                "capturedAt": item.get("occurMs"),
                "url": item.get("url", ""),
                "query": item.get("query", ""),
                "checkType": "sensitive",
                "riskLevel": "NONE",
                "evidence": evidence,
                "executedAt": int(time.time() * 1000),
                "requestHeaders": item.get("requestHeaders", {}),
                "responseHeaders": item.get("responseHeaders", {}),
                "requestBodyBase64": req_b64,
                "responseBodyBase64": resp_b64,
                "requestBody": req_text,
                "responseBody": resp_text,
            }
        except Exception:
            ctx = self._context or {}
            return {
                "taskId": ctx.get("task_id"),
                "projectId": ctx.get("project_id") or ctx.get("projectId"),
                "domain": urlparse(item.get("url", "")).netloc,
                "path": urlparse(item.get("url", "")).path,
                "method": item.get("method", "GET"),
                "occurMs": item.get("occurMs"),
                "capturedAt": item.get("occurMs"),
                "url": item.get("url", ""),
                "query": item.get("query", ""),
                "checkType": "sensitive",
                "riskLevel": "NONE",
                "evidence": {},
                "executedAt": int(time.time() * 1000),
                "requestHeaders": item.get("requestHeaders", {}),
                "responseHeaders": item.get("responseHeaders", {}),
                "requestBodyBase64": item.get("requestBodyBase64", ""),
                "responseBodyBase64": item.get("responseBodyBase64", ""),
                "requestBody": to_str_no_limit(item.get("requestBody")),
                "responseBody": to_str_no_limit(item.get("responseBody")),
            }

    def _collect_json_samples(self, text: str, max_samples: int = 50) -> List[str]:
        """采集 JSON 样例路径:值（不脱敏），最多 max_samples 条"""
        out: List[str] = []
        if not text:
            return out
        try:
            obj = json.loads(text)
        except Exception:
            return out

        def walk(node: Any, path: str):
            if len(out) >= max_samples:
                return
            if isinstance(node, dict):
                for k, v in node.items():
                    if len(out) >= max_samples:
                        break
                    key = str(k)
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(v, (dict, list)):
                        walk(v, new_path)
                    else:
                        try:
                            out.append(f"{new_path}: {to_str_no_limit(v)}")
                        except Exception:
                            out.append(f"{new_path}: <unserializable>")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    if len(out) >= max_samples:
                        break
                    new_path = f"{path}[{i}]" if path else f"[{i}]"
                    if isinstance(v, (dict, list)):
                        walk(v, new_path)
                    else:
                        try:
                            out.append(f"{new_path}: {to_str_no_limit(v)}")
                        except Exception:
                            out.append(f"{new_path}: <unserializable>")
            else:
                out.append(f"{path or '$'}: {to_str_no_limit(node)}")

        walk(obj, "")
        return out
        
    async def _batch_report_to_backend(self, results: List[Dict[str, Any]]):
        """批量上报检测结果到后端"""
        if not results or not self._context:
            logger.warning(f"Skipping batch report: results={len(results) if results else 0}, context={'present' if self._context else 'missing'}")
            return
            
        backend_api: Optional[BackendAPI] = None
        try:
            # 记录上下文信息用于调试（键名）
            context_keys = list(self._context.keys()) if self._context else []
            logger.info(f"Building backend API client with context keys: {context_keys}")
            
            # 使用标准的 BackendAPI 客户端进行上报
            backend_api = build_backend_api_from_context(self._context)
            
            # 修复数据格式：确保 headers 为对象；保留原文与 base64；清理空键与 None
            fixed_results = []
            total_req_len = 0
            total_resp_len = 0
            for result in results:
                fixed_result = result.copy()
                
                # 修复 requestHeaders 和 responseHeaders 格式
                req_hdrs = fix_headers_field(result.get("requestHeaders"))
                resp_hdrs = fix_headers_field(result.get("responseHeaders"))
                # 清理空键与 None 值
                def _clean(h: Dict[str, Any]) -> Dict[str, Any]:
                    cleaned: Dict[str, Any] = {}
                    for k, v in (h or {}).items():
                        try:
                            key = str(k).strip()
                        except Exception:
                            key = ""
                        if not key:
                            continue
                        if v is None:
                            continue
                        cleaned[key] = v
                    return cleaned
                fixed_result["requestHeaders"] = _clean(req_hdrs)
                fixed_result["responseHeaders"] = _clean(resp_hdrs)
                
                # 原文保留：不截断；保留 base64
                req_text = to_str_no_limit(result.get("requestBody"))
                resp_text = to_str_no_limit(result.get("responseBody"))
                fixed_result["requestBody"] = req_text
                fixed_result["responseBody"] = resp_text
                for k in ("requestBodyBase64", "responseBodyBase64"):
                    if k in fixed_result:
                        fixed_result[k] = to_str_no_limit(fixed_result.get(k))

                total_req_len += len(fixed_result.get("requestBody") or "")
                total_resp_len += len(fixed_result.get("responseBody") or "")
                
                fixed_results.append(fixed_result)
            
            # 获取 task_id（兼容两种键名）
            ctx = self._context or {}
            task_id = (ctx.get("task_id") or ctx.get("taskId") or ctx.get("task_id"))
            
            if not task_id:
                logger.error("Task ID not found in context, cannot proceed with batch report")
                return
            
            # 构造请求体
            payload = {
                "taskId": task_id,
                "items": fixed_results
            }
            # 实时-越权：上报的越权检测结果信息（完整payload）
            try:
                logger.info("实时-越权 | 上报越权检测结果 | payload=%s", json.dumps(payload, ensure_ascii=False))
            except Exception:
                pass
            
            headers_req_all_dict = all(isinstance(it.get("requestHeaders"), dict) for it in fixed_results)
            headers_resp_all_dict = all(isinstance(it.get("responseHeaders"), dict) for it in fixed_results)
            logger.info(
                "[HTTP-REQUEST] batch_summary items=%s headers_req_all_dict=%s headers_resp_all_dict=%s total_body_text_len=%s",
                len(fixed_results),
                bool(headers_req_all_dict),
                bool(headers_resp_all_dict),
                (total_req_len + total_resp_len)
            )
            
            # 上报
            resp_data = await backend_api.realtime_batch_ingest(
                payload=payload,
                task_id=task_id
            )
            # 实时-越权：上报返回结果（完整返回值）
            try:
                logger.info("实时-越权 | 上报返回结果 | response=%s", to_str_no_limit(resp_data))
            except Exception:
                pass
            logger.info(f"Successfully reported {len(results)} results to backend using BackendAPI")
            try:
                data = (resp_data.get('data') or resp_data) if isinstance(resp_data, dict) else {}
                ids = data.get('interfaceIds') or []
                if isinstance(ids, list):
                    for i, iid in enumerate(ids):
                        try:
                            if i < len(results) and iid is not None:
                                results[i]['interfaceId'] = iid
                                try:
                                    dom = str(results[i].get('domain') or '').strip().lower()
                                    pth = str(results[i].get('path') or '/')
                                    key = f"{dom}|{pth}"
                                    entry = self._last_items.get(key)
                                    if isinstance(entry, dict) and isinstance(entry.get('item'), dict):
                                        entry['item']['interfaceId'] = iid
                                        entry['ts'] = time.time()
                                        self._last_items[key] = entry
                                except Exception:
                                    pass
                                try:
                                    logger.info("【精确绑定】本地入参入队 interfaceId=%s domain=%s path=%s occurMs=%s", str(iid), str(results[i].get('domain') or ''), str(results[i].get('path') or '/'), str(results[i].get('occurMs')))
                                except Exception:
                                    pass
                                try:
                                    from .param_test_throttler import enqueue_param_test
                                    ctx = self._context or {}
                                    cfg = ctx.get("paramTest") or ctx.get("param_test") or {}
                                    en = bool(cfg.get("enabled"))
                                    allow = set([str(x).strip().upper() for x in (cfg.get("methods") or []) if str(x).strip()])
                                    mth = str(results[i].get("method") or "GET").strip().upper()
                                    if en and (not allow or mth in allow):
                                        asyncio.create_task(enqueue_param_test(results[i], ctx))
                                    else:
                                        try:
                                            logger.info("【入参测试问题排查】入参测试未启用或方法未允许，跳过 method=%s allow=%s", mth, list(allow))
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                        except Exception:
                            pass
            except Exception:
                pass
            
        except Exception as e:
            logger.error(f"Failed to report results to backend: {e}")
            logger.error(f"Context available: {bool(self._context)}")
            if self._context:
                # 脱敏上下文摘要
                ctx2 = self._context or {}
                project_id_raw = ctx2.get("project_id")
                projectId_raw = ctx2.get("projectId")
                user_id_raw = ctx2.get("user_id")
                userId_raw = ctx2.get("userId")
                client_id_raw = ctx2.get("client_id")
                clientId_raw = ctx2.get("clientId")
                task_id_raw = ctx2.get("task_id")
                taskId_raw = ctx2.get("taskId")
                
                context_summary = {
                    "has_project_id": (project_id_raw is not None) or (projectId_raw is not None),
                    "has_user_id": bool(user_id_raw or userId_raw),
                    "has_client_id": bool(client_id_raw or clientId_raw),
                    "has_task_id": bool(task_id_raw or taskId_raw),
                    "context_keys": list(ctx2.keys()),
                }
                logger.error(f"Context summary: {context_summary}")
        finally:
            # 确保关闭 backend_api 连接
            try:
                if backend_api is not None:
                    await backend_api.close()
            except Exception:
                pass
            
                
    async def _final_flush(self):
        """最终冲刷剩余队列"""
        logger.info("Performing final flush of remaining queue items")
        
        while True:
            batch = []
            async with self._queue_lock:
                for _ in range(min(self.batch_size, len(self._queue))):
                    if self._queue:
                        batch.append(self._queue.popleft())
                        
            if not batch:
                break
                
            try:
                results = []
                for item in batch:
                    # 越权前置诊断（降敏）
                    try:
                        self._log_permission_pre_diagnose(item)
                    except Exception:
                        pass

                    item_results = await self._process_single_item(item)
                    results.extend(item_results)
                    
                if results:
                    try:
                        dedup_map: Dict[str, Dict[str, Any]] = {}
                        for r in results:
                            try:
                                dom = str(r.get("domain") or "").lower().strip()
                                pth = str(r.get("path") or "/")
                                key = f"{dom}|{pth}"
                                occ = r.get("occurMs")
                                try:
                                    occ_i = int(occ) if isinstance(occ, (int, float)) else (int(str(occ).strip()) if (occ is not None and str(occ).strip()) else 0)
                                except Exception:
                                    occ_i = 0
                                existing = dedup_map.get(key)
                                if existing is None:
                                    dedup_map[key] = r
                                else:
                                    try:
                                        ex_occ = existing.get("occurMs")
                                        ex_i = int(ex_occ) if isinstance(ex_occ, (int, float)) else (int(str(ex_occ).strip()) if (ex_occ is not None and str(ex_occ).strip()) else 0)
                                    except Exception:
                                        ex_i = 0
                                    if occ_i >= ex_i:
                                        dedup_map[key] = r
                            except Exception:
                                pass
                        deduped_results = list(dedup_map.values())
                        try:
                            logger.info("[realtime-queue] dedupe_summary groups=%s reduced=%s by=domain|path", len(dedup_map), (len(results) - len(deduped_results)))
                        except Exception:
                            pass
                    except Exception:
                        deduped_results = results

                    # 直接上报（最终冲刷保留批次内 domain|path 去重）
                    await self._batch_report_to_backend(deduped_results)
                    
                self._processed_count += len(batch)
                
            except Exception as e:
                logger.error(f"Final flush batch error: {e}")


# 全局队列实例
_realtime_queue: Optional[RealtimeQueue] = None

def get_realtime_queue() -> Optional[RealtimeQueue]:
    """获取全局队列实例"""
    return _realtime_queue

def init_realtime_queue(config: Dict[str, Any]) -> RealtimeQueue:
    """初始化全局队列实例"""
    global _realtime_queue
    _realtime_queue = RealtimeQueue(config)
    return _realtime_queue

# 域名匹配辅助函数
def should_accept_domain(domain: str, accepted_domains: List[str]) -> bool:
    """检查域名是否应该被接受"""
    return domain in accepted_domains

def _build_accepted_domains(project_lines: List[Dict[str, Any]]) -> List[str]:
    """从项目配置构建接受的域名列表"""
    domains = []
    for line in project_lines:
        domains.extend(line.get("domains", []))
    return domains

async def _compute_checks_for_item(item: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """为单个项目计算检测结果（兼容性函数）"""
    queue = get_realtime_queue()
    if queue:
        return await queue._process_single_item(item)
    return []
