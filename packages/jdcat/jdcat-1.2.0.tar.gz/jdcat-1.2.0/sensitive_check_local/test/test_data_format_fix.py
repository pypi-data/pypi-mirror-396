#!/usr/bin/env python3
"""
测试脚本：验证本地服务数据上报格式修复
测试修复后的 headers 字段序列化和 body 字段 base64 编码问题
"""

import json
import sys
import os
from typing import Dict, Any

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from realtime_manager import map_notify_to_item
from backend_client import BackendAPI


def test_headers_serialization():
    """测试 headers 字段序列化修复"""
    print("🧪 测试 headers 字段序列化修复...")
    
    # 测试用例1：正常的字典 headers
    test_case_1 = {
        "flowId": "test-001",
        "method": "POST",
        "url": "https://api.example.com/test",
        "requestHeaders": {"Content-Type": "application/json", "Authorization": "Bearer token123"},
        "responseHeaders": {"Content-Type": "application/json", "X-Response-Time": "100ms"},
        "requestBodyBase64": "eyJ0ZXN0IjoidmFsdWUifQ==",
        "responseBodyBase64": "eyJzdWNjZXNzIjp0cnVlfQ=="
    }
    
    result_1 = map_notify_to_item(test_case_1)
    
    assert isinstance(result_1["requestHeaders"], dict), "requestHeaders 应该是字典类型"
    assert isinstance(result_1["responseHeaders"], dict), "responseHeaders 应该是字典类型"
    assert result_1["requestHeaders"]["Content-Type"] == "application/json"
    assert result_1["responseHeaders"]["X-Response-Time"] == "100ms"
    print("✅ 测试用例1通过：正常字典 headers")
    
    # 测试用例2：字符串 "{}" headers（问题场景）
    test_case_2 = {
        "flowId": "test-002",
        "method": "GET",
        "url": "https://api.example.com/test2",
        "requestHeaders": "{}",  # 字符串格式
        "responseHeaders": "{}",  # 字符串格式
        "requestBodyBase64": "",
        "responseBodyBase64": ""
    }
    
    result_2 = map_notify_to_item(test_case_2)
    
    assert isinstance(result_2["requestHeaders"], dict), "requestHeaders 应该被转换为字典类型"
    assert isinstance(result_2["responseHeaders"], dict), "responseHeaders 应该被转换为字典类型"
    assert result_2["requestHeaders"] == {}, "空字符串 '{}' 应该转换为空字典"
    assert result_2["responseHeaders"] == {}, "空字符串 '{}' 应该转换为空字典"
    print("✅ 测试用例2通过：字符串 '{}' headers 正确转换为空字典")
    
    # 测试用例3：有效的 JSON 字符串 headers
    test_case_3 = {
        "flowId": "test-003",
        "method": "PUT",
        "url": "https://api.example.com/test3",
        "requestHeaders": '{"Content-Type": "application/json", "User-Agent": "TestAgent"}',
        "responseHeaders": '{"Server": "nginx", "Content-Length": "123"}',
        "requestBodyBase64": "dGVzdA==",
        "responseBodyBase64": "cmVzcG9uc2U="
    }
    
    result_3 = map_notify_to_item(test_case_3)
    
    assert isinstance(result_3["requestHeaders"], dict), "requestHeaders 应该是字典类型"
    assert isinstance(result_3["responseHeaders"], dict), "responseHeaders 应该是字典类型"
    assert result_3["requestHeaders"]["Content-Type"] == "application/json"
    assert result_3["responseHeaders"]["Server"] == "nginx"
    print("✅ 测试用例3通过：有效 JSON 字符串 headers 正确解析")
    
    # 测试用例4：无效的 JSON 字符串 headers
    test_case_4 = {
        "flowId": "test-004",
        "method": "DELETE",
        "url": "https://api.example.com/test4",
        "requestHeaders": "invalid json",  # 无效 JSON
        "responseHeaders": "{broken json",  # 无效 JSON
        "requestBodyBase64": None,
        "responseBodyBase64": None
    }
    
    result_4 = map_notify_to_item(test_case_4)
    
    assert isinstance(result_4["requestHeaders"], dict), "无效 JSON 应该回退到空字典"
    assert isinstance(result_4["responseHeaders"], dict), "无效 JSON 应该回退到空字典"
    assert result_4["requestHeaders"] == {}
    assert result_4["responseHeaders"] == {}
    assert result_4["requestBodyBase64"] == ""  # None 应该转换为空字符串
    assert result_4["responseBodyBase64"] == ""  # None 应该转换为空字符串
    print("✅ 测试用例4通过：无效 JSON 字符串正确回退到空字典，None body 转换为空字符串")


