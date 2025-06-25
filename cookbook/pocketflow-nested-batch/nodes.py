import os
from pocketflow import Node

class LoadGrades(Node):
    """从学生文件中加载成绩的节点。"""
    
    def prep(self, shared):
        """从参数中获取文件路径。"""
        class_name = self.params["class"]
        student_file = self.params["student"]
        return os.path.join("school", class_name, student_file)
    
    def exec(self, file_path):
        """从文件中加载并解析成绩。"""
        with open(file_path, 'r') as f:
            # 每行是一个成绩
            grades = [float(line.strip()) for line in f]
        return grades
    
    def post(self, shared, prep_res, grades):
        """将成绩存储到共享存储中。"""
        shared["grades"] = grades
        return "calculate"

class CalculateAverage(Node):
    """计算平均成绩的节点。"""
    
    def prep(self, shared):
        """从共享存储中获取成绩。"""
        return shared["grades"]
    
    def exec(self, grades):
        """计算平均值。"""
        return sum(grades) / len(grades)
    
    def post(self, shared, prep_res, average):
        """存储并打印结果。"""
        # 存储到结果字典中
        if "results" not in shared:
            shared["results"] = {}
        
        class_name = self.params["class"]
        student = self.params["student"]
        
        if class_name not in shared["results"]:
            shared["results"][class_name] = {}
            
        shared["results"][class_name][student] = average
        
        # 打印单个结果
        print(f"- {student}: Average = {average:.1f}")
        return "default"