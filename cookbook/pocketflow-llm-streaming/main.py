import time
import threading
from pocketflow import Node, Flow
from utils import fake_stream_llm, stream_llm

class StreamNode(Node):
    def prep(self, shared):
        # 创建中断事件
        interrupt_event = threading.Event()

        # 启动一个线程来监听用户中断
        def wait_for_interrupt():
            input("随时按 ENTER 键中断流式传输...\n")
            interrupt_event.set()
        listener_thread = threading.Thread(target=wait_for_interrupt)
        listener_thread.start()
        
        # 从共享存储中获取提示
        prompt = shared["prompt"]
        # 从 LLM 函数获取分块
        chunks = stream_llm(prompt)
        return chunks, interrupt_event, listener_thread

    def exec(self, prep_res):
        chunks, interrupt_event, listener_thread = prep_res
        for chunk in chunks:
            if interrupt_event.is_set():
                print("用户中断了流式传输。")
                break
            
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                chunk_content = chunk.choices[0].delta.content
                print(chunk_content, end="", flush=True)
                time.sleep(0.1)  # 模拟延迟
        return interrupt_event, listener_thread

    def post(self, shared, prep_res, exec_res):
        interrupt_event, listener_thread = exec_res
        # 加入中断监听器，使其不再驻留
        interrupt_event.set()
        listener_thread.join()
        return "default"

# 用法:
node = StreamNode()
flow = Flow(start=node)

shared = {"prompt": "生命的意义是什么？"}
flow.run(shared)
