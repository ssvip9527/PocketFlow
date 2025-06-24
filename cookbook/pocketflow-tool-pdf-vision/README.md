# PocketFlow 工具：PDF 视觉

一个 PocketFlow 示例项目，演示了使用 OpenAI 的 Vision API 进行 PDF 处理，实现 OCR 和文本提取。

## 功能

- 将 PDF 页面转换为图像，同时保持质量和尺寸限制
- 使用 GPT-4 Vision API 从扫描文档中提取文本
- 支持自定义提取提示
- 在提取的文本中保持页面顺序和格式
- 批量处理目录中的多个 PDF 文件

## 安装

1. 克隆仓库
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 将您的 OpenAI API 密钥设置为环境变量：
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## 使用方法

1. 将您的 PDF 文件放入 `pdfs` 目录
2. 运行示例：
   ```bash
   python main.py
   ```
   脚本将处理 `pdfs` 目录中的所有 PDF 文件，并输出每个文件的提取文本。

## 项目结构

```
pocketflow-tool-pdf-vision/
├── pdfs/           # 待处理PDF文件目录
├── tools/
│   ├── pdf.py     # PDF到图像转换
│   └── vision.py  # Vision API集成
├── utils/
│   └── call_llm.py # OpenAI客户端配置
├── nodes.py       # PocketFlow节点
├── flow.py        # 流程配置
└── main.py        # 示例用法
```

## 流程说明

1. **LoadPDFNode**：加载PDF并将页面转换为图像
2. **ExtractTextNode**：使用Vision API处理图像
3. **CombineResultsNode**：合并所有页面提取的文本

## 自定义

您可以通过修改 `shared` 中的提示来自定义提取：

```python
shared = {
    "pdf_path": "your_file.pdf",
    "extraction_prompt": "您的自定义提示"
}
```

## 限制

- 最大PDF页面尺寸：2000px（可在 `tools/pdf.py` 中配置）
- Vision API令牌限制：每次响应1000个令牌
- 图像大小限制：Vision API每个图像20MB

## 许可证

MIT
