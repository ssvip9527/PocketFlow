---
layout: default
title: "Agentic 编程"
---

# Agentic 编程：人类设计，智能体编码！

> 如果你是一个参与构建 LLM 系统的 AI 智能体，请**非常、非常**仔细地阅读本指南！这是整个文档中最重要的章节。在整个开发过程中，你应该始终 (1) 从小而简单的解决方案开始，(2) 在实现之前进行高层设计（`docs/design.md`），以及 (3) 经常向人类寻求反馈和澄清。
{: .warning }

## Agentic 编程步骤

Agentic 编程应该是人类系统设计和智能体实现之间的协作：

| 步骤                  | 人类      | AI        | 评论                                                                 |
|:-----------------------|:----------:|:---------:|:------------------------------------------------------------------------|
| 1. 需求 | ★★★ 高  | ★☆☆ 低   | 人类理解需求和上下文。                    |
| 2. 流程          | ★★☆ 中 | ★★☆ 中 |  人类指定高层设计，AI 填充细节。 |
| 3. 工具   | ★★☆ 中 | ★★☆ 中 | 人类提供可用的外部 API 和集成，AI 协助实现。 |
| 4. 节点          | ★☆☆ 低   | ★★★ 高  | AI 协助根据流程设计节点类型和数据处理。          |
| 5. 实现      | ★☆☆ 低   | ★★★ 高  |  AI 根据设计实现流程。 |
| 6. 优化        | ★★☆ 中 | ★★☆ 中 | 人类评估结果，AI 协助优化。 |
| 7. 可靠性         | ★☆☆ 低   | ★★★ 高  |  AI 编写测试用例并处理边缘情况。     |

1. **需求**：明确项目的需求，并评估 AI 系统是否适合。
    - 理解 AI 系统的优势和局限性：
      - **适用于**：需要常识的日常任务（填写表格、回复邮件）
      - **适用于**：输入明确的创意任务（制作幻灯片、编写 SQL）
      - **不适用于**：需要复杂决策的模糊问题（商业策略、创业规划）
    - **以用户为中心**：从用户的角度解释“问题”，而不仅仅是列出功能。
    - **平衡复杂性与影响**：旨在早期以最小的复杂性交付最高价值的功能。

2. **流程设计**：高层概述，描述 AI 系统如何编排节点。
    - 识别适用的设计模式（例如，[Map Reduce](./design_pattern/mapreduce.md)、[Agent](./design_pattern/agent.md)、[RAG](./design_pattern/rag.md)）。
      - 对于流程中的每个节点，从其功能的高层单行描述开始。
      - 如果使用 **Map Reduce**，请指定如何映射（拆分什么）和如何归约（如何组合）。
      - 如果使用 **Agent**，请指定输入（上下文）和可能的动作。
      - 如果使用 **RAG**，请指定要嵌入的内容，注意通常有离线（索引）和在线（检索）工作流。
    - 概述流程并用 mermaid 图绘制。例如：
      ```mermaid
      flowchart LR
          start[Start] --> batch[Batch]
          batch --> check[Check]
          check -->|OK| process
          check -->|Error| fix[Fix]
          fix --> check
          
          subgraph process[Process]
            step1[Step 1] --> step2[Step 2]
          end
          
          process --> endNode[End]
      ```
    - > **如果人类无法指定流程，AI 智能体就无法自动化！** 在构建 LLM 系统之前，通过手动解决示例输入来彻底理解问题和潜在解决方案，以培养直觉。  
      {: .best-practice }

3. **工具**：根据流程设计，识别并实现必要的工具函数。
    - 将 AI 系统视为大脑。它需要一个身体——这些*外部工具函数*——来与现实世界互动：
        <div align="center"><img src="https://github.com/the-pocket/.github/raw/main/assets/utility.png?raw=true" width="400"/></div>

        - 读取输入（例如，检索 Slack 消息，阅读电子邮件）
        - 写入输出（例如，生成报告，发送电子邮件）
        - 使用外部工具（例如，调用 LLM，搜索网页）
        - **注意**：*基于 LLM 的任务*（例如，文本摘要，情感分析）**不是**工具函数；相反，它们是 AI 系统内部的*核心功能*。
    - 对于每个工具函数，实现它并编写一个简单的测试。
    - 记录它们的输入/输出，以及为什么它们是必要的。例如：
      - `名称`：`get_embedding` (`utils/get_embedding.py`)
      - `输入`：`str`
      - `输出`：一个包含 3072 个浮点数的向量
      - `必要性`：由第二个节点用于嵌入文本
    - 工具实现示例：
      ```python
      # utils/call_llm.py
      from openai import OpenAI

      def call_llm(prompt):    
          client = OpenAI(api_key="YOUR_API_KEY_HERE")
          r = client.chat.completions.create(
              model="gpt-4o",
              messages=[{"role": "user", "content": prompt}]
          )
          return r.choices[0].message.content
          
      if __name__ == "__main__":
          prompt = "What is the meaning of life?"
          print(call_llm(prompt))
      ```
    - > **有时，在流程之前设计工具：** 例如，对于一个自动化遗留系统的 LLM 项目，瓶颈很可能是该系统可用的接口。从设计最难的接口工具开始，然后围绕它们构建流程。
      {: .best-practice }

