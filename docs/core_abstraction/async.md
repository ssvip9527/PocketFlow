---
layout: default
title: "(Advanced) Async"
parent: "Core Abstraction"
nav_order: 5
---

# (高级) 异步

**异步**节点实现了 `prep_async()`, `exec_async()`, `exec_fallback_async()` 和/或 `post_async()`。这适用于以下场景:

1. **prep_async()**: 以I/O友好的方式*获取/读取数据(文件、API、数据库)*
2. **exec_async()**: 通常用于异步LLM调用
3. **post_async()**: 用于*等待用户反馈*、*跨多智能体协调*或在`exec_async()`之后执行任何额外的异步步骤

**注意**: `AsyncNode`必须包装在`AsyncFlow`中。`AsyncFlow`也可以包含常规(同步)节点。

### Example

```python
class SummarizeThenVerify(AsyncNode):
    async def prep_async(self, shared):
        # Example: read a file asynchronously
        doc_text = await read_file_async(shared["doc_path"])
        return doc_text

    async def exec_async(self, prep_res):
        # Example: async LLM call
        summary = await call_llm_async(f"Summarize: {prep_res}")
        return summary

    async def post_async(self, shared, prep_res, exec_res):
        # Example: wait for user feedback
        decision = await gather_user_feedback(exec_res)
        if decision == "approve":
            shared["summary"] = exec_res
            return "approve"
        return "deny"

summarize_node = SummarizeThenVerify()
final_node = Finalize()

# Define transitions
summarize_node - "approve" >> final_node
summarize_node - "deny"    >> summarize_node  # retry

flow = AsyncFlow(start=summarize_node)

async def main():
    shared = {"doc_path": "document.txt"}
    await flow.run_async(shared)
    print("Final Summary:", shared.get("summary"))

asyncio.run(main())
```