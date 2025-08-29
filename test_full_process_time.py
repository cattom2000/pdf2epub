#!/usr/bin/env python3
"""
模拟主程序处理流程的时间统计
"""

import sys
import os
import time

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import format_time


def simulate_processing():
    """模拟处理流程"""
    print("开始处理PDF文件: test.pdf")
    
    # 1. PDF页面提取
    print("正在提取PDF页面...")
    pdf_start = time.time()
    time.sleep(0.1)  # 模拟处理时间
    pdf_end = time.time()
    pdf_duration = pdf_end - pdf_start
    print(f"PDF页面提取完成，耗时: {format_time(pdf_duration)}")
    
    # 2. 文本提取
    print("正在使用Gemini提取文本...")
    text_start = time.time()
    
    # 模拟处理多个页面
    total_pages = 5
    processed_pages = 0
    page_times = []
    
    for i in range(total_pages):
        page_start = time.time()
        print(f"处理页面 {i+1}/{total_pages}")
        
        # 模拟页面处理时间
        time.sleep(0.05 + (i * 0.01))  # 每个页面稍微长一点
        
        page_end = time.time()
        page_duration = page_end - page_start
        page_times.append(page_duration)
        processed_pages += 1
        
        # 计算预计剩余时间
        if page_times:
            avg_time = sum(page_times) / len(page_times)
            remaining_pages = total_pages - processed_pages
            estimated_remaining = avg_time * remaining_pages
            
            print(f"页面 {i+1} 处理完成，耗时: {format_time(page_duration)}")
            if remaining_pages > 0:
                print(f"预计剩余时间: {format_time(estimated_remaining)} ({remaining_pages} 页)")
    
    text_end = time.time()
    text_duration = text_end - text_start
    print(f"Gemini文本提取完成，总耗时: {format_time(text_duration)}")
    
    # 3. EPUB生成
    print("正在生成EPUB文件...")
    epub_start = time.time()
    time.sleep(0.05)  # 模拟处理时间
    epub_end = time.time()
    epub_duration = epub_end - epub_start
    print(f"EPUB文件生成完成，耗时: {format_time(epub_duration)}")
    
    # 总结
    total_duration = pdf_duration + text_duration + epub_duration
    print(f"EPUB文件已生成: test.epub")
    print(f"总处理时间: {format_time(total_duration)}")


if __name__ == '__main__':
    simulate_processing()