from flow import create_database_flow

def main():
    # 创建流程
    flow = create_database_flow()
    
    # 准备示例任务数据
    shared = {
        "task_title": "示例任务",
        "task_description": "这是使用 PocketFlow 创建的示例任务"
    }
    
    # 运行流程
    flow.run(shared)
    
    # 打印结果
    print("数据库状态:", shared.get("db_status"))
    print("任务状态:", shared.get("task_status"))
    print("\n所有任务:")
    for task in shared.get("tasks", []):
        print(f"- ID: {task[0]}")
        print(f"  标题: {task[1]}")
        print(f"  描述: {task[2]}")
        print(f"  状态: {task[3]}")
        print(f"  创建时间: {task[4]}")
        print()

if __name__ == "__main__":
    main()
