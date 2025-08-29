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
from utils.progress_manager import ProgressManager


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
    parser.add_argument('--batch-size', type=int, default=10,
                       help='批处理大小，每处理多少页保存一次进度 (默认: 10)')
    parser.add_argument('--resume', action='store_true',
                       help='从上次中断的地方继续处理')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"错误: 输入文件 {args.input} 不存在")
        sys.exit(1)
    
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        start_time = time.time()
        
        # 创建进度管理器
        progress_manager = ProgressManager(args.input, args.output)
        
        pdf_processor = PDFProcessor()
        gemini_client = GeminiClient(model_type=args.model, base_url=args.base_url)
        epub_generator = EpubGenerator()
        
        print(f"开始处理PDF文件: {args.input}")
        
        # 检查是否要恢复之前的进度
        progress_data = None
        if args.resume:
            progress_data = progress_manager.load_progress()
        
        if progress_data and progress_data.get('mode') == args.mode:
            # 恢复之前的进度
            print(f"从第 {progress_data['processed_pages']} 页恢复处理...")
            processed_chapters = progress_data['processed_chapters']
            start_page = progress_data['processed_pages'] + 1
            total_pages = progress_data['total_pages']
            
            # 获取剩余的页面
            if args.page_range:
                page_range = (max(start_page, args.page_range[0]), args.page_range[1])
            else:
                page_range = (start_page, total_pages)
            
            if start_page <= total_pages:
                print("正在提取剩余PDF页面...")
                pdf_start_time = time.time()
                images = pdf_processor.pdf_to_images(args.input, dpi=args.dpi, page_range=page_range)
                pdf_end_time = time.time()
                print(f"PDF页面提取完成，耗时: {format_time(pdf_end_time - pdf_start_time)}")
            else:
                print("所有页面已处理完成，正在生成最终EPUB...")
                images = []
        else:
            # 全新开始
            print("正在提取PDF页面...")
            pdf_start_time = time.time()
            images = pdf_processor.pdf_to_images(args.input, dpi=args.dpi, page_range=args.page_range)
            pdf_end_time = time.time()
            print(f"PDF页面提取完成，耗时: {format_time(pdf_end_time - pdf_start_time)}")
            
            processed_chapters = []
            start_page = 1
            if args.page_range:
                start_page = args.page_range[0]
            total_pages = len(images) + start_page - 1
        
        # 根据模式选择处理流程
        if args.mode == 'rich':
            processed_chapters = process_rich_mode_with_batching(
                images, processed_chapters, gemini_client, epub_generator, 
                progress_manager, args, start_page, total_pages
            )
        else:  # simple mode
            processed_chapters = process_simple_mode_with_batching(
                images, processed_chapters, gemini_client, epub_generator,
                progress_manager, args, start_page, total_pages
            )
        
        # 生成最终EPUB文件
        if processed_chapters:
            print("正在生成最终EPUB文件...")
            final_epub_start = time.time()
            
            if progress_manager.has_temp_epub():
                # 如果有临时EPUB文件，将其重命名为最终文件
                progress_manager.finalize_epub()
            else:
                # 直接生成最终文件
                if args.mode == 'rich':
                    epub_generator.create_epub_from_structure(processed_chapters, args.output, title=args.title)
                else:
                    epub_generator.create_epub_with_toc(processed_chapters, args.output, title=args.title)
            
            final_epub_end = time.time()
            print(f"最终EPUB文件生成完成，耗时: {format_time(final_epub_end - final_epub_start)}")
            
            # 清理临时文件
            progress_manager.cleanup_temp_files()
            
            total_end_time = time.time()
            print(f"\nEPUB文件已生成: {args.output}")
            print(f"总处理时间: {format_time(total_end_time - start_time)}")
        else:
            print("没有内容可转换，请检查PDF文件")
        
    except Exception as e:
        print(f"\n处理过程中发生致命错误: {str(e)}")
        sys.exit(1)


