#!/usr/bin/env python3
"""
PDF转EPUB转换器主程序
"""

import argparse
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processors.pdf_processor import PDFProcessor
from api.gemini_client import GeminiClient
from generator.epub_generator import EpubGenerator


def main():
    parser = argparse.ArgumentParser(description='将PDF转换为EPUB电子书')
    parser.add_argument('--input', '-i', required=True, help='输入PDF文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出EPUB文件路径')
    parser.add_argument('--dpi', type=int, default=200, help='图像DPI (默认: 200)')
    parser.add_argument('--model', choices=['flash', 'pro'], default='flash', 
                       help='使用的Gemini模型 (默认: flash)')
    parser.add_argument('--base-url', help='Gemini API的基础URL (可选，用于指定代理服务器)')
    parser.add_argument('--page-range', nargs=2, type=int, metavar=('START', 'END'),
                       help='处理的页码范围 (例如: --page-range 1 10 表示处理第1到10页)')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件 {args.input} 不存在")
        sys.exit(1)
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # 初始化组件
        pdf_processor = PDFProcessor()
        gemini_client = GeminiClient(model_type=args.model, base_url=args.base_url)
        epub_generator = EpubGenerator()
        
        print(f"开始处理PDF文件: {args.input}")
        
        # 1. 提取PDF页面为图像
        print("正在提取PDF页面...")
        images = pdf_processor.pdf_to_images(args.input, dpi=args.dpi, page_range=args.page_range)
        
        # 2. 使用Gemini提取文本
        print("正在使用Gemini提取文本...")
        chapters = []
        for i, image_path in enumerate(images):
            print(f"处理页面 {i+1}/{len(images)}")
            text = gemini_client.extract_text(image_path)
            chapters.append({
                'title': f'Page {i+1}',
                'content': text
            })
            # 删除临时图像文件
            os.remove(image_path)
        
        # 3. 生成EPUB文件
        print("正在生成EPUB文件...")
        epub_generator.create_epub(chapters, args.output)
        
        print(f"EPUB文件已生成: {args.output}")
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()