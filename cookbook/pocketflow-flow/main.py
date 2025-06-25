from flow import flow

def main():
    print("\n欢迎使用文本转换器！")
    print("=========================")
    
    # 初始化共享存储
    shared = {}
    
    # 运行流程
    flow.run(shared)
    
    print("\n感谢您使用文本转换器！")

if __name__ == "__main__":
    main()