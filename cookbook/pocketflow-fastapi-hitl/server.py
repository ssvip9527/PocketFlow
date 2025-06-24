import asyncio
import uuid
import json
import os
from fastapi import FastAPI, Request, HTTPException, status, BackgroundTasks # Import BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field # Import Pydantic for request/response models
from typing import Dict, Any, Literal # For type hinting

from flow import create_feedback_flow # PocketFlow imports

# --- 配置 ---
app = FastAPI(title="Minimal Feedback Loop API")

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"Warning: Static directory '{static_dir}' not found.")

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
if os.path.isdir(template_dir):
    templates = Jinja2Templates(directory=template_dir)
else:
    print(f"Warning: Template directory '{template_dir}' not found.")
    templates = None

# --- 状态管理（内存中 - 不用于生产环境）---
# 用于存储任务状态的全局字典。在生产环境中，请使用 Redis、数据库等。
tasks: Dict[str, Dict[str, Any]] = {}
# 结构：task_id -> {"shared": dict, "status": str, "task_obj": asyncio.Task | None}


# --- 后台流运行器 ---
# 此函数基本保持不变，因为它定义了要完成的工作。
# 现在它将由 FastAPI 的 BackgroundTasks 调度。
async def run_flow_background(task_id: str, flow, shared: Dict[str, Any]):
    """在后台运行流，使用共享队列进行 SSE。"""
    # 检查任务是否存在（可能已被取消/删除）
    if task_id not in tasks:
        print(f"后台任务 {task_id}: 任务未找到，中止。")
        return
    queue = shared.get("sse_queue")
    if not queue:
        print(f"错误：任务 {task_id} 共享存储中缺少 sse_queue！")
        tasks[task_id]["status"] = "failed"
        # 如果缺少队列，则无法通过 SSE 报告失败
        return

    tasks[task_id]["status"] = "running"
    await queue.put({"status": "running"})
    print(f"任务 {task_id}: 后台流启动中。")

    final_status = "unknown"
    error_message = None
    try:
        # 执行可能长时间运行的 PocketFlow
        await flow.run_async(shared)

        # 根据流完成后共享状态确定最终状态
        if shared.get("final_result") is not None:
            final_status = "completed"
        else:
            # 如果流结束但未设置 final_result
            final_status = "finished_incomplete"
        print(f"任务 {task_id}: 流以状态 {final_status} 完成")

    except Exception as e:
        final_status = "failed"
        error_message = str(e)
        print(f"任务 {task_id}: 流执行失败：{e}")
        # 在生产环境中考虑在此处记录堆栈跟踪
    finally:
        # 确保任务在更新状态之前仍然存在
        if task_id in tasks:
            tasks[task_id]["status"] = final_status
            final_update = {"status": final_status}
            if final_status == "completed":
                final_update["final_result"] = shared.get("final_result")
            elif error_message:
                final_update["error"] = error_message
            # 将最终状态更新放入队列
            await queue.put(final_update)

        # 通过放置 None 来表示 SSE 流的结束
        # 无论任务是否在运行中被删除，都必须发生
        if queue:
           await queue.put(None)
        print(f"任务 {task_id}: 后台任务结束。最终更新哨兵已放入队列。")
        # 移除对已完成/失败的 asyncio Task 对象的引用
        if task_id in tasks:
            tasks[task_id]["task_obj"] = None

# --- 用于请求/响应验证的 Pydantic 模型 ---
class SubmitRequest(BaseModel):
    data: str = Field(..., min_length=1, description="Input data for the task")

class SubmitResponse(BaseModel):
    message: str = "Task submitted"
    task_id: str

class FeedbackRequest(BaseModel):
    feedback: Literal["approved", "rejected"] # Use Literal for specific choices

class FeedbackResponse(BaseModel):
    message: str

# --- FastAPI 路由 ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def get_index(request: Request):
    """提供主 HTML 前端。"""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates directory not configured.")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit", response_model=SubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_task(
    submit_request: SubmitRequest, # 使用 Pydantic 模型进行验证
    background_tasks: BackgroundTasks # 注入 BackgroundTasks 实例
):
    """
    提交一个新任务。实际处理在后台运行。
    立即返回任务 ID。
    """
    task_id = str(uuid.uuid4())
    feedback_event = asyncio.Event()
    status_queue = asyncio.Queue()

    shared = {
        "task_input": submit_request.data,
        "processed_output": None,
        "feedback": None,
        "review_event": feedback_event,
        "sse_queue": status_queue,
        "final_result": None,
        "task_id": task_id
    }

    flow = create_feedback_flow()

    # 在调度后台任务之前存储任务状态
    tasks[task_id] = {
        "shared": shared,
        "status": "pending",
        "task_obj": None # 由 BackgroundTasks 创建的 asyncio Task 的占位符
    }

    await status_queue.put({"status": "pending", "task_id": task_id})

    # 使用 FastAPI 的 BackgroundTasks 调度流执行
    # 这在响应发送后运行
    background_tasks.add_task(run_flow_background, task_id, flow, shared)
    # 注意：我们无法通过这种方式直接获取 asyncio Task 对象的引用，
    # 对于这个最小示例来说没问题。如果需要取消，
    # 则需要手动管理 asyncio.create_task。

    print(f"Task {task_id}: Submitted, scheduled for background execution.")
    return SubmitResponse(task_id=task_id)