def process_rich_mode_with_batching(images, processed_chapters, gemini_client, epub_generator, 
                                  progress_manager, args, start_page, total_pages):
    """富文本模式的分批处理"""
    print("正在使用Gemini提取版面结构 (富文本模式)...")
    text_start_time = time.time()
    
    current_chapter = None
    if processed_chapters:
        # 如果有之前的章节，找到最后一个章节
        current_chapter = processed_chapters[-1] if processed_chapters else None
    
    batch_count = 0
    pages_in_current_batch = 0
    
    for i, image_path in enumerate(images):
        actual_page_num = start_page + i
        page_start_time = time.time()
        print(f"处理页面 {actual_page_num}/{total_pages}...")
        
        try:
            # 检测是否为目录页面
            if gemini_client.is_table_of_contents_page(image_path):
                print(f"检测到目录页面，跳过页面 {actual_page_num}")
                os.remove(image_path)
                continue
            
            # 提取结构化数据
            blocks = gemini_client.extract_rich_structure(image_path)
            
            # 处理内容块，按章节组织
            for block in blocks:
                block_type = block.get('type')
                block_content = block.get('content', '').strip()
                
                # 如果是章节标题（level 1 heading）
                if block_type == 'heading' and block.get('level') == 1:
                    chapter_title = block_content
                    current_chapter = {
                        'title': chapter_title,
                        'blocks': []
                    }
                    processed_chapters.append(current_chapter)
                else:
                    # 如果是普通内容块，添加到当前章节
                    if current_chapter is None:
                        current_chapter = {
                            'title': '',
                            'blocks': []
                        }
                        processed_chapters.append(current_chapter)
                    
                    current_chapter['blocks'].append(block)
            
            os.remove(image_path)
            pages_in_current_batch += 1
            
            page_end_time = time.time()
            print(f"页面 {actual_page_num} 处理完成，耗时: {format_time(page_end_time - page_start_time)}")
            
            # 检查是否达到批处理大小
            if pages_in_current_batch >= args.batch_size:
                batch_count += 1
                print(f"完成第 {batch_count} 批处理，保存进度...")
                
                # 保存进度
                progress_manager.save_progress(
                    processed_pages=actual_page_num,
                    total_pages=total_pages,
                    processed_chapters=processed_chapters,
                    mode='rich',
                    title=args.title
                )
                
                # 创建/更新临时EPUB文件
                temp_epub_path = progress_manager.get_temp_epub_path()
                epub_generator.update_epub_with_new_chapters(
                    temp_epub_path, processed_chapters, title=args.title
                )
                
                pages_in_current_batch = 0
                
        except Exception as e:
            print(f"处理页面 {actual_page_num} 时发生错误: {str(e)}")
            # 保存当前进度
            progress_manager.save_progress(
                processed_pages=actual_page_num - 1,
                total_pages=total_pages,
                processed_chapters=processed_chapters,
                mode='rich',
                title=args.title
            )
            sys.exit(1)
    
    # 保存最终进度
    if pages_in_current_batch > 0:
        progress_manager.save_progress(
            processed_pages=total_pages,
            total_pages=total_pages,
            processed_chapters=processed_chapters,
            mode='rich',
            title=args.title
        )
        
        # 更新临时EPUB文件
        temp_epub_path = progress_manager.get_temp_epub_path()
        epub_generator.update_epub_with_new_chapters(
            temp_epub_path, processed_chapters, title=args.title
        )
    
    text_end_time = time.time()
    print(f"文本提取完成，耗时: {format_time(text_end_time - text_start_time)}")
    
    return processed_chapters


def process_simple_mode_with_batching(images, processed_chapters, gemini_client, epub_generator,
                                    progress_manager, args, start_page, total_pages):
    """纯文本模式的分批处理"""
    print("正在使用Gemini提取文本 (纯文本模式)...")
    text_start_time = time.time()
    
    batch_count = 0
    pages_in_current_batch = 0
    
    for i, image_path in enumerate(images):
        actual_page_num = start_page + i
        page_start_time = time.time()
        print(f"处理页面 {actual_page_num}/{total_pages}...")
        
        try:
            # 检测是否为目录页面
            if gemini_client.is_table_of_contents_page(image_path):
                print(f"检测到目录页面，跳过页面 {actual_page_num}")
                os.remove(image_path)
                continue
            
            text = gemini_client.extract_text(image_path)
            
            # 智能提取标题
            lines = text.split('\n')
            chapter_title = f"Page {actual_page_num}"  # 默认标题
            content_lines = []
            title_found = False
            for line in lines:
                if line.strip().startswith('##') and not title_found:
                    chapter_title = line.strip().lstrip('## ').strip()
                    title_found = True
                    continue
                content_lines.append(line)
            
            content = '\n'.join(content_lines)
            processed_chapters.append({'title': chapter_title, 'content': content})
            os.remove(image_path)
            pages_in_current_batch += 1

            page_end_time = time.time()
            print(f"页面 {actual_page_num} 处理完成，耗时: {format_time(page_end_time - page_start_time)}")
            
            # 检查是否达到批处理大小
            if pages_in_current_batch >= args.batch_size:
                batch_count += 1
                print(f"完成第 {batch_count} 批处理，保存进度...")
                
                # 保存进度
                progress_manager.save_progress(
                    processed_pages=actual_page_num,
                    total_pages=total_pages,
                    processed_chapters=processed_chapters,
                    mode='simple',
                    title=args.title
                )
                
                # 创建/更新临时EPUB文件
                temp_epub_path = progress_manager.get_temp_epub_path()
                epub_generator.create_epub_with_toc(processed_chapters, temp_epub_path, title=args.title)
                
                pages_in_current_batch = 0

        except Exception as e:
            print(f"处理页面 {actual_page_num} 时发生错误: {str(e)}")
            # 保存当前进度
            progress_manager.save_progress(
                processed_pages=actual_page_num - 1,
                total_pages=total_pages,
                processed_chapters=processed_chapters,
                mode='simple',
                title=args.title
            )
            sys.exit(1)
    
    # 保存最终进度
    if pages_in_current_batch > 0:
        progress_manager.save_progress(
            processed_pages=total_pages,
            total_pages=total_pages,
            processed_chapters=processed_chapters,
            mode='simple',
            title=args.title
        )
        
        # 更新临时EPUB文件
        temp_epub_path = progress_manager.get_temp_epub_path()
        epub_generator.create_epub_with_toc(processed_chapters, temp_epub_path, title=args.title)
    
    text_end_time = time.time()
    print(f"文本提取完成，耗时: {format_time(text_end_time - text_start_time)}")
    
    return processed_chapters


if __name__ == '__main__':
    main()