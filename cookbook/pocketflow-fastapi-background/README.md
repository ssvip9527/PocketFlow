# 使用 FastAPI 后台任务和实时进度更新的 PocketFlow

一个演示 PocketFlow 工作流作为 FastAPI 后台任务运行，并通过服务器发送事件 (SSE) 提供实时进度更新的 Web 应用程序。

<p align="center">
  <img 
    src="./assets/banner.png" width="800"
  />
</p>

## 特性

- **现代 Web UI**：简洁的界面，实时进度可视化
- **后台处理**：使用 FastAPI BackgroundTasks 进行非阻塞文章生成
- **服务器发送事件 (SSE)**：无需轮询的实时进度流
- **精细进度**：内容生成期间逐节更新
- **PocketFlow 集成**：三节点工作流（大纲 → 内容 → 样式）

## 如何运行

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 设置您的 OpenAI API 密钥：
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. 运行 FastAPI 服务器：
   ```bash
   python main.py
   ```

4. 访问 Web UI：
   打开浏览器并导航到 `http://localhost:8000`。

5. 使用应用程序：
   - 输入文章主题或点击建议主题
   - 点击“生成文章”开始后台处理
   - 观看带有步骤指示器的实时进度更新
   - 完成后复制最终文章

## 工作原理

该应用程序使用 PocketFlow 定义了一个三步文章生成工作流。FastAPI 处理 Web 请求并管理实时 SSE 通信以进行进度更新。

**PocketFlow 工作流：**

```mermaid
flowchart LR
    A[生成大纲] --> B[撰写内容]
    B --> C[应用样式]
```

1. **`GenerateOutline`**：创建包含最多 3 个部分的结构化大纲
2. **`WriteContent` (BatchNode)**：为每个部分单独撰写内容，并发送进度更新
3. **`ApplyStyle`**：以对话式语气润色文章

**FastAPI 与 SSE 集成：**

- `/start-job` 端点创建一个唯一任务，初始化一个 SSE 队列，并使用 `BackgroundTasks` 调度工作流
- 节点在执行期间向特定任务的 `sse_queue` 发送进度更新
- `/progress/{job_id}` 端点通过服务器发送事件 (Server-Sent Events) 向客户端流式传输实时更新
- Web UI 显示带有动画条、步骤指示器和详细状态消息的进度

**进度更新：**
- 33%：大纲生成完成
- 33-66%：内容撰写（各部分独立更新）
- 66-100%：样式应用
- 100%：文章准备就绪

## 文件

- [`main.py`](./main.py)：带有后台任务和 SSE 端点的 FastAPI 应用程序
- [`flow.py`](./flow.py)：连接三个节点的 PocketFlow 工作流定义
- [`nodes.py`](./nodes.py)：工作流节点（GenerateOutline、WriteContent BatchNode、ApplyStyle）
- [`utils/call_llm.py`](./utils/call_llm.py)：OpenAI LLM 实用函数
- [`static/index.html`](./static/index.html)：带有主题建议的现代任务提交表单
- [`static/progress.html`](./static/progress.html)：实时进度监控与动画