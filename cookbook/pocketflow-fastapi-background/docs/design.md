# Design Doc: PocketFlow FastAPI Background Job with SSE Progress

> Please DON'T remove notes for AI

## 需求

> 给AI的提示：保持简单清晰
> 如果需求比较抽象，请编写具体的用户故事

**用户故事**：作为一个用户，我想通过Web API提交文章主题，并在文章生成过程中接收实时进度更新，这样我可以在不阻塞UI的情况下查看工作流进度。

**核心需求**：
1. 通过REST API端点提交文章主题
2. 启动文章生成工作流的后台任务
3. 通过服务器发送事件(SSE)接收实时进度更新
4. 在工作流完成时获取最终文章结果
5. 处理多个并发请求

**技术要求**：
- 使用FastAPI搭建Web服务器并提供REST端点
- 使用asyncio进行后台任务处理
- 使用服务器发送事件(SSE)进行进度流式传输
- 提供简单的Web界面来测试功能

## Flow Design

> Notes for AI:
> 1. Consider the design patterns of agent, map-reduce, rag, and workflow. Apply them if they fit.
> 2. Present a concise, high-level description of the workflow.

### Applicable Design Pattern:

**Workflow Pattern**: Sequential processing of article generation steps with progress reporting at each stage.

### Flow High-level Design:

1. **Generate Outline Node**: Creates a structured outline for the article topic
2. **Write Content Node**: Writes content for each section in the outline  
3. **Apply Style Node**: Applies conversational styling to the final article

Each node puts progress updates into an asyncio.Queue for SSE streaming.

```mermaid
flowchart LR
    outline[Generate Outline] --> content[Write Content]
    content --> styling[Apply Style]
```

## Utility Functions

> Notes for AI:
> 1. Understand the utility function definition thoroughly by reviewing the doc.
> 2. Include only the necessary utility functions, based on nodes in the flow.

1. **Call LLM** (`utils/call_llm.py`)
   - *Input*: prompt (str)
   - *Output*: response (str)
   - Used by all workflow nodes for LLM tasks

## Node Design

### Shared Store

> Notes for AI: Try to minimize data redundancy

The shared store structure is organized as follows:

```python
shared = {
    "topic": "user-provided-topic",
    "sse_queue": asyncio.Queue(),  # For sending SSE updates
    "sections": ["section1", "section2", "section3"],
    "draft": "combined-section-content",
    "final_article": "styled-final-article"
}
```

### Node Steps

> Notes for AI: Carefully decide whether to use Batch/Async Node/Flow.

1. **Generate Outline Node**
   - *Purpose*: Create a structured outline with 3 main sections using YAML output
   - *Type*: Regular Node (synchronous LLM call)
   - *Steps*:
     - *prep*: Read "topic" from shared store
     - *exec*: Call LLM to generate YAML outline, parse and validate structure
     - *post*: Write "sections" to shared store, put progress update in sse_queue

2. **Write Content Node**
   - *Purpose*: Generate concise content for each outline section
   - *Type*: BatchNode (processes each section independently)
   - *Steps*:
     - *prep*: Read "sections" from shared store (returns list of sections)
     - *exec*: For one section, call LLM to write 100-word content
     - *post*: Combine all section content into "draft", put progress update in sse_queue

3. **Apply Style Node**
   - *Purpose*: Apply conversational, engaging style to the combined content
   - *Type*: Regular Node (single LLM call for styling)
   - *Steps*:
     - *prep*: Read "draft" from shared store
     - *exec*: Call LLM to rewrite in conversational style
     - *post*: Write "final_article" to shared store, put completion update in sse_queue
