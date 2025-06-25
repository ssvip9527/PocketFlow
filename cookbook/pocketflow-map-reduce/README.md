# 简历资格评估 - MapReduce 示例

这是一个 PocketFlow 示例，演示了如何实现 Map-Reduce 模式来处理和评估简历。

## 特性

- 使用 Map-Reduce 模式读取和处理多个简历文件
- 使用 LLM 和结构化 YAML 输出单独评估每份简历
- 根据特定标准确定候选人是否符合技术职位要求
- 汇总结果以生成资格统计数据和摘要

## 快速开始

1. 安装所需依赖：

```bash
pip install -r requirements.txt
```

2. 将您的 OpenAI API 密钥设置为环境变量：

```bash
export OPENAI_API_KEY=your_api_key_here
```

3. 运行应用程序：

```bash
python main.py
```

## 工作原理

工作流程遵循classical Map-Reduce 模式，包含三个顺序节点：

```mermaid
flowchart LR
    ReadResumes[Map: 读取简历] --> EvaluateResumes[Batch: 评估简历]
    EvaluateResumes --> ReduceResults[Reduce: 汇总结果]
```

每个节点的作用如下：

1. **ReadResumesNode (Map 阶段)**: 从数据目录读取所有简历文件并将其存储在共享数据存储中
2. **EvaluateResumesNode (批处理)**: 使用 LLM 单独处理每份简历，以确定候选人是否符合资格
3. **ReduceResultsNode (Reduce 阶段)**: 汇总评估结果并生成合格候选人的摘要

## 文件

- [`main.py`](./main.py): 运行简历资格评估工作流程的主入口点
- [`flow.py`](./flow.py): 定义连接节点的流程
- [`nodes.py`](./nodes.py): 包含工作流程中每个步骤的节点类
- [`utils.py`](./utils.py): 实用函数，包括 LLM 包装器
- [`requirements.txt`](./requirements.txt): 列出所需依赖项
- [`data/`](./data/): 包含用于评估的示例简历文件的目录

## 示例输出

```
Starting resume qualification processing...

===== Resume Qualification Summary =====
Total candidates evaluated: 5
Qualified candidates: 2 (40.0%)

Qualified candidates:
- Emily Johnson
- John Smith

Detailed evaluation results:
✗ Michael Williams (resume3.txt)
✓ Emily Johnson (resume2.txt)
✗ Lisa Chen (resume4.txt)
✗ Robert Taylor (resume5.txt)
✓ John Smith (resume1.txt)

Resume processing complete!
```