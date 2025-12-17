from __future__ import annotations

"""
analysis_local
- 对齐老工具文档描述的响应细粒度比对器、权限检测器、Excel 风险等级映射
- 提供统一入口：
  • compare_responses(original_response, modified_response) -> dict
  • detect_privilege_escalation(original_identity_role, target_identity_role, original_user_id, target_user_id) -> dict
  • map_excel_risk_level(original_status, modified_status, similarity) -> str
  • build_evidence(original_response, modified_response, compare_dict, detector_dict) -> dict
"""

import re
import difflib
from typing import Any, Dict, Optional, Tuple


def _safe_text(x: Any, max_len: int = 4096) -> str:
    try:
        s = str(x) if x is not None else ""
    except Exception:
        s = ""
    return s[:max_len]


def _normalize_text(s: str) -> str:
    """
    标准化文本以进行内容相似度计算：
    - 去除空白差异（多空格/换行）
    - 小写化
    - 移除常见无意义 header 噪声（若传入的是字符串化后的响应）
    """
    if not isinstance(s, str):
        try:
            s = str(s)
        except Exception:
            s = ""
    s = s.strip().lower()
    # 简易去噪：去除多余空白
    s = re.sub(r"\s+", " ", s)
    return s


def compute_similarity(a: Any, b: Any) -> float:
    """
    内容相似度计算（简化对齐版）：
    - 使用 difflib.SequenceMatcher 计算两段标准化文本的相似度
    - 返回 [0.0, 1.0] 浮点
    """
    a_norm = _normalize_text(_safe_text(a))
    b_norm = _normalize_text(_safe_text(b))
    try:
        return float(difflib.SequenceMatcher(None, a_norm, b_norm).ratio())
    except Exception:
        return 0.0


