from __future__ import annotations

"""
本地身份注入器（对齐老工具核心行为的精简实现）
- 头部替换：将目标身份 headers 覆盖到原请求；保留 Host；移除 Content-Length
- Cookie 注入：优先使用目标身份 cookies 生成 Cookie 头；若已存在 Cookie 头则覆盖
- URL 参数替换：替换常见 userId/uid/account_id/member_id 等 query 参数
- 请求体修改：JSON/Form/Text 的最小化替换（仅在 JSON/Form 时进行键替换）
- 路径替换（可选）：如果原记录提供 source_user_id，尝试替换 URL 路径中纯数字的用户ID段
注意：尽量保持保守与可回滚，避免误替换导致请求不可用
"""

import json
import re
import urllib.parse
from typing import Any, Dict, Tuple, Optional


COMMON_USER_KEYS = [
    "user_id", "userid", "userId", "uid", "account_id", "accountId", "member_id", "memberId", "owner_id", "ownerId"
]


def _to_dict_maybe(data: Any) -> Dict[str, Any]:
    """
    尝试将 data 转为 dict（增强版本，对齐老工具逻辑）：
    - 若 data 是 dict，直接返回其拷贝
    - 若 data 是 JSON 字符串，尝试 json.loads
    - 若 data 是空字符串或None，返回 {}
    - 其他情况返回 {}
    """
    if isinstance(data, dict):
        return dict(data)
    if data is None:
        return {}
    if isinstance(data, str):
        s = data.strip()
        if not s or s == "null" or s == "None":
            return {}
        try:
            # 尝试解析JSON，支持更宽松的格式
            obj = json.loads(s)
            if isinstance(obj, dict):
                return dict(obj)
            elif obj is None:
                return {}
        except (json.JSONDecodeError, ValueError) as e:
            # 如果JSON解析失败，尝试eval（仅对安全的dict格式）
            if s.startswith('{') and s.endswith('}'):
                try:
                    # 仅对明显是字典格式的字符串尝试eval
                    import ast
                    obj = ast.literal_eval(s)
                    if isinstance(obj, dict):
                        return dict(obj)
                except (ValueError, SyntaxError):
                    pass
            # 记录解析失败的详细信息
            import logging
            logger = logging.getLogger("sensitive_check_local")
            logger.warning(f"[JSON-PARSE] JSON解析失败: {e}, 原始数据: {s[:100]}...")
            return {}
    return {}


