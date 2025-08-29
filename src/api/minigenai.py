import requests
import json


class MiniGenAI:
    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate_text(self, model: str, prompt: str, generation_config: dict = None):
        """
        调用文本生成接口
        """
        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        # 修改: 添加 generation_config 支持
        if generation_config:
            payload["generationConfig"] = generation_config

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return data

    def chat(self, model: str, history: list, generation_config: dict = None):
        """
        多轮对话
        """
        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": history}

        # 修改: 添加 generation_config 支持
        if generation_config:
            payload["generationConfig"] = generation_config
            
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return data

    def generate_content(self, model: str, contents: list, generation_config: dict = None):
        """
        生成内容，支持文本、图像以及 generation_config
        """
        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": contents}

        # --- 主要修改点 ---
        # 如果提供了 generation_config，则将其添加到请求体中
        if generation_config:
            # 注意：Google API 的 JSON key 是 camelCase 风格的 "generationConfig"
            payload["generationConfig"] = generation_config
        # --- 修改结束 ---

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        
        # 提取内容时，如果返回的是JSON，它会被包含在"text"字段中
        # 这个逻辑保持不变，因为上层 gemini_client 会处理JSON字符串的解析
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            # 如果没有内容返回，或者结构不符合预期，返回原始数据以供调试
            return data