@app.post("/feedback/{task_id}", response_model=FeedbackResponse)
async def provide_feedback(task_id: str, feedback_request: FeedbackRequest):
    """提供反馈（批准/拒绝）以可能解除阻塞等待中的任务。"""
    if task_id not in tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task_info = tasks[task_id]
    shared = task_info["shared"]
    queue = shared.get("sse_queue")
    review_event = shared.get("review_event")

    async def report_error(message, status_code=status.HTTP_400_BAD_REQUEST):
        # 辅助函数，用于记录日志、将状态放入队列并引发 HTTP 异常
        print(f"任务 {task_id}: 反馈错误 - {message}")
        if queue: await queue.put({"status": "feedback_error", "error": message})
        raise HTTPException(status_code=status_code, detail=message)

    if not review_event:
        # 如果任务存在但没有事件，则表示内部设置错误
        await report_error("任务未配置反馈", status.HTTP_500_INTERNAL_SERVER_ERROR)
    if review_event.is_set():
        # 防止多次处理反馈或任务未等待时处理反馈
        await report_error("任务未等待反馈或反馈已发送", status.HTTP_409_CONFLICT)

    feedback = feedback_request.feedback # Already validated by Pydantic
    print(f"Task {task_id}: Received feedback via POST: {feedback}")

    # 在设置事件之前更新状态，以便客户端首先看到“处理中”
    if queue: await queue.put({"status": "processing_feedback", "feedback_value": feedback})
    tasks[task_id]["status"] = "processing_feedback" # 更新中心状态跟踪器

    # 存储反馈并通知等待中的 ReviewNode
    shared["feedback"] = feedback
    review_event.set()

    return FeedbackResponse(message=f"Feedback '{feedback}' received")


# --- SSE 端点 ---
@app.get("/stream/{task_id}")
async def stream_status(task_id: str):
    """使用 Server-Sent Events 为给定任务流式传输状态更新。"""
    if task_id not in tasks or "sse_queue" not in tasks[task_id]["shared"]:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task or queue not found")

    queue = tasks[task_id]["shared"]["sse_queue"]

    async def event_generator():
        """从任务队列中生成 SSE 消息。"""
        print(f"SSE 流: 客户端已连接 {task_id}")
        try:
            while True:
                # 等待队列中的下一个状态更新
                update = await queue.get()
                if update is None: # 哨兵值表示流结束
                    print(f"SSE 流: 收到 {task_id} 的哨兵，关闭流。")
                    yield f"data: {json.dumps({'status': 'stream_closed'})}\n\n"
                    break

                sse_data = json.dumps(update)
                print(f"SSE 流: 正在发送 {task_id}: {sse_data}")
                yield f"data: {sse_data}\n\n" # SSE 格式: "data: <json>\n\n"
                queue.task_done() # 确认处理队列项

        except asyncio.CancelledError:
            # 如果客户端断开连接，则会发生这种情况
            print(f"SSE 流: 客户端已断开连接 {task_id}。")
        except Exception as e:
            # 记录流式传输期间的意外错误
            print(f"SSE 流: {task_id} 的生成器中发生错误: {e}")
            # 如果可能，可以选择向客户端发送错误消息
            try:
                yield f"data: {json.dumps({'status': 'stream_error', 'error': str(e)})}\n\n"
            except Exception: # 捕获 yield 失败时的错误（例如，连接已关闭）
                pass
        finally:
            print(f"SSE 流: {task_id} 的生成器已完成。")
            # 考虑在此处进行清理（例如，如果不再需要，则删除任务）
            # if task_id in tasks: del tasks[task_id]

    # 使用 FastAPI/Starlette 的 StreamingResponse 进行 SSE
    headers = {'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)

# --- 主执行守卫（用于运行 uvicorn）---
if __name__ == "__main__":
    print("Starting FastAPI server using Uvicorn is recommended:")
    print("uvicorn server:app --reload --host 0.0.0.0 --port 8000")
    # 使用 uvicorn 编程方式的示例（不如 CLI 常见）
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)