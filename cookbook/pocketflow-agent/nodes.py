from pocketflow import Node
from utils import call_llm, search_web_duckduckgo
import yaml

class DecideAction(Node):
    def prep(self, shared):
        """为决策过程准备上下文和问题。"""
        # 获取当前上下文（如果不存在，则默认为“无先前搜索”）
        context = shared.get("context", "无先前搜索")
        # 从共享存储中获取问题
        question = shared["question"]
        # 返回两者以供执行步骤使用
        return question, context
        
    def exec(self, inputs):
        """调用LLM来决定是搜索还是回答。"""
        question, context = inputs
        
        print(f"🤔 代理正在决定下一步做什么...")
        
        # 创建一个提示，帮助LLM以正确的yaml格式决定下一步做什么
        prompt = f"""
### 上下文
您是一名可以搜索网络的科研助手。
问题: {question}
先前的研究: {context}

### 行动空间
[1] search
  描述: 在网络上查找更多信息
  参数:
    - query (str): 要搜索的内容

[2] answer
  描述: 用现有知识回答问题
  参数:
    - answer (str): 问题的最终答案

## 下一步行动
根据上下文和可用行动决定下一步行动。
以以下格式返回您的响应:

```yaml
thinking: |
    <您的逐步推理过程>
action: search OR answer
reason: <您选择此行动的原因>
answer: <如果行动是回答>
search_query: <如果行动是搜索，则为具体的搜索查询>
```
重要提示: 确保:
1. 所有多行字段都使用正确的缩进（4个空格）
2. 多行文本字段使用 | 字符
3. 单行字段不使用 | 字符
"""
        
        # Call the LLM to make a decision
        response = call_llm(prompt)
        
        # Parse the response to get the decision
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        decision = yaml.safe_load(yaml_str)
        
        return decision
    
    def post(self, shared, prep_res, exec_res):
        """保存决策并确定流程中的下一步。"""
        # 如果LLM决定搜索，则保存搜索查询
        if exec_res["action"] == "search":
            shared["search_query"] = exec_res["search_query"]
            print(f"🔍 代理决定搜索: {exec_res['search_query']}")
        else:
            shared["context"] = exec_res["answer"] # 如果LLM直接给出答案，则保存上下文。
            print(f"💡 代理决定回答问题")
        
        # 返回动作以确定流程中的下一个节点
        return exec_res["action"]

class SearchWeb(Node):
    def prep(self, shared):
        """从共享存储中获取搜索查询。"""
        return shared["search_query"]
        
    def exec(self, search_query):
        """搜索给定查询的网络。"""
        # 调用搜索工具函数
        print(f"🌐 正在搜索网络: {search_query}")
        results = search_web_duckduckgo(search_query)
        return results
    
    def post(self, shared, prep_res, exec_res):
        """保存搜索结果并返回决策节点。"""
        # 将搜索结果添加到共享存储的上下文中
        previous = shared.get("context", "")
        shared["context"] = previous + "\n\n搜索: " + shared["search_query"] + "\n结果: " + exec_res
        
        print(f"📚 找到信息，正在分析结果...")
        
        # 搜索后总是返回决策节点
        return "decide"

class AnswerQuestion(Node):
    def prep(self, shared):
        """获取问题和上下文以进行回答。"""
        return shared["question"], shared.get("context", "")
        
    def exec(self, inputs):
        """调用LLM生成最终答案。"""
        question, context = inputs
        
        print(f"✍️ 正在生成最终答案...")
        
        # 为LLM创建回答问题的提示
        prompt = f"""
### 上下文
根据以下信息回答问题。
问题: {question}
研究: {context}

## 您的答案:
利用研究结果提供一个全面的答案。
"""
        # Call the LLM to generate an answer
        answer = call_llm(prompt)
        return answer
    
    def post(self, shared, prep_res, exec_res):
        """保存最终答案并完成流程。"""
        # 将答案保存在共享存储中
        shared["answer"] = exec_res
        
        print(f"✅ 答案生成成功")
        
        # 我们完成了 - 无需继续流程
        return "done"
