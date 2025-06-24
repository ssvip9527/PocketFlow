import asyncio
import asyncclick as click # Using asyncclick for async main
from uuid import uuid4
import json # For potentially inspecting raw errors
import anyio
import functools
import logging

# Import from the common directory placed alongside this script
from common.client import A2AClient
from common.types import (
    TaskState,
    A2AClientError,
    TextPart, # Used to construct the message
    JSONRPCResponse # Potentially useful for error checking
)

# --- Configure logging ---
# Set level to INFO to see client requests and responses
# Set level to DEBUG to see raw response bodies and SSE data lines
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Optionally silence overly verbose libraries
# logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("httpcore").setLevel(logging.WARNING)

# --- ANSI Colors (Optional but helpful) ---
C_RED = "\x1b[31m"
C_GREEN = "\x1b[32m"
C_YELLOW = "\x1b[33m"
C_BLUE = "\x1b[34m"
C_MAGENTA = "\x1b[35m"
C_CYAN = "\x1b[36m"
C_WHITE = "\x1b[37m"
C_GRAY = "\x1b[90m"
C_BRIGHT_MAGENTA = "\x1b[95m"
C_RESET = "\x1b[0m"
C_BOLD = "\x1b[1m"

def colorize(color, text):
    return f"{color}{text}{C_RESET}"

@click.command()
@click.option(
    "--agent-url",
    default="http://localhost:10003", # Default to the port used in server __main__
    help="URL of the PocketFlow A2A agent server.",
)
async def cli(agent_url: str):
    """与A2A代理交互的最小CLI客户端。"""

    print(colorize(C_BRIGHT_MAGENTA, f"Connecting to agent at: {agent_url}"))

    # 实例化客户端 - 如果不先获取卡片，只需要URL
    # 注意：PocketFlow包装器通过AgentCard暴露的内容不多，
    # 所以在这个最小客户端中我们跳过获取卡片。
    client = A2AClient(url=agent_url)

    sessionId = uuid4().hex # Generate a new session ID for this run
    print(colorize(C_GRAY, f"Using Session ID: {sessionId}"))

    while True:
        taskId = uuid4().hex # Generate a new task ID for each interaction
        try:
            # 使用functools.partial准备提示函数调用
            prompt_func = functools.partial(
                click.prompt,
                colorize(C_CYAN, "\nEnter your question (:q or quit to exit)"),
                prompt_suffix=" > ",
                type=str
            )
            # 在工作线程中运行同步提示函数
            prompt = await anyio.to_thread.run_sync(prompt_func)
        except (EOFError, RuntimeError, KeyboardInterrupt):
            # 捕获输入期间或stdin关闭时的潜在错误
            print(colorize(C_RED, "\nInput closed or interrupted. Exiting."))
            break

        if prompt.lower() in [":q", "quit"]:
            print(colorize(C_YELLOW, "Exiting client."))
            break

        # --- 构造A2A请求负载 ---
        payload = {
            "id": taskId,
            "sessionId": sessionId,
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text", # 明确匹配TextPart结构
                        "text": prompt,
                    }
                ],
            },
            "acceptedOutputModes": ["text", "text/plain"], # 客户端期望返回的内容
            # 如果需要可以添加historyLength
        }

        print(colorize(C_GRAY, f"Sending task {taskId}..."))

        try:
            # --- 发送任务(非流式) ---
            response = await client.send_task(payload)

            # --- 处理响应 ---
            if response.error:
                print(colorize(C_RED, f"Error from agent (Code: {response.error.code}): {response.error.message}"))
                if response.error.data:
                    print(colorize(C_GRAY, f"Error Data: {response.error.data}"))
            elif response.result:
                task_result = response.result
                print(colorize(C_GREEN, f"Task {task_result.id} finished with state: {task_result.status.state}"))

                final_answer = "Agent did not provide a final artifact."
                # 从artifacts中提取答案(如PocketFlowTaskManager中的实现)
                if task_result.artifacts:
                    try:
                        # Find the first text part in the first artifact
                        first_artifact = task_result.artifacts[0]
                        first_text_part = next(
                            (p for p in first_artifact.parts if isinstance(p, TextPart)),
                            None
                        )
                        if first_text_part:
                            final_answer = first_text_part.text
                        else:
                             final_answer = f"(Non-text artifact received: {first_artifact.parts})"
                    except (IndexError, AttributeError, TypeError) as e:
                        final_answer = f"(Error parsing artifact: {e})"
                elif task_result.status.message and task_result.status.message.parts:
                     # 如果没有artifact则回退到状态消息
                     try:
                        first_text_part = next(
                             (p for p in task_result.status.message.parts if isinstance(p, TextPart)),
                             None
                         )
                        if first_text_part:
                            final_answer = f"(Final status message: {first_text_part.text})"

                     except (AttributeError, TypeError) as e:
                         final_answer = f"(Error parsing status message: {e})"


                print(colorize(C_BOLD + C_WHITE, f"\nAgent Response:\n{final_answer}"))

            else:
                # Should not happen if error is None
                print(colorize(C_YELLOW, "Received response with no result and no error."))

        except A2AClientError as e:
            print(colorize(C_RED, f"\nClient Error: {e}"))
        except Exception as e:
            print(colorize(C_RED, f"\nAn unexpected error occurred: {e}"))

if __name__ == "__main__":
    asyncio.run(cli())