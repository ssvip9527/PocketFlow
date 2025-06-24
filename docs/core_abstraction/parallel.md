---
layout: default
title: "(高级) 并行"
parent: "核心抽象"
nav_order: 6
---

# (高级) 并行

**并行（Parallel）**节点和流允许您**并发**运行多个**异步（Async）**节点和流——例如，同时总结多段文本。这可以通过重叠 I/O 和计算来提高性能。

> 由于 Python 的 GIL，并行节点和流无法真正并行化 CPU 密集型任务（例如，繁重的数值计算）。但是，它们擅长重叠 I/O 密集型工作——例如 LLM 调用、数据库查询、API 请求或文件 I/O。
{: .warning }

> - **确保任务独立**：如果每个项目都依赖于前一个项目的输出，则**不要**并行化。
> 
> - **注意速率限制**：并行调用会**迅速**触发 LLM 服务的速率限制。您可能需要**节流**机制（例如，信号量或睡眠间隔）。
> 
> - **考虑单节点批处理 API**：一些 LLM 提供**批处理推理** API，您可以在一次调用中发送多个提示。这实现起来更复杂，但比启动许多并行请求更高效，并能缓解速率限制。
{: .best-practice }

## AsyncParallelBatchNode

类似于 **AsyncBatchNode**，但在**并行**中运行 `exec_async()`：

```python
class ParallelSummaries(AsyncParallelBatchNode):
    async def prep_async(self, shared):
        # 例如，多段文本
        return shared["texts"]

    async def exec_async(self, text):
        prompt = f"总结：{text}"
        return await call_llm_async(prompt)

    async def post_async(self, shared, prep_res, exec_res_list):
        shared["summary"] = "\n\n".join(exec_res_list)
        return "default"

node = ParallelSummaries()
flow = AsyncFlow(start=node)
```

## AsyncParallelBatchFlow

**BatchFlow** 的并行版本。子流的每次迭代都使用不同的参数**并发**运行：

```python
class SummarizeMultipleFiles(AsyncParallelBatchFlow):
    async def prep_async(self, shared):
        return [{"filename": f} for f in shared["files"]]

sub_flow = AsyncFlow(start=LoadAndSummarizeFile())
parallel_flow = SummarizeMultipleFiles(start=sub_flow)
await parallel_flow.run_async(shared)
```