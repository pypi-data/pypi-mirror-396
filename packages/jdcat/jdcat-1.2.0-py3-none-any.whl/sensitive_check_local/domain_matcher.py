"""
简化的域名匹配系统

基于实时任务启动时配置的域名列表，进行简单的字符串匹配过滤。
与现有的 realtime_queue.py 中的 _build_accepted_domains 和 should_accept_domain 函数集成。

设计目标：
1. 简单高效的域名字符串匹配
2. 与现有实时检测系统无缝集成
3. 支持基本的域名过滤功能
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlsplit

# 模块级 logger
_logger = logging.getLogger("sensitive_check_local.domain_matcher")


class SimpleDomainMatcher:
    """简化的域名匹配器
    
    基于配置的域名列表进行简单的字符串匹配。
    """
    
    def __init__(self, allowed_domains: Optional[Set[str]] = None):
        """初始化域名匹配器
        
        Args:
            allowed_domains: 允许的域名集合，None表示不过滤
        """
        self.allowed_domains = allowed_domains
        
        # 统计信息
        self._stats = {
            "total_matches": 0,
            "allowed_count": 0,
            "filtered_count": 0
        }
    
    def should_accept_domain(self, domain: str) -> bool:
        """判断域名是否应该被接受
        
        Args:
            domain: 要检查的域名
            
        Returns:
            True表示接受，False表示过滤
        """
        self._stats["total_matches"] += 1
        
        # 如果没有配置允许的域名列表，则不过滤
        if self.allowed_domains is None:
            self._stats["allowed_count"] += 1
            return True
        
        # 域名标准化处理
        domain_clean = domain.lower().strip() if domain else ""
        
        # 检查是否在允许列表中
        if domain_clean in self.allowed_domains:
            self._stats["allowed_count"] += 1
            return True
        else:
            self._stats["filtered_count"] += 1
            return False
    
    def should_accept_request(self, request_item: Dict[str, Any]) -> bool:
        """判断请求是否应该被接受（基于域名）
        
        Args:
            request_item: 请求项，包含域名信息
            
        Returns:
            True表示接受，False表示过滤
        """
        # 提取域名，优先级：domain字段 > url解析 > Host头
        domain = self._extract_domain_from_request(request_item)
        return self.should_accept_domain(domain)
    
    def _extract_domain_from_request(self, request_item: Dict[str, Any]) -> str:
        """从请求项中提取域名
        
        Args:
            request_item: 请求项字典
            
        Returns:
            提取的域名字符串
        """
        # 1. 优先使用 domain 字段
        domain = str(request_item.get("domain") or "").strip()
        if domain:
            return domain.lower()
        
        # 2. 从 url 字段解析
        url = request_item.get("url") or ""
        if url:
            try:
                parsed = urlsplit(str(url))
                domain = (parsed.hostname or "").strip()
                if domain:
                    return domain.lower()
            except Exception:
                pass
        
        # 3. 从请求头中获取 Host
        headers = request_item.get("requestHeaders") or request_item.get("headers") or {}
        if isinstance(headers, dict):
            host = str(headers.get("Host") or headers.get("host") or "").strip()
            if host:
                # Host头可能包含端口号，需要去除
                return host.split(':')[0].lower()
        
        # 4. 兼容其他可能的字段
        request_obj = request_item.get("request") or {}
        if isinstance(request_obj, dict):
            host = str(request_obj.get("host") or "").strip()
            if host:
                return host.split(':')[0].lower()
        
        return ""
    
    def update_allowed_domains(self, domains: Optional[Set[str]]) -> None:
        """更新允许的域名列表
        
        Args:
            domains: 新的域名集合，None表示不过滤
        """
        self.allowed_domains = domains
        _logger.info(f"Updated allowed domains: {len(domains) if domains else 0} domains")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            "allowed_domains_count": len(self.allowed_domains) if self.allowed_domains else 0,
            "filter_enabled": self.allowed_domains is not None
        }
    
    def clear_stats(self) -> None:
        """清空统计信息"""
        self._stats = {
            "total_matches": 0,
            "allowed_count": 0,
            "filtered_count": 0
        }


def build_domain_matcher_from_context(ctx: Dict[str, Any]) -> SimpleDomainMatcher:
    """从上下文构建域名匹配器
    
    这个函数复用现有的 _build_accepted_domains 逻辑，
    与 realtime_queue.py 中的实现保持一致。
    
    Args:
        ctx: 运行上下文，包含 projectId/project_id 与 project_lines
        
    Returns:
        配置好的域名匹配器
    """
    try:
        # 读取 project_id（兼容驼峰/下划线）
        raw_pid = ctx.get("projectId") if "projectId" in ctx else ctx.get("project_id")
        pid = int(raw_pid) if raw_pid is not None else None

        # 读取 project_lines（兼容驼峰）
        lines = ctx.get("project_lines")
        if lines is None:
            lines = ctx.get("projectLines")
        if not isinstance(lines, list):
            lines = []

        # 非个人空间：仅使用单行 domains
        if pid is not None and pid > 0:
            if not lines:
                return SimpleDomainMatcher(None)
            row = lines[0] if isinstance(lines[0], dict) else {}
            domains = row.get("domains") or []
            if isinstance(domains, list) and len(domains) > 0:
                domain_set = set(str(x).strip().lower() for x in domains if str(x).strip())
                return SimpleDomainMatcher(domain_set)
            return SimpleDomainMatcher(None)

        # 个人空间：合并所有非空行的 domains
        union: set[str] = set()
        for row in lines:
            if not isinstance(row, dict):
                continue
            dm = row.get("domains") or []
            if isinstance(dm, list) and dm:
                for x in dm:
                    s = str(x).strip().lower()
                    if s:
                        union.add(s)
        
        return SimpleDomainMatcher(union if len(union) > 0 else None)
        
    except Exception as e:
        _logger.warning(f"Failed to build domain matcher from context: {e}")
        return SimpleDomainMatcher(None)


def should_accept_domain_simple(item: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    """简化版本的域名接受判断函数
    
    这个函数可以替代 realtime_queue.py 中的 should_accept_domain 函数，
    提供相同的接口但使用简化的实现。
    
    Args:
        item: 单条事件字典
        ctx: 运行上下文
        
    Returns:
        True表示接受，False表示过滤
    """
    try:
        matcher = build_domain_matcher_from_context(ctx)
        return matcher.should_accept_request(item)
    except Exception as e:
        _logger.warning(f"Domain acceptance check failed: {e}")
        return True  # 失败时默认接受，避免影响现有流程


def build_accepted_domains_simple(ctx: Dict[str, Any]) -> Optional[set[str]]:
    """简化版本的域名集合构建函数
    
    这个函数可以替代 realtime_queue.py 中的 _build_accepted_domains 函数，
    提供相同的接口和返回值格式。
    
    Args:
        ctx: 运行上下文
        
    Returns:
        允许的域名集合，None表示不过滤
    """
    try:
        matcher = build_domain_matcher_from_context(ctx)
        return matcher.allowed_domains
    except Exception as e:
        _logger.warning(f"Failed to build accepted domains: {e}")
        return None


# 全局域名匹配器实例（可选，用于性能优化）
_global_matcher: Optional[SimpleDomainMatcher] = None


def get_global_matcher() -> SimpleDomainMatcher:
    """获取全局域名匹配器实例"""
    global _global_matcher
    if _global_matcher is None:
        _global_matcher = SimpleDomainMatcher(None)
    return _global_matcher


def update_global_matcher(ctx: Dict[str, Any]) -> None:
    """更新全局域名匹配器"""
    global _global_matcher
    _global_matcher = build_domain_matcher_from_context(ctx)