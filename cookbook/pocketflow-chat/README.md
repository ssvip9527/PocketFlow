#  Simple PocketFlow Chat

一个使用 PocketFlow 和 OpenAI 的 GPT-4o 模型的基本聊天应用程序。

## 特性

- 终端中的对话式聊天界面
- 维护完整的对话历史以提供上下文
- 演示 PocketFlow 节点和流程概念的简单实现

## 运行方式

1. 确保您的 OpenAI API 密钥已设置：
    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    ```
    或者，您可以直接编辑 `utils.py` 文件以包含您的 API 密钥。

2. 安装依赖并运行应用程序：
    ```bash
    pip install -r requirements.txt
    python main.py
    ```

## 工作原理

```mermaid
flowchart LR
    chat[ChatNode] -->|continue| chat
```

聊天应用程序使用：
- 一个带有自循环的 `ChatNode`，它：
  - 在 `prep` 方法中获取用户输入
  - 将完整的对话历史发送给 GPT-4o
  - 将响应添加到对话历史
  - 循环以继续聊天，直到用户输入 'exit'


## 文件

- [`main.py`](./main.py)：ChatNode 和聊天流程的实现
- [`utils.py`](./utils.py)：调用 OpenAI API 的简单封装
 