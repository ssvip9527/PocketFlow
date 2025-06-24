#!/usr/bin/env python3
"""
用于从 PocketFlow 文档文件夹生成 MDC 文件的脚本，每个 MD 文件生成一个 MDC 文件。

用法:
    python update_pocketflow_mdc.py [--docs-dir PATH] [--rules-dir PATH]
"""

import os
import re
import shutil
from pathlib import Path
import sys
import html.parser

class HTMLTagStripper(html.parser.HTMLParser):
    """HTML 解析器子类，用于从内容中去除 HTML 标签"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ''.join(self.text)

def strip_html_tags(html_content):
    """从内容中移除 HTML 标签"""
    stripper = HTMLTagStripper()
    stripper.feed(html_content)
    return stripper.get_text()

def extract_frontmatter(file_path):
    """从 markdown frontmatter 中提取标题、父级和导航顺序"""
    frontmatter = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 提取 --- 标记之间的 frontmatter
            fm_match = re.search(r'^---\s*(.+?)\s*---', content, re.DOTALL)
            if fm_match:
                frontmatter_text = fm_match.group(1)
                
                # 提取字段
                title_match = re.search(r'title:\s*"?([^"\n]+)"?', frontmatter_text)
                parent_match = re.search(r'parent:\s*"?([^"\n]+)"?', frontmatter_text)
                nav_order_match = re.search(r'nav_order:\s*(\d+)', frontmatter_text)
                
                if title_match:
                    frontmatter['title'] = title_match.group(1)
                if parent_match:
                    frontmatter['parent'] = parent_match.group(1)
                if nav_order_match:
                    frontmatter['nav_order'] = int(nav_order_match.group(1))
    except Exception as e:
        print(f"Error reading frontmatter from {file_path}: {e}")
    
    return frontmatter

def extract_first_heading(file_path):
    """从 markdown 内容中提取第一个标题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 移除 frontmatter
            content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
            
            # 查找第一个标题
            heading_match = re.search(r'#\s+(.+)', content)
            if heading_match:
                return heading_match.group(1).strip()
    except Exception as e:
        print(f"Error extracting heading from {file_path}: {e}")
    
    # 如果没有找到标题，则回退到文件名
    return Path(file_path).stem.replace('_', ' ').title()

def get_mdc_description(md_file, frontmatter, heading):
    """根据文件元数据为 MDC 文件生成描述"""
    section = ""
    subsection = ""
    
    # 从路径确定部分
    path_parts = Path(md_file).parts
    if 'core_abstraction' in path_parts:
        section = "Core Abstraction"
    elif 'design_pattern' in path_parts:
        section = "Design Pattern"
    elif 'utility_function' in path_parts:
        section = "Utility Function"
    
    # 使用 frontmatter 标题或标题作为子部分
    if 'title' in frontmatter:
        subsection = frontmatter['title']
    else:
        subsection = heading
    
    # 对于组合指南和索引
    if Path(md_file).name == "guide.md":
        return "Guidelines for using PocketFlow, Agentic Coding"
    
    # 对于根级别的 index.md，使用不同的格式
    if Path(md_file).name == "index.md" and section == "":
        return "Guidelines for using PocketFlow, a minimalist LLM framework"
    
    # 对于其他文件，创建更具体的描述
    if section:
        return f"Guidelines for using PocketFlow, {section}, {subsection}"
    else:
        return f"Guidelines for using PocketFlow, {subsection}"

def process_markdown_content(content, remove_local_refs=False):
    """处理 markdown 内容，使其适合 MDC 文件"""
    # 移除 frontmatter
    content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
    
    # 替换 HTML div 标签及其内容
    content = re.sub(r'<div.*?>.*?</div>', '', content, flags=re.DOTALL)
    
    if remove_local_refs:
        # 将指向本地文档的 markdown 链接替换为括号中的文本
        # 这可以防止在加载文件时自动包含所有文档
        # 保留文本周围的括号以便更好地发现
        content = re.sub(r'\[([^\]]+)\]\(\./[^)]+\)', r'[\1]', content)
    else:
        # 调整相对链接以维护文档结构中的引用
        content = re.sub(r'\]\(\./([^)]+)\)', r'](mdc:./\1)', content)
        
        # 确保指向 md 文件的链接正常工作
        content = re.sub(r'\]\(mdc:\./(.+?)\.md\)', r'](mdc:./\1.md)', content)
        content = re.sub(r'\]\(mdc:\./(.+?)\.html\)', r'](mdc:./\1.md)', content)
    
    # 剥离剩余的 HTML 标签
    content = strip_html_tags(content)
    
    return content

