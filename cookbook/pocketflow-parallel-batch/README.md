# 并行批量翻译过程

本项目演示了如何使用 PocketFlow 的异步和并行特性（`AsyncFlow`、`AsyncParallelBatchNode`）来并发地将文档翻译成多种语言。

- 更多信息请查看 [Substack 教程](https://pocketflow.substack.com/p/parallel-llm-calls-from-scratch-tutorial)！

## 目标

并行地将 `../../README.md` 翻译成多种语言（中文、西班牙语等），并将每种语言的翻译保存到 `translations/` 目录下的文件中。主要目标是与顺序处理进行时间比较。

## 开始使用

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 设置 API 密钥：
   设置 Anthropic API 密钥的环境变量。
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```
   *（将 `"your-api-key-here"` 替换为您的实际密钥）*
   *（或者，将 `ANTHROPIC_API_KEY=your-api-key-here` 放入 `.env` 文件中）*

3. 验证 API 密钥（可选）：
   使用工具脚本进行快速检查。
   ```bash
   python utils.py
   ```
   *（注意：这需要设置有效的 API 密钥。）*

4. 运行翻译过程：
   ```bash
   python main.py
   ```

## 工作原理

此实现使用 `AsyncParallelBatchNode` 并发处理翻译请求。`TranslateTextNodeParallel`：

1. 准备批次，将源文本与每种目标语言配对。

2. 使用 `async` 操作并发执行所有语言的 LLM 翻译调用。

3. 将翻译后的内容保存到单独的文件中（`translations/README_LANGUAGE.md`）。

这种方法利用 `asyncio` 和并行执行来加速 I/O 密集型任务，例如多次 API 调用。

## 示例输出与比较

运行此并行版本与顺序方法相比，显著减少了总时间：

```
# --- 顺序运行输出 (来自 pocketflow-batch) ---
Starting sequential translation into 8 languages...
Translated Chinese text
...
Translated Korean text
Saved translation to translations/README_CHINESE.md
...
Saved translation to translations/README_KOREAN.md

Total sequential translation time: ~1136 seconds

=== Translation Complete ===
Translations saved to: translations
============================


# --- 并行运行输出 (本示例) ---
Starting parallel translation into 8 languages...
Translated French text
Translated Portuguese text
... # Messages may appear interleaved
Translated Spanish text
Saved translation to translations/README_CHINESE.md
...
Saved translation to translations/README_KOREAN.md

Total parallel translation time: ~209 seconds

=== Translation Complete ===
Translations saved to: translations
============================
```
*（实际时间会因 API 响应速度和系统而异。）*

## 文件

- [`main.py`](./main.py): 实现了并行批量翻译节点和流。
- [`utils.py`](./utils.py): 调用 Anthropic 模型的异步封装。
- [`requirements.txt`](./requirements.txt): 项目依赖（包括 `aiofiles`）。
- [`translations/`](./translations/): 输出目录（自动创建）。
