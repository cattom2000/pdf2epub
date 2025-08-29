"""
Gemini API客户端模块
负责调用Gemini模型提取文本
"""

import os
from PIL import Image
import base64
import json
import time
import sys
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
    
    def extract_text(self, image_path, max_retries=3):
        """
        从图像中提取文本
        
        Args:
            image_path (str): 图像文件路径
            max_retries (int): 最大重试次数
            
        Returns:
            str: 提取的文本内容
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # 构造提示词
                prompt = """
                请准确提取这张图片中的所有文本内容，并将其整理成流畅的文本。
                请遵循以下规则：
                1. 将同一个段落内因排版而断开的行合并成一个连续的段落。不要保留图片中句子中间的视觉换行。
                2. 段落与段落之间用一个双换行符（一个空行）分隔。
                3. 如果有明显的章节或分节标题，请在标题前使用'## '（井号后有一个空格）进行标记。
                4. 只返回提取和整理后的文本内容，不要添加任何额外的注释或说明。
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
                last_exception = e
                if attempt < max_retries - 1:  # 不是最后一次尝试
                    wait_time = 5 + attempt * 5  # 5秒, 10秒, 15秒
                    print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                    print(f"等待 {wait_time} 秒后进行第 {attempt + 2} 次尝试...")
                    time.sleep(wait_time)
                else:
                    print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
        
        raise Exception(f"文本提取失败，已重试 {max_retries} 次: {last_exception}")
    
    def extract_text_with_structure(self, image_path, max_retries=3):
        """
        从图像中提取文本并识别文档结构
        
        Args:
            image_path (str): 图像文件路径
            max_retries (int): 最大重试次数
            
        Returns:
            dict: 包含文本和结构信息的字典
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # 构造提示词
                prompt = """
                请准确提取这张图片中的所有文本内容，并识别文档结构。
                返回JSON格式的结果，包含以下字段：
                - text: 完整的文本内容
                - titles: 标题列表（如果有）
                - paragraphs: 段落数量
                
                保持原有的排版格式，段落之间用双换行符分隔，段落内保持原有的单行换行。
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
                last_exception = e
                if attempt < max_retries - 1:  # 不是最后一次尝试
                    wait_time = 5 + attempt * 5  # 5秒, 10秒, 15秒
                    print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                    print(f"等待 {wait_time} 秒后进行第 {attempt + 2} 次尝试...")
                    time.sleep(wait_time)
                else:
                    print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
        
        raise Exception(f"结构化文本提取失败，已重试 {max_retries} 次: {last_exception}")
    
    def extract_rich_structure(self, image_path, max_retries=3):
        """
        从图像中提取文本并识别丰富的文档结构（如对齐、标题级别等）。
        
        Args:
            image_path (str): 图像文件路径
            max_retries (int): 最大重试次数
            
        Returns:
            list: 包含结构化信息的字典列表
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # 构造新的、要求返回JSON的提示词
                prompt = """
                请详细分析这张图片的版面布局和文本内容。
                将所有识别到的内容转换成一个JSON数组，每个JSON对象代表一个内容块（如标题或段落）。
                每个对象应包含以下字段：
                - "type": 元素类型，可选值为 "heading" (标题) 或 "paragraph" (段落)。
                - "level": 如果类型是 "heading"，此字段表示标题级别（例如：1, 2, 3）。
                - "style": 一个包含样式信息的对象，目前只需支持 "align" 字段，可选值为 "center", "left", "right"。
                - "content": 元素的纯文本内容。请将段落内视觉上的换行合并。

                例如，一个居中的大标题和随后的段落应转换为：
                [
                    {
                        "type": "heading",
                        "level": 1,
                        "style": { "align": "center" },
                        "content": "译者序"
                    },
                    {
                        "type": "paragraph",
                        "level": 0,
                        "style": { "align": "left" },
                        "content": "本书系美国研究中国问题专家兼著名记者弗克斯·巴特菲尔德关于中国当代社会生活的专著，重点放在饱经10年浩劫的70年代末和80年代初。"
                    }
                ]
                请严格按照此JSON格式返回结果，不要添加任何其他说明文字。
                """.strip()
                
                image_base64 = self.encode_image(image_path)
                
                contents = [
                    {"role": "user", "parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}]}
                ]
                
                # 请求模型返回JSON
                response = self.client.generate_content(
                    self.model_name, 
                    contents,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                # MiniGenAI可能直接返回解析好的dict/list，如果不是则需要手动解析
                if isinstance(response, str):
                    # 清理可能的Markdown代码块标记
                    response_text = response.strip().replace('```json', '').replace('```', '').strip()
                    return json.loads(response_text)
                return response # 假设已经是一个list或dict
                
            except Exception as e:
                last_exception = e
                # (重试逻辑保持不变)
                if attempt < max_retries - 1:
                    wait_time = 5 + attempt * 5
                    print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                    print(f"等待 {wait_time} 秒后进行第 {attempt + 2} 次尝试...")
                    time.sleep(wait_time)
                else:
                    print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
        
        raise Exception(f"结构化文本提取失败，已重试 {max_retries} 次: {last_exception}")