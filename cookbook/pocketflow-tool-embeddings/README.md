# 使用 PocketFlow 的 OpenAI 嵌入

本示例演示了如何将 OpenAI 的文本嵌入 API 与 PocketFlow 正确集成，重点关注：

1. 清晰的代码组织和关注点分离：
   - 用于 API 交互的工具层 (`tools/embeddings.py`)
   - 用于 PocketFlow 集成的节点实现 (`nodes.py`)
   - 流程配置 (`flow.py`)
   - 集中式环境配置 (`utils/call_llm.py`)

2. API 密钥管理的最佳实践：
   - 使用环境变量
   - 支持 `.env` 文件和系统环境变量
   - 安全配置处理

3. 适当的项目结构：
   - 模块化代码组织
   - 工具和 PocketFlow 组件之间的清晰分离
   - 可重用的 OpenAI 客户端配置

## 项目结构

```
pocketflow-tool-embeddings/
├── tools/
│   └── embeddings.py     # OpenAI 嵌入 API 封装
├── utils/
│   └── call_llm.py      # 集中式 OpenAI 客户端配置
├── nodes.py             # PocketFlow 节点实现
├── flow.py             # 流程配置
└── main.py             # 示例用法
```

## 设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # 在 Windows 上：venv\Scripts\activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 通过以下两种方式之一设置您的 OpenAI API 密钥：
   
   a. 使用 `.env` 文件：
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```
   
   b. 或者作为系统环境变量：
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## 使用方法

运行示例：
```bash
python main.py
```

这将：
1. 从环境中加载 OpenAI API 密钥
2. 创建一个 PocketFlow 节点来处理嵌入生成
3. 处理示例文本并生成其嵌入
4. 显示嵌入维度和前几个值

## 演示的关键概念

1. **环境配置**
   - 安全的 API 密钥处理
   - 灵活的配置选项

2. **代码组织**
   - 工具和 PocketFlow 组件之间的清晰分离
   - 可重用的 OpenAI 客户端配置
   - 模块化项目结构

3. **PocketFlow 集成**
   - 具有 prep->exec->post 生命周期的节点实现
   - 流程配置
   - 共享存储用于数据传递