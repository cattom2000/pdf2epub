# PDF转EPUB转换器

这是一个将拍照PDF转换为EPUB电子书的工具，利用Gemini 2.5系列模型的OCR能力提取文本并保持原有排版。

## 功能特点

- 将PDF页面转换为高质量图像
- 利用Gemini 2.5-flash/2.5-pro提取文本
- 保持原有PDF排版和章节结构
- 生成标准EPUB格式电子书（不包含目录文件）
- 智能处理段落换行，将视觉换行合并为逻辑段落
- 记录并保持原始文档格式（标题层级、文本对齐等）
- 自动重试机制，处理Gemini API调用失败情况
- 实时显示处理时间和预计完成时间
- 支持富文本和纯文本两种处理模式
- 按实际章节结构组织内容，而非按页面分割
- **自动检测并跳过目录页面**
- **分批处理支持，可中断和恢复转换任务**
- **进度保存，支持断点续传功能**

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

# 基本转换（处理整个PDF，使用默认设置）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub

# 指定电子书标题
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --title "我的电子书"

# 使用纯文本模式
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --mode simple

# 使用富文本模式，保持原始格式（默认）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --mode rich

# 使用自定义代理URL
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --base-url https://your-gemini-proxy.com

# 只处理指定页码范围
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --page-range 1 10

# 设置批处理大小（每处理多少页保存一次进度）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --batch-size 5

# 从上次中断的地方继续处理
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --resume

# 组合使用：自定义批大小并支持断点续传
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --batch-size 10 --resume
```

## 断点续传功能

本工具支持大文件的分批处理和断点续传：

- **分批处理**：每处理指定数量的页面（默认10页）后自动保存进度和临时EPUB文件
- **断点续传**：程序中断后可使用 `--resume` 参数从上次停止的地方继续
- **进度管理**：自动管理进度文件和临时文件，完成后自动清理

### 使用示例

```bash
# 首次运行大文件转换
python src/main.py -i large_book.pdf -o large_book.epub --batch-size 5

# 如果中途中断，继续处理
python src/main.py -i large_book.pdf -o large_book.epub --resume

# 调整批处理大小（推荐5-20页，根据文件大小和网络情况调整）
python src/main.py -i large_book.pdf -o large_book.epub --batch-size 15 --resume
```

## 智能功能

### 目录页面自动跳过

工具会自动识别并跳过PDF中的目录页面，避免将目录内容转换到EPUB中。检测特征包括：

- 页面标题包含"目录"、"Contents"、"Table of Contents"等字样
- 页面包含多个条目，每个条目后面有页码
- 有明显的层级结构（章节编号、缩进等）
- 页面主要由标题和页码组成，而非完整段落

### EPUB格式优化

- 生成的EPUB不包含自动目录导航文件，避免冗余
- 保持原有文档的章节结构和格式
- 支持标题层级（H1-H4）和文本对齐（居中、左对齐、右对齐）

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
- `--base-url`：Gemini API的基础URL（可选，用于指定代理服务器）
- `--page-range`：处理的页码范围，格式为`START END`（例如：`1 10`）
- `--batch-size`：批处理大小，每处理多少页保存一次进度，默认为10
- `--resume`：从上次中断的地方继续处理