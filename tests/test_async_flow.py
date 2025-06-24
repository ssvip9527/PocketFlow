import unittest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pocketflow import Node, AsyncNode, AsyncFlow

class AsyncNumberNode(AsyncNode):
    """
    简单的异步节点，将 'current' 设置为给定数字。
    演示了如何覆盖 .process() (同步) 并使用
    post_async() 进行异步部分。
    """
    def __init__(self, number):
        super().__init__()
        self.number = number

    async def prep_async(self, shared_storage):
        # 异步节点内允许同步工作，
        # 但最终的“条件”由 post_async() 决定。
        shared_storage['current'] = self.number
        return "set_number"

    async def post_async(self, shared_storage, prep_result, proc_result):
        # 可能在此处执行异步任务
        await asyncio.sleep(0.01)
        # 返回流程的条件
        return "number_set"

class AsyncIncrementNode(AsyncNode):
    """
    演示了异步递增 'current' 值。
    """
    async def prep_async(self, shared_storage):
        shared_storage['current'] = shared_storage.get('current', 0) + 1
        return "incremented"

    async def post_async(self, shared_storage, prep_result, proc_result):
        await asyncio.sleep(0.01)  # 模拟异步 I/O
        return "done"

class AsyncSignalNode(AsyncNode):
    """ 一个异步节点，从 post_async 返回特定的信号字符串。 """
    def __init__(self, signal="default_async_signal"):
        super().__init__()
        self.signal = signal

    # No prep needed usually if just signaling
    async def prep_async(self, shared_storage):
        await asyncio.sleep(0.01) # 模拟异步工作

    async def post_async(self, shared_storage, prep_result, exec_result):
        # 将信号存储在共享存储中以进行验证
        shared_storage['last_async_signal_emitted'] = self.signal
        await asyncio.sleep(0.01) # 模拟异步工作
        print(self.signal)
        return self.signal # 返回特定的动作字符串

class AsyncPathNode(AsyncNode):
    """ 一个异步节点，用于指示在外部流中采取了哪个路径。 """
    def __init__(self, path_id):
        super().__init__()
        self.path_id = path_id

    async def prep_async(self, shared_storage):
        await asyncio.sleep(0.01) # 模拟异步工作
        shared_storage['async_path_taken'] = self.path_id

    # post_async implicitly returns None (for default transition out if needed)
    async def post_async(self, shared_storage, prep_result, exec_result):
         await asyncio.sleep(0.01)
         # 默认返回 None

class TestAsyncNode(unittest.TestCase):
    """
    独立测试 AsyncNode (及其子类) (不在流程中)。
    """
    def test_async_number_node_direct_call(self):
        """
        尽管 AsyncNumberNode 是为异步流设计的，
        我们仍然可以通过调用 run_async() 直接测试它。
        """
        async def run_node():
            node = AsyncNumberNode(42)
            shared_storage = {}
            condition = await node.run_async(shared_storage)
            return shared_storage, condition

        shared_storage, condition = asyncio.run(run_node())
        self.assertEqual(shared_storage['current'], 42)
        self.assertEqual(condition, "number_set")

    def test_async_increment_node_direct_call(self):
        async def run_node():
            node = AsyncIncrementNode()
            shared_storage = {'current': 10}
            condition = await node.run_async(shared_storage)
            return shared_storage, condition

        shared_storage, condition = asyncio.run(run_node())
        self.assertEqual(shared_storage['current'], 11)
        self.assertEqual(condition, "done")


