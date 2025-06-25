import asyncio
import time
import os
from pocketflow import AsyncFlow, AsyncParallelBatchNode
from utils import call_llm

# --- Node Definitions ---

class TranslateTextNodeParallel(AsyncParallelBatchNode):
    """并行翻译README文件到多种语言并保存。"""
    async def prep_async(self, shared):
        """从共享存储中读取文本和目标语言。"""
        text = shared.get("text", "(No text provided)")
        languages = shared.get("languages", [])
        return [(text, lang) for lang in languages]

    async def exec_async(self, data_tuple):
        """为每种目标语言调用异步LLM工具。"""
        text, language = data_tuple
        
        prompt = f"""
Please translate the following markdown file into {language}. 
But keep the original markdown format, links and code blocks.
Directly return the translated text, without any other text or comments.

Original: 
{text}

Translated:"""
        
        result = await call_llm(prompt)
        print(f"已翻译 {language} 文本")
        return {"language": language, "translation": result}

    async def post_async(self, shared, prep_res, exec_res_list):
        """存储 {language: translation} 对的字典并写入文件。"""
        output_dir = shared.get("output_dir", "translations")
        os.makedirs(output_dir, exist_ok=True)
        
        for result in exec_res_list:
            if isinstance(result, dict):
                language = result.get("language", "unknown")
                translation = result.get("translation", "")
                
                filename = os.path.join(output_dir, f"README_{language.upper()}.md")
                try:
                    import aiofiles
                    async with aiofiles.open(filename, "w", encoding="utf-8") as f:
                        await f.write(translation)
                    print(f"Saved translation to {filename}")
                except ImportError:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(translation)
                    print(f"已保存翻译到 {filename} (同步回退)")
                except Exception as e:
                    print(f"写入文件 {filename} 时出错: {e}")
            else:
                print(f"警告: 跳过无效结果项: {result}")
        return "default"

# --- Flow Creation ---

def create_parallel_translation_flow():
    """创建并返回并行翻译流。"""
    translate_node = TranslateTextNodeParallel(max_retries=3)
    return AsyncFlow(start=translate_node)

# --- Main Execution ---

async def main():
    source_readme_path = "../../README.md"
    try:
        with open(source_readme_path, "r", encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到源 README 文件: {source_readme_path}")
        exit(1)
    except Exception as e:
        print(f"读取文件 {source_readme_path} 时出错: {e}")
        exit(1)

    shared = {
        "text": text,
        "languages": ["Chinese", "Spanish", "Japanese", "German", "Russian", "Portuguese", "French", "Korean"],
        "output_dir": "translations"
    }

    translation_flow = create_parallel_translation_flow()

    print(f"开始并行翻译到 {len(shared['languages'])} 种语言...")
    start_time = time.perf_counter()

    await translation_flow.run_async(shared)

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"\n总并行翻译时间: {duration:.4f} 秒")
    print("\n=== 翻译完成 ===")
    print(f"翻译已保存到: {shared['output_dir']}")
    print("============================")

if __name__ == "__main__":
    asyncio.run(main())