def compare_responses(original_response: Dict[str, Any], modified_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    响应细粒度比对（对齐文档口径的简化实现）：
    指标：
      - status_diff: (orig_status, mod_status)
      - content_similarity: 0.0 ~ 1.0
      - granted_access: 原始非200、修改后200 → True
      - same_content: 双200且内容高度相似（≥0.9）
      - header_diff_hint: 仅提示性（若可用）
    """
    import logging
    logger = logging.getLogger(__name__)
    
    orig_status = int(original_response.get("status") or original_response.get("response_status") or 0)
    mod_status = int(modified_response.get("status") or 0)
    orig_body = original_response.get("text") or original_response.get("body") or original_response.get("response_body") or ""
    mod_body = modified_response.get("text") or modified_response.get("body") or ""

    similarity = compute_similarity(orig_body, mod_body)
    granted_access = (orig_status != 200 and mod_status == 200)
    same_content = (orig_status == 200 and mod_status == 200 and similarity >= 0.90)
    
    # 添加响应比较的详细日志
    logger.info(f"[RESPONSE_COMPARE] 响应比较开始:")
    logger.info(f"[RESPONSE_COMPARE] 状态码: {orig_status} -> {mod_status}")
    logger.info(f"[RESPONSE_COMPARE] 内容相似度: {similarity:.4f}")
    logger.info(f"[RESPONSE_COMPARE] 响应体长度: {len(orig_body)} -> {len(mod_body)}")
    
    if granted_access:
        logger.warning(f"[RESPONSE_COMPARE] 检测到权限授予: {orig_status} -> {mod_status}")
    
    if same_content:
        logger.warning(f"[RESPONSE_COMPARE] 检测到相同内容访问: 相似度={similarity:.4f}≥0.9")
        logger.info(f"[RESPONSE_COMPARE] 提示: 相同内容可能表示正常的相同权限，也可能表示越权访问")

    # 可选头部差异（若字段可用）
    # 兼容 original_response 的两种键名：headers/response_headers
    orig_headers = original_response.get("headers") or original_response.get("response_headers") or {}
    mod_headers = modified_response.get("headers") or {}
    header_diff_hint = ""
    try:
        # 仅对关键头做提示
        interesting = ["content-type", "set-cookie", "x-powered-by"]
        diffs = []
        for k in interesting:
            ov = _safe_text(orig_headers.get(k) or orig_headers.get(k.title()))
            mv = _safe_text(mod_headers.get(k) or mod_headers.get(k.title()))
            if ov != mv:
                diffs.append(f"{k}:{ov} -> {mv}")
        header_diff_hint = "; ".join(diffs)
    except Exception:
        header_diff_hint = ""

    return {
        "status_diff": (orig_status, mod_status),
        "content_similarity": similarity,
        "granted_access": granted_access,
        "same_content": same_content,
        "header_diff_hint": header_diff_hint,
    }


def detect_privilege_escalation(
    original_identity_role: Optional[str],
    target_identity_role: Optional[str],
    original_user_id: Optional[str],
    target_user_id: Optional[str],
) -> Dict[str, Any]:
    """
    权限检测器（简化对齐版）：
    - type: horizontal / vertical / mixed / unknown
      • horizontal：角色相同且用户ID不同
      • vertical：角色不同
      • mixed：无法确定或两条件均可能（保守返回）
    - confidence: high / medium / low
      • high：满足明显水平或垂直条件
      • medium：角色缺失但用户ID变化明显
      • low：信息不足
    """
    import logging
    logger = logging.getLogger(__name__)
    
    role_a = (original_identity_role or "").strip().lower()
    role_b = (target_identity_role or "").strip().lower()
    uid_a = (original_user_id or "").strip()
    uid_b = (target_user_id or "").strip()

    ptype = "unknown"
    confidence = "low"
    
    logger.info(f"[PRIVILEGE_DETECT] 权限检测开始:")
    logger.info(f"[PRIVILEGE_DETECT] 原始身份: role='{role_a}', uid='{uid_a}'")
    logger.info(f"[PRIVILEGE_DETECT] 目标身份: role='{role_b}', uid='{uid_b}'")

    try:
        if role_a and role_b:
            if role_a == role_b:
                # 同角色不同用户 → 水平越权
                if uid_a and uid_b and uid_a != uid_b:
                    ptype = "horizontal"
                    confidence = "high"
                    logger.warning(f"[PRIVILEGE_DETECT] 检测到水平越权: 相同角色({role_a})但不同用户({uid_a} -> {uid_b})")
                else:
                    ptype = "horizontal"
                    confidence = "medium"
                    logger.info(f"[PRIVILEGE_DETECT] 可能的水平越权: 相同角色({role_a})但用户信息不明确")
            else:
                # 不同角色 → 垂直越权
                ptype = "vertical"
                confidence = "high"
                logger.warning(f"[PRIVILEGE_DETECT] 检测到垂直越权: 不同角色({role_a} -> {role_b})")
        else:
            # 缺角色信息时，保守依据用户ID差异判定
            if uid_a and uid_b and uid_a != uid_b:
                ptype = "horizontal"
                confidence = "medium"
                logger.info(f"[PRIVILEGE_DETECT] 角色信息缺失，基于用户ID差异判定为水平越权({uid_a} -> {uid_b})")
            else:
                ptype = "unknown"
                confidence = "low"
                logger.info(f"[PRIVILEGE_DETECT] 信息不足，无法准确判定越权类型")
    except Exception as e:
        ptype = "unknown"
        confidence = "low"
        logger.error(f"[PRIVILEGE_DETECT] 权限检测异常: {e}")

    logger.info(f"[PRIVILEGE_DETECT] 检测结果: type={ptype}, confidence={confidence}")
    return {"type": ptype, "confidence": confidence}


def map_excel_risk_level(original_status: int, modified_status: int, similarity: float) -> str:
    """
    简化的风险等级判断逻辑（基于响应内容是否相同）：
    - 不同身份返回内容不同 → LOW风险（正常的权限控制）
    - 不同身份返回内容相同 → HIGH风险（可能存在越权）
    - 原始非200、修改后200 → HIGH风险（权限提升）
    - 其余情况 → MEDIUM风险
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[RISK_ANALYSIS] 开始风险等级判断: original_status={original_status}, modified_status={modified_status}, similarity={similarity:.4f}")
        
        # 权限提升：原始访问被拒绝，修改身份后获得访问权限
        if original_status != 200 and modified_status == 200:
            logger.warning(f"[RISK_ANALYSIS] 检测到权限提升: {original_status} -> {modified_status}, 判定为HIGH风险")
            return "HIGH"
        
        # 双方都成功访问的情况：基于内容是否相同判断
        if original_status == 200 and modified_status == 200:
            if similarity == 1.0:  # 内容完全相同
                logger.warning(f"[RISK_ANALYSIS] 不同身份返回完全相同内容: 可能存在越权访问, 判定为HIGH风险")
                return "HIGH"
            else:  # 内容不同
                logger.info(f"[RISK_ANALYSIS] 不同身份返回不同内容: 权限控制正常, 判定为LOW风险")
                return "LOW"
        
        # 其他情况：无法明确判断
        logger.info(f"[RISK_ANALYSIS] 其他情况({original_status} -> {modified_status}): 判定为MEDIUM风险")
        return "MEDIUM"
        
    except Exception as e:
        logger.error(f"[RISK_ANALYSIS] 风险等级判断异常: {e}")
        return "MEDIUM"


def build_evidence(
    original_response: Dict[str, Any],
    modified_response: Dict[str, Any],
    compare_dict: Dict[str, Any],
    detector_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    证据/evidence 聚合：
    - 包含状态差异、相似度、是否授予访问、权限类型与置信度、关键差异提示
    - 限制大小、避免泄露敏感内容（仅摘要）
    """
    orig_status, mod_status = compare_dict.get("status_diff", (0, 0))
    similarity = float(compare_dict.get("content_similarity") or 0.0)
    granted_access = bool(compare_dict.get("granted_access"))
    same_content = bool(compare_dict.get("same_content"))
    header_hint = _safe_text(compare_dict.get("header_diff_hint"), 512)

    # 摘要体（不直接输出完整响应体）
    orig_body_preview = _safe_text(original_response.get("text") or original_response.get("response_body") or "", 256)
    mod_body_preview = _safe_text(modified_response.get("text") or "", 256)

    evidence = {
        "status_diff": {"original": orig_status, "modified": mod_status},
        "content_similarity": round(similarity, 4),
        "granted_access": granted_access,
        "same_content": same_content,
        "header_diff_hint": header_hint,
        "privilege_type": detector_dict.get("type"),
        "confidence": detector_dict.get("confidence"),
        
    }
    return evidence