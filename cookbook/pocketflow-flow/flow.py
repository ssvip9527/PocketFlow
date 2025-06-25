from pocketflow import Node, Flow

class TextInput(Node):
    def prep(self, shared):
        """从用户获取文本输入。"""
        if "text" not in shared:
            text = input("\nEnter text to convert: ")
            shared["text"] = text
        return shared["text"]

    def post(self, shared, prep_res, exec_res):
        print("\nChoose transformation:")
        print("1. Convert to UPPERCASE")
        print("2. Convert to lowercase")
        print("3. Reverse text")
        print("4. Remove extra spaces")
        print("5. Exit")
        
        choice = input("\nYour choice (1-5): ")
        
        if choice == "5":
            return "exit"
        
        shared["choice"] = choice
        return "transform"

class TextTransform(Node):
    def prep(self, shared):
        return shared["text"], shared["choice"]
    
    def exec(self, inputs):
        text, choice = inputs
        
        if choice == "1":
            return text.upper()
        elif choice == "2":
            return text.lower()
        elif choice == "3":
            return text[::-1]
        elif choice == "4":
            return " ".join(text.split())
        else:
            return "Invalid option!"
    
    def post(self, shared, prep_res, exec_res):
        print("\nResult:", exec_res)
        
        if input("\nConvert another text? (y/n): ").lower() == 'y':
            shared.pop("text", None)  # 移除之前的文本
            return "input"
        return "exit"

class EndNode(Node):
    pass

# 创建节点
text_input = TextInput()
text_transform = TextTransform()
end_node = EndNode()

# 连接节点
text_input - "transform" >> text_transform
text_transform - "input" >> text_input
text_transform - "exit" >> end_node

# 创建流程
flow = Flow(start=text_input)