from flow import create_joke_flow

def main():
    """运行笑话生成器应用程序的主函数。"""
    print("欢迎使用命令行笑话生成器！")

    shared = {
        "topic": None,
        "current_joke": None,
        "disliked_jokes": [],
        "user_feedback": None
    }

    joke_flow = create_joke_flow()
    joke_flow.run(shared)

    print("\n感谢使用笑话生成器！")

if __name__ == "__main__":
    main()