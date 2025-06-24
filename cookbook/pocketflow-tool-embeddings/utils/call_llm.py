import os
from openai import OpenAI

# 如果使用系统环境变量，则无需使用 dotenv
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt):    
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content
    
if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(call_llm(prompt))