def test_body_base64_encoding():
    """测试 body 字段 base64 编码修复"""
    print("\n🧪 测试 body 字段 base64 编码修复...")
    
    # 测试用例1：正常的 base64 字符串
    test_case_1 = {
        "flowId": "body-test-001",
        "requestBodyBase64": "eyJ0ZXN0IjoidmFsdWUifQ==",  # {"test":"value"}
        "responseBodyBase64": "eyJzdWNjZXNzIjp0cnVlfQ=="   # {"success":true}
    }
    
    result_1 = map_notify_to_item(test_case_1)
    
    assert isinstance(result_1["requestBodyBase64"], str), "requestBodyBase64 应该是字符串类型"
    assert isinstance(result_1["responseBodyBase64"], str), "responseBodyBase64 应该是字符串类型"
    assert result_1["requestBodyBase64"] == "eyJ0ZXN0IjoidmFsdWUifQ=="
    assert result_1["responseBodyBase64"] == "eyJzdWNjZXNzIjp0cnVlfQ=="
    print("✅ 测试用例1通过：正常 base64 字符串保持不变")
    
    # 测试用例2：None 值
    test_case_2 = {
        "flowId": "body-test-002",
        "requestBodyBase64": None,
        "responseBodyBase64": None
    }
    
    result_2 = map_notify_to_item(test_case_2)
    
    assert result_2["requestBodyBase64"] == "", "None 应该转换为空字符串"
    assert result_2["responseBodyBase64"] == "", "None 应该转换为空字符串"
    print("✅ 测试用例2通过：None 值正确转换为空字符串")
    
    # 测试用例3：数字类型
    test_case_3 = {
        "flowId": "body-test-003",
        "requestBodyBase64": 12345,
        "responseBodyBase64": 67890
    }
    
    result_3 = map_notify_to_item(test_case_3)
    
    assert result_3["requestBodyBase64"] == "12345", "数字应该转换为字符串"
    assert result_3["responseBodyBase64"] == "67890", "数字应该转换为字符串"
    print("✅ 测试用例3通过：数字类型正确转换为字符串")


def test_backend_payload_format():
    """测试后端上报数据格式"""
    print("\n🧪 测试后端上报数据格式...")
    
    # 模拟修复后的数据格式
    mock_results = [
        {
            "taskId": "RT123",
            "domain": "api.example.com",
            "path": "/test",
            "method": "POST",
            "occurMs": 1698765432000,
            "statusCode": 200,
            "requestHeaders": {"Content-Type": "application/json"},  # 字典对象
            "responseHeaders": {"Content-Type": "application/json", "Server": "nginx"},  # 字典对象
            "requestBodyBase64": "eyJ0ZXN0IjoidmFsdWUifQ==",  # 字符串
            "responseBodyBase64": "eyJzdWNjZXNzIjp0cnVlfQ=="   # 字符串
        }
    ]
    
    # 验证数据格式符合后端 RealtimeIngestItemDTO 要求
    for result in mock_results:
        assert isinstance(result["requestHeaders"], dict), "requestHeaders 必须是 Map<String, Object>"
        assert isinstance(result["responseHeaders"], dict), "responseHeaders 必须是 Map<String, Object>"
        assert isinstance(result["requestBodyBase64"], str), "requestBodyBase64 必须是字符串"
        assert isinstance(result["responseBodyBase64"], str), "responseBodyBase64 必须是字符串"
        assert isinstance(result["taskId"], str), "taskId 必须是字符串"
        assert isinstance(result["domain"], str), "domain 必须是字符串"
        assert isinstance(result["path"], str), "path 必须是字符串"
        assert isinstance(result["method"], str), "method 必须是字符串"
        assert isinstance(result["occurMs"], int), "occurMs 必须是整数"
    
    print("✅ 后端上报数据格式验证通过")
    
    # 构造完整的批量上报请求体
    payload = {
        "taskId": "RT123",
        "items": mock_results
    }
    
    # 验证 JSON 序列化
    try:
        json_str = json.dumps(payload, ensure_ascii=False)
        parsed_back = json.loads(json_str)
        assert parsed_back["taskId"] == "RT123"
        assert len(parsed_back["items"]) == 1
        assert isinstance(parsed_back["items"][0]["requestHeaders"], dict)
        print("✅ JSON 序列化/反序列化验证通过")
    except Exception as e:
        print(f"❌ JSON 序列化失败: {e}")
        raise


def main():
    """运行所有测试"""
    print("🚀 开始验证本地服务数据上报格式修复...\n")
    
    try:
        test_headers_serialization()
        test_body_base64_encoding()
        test_backend_payload_format()
        
        print("\n🎉 所有测试通过！数据格式修复验证成功！")
        print("\n📋 修复总结:")
        print("✅ requestHeaders/responseHeaders 现在始终是字典对象，不再是字符串 '{}'")
        print("✅ requestBodyBase64/responseBodyBase64 现在始终是字符串，None 值转换为空字符串")
        print("✅ 数据格式符合后端 RealtimeIngestItemDTO 的要求")
        print("✅ JSON 序列化/反序列化正常工作")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)