import asyncio, warnings, copy, time

# BaseNode 是所有节点的基础类，定义了节点的通用行为和生命周期方法。
class BaseNode:
    def __init__(self):
        # 初始化节点的参数和后继节点字典
        self.params, self.successors = {}, {}

    def set_params(self, params):
        # 设置节点的参数
        self.params = params

    def next(self, node, action="default"):
        # 定义节点的下一个后继节点
        if action in self.successors:
            warnings.warn(f"Overwriting successor for action '{action}'")
        self.successors[action] = node
        return node

    def prep(self, shared):
        # 准备阶段，用于在执行前进行数据准备，子类可重写
        pass

    def exec(self, prep_res):
        # 执行阶段，用于执行节点的核心逻辑，子类可重写
        pass

    def post(self, shared, prep_res, exec_res):
        # 后处理阶段，用于在执行后进行清理或结果处理，子类可重写
        pass

    def _exec(self, prep_res):
        # 内部执行方法，调用 exec 方法
        return self.exec(prep_res)

    def _run(self, shared):
        # 内部运行方法，按顺序调用 prep, _exec, post 方法
        p = self.prep(shared)
        e = self._exec(p)
        return self.post(shared, p, e)

    def run(self, shared):
        # 运行节点，如果存在后继节点则发出警告，建议使用 Flow
        if self.successors:
            warnings.warn("Node won't run successors. Use Flow.")
        return self._run(shared)

    def __rshift__(self, other):
        # 定义 >> 运算符，用于连接节点
        return self.next(other)

    def __sub__(self, action):
        # 定义 - 运算符，用于创建条件转换
        if isinstance(action, str):
            return _ConditionalTransition(self, action)
        raise TypeError("Action must be a string")

# _ConditionalTransition 类用于处理条件转换逻辑
class _ConditionalTransition:
    def __init__(self, src, action):
        # 初始化源节点和动作
        self.src, self.action = src, action

    def __rshift__(self, tgt):
        # 定义 >> 运算符，将目标节点连接到源节点的特定动作
        return self.src.next(tgt, self.action)

# Node 类继承自 BaseNode，增加了重试机制
class Node(BaseNode):
    def __init__(self, max_retries=1, wait=0):
        # 初始化节点，设置最大重试次数和重试间隔
        super().__init__()
        self.max_retries, self.wait = max_retries, wait

    def exec_fallback(self, prep_res, exc):
        # 执行失败时的回退方法，默认重新抛出异常
        raise exc

    def _exec(self, prep_res):
        # 内部执行方法，包含重试逻辑
        for cur_retry in range(self.max_retries):
            try:
                return self.exec(prep_res)
            except Exception as e:
                # 如果是最后一次重试，则调用回退方法
                if cur_retry == self.max_retries - 1:
                    return self.exec_fallback(prep_res, e)
                # 如果设置了等待时间，则暂停
                if self.wait > 0:
                    time.sleep(self.wait)
        raise Exception("Max retries reached")


# BatchNode 类继承自 Node，用于批量处理数据
class BatchNode(Node):
    def _exec(self, items):
        # 批量执行，对每个项调用父类的 _exec 方法
        return [super(BatchNode, self)._exec(i) for i in (items or [])]

# Flow 类继承自 BaseNode，用于定义和管理节点流程
class Flow(BaseNode):
    def __init__(self, start=None):
        # 初始化流程，设置起始节点
        super().__init__()
        self.start_node = start

    def start(self, start):
        # 设置流程的起始节点
        self.start_node = start
        return start

    @staticmethod
    def get_next_node(curr, action):
        # 获取当前节点的下一个后继节点
        nxt = curr.successors.get(action or "default")
        if not nxt and curr.successors:
            warnings.warn(f"Flow ends: '{action}' not found in {list(curr.successors)}")
        return nxt

    def _orch(self, shared, params=None):
        # 流程编排方法，按顺序执行节点
        curr, p, last_action = copy.copy(self.start_node), (params or {**self.params}), None
        while curr:
            curr.set_params(p)
            last_action = curr.run(shared)
            curr = copy.copy(self.get_next_node(curr, last_action))
        return last_action

    def _run(self, shared):
        # 内部运行方法，调用 prep, _orch, post 方法
        p = self.prep(shared)
        o = self._orch(shared)
        return self.post(shared, p, o)

    def post(self, shared, prep_res, exec_res):
        # 后处理阶段，默认返回执行结果
        return exec_res

