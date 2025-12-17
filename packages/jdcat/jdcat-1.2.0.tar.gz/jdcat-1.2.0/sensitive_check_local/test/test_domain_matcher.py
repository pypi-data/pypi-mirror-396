#!/usr/bin/env python3
"""
域名匹配器测试脚本

测试简化的域名匹配功能，验证基本的字符串匹配逻辑。
"""

import sys
import os
from pathlib import Path

# 添加父目录到 Python 路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from domain_matcher import (
    SimpleDomainMatcher,
    build_domain_matcher_from_context,
    should_accept_domain_simple,
    build_accepted_domains_simple
)


def test_simple_domain_matcher():
    """测试简单域名匹配器"""
    print("=== 测试简单域名匹配器 ===")
    
    # 测试1: 无域名限制（允许所有）
    matcher = SimpleDomainMatcher(None)
    assert matcher.should_accept_domain("api.example.com") == True
    assert matcher.should_accept_domain("test.com") == True
    print("✓ 无域名限制测试通过")
    
    # 测试2: 有域名限制
    allowed_domains = {"api.example.com", "test.com", "admin.test.com"}
    matcher = SimpleDomainMatcher(allowed_domains)
    
    assert matcher.should_accept_domain("api.example.com") == True
    assert matcher.should_accept_domain("test.com") == True
    assert matcher.should_accept_domain("admin.test.com") == True
    assert matcher.should_accept_domain("blocked.com") == False
    assert matcher.should_accept_domain("API.EXAMPLE.COM") == True  # 大小写不敏感
    print("✓ 域名限制测试通过")
    
    # 测试3: 从请求项中提取域名
    request_item1 = {"domain": "api.example.com"}
    assert matcher.should_accept_request(request_item1) == True
    
    request_item2 = {"url": "https://test.com/api/users"}
    assert matcher.should_accept_request(request_item2) == True
    
    request_item3 = {"requestHeaders": {"Host": "admin.test.com:8080"}}
    assert matcher.should_accept_request(request_item3) == True
    
    request_item4 = {"domain": "blocked.com"}
    assert matcher.should_accept_request(request_item4) == False
    print("✓ 请求项域名提取测试通过")


def test_context_based_matcher():
    """测试基于上下文的域名匹配器"""
    print("\n=== 测试基于上下文的域名匹配器 ===")
    
    # 测试1: 非个人空间（project_id > 0）
    ctx1 = {
        "projectId": 1,
        "project_lines": [
            {
                "projectId": 1,
                "domains": ["api.example.com", "test.com"]
            }
        ]
    }
    
    matcher1 = build_domain_matcher_from_context(ctx1)
    assert matcher1.should_accept_domain("api.example.com") == True
    assert matcher1.should_accept_domain("test.com") == True
    assert matcher1.should_accept_domain("blocked.com") == False
    print("✓ 非个人空间域名匹配测试通过")
    
    # 测试2: 个人空间（project_id == 0）
    ctx2 = {
        "projectId": 0,
        "project_lines": [
            {
                "projectId": 0,
                "domains": ["api1.example.com", "test1.com"]
            },
            {
                "projectId": 0,
                "domains": ["api2.example.com", "test2.com"]
            }
        ]
    }
    
    matcher2 = build_domain_matcher_from_context(ctx2)
    assert matcher2.should_accept_domain("api1.example.com") == True
    assert matcher2.should_accept_domain("test1.com") == True
    assert matcher2.should_accept_domain("api2.example.com") == True
    assert matcher2.should_accept_domain("test2.com") == True
    assert matcher2.should_accept_domain("blocked.com") == False
    print("✓ 个人空间域名匹配测试通过")
    
    # 测试3: 空域名列表（不过滤）
    ctx3 = {
        "projectId": 1,
        "project_lines": [
            {
                "projectId": 1,
                "domains": []
            }
        ]
    }
    
    matcher3 = build_domain_matcher_from_context(ctx3)
    assert matcher3.should_accept_domain("any.domain.com") == True
    print("✓ 空域名列表测试通过")


def test_integration_functions():
    """测试集成函数"""
    print("\n=== 测试集成函数 ===")
    
    ctx = {
        "projectId": 1,
        "project_lines": [
            {
                "projectId": 1,
                "domains": ["api.example.com", "test.com"]
            }
        ]
    }
    
    # 测试 should_accept_domain_simple
    request_item1 = {"domain": "api.example.com"}
    assert should_accept_domain_simple(request_item1, ctx) == True
    
    request_item2 = {"domain": "blocked.com"}
    assert should_accept_domain_simple(request_item2, ctx) == False
    
    # 测试 build_accepted_domains_simple
    accepted_domains = build_accepted_domains_simple(ctx)
    assert accepted_domains == {"api.example.com", "test.com"}
    
    print("✓ 集成函数测试通过")


def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    matcher = SimpleDomainMatcher({"test.com"})
    
    # 空域名
    assert matcher.should_accept_domain("") == False
    assert matcher.should_accept_domain(None) == False
    
    # 空白字符
    assert matcher.should_accept_domain("  ") == False
    assert matcher.should_accept_domain("\t\n") == False
    
    # 复杂请求项
    complex_request = {
        "url": "https://test.com:8080/api/users?id=123",
        "requestHeaders": {
            "Host": "test.com:8080",
            "User-Agent": "TestAgent"
        }
    }
    assert matcher.should_accept_request(complex_request) == True
    
    # 无有效域名信息的请求项
    empty_request = {
        "method": "GET",
        "path": "/api/users"
    }
    assert matcher.should_accept_request(empty_request) == False
    
    print("✓ 边界情况测试通过")


def test_performance():
    """简单的性能测试"""
    print("\n=== 简单性能测试 ===")
    
    import time
    
    # 创建包含多个域名的匹配器
    large_domain_set = {f"api{i}.example.com" for i in range(1000)}
    matcher = SimpleDomainMatcher(large_domain_set)
    
    # 测试匹配性能
    start_time = time.time()
    for i in range(10000):
        domain = f"api{i % 1000}.example.com"
        matcher.should_accept_domain(domain)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"✓ 10000次域名匹配耗时: {duration:.3f}秒")
    
    # 获取统计信息
    stats = matcher.get_stats()
    print(f"✓ 统计信息: {stats}")


def main():
    """运行所有测试"""
    print("开始域名匹配器测试...")
    
    try:
        test_simple_domain_matcher()
        test_context_based_matcher()
        test_integration_functions()
        test_edge_cases()
        test_performance()
        
        print("\n🎉 所有测试通过！")
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())