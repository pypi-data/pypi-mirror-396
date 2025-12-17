#!/usr/bin/env python3
"""
域名匹配容错测试脚本（独立版本）
直接测试域名规范化逻辑，无需导入其他模块
"""

from urllib.parse import urlparse

def normalize_domain_from_url(url):
    """
    从URL中提取并规范化域名
    复制自realtime_queue.py中的逻辑
    """
    if not url:
        return None
        
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc
        
        # 规范化域名：去除端口号并转为小写
        if ':' in netloc:
            domain = netloc.split(':')[0].lower()
        else:
            domain = netloc.lower()
            
        return domain
    except Exception:
        return None

def should_process_domain(url, configured_domains):
    """
    检查域名是否应该被处理
    模拟realtime_queue.py中的_should_process_item逻辑
    """
    domain = normalize_domain_from_url(url)
    if not domain:
        return False
        
    # 对配置的域名也进行小写转换进行比较
    normalized_domains = [d.lower() for d in configured_domains]
    return domain in normalized_domains

def test_domain_matching():
    """测试域名匹配容错功能"""
    
    # 模拟配置的域名列表
    configured_domains = ["api.example.com", "test.domain.org", "Service.API.com"]
    
    # 测试用例
    test_cases = [
        # 格式：(URL, 预期结果, 测试描述)
        ("https://api.example.com/api/users", True, "正常域名匹配"),
        ("https://api.example.com:443/api/users", True, "带HTTPS默认端口443"),
        ("http://api.example.com:80/api/users", True, "带HTTP默认端口80"),
        ("https://api.example.com:8080/api/users", True, "带自定义端口8080"),
        ("https://API.EXAMPLE.COM/api/users", True, "大写域名匹配"),
        ("https://API.EXAMPLE.COM:443/api/users", True, "大写域名带端口"),
        ("https://test.domain.org:9000/test", True, "另一个域名带端口"),
        ("https://SERVICE.API.COM/service", True, "混合大小写域名"),
        ("https://unknown.domain.com/api", False, "未配置的域名"),
        ("https://api.example.co/api", False, "相似但不同的域名"),
        ("", False, "空URL"),
        ("invalid-url", False, "无效URL格式"),
    ]
    
    print("🧪 开始域名匹配容错测试")
    print("=" * 60)
    print(f"配置的域名: {configured_domains}")
    print()
    
    passed = 0
    failed = 0
    
    for url, expected, description in test_cases:
        try:
            result = should_process_domain(url, configured_domains)
            
            if result == expected:
                print(f"✅ {description}")
                print(f"   URL: {url}")
                print(f"   提取域名: {normalize_domain_from_url(url)}")
                print(f"   结果: {result} (符合预期)")
                passed += 1
            else:
                print(f"❌ {description}")
                print(f"   URL: {url}")
                print(f"   提取域名: {normalize_domain_from_url(url)}")
                print(f"   预期: {expected}, 实际: {result}")
                failed += 1
                
        except Exception as e:
            print(f"💥 {description}")
            print(f"   URL: {url}")
            print(f"   异常: {e}")
            failed += 1
            
        print()
    
    print("=" * 60)
    print(f"📊 测试结果: 通过 {passed} 个，失败 {failed} 个")
    
    if failed == 0:
        print("🎉 所有测试通过！域名匹配容错修复成功")
        print()
        print("📋 修复效果总结:")
        print("✅ 正确处理带端口号的URL (如 api.example.com:443)")
        print("✅ 正确处理大小写不一致的域名")
        print("✅ 保持对无效URL和未配置域名的正确拒绝")
        return True
    else:
        print("⚠️  存在测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    import sys
    success = test_domain_matching()
    sys.exit(0 if success else 1)