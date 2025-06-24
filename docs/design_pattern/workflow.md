---
layout: default
title: "工作流"
parent: "设计模式"
nav_order: 2
---

# 工作流

许多现实世界的任务对于一次 LLM 调用来说过于复杂。解决方案是 **任务分解**：将它们分解成由多个节点组成的 [链](../core_abstraction/flow.md)。

<div align="center">
  <img src="https://github.com/the-pocket/.github/raw/main/assets/workflow.png?raw=true" width="400"/>
</div>

> - 您不希望将每个任务设置得**过于粗糙**，因为它可能*对于一次 LLM 调用来说过于复杂*。
> - 您不希望将每个任务设置得**过于细致**，因为那样*LLM 调用没有足够的上下文*，并且结果*在不同节点之间不一致*。
> 
> 您通常需要多次*迭代*才能找到*最佳点*。如果任务有太多*边缘情况*，请考虑使用 [智能体](./agent.md)。
{: .best-practice }

### 示例：文章撰写

```python
class GenerateOutline(Node):
    def prep(self, shared): return shared["topic"]
    def exec(self, topic): return call_llm(f"为关于 {topic} 的文章创建详细大纲")
    def post(self, shared, prep_res, exec_res): shared["outline"] = exec_res

class WriteSection(Node):
    def prep(self, shared): return shared["outline"]
    def exec(self, outline): return call_llm(f"根据此大纲撰写内容：{outline}")
    def post(self, shared, prep_res, exec_res): shared["draft"] = exec_res

class ReviewAndRefine(Node):
    def prep(self, shared): return shared["draft"]
    def exec(self, draft): return call_llm(f"审查并改进此草稿：{draft}")
    def post(self, shared, prep_res, exec_res): shared["final_article"] = exec_res

# 连接节点
outline = GenerateOutline()
write = WriteSection()
review = ReviewAndRefine()

outline >> write >> review

# 创建并运行流
writing_flow = Flow(start=outline)
shared = {"topic": "AI 安全"}
writing_flow.run(shared)
```

对于*动态情况*，请考虑使用 [智能体](./agent.md)。