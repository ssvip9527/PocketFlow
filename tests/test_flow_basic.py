# tests/test_flow_basic.py
import unittest
import sys
from pathlib import Path
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent))
from pocketflow import Node, Flow

# --- Node Definitions ---
# Nodes intended for default transitions (>>) should NOT return a specific
# action string from post. Let it return None by default.
# Nodes intended for conditional transitions (-) MUST return the action string.

class NumberNode(Node):
    # 数字节点：将数字设置到共享存储中
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] = self.number
    # post 隐式返回 None - 用于默认转换

class AddNode(Node):
    # 加法节点：将数字加到共享存储中的当前值
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] += self.number
    # post 隐式返回 None - 用于默认转换

class MultiplyNode(Node):
    # 乘法节点：将共享存储中的当前值乘以一个数字
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] *= self.number
    # post 隐式返回 None - 用于默认转换

class CheckPositiveNode(Node):
   # 检查正数节点：根据共享存储中的当前值返回 'positive' 或 'negative'
   # 此节点专为条件分支设计
   def prep(self, shared_storage):
       pass
   def post(self, shared_storage, prep_result, proc_result):
        # 必须返回特定的动作字符串以进行分支
        if shared_storage['current'] >= 0:
            return 'positive'
        else:
            return 'negative'

class NoOpNode(Node):
    # 无操作节点：仅作为占位符节点
    pass # post 隐式返回 None

class EndSignalNode(Node):
    # 结束信号节点：专门用于在结束时返回一个值
    def __init__(self, signal="finished"):
        super().__init__()
        self.signal = signal
    def post(self, shared_storage, prep_result, exec_result):
        return self.signal # 返回一个特定的信号

