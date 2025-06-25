import asyncio
from pocketflow import AsyncNode, AsyncFlow
from utils import call_llm

class AsyncHinter(AsyncNode):
    async def prep_async(self, shared):
        # 等待来自猜词者的消息（或开始时的空字符串）
        guess = await shared["hinter_queue"].get()
        if guess == "GAME_OVER":
            return None
        return shared["target_word"], shared["forbidden_words"], shared.get("past_guesses", [])

    async def exec_async(self, inputs):
        if inputs is None:
            return None
        target, forbidden, past_guesses = inputs
        prompt = f"为 '{target}' 生成提示\n禁用词: {forbidden}"
        if past_guesses:
            prompt += f"\n之前错误的猜测: {past_guesses}\n使提示更具体。"
        prompt += "\n最多使用5个词。"
        
        hint = call_llm(prompt)
        print(f"\n提示者: 这是你的提示 - {hint}")
        return hint

    async def post_async(self, shared, prep_res, exec_res):
        if exec_res is None:
            return "end"
        # 将提示发送给猜词者
        await shared["guesser_queue"].put(exec_res)
        return "continue"

class AsyncGuesser(AsyncNode):
    async def prep_async(self, shared):
        # 等待来自提示者的提示
        hint = await shared["guesser_queue"].get()
        return hint, shared.get("past_guesses", [])

    async def exec_async(self, inputs):
        hint, past_guesses = inputs
        prompt = f"根据提示: {hint}, 之前错误的猜测: {past_guesses}, 进行新的猜测。直接回复一个单词:"
        guess = call_llm(prompt)
        print(f"猜词者: 我猜是 - {guess}")
        return guess

    async def post_async(self, shared, prep_res, exec_res):
        # 检查猜测是否正确
        if exec_res.lower() == shared["target_word"].lower():
            print("游戏结束 - 猜测正确！")
            await shared["hinter_queue"].put("GAME_OVER")
            return "end"
            
        # 将猜测存储在共享状态中
        if "past_guesses" not in shared:
            shared["past_guesses"] = []
        shared["past_guesses"].append(exec_res)
        
        # 将猜测发送给提示者
        await shared["hinter_queue"].put(exec_res)
        return "continue"

async def main():
    # 设置游戏
    shared = {
        "target_word": "nostalgic",
        "forbidden_words": ["memory", "past", "remember", "feeling", "longing"],
        "hinter_queue": asyncio.Queue(),
        "guesser_queue": asyncio.Queue()
    }
    
    print("=========== 禁忌游戏开始！===========")
    print(f"目标词: {shared['target_word']}")
    print(f"禁用词: {shared['forbidden_words']}")
    print("====================================")

    # 通过向提示者发送空猜测进行初始化
    await shared["hinter_queue"].put("")

    # 创建节点和流程
    hinter = AsyncHinter()
    guesser = AsyncGuesser()

    # 设置流程
    hinter_flow = AsyncFlow(start=hinter)
    guesser_flow = AsyncFlow(start=guesser)

    # 连接节点自身以进行循环
    hinter - "continue" >> hinter
    guesser - "continue" >> guesser

    # 并发运行两个代理
    await asyncio.gather(
        hinter_flow.run_async(shared),
        guesser_flow.run_async(shared)
    )
    
    print("=========== 游戏完成！===========")

if __name__ == "__main__":
    asyncio.run(main())
