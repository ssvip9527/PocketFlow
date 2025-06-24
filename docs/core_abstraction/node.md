---
layout: default
title: "节点"
parent: "核心抽象"
nav_order: 1
---

# 节点

**节点（Node）**是最小的构建块。每个节点都有 `prep->exec->post` 三个步骤：

<div align="center">
  <img src="https://github.com/the-pocket/.github/raw/main/assets/node.png?raw=true" width="400"/>
</div>

1. `prep(shared)`
   - 从 `shared` 存储中**读取和预处理数据**。
   - 示例：*查询数据库、读取文件或将数据序列化为字符串*。
   - 返回 `prep_res`，供 `exec()` 和 `post()` 使用。

2. `exec(prep_res)`
   - **执行计算逻辑**，可选择重试和错误处理（见下文）。
   - 示例：*（主要是）LLM 调用、远程 API、工具使用*。
   - ⚠️ 此步骤仅用于计算，**不得**访问 `shared`。
   - ⚠️ 如果启用重试，请确保实现幂等性。
   - 返回 `exec_res`，传递给 `post()`。

3. `post(shared, prep_res, exec_res)`
   - **后处理数据并将其写回** `shared`。
   - 示例：*更新数据库、更改状态、记录结果*。
   - 通过返回一个*字符串*来**决定下一步操作**（如果为 *None*，则 `action = "default"`）。

> **为什么是三步？** 为了强制执行*关注点分离*的原则。数据存储和数据处理是分开操作的。
>
> 所有步骤都是*可选的*。例如，如果您只需要处理数据，则可以只实现 `prep` 和 `post`。
{: .note }

### 容错与重试

您可以通过定义节点时的两个参数来**重试** `exec()`（如果它引发异常）：

- `max_retries` (int)：运行 `exec()` 的最大次数。默认值为 `1`（**不**重试）。
- `wait` (int)：下次重试前等待的时间（单位为**秒**）。默认情况下，`wait=0`（不等待）。
当您遇到 LLM 提供商的速率限制或配额错误并需要退避时，`wait` 会很有帮助。

```python 
my_node = SummarizeFile(max_retries=3, wait=10)
```

当 `exec()` 中发生异常时，节点会自动重试，直到：

- 成功，或者
- 节点已经重试了 `max_retries - 1` 次，并在最后一次尝试中失败。

您可以从 `self.cur_retry` 获取当前重试次数（从 0 开始）。

```python 
class RetryNode(Node):
    def exec(self, prep_res):
        print(f"重试 {self.cur_retry} 次")
        raise Exception("失败")
```

### 优雅降级

要**优雅地处理**异常（在所有重试之后）而不是引发它，请重写：

```python 
def exec_fallback(self, prep_res, exc):
    raise exc
```

默认情况下，它只是重新引发异常。但您可以返回一个回退结果，该结果将成为传递给 `post()` 的 `exec_res`。

### 示例：文件摘要

```python 
class SummarizeFile(Node):
    def prep(self, shared):
        return shared["data"]

    def exec(self, prep_res):
        if not prep_res:
            return "文件内容为空"
        prompt = f"用 10 个词总结这段文本：{prep_res}"
        summary = call_llm(prompt)  # 可能会失败
        return summary

    def exec_fallback(self, prep_res, exc):
        # 提供一个简单的回退，而不是崩溃
        return "处理您的请求时发生错误。"

    def post(self, shared, prep_res, exec_res):
        shared["summary"] = exec_res
        # 不返回任何内容，即返回 "default"

summarize_node = SummarizeFile(max_retries=3)

# node.run() 调用 prep->exec->post
# 如果 exec() 失败，它会重试最多 3 次，然后调用 exec_fallback()
action_result = summarize_node.run(shared)

print("返回的操作：", action_result)  # "default"
print("存储的摘要：", shared["summary"])
```