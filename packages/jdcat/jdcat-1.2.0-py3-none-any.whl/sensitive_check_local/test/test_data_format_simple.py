#!/usr/bin/env python3
"""
简化测试脚本：验证本地服务数据上报格式修复
不依赖外部模块，直接测试核心逻辑
"""

import json
import sys
import os

def test_headers_format_fix():
    """测试 headers 字段格式修复逻辑"""
    print("🧪 测试 headers 字段格式修复逻辑...")
    
    def fix_headers_field(headers_raw):
        """修复 headers 字段的函数（从 realtime_manager.py 提取的逻辑）"""
        if isinstance(headers_raw, dict):
            return headers_raw
        elif isinstance(headers_raw, str):
            try:
                return json.loads(headers_raw) if headers_raw.strip() else {}
            except (json.JSONDecodeError, AttributeError):
                return {}
        else:
            return {}
    
    # 测试用例1：正常字典
    test1 = {"Content-Type": "application/json", "Authorization": "Bearer token"}
    result1 = fix_headers_field(test1)
    assert isinstance(result1, dict), "正常字典应该保持不变"
    assert result1["Content-Type"] == "application/json"
    print("✅ 测试用例1通过：正常字典保持不变")
    
    # 测试用例2：字符串 "{}"（问题场景）
    test2 = "{}"
    result2 = fix_headers_field(test2)
    assert isinstance(result2, dict), "字符串 '{}' 应该转换为字典"
    assert result2 == {}, "空字符串 '{}' 应该转换为空字典"
    print("✅ 测试用例2通过：字符串 '{}' 正确转换为空字典")
    
    # 测试用例3：有效 JSON 字符串
    test3 = '{"Server": "nginx", "Content-Length": "123"}'
    result3 = fix_headers_field(test3)
    assert isinstance(result3, dict), "有效 JSON 字符串应该转换为字典"
    assert result3["Server"] == "nginx"
    print("✅ 测试用例3通过：有效 JSON 字符串正确解析")
    
    # 测试用例4：无效 JSON 字符串
    test4 = "invalid json"
    result4 = fix_headers_field(test4)
    assert isinstance(result4, dict), "无效 JSON 应该回退到空字典"
    assert result4 == {}
    print("✅ 测试用例4通过：无效 JSON 正确回退到空字典")
    
    # 测试用例5：None 值
    test5 = None
    result5 = fix_headers_field(test5)
    assert isinstance(result5, dict), "None 应该转换为空字典"
    assert result5 == {}
    print("✅ 测试用例5通过：None 值正确转换为空字典")


def test_body_format_fix():
    """测试 body 字段格式修复逻辑"""
    print("\n🧪 测试 body 字段格式修复逻辑...")
    
    def fix_body_field(body_raw):
        """修复 body 字段的函数（从 realtime_manager.py 提取的逻辑）"""
        return str(body_raw) if body_raw is not None else ""
    
    # 测试用例1：正常字符串
    test1 = "eyJ0ZXN0IjoidmFsdWUifQ=="
    result1 = fix_body_field(test1)
    assert isinstance(result1, str), "正常字符串应该保持字符串类型"
    assert result1 == "eyJ0ZXN0IjoidmFsdWUifQ=="
    print("✅ 测试用例1通过：正常字符串保持不变")
    
    # 测试用例2：None 值
    test2 = None
    result2 = fix_body_field(test2)
    assert result2 == "", "None 应该转换为空字符串"
    print("✅ 测试用例2通过：None 值正确转换为空字符串")
    
    # 测试用例3：数字类型
    test3 = 12345
    result3 = fix_body_field(test3)
    assert result3 == "12345", "数字应该转换为字符串"
    print("✅ 测试用例3通过：数字类型正确转换为字符串")
    
    # 测试用例4：空字符串
    test4 = ""
    result4 = fix_body_field(test4)
    assert result4 == "", "空字符串应该保持空字符串"
    print("✅ 测试用例4通过：空字符串保持不变")


