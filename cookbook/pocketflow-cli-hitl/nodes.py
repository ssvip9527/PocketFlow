from pocketflow import Node
from utils.call_llm import call_llm

class GetTopicNode(Node):
    """提示用户输入笑话的主题。"""
    def exec(self, _shared):
        return input("您想听什么主题的笑话？ ")

    def post(self, shared, _prep_res, exec_res):
        shared["topic"] = exec_res

class GenerateJokeNode(Node):
    """根据主题和任何先前的反馈生成笑话。"""
    def prep(self, shared):
        topic = shared.get("topic", "任何")
        disliked_jokes = shared.get("disliked_jokes", [])
        
        prompt = f"请生成一个关于：{topic} 的单行笑话。请简短有趣。"
        if disliked_jokes:
            disliked_str = "; ".join(disliked_jokes)
            prompt = f"用户不喜欢以下笑话：[{disliked_str}]。请生成一个关于 {topic} 的新的、不同的笑话。"
        return prompt

    def exec(self, prep_res):
        return call_llm(prep_res)

    def post(self, shared, _prep_res, exec_res):
        shared["current_joke"] = exec_res
        print(f"\n笑话: {exec_res}")

class GetFeedbackNode(Node):
    """向用户展示笑话并征求批准。"""
    def exec(self, _prep_res):
        while True:
            feedback = input("您喜欢这个笑话吗？(是/否): ").strip().lower()
            if feedback in ["yes", "y", "no", "n"]:
                return feedback
            print("无效输入。请输入 '是' 或 '否'。")

    def post(self, shared, _prep_res, exec_res):
        if exec_res in ["yes", "y"]:
            shared["user_feedback"] = "approve"
            print("太棒了！很高兴您喜欢它。")
            return "Approve"
        else:
            shared["user_feedback"] = "disapprove"
            current_joke = shared.get("current_joke")
            if current_joke:
                if "disliked_jokes" not in shared:
                    shared["disliked_jokes"] = []
                shared["disliked_jokes"].append(current_joke)
            print("好的，我再试一个。")
            return "Disapprove"