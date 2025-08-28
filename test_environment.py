#!/usr/bin/env python3
"""
环境配置测试脚本
"""

import sys
import os

def test_environment():
    """测试环境配置"""
    print("测试环境配置...")
    
    # 测试系统依赖
    try:
        import subprocess
        result = subprocess.run(['pdftoppm', '-h'], capture_output=True, text=True)
        print("✓ pdftoppm 可用")
    except FileNotFoundError:
        print("✗ pdftoppm 不可用，请安装 poppler-utils")
        return False
    except Exception as e:
        print(f"✗ pdftoppm 测试失败: {e}")
        return False
    
    try:
        result = subprocess.run(['pdfinfo', '-h'], capture_output=True, text=True)
        print("✓ pdfinfo 可用")
    except FileNotFoundError:
        print("✗ pdfinfo 不可用，请安装 poppler-utils")
        return False
    except Exception as e:
        print(f"✗ pdfinfo 测试失败: {e}")
        return False
    
    # 测试Python依赖
    try:
        import requests
        print("✓ requests 可用")
    except ImportError:
        print("✗ requests 不可用，请安装: pip install requests")
        return False
    
    try:
        import ebooklib
        print("✓ ebooklib 可用")
    except ImportError:
        print("✗ ebooklib 不可用，请安装: pip install ebooklib")
        return False
    
    try:
        from PIL import Image
        print("✓ pillow 可用")
    except ImportError:
        print("✗ pillow 不可用，请安装: pip install pillow")
        return False
    
    try:
        import PyPDF2
        print("✓ PyPDF2 可用")
    except ImportError:
        print("✗ PyPDF2 不可用，请安装: pip install PyPDF2")
        return False
    
    print("\n环境配置测试完成！")
    print("\n下一步：")
    print("1. 设置Gemini API密钥:")
    print("   export GEMINI_API_KEY=your_api_key_here")
    print("2. 运行转换器:")
    print("   python src/main.py --input /path/to/input.pdf --output /path/to/output.epub")
    
    return True

if __name__ == '__main__':
    test_environment()