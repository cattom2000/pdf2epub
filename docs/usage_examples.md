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
# 转换PDF到EPUB
python src/main.py --input /path/to/your/book.pdf --output /path/to/output/book.epub

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

### 4.2 性能优化建议

1. 对于大文件，考虑先分割PDF再处理：
   ```bash
   # 使用pdfseparate分割PDF
   pdfseparate large_book.pdf chunk_%d.pdf
   ```

2. 监控API使用量，避免超出配额限制

3. 对于重复处理相同文件，实现缓存机制以避免重复OCR