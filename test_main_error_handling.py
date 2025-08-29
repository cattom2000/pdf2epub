#!/usr/bin/env python3
"""
测试主程序中的错误处理机制
"""

import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main


def test_main_error_handling():
    """测试主程序中的错误处理"""
    print("测试主程序中的错误处理机制...")
    
    # 创建一个临时的测试PDF文件
    test_pdf_path = "/tmp/test.pdf"
    with open(test_pdf_path, "wb") as f:
        f.write(b"%PDF-1.4 fake PDF content")
    
    try:
        # 模拟命令行参数
        test_args = [
            'main.py',
            '--input', test_pdf_path,
            '--output', '/tmp/test.epub'
        ]
        
        # 模拟PDF处理成功但Gemini调用失败的情况
        with patch.object(sys, 'argv', test_args):
            with patch('src.main.PDFProcessor') as mock_pdf_processor, \
                 patch('src.main.GeminiClient') as mock_gemini_client:
                
                # 模拟PDF处理成功
                mock_pdf_processor_instance = MagicMock()
                mock_pdf_processor.return_value = mock_pdf_processor_instance
                mock_pdf_processor_instance.pdf_to_images.return_value = ['/tmp/image1.png', '/tmp/image2.png']
                
                # 模拟Gemini调用失败
                mock_gemini_client_instance = MagicMock()
                mock_gemini_client.return_value = mock_gemini_client_instance
                mock_gemini_client_instance.extract_text.side_effect = Exception("模拟Gemini调用失败")
                
                try:
                    main()
                except SystemExit as e:
                    print(f"程序正确退出，退出码: {e.code}")
                    if e.code == 1:
                        print("错误处理机制工作正常")
                    else:
                        print("意外的退出码")
                except Exception as e:
                    print(f"捕获到未预期的异常: {e}")
                    
    finally:
        # 清理临时文件
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)


if __name__ == '__main__':
    test_main_error_handling()