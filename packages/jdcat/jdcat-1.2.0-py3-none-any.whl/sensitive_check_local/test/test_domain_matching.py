#!/usr/bin/env python3
"""
域名匹配容错测试脚本
验证修复后的域名匹配逻辑是否正确处理端口号和大小写问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from realtime_queue import RealtimeQueue

def test_domain_matching():
    """测试域名匹配容错功能"""
    
    # 模拟配置数据
    config = {
        "realtime": {
            "maxQueueSize": 1000,
            "batchIntervalSec": 10,
            "batchSize": 5,
            "finalFlushOnStop": True
        }
    }
    
    # 创建队列实例
    queue = RealtimeQueue(config)
    
    # 模拟上下文数据（包含域名配置）
    context = {
        "project_lines": [
            {
                "domains": ["api.example.com", "test.domain.org", "Service.API.com"]
            }
        ]
    }
    
    queue._context = context
    
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
    
    passed = 0
    failed = 0
    
    for url, expected, description in test_cases:
        # 构造测试项目
        item = {"url": url}
        
        try:
            result = queue._should_process_item(item)
            
            if result == expected:
                print(f"✅ {description}")
                print(f"   URL: {url}")
                print(f"   结果: {result} (符合预期)")
                passed += 1
            else:
                print(f"❌ {description}")
                print(f"   URL: {url}")
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
        return True
    else:
        print("⚠️  存在测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = test_domain_matching()
    sys.exit(0 if success else 1)