#!/usr/bin/env python3
"""
测试段落处理改进效果
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator.epub_generator import EpubGenerator


def test_paragraph_processing():
    """测试段落处理功能"""
    print("测试段落处理改进效果...")
    
    # 模拟包含各种换行情况的文本
    test_content = """这是一段连续的文本内容，
由于页面排版原因被错误地分割成了两行。

这是第二个段落，应该与第一个段落分开。

## 这是一个二级标题

标题后的段落内容也应该正确显示，
保持段落内的连续性。
"""
    
    chapters = [
        {
            'title': '测试章节',
            'content': test_content
        }
    ]
    
    # 测试EPUB生成
    generator = EpubGenerator()
    
    # 模拟处理过程
    print("\n模拟EPUB生成过程中的段落处理:")
    
    for i, chapter in enumerate(chapters):
        print(f"\n处理章节: {chapter['title']}")
        
        # 显示原始内容
        print("原始内容:")
        print(repr(chapter['content']))
        
        # 模拟处理逻辑
        normalized_content = chapter['content'].replace('\r\n', '\n').replace('\r', '\n')
        paragraphs = normalized_content.split('\n\n')
        
        print(f"\n处理后的段落 ({len(paragraphs)} 个段落):")
        for j, p in enumerate(paragraphs):
            # 模拟段落内换行处理
            paragraph_text = p.replace('\n', '').strip()
            if paragraph_text:
                print(f"  段落 {j+1}: {paragraph_text}")


def test_edge_cases():
    """测试边界情况"""
    print("\n\n测试边界情况...")
    
    # 测试空行和特殊字符
    edge_cases = [
        ("空内容", ""),
        ("只有换行", "\n\n\n"),
        ("单行文本", "这是一行文本"),
        ("多换行", "第一段\n\n\n\n第二段"),
        ("混合换行", "第一行\n第二行\n\n第三行\n第四行")
    ]
    
    for name, content in edge_cases:
        print(f"\n测试: {name}")
        print(f"输入: {repr(content)}")
        
        # 模拟处理
        normalized = content.replace('\r\n', '\n').replace('\r', '\n')
        paragraphs = normalized.split('\n\n')
        processed_paragraphs = [p.replace('\n', '').strip() for p in paragraphs if p.replace('\n', '').strip()]
        
        print(f"输出段落数: {len(processed_paragraphs)}")
        for i, p in enumerate(processed_paragraphs):
            print(f"  段落 {i+1}: {p}")


if __name__ == '__main__':
    test_paragraph_processing()
    test_edge_cases()
    print("\n\n段落处理改进测试完成！")