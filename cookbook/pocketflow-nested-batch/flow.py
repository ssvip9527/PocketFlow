import os
from pocketflow import Flow, BatchFlow
from nodes import LoadGrades, CalculateAverage

def create_base_flow():
    """创建基础流程用于处理单个学生的成绩。"""
    # 创建节点
    load = LoadGrades()
    calc = CalculateAverage()
    
    # 连接节点
    load - "calculate" >> calc
    
    # 创建并返回流程
    return Flow(start=load)

class ClassBatchFlow(BatchFlow):
    """用于处理一个班级所有学生成绩的批量流程。"""
    
    def prep(self, shared):
        """为班级中的每个学生生成参数。"""
        # 从参数中获取班级文件夹
        class_folder = self.params["class"]
        
        # 列出所有学生文件
        class_path = os.path.join("school", class_folder)
        students = [f for f in os.listdir(class_path) if f.endswith(".txt")]
        
        # 返回每个学生的参数
        return [{"student": student} for student in students]
    
    def post(self, shared, prep_res, exec_res):
        """计算并打印班级平均分。"""
        class_name = self.params["class"]
        class_results = shared["results"][class_name]
        class_average = sum(class_results.values()) / len(class_results)
        
        print(f"Class {class_name.split('_')[1].upper()} Average: {class_average:.2f}\n")
        return "default"

class SchoolBatchFlow(BatchFlow):
    """用于处理学校所有班级的批量流程。"""
    
    def prep(self, shared):
        """为每个班级生成参数。"""
        # 列出所有班级文件夹
        classes = [d for d in os.listdir("school") if os.path.isdir(os.path.join("school", d))]
        
        # 返回每个班级的参数
        return [{"class": class_name} for class_name in classes]
    
    def post(self, shared, prep_res, exec_res):
        """计算并打印学校平均分。"""
        all_grades = []
        for class_results in shared["results"].values():
            all_grades.extend(class_results.values())
            
        school_average = sum(all_grades) / len(all_grades)
        print(f"School Average: {school_average:.2f}")
        return "default"

def create_flow():
    """创建完整的嵌套批量处理流程。"""
    # 创建处理单个学生的基础流程
    base_flow = create_base_flow()
    
    # 包装成ClassBatchFlow用于处理班级所有学生
    class_flow = ClassBatchFlow(start=base_flow)
    
    # 包装成SchoolBatchFlow用于处理所有班级
    school_flow = SchoolBatchFlow(start=class_flow)
    
    return school_flow