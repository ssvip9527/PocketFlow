# nodes.py

from pocketflow import Node
import yaml
from utils import call_llm

class ThinkNode(Node):
    def prep(self, shared):
        """准备思考所需的上下文"""
        query = shared.get("query", "")
        observations = shared.get("observations", [])
        thoughts = shared.get("thoughts", [])
        current_thought_number = shared.get("current_thought_number", 0)
        
        # 更新思考次数
        shared["current_thought_number"] = current_thought_number + 1
        
        # 格式化之前的观察
        observations_text = "\n".join([f"观察 {i+1}: {obs}" for i, obs in enumerate(observations)])
        if not observations_text:
            observations_text = "尚无观察。"
            
        return {
            "query": query,
            "observations_text": observations_text,
            "thoughts": thoughts,
            "current_thought_number": current_thought_number + 1
        }
    
    def exec(self, prep_res):
        """执行思考过程，决定下一步行动"""
        query = prep_res["query"]
        observations_text = prep_res["observations_text"]
        current_thought_number = prep_res["current_thought_number"]
        
        # 构建提示
        prompt = f"""
        你是一个AI助手，正在解决问题。根据用户的查询和之前的观察，考虑下一步行动。
        
        用户查询: {query}
        
        之前的观察：
        {observations_text}
        
        请考虑下一步行动，并以YAML格式返回你的思考过程和决策：
        ```yaml
        thinking: |
            <详细的思考过程>
        action: <行动名称，例如'search'或'answer'>
        action_input: <行动的输入参数>
        is_final: <如果这是最终答案，则设置为true，否则为false>
        ```
        """
        
        # 调用LLM获取思考结果
        response = call_llm(prompt)
        
        # 解析YAML响应
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        thought_data = yaml.safe_load(yaml_str)
        
        # 添加思考次数
        thought_data["thought_number"] = current_thought_number
        
        return thought_data
    
    def post(self, shared, prep_res, exec_res):
        """保存思考结果并决定流程的下一步"""
        # 保存思考结果
        if "thoughts" not in shared:
            shared["thoughts"] = []
        shared["thoughts"].append(exec_res)
        
        # 保存行动信息
        shared["current_action"] = exec_res["action"]
        shared["current_action_input"] = exec_res["action_input"]
        
        # 如果是最终答案，结束流程
        if exec_res.get("is_final", False):
            shared["final_answer"] = exec_res["action_input"]
            print(f"🎯 最终答案: {exec_res['action_input']}")
            return "end"
        
        # 否则继续行动
        print(f"🤔 思考 {exec_res['thought_number']}: 决定执行 {exec_res['action']}")
        return "action"

class ActionNode(Node):
    def prep(self, shared):
        """准备执行行动"""
        action = shared["current_action"]
        action_input = shared["current_action_input"]
        return action, action_input
    
    def exec(self, inputs):
        """执行行动并返回结果"""
        action, action_input = inputs
        
        print(f"🚀 执行动作: {action}, 输入: {action_input}")
        
        # 根据行动类型执行不同操作
        if action == "search":
            # 模拟搜索操作
            result = self.search_web(action_input)
        elif action == "calculate":
            # 模拟计算操作
            result = self.calculate(action_input)
        elif action == "answer":
            # 直接返回答案
            result = action_input
        else:
            # 未知行动类型
            result = f"未知行动类型: {action}"
        
        return result
    
    def post(self, shared, prep_res, exec_res):
        """保存行动结果"""
        # 保存当前行动结果
        shared["current_action_result"] = exec_res
        print(f"✅ 行动完成，结果已获得")
        
        # 继续到观察节点
        return "observe"
    
    # 模拟工具函数
    def search_web(self, query):
        # 这应该是实际的搜索逻辑
        return f"搜索结果: 关于'{query}'的信息..."
    
    def calculate(self, expression):
        # 这应该是实际的计算逻辑
        try:
            return f"计算结果: {eval(expression)}"
        except:
            return f"无法计算表达式: {expression}"

class ObserveNode(Node):
    def prep(self, shared):
        """准备观察数据"""
        action = shared["current_action"]
        action_input = shared["current_action_input"]
        action_result = shared["current_action_result"]
        return action, action_input, action_result
    
    def exec(self, inputs):
        """分析行动结果，生成观察"""
        action, action_input, action_result = inputs
        
        # 构建提示
        prompt = f"""
        你是一个观察者，需要分析行动结果并提供客观观察。
        
        行动: {action}
        行动输入: {action_input}
        行动结果: {action_result}
        
        请提供对此结果的简明观察。不要做决定，只描述你所看到的。
        """
        
        # 调用LLM获取观察结果
        observation = call_llm(prompt)
        
        print(f"👁️ 观察: {observation[:50]}...")
        return observation
    
    def post(self, shared, prep_res, exec_res):
        """保存观察结果并决定下一个流程步骤"""
        # 保存观察结果
        if "observations" not in shared:
            shared["observations"] = []
        shared["observations"].append(exec_res)
        
        # 继续思考
        return "think"
    

    
class EndNode(Node):
    def prep(self, shared):
        """准备结束节点"""
        
        return {}
    def exec(self, prep_res):
        """执行结束操作"""
        print("流程结束，感谢使用！")
        return None
    def post(self, shared, prep_res, exec_res):
        """结束流程"""
        return None