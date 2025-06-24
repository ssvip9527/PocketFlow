from pocketflow import Node, Flow
from utils import call_llm

class UserInputNode(Node):
    def prep(self, shared):
        # 如果是第一次运行，则初始化消息
        if "messages" not in shared:
            shared["messages"] = []
            print("欢迎使用旅行顾问聊天！输入'exit'结束对话。")
        
        return None

    def exec(self, _):
        # 获取用户输入
        user_input = input("\n你: ")
        return user_input

    def post(self, shared, prep_res, exec_res):
        user_input = exec_res
        
        # 检查用户是否要退出
        if user_input and user_input.lower() == 'exit':
            print("\n再见！旅途愉快！")
            return None  # 结束对话
        
        # 将用户输入存储在共享数据中
        shared["user_input"] = user_input
        
        # 转到护栏验证
        return "validate"

class GuardrailNode(Node):
    def prep(self, shared):
        # 从共享数据中获取用户输入
        user_input = shared.get("user_input", "")
        return user_input
    
    def exec(self, user_input):
        # 基本验证检查
        if not user_input or user_input.strip() == "":
            return False, "您的查询为空。请提供与旅行相关的问题。"
        
        if len(user_input.strip()) < 3:
            return False, "您的查询太短。请提供更多关于旅行问题的详细信息。"
        
        # 基于LLM的旅行主题验证
        prompt = f"""
评估以下用户查询是否与旅行建议、目的地、规划或其他旅行主题相关。
聊天应仅回答与旅行相关的问题，拒绝任何无关、有害或不适当的查询。
用户查询: {user_input}
以YAML格式返回您的评估:
```yaml
valid: true/false
reason: [解释查询有效或无效的原因]
```"""
        
        # 使用验证提示调用LLM
        messages = [{"role": "user", "content": prompt}]
        response = call_llm(messages)
        
        # 提取YAML内容
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        
        import yaml
        result = yaml.safe_load(yaml_content)
        assert result is not None, "错误: 无效的YAML格式"
        assert "valid" in result and "reason" in result, "错误: 无效的YAML格式"
        is_valid = result.get("valid", False)
        reason = result.get("reason", "YAML响应中缺少原因")
        
        return is_valid, reason
    
    def post(self, shared, prep_res, exec_res):
        is_valid, message = exec_res
        
        if not is_valid:
            # 向用户显示错误信息
            print(f"\n旅行顾问: {message}")
            # 跳过LLM调用并返回用户输入
            return "retry"
        
        # 有效输入，添加到消息历史
        shared["messages"].append({"role": "user", "content": shared["user_input"]})
        # 继续LLM处理
        return "process"

class LLMNode(Node):
    def prep(self, shared):
        # 如果不存在系统消息则添加
        if not any(msg.get("role") == "system" for msg in shared["messages"]):
            shared["messages"].insert(0, {
                "role": "system", 
                "content": "你是一个乐于助人的旅行顾问，提供有关目的地、旅行规划、住宿、交通、活动和其他旅行相关主题的信息。只回答与旅行相关的查询，保持回复信息丰富且友好。你的回复简洁，不超过100字。"
            })
        
        # 返回所有消息给LLM
        return shared["messages"]

    def exec(self, messages):
        # 使用完整的对话历史调用LLM
        response = call_llm(messages)
        return response

    def post(self, shared, prep_res, exec_res):
        # 打印助手的回复
        print(f"\n旅行顾问: {exec_res}")
        
        # 将助手消息添加到历史记录
        shared["messages"].append({"role": "assistant", "content": exec_res})
        
        # 循环以继续对话
        return "continue"

# 创建带节点和连接的流程
user_input_node = UserInputNode()
guardrail_node = GuardrailNode()
llm_node = LLMNode()

# 创建流程连接
user_input_node - "validate" >> guardrail_node
guardrail_node - "retry" >> user_input_node  # 如果输入无效则循环返回
guardrail_node - "process" >> llm_node
llm_node - "continue" >> user_input_node     # 继续对话

flow = Flow(start=user_input_node)

# 启动聊天
if __name__ == "__main__":
    shared = {}
    flow.run(shared)
