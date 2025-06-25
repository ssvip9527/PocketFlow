from flow import qa_flow

# 示例主函数
# 请将其替换为您自己的主函数
def main():
    shared = {
        "question": "用一句话概括，宇宙的终结是什么？",
        "answer": None
    }

    qa_flow.run(shared)
    print("问题:", shared["question"])
    print("答案:", shared["answer"])

if __name__ == "__main__":
    main()