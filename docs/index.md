---
layout: default
title: "主页"
nav_order: 1
---

# Pocket Flow

一个 [100 行](https://github.com/the-pocket/PocketFlow/blob/main/pocketflow/__init__.py) 的极简 LLM 框架，用于*智能体、任务分解、RAG 等*。

- **轻量级**：核心图抽象仅 100 行。零依赖，无厂商锁定。
- **富有表现力**：包含您喜爱的大型框架中的所有功能——（[多智能体](./design_pattern/multi_agent.html)）[智能体](./design_pattern/agent.html)、[工作流](./design_pattern/workflow.html)、[RAG](./design_pattern/rag.html) 等。
- **智能体编程**：足够直观，可供 AI 智能体帮助人类构建复杂的 LLM 应用程序。

<div align="center">
  <img src="https://github.com/the-pocket/.github/raw/main/assets/meme.jpg?raw=true" alt="Pocket Flow – 100-line minimalist LLM framework" width="400"/>
</div>


## 核心抽象

我们将 LLM 工作流建模为**图 + 共享存储**：

- [节点](./core_abstraction/node.md) 处理简单的 (LLM) 任务。
- [流](./core_abstraction/flow.md) 通过**动作**（带标签的边）连接节点。
- [共享存储](./core_abstraction/communication.md) 允许流内节点之间的通信。
- [批处理](./core_abstraction/batch.md) 节点/流允许数据密集型任务。
- [异步](./core_abstraction/async.md) 节点/流允许等待异步任务。
- [（高级）并行](./core_abstraction/parallel.md) 节点/流处理 I/O 密集型任务。

<div align="center">
  <img src="https://github.com/the-pocket/.github/raw/main/assets/abstraction.png" alt="Pocket Flow – Core Abstraction" width="700"/>
</div>

## 设计模式

在此基础上，可以轻松实现流行的设计模式：

- [智能体](./design_pattern/agent.md) 自主做出决策。
- [工作流](./design_pattern/workflow.md) 将多个任务串联成管道。
- [RAG](./design_pattern/rag.md) 将数据检索与生成集成。
- [Map Reduce](./design_pattern/mapreduce.md) 将数据任务分解为 Map 和 Reduce 步骤。
- [结构化输出](./design_pattern/structure.md) 格式化输出以保持一致性。
- [（高级）多智能体](./design_pattern/multi_agent.md) 协调多个智能体。

<div align="center">
  <img src="https://github.com/the-pocket/.github/raw/main/assets/design.png" alt="Pocket Flow – Design Pattern" width="700"/>
</div>

## 实用函数

我们**不**提供内置实用程序。相反，我们提供*示例*——请*自行实现*：

- [LLM 封装器](./utility_function/llm.md)
- [可视化与调试](./utility_function/viz.md)
- [网络搜索](./utility_function/websearch.md)
- [分块](./utility_function/chunking.md)
- [嵌入](./utility_function/embedding.md)
- [向量数据库](./utility_function/vector.md)
- [文本转语音](./utility_function/text_to_speech.md)

**为什么不内置？**：我认为在通用框架中使用特定于供应商的 API 是一种*不良实践*：
- *API 不稳定性*：频繁的更改导致硬编码 API 的维护成本高昂。
- *灵活性*：您可能希望切换供应商、使用微调模型或在本地运行它们。
- *优化*：在没有供应商锁定的情况下，提示缓存、批处理和流式传输更容易实现。

## 准备好构建您的应用程序了吗？

查看 [智能体编程指南](./guide.md)，这是使用 Pocket Flow 开发 LLM 项目的最快方式！
