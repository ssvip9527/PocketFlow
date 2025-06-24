import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pocketflow import Node, BatchNode, Flow

class ArrayChunkNode(BatchNode):
    def __init__(self, chunk_size=10):
        super().__init__()
        self.chunk_size = chunk_size
    
    def prep(self, shared_storage):
        # 从共享存储中获取数组并将其分成块
        array = shared_storage.get('input_array', [])
        chunks = []
        for start in range(0, len(array), self.chunk_size):
            end = min(start + self.chunk_size, len(array))
            chunks.append(array[start: end])
        return chunks
    
    def exec(self, chunk):
        # 处理块并返回其总和
        chunk_sum = sum(chunk)
        return chunk_sum
        
    def post(self, shared_storage, prep_result, proc_result):
        # 将块结果存储在共享存储中
        shared_storage['chunk_results'] = proc_result
        return "default"

class SumReduceNode(Node):
    def prep(self, shared_storage):
        # 从共享存储中获取块结果并求和
        chunk_results = shared_storage.get('chunk_results', [])
        total = sum(chunk_results)
        shared_storage['total'] = total

class TestBatchNode(unittest.TestCase):
    # 批处理节点测试类
    def test_array_chunking(self):
        """
        测试数组是否正确分块
        """
        shared_storage = {
            'input_array': list(range(25))  # [0,1,2,...,24]
        }
        
        chunk_node = ArrayChunkNode(chunk_size=10)
        chunk_node.run(shared_storage)
        results = shared_storage['chunk_results']
        self.assertEqual(results, [45, 145, 110])
        
    def test_map_reduce_sum(self):
        """
        测试一个完整的 Map-Reduce 管道，用于对大型数组求和：
        1. Map：将数组分成块并对每个块求和
        2. Reduce：对所有块的总和求和
        """
        # Create test array: [0,1,2,...,99]
        array = list(range(100))
        expected_sum = sum(array)  # 4950
        
        shared_storage = {
            'input_array': array
        }
        
        # Create nodes
        chunk_node = ArrayChunkNode(chunk_size=10)
        reduce_node = SumReduceNode()
        
        # Connect nodes
        chunk_node >> reduce_node
        
        # Create and run pipeline
        pipeline = Flow(start=chunk_node)
        pipeline.run(shared_storage)
        
        self.assertEqual(shared_storage['total'], expected_sum)
        
    def test_uneven_chunks(self):
        """
        测试 Map-Reduce 在数组长度不能被 chunk_size 整除时是否正常工作
        """
        array = list(range(25))
        expected_sum = sum(array)  # 300
        
        shared_storage = {
            'input_array': array
        }
        
        chunk_node = ArrayChunkNode(chunk_size=10)
        reduce_node = SumReduceNode()
        
        chunk_node >> reduce_node
        pipeline = Flow(start=chunk_node)
        pipeline.run(shared_storage)
        
        self.assertEqual(shared_storage['total'], expected_sum)

    def test_custom_chunk_size(self):
        """
        测试 Map-Reduce 在不同分块大小下是否正常工作
        """
        array = list(range(100))
        expected_sum = sum(array)
        
        shared_storage = {
            'input_array': array
        }
        
        # Use chunk_size=15 instead of default 10
        chunk_node = ArrayChunkNode(chunk_size=15)
        reduce_node = SumReduceNode()
        
        chunk_node >> reduce_node
        pipeline = Flow(start=chunk_node)
        pipeline.run(shared_storage)
        
        self.assertEqual(shared_storage['total'], expected_sum)
        
    def test_single_element_chunks(self):
        """
        测试 chunk_size=1 的极端情况
        """
        array = list(range(5))
        expected_sum = sum(array)
        
        shared_storage = {
            'input_array': array
        }
        
        chunk_node = ArrayChunkNode(chunk_size=1)
        reduce_node = SumReduceNode()
        
        chunk_node >> reduce_node
        pipeline = Flow(start=chunk_node)
        pipeline.run(shared_storage)
        
        self.assertEqual(shared_storage['total'], expected_sum)

    def test_empty_array(self):
        """
        测试空输入数组的边缘情况
        """
        shared_storage = {
            'input_array': []
        }
        
        chunk_node = ArrayChunkNode(chunk_size=10)
        reduce_node = SumReduceNode()
        
        chunk_node >> reduce_node
        pipeline = Flow(start=chunk_node)
        pipeline.run(shared_storage)
        
        self.assertEqual(shared_storage['total'], 0)

if __name__ == '__main__':
    unittest.main()
