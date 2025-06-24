import click
import logging
import os

# 从您复制的通用代码中导入
from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError

# 导入您的自定义任务管理器（现在从您的原始文件导入）
from task_manager import PocketFlowTaskManager

# --- 配置日志 ---
# 设置INFO级别以查看服务器启动、请求、响应
# 设置DEBUG级别以查看来自客户端的原始响应体
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# 可选地，使过于详细的库静默
# logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("httpcore").setLevel(logging.WARNING)
# logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10003) # Use a different port from other agents
def main(host, port):
    """启动PocketFlow A2A代理服务器。"""
    try:
        # 检查必要的API密钥（如果需要，可添加其他）
        if not os.getenv("OPENAI_API_KEY"):
            raise MissingAPIKeyError("OPENAI_API_KEY environment variable not set.")

        # --- 定义代理卡片 ---
        capabilities = AgentCapabilities(
            streaming=False, # 这个简单的实现是同步的
            pushNotifications=False,
            stateTransitionHistory=False # PocketFlow状态不通过A2A历史暴露
        )
        skill = AgentSkill(
            id="web_research_qa",
            name="Web Research and Answering",
            description="Answers questions using web search results when necessary.",
            tags=["research", "qa", "web search"],
            examples=[
                "Who won the Nobel Prize in Physics 2024?",
                "What is quantum computing?",
                "Summarize the latest news about AI.",
            ],
            # 在TaskManager中定义的输入/输出模式
            inputModes=PocketFlowTaskManager.SUPPORTED_CONTENT_TYPES,
            outputModes=PocketFlowTaskManager.SUPPORTED_CONTENT_TYPES,
        )
        agent_card = AgentCard(
            name="PocketFlow Research Agent (A2A Wrapped)",
            description="A simple research agent based on PocketFlow, made accessible via A2A.",
            url=f"http://{host}:{port}/", # A2A客户端将使用的端点
            version="0.1.0-a2a",
            capabilities=capabilities,
            skills=[skill],
            # 假设此示例没有特定的提供者或认证
            provider=None,
            authentication=None,
            defaultInputModes=PocketFlowTaskManager.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=PocketFlowTaskManager.SUPPORTED_CONTENT_TYPES,
        )

        # --- 初始化并启动服务器 ---
        task_manager = PocketFlowTaskManager() # 实例化您的自定义管理器
        server = A2AServer(
            agent_card=agent_card,
            task_manager=task_manager,
            host=host,
            port=port,
        )

        logger.info(f"Starting PocketFlow A2A server on http://{host}:{port}")
        server.start()

    except MissingAPIKeyError as e:
        logger.error(f"Configuration Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()