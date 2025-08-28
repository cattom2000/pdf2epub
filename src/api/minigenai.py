import requests
import json


class MiniGenAI:
    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate_text(self, model: str, prompt: str):
        """
        调用文本生成接口
        """
        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        # 取出生成的文本
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return data

    def chat(self, model: str, history: list):
        """
        多轮对话，history 格式类似：
        [
            {"role": "user", "parts": [{"text": "你好"}]},
            {"role": "model", "parts": [{"text": "你好，请问有什么能帮你？"}]}
        ]
        """
        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": history}

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return data

    def generate_content(self, model: str, contents: list):
        """
        生成内容，支持文本和图像
        contents格式示例：
        [
            {
                "role": "user",
                "parts": [
                    {"text": "请描述这张图片"},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": "base64_encoded_image_data"
                        }
                    }
                ]
            }
        ]
        """
        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": contents}

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return data