# BatchFlow 类继承自 Flow，用于批量运行流程
class BatchFlow(Flow):
    def _run(self, shared):
        # 批量运行流程，对每个批处理参数执行编排
        pr = self.prep(shared) or []
        for bp in pr:
            self._orch(shared, {**self.params, **bp})
        return self.post(shared, pr, None)

# AsyncNode 类继承自 Node，用于支持异步操作
class AsyncNode(Node):
    async def prep_async(self, shared):
        # 异步准备阶段，子类可重写
        pass

    async def exec_async(self, prep_res):
        # 异步执行阶段，子类可重写
        pass

    async def exec_fallback_async(self, prep_res, exc):
        # 异步执行失败时的回退方法，默认重新抛出异常
        raise exc

    async def post_async(self, shared, prep_res, exec_res):
        # 异步后处理阶段，子类可重写
        pass

    async def _exec(self, prep_res):
        # 内部异步执行方法，包含重试逻辑
        for cur_retry in range(self.max_retries):
            try:
                return await self.exec_async(prep_res)
            except Exception as e:
                # 如果是最后一次重试，则调用异步回退方法
                if cur_retry == self.max_retries - 1:
                    return await self.exec_fallback_async(prep_res, e)
                # 如果设置了等待时间，则异步暂停
                if self.wait > 0:
                    await asyncio.sleep(self.wait)
        raise Exception("Max retries reached")

    async def run_async(self, shared):
        # 异步运行节点，如果存在后继节点则发出警告，建议使用 AsyncFlow
        if self.successors:
            warnings.warn("Node won't run successors. Use AsyncFlow.")
        return await self._run_async(shared)

    async def _run_async(self, shared):
        # 内部异步运行方法，按顺序调用异步 prep, _exec, post 方法
        p = await self.prep_async(shared)
        e = await self._exec(p)
        return await self.post_async(shared, p, e)

    def _run(self, shared):
        # 覆盖同步运行方法，强制使用异步运行
        raise RuntimeError("Use run_async.")

# AsyncBatchNode 类继承自 AsyncNode 和 BatchNode，用于异步批量处理数据
class AsyncBatchNode(AsyncNode, BatchNode):
    async def _exec(self, items):
        # 异步批量执行，对每个项调用父类的异步 _exec 方法
        return [await super(AsyncBatchNode, self)._exec(i) for i in items]

# AsyncParallelBatchNode 类继承自 AsyncNode 和 BatchNode，用于异步并行批量处理数据
class AsyncParallelBatchNode(AsyncNode, BatchNode):
    async def _exec(self, items):
        # 异步并行批量执行，使用 asyncio.gather 并行运行
        return await asyncio.gather(*(super(AsyncParallelBatchNode, self)._exec(i) for i in items))

# AsyncFlow 类继承自 Flow 和 AsyncNode，用于定义和管理异步节点流程
class AsyncFlow(Flow, AsyncNode):
    async def _orch_async(self, shared, params=None):
        # 异步流程编排方法，按顺序异步执行节点
        curr, p, last_action = copy.copy(self.start_node), (params or {**self.params}), None
        while curr:
            curr.set_params(p)
            # 根据节点类型选择同步或异步运行方法
            last_action = await curr._run_async(shared) if isinstance(curr, AsyncNode) else curr.run(shared)
            curr = copy.copy(self.get_next_node(curr, last_action))
        return last_action

    async def _run_async(self, shared):
        # 内部异步运行方法，调用异步 prep, _orch, post 方法
        p = await self.prep_async(shared)
        o = await self._orch_async(shared)
        return await self.post_async(shared, p, o)

    async def post_async(self, shared, prep_res, exec_res):
        # 异步后处理阶段，默认返回执行结果
        return exec_res

# AsyncBatchFlow 类继承自 AsyncFlow 和 BatchFlow，用于异步批量运行流程
class AsyncBatchFlow(AsyncFlow, BatchFlow):
    async def _run_async(self, shared):
        # 异步批量运行流程，对每个批处理参数异步执行编排
        pr = await self.prep_async(shared) or []
        for bp in pr:
            await self._orch_async(shared, {**self.params, **bp})
        return await self.post_async(shared, pr, None)

# AsyncParallelBatchFlow 类继承自 AsyncFlow 和 BatchFlow，用于异步并行批量运行流程
class AsyncParallelBatchFlow(AsyncFlow, BatchFlow):
    async def _run_async(self, shared):
        # 异步并行批量运行流程，使用 asyncio.gather 并行执行编排
        pr = await self.prep_async(shared) or []
        await asyncio.gather(*(self._orch_async(shared, {**self.params, **bp}) for bp in pr))
        return await self.post_async(shared, pr, None)