import os
import time
from pocketflow import BatchNode, Flow
from utils import call_llm

class TranslateTextNode(BatchNode):
    def prep(self, shared):
        text = shared.get("text", "(No text provided)")
        languages = shared.get("languages", ["Chinese", "Spanish", "Japanese", "German", 
                              "Russian", "Portuguese", "French", "Korean"])
        
        # 为每种语言翻译创建批次
        return [(text, lang) for lang in languages]

    def exec(self, data_tuple):
        text, language = data_tuple
        
        prompt = f"""
Please translate the following markdown file into {language}. 
But keep the original markdown format, links and code blocks.
Directly return the translated text, without any other text or comments.

Original: 
{text}

Translated:"""
        
        result = call_llm(prompt)
        print(f"Translated {language} text")
        return {"language": language, "translation": result}

    def post(self, shared, prep_res, exec_res_list):
        # 如果输出目录不存在，则创建它
        output_dir = shared.get("output_dir", "translations")
        os.makedirs(output_dir, exist_ok=True)
        
        # 将每个翻译写入文件
        for result in exec_res_list:
            language, translation = result["language"], result["translation"]
            
            # 写入文件
            filename = os.path.join(output_dir, f"README_{language.upper()}.md")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(translation)
            
            print(f"Saved translation to {filename}")

if __name__ == "__main__":
    # 从 ../../README.md 读取文本
    with open("../../README.md", "r") as f:
        text = f.read()
    
    # 默认设置
    shared = {
        "text": text,
        "languages": ["Chinese", "Spanish", "Japanese", "German", "Russian", "Portuguese", "French", "Korean"],
        "output_dir": "translations"
    }

    # --- 时间测量开始 ---
    print(f"Starting sequential translation into {len(shared['languages'])} languages...")
    start_time = time.perf_counter()

    # Run the translation flow
    translate_node = TranslateTextNode(max_retries=3)
    flow = Flow(start=translate_node)
    flow.run(shared)

    # --- 时间测量结束 ---
    end_time = time.perf_counter()
    duration = end_time - start_time

    print(f"\n总顺序翻译时间: {duration:.4f} 秒") # 打印持续时间
    print("\n=== Translation Complete ===")
    print(f"Translations saved to: {shared['output_dir']}")
    print("============================")