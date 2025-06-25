from flow import create_resume_processing_flow

def main():
    # 初始化共享存储
    shared = {}
    
    # 创建简历处理流程
    resume_flow = create_resume_processing_flow()
    
    # 运行流程
    print("开始简历资格处理...")
    resume_flow.run(shared)
    
    # 显示最终摘要信息（ReduceResultsNode 中已打印的额外信息）
    if "summary" in shared:
        print("\n详细评估结果:")
        for filename, evaluation in shared.get("evaluations", {}).items():
            qualified = "✓" if evaluation.get("qualifies", False) else "✗"
            name = evaluation.get("candidate_name", "未知")
            print(f"{qualified} {name} ({filename})")
    
    print("\n简历处理完成!")

if __name__ == "__main__":
    main()