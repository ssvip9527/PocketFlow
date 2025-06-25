# PocketFlow 摘要

这是一个实际示例，演示如何使用 PocketFlow 构建一个具有错误处理和重试功能的健壮文本摘要工具。此示例展示了 PocketFlow 在实际应用中的核心概念。

## 特性

- 使用 LLM（大型语言模型）进行文本摘要
- API 失败时自动重试机制（最多 3 次尝试）
- 优雅的错误处理与回退响应
- 使用 PocketFlow 的节点架构实现关注点分离

## 项目结构

```
.
├── docs/          # 文档文件
├── utils/         # 工具函数（LLM API 封装）
├── flow.py        # 包含摘要节点的 PocketFlow 实现
├── main.py        # 主应用程序入口点
└── README.md      # 项目文档
```

## 实现细节

此示例实现了一个简单但健壮的文本摘要工作流：

1. **摘要节点**（`flow.py`）：
   - `prep()`: 从共享存储中检索文本
   - `exec()`: 调用 LLM 将文本总结为 10 个词
   - `exec_fallback()`: 提供优雅的错误处理
   - `post()`: 将摘要存储回共享存储

2. **流程结构**：
   - 用于演示的单节点流程
   - 配置 3 次重试以提高可靠性
   - 使用共享存储进行数据传递

## 设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # 在 Windows 上: venv\Scripts\activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置您的环境：
   - 设置您的 LLM API 密钥（请检查 utils/call_llm.py 进行配置）

4. 运行示例：
```bash
python main.py
```

## 示例用法

此示例包含一段关于 PocketFlow 的示例文本，但您可以修改 `main.py` 来总结您自己的文本：

```python
shared = {"data": "您的文本在此处进行总结..."}
flow.run(shared)
print("摘要:", shared["summary"])
```

## 您将学到什么

此示例演示了几个关键的 PocketFlow 概念：

- **节点架构**：如何使用 prep/exec/post 模式构建 LLM 任务
- **错误处理**：实现重试机制和回退
- **共享存储**：使用共享存储在步骤之间传递数据
- **流程创建**：设置基本的 PocketFlow 工作流

## 额外资源

- [PocketFlow 文档](https://the-pocket.github.io/PocketFlow/)
- [节点概念指南](https://the-pocket.github.io/PocketFlow/node.html)
- [流程设计模式](https://the-pocket.github.io/PocketFlow/flow.html)