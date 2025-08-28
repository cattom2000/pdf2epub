#!/usr/bin/env python3
"""
测试MiniGenAI类
"""

import os
import sys
import argparse

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.minigenai import MiniGenAI


def test_minigenai(model='gemini-2.5-flash', base_url=None):
    """测试MiniGenAI类"""
    print(f"测试MiniGenAI类 (模型: {model})...")
    
    # 检查API密钥
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("请设置GEMINI_API_KEY环境变量")
        return False
    
    try:
        # 初始化MiniGenAI客户端
        client = MiniGenAI(api_key, base_url) if base_url else MiniGenAI(api_key)
        print("✓ MiniGenAI客户端初始化成功")
        
        # 测试文本生成
        response = client.generate_text(model, '你好，世界！')
        print(f"✓ 文本生成测试成功: {response}")
        
        # 测试对话功能
        history = [
            {"role": "user", "parts": [{"text": "你好"}]},
            {"role": "model", "parts": [{"text": "你好，请问有什么能帮你？"}]},
            {"role": "user", "parts": [{"text": "今天天气怎么样？"}]}
        ]
        response = client.chat(model, history)
        print(f"✓ 对话功能测试成功: {response}")
        
        # 测试generate_content功能（如果模型支持图像处理）
        contents = [
            {
                "role": "user",
                "parts": [
                    {"text": "请描述这张图片的内容"}
                ]
            }
        ]
        try:
            response = client.generate_content(model, contents)
            print(f"✓ 内容生成功能测试成功: {response}")
        except Exception as e:
            print(f"⚠ 内容生成功能测试警告: {e}")
        
        print("\nMiniGenAI类测试完成！")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='测试MiniGenAI类')
    parser.add_argument('--model', default='gemini-2.5-flash', 
                       choices=['gemini-2.5-flash', 'gemini-2.5-pro'],
                       help='使用的Gemini模型 (默认: gemini-2.5-flash)')
    parser.add_argument('--base-url', help='Gemini API的基础URL (可选，用于指定代理服务器)')
    
    args = parser.parse_args()
    
    test_minigenai(args.model, args.base_url)


if __name__ == '__main__':
    main()