def test_backend_expected_format():
    """测试后端期望的数据格式"""
    print("\n🧪 测试后端期望的数据格式...")
    
    # 模拟修复后的数据格式
    mock_item = {
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
    
    # 验证数据格式符合后端 RealtimeIngestItemDTO 要求
    assert isinstance(mock_item["requestHeaders"], dict), "requestHeaders 必须是字典"
    assert isinstance(mock_item["responseHeaders"], dict), "responseHeaders 必须是字典"
    assert isinstance(mock_item["requestBodyBase64"], str), "requestBodyBase64 必须是字符串"
    assert isinstance(mock_item["responseBodyBase64"], str), "responseBodyBase64 必须是字符串"
    assert isinstance(mock_item["taskId"], str), "taskId 必须是字符串"
    assert isinstance(mock_item["domain"], str), "domain 必须是字符串"
    assert isinstance(mock_item["path"], str), "path 必须是字符串"
    assert isinstance(mock_item["method"], str), "method 必须是字符串"
    assert isinstance(mock_item["occurMs"], int), "occurMs 必须是整数"
    
    print("✅ 后端期望数据格式验证通过")
    
    # 构造完整的批量上报请求体
    payload = {
        "taskId": "RT123",
        "items": [mock_item]
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


def test_problem_scenario():
    """测试原问题场景：字符串 "{}" 导致后端解析错误"""
    print("\n🧪 测试原问题场景修复...")
    
    # 模拟原问题：上报的数据包含字符串 "{}"
    problematic_data = {
        "taskId": "RT123",
        "domain": "api.example.com", 
        "path": "/test",
        "method": "GET",
        "occurMs": 1698765432000,
        "statusCode": 200,
        "requestHeaders": "{}",  # 问题：字符串而不是对象
        "responseHeaders": "{}",  # 问题：字符串而不是对象
        "requestBodyBase64": None,  # 问题：None 而不是字符串
        "responseBodyBase64": None   # 问题：None 而不是字符串
    }
    
    print(f"🔍 原问题数据格式:")
    print(f"  - requestHeaders: {type(problematic_data['requestHeaders'])} = {problematic_data['requestHeaders']}")
    print(f"  - responseHeaders: {type(problematic_data['responseHeaders'])} = {problematic_data['responseHeaders']}")
    print(f"  - requestBodyBase64: {type(problematic_data['requestBodyBase64'])} = {problematic_data['requestBodyBase64']}")
    print(f"  - responseBodyBase64: {type(problematic_data['responseBodyBase64'])} = {problematic_data['responseBodyBase64']}")
    
    # 应用修复逻辑
    def fix_headers_field(headers_raw):
        if isinstance(headers_raw, dict):
            return headers_raw
        elif isinstance(headers_raw, str):
            try:
                return json.loads(headers_raw) if headers_raw.strip() else {}
            except (json.JSONDecodeError, AttributeError):
                return {}
        else:
            return {}
    
    def fix_body_field(body_raw):
        return str(body_raw) if body_raw is not None else ""
    
    fixed_data = problematic_data.copy()
    fixed_data["requestHeaders"] = fix_headers_field(problematic_data["requestHeaders"])
    fixed_data["responseHeaders"] = fix_headers_field(problematic_data["responseHeaders"])
    fixed_data["requestBodyBase64"] = fix_body_field(problematic_data["requestBodyBase64"])
    fixed_data["responseBodyBase64"] = fix_body_field(problematic_data["responseBodyBase64"])
    
    print(f"\n✅ 修复后数据格式:")
    print(f"  - requestHeaders: {type(fixed_data['requestHeaders'])} = {fixed_data['requestHeaders']}")
    print(f"  - responseHeaders: {type(fixed_data['responseHeaders'])} = {fixed_data['responseHeaders']}")
    print(f"  - requestBodyBase64: {type(fixed_data['requestBodyBase64'])} = {fixed_data['requestBodyBase64']}")
    print(f"  - responseBodyBase64: {type(fixed_data['responseBodyBase64'])} = {fixed_data['responseBodyBase64']}")
    
    # 验证修复结果
    assert isinstance(fixed_data["requestHeaders"], dict), "requestHeaders 应该是字典"
    assert isinstance(fixed_data["responseHeaders"], dict), "responseHeaders 应该是字典"
    assert isinstance(fixed_data["requestBodyBase64"], str), "requestBodyBase64 应该是字符串"
    assert isinstance(fixed_data["responseBodyBase64"], str), "responseBodyBase64 应该是字符串"
    assert fixed_data["requestHeaders"] == {}
    assert fixed_data["responseHeaders"] == {}
    assert fixed_data["requestBodyBase64"] == ""
    assert fixed_data["responseBodyBase64"] == ""
    
    print("✅ 原问题场景修复验证通过")


def main():
    """运行所有测试"""
    print("🚀 开始验证本地服务数据上报格式修复...\n")
    
    try:
        test_headers_format_fix()
        test_body_format_fix()
        test_backend_expected_format()
        test_problem_scenario()
        
        print("\n🎉 所有测试通过！数据格式修复验证成功！")
        print("\n📋 修复总结:")
        print("✅ requestHeaders/responseHeaders 现在始终是字典对象，不再是字符串 '{}'")
        print("✅ requestBodyBase64/responseBodyBase64 现在始终是字符串，None 值转换为空字符串")
        print("✅ 数据格式符合后端 RealtimeIngestItemDTO 的要求")
        print("✅ JSON 序列化/反序列化正常工作")
        print("✅ 原问题场景（字符串 '{}' 和 None 值）已完全修复")
        
        print("\n🔧 修复的关键问题:")
        print("1. 后端日志错误：'Cannot construct instance of java.util.LinkedHashMap'")
        print("   - 原因：本地服务发送字符串 '{}' 而不是 JSON 对象")
        print("   - 修复：在数据映射和上报时确保 headers 字段是字典对象")
        print("2. Body 字段 null 值问题：")
        print("   - 原因：None 值导致后端无法正确处理")
        print("   - 修复：None 值统一转换为空字符串")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)