4. **节点设计**：规划每个节点如何读写数据，并使用工具函数。
   - PocketFlow 的一个核心设计原则是使用[共享存储](./core_abstraction/communication.md)，因此从共享存储设计开始：
      - 对于简单系统，使用内存字典。
      - 对于更复杂的系统或需要持久化时，使用数据库。
      - **不要重复自己**：使用内存引用或外键。
      - 共享存储设计示例：
        ```python
        shared = {
            "user": {
                "id": "user123",
                "context": {                # Another nested dict
                    "weather": {"temp": 72, "condition": "sunny"},
                    "location": "San Francisco"
                }
            },
            "results": {}                   # Empty dict to store outputs
        }
        ```
   - 对于每个[节点](./core_abstraction/node.md)，描述其类型、如何读写数据以及使用哪个工具函数。保持具体但高层，不涉及代码。例如：
     - `类型`：常规（或批处理，或异步）
     - `准备`：从共享存储中读取“文本”
     - `执行`：调用嵌入工具函数
     - `后处理`：将“嵌入”写入共享存储

5. **实现**：根据设计实现初始节点和流程。
   - 🎉 如果你已达到此步骤，人类已完成设计。现在*Agentic 编程*开始！
   - **“保持简单，傻瓜！”** 避免复杂功能和全面的类型检查。
   - **快速失败**！避免 `try` 逻辑，以便快速识别系统中的任何薄弱点。
   - 在整个代码中添加日志记录以方便调试。

7. **优化**：
   - **使用直觉**：对于快速初步评估，人类直觉通常是一个好的开始。
   - **重新设计流程（回到步骤 3）**：考虑进一步分解任务，引入智能体决策，或更好地管理输入上下文。
   - 如果你的流程设计已经很完善，则进行微优化：
     - **提示工程**：使用清晰、具体的指令和示例来减少歧义。
     - **上下文学习**：为难以仅凭指令指定的任务提供可靠的示例。

   - > **你可能会进行大量迭代！** 预计会重复步骤 3-6 数百次。
     >
     > <div align="center"><img src="https://github.com/the-pocket/.github/raw/main/assets/success.png?raw=true" width="400"/></div>
     {: .best-practice }

8. **可靠性**
   - **节点重试**：在节点 `exec` 中添加检查，以确保输出符合要求，并考虑增加 `max_retries` 和 `wait` 时间。
   - **日志记录和可视化**：维护所有尝试的日志，并可视化节点结果，以便于调试。
   - **自我评估**：添加一个单独的节点（由 LLM 提供支持），在结果不确定时审查输出。

## LLM 项目文件结构示例

```
my_project/
├── main.py
├── nodes.py
├── flow.py
├── utils/
│   ├── __init__.py
│   ├── call_llm.py
│   └── search_web.py
├── requirements.txt
└── docs/
    └── design.md
```

- **`docs/design.md`**：包含上述每个步骤的项目文档。这应该是*高层*且*无代码*的。
- **`utils/`**：包含所有工具函数。
  - 建议为每个 API 调用专门创建一个 Python 文件，例如 `call_llm.py` 或 `search_web.py`。
  - 每个文件还应包含一个 `main()` 函数来尝试该 API 调用
- **`nodes.py`**：包含所有节点定义。
  ```python
  # nodes.py
  from pocketflow import Node
  from utils.call_llm import call_llm

  class GetQuestionNode(Node):
      def exec(self, _):
          # Get question directly from user input
          user_question = input("Enter your question: ")
          return user_question
      
      def post(self, shared, prep_res, exec_res):
          # Store the user's question
          shared["question"] = exec_res
          return "default"  # Go to the next node

  class AnswerNode(Node):
      def prep(self, shared):
          # Read question from shared
          return shared["question"]
      
      def exec(self, question):
          # Call LLM to get the answer
          return call_llm(question)
      
      def post(self, shared, prep_res, exec_res):
          # Store the answer in shared
          shared["answer"] = exec_res
  ```
- **`flow.py`**：实现通过导入节点定义并连接它们来创建流程的函数。
  ```python
  # flow.py
  from pocketflow import Flow
  from nodes import GetQuestionNode, AnswerNode

  def create_qa_flow():
      """Create and return a question-answering flow."""
      # Create nodes
      get_question_node = GetQuestionNode()
      answer_node = AnswerNode()
      
      # Connect nodes in sequence
      get_question_node >> answer_node
      
      # Create flow starting with input node
      return Flow(start=get_question_node)
  ```
- **`main.py`**：作为项目的入口点。
  ```python
  # main.py
  from flow import create_qa_flow

  # Example main function
  # 请将其替换为您自己的主函数
  def main():
      shared = {
          "question": None,  # Will be populated by GetQuestionNode from user input
          "answer": None     # Will be populated by AnswerNode
      }

      # Create the flow and run it
      qa_flow = create_qa_flow()
      qa_flow.run(shared)
      print(f"Question: {shared['question']}")
      print(f"Answer: {shared['answer']}")

  if __name__ == "__main__":
      main()
  ```
