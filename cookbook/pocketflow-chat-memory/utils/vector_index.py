import numpy as np
import faiss

def create_index(dimension=1536):
    return faiss.IndexFlatL2(dimension)

def add_vector(index, vector):
    # 确保向量是具有 FAISS 适当形状的 numpy 数组
    vector = np.array(vector).reshape(1, -1).astype(np.float32)
    
    # 将向量添加到索引中
    index.add(vector)
    
    # 返回位置（index.ntotal 是索引中向量的总数）
    return index.ntotal - 1

def search_vectors(index, query_vector, k=1):
    """搜索与查询向量最相似的 k 个向量
    
    参数:
        index: FAISS 索引
        query_vector: 查询向量（numpy 数组或列表）
        k: 返回结果的数量（默认值：1）
        
    返回:
        tuple: (indices, distances)，其中：
            - indices 是索引中的位置列表
            - distances 是相应距离的列表
    """
    # 确保我们不会尝试检索比索引中存在的向量更多的向量
    k = min(k, index.ntotal)
    if k == 0:
        return [], []
        
    # 确保查询是具有 FAISS 适当形状的 numpy 数组
    query_vector = np.array(query_vector).reshape(1, -1).astype(np.float32)
    
    # 搜索索引
    distances, indices = index.search(query_vector, k)
    
    return indices[0].tolist(), distances[0].tolist()# 示例用法
if __name__ == "__main__":
    # 创建一个新索引
    index = create_index(dimension=3)
    
    # 添加一些随机向量并单独跟踪它们
    items = []
    for i in range(5):
        vector = np.random.random(3)
        position = add_vector(index, vector)
        items.append(f"Item {i}")
        print(f"在位置 {position} 添加了向量")
        
    print(f"索引包含 {index.ntotal} 个向量")
    
    # 搜索相似向量
    query = np.random.random(3)
    indices, distances = search_vectors(index, query, k=2)
    
    print("查询:", query)
    print("找到的索引:", indices)
    print("距离:", distances)
    print("检索到的项目:", [items[idx] for idx in indices])