def get_documentation_first_policy():
    """返回要包含在指南中的“文档优先策略”文本"""
    return """# DOCUMENTATION FIRST POLICY

**关键指令**：在实现 Pocket Flow 应用程序时：

1. **始终首先请求 MDC 文件** - 在编写任何代码之前，请求并审查所有相关的 MDC 文档文件。本文档提供了对这些文档的解释。
2. **理解框架** - 通过文档全面理解 Pocket Flow 框架。
3. **避免假设驱动的开发** - 不要基于假设或猜测进行实现。即使人类在他们的请求中没有明确提及 Pocket Flow，如果您正在编辑的代码正在使用 Pocket Flow，您也应该请求相关文档以帮助您理解最佳实践，然后再进行编辑。

**验证**：每次实现都以您审查过的文档的简要摘要开始，以指导您的方法。

"""

def generate_mdc_header(md_file, description, always_apply=False):
    """生成带有适当 frontmatter 的 MDC 文件头"""
    # 确定是否应包含 globs
    # 对于 index.md 和 guide.md，我们包含 **/*.py 以提供 Python 文件的高级上下文
    # 对于其他文件，将其留空以减少侵入性
    globs = "**/*.py" if always_apply else ""
    
    return f"""---
description: {description}
globs: {globs}
alwaysApply: {"true" if always_apply else "false"}
---
"""

def has_substantive_content(content):
    """检查处理后的内容是否包含除 frontmatter 之外的实质性内容"""
    # 移除 frontmatter
    content_without_frontmatter = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
    
    # 移除空格和常见的 HTML/markdown 格式
    cleaned_content = re.sub(r'\s+', '', content_without_frontmatter)
    cleaned_content = re.sub(r'{:.*?}', '', cleaned_content)
    
    # 如果清理后几乎没有留下任何内容，则认为它是空的
    return len(cleaned_content) > 20  # 任意阈值，根据需要调整

def create_combined_guide(docs_dir, rules_dir):
    """创建一个包含指南和索引内容的组合指南"""
    docs_path = Path(docs_dir)
    rules_path = Path(rules_dir)
    
    guide_file = docs_path / "guide.md"
    index_file = docs_path / "index.md"
    
    if not guide_file.exists() or not index_file.exists():
        print("警告：未找到 guide.md 或 index.md，跳过组合指南创建")
        return False
    
    # 获取指南内容和索引内容
    with open(guide_file, 'r', encoding='utf-8') as f:
        guide_content = f.read()
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # 处理内容
    processed_guide = process_markdown_content(guide_content, remove_local_refs=True)
    processed_index = process_markdown_content(index_content, remove_local_refs=True)
    
    # 获取文档优先策略
    doc_first_policy = get_documentation_first_policy()
    
    # 将内容与文档优先策略结合在一起
    combined_content = doc_first_policy + processed_guide + "\n\n" + processed_index
    
    # 生成 MDC 头
    description = "Guidelines for using PocketFlow, Agentic Coding"
    mdc_header = generate_mdc_header(guide_file, description, always_apply=True)
    
    # 结合头部和处理后的内容
    mdc_content = mdc_header + combined_content
    
    # 使用新文件名创建输出路径
    output_path = rules_path / "guide_for_pocketflow.mdc"
    
    # 写入 MDC 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(mdc_content)
    
    print(f"Created combined guide MDC file: {output_path}")
    return True

