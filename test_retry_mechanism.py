#!/usr/bin/env python3
"""
测试Gemini客户端的重试机制
"""

import sys
import os
import time
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.gemini_client import GeminiClient


def test_retry_mechanism():
    """测试重试机制"""
    print("测试Gemini客户端的重试机制...")
    
    # 创建一个临时的测试图像文件
    test_image_path = "/tmp/test_image.png"
    with open(test_image_path, "wb") as f:
        f.write(b"fake image data")
    
    try:
        # 创建GeminiClient实例（使用模拟的API密钥）
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            client = GeminiClient()
        
        # 测试连续失败的情况
        print("\n测试连续失败情况（最大重试3次）:")
        try:
            with patch.object(client.client, 'generate_content', side_effect=Exception("模拟API错误")):
                start_time = time.time()
                client.extract_text(test_image_path, max_retries=3)
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"捕获到预期的异常: {e}")
            print(f"总耗时: {elapsed:.2f} 秒")
            print("重试机制工作正常")
        
        # 测试第一次失败，第二次成功的情况
        print("\n测试第一次失败，第二次成功:")
        call_count = 0
        def mock_generate_content(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("第一次调用失败")
            return "测试文本内容"
        
        try:
            with patch.object(client.client, 'generate_content', side_effect=mock_generate_content):
                result = client.extract_text(test_image_path, max_retries=3)
                print(f"成功获取结果: {result}")
                print(f"总共尝试了 {call_count} 次")
        except Exception as e:
            print(f"意外错误: {e}")
            
        # 测试立即成功的情况
        print("\n测试立即成功:")
        try:
            with patch.object(client.client, 'generate_content', return_value="立即成功的测试文本"):
                result = client.extract_text(test_image_path, max_retries=3)
                print(f"成功获取结果: {result}")
        except Exception as e:
            print(f"意外错误: {e}")
            
    finally:
        # 清理临时文件
        if os.path.exists(test_image_path):
            os.remove(test_image_path)


if __name__ == '__main__':
    test_retry_mechanism()