def _normalize_headers(orig_headers: Dict[str, Any], identity_headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    头部归一化（对齐老工具逻辑）：
    - 完全使用身份的headers替换原请求headers（不是覆盖，是替换）
    - 保留 Host（若原请求包含且身份headers中没有）
    - 移除 Content-Length
    - 处理headers中的中文字符编码问题
    """
    import logging
    logger = logging.getLogger("sensitive_check_local")
    
    # 对齐老工具：完全使用身份headers，而不是在原headers基础上覆盖
    out: Dict[str, Any] = {}
    
    # 完全使用身份的headers（对齐老工具第104行逻辑）
    if identity_headers:
        # 处理headers中的编码问题（对齐老工具逻辑）
        for k, v in identity_headers.items():
            key_str = str(k) if k is not None else ""
            if not key_str:
                continue
            
            value_str = str(v) if v is not None else ""
            
            # 处理headers中的中文字符编码问题
            # HTTP headers必须是ASCII字符，包含中文的header需要特殊处理
            try:
                # 检查key是否包含非ASCII字符
                key_str.encode('ascii')
                processed_key = key_str
            except UnicodeEncodeError:
                # key包含中文字符，记录警告并跳过
                logger.warning(f"跳过包含中文字符的Header key: {key_str}")
                continue
            
            try:
                # 检查value是否包含非ASCII字符
                value_str.encode('ascii')
                processed_value = value_str
            except UnicodeEncodeError:
                # value包含中文字符，需要特殊处理
                if key_str.lower() in ['cookie', 'set-cookie']:
                    # Cookie header需要URL编码处理
                    from urllib.parse import quote
                    processed_value = quote(value_str, safe='=;, ')
                    logger.debug(f"Header {key_str} 包含中文字符，已进行URL编码")
                else:
                    # 其他headers包含中文字符时，记录警告并跳过
                    logger.warning(f"跳过包含中文字符的Header: {key_str}")
                    continue
            
            out[processed_key] = processed_value
        
        logger.info(f"[IDENTITY-REPLACE] 完全使用身份headers，共 {len(out)} 个header")
    
    # 保留 Host：如果原始请求包含 Host 且身份headers中没有Host，则使用原值（避免跨域失败）
    orig_host = None
    for k, v in (orig_headers or {}).items():
        if str(k).lower() == "host":
            orig_host = v
            break
    
    # 检查身份headers中是否已有Host
    has_identity_host = any(str(k).lower() == "host" for k in out.keys())
    
    if orig_host is not None and not has_identity_host:
        out["Host"] = orig_host
        logger.info(f"[IDENTITY-REPLACE] 保留原始Host: {orig_host}")
    elif has_identity_host:
        host_value = None
        for k, v in out.items():
            if str(k).lower() == "host":
                host_value = v
                break
        logger.info(f"[IDENTITY-REPLACE] 使用身份Host: {host_value}")

    # 移除 Content-Length（由 http 客户端自动计算）
    keys_to_remove = []
    for k in out.keys():
        if str(k).lower() == "content-length":
            keys_to_remove.append(k)
    for k in keys_to_remove:
        out.pop(k, None)
    
    logger.info(f"[IDENTITY-REPLACE] 最终headers数量: {len(out)}, keys: {list(out.keys())}")
    return out


def _build_cookie_header(identity_cookies: Dict[str, Any]) -> Optional[str]:
    """
    将 cookies dict 转为 Cookie header 字符串；若为空返回 None
    对齐老工具逻辑，正确处理Cookie值的编码
    """
    if not identity_cookies:
        return None
    parts = []
    for k, v in identity_cookies.items():
        k_s = str(k).strip()
        if not k_s:
            continue
        # 确保Cookie值正确编码，处理中文字符
        v_s = str(v) if v is not None else ""
        # Cookie值中的特殊字符处理（对齐老工具逻辑）
        try:
            # 检查是否包含非ASCII字符
            v_s.encode('ascii')
            cookie_value = v_s
        except UnicodeEncodeError:
            # 包含中文字符，进行URL编码
            from urllib.parse import quote
            cookie_value = quote(v_s, safe='')
        parts.append(f"{k_s}={cookie_value}")
    return "; ".join(parts) if parts else None


def _replace_query_params(url: str, target_user_value: Optional[str], custom_params: Dict[str, Any]) -> str:
    """
    替换 URL query 中的常见 userId/uid/account_id/member_id 等键
    - 优先使用 target_user_value（来自 identity.identity_user_id）
    - 其次根据 custom_params 中的同名键进行替换
    """
    try:
        parsed = urllib.parse.urlsplit(url)
        qsl = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        new_q = []
        for k, v in qsl:
            new_v = v
            lk = k if not isinstance(k, str) else k
            if target_user_value and any(lk == key for key in COMMON_USER_KEYS):
                new_v = str(target_user_value)
            elif custom_params:
                for ck, cv in custom_params.items():
                    if str(ck) == k:
                        new_v = str(cv)
                        break
            new_q.append((k, new_v))
        new_query = urllib.parse.urlencode(new_q, doseq=True)
        rebuilt = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))
        return rebuilt
    except Exception:
        return url


def _replace_path_user_segment(url: str, source_user_id: Optional[str], target_user_value: Optional[str]) -> str:
    """
    尝试在 URL 路径中替换用户ID段（仅在有明确 source_user_id 且 target_user_value 时进行）
    规则（保守）：
    - 若 path 中存在 '/{source_user_id}(/|$)'，替换为 target_user_value
    - 不做广泛的数字段替换，避免误伤
    """
    if not source_user_id or not target_user_value:
        return url
    try:
        parsed = urllib.parse.urlsplit(url)
        pattern = re.compile(rf"(?<=\/){re.escape(str(source_user_id))}(?=\/|$)")
        new_path = pattern.sub(str(target_user_value), parsed.path)
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, new_path, parsed.query, parsed.fragment))
    except Exception:
        return url


def _modify_json_like(obj: Any, target_user_value: Optional[str], custom_params: Dict[str, Any]) -> Any:
    """
    在 JSON 对象内进行键替换：
    - 对 COMMON_USER_KEYS 替换为 target_user_value（若提供）
    - 对 custom_params 中的键进行覆盖
    """
    try:
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                new_v = v
                if target_user_value and any(str(k) == key for key in COMMON_USER_KEYS):
                    new_v = target_user_value
                elif custom_params and str(k) in custom_params:
                    new_v = custom_params[str(k)]
                else:
                    new_v = _modify_json_like(v, target_user_value, custom_params)
                out[k] = new_v
            return out
        elif isinstance(obj, list):
            return [_modify_json_like(x, target_user_value, custom_params) for x in obj]
        else:
            return obj
    except Exception:
        return obj


def _coerce_json(body: Any) -> Tuple[Optional[dict], Optional[str]]:
    """
    将 body 解读为 JSON（若可能）
    返回：(json_obj, raw_text)
    """
    if body is None:
        return None, None
    if isinstance(body, (dict, list)):
        return body, None
    if isinstance(body, (bytes, bytearray)):
        try:
            s = body.decode("utf-8", errors="ignore")
            return json.loads(s), s
        except Exception:
            return None, body.decode("utf-8", errors="ignore")
    if isinstance(body, str):
        s = body
        try:
            return json.loads(s), s
        except Exception:
            return None, s
    # 其他类型转字符串
    try:
        s = str(body)
    except Exception:
        s = ""
    try:
        return json.loads(s), s
    except Exception:
        return None, s


def modify_request_with_identity(original_request: Dict[str, Any], identity: Dict[str, Any], source_user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    入口：根据目标身份 identity 修改原始请求 original_request
    输入：
      - original_request: { method, url, headers, request_body, query? }
      - identity: { identity_user_id, role, headers, cookies, tokens, custom_params }
    输出：
      - { method, url, headers, body, cookies? }
    """
    method = str(original_request.get("method") or "GET").upper()
    url = str(original_request.get("url") or "")
    headers = _to_dict_maybe(original_request.get("headers"))
    body = original_request.get("request_body")

    # 解析身份结构（兼容 JSON 文本/对象）- 对齐老工具逻辑，完全使用身份的headers替换原请求
    import logging
    logger = logging.getLogger("sensitive_check_local")
    logger.info(f"[IDENTITY-REPLACE] ========== 开始身份替换 ==========")
    logger.info(f"[IDENTITY-REPLACE] 目标身份: {identity.get('identity_user_id')} (角色: {identity.get('role')})")
    logger.info(f"[IDENTITY-REPLACE] 原始身份数据keys: {list(identity.keys())}")
    
    # 详细输出原始身份数据内容 - 支持多种字段名格式
    # 优先使用 JSON 字段（来自数据库），其次使用普通字段
    headers_raw = (identity.get("headers_json") or identity.get("headersJson") or
                  identity.get("headers") or {})
    cookies_raw = (identity.get("cookies_json") or identity.get("cookiesJson") or
                  identity.get("cookies") or {})
    tokens_raw = (identity.get("tokens_json") or identity.get("tokensJson") or
                 identity.get("tokens") or {})
    custom_raw = (identity.get("custom_params_json") or identity.get("customParamsJson") or
                 identity.get("custom_params") or identity.get("customParams") or {})
    
    logger.info(f"[IDENTITY-REPLACE] 原始headers数据: {headers_raw}")
    logger.info(f"[IDENTITY-REPLACE] 原始cookies数据: {cookies_raw}")
    logger.info(f"[IDENTITY-REPLACE] 原始tokens数据: {tokens_raw}")
    logger.info(f"[IDENTITY-REPLACE] 原始custom数据: {custom_raw}")
    
    # 解析身份数据（增强版本）
    id_headers = _to_dict_maybe(headers_raw)
    id_cookies = _to_dict_maybe(cookies_raw)
    id_tokens = _to_dict_maybe(tokens_raw)
    id_custom = _to_dict_maybe(custom_raw)
    
    logger.info(f"[IDENTITY-REPLACE] 解析后headers数量: {len(id_headers) if id_headers else 0}")
    logger.info(f"[IDENTITY-REPLACE] 解析后cookies数量: {len(id_cookies) if id_cookies else 0}")
    logger.info(f"[IDENTITY-REPLACE] 解析后tokens数量: {len(id_tokens) if id_tokens else 0}")
    
    if id_headers:
        logger.info(f"[IDENTITY-REPLACE] Headers keys: {list(id_headers.keys())}")
        # 输出关键认证headers的值（脱敏）
        for key in ['Cookie', 'Authorization', 'Referer', 'Origin']:
            if key in id_headers:
                value = str(id_headers[key])
                logger.info(f"[IDENTITY-REPLACE] {key}: {value[:50]}..." if len(value) > 50 else f"[IDENTITY-REPLACE] {key}: {value}")
    else:
        logger.warning(f"[IDENTITY-REPLACE] ⚠️ 身份 {identity.get('identity_user_id')} 没有headers数据！")

    # 目标用户ID
    identity_user_id = identity.get("identity_user_id") or identity.get("user_id") or identity.get("uid") or id_custom.get("userId") if id_custom else None
    identity_user_id = str(identity_user_id) if identity_user_id is not None else None
    source_user_id = str(source_user_id) if source_user_id is not None else None

    # 1) 头部注入 + Token处理（对齐老工具逻辑）
    # 处理Authorization头（如果身份中有token信息）
    if id_tokens:
        if 'jwt' in id_tokens:
            id_headers["Authorization"] = f"Bearer {id_tokens['jwt']}"
        elif 'basic' in id_tokens:
            id_headers["Authorization"] = f"Basic {id_tokens['basic']}"
        elif 'custom' in id_tokens:
            id_headers["Authorization"] = id_tokens['custom']
        
        # 处理其他令牌头
        for token_type, token_value in id_tokens.items():
            if token_type.startswith('custom_'):
                # 自定义令牌头
                header_name = token_type.replace('custom_', '').replace('_', '-').title()
                id_headers[header_name] = token_value
    
    # 将 tokens 中的典型授权头提升到 headers（若未在 headers 内提供）
    token_header_candidates = {
        "Authorization": None,
        "X-Auth-Token": None,
        "X-Token": None,
        "Access-Token": None,
    }
    for k in list(token_header_candidates.keys()):
        if id_tokens and k in id_tokens and k not in id_headers:
            id_headers[k] = id_tokens[k]

    mod_headers = _normalize_headers(headers, id_headers)

    # 2) Cookie 注入（对齐老工具逻辑：完全替换cookies并设置Cookie头）
    cookie_header = _build_cookie_header(id_cookies)
    if id_cookies:
        # 对齐老工具：同时设置Cookie头和cookies字典
        mod_headers["Cookie"] = cookie_header
        logger.info(f"[IDENTITY-REPLACE] 用户 {identity_user_id} 的cookie已替换，共 {len(id_cookies)} 个")
        logger.info(f"[IDENTITY-REPLACE] Cookie头: {cookie_header[:100]}..." if len(cookie_header) > 100 else f"[IDENTITY-REPLACE] Cookie头: {cookie_header}")
    else:
        # 如果身份没有Cookie，则清空Cookie头（对齐老工具逻辑）
        if "Cookie" in mod_headers:
            del mod_headers["Cookie"]
        logger.info(f"[IDENTITY-REPLACE] 用户 {identity_user_id} 没有cookie，已清空原始请求的cookie")

    # 3) URL 参数替换（query）
    mod_url = _replace_query_params(url, identity_user_id, id_custom)

    # 4) 路径替换（仅当提供了 source_user_id）
    mod_url = _replace_path_user_segment(mod_url, source_user_id, identity_user_id)

    # 5) Body 修改（JSON/Form 优先）
    json_obj, raw_text = _coerce_json(body)
    mod_body: Any
    if json_obj is not None:
        # JSON 场景：键替换
        mod_json = _modify_json_like(json_obj, identity_user_id, id_custom)
        mod_body = mod_json
        # 设置 Content-Type
        if not any(str(k).lower() == "content-type" for k in mod_headers.keys()):
            mod_headers["Content-Type"] = "application/json"
    else:
        # 非 JSON：保持原文（可选：基于 key=value 的 form 做简单替换）
        # 尝试解析为 application/x-www-form-urlencoded
        try:
            if isinstance(raw_text, str) and "=" in raw_text and "&" in raw_text:
                qsl = urllib.parse.parse_qsl(raw_text, keep_blank_values=True)
                new_pairs = []
                for k, v in qsl:
                    new_v = v
                    if identity_user_id and any(k == key for key in COMMON_USER_KEYS):
                        new_v = str(identity_user_id)
                    elif id_custom and k in id_custom:
                        new_v = str(id_custom[k])
                    new_pairs.append((k, new_v))
                mod_body = urllib.parse.urlencode(new_pairs)
                if not any(str(k).lower() == "content-type" for k in mod_headers.keys()):
                    mod_headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                mod_body = raw_text if raw_text is not None else body
        except Exception:
            mod_body = raw_text if raw_text is not None else body

    # 6) 内部标记头保证：在统一头替换完成后进行最终注入，避免被覆盖
    try:
        present_non_empty = False
        for k, v in list(mod_headers.items()):
            if str(k).lower().strip() == "x-ss-internal":
                if str(v).strip():
                    present_non_empty = True
                break
        if not present_non_empty:
            mod_headers["X-SS-Internal"] = "permission-test"
            logger.info("[IDENTITY-REPLACE] inject_internal_hdr_at_source=true")
        else:
            logger.info("[IDENTITY-REPLACE] inject_internal_hdr_at_source=false")
    except Exception:
        # 忽略注入失败，由发送侧兜底
        pass

    # 6) 返回结果 + 详细日志输出（对齐老工具格式，包含cookies）
    result = {
        "method": method,
        "url": mod_url,
        "headers": mod_headers,
        "request_body": mod_body,
        "cookies": id_cookies,  # 关键修复：返回cookies信息
    }
    
    # 详细日志：输出最终请求信息（对齐老工具调试逻辑）
    logger.info(f"[IDENTITY-REPLACE] ========== 身份替换完成 ==========")
    logger.info(f"[IDENTITY-REPLACE] 最终请求方法: {method}")
    logger.info(f"[IDENTITY-REPLACE] 最终请求URL: {mod_url}")
    logger.info(f"[IDENTITY-REPLACE] 最终headers数量: {len(mod_headers)}")
    logger.info(f"[IDENTITY-REPLACE] 最终headers keys: {list(mod_headers.keys())}")
    
    # 输出关键认证信息（对齐老工具调试逻辑）
    auth_headers = ['Authorization', 'Cookie', 'corp-id', 'customer-id', 'login-type', 'platform', 'project-id', 'wx-data-source']
    for header in auth_headers:
        if header in mod_headers:
            value = str(mod_headers[header])
            if header == 'Cookie':
                logger.info(f"[IDENTITY-REPLACE] 认证Header {header}: {value[:100]}..." if len(value) > 100 else f"[IDENTITY-REPLACE] 认证Header {header}: {value}")
            else:
                logger.info(f"[IDENTITY-REPLACE] 认证Header {header}: {value}")
    
    return result