class TestAsyncFlow(unittest.TestCase):
    """
    测试 AsyncFlow 如何编排多个异步节点。
    """
    def test_simple_async_flow(self):
        """
        流程:
          1) AsyncNumberNode(5) -> 将 'current' 设置为 5
          2) AsyncIncrementNode() -> 将 'current' 递增到 6
        """

        # Create our nodes
        start = AsyncNumberNode(5)
        inc_node = AsyncIncrementNode()

        # Chain them: start >> inc_node
        start - "number_set" >> inc_node

        # Create an AsyncFlow with start
        flow = AsyncFlow(start)

        # We'll run the flow synchronously (which under the hood is asyncio.run())
        shared_storage = {}
        asyncio.run(flow.run_async(shared_storage))

        self.assertEqual(shared_storage['current'], 6)

    def test_async_flow_branching(self):
        """
        演示一个分支场景，其中我们返回不同的条件。
        例如，你可以在 post_async 中有一个异步节点，返回 "go_left" 或 "go_right"，
        但这里为了演示，我们将其保持简单。
        """

        class BranchingAsyncNode(AsyncNode):
            def exec(self, data):
                value = shared_storage.get("value", 0)
                shared_storage["value"] = value
                # 我们将根据 'value' 是否为正来决定分支
                return None

            async def post_async(self, shared_storage, prep_result, proc_result):
                await asyncio.sleep(0.01)
                if shared_storage["value"] >= 0:
                    return "positive_branch"
                else:
                    return "negative_branch"

        class PositiveNode(Node):
            def exec(self, data):
                shared_storage["path"] = "positive"
                return None

        class NegativeNode(Node):
            def exec(self, data):
                shared_storage["path"] = "negative"
                return None

        shared_storage = {"value": 10}

        start = BranchingAsyncNode()
        positive_node = PositiveNode()
        negative_node = NegativeNode()

        # Condition-based chaining
        start - "positive_branch" >> positive_node
        start - "negative_branch" >> negative_node

        flow = AsyncFlow(start)
        asyncio.run(flow.run_async(shared_storage))

        self.assertEqual(shared_storage["path"], "positive", 
                         "Should have taken the positive branch")

    def test_async_composition_with_action_propagation(self):
        """
        测试 AsyncFlow 根据嵌套 AsyncFlow 最后一个节点的动作进行分支。
        """
        async def run_test():
            shared_storage = {}

            # 1. 定义一个以 AsyncSignalNode 结尾的内部异步流
            # 使用现有的 AsyncNumberNode，它应该从 post_async 隐式返回 None
            inner_start_node = AsyncNumberNode(200)
            inner_end_node = AsyncSignalNode("async_inner_done") # post_async -> "async_inner_done"
            inner_start_node - "number_set" >> inner_end_node
            # 内部流将执行 start->end，Flow exec 返回 "async_inner_done"
            inner_flow = AsyncFlow(start=inner_start_node)

            # 2. 为外部流分支定义目标异步节点
            path_a_node = AsyncPathNode("AsyncA") # post_async -> None
            path_b_node = AsyncPathNode("AsyncB") # post_async -> None

            # 3. 定义从内部异步流开始的外部异步流
            outer_flow = AsyncFlow(start=inner_flow)

            # 将外部流链接到根据内部流结果进行分支
            outer_flow - "async_inner_done" >> path_a_node
            outer_flow - AsyncFlow.DEFAULT_TRANSITION >> path_b_node # 不应被采用

            # 5. Run the outer async flow and capture the last action
            # Execution: inner_start -> inner_end -> path_b
            last_action_outer = await outer_flow.run_async(shared_storage)

            # 6. Return results for assertion
            return shared_storage, last_action_outer

        # Run the async test function
        shared_storage, last_action_outer = asyncio.run(run_test())

        # 7. Assert the results
        # Check state after inner flow execution
        self.assertEqual(shared_storage.get('current'), 200) # From AsyncNumberNode
        self.assertEqual(shared_storage.get('last_async_signal_emitted'), "async_inner_done")
        # Check that the correct outer path was taken
        self.assertEqual(shared_storage.get('async_path_taken'), "AsyncB")
        # Check the action returned by the outer flow. The last node executed was
        # path_b_node, which returns None from its post_async method.
        self.assertIsNone(last_action_outer)

if __name__ == '__main__':
    unittest.main()
