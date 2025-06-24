from flow import create_vision_flow

def main():
    # 创建并运行流程
    flow = create_vision_flow()
    shared = {}
    flow.run(shared)
    
    # 打印结果
    if "results" in shared:
        for result in shared["results"]:
            print(f"\n文件: {result['filename']}")
            print("-" * 50)
            print(result["text"])

if __name__ == "__main__":
    main()
