---
layout: default
title: "(高级) 多智能体"
parent: "设计模式"
nav_order: 6
---

# (高级) 多智能体

多个 [智能体](./flow.md) 可以通过处理子任务和沟通进度来协同工作。
智能体之间的通信通常使用共享存储中的消息队列来实现。

> 大多数情况下，您不需要多智能体。请先从简单的解决方案开始。
{: .best-practice }

### 智能体通信示例：消息队列

这是一个使用 `asyncio.Queue` 实现智能体通信的简单示例。
智能体监听消息，处理它们，并继续监听：

```python
class AgentNode(AsyncNode):
    async def prep_async(self, _):
        message_queue = self.params["messages"]
        message = await message_queue.get()
        print(f"智能体收到：{message}")
        return message

# 创建节点和流
agent = AgentNode()
agent >> agent  # 连接到自身
flow = AsyncFlow(start=agent)

# 创建心跳发送器
async def send_system_messages(message_queue):
    counter = 0
    messages = [
        "系统状态：所有系统运行正常",
        "内存使用：正常",
        "网络连接：稳定",
        "处理负载：最佳"
    ]
    
    while True:
        message = f"{messages[counter % len(messages)]} | timestamp_{counter}"
        await message_queue.put(message)
        counter += 1
        await asyncio.sleep(1)

async def main():
    message_queue = asyncio.Queue()
    shared = {}
    flow.set_params({"messages": message_queue})
    
    # 运行两个协程
    await asyncio.gather(
        flow.run_async(shared),
        send_system_messages(message_queue)
    )
    
asyncio.run(main())
```

输出：

```
智能体收到：系统状态：所有系统运行正常 | timestamp_0
智能体收到：内存使用：正常 | timestamp_1
智能体收到：网络连接：稳定 | timestamp_2
智能体收到：处理负载：最佳 | timestamp_3
```

### 交互式多智能体示例：禁忌游戏

这是一个更复杂的示例，其中两个智能体玩猜词游戏禁忌。
一个智能体提供提示，同时避免禁忌词，另一个智能体尝试猜测目标词：

```python
class AsyncHinter(AsyncNode):
    async def prep_async(self, shared):
        guess = await shared["hinter_queue"].get()
        if guess == "GAME_OVER":
            return None
        return shared["target_word"], shared["forbidden_words"], shared.get("past_guesses", [])

    async def exec_async(self, inputs):
        if inputs is None:
            return None
        target, forbidden, past_guesses = inputs
        prompt = f"为 '{target}' 生成提示\n禁忌词：{forbidden}"
        if past_guesses:
            prompt += f"\n之前错误的猜测：{past_guesses}\n使提示更具体。"
        prompt += "\n最多使用 5 个词。"
        
        hint = call_llm(prompt)
        print(f"\n提示者：这是你的提示 - {hint}")
        return hint

    async def post_async(self, shared, prep_res, exec_res):
        if exec_res is None:
            return "end"
        await shared["guesser_queue"].put(exec_res)
        return "continue"

class AsyncGuesser(AsyncNode):
    async def prep_async(self, shared):
        hint = await shared["guesser_queue"].get()
        return hint, shared.get("past_guesses", [])

    async def exec_async(self, inputs):
        hint, past_guesses = inputs
        prompt = f"给定提示：{hint}，过去错误的猜测：{past_guesses}，进行新的猜测。直接回复一个单词："
        guess = call_llm(prompt)
        print(f"猜测者：我猜是 - {guess}")
        return guess

    async def post_async(self, shared, prep_res, exec_res):
        if exec_res.lower() == shared["target_word"].lower():
            print("游戏结束 - 猜测正确！")
            await shared["hinter_queue"].put("GAME_OVER")
            return "end"
            
        if "past_guesses" not in shared:
            shared["past_guesses"] = []
        shared["past_guesses"].append(exec_res)
        
        await shared["hinter_queue"].put(exec_res)
        return "continue"

async def main():
    # 设置游戏
    shared = {
        "target_word": "怀旧",
        "forbidden_words": ["记忆", "过去", "记住", "感觉", "渴望"],
        "hinter_queue": asyncio.Queue(),
        "guesser_queue": asyncio.Queue()
    }
    
    print("游戏开始！")
    print(f"目标词：{shared['target_word']}")
    print(f"禁忌词：{shared['forbidden_words']}")

    # 通过向提示者发送空猜测来初始化
    await shared["hinter_queue"].put("")

    # 创建节点和流
    hinter = AsyncHinter()
    guesser = AsyncGuesser()

    # 设置流
    hinter_flow = AsyncFlow(start=hinter)
    guesser_flow = AsyncFlow(start=guesser)

    # 连接节点到自身
    hinter - "continue" >> hinter
    guesser - "continue" >> guesser

    # 并发运行两个智能体
    await asyncio.gather(
        hinter_flow.run_async(shared),
        guesser_flow.run_async(shared)
    )

asyncio.run(main())
```

输出：

```
游戏开始！
目标词：怀旧
禁忌词：['记忆', '过去', '记住', '感觉', '渴望']

提示者：这是你的提示 - 思考童年夏日
猜测者：我猜是 - 冰棒

提示者：这是你的提示 - 当童年卡通让你感动时
猜测者：我猜是 - 怀旧

提示者：这是你的提示 - 当老歌打动你时
猜测者：我猜是 - 记忆

提示者：这是你的提示 - 关于童年的那种温暖情感
猜测者：我猜是 - 怀旧
游戏结束 - 猜测正确！
```