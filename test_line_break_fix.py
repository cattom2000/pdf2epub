#!/usr/bin/env python3
"""
测试行内换行修复功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from generator.epub_generator import EpubGenerator


def test_line_break_processing():
    """测试行内换行处理功能"""
    print("测试行内换行处理功能...")
    
    # 模拟包含各种换行情况的文本
    test_content = """这是一段连续的文本内容，
应该保持在同一段落内显示。

这是第二个段落，与第一个段落之间应该有明显的分隔。

## 这是一个二级标题
标题后的段落内容也应该正确显示，
保持段落内的换行格式。
"""
    
    chapters = [
        {
            'title': '测试章节',
            'content': test_content
        }
    ]
    
    # 测试EPUB生成
    generator = EpubGenerator()
    output_path = '/tmp/test_line_break.epub'
    
    try:
        generator.create_epub_with_toc(chapters, output_path, title="行内换行测试", author="测试作者")
        print(f"✓ EPUB文件已生成: {output_path}")
        
        # 显示生成的HTML内容
        print("\n生成的HTML内容预览:")
        # 模拟生成过程中的处理
        paragraphs = test_content.split('\n\n')
        for i, paragraph in enumerate(paragraphs):
            lines = paragraph.strip().split('\n')
            if lines and lines[0].strip():
                first_line = lines[0].strip()
                if first_line.startswith('##'):  # 二级标题
                    print(f"  标题: {first_line[2:].strip()}")
                    remaining_content = '<br/>'.join(line.strip() for line in lines[1:] if line.strip())
                    if remaining_content:
                        print(f"  段落内容: {remaining_content}")
                elif first_line.startswith('#'):  # 一级标题
                    print(f"  一级标题: {first_line[1:].strip()}")
                    remaining_content = '<br/>'.join(line.strip() for line in lines[1:] if line.strip())
                    if remaining_content:
                        print(f"  段落内容: {remaining_content}")
                else:
                    # 普通段落
                    paragraph_content = '<br/>'.join(line.strip() for line in lines if line.strip())
                    if paragraph_content:
                        print(f"  段落 {i+1}: {paragraph_content}")
            print()
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    
    return True


def main():
    test_line_break_processing()


if __name__ == '__main__':
    main()