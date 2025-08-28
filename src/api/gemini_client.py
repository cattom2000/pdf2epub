"""
Gemini API客户端模块
负责调用Gemini模型提取文本
"""

import os
from PIL import Image
import base64
import json
from .minigenai import MiniGenAI


class GeminiClient:
    def __init__(self, model_type='flash', base_url=None):
        """
        初始化Gemini客户端
        
        Args:
            model_type (str): 使用的模型类型 ('flash' 或 'pro')
            base_url (str): 可选的基础URL，用于指定代理服务器
        """
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("请设置GEMINI_API_KEY环境变量")
        
        # 初始化MiniGenAI客户端
        self.client = MiniGenAI(api_key, base_url) if base_url else MiniGenAI(api_key)
        
        # 选择模型
        if model_type == 'pro':
            self.model_name = 'gemini-2.5-pro'
        else:
            self.model_name = 'gemini-2.5-flash'
    
    def encode_image(self, image_path):
        """
        将图像编码为base64
        
        Args:
            image_path (str): 图像文件路径
            
        Returns:
            str: base64编码的图像数据
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text(self, image_path):
        """
        从图像中提取文本
        
        Args:
            image_path (str): 图像文件路径
            
        Returns:
            str: 提取的文本内容
        """
        try:
            # 构造提示词
            prompt = """
            请准确提取这张图片中的所有文本内容，并保持原有的排版格式。
            注意识别标题、段落等结构，并在适当位置添加换行符。
            如果有明显的章节标题，请用##标记。
            只返回提取的文本内容，不要添加任何其他说明。
            """.strip()
            
            # 将图像转换为base64
            image_base64 = self.encode_image(image_path)
            
            # 构造包含图像的内容
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
            
            # 调用模型
            response = self.client.generate_content(self.model_name, contents)
            
            return response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)
            
        except Exception as e:
            raise Exception(f"文本提取失败: {e}")
    
    def extract_text_with_structure(self, image_path):
        """
        从图像中提取文本并识别文档结构
        
        Args:
            image_path (str): 图像文件路径
            
        Returns:
            dict: 包含文本和结构信息的字典
        """
        try:
            # 构造提示词
            prompt = """
            请准确提取这张图片中的所有文本内容，并识别文档结构。
            返回JSON格式的结果，包含以下字段：
            - text: 完整的文本内容
            - titles: 标题列表（如果有）
            - paragraphs: 段落数量
            
            保持原有的排版格式，并在适当位置添加换行符。
            """.strip()
            
            # 将图像转换为base64
            image_base64 = self.encode_image(image_path)
            
            # 构造包含图像的内容
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
            
            # 调用模型
            response = self.client.generate_content(self.model_name, contents)
            
            if isinstance(response, str):
                return {
                    'text': response,
                    'titles': [],
                    'paragraphs': 0
                }
            else:
                return {
                    'text': json.dumps(response, ensure_ascii=False),
                    'titles': [],
                    'paragraphs': 0
                }
            
        except Exception as e:
            raise Exception(f"结构化文本提取失败: {e}")