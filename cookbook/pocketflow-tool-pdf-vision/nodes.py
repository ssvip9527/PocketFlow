from pocketflow import Node, BatchNode
from tools.pdf import pdf_to_images
from tools.vision import extract_text_from_image
from typing import List, Dict, Any
from pathlib import Path
import os

class ProcessPDFBatchNode(BatchNode):
    """用于处理目录中多个PDF的节点"""
    
    def prep(self, shared):
        # 获取PDF目录路径
        root_dir = Path(__file__).parent
        pdf_dir = root_dir / "pdfs"
        
        # 列出所有PDF文件
        pdf_files = []
        for file in os.listdir(pdf_dir):
            if file.lower().endswith('.pdf'):
                pdf_files.append({
                    "pdf_path": str(pdf_dir / file),
                    "extraction_prompt": shared.get("extraction_prompt", 
                        "从该文档中提取所有文本，保留格式和布局。")
                })
        
        if not pdf_files:
            print("在'pdfs'目录中没有找到PDF文件！")
            return []
            
        print(f"找到 {len(pdf_files)} 个PDF文件")
        return pdf_files
    
    def exec(self, item):
        # 为单个PDF创建流程
        flow = create_single_pdf_flow()
        
        # 处理PDF
        print(f"\n正在处理: {os.path.basename(item['pdf_path'])}")
        print("-" * 50)
        
        # 运行流程
        shared = item.copy()
        flow.run(shared)
        
        return {
            "filename": os.path.basename(item["pdf_path"]),
            "text": shared.get("final_text", "未提取到文本")
        }
    
    def post(self, shared, prep_res, exec_res_list):
        shared["results"] = exec_res_list
        return "default"

class LoadPDFNode(Node):
    """用于加载单个PDF并将其转换为图像的节点"""
    
    def prep(self, shared):
        return shared.get("pdf_path", "")
        
    def exec(self, pdf_path):
        return pdf_to_images(pdf_path)
        
    def post(self, shared, prep_res, exec_res):
        shared["page_images"] = exec_res
        return "default"

class ExtractTextNode(Node):
    """使用Vision API从图像中提取文本的节点"""
    
    def prep(self, shared):
        return (
            shared.get("page_images", []),
            shared.get("extraction_prompt", None)
        )
        
    def exec(self, inputs):
        images, prompt = inputs
        results = []
        
        for img, page_num in images:
            text = extract_text_from_image(img, prompt)
            results.append({
                "page": page_num,
                "text": text
            })
            
        return results
        
    def post(self, shared, prep_res, exec_res):
        shared["extracted_text"] = exec_res
        return "default"

class CombineResultsNode(Node):
    """用于组合和格式化提取文本的节点"""
    
    def prep(self, shared):
        return shared.get("extracted_text", [])
        
    def exec(self, results):
        # 按页码排序
        sorted_results = sorted(results, key=lambda x: x["page"])
        
        # 结合文本和页码
        combined = []
        for result in sorted_results:
            combined.append(f"=== 第 {result['page']} 页 ===\n{result['text']}\n")
            
        return "\n".join(combined)
        
    def post(self, shared, prep_res, exec_res):
        shared["final_text"] = exec_res
        return "default"

def create_single_pdf_flow():
    """创建用于处理单个PDF的流程"""
    from pocketflow import Flow
    
    # 创建节点
    load_pdf = LoadPDFNode()
    extract_text = ExtractTextNode()
    combine_results = CombineResultsNode()
    
    # 连接节点
    load_pdf >> extract_text >> combine_results
    
    # 创建并返回流程
    return Flow(start=load_pdf)
