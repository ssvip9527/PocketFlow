# tests/test_flow_composition.py
import unittest
import asyncio # Keep import, might be needed if other tests use it indirectly
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pocketflow import Node, Flow

# --- Existing Nodes ---
class NumberNode(Node):
    # 数字节点：将数字设置到共享存储中
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] = self.number
    # post 隐式返回 None

class AddNode(Node):
    # 加法节点：将数字加到共享存储中的当前值
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] += self.number
    # post 隐式返回 None

class MultiplyNode(Node):
    # 乘法节点：将共享存储中的当前值乘以一个数字
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] *= self.number
    # post 隐式返回 None

# --- New Nodes for Action Propagation Test ---
class SignalNode(Node):
    """信号节点：从其 post 方法返回特定信号字符串。"""
    def __init__(self, signal="default_signal"):
        super().__init__()
        self.signal = signal
    # 如果只是发出信号，通常不需要 prep
    def post(self, shared_storage, prep_result, exec_result):
        # 将信号存储在共享存储中以进行验证
        shared_storage['last_signal_emitted'] = self.signal
        return self.signal # 返回特定的动作字符串

class PathNode(Node):
    """指示在外部流中采取了哪个路径的节点。"""
    def __init__(self, path_id):
        super().__init__()
        self.path_id = path_id
    def prep(self, shared_storage):
        shared_storage['path_taken'] = self.path_id
    # post 隐式返回 None

# --- Test Class ---
class TestFlowComposition(unittest.TestCase):
    # 流组合测试类

    # --- 现有测试（未更改）---
    def test_flow_as_node(self):
        """
        1) 创建一个流 (f1)，从 NumberNode(5) 开始，然后是 AddNode(10)，再是 MultiplyNode(2)。
        2) 创建第二个流 (f2)，其起始节点是 f1。
        3) 创建一个包装流 (f3)，包含 f2 以确保正确执行。
        shared_storage['current'] 中预期的最终结果：(5 + 10) * 2 = 30。
        """
        shared_storage = {}
        f1 = Flow(start=NumberNode(5))
        f1 >> AddNode(10) >> MultiplyNode(2)
        f2 = Flow(start=f1)
        f3 = Flow(start=f2)
        f3.run(shared_storage)
        self.assertEqual(shared_storage['current'], 30)

    def test_nested_flow(self):
        """
        演示了正确包装的嵌套流：
        inner_flow: NumberNode(5) -> AddNode(3)
        middle_flow: 从 inner_flow 开始 -> MultiplyNode(4)
        wrapper_flow: 包含 middle_flow 以确保正确执行
        预期最终结果：(5 + 3) * 4 = 32。
        """
        shared_storage = {}
        inner_flow = Flow(start=NumberNode(5))
        inner_flow >> AddNode(3)
        middle_flow = Flow(start=inner_flow)
        middle_flow >> MultiplyNode(4)
        wrapper_flow = Flow(start=middle_flow)
        wrapper_flow.run(shared_storage)
        self.assertEqual(shared_storage['current'], 32)

    def test_flow_chaining_flows(self):
        """
        演示了正确包装的两个流的链式调用：
        flow1: NumberNode(10) -> AddNode(10) # 最终 = 20
        flow2: MultiplyNode(2) # 最终 = 40
        wrapper_flow: 包含 flow1 和 flow2 以确保正确执行
        预期最终结果：(10 + 10) * 2 = 40。
        """
        shared_storage = {}
        numbernode = NumberNode(10)
        numbernode >> AddNode(10)
        flow1 = Flow(start=numbernode)
        flow2 = Flow(start=MultiplyNode(2))
        flow1 >> flow2 # Default transition based on flow1 returning None
        wrapper_flow = Flow(start=flow1)
        wrapper_flow.run(shared_storage)
        self.assertEqual(shared_storage['current'], 40)

    def test_composition_with_action_propagation(self):
        """
        测试外部流是否可以根据内部流中最后一个节点的 post() 返回的动作进行分支。
        """
        shared_storage = {}

        # 1. 定义一个以返回特定动作的节点结束的内部流
        inner_start_node = NumberNode(100)       # current = 100, post -> None
        inner_end_node = SignalNode("inner_done") # post -> "inner_done"
        inner_start_node >> inner_end_node
        # 内部流将执行 start->end，并且 Flow 的执行将返回 "inner_done"
        inner_flow = Flow(start=inner_start_node)

        # 2. 为外部流分支定义目标节点
        path_a_node = PathNode("A") # post -> None
        path_b_node = PathNode("B") # post -> None

        # 3. 定义从内部流开始的外部流
        outer_flow = Flow()
        outer_flow.start(inner_flow) # 使用 start() 方法

        # 4. 根据 inner_flow 对象返回的动作定义分支
        inner_flow - "inner_done" >> path_b_node  # 应采用此路径
        inner_flow - "other_action" >> path_a_node # 不应采用此路径

        # 5. 运行外部流并捕获最后一个动作
        # 执行：inner_start -> inner_end -> path_b
        last_action_outer = outer_flow.run(shared_storage)

        # 6. 断言结果
        # 检查内部流执行后的状态
        self.assertEqual(shared_storage.get('current'), 100)
        self.assertEqual(shared_storage.get('last_signal_emitted'), "inner_done")
        # 检查是否采用了正确的外部路径
        self.assertEqual(shared_storage.get('path_taken'), "B")
        # 检查外部流返回的动作。执行的最后一个节点是
        # path_b_node，其 post 方法返回 None。
        self.assertIsNone(last_action_outer)

if __name__ == '__main__':
    unittest.main()