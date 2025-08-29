# PDF转EPUB转换器实现总结

## 项目概述

本项目实现了将拍照PDF转换为EPUB电子书的功能，利用Gemini 2.5系列模型的OCR能力提取文本并保持原有排版。

## 主要功能特性

1. **PDF处理**：使用`pdftoppm`将PDF页面转换为图像
2. **文本提取**：利用Gemini 2.5-flash/2.5-pro模型从图像中提取文本
3. **排版保持**：保持原有PDF的排版和章节结构
4. **EPUB生成**：生成标准EPUB格式电子书（无目录导航文件）
5. **智能换行处理**：将视觉换行合并为逻辑段落
6. **格式保持**：记录并保持原始文档格式（标题层级、文本对齐等）
7. **处理模式**：支持富文本和纯文本两种处理模式
8. **自动重试机制**：处理Gemini API调用失败，最多重试3次
9. **处理时间统计**：实时显示各步骤耗时和预计完成时间
10. **自定义代理**：支持配置自定义Gemini API代理URL
11. **章节合并**：按实际章节结构组织内容，而非按页面分割
12. **目录页面检测**：自动识别并跳过PDF中的目录页面
13. **分批处理**：支持大文件的分批处理，可设置批次大小
14. **断点续传**：支持中断后从上次停止位置继续处理
15. **进度管理**：自动保存和恢复处理进度

## 技术实现

### 核心组件

1. **PDF处理器** (`src/processors/pdf_processor.py`)
   - 使用`pdfinfo`获取PDF文档信息
   - 使用`pdftoppm`将PDF页面转换为PNG图像

2. **Gemini API客户端** (`src/api/gemini_client.py`)
   - 集成自定义的MiniGenAI类
   - 支持文本提取和结构化内容识别
   - 处理图像编码和API调用
   - 指导Gemini将视觉换行合并为逻辑段落
   - 支持富文本结构提取（标题层级、文本对齐等）
   - 识别文档章节结构，支持跨页面章节合并
   - 目录页面智能检测功能

3. **MiniGenAI封装** (`src/api/minigenai.py`)
   - 轻量级Gemini API封装
   - 支持自定义代理URL
   - 提供文本生成、对话和内容生成功能
   - 由Gemini客户端提供自动重试机制

4. **EPUB生成器** (`src/generator/epub_generator.py`)
   - 使用`ebooklib`库生成EPUB文件
   - 创建符合标准的EPUB结构（无导航目录文件）
   - 智能处理段落换行，将视觉换行合并为逻辑段落
   - 支持结构化数据生成，保持原始文档格式
   - 按实际章节结构组织内容，而非按页面分割
   - 支持增量更新，可向现有EPUB添加新章节

5. **进度管理器** (`src/utils/progress_manager.py`)
   - 管理转换进度的保存和恢复
   - 处理临时EPUB文件的创建和管理
   - 支持断点续传功能
   - 自动清理临时文件和进度记录

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
│   ├── utils/
│   │   ├── __init__.py
│   │   └── progress_manager.py
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
- `--title`：EPUB电子书的标题
- `--mode`：处理模式，可选'simple'（纯文本）或'rich'（富文本），默认为'rich'
- `--dpi`：图像DPI，默认为300
- `--model`：使用的Gemini模型，可选'flash'或'pro'，默认为'flash'
- `--base-url`：Gemini API的基础URL，用于指定代理服务器
- `--page-range START END`：处理的页码范围，例如`--page-range 1 10`表示处理第1到10页
- `--batch-size`：批处理大小，每处理多少页保存一次进度，默认为10
- `--resume`：从上次中断的地方继续处理

## 自定义代理URL支持

本项目支持使用自定义的Gemini API代理URL，这对于以下场景非常有用：
- 使用Gemini API的镜像服务
- 本地部署的代理服务器
- 需要通过特定网络路径访问API的情况

通过`--base-url`参数可以轻松指定代理服务器地址。

## 核心技术特性

### 目录页面检测

系统会自动识别并跳过PDF中的目录页面，避免将目录内容转换到EPUB中：

- 使用AI模型分析页面内容和布局
- 识别目录页面的特征（标题、页码、层级结构等）
- 自动跳过检测到的目录页面
- 在出现检测错误时默认继续处理，确保转换不会中断

### 分批处理和断点续传

为了处理大型PDF文件，系统实现了分批处理机制：

**分批处理流程：**
1. 每处理指定数量的页面（默认10页）后保存进度
2. 创建/更新临时EPUB文件，保存已处理内容
3. 记录处理进度到JSON文件
4. 在处理完成后生成最终EPUB文件并清理临时文件

**断点续传机制：**
1. 程序启动时检查是否存在进度文件
2. 验证进度文件的有效性（PDF路径、输出路径、处理模式匹配）
3. 从上次停止的页面继续处理
4. 恢复已处理的章节数据，继续累积新内容

**进度管理：**
- 进度文件包含：已处理页数、总页数、处理模式、章节数据等
- 临时EPUB文件在每批处理后更新
- 支持不同处理模式间的进度隔离
- 异常处理：在出错时保存当前进度状态

### EPUB格式优化

- 移除自动生成的目录导航文件，避免冗余
- 保持原有文档的章节结构和格式层级
- 支持增量更新机制，可向现有EPUB文件添加新章节

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

1. **性能优化**：进一步优化批处理算法和缓存机制
2. **错误处理**：增强异常处理和自动恢复机制
3. **用户体验**：优化进度显示和更详细的日志记录
4. **段落识别优化**：进一步优化复杂文档的段落边界识别
5. **格式识别优化**：提高标题层级和文本对齐的识别准确率
6. **重试机制优化**：支持可配置的重试次数和等待时间
7. **时间统计优化**：提供更详细的时间分析和性能报告
8. **功能扩展**：支持更多输出格式和自定义选项
9. **并发处理**：实现多线程/多进程处理以提高处理速度
10. **智能检测**：改进目录页面和其他特殊页面的检测准确率

## 总结

本项目成功实现了PDF到EPUB的转换功能，具有以下优势：
- 保持原有排版和结构
- 支持自定义API代理
- 模块化设计，易于扩展
- 完整的文档和使用示例
- 轻量级实现，依赖项少
- 智能目录页面检测和跳过功能
- 分批处理和断点续传，适合大文件处理
- 强大的进度管理和恢复机制