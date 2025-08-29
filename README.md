# PDF转EPUB转换器

这是一个将拍照PDF转换为EPUB电子书的工具，利用Gemini 2.5系列模型的OCR能力提取文本并保持原有排版。

## 功能特点

- 将PDF页面转换为高质量图像
- 利用Gemini 2.5-flash/2.5-pro提取文本
- 保持原有PDF排版和章节结构
- 生成标准EPUB格式电子书
- 智能处理段落换行，将视觉换行合并为逻辑段落
- 记录并保持原始文档格式（标题层级、文本对齐等）
- 自动重试机制，处理Gemini API调用失败情况
- 实时显示处理时间和预计完成时间
- 支持富文本和纯文本两种处理模式

## 安装依赖

```bash
# 安装系统依赖
sudo apt-get install poppler-utils

# 安装Python依赖
pip install -r requirements.txt
```

## 环境测试

在首次使用之前，建议运行环境测试脚本以确保所有依赖项都已正确安装：

```bash
# 测试基本环境
python test_environment.py

# 测试MiniGenAI功能
python test_minigenai.py --model gemini-2.5-flash

# 测试MiniGenAI功能（使用自定义代理URL）
python test_minigenai.py --model gemini-2.5-flash --base-url https://your-gemini-proxy.com
```

## 使用方法

```bash
# 设置Gemini API密钥
export GEMINI_API_KEY=your_api_key_here

# 运行转换器（处理整个PDF，使用默认设置）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub

# 运行转换器（指定电子书标题）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --title "我的电子书"

# 运行转换器（使用纯文本模式）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --mode simple

# 运行转换器（使用富文本模式，保持原始格式）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --mode rich

# 运行转换器（使用自定义代理URL）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --base-url https://your-gemini-proxy.com

# 运行转换器（只处理指定页码范围）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --page-range 1 10
```

## 自定义代理URL

本项目支持使用自定义的Gemini API代理URL，您可以通过`--base-url`参数指定代理服务器地址。这对于使用Gemini API的镜像服务或本地部署的代理非常有用。

## 配置

在使用之前，需要设置Gemini API密钥：

```bash
export GEMINI_API_KEY=your_api_key_here
```

或者在代码中设置：

```python
import google.generativeai as genai

genai.configure(api_key="your_api_key_here")
```

## 参数说明

- `--input` 或 `-i`：输入PDF文件路径
- `--output` 或 `-o`：输出EPUB文件路径
- `--title`：EPUB电子书的标题
- `--mode`：处理模式，可选'simple'（纯文本）或'rich'（富文本），默认为'rich'
- `--dpi`：图像DPI，默认为300
- `--model`：使用的Gemini模型，可选'flash'或'pro'，默认为'flash'