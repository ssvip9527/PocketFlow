import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import gradio as gr
from gradio import ChatMessage

from flow import create_flow

# 创建全局线程池
chatflow_thread_pool = ThreadPoolExecutor(
    max_workers=5,
    thread_name_prefix="chatflow_worker",
)


def chat_fn(message, history, uuid):
    """
    处理对话流程和消息处理的主聊天函数。
    
    Args:
        message (str): 当前用户消息
        history (list): 先前对话历史
        uuid (UUID): 对话的唯一标识符
    
    Yields:
        ChatMessage: 思维过程和聊天响应的流
    """
    # 记录对话详情
    print(f"Conversation ID: {str(uuid)}\nHistory: {history}\nQuery: {message}\n---")
    
    # 初始化聊天消息和流程思考的队列
    chat_queue = Queue()
    flow_queue = Queue()
    
    # 为流程创建共享上下文
    shared = {
        "conversation_id": str(uuid),
        "query": message,
        "history": history,
        "queue": chat_queue,
        "flow_queue": flow_queue,
    }
    
    # 在单独的线程中创建并运行聊天流程
    chat_flow = create_flow()
    chatflow_thread_pool.submit(chat_flow.run, shared)

    # 初始化思考响应跟踪
    start_time = time.time()
    thought_response = ChatMessage(
        content="", metadata={"title": "流程日志", "id": 0, "status": "pending"}
    )
    yield thought_response

    # 处理并累积流程队列中的思考
    accumulated_thoughts = ""
    while True:
        thought = flow_queue.get()
        if thought is None:
            break
        accumulated_thoughts += f"- {thought}\n\n"
        thought_response.content = accumulated_thoughts.strip()
        yield thought_response
        flow_queue.task_done()

    # 标记思考处理完成并记录持续时间
    thought_response.metadata["status"] = "done"
    thought_response.metadata["duration"] = time.time() - start_time
    yield thought_response

    # 处理并生成聊天队列中的聊天消息
    while True:
        msg = chat_queue.get()
        if msg is None:
            break
        chat_response = [thought_response, ChatMessage(content=msg)]
        yield chat_response
        chat_queue.task_done()


def clear_fn():
    print("正在清除对话")
    return uuid.uuid4()


with gr.Blocks(fill_height=True, theme="ocean") as demo:
    uuid_state = gr.State(uuid.uuid4())
    demo.load(clear_fn, outputs=[uuid_state])

    chatbot = gr.Chatbot(type="messages", scale=1)
    chatbot.clear(clear_fn, outputs=[uuid_state])

    gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        additional_inputs=[uuid_state],
        chatbot=chatbot,
        title="PocketFlow Gradio 演示",
    )


demo.launch()
