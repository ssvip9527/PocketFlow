import yaml
from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
from utils.code_executor import execute_python

class GenerateTestCases(Node):
    def prep(self, shared):
        return shared["problem"]

    def exec(self, problem):
        prompt = f"""为这个编码问题生成5-7个测试用例：

{problem}

以包含推理的YAML格式输出：
```yaml
reasoning: |
    输入参数应为：param1作为字符串，param2作为数字。
    为了测试函数，我将考虑基本情况、边界情况和极端情况。
    对于这个问题，我需要测试...
test_cases:
  - name: "基本情况"
    input: {{param1: value1, param2: value2}}
    expected: result1
  - name: "边缘情况 - 空"
    input: {{param1: value3, param2: value4}}
    expected: result2
```"""
        response = call_llm(prompt)
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)
        
        # 验证断言
        assert "test_cases" in result, "结果必须包含 'test_cases' 字段"
        assert isinstance(result["test_cases"], list), "'test_cases' 必须是列表"
        
        for i, test_case in enumerate(result["test_cases"]):
            assert "name" in test_case, f"测试用例 {i} 缺少 'name' 字段"
            assert isinstance(test_case["name"], str), f"测试用例 {i} 的 'name' 必须是字符串"
            assert "input" in test_case, f"测试用例 {i} 缺少 'input' 字段"
            assert isinstance(test_case["input"], dict), f"测试用例 {i} 的 'input' 必须是字典"
            assert "expected" in test_case, f"测试用例 {i} 缺少 'expected' 字段"
        
        return result

    def post(self, shared, prep_res, exec_res):
        shared["test_cases"] = exec_res["test_cases"]
        
        # 打印所有生成的测试用例
        print(f"\n=== 生成的 {len(exec_res['test_cases'])} 个测试用例 ===")
        for i, test_case in enumerate(exec_res["test_cases"], 1):
            print(f"{i}. {test_case['name']}")
            print(f"   输入: {test_case['input']}")
            print(f"   预期: {test_case['expected']}")

class ImplementFunction(Node):
    def prep(self, shared):
        return shared["problem"], shared["test_cases"]

    def exec(self, inputs):
        problem, test_cases = inputs
        
        # 为提示信息格式化测试用例
        formatted_tests = ""
        for i, test in enumerate(test_cases, 1):
            formatted_tests += f"{i}. {test['name']}\n"
            formatted_tests += f"   输入: {test['input']}\n"
            formatted_tests += f"   预期: {test['expected']}\n\n"
        
        prompt = f"""为这个问题实现一个解决方案：

{problem}

要考虑的测试用例：
{formatted_tests}

重要提示：函数名称必须是 "run_code"

以YAML格式输出：
```yaml
reasoning: |
    为了实现这个函数，我将...
    我的方法是...
function_code: |
    def run_code(...):
        # 你的实现
        return result
```"""
        response = call_llm(prompt)
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)
        
        # 验证断言
        assert "function_code" in result, "结果必须包含 'function_code' 字段"
        assert isinstance(result["function_code"], str), "'function_code' 必须是字符串"
        assert "def run_code" in result["function_code"], "函数名称必须是 'run_code'"
        
        return result["function_code"]

    def post(self, shared, prep_res, exec_res):
        shared["function_code"] = exec_res
        
        # 打印已实现的函数
        print(f"\n=== 已实现的函数 ===")
        print(exec_res)

class RunTests(BatchNode):
    def prep(self, shared):
        function_code = shared["function_code"]
        test_cases = shared["test_cases"]
        # 返回元组列表 (function_code, test_case)
        return [(function_code, test_case) for test_case in test_cases]

    def exec(self, test_data):
        function_code, test_case = test_data
        output, error = execute_python(function_code, test_case["input"])
        
        if error:
            return {
                "test_case": test_case,
                "passed": False,
                "actual": None,
                "expected": test_case["expected"],
                "error": error
            }
        
        passed = output == test_case["expected"]
        return {
            "test_case": test_case,
            "passed": passed,
            "actual": output,
            "expected": test_case["expected"],
            "error": None if passed else f"Expected {test_case['expected']}, got {output}"
        }

    def post(self, shared, prep_res, exec_res_list):
        shared["test_results"] = exec_res_list
        all_passed = all(result["passed"] for result in exec_res_list)
        shared["iteration_count"] = shared.get("iteration_count", 0) + 1
        
        # 打印测试结果
        passed_count = len([r for r in exec_res_list if r["passed"]])
        total_count = len(exec_res_list)
        print(f"\n=== 测试结果：{passed_count}/{total_count} 通过 ===")
        
        failed_tests = [r for r in exec_res_list if not r["passed"]]
        if failed_tests:
            print("失败的测试：")
            for i, result in enumerate(failed_tests, 1):
                test_case = result['test_case']
                print(f"{i}. {test_case['name']}:")
                if result['error']:
                    print(f"   错误: {result['error']}")
                else:
                    print(f"   输出: {result['actual']}")
                print(f"   预期: {result['expected']}")
        
        if all_passed:
            return "success"
        elif shared["iteration_count"] >= shared.get("max_iterations", 5):
            return "max_iterations"
        else:
            return "failure"

