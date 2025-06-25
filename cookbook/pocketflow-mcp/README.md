# PocketFlow MCP 演示

本项目展示了如何使用 PocketFlow 和模型上下文协议 (MCP) 构建一个执行加法运算的代理。它比较了使用 MCP 和基本函数调用方法的区别。

此实现基于教程：<mcurl name="MCP Simply Explained: Function Calling Rebranded or Genuine Breakthrough?" url="https://zacharyhuang.substack.com/p/mcp-simply-explained-function-calling"></mcurl>

## 特性

- 通过简单的终端界面提供数学运算工具
- 集成模型上下文协议 (MCP)
- 比较 MCP 和直接函数调用
- **简单切换** MCP 和本地函数调用

## 如何运行

1. 设置您的 API 密钥：
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   或者直接在 <mcfile name="utils.py" path="/Users/dreamxyp/Transcend/work_9527/PocketFlow/cookbook/pocketflow-mcp/utils.py"></mcfile> 中更新

2. 安装并运行：
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

## MCP 与函数调用

为了比较这两种方法，此演示提供了不需要 MCP 的本地函数替代方案：

- **通过简单标志切换**：在 <mcfile name="utils.py" path="/Users/dreamxyp/Transcend/work_9527/PocketFlow/cookbook/pocketflow-mcp/utils.py"></mcfile> 顶部设置 `MCP = True` 或 `MCP = False` 以在 MCP 和本地实现之间切换。
- 无需代码更改！应用程序会自动使用：
  - 当 `MCP = True` 时使用 MCP 服务器工具
  - 当 `MCP = False` 时使用本地函数实现

这使您可以在保持相同工作流程的同时，查看两种方法之间的差异。

### 函数调用
- 函数直接嵌入到应用程序代码中
- 每个新工具都需要修改应用程序
- 工具在应用程序本身中定义

### MCP 方法
- 工具存在于单独的 MCP 服务器中
- 所有工具交互的标准协议
- 无需更改代理即可添加新工具
- AI 可以通过一致的接口与工具交互

## 工作原理

```mermaid
flowchart LR
    tools[GetToolsNode] -->|decide| decide[DecideToolNode]
    decide -->|execute| execute[ExecuteToolNode]
```

代理使用 PocketFlow 创建一个工作流程，其中：
1. 它获取用户关于数字的输入
2. 连接到 MCP 服务器进行数学运算（或根据 `MCP` 标志使用本地函数）
3. 返回结果

## 文件

- [`main.py`](./main.py)：使用 PocketFlow 实现加法代理
- [`utils.py`](./utils.py)：用于 API 调用和 MCP 集成的辅助函数
- [`simple_server.py`](./simple_server.py)：提供加法工具的 MCP 服务器
