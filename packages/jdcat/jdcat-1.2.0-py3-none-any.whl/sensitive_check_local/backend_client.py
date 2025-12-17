"""
Backend API client for permission testing.
Handles HTTP communication with the Java backend service.
"""
from __future__ import annotations

import os
import json
import asyncio
from typing import Any, Dict, List, Optional
import httpx
import inspect

# httpx 异常别名兼容处理（不同版本可能不存在 NetworkError/TimeoutException）
# - HTTPXTimeout: 优先使用 TimeoutException，其次 ReadTimeout；最终回退到 Exception
# - HTTPXNetworkError: 优先使用 NetworkError，其次 TransportError；最终回退到 Exception
HTTPXTimeout = getattr(httpx, "TimeoutException", getattr(httpx, "ReadTimeout", Exception))
HTTPXNetworkError = getattr(httpx, "NetworkError", getattr(httpx, "TransportError", Exception))


class BackendAPIError(Exception):
    """Backend API communication error"""
    def __init__(self, message: str, status_code: Optional[int] = None, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


class BackendAPI:
    """
    HTTP 客户端封装，统一向后端 Java 发起请求并注入必要头与参数
    
    统一注入 Headers：Project-Id、User-Id、X-Client-Id；Content-Type: application/json
    采用指数退避重试策略：对网络错误/超时/5xx 进行重试；4xx 不重试直接上抛
    """
    
    def __init__(self, project_id: str, user_id: str, client_id: str, base_url: Optional[str] = None, timeout_sec: float = 10.0):
        self.project_id = project_id
        self.user_id = user_id
        self.client_id = client_id
        self.base_url = base_url or os.getenv("BACKEND_BASE_URL", "http://aqapi.jdtest.local:8008")
        self.timeout_sec = timeout_sec
        self.session: Optional[httpx.AsyncClient] = None
        # 头部双写兼容开关：默认启用；当 HEADER_DUAL_WRITE 为 "false" 时禁用
        # 设计意图：标准名优先(Project-Id/User-Id) + 可选双写兼容(Project-ID/User-ID)，与后端拦截器一致
        # 默认关闭双写，避免部分服务/代理将同义头合并为逗号分隔字符串
        self.header_dual_write = (os.getenv("HEADER_DUAL_WRITE", "false").lower() != "false")
        
    async def _get_session(self) -> httpx.AsyncClient:
        if self.session is None:
            self.session = httpx.AsyncClient(timeout=self.timeout_sec)
        return self.session
        
    async def close(self) -> None:
        if self.session:
            await self.session.aclose()
            self.session = None
    
    async def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        initial_delay: float = 0.5,
        backoff_factor: float = 2.0,
        max_delay: float = 2.0
    ) -> Dict[str, Any]:
        """
        发起 HTTP 请求，带指数退避重试策略
        对网络错误/超时/5xx 进行重试；4xx 不重试直接上抛
        默认重试 3 次（总尝试 4 次），退避间隔 0.5s/1s/2s
        """
        import logging
        logger = logging.getLogger("sensitive_check_local")
        
        url = f"{self.base_url.rstrip('/')}{path}"
        # 标准头优先 + 兼容双写：始终注入 Project-Id/User-Id；当启用双写时同时注入 Project-ID/User-ID
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Project-Id": self.project_id,
            "User-Id": self.user_id,
            "X-Client-Id": self.client_id,
            "X-SS-Internal": "sensitive-check-local",
        }
        if self.header_dual_write:
            headers["Project-ID"] = self.project_id
            headers["User-ID"] = self.user_id
        
        # 安全的请求体预览
        body_preview = "None"
        if json_body:
            try:
                import json
                body_str = json.dumps(json_body, ensure_ascii=False)
                body_preview = body_str[:200] + "..." if len(body_str) > 200 else body_str
            except Exception:
                body_preview = str(json_body)[:200]
        
        logger.info(f"[HTTP-REQUEST] 🌐 发起请求:")
        logger.info(f"[HTTP-REQUEST]   - Method: {method.upper()}")
        logger.info(f"[HTTP-REQUEST]   - URL: {url}")
        # 避免泄露敏感值：仅提示已注入标准头，并标注双写兼容状态
        logger.info(f"[HTTP-REQUEST]   - Headers: 标准头已注入(Project-Id/User-Id)，双写兼容={'启用' if self.header_dual_write else '禁用'}")
        # 临时调试：显示实际的头部值
        logger.info(f"[HTTP-REQUEST]   - Debug Headers: Project-Id={repr(self.project_id)}, User-Id={repr(self.user_id)}")
        logger.info(f"[HTTP-REQUEST]   - Body: {body_preview}")
        
        session = await self._get_session()
        delay = initial_delay
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"[HTTP-REQUEST] 尝试 {attempt + 1}/{max_retries + 1}...")
                
                if method.upper() == "GET":
                    response = await session.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = await session.post(url, headers=headers, json=json_body)
                else:
                    raise BackendAPIError(f"Unsupported HTTP method: {method}")
                
                logger.info(f"[HTTP-RESPONSE] 收到响应: status={response.status_code}")

                # 显式处理 3xx（重定向到 SSO 等）：直接提示需要加白名单或认证
                if 300 <= response.status_code < 400:
                    loc = response.headers.get("Location", "")
                    hdr_keys = list(response.headers.keys())
                    resp_text = None
                    try:
                        resp_text = response.text
                        if resp_text and len(resp_text) > 500:
                            resp_text = resp_text[:500] + "..."
                    except Exception:
                        resp_text = None
                    msg = f"HTTP {response.status_code} redirect to {loc or 'unknown'} (可能需要SSO登录或本地服务加白名单)"
                    src = None
                    try:
                        frame = inspect.stack()[1]
                        src = f"{frame.function}({frame.filename.split('/')[-1]})"
                    except Exception:
                        src = None
                    logger.error("[HTTP-RESPONSE] ❌ 重定向 | method=%s | url=%s | status=%s | location=%s | headers=%s | body.preview=%s | pid=%s | uid=%s | source=%s",
                                 method.upper(), url, response.status_code, loc, hdr_keys, resp_text, self.project_id, self.user_id, src)
                    raise BackendAPIError(msg, response.status_code, {"location": loc, "headers": hdr_keys})
                
                # 4xx 错误不重试，直接抛出
                if 400 <= response.status_code < 500:
                    error_data: Dict[str, Any] = {}
                    hdr_keys = list(response.headers.keys())
                    body_preview = None
                    try:
                        error_data = response.json()
                        message = error_data.get("message", f"HTTP {response.status_code}")
                        try:
                            import json as _json
                            body_str = _json.dumps(error_data, ensure_ascii=False)
                            body_preview = body_str[:500] + "..." if len(body_str) > 500 else body_str
                        except Exception:
                            body_preview = str(error_data)[:500]
                        src = None
                        try:
                            frame = inspect.stack()[1]
                            src = f"{frame.function}({frame.filename.split('/')[-1]})"
                        except Exception:
                            src = None
                        logger.error("[HTTP-RESPONSE] ❌ 客户端错误 | method=%s | url=%s | status=%s | headers=%s | body.preview=%s | pid=%s | uid=%s | source=%s",
                                     method.upper(), url, response.status_code, hdr_keys, body_preview, self.project_id, self.user_id, src)
                    except Exception:
                        try:
                            body_preview = response.text
                            if body_preview and len(body_preview) > 500:
                                body_preview = body_preview[:500] + "..."
                        except Exception:
                            body_preview = None
                        message = f"HTTP {response.status_code}"
                        src = None
                        try:
                            frame = inspect.stack()[1]
                            src = f"{frame.function}({frame.filename.split('/')[-1]})"
                        except Exception:
                            src = None
                        logger.error("[HTTP-RESPONSE] ❌ 客户端错误 | method=%s | url=%s | status=%s | headers=%s | body.preview=%s | pid=%s | uid=%s | source=%s",
                                     method.upper(), url, response.status_code, hdr_keys, body_preview, self.project_id, self.user_id, src)
                    raise BackendAPIError(message, response.status_code, error_data or {})
                
                # 5xx 错误进行重试
                if response.status_code >= 500:
                    logger.warning(f"[HTTP-RESPONSE] ⚠️ 服务器错误: {response.status_code}, 将重试...")
                    if attempt < max_retries:
                        logger.info(f"[HTTP-REQUEST] 等待 {delay}s 后重试...")
                        await asyncio.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                        continue
                    else:
                        logger.error(f"[HTTP-RESPONSE] ❌ 重试次数耗尽: HTTP {response.status_code}")
                        raise BackendAPIError(f"HTTP {response.status_code} after {max_retries} retries", response.status_code)
                
                # 成功响应
                response.raise_for_status()
                try:
                    response_data = response.json()
                except Exception:
                    logger.error("[HTTP-RESPONSE] ❌ 非JSON响应（可能为登录页面或重定向后内容）")
                    raise BackendAPIError("Non-JSON response (auth required or whitelist needed)", response.status_code)
                
                # 安全的响应预览
                try:
                    import json
                    resp_str = json.dumps(response_data, ensure_ascii=False)
                    resp_preview = resp_str[:300] + "..." if len(resp_str) > 300 else resp_str
                except Exception:
                    resp_preview = str(response_data)[:300]
                
                logger.info(f"[HTTP-RESPONSE] ✅ 请求成功: {resp_preview}")
                return response_data
                
            except HTTPXTimeout:
                logger.warning(f"[HTTP-REQUEST] ⏰ 请求超时 (尝试 {attempt + 1})")
                if attempt < max_retries:
                    logger.info(f"[HTTP-REQUEST] 等待 {delay}s 后重试...")
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                    continue
                else:
                    logger.error(f"[HTTP-REQUEST] ❌ 超时重试次数耗尽")
                    raise BackendAPIError(f"Request timeout after {max_retries} retries")
                    
            except HTTPXNetworkError as e:
                logger.warning(f"[HTTP-REQUEST] 🌐 网络错误: {e} (尝试 {attempt + 1})")
                if attempt < max_retries:
                    logger.info(f"[HTTP-REQUEST] 等待 {delay}s 后重试...")
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                    continue
                else:
                    logger.error(f"[HTTP-REQUEST] ❌ 网络错误重试次数耗尽: {e}")
                    raise BackendAPIError(f"Network error after {max_retries} retries: {e}")
                    
            except BackendAPIError:
                # 重新抛出我们自己的异常
                raise
                
            except Exception as e:
                src = None
                try:
                    frame = inspect.stack()[1]
                    src = f"{frame.function}({frame.filename.split('/')[-1]})"
                except Exception:
                    src = None
                logger.error(f"[HTTP-REQUEST] ❌ 未知错误: {e} | method={method.upper()} | url={url} | pid={self.project_id} | uid={self.user_id} | source={src}", exc_info=True)
                raise BackendAPIError(f"Unexpected error: {e}")
    
    # 原子认领：POST /api/permission/tasks/claim
    async def claim(self, task_id: str, client_id: Optional[str] = None) -> Dict[str, Any]:
        if not task_id:
            raise BackendAPIError("missing task_id for claim")
        payload = {
            "task_id": task_id,
            "client_id": client_id or self.client_id
        }
        return await self._request("POST", "/api/permission/tasks/claim", json_body=payload)
    
    # 详情拉取：GET /api/permission/tasks/detail
    async def detail(self, task_id: str) -> Dict[str, Any]:
        if not task_id:
            raise BackendAPIError("missing task_id for detail")
        return await self._request("GET", f"/api/permission/tasks/detail?taskId={task_id}")
    
    # 进度上报：POST /api/permission/tasks/progress
    async def progress(self, task_id: str, current: int, total: int, message: str) -> Dict[str, Any]:
        if not task_id:
            raise BackendAPIError("missing task_id for progress")
        payload = {
            "task_id": task_id,
            "current": int(current),
            "total": int(total),
            "message": str(message)
        }
        return await self._request("POST", "/api/permission/tasks/progress", json_body=payload)
    
    # 结果上报：POST /api/permission/tasks/results
    async def results(self, task_id: str, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not task_id:
            raise BackendAPIError("missing task_id for results")
        if not isinstance(test_results, list):
            raise BackendAPIError("test_results must be a list")
        payload = {"task_id": task_id, "test_results": test_results}
        return await self._request("POST", "/api/permission/tasks/results", json_body=payload)

    # 完成状态：POST /api/permission/tasks/complete
    async def complete(self, task_id: str, success: bool) -> Dict[str, Any]:
        if not task_id:
            raise BackendAPIError("missing task_id for complete")
        payload = {"task_id": task_id, "success": bool(success)}
        return await self._request("POST", "/api/permission/tasks/complete", json_body=payload)

    async def realtime_batch_ingest(
        self,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
        max_retries: int = 3,
        initial_delay: float = 0.5,
        backoff_factor: float = 2.0,
        max_delay: float = 2.0
    ) -> Dict[str, Any]:
        """
        统一退避口径：本模块实现指数退避重试；调用方无需叠加本地层重试
        批量上报实时检测结果到后端:
          - URL: /api/realtime/results/batchIngest
          - Headers 注入: Project-Id, User-Id, Task-Id(可选), Content-Type: application/json
          - 退避与重试：对网络错误/超时/5xx 使用指数退避，最多3次；4xx 不重试直接上抛（实际参数以当前实现为准）
          - 关键参数（与实现保持一致）：max_retries=3, backoff_factor=2.0, initial_delay=0.5, max_delay=2.0
          - 日志：请求体预览最多200字符；响应体预览最多300字符，统一进行截断以避免过长日志
        返回：
          - 返回后端 JSON；日志仅输出截断预览
        """
        import logging
        logger = logging.getLogger("sensitive_check_local")

        url = f"{self.base_url.rstrip('/')}/api/realtime/results/batchIngest"
        # 统一使用标准头部格式：Project-Id, User-Id, Task-Id + API Key
        headers = {
            "Content-Type": "application/json",
            "Project-Id": str(self.project_id),
            "User-Id": str(self.user_id),
            "X-INGEST-KEY": "dev-ingest-key",  # API Key验证
        }
        if task_id:
            headers["Task-Id"] = str(task_id)

        # 安全请求体预览
        body_str: str = ""
        try:
            body_str = json.dumps(payload, ensure_ascii=False)
            body_preview = body_str[:200] + "..." if len(body_str) > 200 else body_str
        except Exception:
            body_str = "<unserializable>"
            body_preview = "unserializable"

        logger.info("[HTTP-REQUEST] 🌐 realtime batchIngest")
        logger.info(f"[HTTP-REQUEST]   - URL: {url}")
        # 避免泄露敏感值：仅提示已注入标准头；Task-Id 仅提示存在与否
        logger.info(f"[HTTP-REQUEST]   - Headers: 标准头已注入(Project-Id/User-Id)")
        logger.info(f"[HTTP-REQUEST]   - Task-Id: {'存在' if task_id else '-'}")
        logger.info(f"[HTTP-REQUEST]   - Body: {body_preview}")

        # 实时-越权：上报请求完整信息（headers、url、params、requestBody）
        try:
            logger.info("实时-越权 | 上报请求完整信息 | url=%s", url)
            logger.info("实时-越权 | 上报请求完整信息 | headers=%s", headers)
            logger.info("实时-越权 | 上报请求完整信息 | params=%s", {})
            logger.info("实时-越权 | 上报请求完整信息 | requestBody=%s", body_str)
        except Exception:
            pass

        session = await self._get_session()
        delay = initial_delay

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"[HTTP-REQUEST] 尝试 {attempt + 1}/{max_retries + 1}...")
                resp = await session.post(url, headers=headers, json=payload)
                logger.info(f"[HTTP-RESPONSE] status={resp.status_code}")

                # 4xx 直接失败
                if 400 <= resp.status_code < 500:
                    try:
                        error_data = resp.json()
                        message = error_data.get("message", f"HTTP {resp.status_code}")
                    except Exception:
                        error_data = {}
                        message = f"HTTP {resp.status_code}: {resp.text}"
                    logger.error(f"[HTTP-RESPONSE] ❌ 客户端错误: {message}")
                    # 实时-越权：上报返回结果（4xx）
                    try:
                        logger.info("实时-越权 | 上报返回结果 | status=%s body=%s", resp.status_code, error_data or resp.text)
                    except Exception:
                        pass
                    raise BackendAPIError(message, resp.status_code, error_data)

                # 5xx 重试
                if resp.status_code >= 500:
                    if attempt < max_retries:
                        logger.warning(f"[HTTP-RESPONSE] 服务器错误 {resp.status_code}，{delay}s 后重试")
                        await asyncio.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                        continue
                    logger.error(f"[HTTP-RESPONSE] ❌ 重试用尽: HTTP {resp.status_code}")
                    raise BackendAPIError(f"HTTP {resp.status_code} after {max_retries} retries", resp.status_code)

                # 成功
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception:
                    data = {"accepted": True}
                try:
                    resp_preview = json.dumps(data, ensure_ascii=False)
                    resp_preview = resp_preview[:300] + "..." if len(resp_preview) > 300 else resp_preview
                except Exception:
                    resp_preview = "unserializable"
                logger.info(f"[HTTP-RESPONSE] ✅ 成功: {resp_preview}")
                # 实时-越权：上报返回结果（200）
                try:
                    logger.info("实时-越权 | 上报返回结果 | status=%s body=%s", resp.status_code, data)
                except Exception:
                    pass
                return data

            except HTTPXTimeout:
                if attempt < max_retries:
                    logger.warning(f"[HTTP-REQUEST] ⏰ 超时，{delay}s 后重试")
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                    continue
                logger.error("[HTTP-REQUEST] ❌ 超时重试用尽")
                raise BackendAPIError(f"Request timeout after {max_retries} retries")

            except HTTPXNetworkError as e:
                if attempt < max_retries:
                    logger.warning(f"[HTTP-REQUEST] 🌐 网络错误: {e}，{delay}s 后重试")
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                    continue
                logger.error(f"[HTTP-REQUEST] ❌ 网络重试用尽: {e}")
                raise BackendAPIError(f"Network error after {max_retries} retries: {e}")

            except BackendAPIError:
                raise

            except Exception as e:
                logger.error(f"[HTTP-REQUEST] ❌ 未知错误: {e}", exc_info=False)
        raise BackendAPIError(f"Unexpected error: {e}")


