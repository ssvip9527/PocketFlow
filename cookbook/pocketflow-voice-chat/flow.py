from pocketflow import Flow
from nodes import CaptureAudioNode, SpeechToTextNode, QueryLLMNode, TextToSpeechNode

def create_voice_chat_flow() -> Flow:
    """创建并返回语音聊天流。"""
    # 创建节点
    capture_audio = CaptureAudioNode()
    speech_to_text = SpeechToTextNode()
    query_llm = QueryLLMNode()
    text_to_speech = TextToSpeechNode()

    # 定义转换
    capture_audio >> speech_to_text
    speech_to_text >> query_llm
    query_llm >> text_to_speech

    # 循环返回进行下一轮或结束
    text_to_speech - "next_turn" >> capture_audio
    # 任何节点的 "end_conversation" 动作都将自然终止流
    # 如果当前节点没有为其定义转换。
    # 或者，如果需要，可以明确地转换为 EndNode。

    # 创建从捕获音频节点开始的流
    voice_chat_flow = Flow(start=capture_audio)
    return voice_chat_flow 