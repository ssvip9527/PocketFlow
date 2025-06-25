import sys
from flow import offline_flow, online_flow

def run_rag_demo():
    """
    运行 RAG 系统的演示。
    
    此函数:
    1. 索引一组示例文档（离线流）
    2. 从命令行获取查询
    3. 检索最相关的文档（在线流）
    4. 使用 LLM 生成答案
    """

    # 示例文本 - 受益于 RAG 的专业/虚构内容
    texts = [
        # PocketFlow 框架
        """Pocket Flow 是一个 100 行的极简 LLM 框架
        轻量级: 仅 100 行。零膨胀，零依赖，零供应商锁定。
        富有表现力: 您喜欢的一切——（多）代理，工作流，RAG 等。
        代理编码: 让 AI 代理（例如，Cursor AI）构建代理——10 倍生产力提升！
        要安装，请 pip install pocketflow 或直接复制源代码（仅 100 行）。""",
        
        # 虚构医疗设备
        """NeurAlign M7 是一种革命性的非侵入式神经对齐设备。
        靶向磁共振技术可增加特定大脑区域的神经可塑性。
        临床试验显示 PTSD 治疗效果提高了 72%。
        由 Cortex Medical 于 2024 年开发，作为标准认知疗法的辅助手段。
        便携式设计允许在家中使用，并可进行远程医生监控。""",
        
        # 虚构历史事件
        """卡尔多尼亚的天鹅绒革命（1967-1968）结束了维拉克将军长达 40 年的统治。
        由诗人伊丽莎·马尔科维安通过地下文学社团领导。
        最终以 30 万无声抗议者的“大沉默抗议”达到高潮。
        1968 年 3 月举行了首次民主选举，投票率达 94%。
        成为邻近地区非暴力政治转型的典范。""",
        
        # 虚构技术 
        """Q-Mesh 是 QuantumLeap Technologies 的即时数据同步协议。
        利用有向无环图共识，每秒可处理 500,000 笔事务。
        比传统区块链系统能耗降低 95%。
        已被三家中央银行采用，用于安全金融数据传输。
        经过五年秘密开发，于 2024 年 2 月发布。""",
        
        # 虚构科学研究
        """Harlow 研究所的菌丝体菌株 HI-271 可从受污染土壤中去除 99.7% 的 PFAS。
        工程真菌与原生土壤细菌建立共生关系。
        在 60 天内将“永久化学品”分解为无毒化合物。
        现场测试成功修复了以前永久受污染的工业场地。
        部署成本比传统化学提取方法低 80%。"""
    ]
    
    print("=" * 50)
    print("PocketFlow RAG 文档检索")
    print("=" * 50)
    
    # 关于虚构技术的默认查询
    default_query = "如何安装 PocketFlow？"
    
    # 如果命令行提供了 --，则从命令行获取查询
    query = default_query
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            query = arg[2:]
            break
    
    # 两个流的单一共享存储
    shared = {
        "texts": texts,
        "embeddings": None,
        "index": None,
        "query": query,
        "query_embedding": None,
        "retrieved_document": None,
        "generated_answer": None
    }
    
    # 初始化并运行离线流（文档索引）
    offline_flow.run(shared)
    
    # 运行在线流以检索最相关的文档并生成答案
    online_flow.run(shared)


if __name__ == "__main__":
    run_rag_demo()