# PocketFlow FastAPI WebSocket 聊天

使用 PocketFlow、FastAPI 和 WebSocket 实现的实时聊天界面，支持流式 LLM 响应。

<p align="center">
  <img 
    src="./assets/banner.png" width="800"
  />
</p>

## 功能

- **实时流式传输**：LLM 生成 AI 响应时，实时显示打字效果
- **对话记忆**：跨消息维护聊天历史记录
- **现代 UI**：简洁、响应式的聊天界面，采用渐变设计
- **WebSocket 连接**：持久连接，实现即时通信
- **PocketFlow 集成**：使用 PocketFlow `AsyncNode` 和 `AsyncFlow` 进行流式传输

## 如何运行

1. **设置 OpenAI API 密钥：**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用程序：**
   ```bash
   python main.py
   ```

4. **访问 Web UI：**
   在浏览器中打开 `http://localhost:8000`。

## 使用方法

1. **输入消息**：在输入框中输入您的消息
2. **发送**：按 Enter 键或点击发送按钮
3. **观看流式传输**：实时查看 AI 响应的出现
4. **继续聊天**：对话历史记录自动维护

## 文件

- [`main.py`](./main.py)：带有 WebSocket 端点的 FastAPI 应用程序
- [`nodes.py`](./nodes.py)：PocketFlow `StreamingChatNode` 定义
- [`flow.py`](./flow.py)：用于聊天处理的 PocketFlow `AsyncFlow`
- [`utils/stream_llm.py`](./utils/stream_llm.py)：OpenAI 流式传输实用程序
- [`static/index.html`](./static/index.html)：现代聊天界面
- [`requirements.txt`](./requirements.txt)：项目依赖
- [`docs/design.md`](./docs/design.md)：系统设计文档
- [`README.md`](./README.md)：此文件