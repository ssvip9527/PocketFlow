使用 PocketFlow 和 Streamlit 构建的人机协作 (HITL) 图像生成应用程序。输入文本提示，使用 OpenAI 生成图像，并批准/重新生成结果。

<p align="center">
  <img 
    src="./assets/banner.png" width="800"
  />
</p>

## 功能

-   **图像生成:** 使用 OpenAI 的 `gpt-image-1` 模型从文本提示生成图像
-   **人工审查:** 交互式界面，用于批准或重新生成图像
-   **状态机:** 清晰的基于状态的工作流（`initial_input` → `user_feedback` → `final`）
-   **PocketFlow 集成:** 使用 PocketFlow `Node` 和 `Flow` 进行图像生成，内置重试功能
-   **会话状态管理:** Streamlit 会话状态充当 PocketFlow 的共享存储
-   **内存中图像:** 图像以 base64 字符串形式存储，无需磁盘存储

## 如何运行

1.  **设置 OpenAI API 密钥:**
    ```bash
    export OPENAI_API_KEY="your-openai-api-key"
    ```

2.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **运行 Streamlit 应用程序:**
    ```bash
    streamlit run app.py
    ```

4.  **访问 Web UI:**
    打开 Streamlit 提供的 URL（通常是 `http://localhost:8501`）。

## 用法

1.  **输入提示**: 描述您想要生成的图像
2.  **生成**: 点击“生成图像”创建图像
3.  **审查**: 查看生成的图像并选择:
    -   **批准**: 接受图像并进入最终结果
    -   **重新生成**: 使用相同的提示生成新图像
4.  **最终**: 查看批准的图像并选择重新开始

## 文件

-   [`app.py`](./app.py): 带有基于状态 UI 的主 Streamlit 应用程序
-   [`nodes.py`](./nodes.py): PocketFlow `GenerateImageNode` 定义
-   [`flow.py`](./flow.py): 用于图像生成的 PocketFlow `Flow`
-   [`utils/generate_image.py`](./utils/generate_image.py): OpenAI 图像生成实用程序
-   [`requirements.txt`](./requirements.txt): 项目依赖
-   [`docs/design.md`](./docs/design.md): 系统设计文档
-   [`README.md`](./README.md): 本文件
