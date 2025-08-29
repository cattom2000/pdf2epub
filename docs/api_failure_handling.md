# Gemini API调用失败处理

## 重试机制说明

当Gemini API调用失败时，系统会自动进行重试：

1. **第一次失败**：等待5秒后重试
2. **第二次失败**：等待10秒后重试
3. **第三次失败**：终止程序并显示错误信息

## 错误信息示例

当API调用连续失败3次时，程序会输出类似以下的错误信息：

```
处理页面 5/20
第 1 次尝试失败: HTTPConnectionPool(host='generativelanguage.googleapis.com', port=443): Read timed out.
等待 5 秒后进行第 2 次尝试...
第 2 次尝试失败: HTTPConnectionPool(host='generativelanguage.googleapis.com', port=443): Read timed out.
等待 10 秒后进行第 3 次尝试...
第 3 次尝试失败: HTTPConnectionPool(host='generativelanguage.googleapis.com', port=443): Read timed out.
处理页面 5 时发生错误: 文本提取失败，已重试 3 次: HTTPConnectionPool(host='generativelanguage.googleapis.com', port=443): Read timed out.
处理进度: 4/20 页已完成
程序终止。
```

## 处理建议

1. **检查网络连接**：确保网络连接稳定
2. **检查API密钥**：确认GEMINI_API_KEY设置正确
3. **稍后重试**：等待一段时间后再次运行程序
4. **减少并发**：如果处理大量页面，可以考虑分批处理

## 未来改进

计划在后续版本中支持：
- 可配置的重试次数和等待时间
- 断点续传功能
- 更详细的错误日志记录