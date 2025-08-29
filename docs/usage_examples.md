# 使用示例

## 1. 环境准备

```bash
# 克隆或下载项目
git clone <repository-url>
cd pdf2epub

# 安装系统依赖
sudo apt-get install poppler-utils

# 安装Python依赖
pip install -r requirements.txt

# 设置Gemini API密钥
export GEMINI_API_KEY=your_actual_api_key_here
```

## 2. 测试MiniGenAI功能

在使用转换器之前，建议先测试MiniGenAI功能：

```bash
# 基本测试
python test_minigenai.py

# 指定模型测试
python test_minigenai.py --model gemini-2.5-pro

# 使用自定义代理URL测试
python test_minigenai.py --model gemini-2.5-flash --base-url https://your-gemini-proxy.com
```

## 2. 基本使用

```bash
# 转换PDF到EPUB（默认富文本模式）
python src/main.py --input /path/to/your/book.pdf --output /path/to/output/book.epub

# 指定电子书标题
python src/main.py --input /path/to/your/book.pdf --output /path/to/output/book.epub --title "我的电子书"

# 使用纯文本模式
python src/main.py --input /path/to/your/book.pdf --output /path/to/output/book.epub --mode simple

# 使用富文本模式（保持原始格式）
python src/main.py --input /path/to/your/book.pdf --output /path/to/output/book.epub --mode rich

# 使用更高DPI以获得更好的OCR效果
python src/main.py --input /path/to/your/book.pdf --output /path/to/output/book.epub --dpi 300

# 使用Gemini 2.5-pro模型（如果可用）
python src/main.py --input /path/to/your/book.pdf --output /path/to/output/book.epub --model pro
```

## 3. 高级选项

### 3.1 批处理多个文件

```bash
#!/bin/bash
# batch_convert.sh

INPUT_DIR="/path/to/pdf/files"
OUTPUT_DIR="/path/to/epub/files"

for pdf_file in "$INPUT_DIR"/*.pdf; do
    filename=$(basename "$pdf_file" .pdf)
    echo "Processing $filename..."
    python src/main.py --input "$pdf_file" --output "$OUTPUT_DIR/${filename}.epub"
done
```

### 3.2 自定义处理参数

```bash
# 对于低质量扫描，使用较低DPI以减少处理时间
python src/main.py --input book.pdf --output book.epub --dpi 150

# 对于高质量扫描，使用较高DPI以获得更好的OCR效果
python src/main.py --input book.pdf --output book.epub --dpi 300

# 只处理PDF的前10页
python src/main.py --input book.pdf --output book.epub --page-range 1 10

# 处理PDF的第50到100页
python src/main.py --input book.pdf --output book.epub --page-range 50 100
```

## 3.3 处理时间监控

程序会自动显示处理时间统计和预计完成时间：

```
开始处理PDF文件: book.pdf
正在提取PDF页面...
PDF页面提取完成，耗时: 2.1秒
正在使用Gemini提取文本...
处理页面 1/50
页面 1 处理完成，耗时: 6.8秒
预计剩余时间: 5.7分钟 (49 页)
...
```

## 4. 故障排除

### 4.1 常见错误

1. **API密钥错误**
   ```
   Error: API key not set
   ```
   解决方案：确保已正确设置GEMINI_API_KEY环境变量

2. **PDF处理错误**
   ```
   Error: Cannot process PDF file
   ```
   解决方案：检查PDF文件是否损坏，确认已安装poppler-utils

3. **内存不足错误**
   ```
   Error: Out of memory
   ```
   解决方案：降低DPI参数，或分批处理大文件

4. **Gemini API调用失败**
   ```
   Error: 文本提取失败，已重试 3 次
   ```
   解决方案：检查网络连接，确认API密钥有效，稍后重试

### 4.2 段落处理问题

如果生成的EPUB文件中段落格式不正确，请检查：

1. 确认PDF文件质量良好，OCR识别准确
2. Gemini模型可能未能正确识别段落边界
3. 对于复杂排版的文档，可能需要手动调整

### 4.3 处理模式选择问题

如果生成的EPUB文件格式不符合预期，请尝试切换处理模式：

1. **富文本模式问题**：如果标题层级或文本对齐不正确，可能是Gemini模型未能正确识别结构
   - 解决方案：尝试使用纯文本模式 (`--mode simple`)

2. **纯文本模式问题**：如果缺少标题层级信息，可能需要使用富文本模式
   - 解决方案：使用富文本模式 (`--mode rich`)

3. **标题提取问题**：如果章节标题不正确，检查PDF文件中的标题格式
   - 解决方案：确保原始文档中有清晰的标题标识

### 4.4 性能优化建议

1. 对于大文件，考虑先分割PDF再处理：
   ```bash
   # 使用pdfseparate分割PDF
   pdfseparate large_book.pdf chunk_%d.pdf
   ```

2. 监控API使用量，避免超出配额限制

3. 对于重复处理相同文件，实现缓存机制以避免重复OCR