class Revise(Node):
    def prep(self, shared):
        failed_tests = [r for r in shared["test_results"] if not r["passed"]]
        return {
            "problem": shared["problem"],
            "test_cases": shared["test_cases"],
            "function_code": shared["function_code"],
            "failed_tests": failed_tests
        }

    def exec(self, inputs):
        # 格式化当前测试用例
        formatted_tests = ""
        for i, test in enumerate(inputs['test_cases'], 1):
            formatted_tests += f"{i}. {test['name']}\n"
            formatted_tests += f"   输入: {test['input']}\n"
            formatted_tests += f"   预期: {test['expected']}\n\n"
        
        # 格式化失败的测试用例
        formatted_failures = ""
        for i, result in enumerate(inputs['failed_tests'], 1):
            test_case = result['test_case']
            formatted_failures += f"{i}. {test_case['name']}:\n"
            if result['error']:
                formatted_failures += f"   错误: {result['error']}\n"
            else:
                formatted_failures += f"   输出: {result['actual']}\n"
            formatted_failures += f"   预期: {result['expected']}\n\n"

        prompt = f"""Problem: {inputs['problem']}

Current test cases:
{formatted_tests}

Current function:
```python
{inputs['function_code']}
```

Failed tests:
{formatted_failures}

分析失败并以YAML格式输出修订。您可以修改测试用例、函数代码或两者：

```yaml
reasoning: |
    查看失败，我发现...
    问题似乎是...
    我将修改...
test_cases:  # 将测试用例索引（从1开始）映射到修订后的测试用例的字典
  1:
    name: "修订后的测试名称"
    input: {{...}}
    expected: ...
function_code: |  # 如果修改函数，请包含此项
  def run_code(...):
    return ...
```"""
        response = call_llm(prompt)
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)
        
        # 验证断言
        if "test_cases" in result:
            assert isinstance(result["test_cases"], dict), "test_cases 必须是字典"
            for index_str, test_case in result["test_cases"].items():
                assert isinstance(index_str, (str, int)), "test_cases 键必须是字符串或整数"
                assert "name" in test_case, f"修订后的测试用例 {index_str} 缺少 'name' 字段"
                assert "input" in test_case, f"修订后的测试用例 {index_str} 缺少 'input' 字段"
                assert "expected" in test_case, f"修订后的测试用例 {index_str} 缺少 'expected' 字段"
        
        if "function_code" in result:
            assert isinstance(result["function_code"], str), "function_code 必须是字符串"
            assert "def run_code" in result["function_code"], "函数必须命名为 'run_code'"
        
        return result

    def post(self, shared, prep_res, exec_res):
        # 打印正在修订的内容
        print(f"\n=== 修订 (迭代 {shared['iteration_count']}) ===")
        
        # 处理测试用例修订 - 将索引映射到实际测试用例
        if "test_cases" in exec_res:
            current_tests = shared["test_cases"].copy()
            print("修订测试用例：")
            for index_str, revised_test in exec_res["test_cases"].items():
                index = int(index_str) - 1  # 转换为0-based
                if 0 <= index < len(current_tests):
                    old_test = current_tests[index]
                    print(f"  测试 {index_str}: '{old_test['name']}' -> '{revised_test['name']}'")
                    print(f"    旧输入: {old_test['input']}")
                    print(f"    新输入: {revised_test['input']}")
                    print(f"    旧预期: {old_test['expected']}")
                    print(f"    新预期: {revised_test['expected']}")
                    current_tests[index] = revised_test
            shared["test_cases"] = current_tests
            
        if "function_code" in exec_res:
            print("修订函数代码：")
            print("新函数：")
            print(exec_res["function_code"])
            shared["function_code"] = exec_res["function_code"]