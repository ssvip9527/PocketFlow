import sys
from flow import create_code_generator_flow

def main():
    """运行 PocketFlow 代码生成器应用程序。"""
    print("正在启动 PocketFlow 代码生成器...")
    
    # 检查是否提供了问题作为参数
    if len(sys.argv) > 1:
        problem = " ".join(sys.argv[1:])
    else:
        # 默认的两数之和问题
        problem = """两数之和

给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

示例 1:
输入: nums = [2,7,11,15], target = 9
输出: [0,1]

示例 2:
输入: nums = [3,2,4], target = 6
输出: [1,2]

示例 3:
输入: nums = [3,3], target = 6
输出: [0,1]"""

    shared = {
        "problem": problem,
        "test_cases": [],  # 将填充 [{name, input, expected}, ...]
        "function_code": "",
        "test_results": [],
        "iteration_count": 0,
        "max_iterations": 5
    }

    # 创建并运行流程
    flow = create_code_generator_flow()
    flow.run(shared)
    
    print("\n=== 最终结果 ===")
    print(f"问题: {shared['problem'][:50]}...")
    print(f"迭代次数: {shared['iteration_count']}")
    print(f"函数:\n{shared['function_code']}")
    print(f"测试结果: {len([r for r in shared['test_results'] if r['passed']])}/{len(shared['test_results'])} 通过")

if __name__ == "__main__":
    main()