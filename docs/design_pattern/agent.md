---
layout: default
title: "代理"
parent: "设计模式"
nav_order: 1
---

# 代理

代理（Agent）是一种强大的设计模式，其中节点可以根据上下文采取动态行动。

<div align="center">
  <img src="https://github.com/the-pocket/.github/raw/main/assets/agent.png?raw=true" width="350"/>
</div>

## 使用图实现代理

1. **上下文和行动**：实现提供上下文并执行行动的节点。
2. **分支**：使用分支将每个行动节点连接到代理节点。使用行动允许代理指导节点之间的[流](../core_abstraction/flow.md)——并可能循环回多步骤。
3. **代理节点**：提供一个提示来决定行动——例如：

```python
f"""
### 上下文
任务：{task_description}
之前的行动：{previous_actions}
当前状态：{current_state}

### 行动空间
[1] 搜索
  描述：使用网络搜索获取结果
  参数：
    - query (str)：要搜索的内容

[2] 回答
  描述：根据结果得出结论
  参数：
    - result (str)：要提供的最终答案

### 下一步行动
根据当前上下文和可用的行动空间决定下一步行动。
以以下格式返回您的响应：

```yaml
thinking: |
    <您的逐步推理过程>
action: <行动名称>
parameters:
    <参数名称>：<参数值>
```"""
```

构建**高性能**和**可靠**代理的核心归结为：

1. **上下文管理**：提供*相关、最小的上下文*。例如，与其包含整个聊天历史记录，不如通过[RAG](./rag.md)检索最相关的。即使上下文窗口更大，LLM 仍然容易受到["中间丢失"](https://arxiv.org/abs/2307.03172)的影响，忽略提示中间的内容。

2. **行动空间**：提供*结构良好且明确*的行动集——避免像单独的 `read_databases` 或 `read_csvs` 这样的重叠。相反，将 CSV 导入数据库。

## 良好行动设计的示例

- **增量**：以可管理的块（500 行或 1 页）而不是一次性地提供内容。

- **概览-深入**：首先提供高级结构（目录、摘要），然后允许深入细节（原始文本）。

- **参数化/可编程**：除了固定行动外，还启用参数化（要选择的列）或可编程（SQL 查询）行动，例如，读取 CSV 文件。

- **回溯**：让代理撤消上一步而不是完全重新开始，在遇到错误或死胡同时保留进度。

## 示例：搜索代理

此代理：
1. 决定是搜索还是回答
2. 如果搜索，则循环回决定是否需要更多搜索
3. 在收集到足够上下文时回答

```python
class DecideAction(Node):
    def prep(self, shared):
        context = shared.get("context", "没有之前的搜索")
        query = shared["query"]
        return query, context
        
    def exec(self, inputs):
        query, context = inputs
        prompt = f"""
给定输入：{query}
之前的搜索结果：{context}
我应该：1) 搜索网络获取更多信息 2) 用当前知识回答
以 yaml 格式输出：
```yaml
action: search/answer
reason: 为什么采取此行动
search_term: 如果行动是搜索，则为搜索短语
```"""
        resp = call_llm(prompt)
        yaml_str = resp.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)
        
        assert isinstance(result, dict)
        assert "action" in result
        assert "reason" in result
        assert result["action"] in ["search", "answer"]
        if result["action"] == "search":
            assert "search_term" in result
        
        return result

    def post(self, shared, prep_res, exec_res):
        if exec_res["action"] == "search":
            shared["search_term"] = exec_res["search_term"]
        return exec_res["action"]

class SearchWeb(Node):
    def prep(self, shared):
        return shared["search_term"]
        
    def exec(self, search_term):
        return search_web(search_term)
    
    def post(self, shared, prep_res, exec_res):
        prev_searches = shared.get("context", [])
        shared["context"] = prev_searches + [
            {"term": shared["search_term"], "result": exec_res}
        ]
        return "decide"
        
class DirectAnswer(Node):
    def prep(self, shared):
        return shared["query"], shared.get("context", "")
        
    def exec(self, inputs):
        query, context = inputs
        return call_llm(f"上下文：{context}\n回答：{query}")

    def post(self, shared, prep_res, exec_res):
       print(f"回答：{exec_res}")
       shared["answer"] = exec_res

# 连接节点
decide = DecideAction()
search = SearchWeb()
answer = DirectAnswer()

decide - "search" >> search
decide - "answer" >> answer
search - "decide" >> decide  # 循环回

flow = Flow(start=decide)
flow.run({"query": "谁获得了 2024 年诺贝尔物理学奖？"})
```
