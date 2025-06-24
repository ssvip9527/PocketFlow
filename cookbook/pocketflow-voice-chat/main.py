from flow import create_voice_chat_flow

def main():
    """运行 PocketFlow 语音聊天应用程序。"""
    print("正在启动 PocketFlow 语音聊天...")
    print("在出现 '正在聆听您的查询...' 后说出您的查询。")
    print("对话将持续进行，直到发生错误或循环被有意停止。")
    print("要尝试停止，您可能需要引发错误（例如，捕获期间的静音，如果 VAD 未处理以优雅地结束）或在添加机制时修改 shared[\"continue_conversation\"]。")

    shared = {
        "user_audio_data": None,
        "user_audio_sample_rate": None,
        "chat_history": [],
        "continue_conversation": True # 控制主对话循环的标志
    }

    # 创建流
    voice_chat_flow = create_voice_chat_flow()

    # 运行流
    # 流将根据 TextToSpeechNode 的 "next_turn" 动作
    # 和节点内检查的 continue_conversation 标志或返回错误动作时循环。
    voice_chat_flow.run(shared)

if __name__ == "__main__":
    main()
