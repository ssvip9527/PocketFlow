from flow import flow

def main():
    # 示例文本用于总结
    text = """
    PocketFlow 是一个极简的 LLM 框架，它将工作流建模为嵌套有向图。
    节点处理简单的 LLM 任务，通过代理的动作进行连接。
    流编排这些节点以进行任务分解，并且可以嵌套。
    它还支持批处理和异步执行。
    """

    # 初始化共享存储
    shared = {"data": text}
    
    # 运行流程
    flow.run(shared)
    
    # 打印结果
    print("\n输入文本:", text)
    print("\n摘要:", shared["summary"])

if __name__ == "__main__":
    main()