def convert_md_to_mdc(md_file, output_dir, docs_dir, special_treatment=False):
    """将 markdown 文件转换为 MDC 格式并保存到输出目录"""
    try:
        print(f"Processing: {md_file}")
        
        # 跳过 guide.md 和 index.md，因为它们将单独处理
        file_name = Path(md_file).name
        if file_name in ["guide.md", "index.md"]:
            print(f"跳过 {file_name} 进行单独处理 - 它将包含在组合指南中")
            return True
        
        # 跳过子文件夹中的空 index.md 文件
        parent_dir = Path(md_file).parent.name
        
        # 检查这是否是子文件夹中的 index.md（不是主 index.md）
        if (file_name == "index.md" and parent_dir != "docs" and 
            parent_dir in ["core_abstraction", "design_pattern", "utility_function"]):
            
            # 读取内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 如果没有实质性内容则跳过
            if not has_substantive_content(content):
                print(f"跳过空子文件夹索引: {md_file}")
                return True
        
        # 从文件中提取元数据
        frontmatter = extract_frontmatter(md_file)
        heading = extract_first_heading(md_file)
        description = get_mdc_description(md_file, frontmatter, heading)
        
        # 读取内容
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 处理内容
        processed_content = process_markdown_content(content, remove_local_refs=special_treatment)
        
        # 生成 MDC 头
        mdc_header = generate_mdc_header(md_file, description, always_apply=special_treatment)
        
        # 结合头部和处理后的内容
        mdc_content = mdc_header + processed_content
        
        # 执行最终检查以确保处理后的内容是实质性的
        if not has_substantive_content(processed_content):
            print(f"跳过处理后没有实质性内容的文件: {md_file}")
            return True
        
        # 获取相对于 docs 目录的路径
        rel_path = os.path.relpath(md_file, start=Path(docs_dir))
        
        # 仅提取文件名和目录结构，不带 'docs/' 前缀
        path_parts = Path(rel_path).parts
        if len(path_parts) > 1 and path_parts[0] == 'docs':
            # 从路径中移除 'docs/' 前缀
            rel_path = os.path.join(*path_parts[1:])
        
        # 创建输出路径
        output_path = Path(output_dir) / rel_path
        
        # 如果输出目录不存在则创建
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 将扩展名从 .md 更改为 .mdc
        output_path = output_path.with_suffix('.mdc')
        
        # 写入 MDC 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mdc_content)
        
        print(f"Created MDC file: {output_path}")
        return True
    
    except Exception as e:
        print(f"Error converting {md_file} to MDC: {e}")
        return False

def generate_mdc_files(docs_dir, rules_dir):
    """从 docs 目录中的所有 markdown 文件生成 MDC 文件"""
    docs_path = Path(docs_dir)
    rules_path = Path(rules_dir)
    
    # 确保 docs 目录存在
    if not docs_path.exists() or not docs_path.is_dir():
        raise ValueError(f"Directory not found: {docs_dir}")
    
    print(f"Generating MDC files from docs in: {docs_dir}")
    print(f"Output will be written to: {rules_dir}")
    
    # 如果规则目录不存在则创建
    rules_path.mkdir(parents=True, exist_ok=True)
    
    # 首先创建组合指南文件（包括 guide.md 和 index.md）
    create_combined_guide(docs_dir, rules_dir)
    
    # 处理所有其他 markdown 文件
    success_count = 0
    failure_count = 0
    
    # 查找所有 markdown 文件
    md_files = list(docs_path.glob("**/*.md"))
    
    # 跳过主 index.md 和 guide.md 文件，因为我们已经在 create_combined_guide 中处理过它们
    md_files = [f for f in md_files if f.name != "index.md" and f.name != "guide.md"]
    
    # 处理每个 markdown 文件
    for md_file in md_files:
        if convert_md_to_mdc(md_file, rules_path, docs_dir):
            success_count += 1
        else:
            failure_count += 1
    
    print(f"\nProcessed {len(md_files) + 1} markdown files:")  # +1 用于组合指南
    print(f"  - Successfully converted: {success_count + 1}")  # +1 用于组合指南
    print(f"  - Failed conversions: {failure_count}")
    
    return success_count > 0 and failure_count == 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="从 PocketFlow 文档生成 MDC 文件")
    
    # 获取脚本目录
    script_dir = Path(__file__).parent.absolute()
    
    # 默认为相对于脚本位置的 PocketFlow/docs 目录
    default_docs_dir = (script_dir.parent / "docs").as_posix()
    
    # 默认规则目录 - 已更改为 .cursor/rules
    default_rules_dir = (script_dir.parent / ".cursor" / "rules").as_posix()
    
    parser.add_argument("--docs-dir", 
                        default=default_docs_dir, 
                        help="PocketFlow 文档目录的路径")
    parser.add_argument("--rules-dir", 
                        default=default_rules_dir, 
                        help="MDC 文件的输出目录")
    
    args = parser.parse_args()
    
    try:
        success = generate_mdc_files(args.docs_dir, args.rules_dir)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 