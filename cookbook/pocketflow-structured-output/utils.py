import os
from openai import OpenAI

# 初始化 OpenAI 客户端
# 确保您的 OPENAI_API_KEY 环境变量已设置
client = OpenAI()

def call_llm(prompt: str, model: str = "gpt-4-turbo-preview") -> str:
    """调用 OpenAI LLM 并返回其响应。"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0 # 确保确定性输出
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"调用 LLM 时发生错误: {e}")
        return ""

# --- 测试函数 ---
if __name__ == "__main__":
    # 确保设置了 API 密钥
    if "OPENAI_API_KEY" not in os.environ:
        print("错误: OPENAI_API_KEY 环境变量未设置。请在运行测试前设置它。")
        exit(1)

    print("\n=== 测试 LLM 调用 ===")
    test_prompt = "你好，世界！请用一句话回答。"
    llm_response = call_llm(test_prompt)
    print(f"提示: {test_prompt}")
    print(f"LLM 响应: {llm_response}")
    print("=======================\n")

    # 预期一个简短的响应
    assert len(llm_response) > 0, "测试失败: LLM 响应为空"
    print("✅ LLM 调用测试通过。")