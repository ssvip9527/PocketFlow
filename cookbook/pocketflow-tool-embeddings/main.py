from flow import create_embedding_flow

def main():
    # 创建流程
    flow = create_embedding_flow()
    
    # 示例文本
    text = "生命的意义是什么？"
    
    # 准备共享数据
    shared = {"text": text}
    
    # 运行流程
    flow.run(shared)
    
    # 打印结果
    print("文本:", text)
    print("嵌入维度:", len(shared["embedding"]))
    print("前5个值:", shared["embedding"][:5])

if __name__ == "__main__":
    main()