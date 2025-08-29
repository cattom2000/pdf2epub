"""
进度管理器模块
负责保存和恢复转换进度
"""

import json
import os
from pathlib import Path


class ProgressManager:
    def __init__(self, pdf_path, output_path):
        """
        初始化进度管理器
        
        Args:
            pdf_path (str): PDF文件路径
            output_path (str): 输出EPUB文件路径
        """
        self.pdf_path = pdf_path
        self.output_path = output_path
        
        # 生成进度文件路径
        pdf_name = Path(pdf_path).stem
        output_dir = Path(output_path).parent
        self.progress_file = output_dir / f"{pdf_name}_progress.json"
        
        # 临时EPUB文件路径
        self.temp_epub_path = output_dir / f"{pdf_name}_temp.epub"
    
    def save_progress(self, processed_pages, total_pages, processed_chapters, mode, **kwargs):
        """
        保存当前进度
        
        Args:
            processed_pages (int): 已处理页数
            total_pages (int): 总页数
            processed_chapters (list): 已处理的章节数据
            mode (str): 处理模式 ('rich' 或 'simple')
            **kwargs: 其他需要保存的参数
        """
        progress_data = {
            'pdf_path': self.pdf_path,
            'output_path': self.output_path,
            'processed_pages': processed_pages,
            'total_pages': total_pages,
            'mode': mode,
            'processed_chapters': processed_chapters,
            'temp_epub_path': str(self.temp_epub_path),
            **kwargs
        }
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        
        print(f"进度已保存: {processed_pages}/{total_pages} 页")
    
    def load_progress(self):
        """
        加载之前的进度
        
        Returns:
            dict: 进度数据，如果没有进度文件返回None
        """
        if not self.progress_file.exists():
            return None
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            # 验证进度文件有效性
            if (progress_data.get('pdf_path') == self.pdf_path and 
                progress_data.get('output_path') == self.output_path):
                print(f"找到之前的进度: {progress_data.get('processed_pages', 0)}/{progress_data.get('total_pages', 0)} 页")
                return progress_data
            else:
                print("进度文件与当前任务不匹配，将重新开始")
                return None
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"进度文件损坏，将重新开始: {e}")
            return None
    
    def cleanup_temp_files(self):
        """
        清理临时文件
        """
        if self.progress_file.exists():
            os.remove(self.progress_file)
            print("已清理进度文件")
        
        if self.temp_epub_path.exists():
            os.remove(self.temp_epub_path)
            print("已清理临时EPUB文件")
    
    def get_temp_epub_path(self):
        """
        获取临时EPUB文件路径
        
        Returns:
            str: 临时EPUB文件路径
        """
        return str(self.temp_epub_path)
    
    def has_temp_epub(self):
        """
        检查是否存在临时EPUB文件
        
        Returns:
            bool: 是否存在临时EPUB文件
        """
        return self.temp_epub_path.exists()
    
    def finalize_epub(self):
        """
        将临时EPUB文件重命名为最终文件
        """
        if self.temp_epub_path.exists():
            # 如果目标文件已存在，先删除
            if Path(self.output_path).exists():
                os.remove(self.output_path)
            
            # 重命名临时文件
            os.rename(self.temp_epub_path, self.output_path)
            print(f"EPUB文件已完成: {self.output_path}")
        
        # 清理进度文件
        if self.progress_file.exists():
            os.remove(self.progress_file)