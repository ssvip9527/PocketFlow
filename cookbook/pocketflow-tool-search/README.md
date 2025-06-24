# 带有分析功能的网络搜索

一个使用PocketFlow构建的网络搜索工具，它使用SerpAPI执行搜索并使用LLM分析结果。

## 功能

- 通过SerpAPI使用Google进行网络搜索
- 提取标题、摘要和链接
- 使用GPT-4分析搜索结果以提供：
  - 结果摘要
  - 关键点/事实
  - 建议的后续查询
- 简洁的命令行界面

## 安装

1. 克隆仓库
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 设置所需的API密钥：
   ```bash
   export SERPAPI_API_KEY='your-serpapi-key'
   export OPENAI_API_KEY='your-openai-key'
   ```

## 使用

运行搜索工具：
```bash
python main.py
```

您将被提示：
1. 输入您的搜索查询
2. 指定要获取的结果数量（默认：5）

该工具将：
1. 使用SerpAPI执行搜索
2. 使用GPT-4分析结果
3. 展示包含关键点和后续查询的摘要

## 项目结构

```
pocketflow-tool-search/
├── tools/
│   ├── search.py      # SerpAPI搜索功能
│   └── parser.py      # 使用LLM进行结果分析
├── utils/
│   └── call_llm.py    # LLM API封装
├── nodes.py           # PocketFlow节点
├── flow.py           # 流程配置
├── main.py           # 主脚本
└── requirements.txt   # 依赖项
```

## 限制

- 需要SerpAPI订阅
- 受两个API的速率限制
- 基本的错误处理
- 仅限文本结果

## 依赖

- pocketflow: 基于流的处理
- google-search-results: SerpAPI客户端
- openai: GPT-4 API访问
- pyyaml: YAML处理
