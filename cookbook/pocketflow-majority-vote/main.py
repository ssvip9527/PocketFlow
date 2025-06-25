import argparse
from pocketflow import BatchNode, Flow
import collections
from utils import call_llm
import yaml

class MajorityVoteNode(BatchNode):
    def prep(self, shared):
        question = shared.get("question", "(未提供问题)")
        attempts_count = shared.get("num_tries", 3)
        return [question for _ in range(attempts_count)]

    def exec(self, single_question: str):
        prompt = f"""
你是一个乐于助人的助手。请回答以下用户的问题。
问题: {single_question}

请严格使用以下 YAML 结构返回：
```yaml
thinking: |
    (你的思考过程在这里)
answer: 0.123 # 最终答案为保留三位小数的十进制数
```"""
        raw_response = call_llm(prompt)
        yaml_part = raw_response.split("```yaml")[1].split("```")[0].strip()
        parsed = yaml.safe_load(yaml_part)

        # 验证我们至少有 'answer' 字段
        if not isinstance(parsed, dict) or 'answer' not in parsed:
            raise RuntimeError(f"YAML 中缺少 'answer': {parsed}")

        # 仅返回 'answer' 字段用于多数投票。
        return str(parsed['answer'])
    
    def exec_fallback(self, prep_res, exc):
        return None

    def post(self, shared, prep_res, exec_res_list):
        # 计算非 None 答案的频率
        exec_res_list = [res for res in exec_res_list if res is not None]
        counter = collections.Counter(exec_res_list)
        best_answer, freq = counter.most_common(1)[0]

        # 存储最终结果
        shared["majority_answer"] = best_answer

        print("========================")
        print("所有结构化答案:", exec_res_list)
        print("多数投票 =>", best_answer)
        print("频率 =>", freq)
        print("========================")

        # 结束流程
        return "end"

if __name__ == "__main__":
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="对问题运行多数投票推理")
    parser.add_argument("--problem", type=str, help="您要解决的推理问题")
    parser.add_argument("--tries", type=int, default=5, help="尝试次数 (默认: 5)")
    args = parser.parse_args()
    
    # 如果未提供问题，则使用默认问题
    default_problem = """你在一间鞋厂工作。你面前有三双鞋（六只独立的鞋），尺码如下：两只 4 码，两只 5 码，两只 6 码。工厂将“可接受的配对”定义为尺码差异最多为一码的两只鞋（例如，5 码和 6 码将是可接受的配对）。如果你闭上眼睛，随机抽取三双鞋，不放回，那么你最终抽到三双可接受的配对的概率是多少？"""
    
    shared = {
        "question": args.problem if args.problem else default_problem,
        "num_tries": args.tries
    }

    majority_node = MajorityVoteNode()
    flow = Flow(start=majority_node)
    flow.run(shared)

    print("\n=== 最终答案 ===")
    print(shared["majority_answer"])
    print("====================")