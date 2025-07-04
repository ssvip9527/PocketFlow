from starlette.applications import Starlette
from starlette.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request
from common.types import (
    A2ARequest,
    JSONRPCResponse,
    InvalidRequestError,
    JSONParseError,
    GetTaskRequest,
    CancelTaskRequest,
    SendTaskRequest,
    SetTaskPushNotificationRequest,
    GetTaskPushNotificationRequest,
    InternalError,
    AgentCard,
    TaskResubscriptionRequest,
    SendTaskStreamingRequest,
    Message,
)
from pydantic import ValidationError
import json
from typing import AsyncIterable, Any
from common.server.task_manager import TaskManager

import logging

# 配置服务器特有的日志记录器
logger = logging.getLogger("A2AServer")


class A2AServer:
    def __init__(
        self,
        host="0.0.0.0",
        port=5000,
        endpoint="/",
        agent_card: AgentCard = None,
        task_manager: TaskManager = None,
    ):
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.task_manager = task_manager
        self.agent_card = agent_card
        self.app = Starlette()
        self.app.add_route(self.endpoint, self._process_request, methods=["POST"])
        self.app.add_route(
            "/.well-known/agent.json", self._get_agent_card, methods=["GET"]
        )

    def start(self):
        if self.agent_card is None:
            raise ValueError("agent_card is not defined")

        if self.task_manager is None:
            raise ValueError("request_handler is not defined")

        import uvicorn

        # 基本日志配置已移至__main__.py，用于应用程序级别的控制
        uvicorn.run(self.app, host=self.host, port=self.port)

    def _get_agent_card(self, request: Request) -> JSONResponse:
        logger.info("Serving Agent Card request")
        return JSONResponse(self.agent_card.model_dump(exclude_none=True))

    async def _process_request(self, request: Request):
        request_id_for_log = "N/A"  # 如果解析早期失败，则为默认值
        raw_body = b""
        try:
            # Log raw body first
            raw_body = await request.body()
            body = json.loads(raw_body)  # 尝试解析
            request_id_for_log = body.get("id", "N/A")  # 如果可能，获取ID
            logger.info(f"<- Received Request (ID: {request_id_for_log}):\n{json.dumps(body, indent=2)}")

            json_rpc_request = A2ARequest.validate_python(body)

            # 基于方法进行路由（与之前相同）
            if isinstance(json_rpc_request, GetTaskRequest):
                result = await self.task_manager.on_get_task(json_rpc_request)
            elif isinstance(json_rpc_request, SendTaskRequest):
                result = await self.task_manager.on_send_task(json_rpc_request)
            elif isinstance(json_rpc_request, SendTaskStreamingRequest):
                result = await self.task_manager.on_send_task_subscribe(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, CancelTaskRequest):
                result = await self.task_manager.on_cancel_task(json_rpc_request)
            elif isinstance(json_rpc_request, SetTaskPushNotificationRequest):
                result = await self.task_manager.on_set_task_push_notification(json_rpc_request)
            elif isinstance(json_rpc_request, GetTaskPushNotificationRequest):
                result = await self.task_manager.on_get_task_push_notification(json_rpc_request)
            elif isinstance(json_rpc_request, TaskResubscriptionRequest):
                result = await self.task_manager.on_resubscribe_to_task(
                    json_rpc_request
                )
            else:
                logger.warning(f"Unexpected request type: {type(json_rpc_request)}")
                raise ValueError(f"Unexpected request type: {type(request)}")

            return self._create_response(result)  # 将结果传递给响应创建

        except json.decoder.JSONDecodeError as e:
            logger.error(f"JSON Parse Error for Request body: <<<{raw_body.decode('utf-8', errors='replace')}>>>\nError: {e}")
            return self._handle_exception(e, request_id_for_log)  # Pass ID if known
        except ValidationError as e:
             logger.error(f"Request Validation Error (ID: {request_id_for_log}): {e.json()}")
             return self._handle_exception(e, request_id_for_log)
        except Exception as e:
             logger.error(f"Unhandled Exception processing request (ID: {request_id_for_log}): {e}", exc_info=True)
             return self._handle_exception(e, request_id_for_log)  # Pass ID if known

    def _handle_exception(self, e: Exception, req_id=None) -> JSONResponse:  # 接受req_id
        if isinstance(e, json.decoder.JSONDecodeError):
            json_rpc_error = JSONParseError()
        elif isinstance(e, ValidationError):
            json_rpc_error = InvalidRequestError(data=json.loads(e.json()))
        else:
            # 记录完整的异常详细信息
            logger.error(f"Internal Server Error (ReqID: {req_id}): {e}", exc_info=True)
            json_rpc_error = InternalError(message=f"Internal Server Error: {type(e).__name__}")

        response = JSONRPCResponse(id=req_id, error=json_rpc_error)
        response_dump = response.model_dump(exclude_none=True)
        logger.info(f"-> Sending Error Response (ReqID: {req_id}):\n{json.dumps(response_dump, indent=2)}")
        # A2A错误仍然以HTTP 200发送
        return JSONResponse(response_dump, status_code=200)

    def _create_response(self, result: Any) -> JSONResponse | EventSourceResponse:
        if isinstance(result, AsyncIterable):
            # 流式响应
            async def event_generator(result_stream) -> AsyncIterable[dict[str, str]]:
                stream_request_id = None  # 如果可能，从第一个事件中捕获ID
                try:
                    async for item in result_stream:
                        # 记录每个流式项
                        response_json = item.model_dump_json(exclude_none=True)
                        stream_request_id = item.id  # 更新ID
                        logger.info(f"-> Sending SSE Event (ID: {stream_request_id}):\n{json.dumps(json.loads(response_json), indent=2)}")
                        yield {"data": response_json}
                    logger.info(f"SSE Stream ended for request ID: {stream_request_id}")
                except Exception as e:
                    logger.error(f"Error during SSE generation (ReqID: {stream_request_id}): {e}", exc_info=True)
                    # Optionally yield an error event if the protocol allows/requires it
                    # error_payload = JSONRPCResponse(id=stream_request_id, error=InternalError(message=f"SSE Error: {e}"))
                    # yield {"data": error_payload.model_dump_json(exclude_none=True)}

            logger.info("Starting SSE stream...")  # Log stream start
            return EventSourceResponse(event_generator(result))
        elif isinstance(result, JSONRPCResponse):
            # 标准JSON响应
            response_dump = result.model_dump(exclude_none=True)
            log_id = result.id if result.id is not None else "N/A (Notification?)"
            log_prefix = "->"
            log_type = "Response"
            if result.error:
                 log_prefix = "-> Sending Error"
                 log_type = "Error Response"

            logger.info(f"{log_prefix} {log_type} (ID: {log_id}):\n{json.dumps(response_dump, indent=2)}")
            return JSONResponse(response_dump)
        else:
            # 如果任务管理器正确返回，这理想情况下不应该发生
            logger.error(f"Task manager returned unexpected type: {type(result)}")
            err_resp = JSONRPCResponse(id=None, error=InternalError(message="Invalid internal response type"))
            return JSONResponse(err_resp.model_dump(exclude_none=True), status_code=500)
