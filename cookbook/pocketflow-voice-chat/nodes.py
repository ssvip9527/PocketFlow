import numpy as np
import scipy.io.wavfile
import io
import soundfile # For converting MP3 bytes to NumPy array

from pocketflow import Node
from utils.audio_utils import record_audio, play_audio_data
from utils.speech_to_text import speech_to_text_api
from utils.call_llm import call_llm
from utils.text_to_speech import text_to_speech_api

class CaptureAudioNode(Node):
    """从用户那里录制音频输入，使用 VAD。"""
    def exec(self, _): # prep_res 不按设计使用
        print("\n正在聆听您的查询...")
        audio_data, sample_rate = record_audio()
        if audio_data is None:
            return None, None
        return audio_data, sample_rate

    def post(self, shared, prep_res, exec_res):
        audio_numpy_array, sample_rate = exec_res
        if audio_numpy_array is None:
            shared["user_audio_data"] = None
            shared["user_audio_sample_rate"] = None
            print("CaptureAudioNode: 未能捕获音频。")
            return "end_conversation" 

        shared["user_audio_data"] = audio_numpy_array
        shared["user_audio_sample_rate"] = sample_rate
        print(f"音频已捕获 ({len(audio_numpy_array)/sample_rate:.2f}s)，正在进行 STT。")

class SpeechToTextNode(Node):
    """将录制的内存音频转换为文本。"""
    def prep(self, shared):
        user_audio_data = shared.get("user_audio_data")
        user_audio_sample_rate = shared.get("user_audio_sample_rate")
        if user_audio_data is None or user_audio_sample_rate is None:
            print("SpeechToTextNode: 没有要处理的音频数据。")
            return None # 信号以跳过 exec
        return user_audio_data, user_audio_sample_rate

    def exec(self, prep_res):
        if prep_res is None:
            return None # 如果没有音频数据则跳过

        audio_numpy_array, sample_rate = prep_res
        
        # 将 NumPy 数组转换为 WAV 字节以供 API 使用
        byte_io = io.BytesIO()
        scipy.io.wavfile.write(byte_io, sample_rate, audio_numpy_array)
        wav_bytes = byte_io.getvalue()
        
        print("正在将语音转换为文本...")
        transcribed_text = speech_to_text_api(audio_data=wav_bytes, sample_rate=sample_rate)
        return transcribed_text

    def post(self, shared, prep_res, exec_res):
        if exec_res is None:
            print("SpeechToTextNode: STT API 未返回文本。")
            return "end_conversation" 

        transcribed_text = exec_res
        print(f"用户: {transcribed_text}")
        
        if "chat_history" not in shared:
            shared["chat_history"] = []
        shared["chat_history"].append({"role": "user", "content": transcribed_text})
        
        shared["user_audio_data"] = None
        shared["user_audio_sample_rate"] = None
        return "default"

class QueryLLMNode(Node):
    """从 LLM 获取回复。"""
    def prep(self, shared):
        chat_history = shared.get("chat_history", [])
        
        if not chat_history:
            print("QueryLLMNode: 聊天历史为空。跳过 LLM 调用。")
            return None 
        
        return chat_history

    def exec(self, prep_res):
        if prep_res is None: 
            return None 

        chat_history = prep_res
        print("正在向 LLM 发送查询...")
        llm_response_text = call_llm(messages=chat_history)
        return llm_response_text

    def post(self, shared, prep_res, exec_res):
        if exec_res is None:
            print("QueryLLMNode: LLM API 未返回回复。")
            return "end_conversation" 

        llm_response_text = exec_res
        print(f"LLM: {llm_response_text}")
        
        shared["chat_history"].append({"role": "assistant", "content": llm_response_text})
        return "default"

class TextToSpeechNode(Node):
    """将 LLM 的文本回复转换为语音并播放。"""
    def prep(self, shared):
        chat_history = shared.get("chat_history", [])
        if not chat_history:
            print("TextToSpeechNode: 聊天历史为空。没有 LLM 回复可合成。")
            return None
        
        last_message = chat_history[-1]
        if last_message.get("role") == "assistant" and last_message.get("content"):
            return last_message.get("content")
        else:
            print("TextToSpeechNode: 最后一条消息不是来自助手或没有内容。跳过 TTS。")
            return None

    def exec(self, prep_res):
        if prep_res is None:
            return None, None
            
        llm_text_response = prep_res
        print("正在将 LLM 回复转换为语音...")
        llm_audio_bytes, llm_sample_rate = text_to_speech_api(llm_text_response)
        return llm_audio_bytes, llm_sample_rate

    def post(self, shared, prep_res, exec_res):
        if exec_res is None or exec_res[0] is None:
            print("TextToSpeechNode: TTS 失败或已跳过。")
            return "next_turn" 

        llm_audio_bytes, llm_sample_rate = exec_res
        
        print("正在播放 LLM 回复...")
        try:
            audio_segment, sr_from_file = soundfile.read(io.BytesIO(llm_audio_bytes))
            play_audio_data(audio_segment, sr_from_file)
        except Exception as e:
            print(f"播放 TTS 音频时出错: {e}")
            return "next_turn" 

        if shared.get("continue_conversation", True):
            return "next_turn"
        else:
            print("用户标志已结束对话。")
            return "end_conversation"