"""
PDF处理器模块
负责将PDF文件转换为图像
"""

import os
import subprocess
import tempfile
from pathlib import Path


class PDFProcessor:
    def __init__(self):
        pass
    
    def get_pdf_info(self, pdf_path):
        """
        获取PDF文件信息
        
        Args:
            pdf_path (str): PDF文件路径
            
        Returns:
            dict: PDF信息字典
        """
        try:
            result = subprocess.run([
                'pdfinfo', pdf_path
            ], capture_output=True, text=True, check=True)
            
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            return info
        except subprocess.CalledProcessError as e:
            raise Exception(f"无法获取PDF信息: {e}")
    
    def pdf_to_images(self, pdf_path, dpi=200, page_range=None):
        """
        将PDF转换为PNG图像
        
        Args:
            pdf_path (str): PDF文件路径
            dpi (int): 图像DPI
            page_range (tuple): 页码范围 (start_page, end_page)，从1开始计数
            
        Returns:
            list: 图像文件路径列表
        """
        # 获取PDF信息
        pdf_info = self.get_pdf_info(pdf_path)
        total_pages = int(pdf_info.get('Pages', 1))
        
        # 处理页码范围
        if page_range:
            start_page, end_page = page_range
            # 确保页码在有效范围内
            start_page = max(1, min(start_page, total_pages))
            end_page = max(start_page, min(end_page, total_pages))
            print(f"PDF信息: {total_pages} 页，处理范围: {start_page}-{end_page}页")
        else:
            start_page, end_page = 1, total_pages
            print(f"PDF信息: {total_pages} 页")
        
        # 创建临时目录存储图像
        temp_dir = tempfile.mkdtemp()
        
        # 使用pdftoppm转换PDF为图像
        try:
            # 构建命令参数
            cmd = [
                'pdftoppm',
                '-png',
                '-r', str(dpi),
                '-progress'
            ]
            
            # 如果指定了页码范围，添加范围参数
            if page_range:
                cmd.extend(['-f', str(start_page), '-l', str(end_page)])
            
            cmd.extend([pdf_path, os.path.join(temp_dir, 'page')])
            
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"PDF转换失败: {e}")
        
        # 获取生成的图像文件
        image_files = []
        for i in range(start_page, end_page + 1):
            # pdftoppm生成的文件名格式为 page-001.png, page-002.png, ...
            filename = f"page-{i:03d}.png"
            filepath = os.path.join(temp_dir, filename)
            if os.path.exists(filepath):
                image_files.append(filepath)
        
        return image_files