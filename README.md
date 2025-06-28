<div align="center">
  <img src="https://github.com/The-Pocket/.github/raw/main/assets/title.png" alt="Pocket Flow – 100行极简LLM框架" width="600"/>
</div>

<!-- For translation, replace English with [English](https://github.com/ssvip9527/PocketFlow/blob/main/README.md), and remove the link for the target language. -->

English | [中文](https://github.com/ssvip9527/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_CHINESE.md) | [Español](https://github.com/ssvip9527/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_SPANISH.md) | [日本語](https://github.com/ssvip9527/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_JAPANESE.md) | [Deutsch](https://github.com/ssvip9527/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_GERMAN.md) | [Русский](https://github.com/ssvip9527/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_RUSSIAN.md) | [Português](https://github.com/ssvip9527/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_PORTUGUESE.md) | [Français](https://github.com/ssvip9527/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_FRENCH.md) | [한국어](https://github.com/ssvip9527/PocketFlow/blob/main/cookbook/pocketflow-batch/translations/README_KOREAN.md)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://the-pocket.github.io/PocketFlow/)
 <a href="https://discord.gg/hUHHE9Sa6T">
    <img src="https://img.shields.io/discord/1346833819172601907?logo=discord&style=flat">
</a>

Pocket Flow 是一个 [100行](https://github.com/ssvip9527/PocketFlow/blob/main/pocketflow/__init__.py) 的极简 LLM 框架

- **轻量级**: 仅100行代码。零冗余，零依赖，零供应商锁定。
  
- **表达力强**: 包含您喜爱的一切功能—([多](https://the-pocket.github.io/PocketFlow/design_pattern/multi_agent.html))[智能体](https://the-pocket.github.io/PocketFlow/design_pattern/agent.html)、[工作流](https://the-pocket.github.io/PocketFlow/design_pattern/workflow.html)、[RAG](https://the-pocket.github.io/PocketFlow/design_pattern/rag.html)等。

- **[智能体编码](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to)**: 让AI智能体(如Cursor AI)构建智能体—10倍生产力提升！

开始使用 Pocket Flow:
- 安装: ```pip install pocketflow``` 或直接复制[源代码](https://github.com/ssvip9527/PocketFlow/blob/main/pocketflow/__init__.py)(仅100行)。
- 了解更多: 查看[文档](https://the-pocket.github.io/PocketFlow/)。了解动机，请阅读[故事](https://zacharyhuang.substack.com/p/i-built-an-llm-framework-in-just)。
- 有问题？查看这个[AI助手](https://chatgpt.com/g/g-677464af36588191b9eba4901946557b-pocket-flow-assistant)，或[创建issue!](https://github.com/ssvip9527/PocketFlow/issues/new)
- 🎉 加入我们的[Discord](https://discord.gg/hUHHE9Sa6T)与其他使用Pocket Flow的开发者交流！
- 🎉 Pocket Flow最初是Python版本，但现在我们还有[Typescript](https://github.com/ssvip9527/PocketFlow-Typescript)、[Java](https://github.com/ssvip9527/PocketFlow-Java)、[C++](https://github.com/ssvip9527/PocketFlow-CPP)和[Go](https://github.com/ssvip9527/PocketFlow-Go)版本！

## 为什么选择 Pocket Flow？

当前的 LLM 框架过于臃肿... 你的 LLM 框架只需要100行代码！

<div align="center">
  <img src="https://github.com/The-Pocket/.github/raw/main/assets/meme.jpg" width="400"/>


  |                | **抽象**          | **应用特定封装**                                      | **供应商特定封装**                                    | **代码行数**       | **大小**    |
|----------------|:-----------------------------: |:-----------------------------------------------------------:|:------------------------------------------------------------:|:---------------:|:----------------------------:|
| LangChain  | Agent, Chain               | 多 <br><sup><sub>(例如，问答，摘要)</sub></sup>              | 多 <br><sup><sub>(例如，OpenAI，Pinecone等)</sub></sup>                   | 405K          | +166MB                     |
| CrewAI     | Agent, Chain            | 多 <br><sup><sub>(例如，FileReadTool，SerperDevTool)</sub></sup>         | 多 <br><sup><sub>(例如，OpenAI，Anthropic，Pinecone等)</sub></sup>        | 18K           | +173MB                     |
| SmolAgent   | Agent                      | 一些 <br><sup><sub>(例如，CodeAgent，VisitWebTool)</sub></sup>         | 一些 <br><sup><sub>(例如，DuckDuckGo，Hugging Face等)</sub></sup>           | 8K            | +198MB                     |
| LangGraph   | Agent, Graph           | 一些 <br><sup><sub>(例如，语义搜索)</sub></sup>                     | 一些 <br><sup><sub>(例如，PostgresStore，SqliteSaver等) </sub></sup>        | 37K           | +51MB                      |
| AutoGen    | Agent                | 一些 <br><sup><sub>(例如，工具代理，聊天代理)</sub></sup>              | 多 <sup><sub>[可选]<br> (例如，OpenAI，Pinecone等)</sub></sup>        | 7K <br><sup><sub>(仅核心)</sub></sup>    | +26MB <br><sup><sub>(仅核心)</sub></sup>          |
| **PocketFlow** | **图**                    | **无**                                                 | **无**                                                  | **100**       | **+56KB**                  |

</div>

## Pocket Flow 如何工作？

这 [100行](https://github.com/ssvip9527/PocketFlow/blob/main/pocketflow/__init__.py) 代码捕捉了 LLM 框架的核心抽象：图！
<br>
<div align="center">
  <img src="https://github.com/The-Pocket/.github/raw/main/assets/abstraction.png" width="900"/>
</div>
<br>

在此基础上，可以轻松实现流行的设计模式，如 ([多](https://the-pocket.github.io/PocketFlow/design_pattern/multi_agent.html))[智能体](https://the-pocket.github.io/PocketFlow/design_pattern/agent.html)、[工作流](https://the-pocket.github.io/PocketFlow/design_pattern/workflow.html)、[RAG](https://the-pocket.github.io/PocketFlow/design_pattern/rag.html) 等。
<br>
<div align="center">
  <img src="https://github.com/The-Pocket/.github/raw/main/assets/design.png" width="900"/>
</div>
<br>
✨ 以下是基本教程：

<div align="center">
  
|  名称  | 难度    |  描述  |  
| :-------------:  | :-------------: | :--------------------- |  
| [聊天](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-chat) | ☆☆☆ <sup>*入门*</sup>  | 一个带有对话历史的基本聊天机器人 |
| [结构化输出](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-structured-output) | ☆☆☆ <sup>*入门*</sup> | 通过提示从简历中提取结构化数据 |
| [工作流](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-workflow) | ☆☆☆ <sup>*入门*</sup> | 一个写作工作流，包括大纲、内容撰写和样式应用 |
| [智能体](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-agent) | ☆☆☆ <sup>*入门*</sup>  | 一个可以搜索网页并回答问题的研究智能体 |
| [RAG](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-rag) | ☆☆☆ <sup>*入门*</sup> | 一个简单的检索增强生成过程 |
| [批处理](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-batch) | ☆☆☆ <sup>*入门*</sup> | 一个将 Markdown 翻译成多种语言的批处理器 |
| [流式传输](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-llm-streaming) | ☆☆☆ <sup>*入门*</sup> | 一个具有用户中断功能的实时 LLM 流式传输演示 |
| [聊天护栏](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-chat-guardrail) | ☆☆☆ <sup>*入门*</sup> | 一个只处理旅行相关查询的旅行顾问聊天机器人 |
| [多数投票](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-majority-vote) | ☆☆☆ <sup>*入门*</sup> | 通过聚合多个解决方案尝试来提高推理准确性 |
| [Map-Reduce](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-map-reduce) | ☆☆☆ <sup>*入门*</sup>  | 使用 Map-Reduce 模式进行批量简历筛选 |
| [CLI HITL](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-cli-hitl) | ☆☆☆ <sup>*入门*</sup>  | 一个带有人工反馈的命令行笑话生成器 |
| [多智能体](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-multi-agent) | ★☆☆ <sup>*初级*</sup> | 一个用于两个智能体之间异步通信的禁忌词游戏 |
| [监督器](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-supervisor) | ★☆☆ <sup>*初级*</sup> | 研究智能体变得不可靠... 让我们构建一个监督过程 |
| [并行](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-parallel-batch) |  ★☆☆ <sup>*初级*</sup> | 一个展示3倍加速的并行执行演示 |
| [并行流](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-parallel-batch-flow) | ★☆☆ <sup>*初级*</sup> | 一个展示8倍加速的并行图像处理 |
| [思考](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-thinking) |  ★☆☆ <sup>*初级*</sup> | 通过思维链解决复杂的推理问题 |
| [记忆](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-chat-memory) |  ★☆☆ <sup>*初级*</sup> | 一个具有短期和长期记忆的聊天机器人 |
| [Text2SQL](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-text2sql) |  ★☆☆ <sup>*初级*</sup>  | 通过自动调试循环将自然语言转换为 SQL 查询 |
| [代码生成器](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-code-generator) | ★☆☆ <sup>*初级*</sup> | 生成测试用例，实现解决方案，并迭代改进代码 |
| [MCP](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-mcp) |  ★☆☆ <sup>*初级*</sup> |  使用模型上下文协议进行数值运算的智能体 |
| [A2A](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-a2a) |  ★☆☆ <sup>*初级*</sup> | 使用 A2A 协议封装的智能体，用于智能体间通信 |
| [Streamlit FSM](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-streamlit-fsm) | ★☆☆ <sup>*初级*</sup> | 带有有限状态机的 Streamlit 应用，用于 HITL 图像生成 |
| [FastAPI WebSocket](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-fastapi-websocket) | ★☆☆ <sup>*初级*</sup> | 通过 WebSocket 实现的实时聊天界面，带有流式 LLM 响应 |
| [FastAPI 后台](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-fastapi-background) | ★☆☆ <sup>*初级*</sup> | 带有后台任务和通过 SSE 实现实时进度的 FastAPI 应用 |
| [语音聊天](https://github.com/ssvip9527/PocketFlow/tree/main/cookbook/pocketflow-voice-chat) | ★☆☆ <sup>*初级*</sup> | 一个带有 VAD、STT、LLM 和 TTS 的交互式语音聊天应用 |

</div>

👀 想看更多面向初学者的教程？[创建一个 issue！](https://github.com/ssvip9527/PocketFlow/issues/new)

## How to Use Pocket Flow?

🚀 Through **Agentic Coding**—the fastest LLM App development paradigm-where *humans design* and *agents code*!

<br>
<div align="center">
  <a href="https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to" target="_blank">
    <img src="https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F423a39af-49e8-483b-bc5a-88cc764350c6_1050x588.png" width="700" alt="IMAGE ALT TEXT" style="cursor: pointer;">
  </a>
</div>
<br>

✨ Below are examples of more complex LLM Apps:

<div align="center">
  
|  App Name     |  Difficulty    | Topics  | Human Design | Agent Code |
| :-------------:  | :-------------: | :---------------------: |  :---: |  :---: |
| [Website Chatbot](https://github.com/ssvip9527/PocketFlow-Tutorial-Website-Chatbot) <br> <sup><sub>Turn your website into a 24/7 customer support genius</sup></sub> | ★★☆ <br> *Medium* | [Agent](https://the-pocket.github.io/PocketFlow/design_pattern/agent.html) <br> [RAG](https://the-pocket.github.io/PocketFlow/design_pattern/rag.html) | [Design Doc](https://github.com/ssvip9527/PocketFlow-Tutorial-Website-Chatbot/blob/main/docs/design.md) | [Flow Code](https://github.com/ssvip9527/PocketFlow-Tutorial-Website-Chatbot/blob/main/flow.py)
| [Danganronpa Simulator](https://github.com/ssvip9527/PocketFlow-Tutorial-Danganronpa-Simulator) <br> <sup><sub>Forget the Turing test. Danganronpa, the ultimate AI experiment!</sup></sub> | ★★★ <br> *Advanced*   | [Workflow](https://the-pocket.github.io/PocketFlow/design_pattern/workflow.html) <br> [Agent](https://the-pocket.github.io/PocketFlow/design_pattern/agent.html) | [Design Doc](https://github.com/ssvip9527/PocketFlow-Tutorial-Danganronpa-Simulator/blob/main/docs/design.md) | [Flow Code](https://github.com/ssvip9527/PocketFlow-Tutorial-Danganronpa-Simulator/blob/main/flow.py)
| [Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge) <br> <sup><sub>Life's too short to stare at others' code in confusion</sup></sub> |  ★★☆ <br> *Medium* | [Workflow](https://the-pocket.github.io/PocketFlow/design_pattern/workflow.html) | [Design Doc](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge/blob/main/docs/design.md) | [Flow Code](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge/blob/main/flow.py)
| [Build Cursor with Cursor](https://github.com/The-Pocket/Tutorial-Cursor) <br> <sup><sub>We'll reach the singularity soon ...</sup></sub> | ★★★ <br> *Advanced*   | [Agent](https://the-pocket.github.io/PocketFlow/design_pattern/agent.html) | [Design Doc](https://github.com/The-Pocket/Tutorial-Cursor/blob/main/docs/design.md) | [Flow Code](https://github.com/The-Pocket/Tutorial-Cursor/blob/main/flow.py)
| [Ask AI Paul Graham](https://github.com/The-Pocket/Tutorial-YC-Partner) <br> <sup><sub>Ask AI Paul Graham, in case you don't get in</sup></sub> | ★★☆ <br> *Medium*  | [RAG](https://the-pocket.github.io/PocketFlow/design_pattern/rag.html) <br> [Map Reduce](https://the-pocket.github.io/PocketFlow/design_pattern/mapreduce.html) <br> [TTS](https://the-pocket.github.io/PocketFlow/utility_function/text_to_speech.html) | [Design Doc](https://github.com/The-Pocket/Tutorial-AI-Paul-Graham/blob/main/docs/design.md) | [Flow Code](https://github.com/The-Pocket/Tutorial-AI-Paul-Graham/blob/main/flow.py)
| [Youtube Summarizer](https://github.com/The-Pocket/Tutorial-Youtube-Made-Simple)  <br> <sup><sub> Explain YouTube Videos to you like you're 5 </sup></sub> | ★☆☆ <br> *Beginner*   | [Map Reduce](https://the-pocket.github.io/PocketFlow/design_pattern/mapreduce.html) |  [Design Doc](https://github.com/The-Pocket/Tutorial-Youtube-Made-Simple/blob/main/docs/design.md) | [Flow Code](https://github.com/The-Pocket/Tutorial-Youtube-Made-Simple/blob/main/flow.py)
| [Cold Opener Generator](https://github.com/The-Pocket/Tutorial-Cold-Email-Personalization)  <br> <sup><sub> Instant icebreakers that turn cold leads hot </sup></sub> | ★☆☆ <br> *Beginner*   | [Map Reduce](https://the-pocket.github.io/PocketFlow/design_pattern/mapreduce.html) <br> [Web Search](https://the-pocket.github.io/PocketFlow/utility_function/websearch.html) |  [Design Doc](https://github.com/The-Pocket/Tutorial-Cold-Email-Personalization/blob/master/docs/design.md) | [Flow Code](https://github.com/The-Pocket/Tutorial-Cold-Email-Personalization/blob/master/flow.py)


</div>

- Want to learn **Agentic Coding**?

  - Check out [my YouTube](https://www.youtube.com/@ZacharyLLM?sub_confirmation=1) for video tutorial on how some apps above are made!

  - Want to build your own LLM App? Read this [post](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to)! Start with [this template](https://github.com/ssvip9527/PocketFlow-Template-Python)!


