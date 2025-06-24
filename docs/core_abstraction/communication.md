---
layout: default
title: "Communication"
parent: "Core Abstraction"
nav_order: 3
---

# 通信

节点和流通过两种方式**通信**:

1. **共享存储(适用于几乎所有情况)**

   - 一个全局数据结构(通常是内存中的字典)，所有节点都可以读取(`prep()`)和写入(`post()`)。
   - 非常适合数据结果、大内容或多个节点需要的任何东西。
   - 您应该提前设计数据结构并填充它。

   - > **关注点分离:** 在几乎所有情况下都使用`共享存储`来分离*数据模式*和*计算逻辑*! 这种方法既灵活又易于管理，从而产生更可维护的代码。`Params`更像是[批处理](./batch.md)的语法糖。
     {: .best-practice }

2. **参数(仅适用于[批处理](./batch.md))**
   - 每个节点都有一个由**父流**传入的本地、临时`params`字典，用作任务的标识符。参数键和值应为**不可变**。
   - 适用于批处理模式下的文件名或数字ID等标识符。

如果您了解内存管理，可以将**共享存储**视为**堆**(所有函数调用共享)，将**参数**视为**栈**(由调用者分配)。

---

## 1. 共享存储

### 概述

共享存储通常是一个内存中的字典，例如:
```python
shared = {"data": {}, "summary": {}, "config": {...}, ...}
```

它还可以包含本地文件句柄、数据库连接或用于持久化的组合。我们建议根据您的应用程序需求首先确定数据结构或数据库模式。

### 示例

```python
class LoadData(Node):
    def post(self, shared, prep_res, exec_res):
        # We write data to shared store
        shared["data"] = "Some text content"
        return None

class Summarize(Node):
    def prep(self, shared):
        # We read data from shared store
        return shared["data"]

    def exec(self, prep_res):
        # Call LLM to summarize
        prompt = f"Summarize: {prep_res}"
        summary = call_llm(prompt)
        return summary

    def post(self, shared, prep_res, exec_res):
        # We write summary to shared store
        shared["summary"] = exec_res
        return "default"

load_data = LoadData()
summarize = Summarize()
load_data >> summarize
flow = Flow(start=load_data)

shared = {}
flow.run(shared)
```

Here:
- `LoadData` writes to `shared["data"]`.
- `Summarize` reads from `shared["data"]`, summarizes, and writes to `shared["summary"]`.

---

## 2. 参数

**参数**允许您存储*每个节点*或*每个流*的配置，而无需存储在共享存储中。它们是:
- 在节点的运行周期中**不可变**(即，它们在`prep->exec->post`中间不会改变)。
- 通过`set_params()`**设置**。
- 每次父流调用时都会**清除**和更新。

> 只设置最上层的流参数，因为其他参数将被父流覆盖。
> 
> 如果您需要设置子节点参数，请参阅[批处理](./batch.md)。
{: .warning }

通常，**参数**是标识符(例如，文件名、页码)。使用它们来获取您分配的任务或写入共享存储的特定部分。

### 示例

```python
# 1) Create a Node that uses params
class SummarizeFile(Node):
    def prep(self, shared):
        # Access the node's param
        filename = self.params["filename"]
        return shared["data"].get(filename, "")

    def exec(self, prep_res):
        prompt = f"Summarize: {prep_res}"
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        filename = self.params["filename"]
        shared["summary"][filename] = exec_res
        return "default"

# 2) Set params
node = SummarizeFile()

# 3) Set Node params directly (for testing)
node.set_params({"filename": "doc1.txt"})
node.run(shared)

# 4) Create Flow
flow = Flow(start=node)

# 5) Set Flow params (overwrites node params)
flow.set_params({"filename": "doc2.txt"})
flow.run(shared)  # The node summarizes doc2, not doc1
```
