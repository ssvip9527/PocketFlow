import os
from flow import create_flow

def create_sample_data():
    """创建示例成绩文件。"""
    # 创建目录结构
    os.makedirs("school/class_a", exist_ok=True)
    os.makedirs("school/class_b", exist_ok=True)
    
    # 示例成绩
    data = {
        "class_a": {
            "student1.txt": [7.5, 8.0, 9.0],
            "student2.txt": [8.5, 7.0, 9.5]
        },
        "class_b": {
            "student3.txt": [6.5, 8.5, 7.0],
            "student4.txt": [9.0, 9.5, 8.0]
        }
    }
    
    # 创建文件
    for class_name, students in data.items():
        for student, grades in students.items():
            file_path = os.path.join("school", class_name, student)
            with open(file_path, 'w') as f:
                for grade in grades:
                    f.write(f"{grade}\n")

def main():
    """运行嵌套批量示例。"""
    # 创建示例数据
    create_sample_data()
    
    print("正在处理学校成绩...\n")
    
    # 创建并运行流程
    flow = create_flow()
    flow.run({})

if __name__ == "__main__":
    main()