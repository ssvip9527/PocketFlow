import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from flow import create_streaming_chat_flow

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_chat_interface():
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # 为此连接初始化对话历史
    shared_store = {
        "websocket": websocket,
        "conversation_history": []
    }
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 仅更新当前消息，保留对话历史
            shared_store["user_message"] = message.get("content", "")
            
            flow = create_streaming_chat_flow()
            await flow.run_async(shared_store)
            
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 