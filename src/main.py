#!/usr/bin/env python3
"""
PDF转EPUB转换器主程序
"""

import argparse
import os
import sys
import time
from pathlib import Path

# 添加src目录到Python路径
# 假设您的目录结构是:
# main.py
# processors/pdf_processor.py
# api/gemini_client.py
# generator/epub_generator.py
# 如果 main.py 在项目根目录，而模块在 src/ 下，请使用 sys.path.append('src')
# 根据您的实际结构调整
# sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from processors.pdf_processor import PDFProcessor
from api.gemini_client import GeminiClient
from generator.epub_generator import EpubGenerator


def format_time(seconds):
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"

def main():
    parser = argparse.ArgumentParser(description='将PDF转换为EPUB电子书')
    parser.add_argument('--input', '-i', required=True, help='输入PDF文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出EPUB文件路径')
    # --- 新增参数 ---
    parser.add_argument('--title', default='转换的电子书', help='EPUB电子书的标题')
    parser.add_argument('--mode', choices=['simple', 'rich'], default='rich',
                       help='处理模式: simple (纯文本) 或 rich (保留版面结构，默认)')
    # --- 原有参数 ---
    parser.add_argument('--dpi', type=int, default=300, help='图像DPI (建议300以提高识别精度，默认: 300)')
    parser.add_argument('--model', choices=['flash', 'pro'], default='flash', 
                       help='使用的Gemini模型 (默认: flash)')
    parser.add_argument('--base-url', help='Gemini API的基础URL (可选，用于指定代理服务器)')
    parser.add_argument('--page-range', nargs=2, type=int, metavar=('START', 'END'),
                       help='处理的页码范围 (例如: --page-range 1 10 表示处理第1到10页)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"错误: 输入文件 {args.input} 不存在")
        sys.exit(1)
    
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        start_time = time.time()
        
        pdf_processor = PDFProcessor()
        gemini_client = GeminiClient(model_type=args.model, base_url=args.base_url)
        epub_generator = EpubGenerator()
        
        print(f"开始处理PDF文件: {args.input}")
        
        print("正在提取PDF页面...")
        pdf_start_time = time.time()
        images = pdf_processor.pdf_to_images(args.input, dpi=args.dpi, page_range=args.page_range)
        pdf_end_time = time.time()
        print(f"PDF页面提取完成，耗时: {format_time(pdf_end_time - pdf_start_time)}")
        
        # --- 根据模式选择不同的处理流程 ---
        
        if args.mode == 'rich':
            # --- 富文本模式处理流程 ---
            print("正在使用Gemini提取版面结构 (富文本模式)...")
            text_start_time = time.time()
            structured_chapters = []
            current_chapter = None
            total_pages = len(images)
            
            for i, image_path in enumerate(images):
                page_start_time = time.time()
                print(f"处理页面 {i+1}/{total_pages}...")
                
                try:
                    # 1. 调用新的方法获取结构化数据
                    blocks = gemini_client.extract_rich_structure(image_path)
                    
                    # 2. 处理内容块，按章节组织
                    for block in blocks:
                        block_type = block.get('type')
                        block_content = block.get('content', '').strip()
                        
                        # 如果是章节标题（level 1 heading）
                        if block_type == 'heading' and block.get('level') == 1:
                            # 创建新章节
                            chapter_title = block_content
                            current_chapter = {
                                'title': chapter_title,
                                'blocks': []
                            }
                            structured_chapters.append(current_chapter)
                        else:
                            # 如果是普通内容块，添加到当前章节
                            if current_chapter is None:
                                # 如果还没有章节，创建一个默认章节
                                current_chapter = {
                                    'title': '',
                                    'blocks': []
                                }
                                structured_chapters.append(current_chapter)
                            
                            # 将内容块添加到当前章节
                            current_chapter['blocks'].append(block)
                    
                    os.remove(image_path)
                    
                    page_end_time = time.time()
                    print(f"页面 {i+1} 处理完成，耗时: {format_time(page_end_time - page_start_time)}")

                except Exception as e:
                    print(f"处理页面 {i+1} 时发生错误: {str(e)}")
                    sys.exit(1)

            print("正在生成EPUB文件 (富文本模式)...")
            epub_start_time = time.time()
            # 3. 调用新的EPUB生成器方法
            epub_generator.create_epub_from_structure(structured_chapters, args.output, title=args.title)
            epub_end_time = time.time()
            print(f"EPUB文件生成完成，耗时: {format_time(epub_end_time - epub_start_time)}")

        else: # args.mode == 'simple'
            # --- 纯文本模式处理流程 (兼容旧版) ---
            print("正在使用Gemini提取文本 (纯文本模式)...")
            text_start_time = time.time()
            chapters = []
            total_pages = len(images)
            
            for i, image_path in enumerate(images):
                page_start_time = time.time()
                print(f"处理页面 {i+1}/{total_pages}...")
                
                try:
                    text = gemini_client.extract_text(image_path)
                    
                    # 智能提取标题
                    lines = text.split('\n')
                    chapter_title = f"Page {i + 1}" # 默认标题
                    content_lines = []
                    title_found = False
                    for line in lines:
                        if line.strip().startswith('##') and not title_found:
                            chapter_title = line.strip().lstrip('## ').strip()
                            title_found = True
                            continue
                        content_lines.append(line)
                    
                    content = '\n'.join(content_lines)
                    chapters.append({'title': chapter_title, 'content': content})
                    os.remove(image_path)

                    page_end_time = time.time()
                    print(f"页面 {i+1} 处理完成，耗时: {format_time(page_end_time - page_start_time)}")

                except Exception as e:
                    print(f"处理页面 {i+1} 时发生错误: {str(e)}")
                    sys.exit(1)
            
            print("正在生成EPUB文件 (纯文本模式)...")
            epub_start_time = time.time()
            epub_generator.create_epub_with_toc(chapters, args.output, title=args.title)
            epub_end_time = time.time()
            print(f"EPUB文件生成完成，耗时: {format_time(epub_end_time - epub_start_time)}")
        
        total_end_time = time.time()
        print(f"\nEPUB文件已生成: {args.output}")
        print(f"总处理时间: {format_time(total_end_time - start_time)}")
        
    except Exception as e:
        print(f"\n处理过程中发生致命错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()