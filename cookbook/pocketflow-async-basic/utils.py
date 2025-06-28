import asyncio
import aiohttp
from openai import AsyncOpenAI

async def fetch_recipes(ingredient):
    """异步从API获取菜谱。"""
    print(f"Fetching recipes for {ingredient}...")
    
    # 模拟带延迟的API调用
    await asyncio.sleep(1)
    
    # 模拟菜谱（在实际应用中，会从API获取）
    recipes = [
        f"{ingredient} Stir Fry",
        f"Grilled {ingredient} with Herbs",
        f"Baked {ingredient} with Vegetables"
    ]
    
    print(f"Found {len(recipes)} recipes.")
    
    return recipes

async def call_llm_async(prompt):
    """进行异步LLM调用。"""
    print("\nSuggesting best recipe...")
    
    # 模拟带延迟的LLM调用
    await asyncio.sleep(1)
    
    # 模拟LLM响应（在实际应用中，会调用OpenAI）
    recipes = prompt.split(": ")[1].split(", ")
    suggestion = recipes[1]  # 总是建议第二个菜谱
    
    print(f"How about: {suggestion}")
    return suggestion

async def get_user_input(prompt):
    """异步获取用户输入。"""
    # 创建事件循环来处理异步输入
    loop = asyncio.get_event_loop()
    
    # 以非阻塞方式获取输入
    answer = await loop.run_in_executor(None, input, prompt)

    return answer.lower() 