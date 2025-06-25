def format_chat_history(history):
    """
    格式化聊天历史以供 LLM 使用

    Args:
        history (list): 聊天历史列表，每个元素包含角色和内容

    Returns:
        str: 格式化后的聊天历史字符串
    """
    if not history:
        return "无历史记录"

    formatted_history = []
    for message in history:
        role = "user" if message["role"] == "user" else "assistant"
        content = message["content"]
        # 过滤掉思考内容
        if role == "assistant":
            if (
                content.startswith("- 🤔")
                or content.startswith("- ➡️")
                or content.startswith("- ⬅️")
            ):
                continue
        formatted_history.append(f"{role}: {content}")

    return "\n".join(formatted_history)
