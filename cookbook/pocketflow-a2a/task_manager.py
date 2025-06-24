# FILE: pocketflow_a2a_agent/task_manager.py
import logging
from typing import AsyncIterable, Union
import asyncio

# 从您复制的通用代码中导入
from common.server.task_manager import InMemoryTaskManager
from common.types import (
    JSONRPCResponse, SendTaskRequest, SendTaskResponse,
    SendTaskStreamingRequest, SendTaskStreamingResponse, Task, TaskSendParams,
    TaskState, TaskStatus, TextPart, Artifact, UnsupportedOperationError,
    InternalError, InvalidParamsError, 
    Message
)
import common.server.utils as server_utils

# 直接从您的原始PocketFlow文件导入
from flow import create_agent_flow

logger = logging.getLogger(__name__)

class PocketFlowTaskManager(InMemoryTaskManager):
    """ 运行PocketFlow代理的任务管理器实现。 """

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"] # 定义代理接受/输出的内容

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """处理非流式任务请求。"""
        logger.info(f"Received task send request: {request.params.id}")

        # 验证输出模式
        if not server_utils.are_modalities_compatible(
            request.params.acceptedOutputModes, self.SUPPORTED_CONTENT_TYPES
        ):
            logger.warning(
                "Unsupported output mode. Received %s, Support %s",
                request.params.acceptedOutputModes, self.SUPPORTED_CONTENT_TYPES
            )
            return SendTaskResponse(id=request.id, error=server_utils.new_incompatible_types_error(request.id).error)

        # 在存储中插入或更新任务（初始状态：已提交）
        # 我们首先创建任务，以便即使同步执行失败，也可以跟踪其状态
        await self.upsert_task(request.params)
        # 运行前更新状态为工作
        await self.update_store(request.params.id, TaskStatus(state=TaskState.WORKING), [])


        # --- 运行PocketFlow逻辑 ---
        task_params: TaskSendParams = request.params
        query = self._get_user_query(task_params)
        if query is None:
            fail_status = TaskStatus(state=TaskState.FAILED, message=Message(role="agent", parts=[TextPart(text="No text query found")]))
            await self.update_store(task_params.id, fail_status, [])
            return SendTaskResponse(id=request.id, error=InvalidParamsError(message="No text query found in message parts"))

        shared_data = {"question": query}
        agent_flow = create_agent_flow() # 创建流程实例

        try:
            # 运行同步PocketFlow
            # 在真实的异步服务器中，您可能会在单独的线程/进程执行器中运行它，以避免阻塞事件循环。
            # 为简单起见，这里我们直接运行它。如果流程可能挂起，请考虑添加超时。
            logger.info(f"Running PocketFlow for task {task_params.id}...")
            agent_flow.run(shared_data) # 运行流程，就地修改shared_data
            logger.info(f"PocketFlow completed for task {task_params.id}")
            # 访问被流程修改过的原始shared_data字典
            answer_text = shared_data.get("answer", "Agent did not produce a final answer text.")

            # --- 将结果打包成A2A任务 ---
            final_task_status = TaskStatus(state=TaskState.COMPLETED)
            # 将答案打包为artifact
            final_artifact = Artifact(parts=[TextPart(text=answer_text)])

            # 使用最终状态和artifact更新存储中的任务
            final_task = await self.update_store(
                task_params.id, final_task_status, [final_artifact]
            )

            # 准备并返回A2A响应
            task_result = self.append_task_history(final_task, task_params.historyLength)
            return SendTaskResponse(id=request.id, result=task_result)

        except Exception as e:
            logger.error(f"Error executing PocketFlow for task {task_params.id}: {e}", exc_info=True)
            # 更新任务状态为FAILED
            fail_status = TaskStatus(
                state=TaskState.FAILED,
                message=Message(role="agent", parts=[TextPart(text=f"Agent execution failed: {e}")])
            )
            await self.update_store(task_params.id, fail_status, [])
            return SendTaskResponse(id=request.id, error=InternalError(message=f"Agent error: {e}"))

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        """处理流式请求 - 此同步代理未实现。"""
        logger.warning(f"Streaming requested for task {request.params.id}, but not supported by this PocketFlow agent implementation.")
        # 返回一个错误，指示不支持流式传输
        return JSONRPCResponse(id=request.id, error=UnsupportedOperationError(message="Streaming not supported by this agent"))

    def _get_user_query(self, task_send_params: TaskSendParams) -> str | None:
        """从用户消息中提取第一个文本部分。"""
        if not task_send_params.message or not task_send_params.message.parts:
            logger.warning(f"No message parts found for task {task_send_params.id}")
            return None
        for part in task_send_params.message.parts:
            # 确保如果part来自JSON，则将其视为字典
            part_dict = part if isinstance(part, dict) else part.model_dump()
            if part_dict.get("type") == "text" and "text" in part_dict:
                 return part_dict["text"]
        logger.warning(f"No text part found in message for task {task_send_params.id}")
        return None # 未找到文本部分