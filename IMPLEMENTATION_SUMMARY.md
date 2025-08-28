# PDF转EPUB转换器实现总结

## 项目概述

本项目实现了将拍照PDF转换为EPUB电子书的功能，利用Gemini 2.5系列模型的OCR能力提取文本并保持原有排版。

## 主要功能特性

1. **PDF处理**：使用`pdftoppm`将PDF页面转换为图像
2. **文本提取**：利用Gemini 2.5-flash/2.5-pro模型从图像中提取文本
3. **排版保持**：保持原有PDF的排版和章节结构
4. **EPUB生成**：生成标准EPUB格式电子书
5. **自定义代理**：支持配置自定义Gemini API代理URL

## 技术实现

### 核心组件

1. **PDF处理器** (`src/processors/pdf_processor.py`)
   - 使用`pdfinfo`获取PDF文档信息
   - 使用`pdftoppm`将PDF页面转换为PNG图像

2. **Gemini API客户端** (`src/api/gemini_client.py`)
   - 集成自定义的MiniGenAI类
   - 支持文本提取和结构化内容识别
   - 处理图像编码和API调用

3. **MiniGenAI封装** (`src/api/minigenai.py`)
   - 轻量级Gemini API封装
   - 支持自定义代理URL
   - 提供文本生成、对话和内容生成功能

4. **EPUB生成器** (`src/generator/epub_generator.py`)
   - 使用`ebooklib`库生成EPUB文件
   - 创建符合标准的EPUB结构

### 项目结构

```
pdf2epub/
├── src/
│   ├── api/
│   │   ├── gemini_client.py
│   │   └── minigenai.py
│   ├── processors/
│   │   └── pdf_processor.py
│   ├── generator/
│   │   └── epub_generator.py
│   └── main.py
├── docs/
│   └── usage_examples.md
├── requirements.txt
├── README.md
├── LICENSE
└── test_environment.py
```

## 使用方法

### 基本使用

```bash
# 设置Gemini API密钥
export GEMINI_API_KEY=your_api_key_here

# 运行转换器（使用默认Google API）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub

# 运行转换器（使用自定义代理URL）
python src/main.py --input /path/to/input.pdf --output /path/to/output.epub --base-url https://your-gemini-proxy.com
```

### 参数说明

- `--input` 或 `-i`：输入PDF文件路径
- `--output` 或 `-o`：输出EPUB文件路径
- `--dpi`：图像DPI，默认为200
- `--model`：使用的Gemini模型，可选'flash'或'pro'，默认为'flash'
- `--base-url`：Gemini API的基础URL，用于指定代理服务器
- `--page-range START END`：处理的页码范围，例如`--page-range 1 10`表示处理第1到10页

## 自定义代理URL支持

本项目支持使用自定义的Gemini API代理URL，这对于以下场景非常有用：
- 使用Gemini API的镜像服务
- 本地部署的代理服务器
- 需要通过特定网络路径访问API的情况

通过`--base-url`参数可以轻松指定代理服务器地址。

## 依赖项

### 系统依赖
- poppler-utils（pdftoppm, pdfinfo）

### Python依赖
- ebooklib：EPUB生成库
- pillow：图像处理库
- PyPDF2：PDF信息读取
- requests：HTTP请求库

## 测试和验证

项目包含以下测试脚本：
- `test_environment.py`：环境配置测试
- `test_minigenai.py`：MiniGenAI类功能测试，支持模型选择和自定义代理URL

### 测试脚本使用方法

```bash
# 基本测试
python test_minigenai.py

# 指定模型测试
python test_minigenai.py --model gemini-2.5-pro

# 使用自定义代理URL测试
python test_minigenai.py --model gemini-2.5-flash --base-url https://your-gemini-proxy.com
```

## 未来改进方向

1. **性能优化**：实现批量处理和缓存机制
2. **错误处理**：增强异常处理和恢复机制
3. **用户体验**：添加进度显示和日志记录
4. **功能扩展**：支持更多输出格式和自定义选项

## 总结

本项目成功实现了PDF到EPUB的转换功能，具有以下优势：
- 保持原有排版和结构
- 支持自定义API代理
- 模块化设计，易于扩展
- 完整的文档和使用示例
- 轻量级实现，依赖项少