def build_backend_api_from_context(ctx: Dict[str, Any]) -> BackendAPI:
    """
    从本地上下文构建 BackendAPI 客户端（兼容多种字段命名格式）
    ctx 结构：{project_id, user_id, task_id, client_id, ...} 或 {projectId, userId, taskId, clientId, ...}
    """
    if not isinstance(ctx, dict):
        raise BackendAPIError("invalid context")
    
    # 兼容多种字段命名格式：优先使用下划线格式，然后尝试驼峰格式
    # 特别处理 project_id，可能存储为字符串形式的数字
    project_id_raw = ctx.get("project_id") or ctx.get("projectId")
    def _digits_only(val: str) -> str:
        import re
        m = re.findall(r"\d+", str(val))
        return m[0] if m else str(val)

    if project_id_raw is not None:
        project_id = _digits_only(str(project_id_raw).strip().strip("'\""))
    else:
        project_id = ""
    
    user_id_raw = ctx.get("user_id") or ctx.get("userId")
    if user_id_raw is not None:
        user_id_before = str(user_id_raw).strip()
        user_id = user_id_before.strip("'\"")
        user_id = user_id.replace(",", "")
    else:
        user_id = ""
    
    client_id_raw = ctx.get("client_id") or ctx.get("clientId")
    if client_id_raw is not None:
        client_id = str(client_id_raw).strip().strip("'\"")  # 去除可能的引号
    else:
        client_id = ""
    
    # 修复：project_id 可能为 0（个人空间），不能使用 not project_id 判断
    # 应该检查是否为 None 或空字符串
    project_id_missing = project_id_raw is None or str(project_id).strip() == ""
    user_id_missing = user_id_raw is None or str(user_id).strip() == "" or str(user_id).strip() == "0"
    client_id_missing = client_id_raw is None or str(client_id).strip() == ""
    
    if project_id_missing or user_id_missing or client_id_missing:
        # 提供更详细的错误信息，帮助调试
        missing_fields = []
        debug_info = {}
        
        if project_id_missing:
            missing_fields.append("project_id/projectId")
            debug_info["project_id_raw"] = repr(ctx.get("project_id"))
            debug_info["projectId_raw"] = repr(ctx.get("projectId"))
            debug_info["project_id_processed"] = repr(project_id)
        if user_id_missing:
            missing_fields.append("user_id/userId")
            debug_info["user_id_raw"] = repr(ctx.get("user_id"))
            debug_info["userId_raw"] = repr(ctx.get("userId"))
            debug_info["user_id_processed"] = repr(user_id)
        if client_id_missing:
            missing_fields.append("client_id/clientId")
            debug_info["client_id_raw"] = repr(ctx.get("client_id"))
            debug_info["clientId_raw"] = repr(ctx.get("clientId"))
            debug_info["client_id_processed"] = repr(client_id)
        
        import logging
        logger = logging.getLogger("sensitive_check_local")
        logger.error(f"Context field debug info: {debug_info}")
        
        # 尝试从环境变量回退 user_id
        if user_id_missing:
            import os
            env_uid = os.getenv("USER_ID")
            if env_uid and env_uid.strip() not in ("", "0"):
                user_id = env_uid.strip()
                user_id_missing = False
        if project_id_missing or user_id_missing or client_id_missing:
            raise BackendAPIError(f"context missing fields: {'/'.join(missing_fields)}")
    
    # 统一确保头部使用纯字符串数字/标识
    try:
        project_id = str(int(project_id))
    except Exception:
        project_id = str(project_id)
    user_id = str(user_id)

    return BackendAPI(project_id=project_id, user_id=user_id, client_id=client_id)


