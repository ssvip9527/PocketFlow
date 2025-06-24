from pocketflow import Node
from utils.vector_index import create_index, add_vector, search_vectors
from utils.call_llm import call_llm
from utils.get_embedding import get_embedding

class GetUserQuestionNode(Node):
    def prep(self, shared):
        """如果首次运行，则初始化消息"""
        if "messages" not in shared:
            shared["messages"] = []
            print("Welcome to the interactive chat! Type 'exit' to end the conversation.")
        
        return None
    
    def exec(self, _):
        """交互式获取用户输入。"""
        # 从用户获取交互式输入
        user_input = input("\nYou: ")
            
        # 检查用户是否想退出
        if user_input.lower() == 'exit':
            return None
            
        return user_input
    
    def post(self, shared, prep_res, exec_res):
        # 如果 exec_res 为 None，则用户想要退出
        if exec_res is None:
            print("\n再见！")
            return None  # 结束对话
            
        # 将用户消息添加到当前消息中
        shared["messages"].append({"role": "user", "content": exec_res})
        
        return "retrieve"

class AnswerNode(Node):
    def prep(self, shared):
        """为 LLM 准备上下文"""
        if not shared.get("messages"):
            return None
            
        # 1. 获取最近 3 对对话（如果不足则获取所有可用对话）
        recent_messages = shared["messages"][-6:] if len(shared["messages"]) > 6 else shared["messages"]
        
        # 2. 如果有检索到的相关对话，则添加它
        context = []
        if shared.get("retrieved_conversation"):
            # 添加系统消息以指示这是相关的历史对话
            context.append({
                "role": "system", 
                "content": "以下是可能有助于当前查询的相关历史对话："
            })
            context.extend(shared["retrieved_conversation"])
            context.append({
                "role": "system", 
                "content": "现在继续当前对话："
            })
        
        # 3. 添加最近的消息
        context.extend(recent_messages)
        
        return context
    
    def exec(self, messages):
        """使用 LLM 生成响应"""
        if messages is None:
            return None
        
        # 使用上下文调用 LLM
        response = call_llm(messages)
        return response
    
    def post(self, shared, prep_res, exec_res):
        """处理 LLM 响应"""
        if prep_res is None or exec_res is None:
            return None  # 结束对话
        
        # 打印助手的响应
        print(f"\n助手: {exec_res}")
        
        # 将助手消息添加到历史记录
        shared["messages"].append({"role": "assistant", "content": exec_res})
        
        # 如果我们有超过 6 条消息（3 对对话），则归档最旧的一对
        if len(shared["messages"]) > 6:
            return "embed"
        
        # 只有当用户明确输入 'exit' 时才结束
        # 即使设置了 last_question，我们也会在交互模式下继续
        return "question"

class EmbedNode(Node):
    """嵌入对话的节点。"""
    def prep(self, shared):
        """提取最旧的对话对进行嵌入"""
        if len(shared["messages"]) <= 6:
            return None
            
        # 提取最旧的用户-助手对话对
        oldest_pair = shared["messages"][:2]
        # 从当前消息中移除它们
        shared["messages"] = shared["messages"][2:]
        
        return oldest_pair
    
    def exec(self, conversation):
        """嵌入对话"""
        if not conversation:
            return None
            
        # 将用户和助手消息合并为单个文本进行嵌入
        user_msg = next((msg for msg in conversation if msg["role"] == "user"), {"content": ""})
        assistant_msg = next((msg for msg in conversation if msg["role"] == "assistant"), {"content": ""})
        combined = f"User: {user_msg['content']} Assistant: {assistant_msg['content']}"
        
        # 生成嵌入
        embedding = get_embedding(combined)
        
        return {
            "conversation": conversation,
            "embedding": embedding
        }
    
    def post(self, shared, prep_res, exec_res):
        """存储嵌入并添加到索引"""
        if not exec_res:
            # 如果没有要嵌入的内容，则继续下一个问题
            return "question"
            
        # 如果不存在，则初始化向量索引
        if "vector_index" not in shared:
            shared["vector_index"] = create_index()
            shared["vector_items"] = []  # 单独跟踪项目
            
        # 将嵌入添加到索引并存储对话
        position = add_vector(shared["vector_index"], exec_res["embedding"])
        shared["vector_items"].append(exec_res["conversation"])
        
        print(f"✅ 已将对话添加到索引位置 {position}")
        print(f"✅ 索引现在包含 {len(shared['vector_items'])} 个对话")
        
        # 继续下一个问题
        return "question"

class RetrieveNode(Node):
    """检索相关对话的节点。"""
    def prep(self, shared):
        """获取当前查询以进行检索"""
        if not shared.get("messages"):
            return None
            
        # 获取最新的用户消息进行搜索
        latest_user_msg = next((msg for msg in reversed(shared["messages"]) 
                                if msg["role"] == "user"), {"content": ""})
        
        # 检查我们是否有带有项目的向量索引
        if ("vector_index" not in shared or 
            "vector_items" not in shared or 
            len(shared["vector_items"]) == 0):
            return None
            
        return {
            "query": latest_user_msg["content"],
            "vector_index": shared["vector_index"],
            "vector_items": shared["vector_items"]
        }
    
    def exec(self, inputs):
        """查找最相关的历史对话"""
        if not inputs:
            return None
            
        query = inputs["query"]
        vector_index = inputs["vector_index"]
        vector_items = inputs["vector_items"]
        
        print(f"🔍 正在查找与以下内容相关的对话：{query[:30]}...")
        
        # 为查询创建嵌入
        query_embedding = get_embedding(query)
        
        # 搜索最相似的对话
        indices, distances = search_vectors(vector_index, query_embedding, k=1)
        
        if not indices:
            return None
            
        # 获取相应的对话
        conversation = vector_items[indices[0]]
        
        return {
            "conversation": conversation,
            "distance": distances[0]
        }
    
    def post(self, shared, prep_res, exec_res):
        """存储检索到的对话"""
        if exec_res is not None:
            shared["retrieved_conversation"] = exec_res["conversation"]
            print(f"📄 已检索到对话（距离：{exec_res['distance']:.4f}）")
        else:
            shared["retrieved_conversation"] = None
            shared["retrieved_conversation"] = None
        
        return "answer"