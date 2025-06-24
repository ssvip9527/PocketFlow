from flow import chat_flow

def run_chat_memory_demo():
    """运行一个带有记忆检索的交互式聊天界面。
    Run an interactive chat interface with memory retrieval.
    
    功能：
    1. 维护最近 3 对对话的窗口
    2. 使用嵌入归档旧对话
    3. 在需要时检索 1 个相关的旧对话
    4. LLM 的总上下文：3 个最近的对话对 + 1 个检索到的对话对
    """
    
    print("=" * 50)
    print("PocketFlow 记忆聊天")
    print("=" * 50)
    print("此聊天会保留您最近的 3 次对话")
    print("并在有帮助时带回相关的历史对话")
    print("输入 'exit' 结束对话")
    print("=" * 50)
    
    # 运行聊天流程
    chat_flow.run({})

if __name__ == "__main__":
    run_chat_memory_demo()