async def param_test_create(api: BackendAPI, body: Dict[str, Any]) -> Dict[str, Any]:
    return await api._request("POST", "/api/param-test/tasks/create", json_body=body)

async def param_test_list(api: BackendAPI, query: Dict[str, Any]) -> Dict[str, Any]:
    from urllib.parse import quote_plus
    qs = []
    for k, v in (query or {}).items():
        if v is None:
            continue
        qs.append(f"{k}={quote_plus(str(v))}")
    path = "/api/param-test/tasks/list" + ("?" + "&".join(qs) if qs else "")
    return await api._request("GET", path)

async def param_test_complete(api: BackendAPI, task_id: int) -> Dict[str, Any]:
    return await api._request("POST", f"/api/param-test/tasks/{task_id}/complete")

async def param_test_fail(api: BackendAPI, task_id: int, reason: str) -> Dict[str, Any]:
    payload = {"reason": str(reason)}
    return await api._request("POST", f"/api/param-test/tasks/{task_id}/fail", json_body=payload)

async def param_test_details_batch(api: BackendAPI, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    return await api._request("POST", "/api/param-test/details/batch", json_body=items)

async def param_test_details_raw(api: BackendAPI, task_id: int, response_all: str) -> Dict[str, Any]:
    payload = {"taskId": int(task_id), "responseAll": str(response_all or "")}
    return await api._request("POST", "/api/param-test/details/raw", json_body=payload)

async def param_test_result_check_by_interface_id(api: BackendAPI, interface_id: int) -> Dict[str, Any]:
    from urllib.parse import quote_plus
    qs = f"interfaceId={quote_plus(str(interface_id))}"
    return await api._request("GET", f"/api/param-test/results/check?{qs}")

async def param_test_result_list(api: BackendAPI, rt_task_id: int, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    from urllib.parse import quote_plus
    qs = f"rtTaskId={quote_plus(str(rt_task_id))}&page={quote_plus(str(page))}&pageSize={quote_plus(str(page_size))}"
    return await api._request("GET", f"/api/param-test/results/list?{qs}")

async def param_test_result_ingest(api: BackendAPI, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    return await api._request("POST", "/api/param-test/results/ingest", json_body=items)

async def param_test_result_update_passed(api: BackendAPI, rid: int, passed: bool) -> Dict[str, Any]:
    from urllib.parse import quote_plus
    qs = f"id={quote_plus(str(rid))}&passed={quote_plus('1' if passed else '0')}"
    return await api._request("POST", f"/api/param-test/results/updatePassed?{qs}")

async def param_test_result_detail(api: BackendAPI, rid: int) -> Dict[str, Any]:
    return await api._request("GET", f"/api/param-test/results/{rid}")

async def param_test_tasks_latest(api: BackendAPI, domain: str, path: str) -> Dict[str, Any]:
    from urllib.parse import quote_plus
    qs = f"domain={quote_plus(str(domain))}&path={quote_plus(str(path))}"
    return await api._request("GET", f"/api/param-test/tasks/latest?{qs}")

async def param_test_details_list(api: BackendAPI, task_id: int) -> Dict[str, Any]:
    from urllib.parse import quote_plus
    qs = f"taskId={quote_plus(str(task_id))}"
    return await api._request("GET", f"/api/param-test/details?{qs}")

async def realtime_ignore_detail(api: BackendAPI, domain: str, path: str, method: str) -> Dict[str, Any]:
    from urllib.parse import quote_plus
    qs = f"domain={quote_plus(str(domain))}&path={quote_plus(str(path))}&method={quote_plus(str(method))}"
    return await api._request("GET", f"/api/realtime/ignore/detail?{qs}")

async def project_domain_by_host(api: BackendAPI, project_id: int, domain: str) -> Dict[str, Any]:
    payload = {"domain": str(domain)}
    return await api._request("POST", f"/api/projects/{project_id}/domains/byDomain", json_body=payload)

async def project_domains_list(api: BackendAPI, project_id: int, domain: str) -> Dict[str, Any]:
    from urllib.parse import quote_plus
    qs = f"pageNum=1&pageSize=200&domain={quote_plus(str(domain))}"
    return await api._request("GET", f"/api/projects/{project_id}/domains?{qs}")
