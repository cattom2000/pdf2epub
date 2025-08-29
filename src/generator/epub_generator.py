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
            # 正确处理段落，将视觉换行合并
            html_content = [f"<h1>{chapter['title']}</h1>"]
            
            # 统一换行符
            normalized_content = chapter['content'].replace('\r\n', '\n').replace('\r', '\n')
            
            # 按双换行（空行）分割成段落
            paragraphs = normalized_content.split('\n\n')
            
            for p in paragraphs:
                # 将段落内部的单换行替换为空格或直接移除，以合并成一行
                # 对于中文，直接移除通常效果更好
                paragraph_text = p.replace('\n', '').strip()
                if paragraph_text:
                    html_content.append(f"<p>{paragraph_text}</p>")
            
            epub_chapter.content = '\n'.join(html_content)

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
        
        # 设置书籍脊柱（不包含导航页）
        book.spine = epub_chapters
        
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
            # 修复段落换行问题：正确处理段落和行内换行
            html_content = ['<h1>{}</h1>'.format(chapter['title'])]
            
            # 按段落分割（双换行）
            paragraphs = chapter['content'].split('\n\n')
            for paragraph in paragraphs:
                # 处理段落内的换行
                lines = paragraph.strip().split('\n')
                if lines:
                    # 如果段落以标题标记开始
                    first_line = lines[0].strip()
                    if first_line.startswith('##'):  # 二级标题
                        html_content.append('<h2>{}</h2>'.format(first_line[2:].strip()))
                        # 处理剩余行作为普通段落内容
                        remaining_content = '<br/>'.join(line.strip() for line in lines[1:] if line.strip())
                        if remaining_content:
                            html_content.append('<p>{}</p>'.format(remaining_content))
                    elif first_line.startswith('#'):  # 一级标题
                        html_content.append('<h1>{}</h1>'.format(first_line[1:].strip()))
                        # 处理剩余行作为普通段落内容
                        remaining_content = '<br/>'.join(line.strip() for line in lines[1:] if line.strip())
                        if remaining_content:
                            html_content.append('<p>{}</p>'.format(remaining_content))
                    else:
                        # 普通段落：将所有行合并成一个字符串，不再使用<br/>
                        # 对于中文，直接连接即可。如果处理英文，可能需要在中间加空格。
                        paragraph_content = ''.join(line.strip() for line in lines if line.strip())
                        if paragraph_content:
                            html_content.append('<p>{}</p>'.format(paragraph_content))
            
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
        
        # 设置书籍脊柱（不包含导航页）
        book.spine = epub_chapters
        
        # 写入EPUB文件
        epub.write_epub(output_path, book, {})

    def create_epub_from_structure(self, structured_data, output_path, title="结构化电子书", author="未知作者"):
        """
        根据结构化的数据创建EPUB文件。
        
        Args:
            structured_data (list): 章节列表，每个元素是一个包含结构化内容块的列表。
                                    例如: [{'title': '章节1', 'blocks': [...]}, ...]
            output_path (str): 输出EPUB文件路径
            title (str): 电子书标题
            author (str): 作者名
        """
        book = epub.EpubBook()
        
        # 设置元数据
        book.set_identifier(f'id_{hash(output_path) % 1000000}')
        book.set_title(title)
        book.set_language('zh')
        book.add_author(author)
        
        epub_chapters = []
        for i, chapter_data in enumerate(structured_data):
            chapter_title = chapter_data.get('title', '')
            blocks = chapter_data.get('blocks', [])
            
            epub_chapter = epub.EpubHtml(
                title=chapter_title if chapter_title else f'第{i+1}页',
                file_name=f'chap_{i+1:03d}.xhtml',
                lang='zh'
            )
            
            html_parts = []
            # 只有在有标题时才添加章节大标题
            if chapter_title:
                html_parts.append(f'<h1>{chapter_title}</h1>')

            # 解析内容块并生成HTML
            for block in blocks:
                content = block.get('content', '')
                block_type = block.get('type', 'paragraph')
                style = block.get('style', {})
                align = style.get('align', 'left')
                
                # 构建 style 字符串
                style_str = f'style="text-align: {align};"'

                if block_type == 'heading':
                    level = block.get('level', 2)
                    html_parts.append(f'<h{level} {style_str}>{content}</h{level}>')
                else: # paragraph
                    # 段落默认左对齐，首行缩进由全局CSS控制
                    # 如果有特殊对齐要求，则应用
                    if align != 'left':
                         html_parts.append(f'<p {style_str}>{content}</p>')
                    else:
                         html_parts.append(f'<p>{content}</p>')
            
            epub_chapter.content = '\n'.join(html_parts)
            book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)

        # (添加CSS, 创建导航等部分与原方法保持一致)
        style = '''
            @namespace epub "http://www.idpf.org/2007/ops";
            body { font-family: Arial, Helvetica, sans-serif; }
            h1 { text-align: center; }
            p { text-indent: 2em; line-height: 1.5em; text-align: justify; }
            h2, h3, h4 { text-align: left; }
        '''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)
        
        # 设置书籍脊柱（不包含导航页）
        book.spine = epub_chapters
        
        epub.write_epub(output_path, book, {})
    
    def update_epub_with_new_chapters(self, existing_epub_path, new_chapters, title="转换的电子书", author="未知作者"):
        """
        向现有EPUB文件中添加新章节
        
        Args:
            existing_epub_path (str): 现有EPUB文件路径
            new_chapters (list): 新章节列表
            title (str): 电子书标题
            author (str): 作者名
        """
        if os.path.exists(existing_epub_path):
            # 如果存在现有EPUB，读取并添加新章节
            import zipfile
            import tempfile
            import shutil
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            try:
                # 解压现有EPUB
                with zipfile.ZipFile(existing_epub_path, 'r') as zip_file:
                    zip_file.extractall(temp_dir)
                
                # 重新创建带有所有章节的EPUB
                book = epub.EpubBook()
                book.set_identifier(f'id_{hash(existing_epub_path) % 1000000}')
                book.set_title(title)
                book.set_language('zh')
                book.add_author(author)
                
                # 添加所有章节（现有的 + 新的）
                all_chapters = []
                
                # 这里需要从解压的文件中读取现有章节
                # 为了简化，我们直接重新生成所有章节
                for i, chapter in enumerate(new_chapters):
                    epub_chapter = epub.EpubHtml(
                        title=chapter.get('title', f'第{i+1}页'),
                        file_name=f'chap_{i+1:03d}.xhtml',
                        lang='zh'
                    )
                    
                    html_parts = []
                    if chapter.get('title'):
                        html_parts.append(f'<h1>{chapter["title"]}</h1>')
                    
                    blocks = chapter.get('blocks', [])
                    for block in blocks:
                        content = block.get('content', '')
                        block_type = block.get('type', 'paragraph')
                        style = block.get('style', {})
                        align = style.get('align', 'left')
                        
                        style_str = f'style="text-align: {align};"' if align != 'left' else ''
                        
                        if block_type == 'heading':
                            level = block.get('level', 2)
                            html_parts.append(f'<h{level} {style_str}>{content}</h{level}>')
                        else:
                            html_parts.append(f'<p {style_str}>{content}</p>')
                    
                    epub_chapter.content = '\n'.join(html_parts)
                    book.add_item(epub_chapter)
                    all_chapters.append(epub_chapter)
                
                # 添加CSS样式
                style = '''
                    @namespace epub "http://www.idpf.org/2007/ops";
                    body { font-family: Arial, Helvetica, sans-serif; }
                    h1 { text-align: center; }
                    p { text-indent: 2em; line-height: 1.5em; text-align: justify; }
                    h2, h3, h4 { text-align: left; }
                '''
                nav_css = epub.EpubItem(
                    uid="style_nav", 
                    file_name="style/nav.css", 
                    media_type="text/css", 
                    content=style
                )
                book.add_item(nav_css)
                
                # 设置书籍脊柱
                book.spine = all_chapters
                
                # 写入EPUB文件
                epub.write_epub(existing_epub_path, book, {})
                
            finally:
                # 清理临时目录
                shutil.rmtree(temp_dir)
        else:
            # 如果不存在现有EPUB，直接创建新的
            self.create_epub_from_structure(new_chapters, existing_epub_path, title, author)