"""
EPUB生成器模块
负责创建EPUB电子书文件
"""

import os
from ebooklib import epub
from pathlib import Path


class EpubGenerator:
    def __init__(self):
        pass
    
    def create_epub(self, chapters, output_path, title="转换的电子书", author="未知作者"):
        """
        创建EPUB文件
        
        Args:
            chapters (list): 章节列表，每个元素包含'title'和'content'键
            output_path (str): 输出EPUB文件路径
            title (str): 电子书标题
            author (str): 作者名
        """
        # 创建EPUB书籍
        book = epub.EpubBook()
        
        # 设置元数据
        book.set_identifier(f'id_{hash(output_path) % 1000000}')
        book.set_title(title)
        book.set_language('zh')
        book.add_author(author)
        
        # 创建章节
        epub_chapters = []
        for i, chapter in enumerate(chapters):
            # 创建章节
            epub_chapter = epub.EpubHtml(
                title=chapter['title'],
                file_name=f'chap_{i+1:03d}.xhtml',
                lang='zh'
            )
            
            # 设置章节内容
            content = f"""
            <h1>{chapter['title']}</h1>
            <p>{chapter['content'].replace(chr(10), '</p><p>').replace(chr(13), '')}</p>
            """
            epub_chapter.content = content
            
            # 添加章节到书籍
            book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)
        
        # 添加默认CSS样式
        style = '''
            @namespace epub "http://www.idpf.org/2007/ops";
            body { font-family: Arial, Helvetica, sans-serif; }
            h1 { text-align: center; }
            p { text-indent: 2em; }
        '''
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)
        
        # 创建导航
        book.toc = epub_chapters
        
        # 添加基本导航文件
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # 设置书籍脊柱
        book.spine = ['nav'] + epub_chapters
        
        # 写入EPUB文件
        epub.write_epub(output_path, book, {})
    
    def create_epub_with_toc(self, chapters, output_path, title="转换的电子书", author="未知作者"):
        """
        创建带目录的EPUB文件
        
        Args:
            chapters (list): 章节列表，每个元素包含'title'和'content'键
            output_path (str): 输出EPUB文件路径
            title (str): 电子书标题
            author (str): 作者名
        """
        # 创建EPUB书籍
        book = epub.EpubBook()
        
        # 设置元数据
        book.set_identifier(f'id_{hash(output_path) % 1000000}')
        book.set_title(title)
        book.set_language('zh')
        book.add_author(author)
        
        # 创建章节
        epub_chapters = []
        for i, chapter in enumerate(chapters):
            # 创建章节
            epub_chapter = epub.EpubHtml(
                title=chapter['title'],
                file_name=f'chap_{i+1:03d}.xhtml',
                lang='zh'
            )
            
            # 处理内容，识别标题
            content_lines = chapter['content'].split('\n')
            html_content = ['<h1>{}</h1>'.format(chapter['title'])]
            
            for line in content_lines:
                if line.startswith('##'):  # 二级标题
                    html_content.append('<h2>{}</h2>'.format(line[2:].strip()))
                elif line.startswith('#'):  # 一级标题
                    html_content.append('<h1>{}</h1>'.format(line[1:].strip()))
                elif line.strip():  # 普通段落
                    html_content.append('<p>{}</p>'.format(line.strip()))
                else:  # 空行
                    html_content.append('<p><br/></p>')
            
            epub_chapter.content = '\n'.join(html_content)
            
            # 添加章节到书籍
            book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)
        
        # 添加默认CSS样式
        style = '''
            @namespace epub "http://www.idpf.org/2007/ops";
            body { font-family: Arial, Helvetica, sans-serif; }
            h1 { text-align: center; }
            h2 { text-align: left; }
            p { text-indent: 2em; line-height: 1.5em; }
        '''
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)
        
        # 创建导航
        book.toc = epub_chapters
        
        # 添加基本导航文件
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # 设置书籍脊柱
        book.spine = ['nav'] + epub_chapters
        
        # 写入EPUB文件
        epub.write_epub(output_path, book, {})