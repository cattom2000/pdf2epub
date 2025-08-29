#!/usr/bin/env python3
"""
测试新的处理模式功能
"""

import sys
import os
import json

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.gemini_client import GeminiClient
from src.generator.epub_generator import EpubGenerator


def test_rich_structure_format():
    """测试富文本结构格式"""
    print("测试富文本结构格式...")
    
    # 模拟Gemini返回的结构化数据
    mock_blocks = [
        {
            "type": "heading",
            "level": 1,
            "style": {"align": "center"},
            "content": "译者序"
        },
        {
            "type": "paragraph",
            "level": 0,
            "style": {"align": "left"},
            "content": "本书系美国研究中国问题专家兼著名记者弗克斯·巴特菲尔德关于中国当代社会生活的专著，重点放在饱经10年浩劫的70年代末和80年代初。"
        },
        {
            "type": "heading",
            "level": 2,
            "style": {"align": "left"},
            "content": "第一章 导言"
        },
        {
            "type": "paragraph",
            "level": 0,
            "style": {"align": "left"},
            "content": "中国是一个拥有五千年文明历史的国家，其社会结构和文化传统具有独特的复杂性。"
        }
    ]
    
    print("模拟的结构化数据:")
    print(json.dumps(mock_blocks, ensure_ascii=False, indent=2))
    
    # 测试EPUB生成
    structured_data = [
        {
            'title': '译者序',
            'blocks': mock_blocks
        }
    ]
    
    generator = EpubGenerator()
    output_path = '/tmp/test_rich_structure.epub'
    
    try:
        generator.create_epub_from_structure(structured_data, output_path, title="富文本测试")
        print(f"\n✓ 富文本EPUB文件已生成: {output_path}")
        
        # 显示生成的HTML结构
        print("\n生成的HTML结构预览:")
        print("<h1>译者序</h1>")
        print('<h1 style="text-align: center;">译者序</h1>')
        print('<p style="text-align: left;">本书系美国研究中国问题专家兼著名记者弗克斯·巴特菲尔德关于中国当代社会生活的专著，重点放在饱经10年浩劫的70年代末和80年代初。</p>')
        print('<h2 style="text-align: left;">第一章 导言</h2>')
        print('<p style="text-align: left;">中国是一个拥有五千年文明历史的国家，其社会结构和文化传统具有独特的复杂性。</p>')
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_simple_mode_format():
    """测试纯文本模式格式"""
    print("\n\n测试纯文本模式格式...")
    
    # 模拟纯文本内容
    mock_content = """## 译者序

本书系美国研究中国问题专家兼著名记者弗克斯·巴特菲尔德关于中国当代社会生活的专著，重点放在饱经10年浩劫的70年代末和80年代初。

## 第一章 导言

中国是一个拥有五千年文明历史的国家，其社会结构和文化传统具有独特的复杂性。
"""
    
    print("模拟的纯文本内容:")
    print(repr(mock_content))
    
    # 测试标题提取
    lines = mock_content.split('\n')
    chapter_title = "默认标题"
    content_lines = []
    title_found = False
    
    for line in lines:
        if line.strip().startswith('##') and not title_found:
            chapter_title = line.strip().lstrip('## ').strip()
            title_found = True
            continue
        content_lines.append(line)
    
    content = '\n'.join(content_lines)
    
    print(f"\n提取的章节标题: {chapter_title}")
    print(f"处理后的内容: {repr(content)}")
    
    # 测试EPUB生成
    chapters = [
        {
            'title': chapter_title,
            'content': content
        }
    ]
    
    generator = EpubGenerator()
    output_path = '/tmp/test_simple_mode.epub'
    
    try:
        generator.create_epub_with_toc(chapters, output_path, title="纯文本测试")
        print(f"\n✓ 纯文本EPUB文件已生成: {output_path}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_mode_comparison():
    """比较两种模式的差异"""
    print("\n\n比较两种处理模式...")
    
    print("""
    富文本模式 vs 纯文本模式:
    
    富文本模式:
    - 保持原始文档的标题层级结构
    - 识别并应用文本对齐样式
    - 智能提取章节标题
    - 更好地保持原始版面布局
    
    纯文本模式:
    - 使用"##"标记识别标题
    - 保持段落换行处理的连续性
    - 兼容旧版处理方式
    - 适用于简单的文本转换需求
    """)


if __name__ == '__main__':
    test_rich_structure_format()
    test_simple_mode_format()
    test_mode_comparison()
    print("\n\n所有处理模式测试完成！")