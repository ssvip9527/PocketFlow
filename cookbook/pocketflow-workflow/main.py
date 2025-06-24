from flow import create_article_flow

def run_flow(topic="AI Safety"):
    """
    运行文章写作工作流，指定主题
    
    参数：
        topic (str)：文章的主题
    """
    # 使用主题初始化共享数据
    shared = {"topic": topic}
    
    # 打印开始消息
    print(f"\n=== Starting Article Workflow on Topic: {topic} ===\n")
    
    # 运行流
    flow = create_article_flow()
    flow.run(shared)
    
    # 输出总结
    print("\n=== Workflow Completed ===\n")
    print(f"Topic: {shared['topic']}")
    print(f"Outline Length: {len(shared['outline'])} characters")
    print(f"Draft Length: {len(shared['draft'])} characters")
    print(f"Final Article Length: {len(shared['final_article'])} characters")
    
    return shared

if __name__ == "__main__":
    import sys
    
    # 如果提供了命令行参数，则从命令行获取主题
    topic = "AI Safety"  # 默认主题
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    
    run_flow(topic)