import asyncio
import json
import uuid
from fastapi import FastAPI, BackgroundTasks, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from flow import create_article_flow

app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 存储活跃任务及其 SSE 队列
active_jobs = {}

def run_article_workflow(job_id: str, topic: str):
    """在后台运行文章工作流"""
    try:
        # 从 active_jobs 中获取预创建的队列
        sse_queue = active_jobs[job_id]
        shared = {
            "topic": topic,
            "sse_queue": sse_queue,
            "sections": [],
            "draft": "",
            "final_article": ""
        }
        
        # 运行工作流
        flow = create_article_flow()
        flow.run(shared)
        
    except Exception as e:
        # 发送错误消息
        error_msg = {"step": "error", "progress": 0, "data": {"error": str(e)}}
        if job_id in active_jobs:
            active_jobs[job_id].put_nowait(error_msg)

@app.post("/start-job")
async def start_job(background_tasks: BackgroundTasks, topic: str = Form(...)):
    """开始新的文章生成任务"""
    job_id = str(uuid.uuid4())
    
    # 立即创建 SSE 队列并注册任务
    sse_queue = asyncio.Queue()
    active_jobs[job_id] = sse_queue
    
    # 启动后台任务
    background_tasks.add_task(run_article_workflow, job_id, topic)
    
    return {"job_id": job_id, "topic": topic, "status": "started"}

@app.get("/progress/{job_id}")
async def get_progress(job_id: str):
    """通过 SSE 流式传输进度更新"""
    
    async def event_stream():
        if job_id not in active_jobs:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return
            
        sse_queue = active_jobs[job_id]
        
        # 发送初始连接确认
        yield f"data: {json.dumps({'step': 'connected', 'progress': 0, 'data': {'message': 'Connected to job progress'}})}\n\n"
        
        try:
            while True:
                # 等待下一个进度更新
                try:
                    # 使用 asyncio.wait_for 避免永远阻塞
                    progress_msg = await asyncio.wait_for(sse_queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(progress_msg)}\n\n"
                    
                    # 如果任务完成，清理并退出
                    if progress_msg.get("step") == "complete":
                        del active_jobs[job_id]
                        break
                        
                except asyncio.TimeoutError:
                    # 发送心跳以保持连接活跃
                    yield f"data: {json.dumps({'heartbeat': True})}\n\n"
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.get("/")
async def get_index():
    """提供主页面"""
    return FileResponse("static/index.html")

@app.get("/progress.html")
async def get_progress_page():
    """提供进度页面"""
    return FileResponse("static/progress.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 