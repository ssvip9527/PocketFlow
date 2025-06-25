# LLM 流式传输与中断

演示了具有用户中断功能的实时 LLM 响应流式传输。

- 更多内容请查看 [Substack 帖子教程](https://zacharyhuang.substack.com/p/streaming-llm-responses-tutorial)！

## 特性

- 实时显示 LLM 生成的响应
- 随时通过 ENTER 键中断用户

## 运行

```bash
pip install -r requirements.txt
python main.py
```

## 工作原理

StreamNode：
1. 创建中断监听线程
2. 从 LLM 获取内容块
3. 实时显示内容块
4. 处理用户中断

## API 密钥

默认情况下，演示使用伪造的流式响应。要使用真实的 OpenAI 流式传输：

1. 编辑 main.py，将 `fake_stream_llm` 替换为 `stream_llm`：
```python
# 将此行更改为：
chunks = fake_stream_llm(prompt)
# 更改为：
chunks = stream_llm(prompt)
```

2. 确保您的 OpenAI API 密钥已设置：
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 文件

- `main.py`：StreamNode 实现
- `utils.py`：真实和伪造的 LLM 流式传输函数
 