# --- Test Class ---
class TestFlowBasic(unittest.TestCase):
    # 基本流测试类

    def test_start_method_initialization(self):
        """测试在创建后使用 start() 初始化流。"""
        shared_storage = {}
        n1 = NumberNode(5)
        pipeline = Flow()
        pipeline.start(n1)
        last_action = pipeline.run(shared_storage)
        self.assertEqual(shared_storage['current'], 5)
        # NumberNode.post returns None (default)
        self.assertIsNone(last_action)

    def test_start_method_chaining(self):
        """测试使用 start().next()... 进行流畅链式调用。"""
        shared_storage = {}
        pipeline = Flow()
        # Chain: NumberNode -> AddNode -> MultiplyNode
        # All use default transitions (post returns None)
        pipeline.start(NumberNode(5)).next(AddNode(3)).next(MultiplyNode(2))
        last_action = pipeline.run(shared_storage)
        self.assertEqual(shared_storage['current'], 16)
        # Last node (MultiplyNode) post returns None
        self.assertIsNone(last_action)

    def test_sequence_with_rshift(self):
        """测试使用 >> 的简单线性管道。"""
        shared_storage = {}
        n1 = NumberNode(5)
        n2 = AddNode(3)
        n3 = MultiplyNode(2)

        pipeline = Flow()
        # All default transitions (post returns None)
        pipeline.start(n1) >> n2 >> n3

        last_action = pipeline.run(shared_storage)
        self.assertEqual(shared_storage['current'], 16)
        # Last node (n3: MultiplyNode) post returns None
        self.assertIsNone(last_action)

    def test_branching_positive(self):
        """测试正向分支：CheckPositiveNode 返回 'positive'"""
        shared_storage = {}
        start_node = NumberNode(5)    # post -> None
        check_node = CheckPositiveNode() # post -> 'positive' or 'negative'
        add_if_positive = AddNode(10) # post -> None
        add_if_negative = AddNode(-20) # post -> None (won't run)

        pipeline = Flow()
        # start -> check (default); check branches on 'positive'/'negative'
        pipeline.start(start_node) >> check_node
        check_node - "positive" >> add_if_positive
        check_node - "negative" >> add_if_negative

        # Execution: start_node -> check_node -> add_if_positive
        last_action = pipeline.run(shared_storage)
        self.assertEqual(shared_storage['current'], 15) # 5 + 10
        # Last node executed was add_if_positive, its post returns None
        self.assertIsNone(last_action)

    def test_branching_negative(self):
        """测试负向分支：CheckPositiveNode 返回 'negative'"""
        shared_storage = {}
        start_node = NumberNode(-5)   # post -> None
        check_node = CheckPositiveNode() # post -> 'positive' or 'negative'
        add_if_positive = AddNode(10) # post -> None (won't run)
        add_if_negative = AddNode(-20) # post -> None

        pipeline = Flow()
        pipeline.start(start_node) >> check_node
        check_node - "positive" >> add_if_positive
        check_node - "negative" >> add_if_negative

        # Execution: start_node -> check_node -> add_if_negative
        last_action = pipeline.run(shared_storage)
        self.assertEqual(shared_storage['current'], -25) # -5 + -20
        # Last node executed was add_if_negative, its post returns None
        self.assertIsNone(last_action)

    def test_cycle_until_negative_ends_with_signal(self):
        """测试循环，以返回信号的节点结束"""
        shared_storage = {}
        n1 = NumberNode(10)           # post -> None
        check = CheckPositiveNode()   # post -> 'positive' or 'negative'
        subtract3 = AddNode(-3)       # post -> None
        end_node = EndSignalNode("cycle_done") # post -> "cycle_done"

        pipeline = Flow()
        pipeline.start(n1) >> check
        # Branching from CheckPositiveNode
        check - 'positive' >> subtract3
        check - 'negative' >> end_node # End on negative branch
        # After subtracting, go back to check (default transition)
        subtract3 >> check

        # Execution: n1->check->sub3->check->sub3->check->sub3->check->sub3->check->end_node
        last_action = pipeline.run(shared_storage)
        self.assertEqual(shared_storage['current'], -2) # 10 -> 7 -> 4 -> 1 -> -2
        # Last node executed was end_node, its post returns "cycle_done"
        self.assertEqual(last_action, "cycle_done")

    def test_flow_ends_warning_default_missing(self):
        """测试当需要默认转换但未找到时的警告"""
        shared_storage = {}
        # 返回特定动作的节点
        class ActionNode(Node):
            # 动作节点：返回一个特定的动作字符串
            def post(self, *args): return "specific_action"
        start_node = ActionNode()
        next_node = NoOpNode()

        pipeline = Flow()
        pipeline.start(start_node)
        # 仅为特定动作定义后续节点
        start_node - "specific_action" >> next_node

        # 使 start_node 返回一个特定动作，触发特定搜索
        start_node.post = lambda *args: "specific_action"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # 运行流。start_node 运行，post 返回 None。
            # 流寻找 "default"，但只存在 "specific_action"。
            last_action = pipeline.run(shared_storage)

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            # 警告消息应指示未找到 "default"
            self.assertIn("Flow ends: 'None' not found in ['specific_action']", str(w[-1].message))
        # 最后一个动作来自 start_node 的 post
        self.assertIsNone(last_action)

    def test_flow_ends_warning_specific_missing(self):
        """测试当返回特定动作但未找到时的警告"""
        shared_storage = {}
        # Node that returns a specific action from post
        class ActionNode(Node):
            def post(self, *args): return "specific_action"
        start_node = ActionNode()
        next_node = NoOpNode()

        pipeline = Flow()
        pipeline.start(start_node)
        # Define successor only for "default"
        start_node >> next_node # same as start_node.next(next_node, "default")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Run flow. start_node runs, post returns "specific_action".
            # Flow looks for "specific_action", but only "default" exists.
            last_action = pipeline.run(shared_storage)

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            # Warning message should indicate "specific_action" wasn't found
            self.assertIn("Flow ends: 'specific_action' not found in ['default']", str(w[-1].message))
        # Last action is from start_node's post
        self.assertEqual(last_action, "specific_action")


if __name__ == '__main__':
    unittest.main()