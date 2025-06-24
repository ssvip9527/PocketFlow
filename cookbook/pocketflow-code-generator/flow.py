from pocketflow import Flow
from nodes import GenerateTestCases, ImplementFunction, RunTests, Revise

def create_code_generator_flow():
    """创建并返回代码生成器流程。"""
    # 创建节点
    generate_tests = GenerateTestCases()
    implement_function = ImplementFunction()
    run_tests = RunTests()
    revise = Revise()

    # 定义转换
    generate_tests >> implement_function
    implement_function >> run_tests
    run_tests - "failure" >> revise
    revise >> run_tests

    # 创建从测试生成开始的流程
    flow = Flow(start=generate_tests)
    return flow