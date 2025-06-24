import sys
from flow import create_chain_of_thought_flow

def main():
    # 默认问题
    default_question = "You keep rolling a fair die until you roll three, four, five in that order consecutively on three rolls. What is the probability that you roll the die an odd number of times?"
    
    # 如果通过 -- 提供，则从命令行获取问题
    question = default_question
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            question = arg[2:]
            break
    
    print(f"🤔 正在处理问题: {question}")   

    # 创建流程
    cot_flow = create_chain_of_thought_flow()

    # 设置共享状态
    shared = {
        "problem": question,
        "thoughts": [],
        "current_thought_number": 0,
        "total_thoughts_estimate": 10,
        "solution": None
    }
    
    # 运行流程
    cot_flow.run(shared)
    
if __name__ == "__main__":
    main()