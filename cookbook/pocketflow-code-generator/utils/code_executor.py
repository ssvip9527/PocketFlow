import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr

def execute_python(function_code, input):
    try:
        namespace = {"__builtins__": __builtins__}
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(function_code, namespace)
            
            if "run_code" not in namespace:
                return None, "未找到函数 'run_code'"
            
            run_code = namespace["run_code"]
            
            if isinstance(input, dict):
                result = run_code(**input)
            elif isinstance(input, (list, tuple)):
                result = run_code(*input)
            else:
                result = run_code(input)
            
            return result, None
                
    except Exception as e:
        return None, f"执行错误: {type(e).__name__}: {str(e)}"

if __name__ == "__main__":
    # 测试 1: 正常工作的函数
    function_code = """
def run_code(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    input = {"nums": [2, 7, 11, 15], "target": 9}
    output, error = execute_python(function_code, input)
    print(f"输出: {output}")
    print(f"错误: {error}")
    
    # 测试 2: 带有错误的函数
    broken_function_code = """
def run_code(nums, target):
    return nums[100]  # 索引错误
"""
    
    output2, error2 = execute_python(broken_function_code, input)
    print(f"输出: {output2}")
    print(f"错误: {error2}")