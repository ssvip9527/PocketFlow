from pocketflow import Node
from utils import call_llm, search_web
import yaml
import random

class DecideAction(Node):
    def prep(self, shared):
        """准备决策过程的上下文和问题。"""
        # 获取当前上下文（如果不存在，则默认为“无先前搜索”）
        context = shared.get("context", "无先前搜索")
        # 从共享存储中获取问题
        question = shared["question"]
        # 返回两者以供执行步骤使用
        return question, context
        
    def exec(self, inputs):
        """调用LLM以决定是搜索还是回答。"""
        question, context = inputs
        
        print(f"🤔 代理正在决定下一步... ")
        
        # 创建一个提示，帮助LLM决定下一步做什么
        prompt = f"""
### 上下文
你是一个可以搜索网络的研发助理。
问题: {question}
先前的研究: {context}

### 行动空间
[1] 搜索
  描述: 在网络上查找更多信息
  参数:
    - query (str): 要搜索的内容

[2] 回答
  描述: 用现有知识回答问题
  参数:
    - answer (str): 问题的最终答案

## 下一步行动
根据上下文和可用行动决定下一步行动。
以这种格式返回你的响应:

```yaml
thinking: |
    <你的逐步推理过程>
action: search 或 answer
reason: <你选择此行动的原因>
search_query: <如果行动是搜索，则为具体的搜索查询>
```"""
        
        # 调用LLM做出决定
        response = call_llm(prompt)
        
        # 解析响应以获取决定
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        decision = yaml.safe_load(yaml_str)
        
        return decision
    
    def post(self, shared, prep_res, exec_res):
        """保存决定并确定流程中的下一步。"""
        # 如果LLM决定搜索，则保存搜索查询
        if exec_res["action"] == "search":
            shared["search_query"] = exec_res["search_query"]
            print(f"🔍 代理决定搜索: {exec_res['search_query']}")
        else:
            print(f"💡 代理决定回答问题")
        
        # 返回行动以确定流程中的下一个节点
        return exec_res["action"]

class SearchWeb(Node):
    def prep(self, shared):
        """从共享存储中获取搜索查询。"""
        return shared["search_query"]
        
    def exec(self, search_query):
        """搜索给定查询的网络。"""
        # 调用搜索实用函数
        print(f"🌐 正在搜索网络: {search_query}")
        results = search_web(search_query)
        return results
    
    def post(self, shared, prep_res, exec_res):
        """保存搜索结果并返回决策节点。"""
        # 将搜索结果添加到共享存储中的上下文
        previous = shared.get("context", "")
        shared["context"] = previous + "\n\n搜索: " + shared["search_query"] + "\n结果: " + exec_res
        
        print(f"📚 找到信息，正在分析结果...")
        
        # 搜索后始终返回决策节点
        return "decide"

class UnreliableAnswerNode(Node):
    def prep(self, shared):
        """获取问题和上下文以进行回答。"""
        return shared["question"], shared.get("context", "")
        
    def exec(self, inputs):
        """调用LLM生成最终答案，有50%的几率返回一个虚拟答案。"""
        question, context = inputs
        
        # 50%的几率返回一个虚拟答案
        if random.random() < 0.5:
            print(f"🤪 正在生成不可靠的虚拟答案...")
            return "抱歉，我正在休息。我提供的所有信息都是完全虚构的。你问题的答案是42，或者可能是紫色的独角兽。谁知道呢？反正我不知道！"
        
        print(f"✍️ 正在撰写最终答案...")
        
        # 为LLM创建提示以回答问题
        prompt = f"""
### 上下文
根据以下信息回答问题。
问题: {question}
研究: {context}

## 你的答案:
使用研究结果提供全面答案。
"""
        # 调用LLM生成答案
        answer = call_llm(prompt)
        return answer
    
    def post(self, shared, prep_res, exec_res):
        """保存最终答案并完成流程。"""
        # 将答案保存在共享存储中
        shared["answer"] = exec_res
        
        print(f"✅ 答案生成成功")

class SupervisorNode(Node):
    def prep(self, shared):
        """获取当前答案以进行评估。"""
        return shared["answer"]
    
    def exec(self, answer):
        """检查答案是否有效或无意义。"""
        print(f"    🔍 监督器正在检查答案质量...")
        
        # 检查无意义答案的明显标记
        nonsense_markers = [
            "coffee break", 
            "purple unicorns", 
            "made up", 
            "42", 
            "Who knows?"
        ]
        
        # 检查答案是否包含任何无意义标记
        is_nonsense = any(marker in answer for marker in nonsense_markers)
        
        if is_nonsense:
            return {"valid": False, "reason": "答案似乎是无意义或无用的"}
        else:
            return {"valid": True, "reason": "答案似乎是合法的"}
    
    def post(self, shared, prep_res, exec_res):
        """决定是接受答案还是重新启动过程。"""
        if exec_res["valid"]:
            print(f"    ✅ 监督器批准答案: {exec_res['reason']}")
        else:
            print(f"    ❌ 监督器拒绝答案: {exec_res['reason']}")
            # 清理错误的答案
            shared["answer"] = None
            # 添加关于被拒绝答案的注释
            context = shared.get("context", "")
            shared["context"] = context + "\n\n注意: 先前的答案尝试被监督器拒绝。"
            return "retry"