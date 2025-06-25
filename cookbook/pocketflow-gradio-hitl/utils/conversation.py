conversation_cache = {}


def load_conversation(conversation_id: str):
    # 打印加载对话的信息
    print(f"Loading conversation {conversation_id}")
    # 从缓存中加载对话，如果不存在则返回空字典
    return conversation_cache.get(conversation_id, {})


def save_conversation(conversation_id: str, session: dict):
    # 打印保存对话的信息
    print(f"Saving conversation {session}")
    # 将对话保存到缓存中
    conversation_cache[conversation_id] = session
