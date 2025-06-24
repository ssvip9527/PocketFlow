from pocketflow import Node, Flow
from utils import call_llm

class ChatNode(Node):
    def prep(self, shared):
        # 如果是第一次运行，则初始化消息
        if "messages" not in shared:
            shared["messages"] = []
            print("欢迎来到聊天室！输入 'exit' 结束对话。")
        
        # 获取用户输入
        user_input = input("\n你: ")
        
        # 检查用户是否要退出
        if user_input.lower() == 'exit':
            return None
        
        # 将用户消息添加到历史记录
        shared["messages"].append({"role": "user", "content": user_input})
        
        # 返回所有消息给 LLM
        return shared["messages"]

    def exec(self, messages):
        if messages is None:
            return None
        
        # 使用整个对话历史调用 LLM
        response = call_llm(messages)
        return response

    def post(self, shared, prep_res, exec_res):
        if prep_res is None or exec_res is None:
            print("\n再见！")
            return None  # 结束对话
        
        # 打印助手的回复
        print(f"\n助手: {exec_res}")
        
        # 将助手消息添加到历史记录
        shared["messages"].append({"role": "assistant", "content": exec_res})
        
        # 循环以继续对话
        return "continue"

# 创建带自循环的流程
chat_node = ChatNode()
chat_node - "continue" >> chat_node  # 循环以继续对话

flow = Flow(start=chat_node)

# 启动聊天
if __name__ == "__main__":
    shared = {}
    flow.run(shared)
