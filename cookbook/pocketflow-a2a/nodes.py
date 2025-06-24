from pocketflow import Node
from utils import call_llm, search_web
import yaml

class DecideAction(Node):
    def prep(self, shared):
        """为决策过程准备上下文和问题。"""
        # 获取当前上下文（如果不存在，则默认为“无先前搜索”）
        context = shared.get("context", "No previous search")
        # 从共享存储中获取问题
        question = shared["question"]
        # 返回两者以供执行步骤使用
        return question, context
        
    def exec(self, inputs):
        """调用LLM来决定是搜索还是回答。"""
        question, context = inputs
        
        print(f"🤔 Agent deciding what to do next...")
        
        # 创建一个提示，帮助LLM决定下一步做什么，并使用正确的yaml格式
        prompt = f"""
### CONTEXT
You are a research assistant that can search the web.
Question: {question}
Previous Research: {context}

### ACTION SPACE
[1] search
  Description: Look up more information on the web
  Parameters:
    - query (str): What to search for

[2] answer
  Description: Answer the question with current knowledge
  Parameters:
    - answer (str): Final answer to the question

## NEXT ACTION
Decide the next action based on the context and available actions.
Return your response in this format:

```yaml
thinking: |
    <your step-by-step reasoning process>
action: search OR answer
reason: <why you chose this action>
answer: <if action is answer>
search_query: <specific search query if action is search>
```
IMPORTANT: Make sure to:
1. Use proper indentation (4 spaces) for all multi-line fields
2. Use the | character for multi-line text fields
3. Keep single-line fields without the | character
"""
        
        # 调用LLM做出决定
        response = call_llm(prompt)
        
        # 解析响应以获取决策
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        decision = yaml.safe_load(yaml_str)
        
        return decision
    
    def post(self, shared, prep_res, exec_res):
        """保存决策并确定流程中的下一步。"""
        # 如果LLM决定搜索，则保存搜索查询
        if exec_res["action"] == "search":
            shared["search_query"] = exec_res["search_query"]
            print(f"🔍 Agent decided to search for: {exec_res['search_query']}")
        else:
            shared["context"] = exec_res["answer"] # 如果LLM直接给出答案而没有搜索，则保存上下文。
            print(f"💡 Agent decided to answer the question")
        
        # 返回动作以确定流程中的下一个节点
        return exec_res["action"]

class SearchWeb(Node):
    def prep(self, shared):
        """从共享存储中获取搜索查询。"""
        return shared["search_query"]
        
    def exec(self, search_query):
        """搜索给定查询的网页。"""
        # 调用搜索工具函数
        print(f"🌐 Searching the web for: {search_query}")
        results = search_web(search_query)
        return results
    
    def post(self, shared, prep_res, exec_res):
        """保存搜索结果并返回决策节点。"""
        # 将搜索结果添加到共享存储的上下文中
        previous = shared.get("context", "")
        shared["context"] = previous + "\n\nSEARCH: " + shared["search_query"] + "\nRESULTS: " + exec_res
        
        print(f"📚 Found information, analyzing results...")
        
        # 搜索后总是返回决策节点
        return "decide"

class AnswerQuestion(Node):
    def prep(self, shared):
        """获取问题和上下文以进行回答。"""
        return shared["question"], shared.get("context", "")
        
    def exec(self, inputs):
        """调用LLM生成最终答案。"""
        question, context = inputs
        
        print(f"✍️ Crafting final answer...")
        
        # 为LLM创建回答问题的提示
        prompt = f"""
### CONTEXT
Based on the following information, answer the question.
Question: {question}
Research: {context}

## YOUR ANSWER:
Provide a comprehensive answer using the research results.
"""
        # 调用LLM生成答案
        answer = call_llm(prompt)
        return answer
    
    def post(self, shared, prep_res, exec_res):
        """保存最终答案并完成流程。"""
        # 将答案保存在共享存储中
        shared["answer"] = exec_res
        
        print(f"✅ Answer generated successfully")
        
        # 完成 - 无需继续流程
        return "done"
