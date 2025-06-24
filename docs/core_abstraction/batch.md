---
layout: default
title: "Batch"
parent: "Core Abstraction"
nav_order: 4
---

# 批处理

**批处理**使得在一个节点中处理大量输入或**多次运行**一个流变得更容易。示例用例:
- **基于块**的处理(例如，分割大文本)。
- 对输入项列表(例如，用户查询、文件、URL)进行**迭代**处理。

## 1. 批处理节点

**批处理节点**扩展了`Node`，但改变了`prep()`和`exec()`:

- **`prep(shared)`**: 返回一个**可迭代对象**(例如，列表、生成器)。
- **`exec(item)`**: 对该可迭代对象中的每个项**调用一次**。
- **`post(shared, prep_res, exec_res_list)`**: 处理完所有项后，接收一个结果**列表**(`exec_res_list`)并返回一个**动作**。


### 示例: 汇总大文件

```python
class MapSummaries(BatchNode):
    def prep(self, shared):
        # Suppose we have a big file; chunk it
        content = shared["data"]
        chunk_size = 10000
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        return chunks

    def exec(self, chunk):
        prompt = f"Summarize this chunk in 10 words: {chunk}"
        summary = call_llm(prompt)
        return summary

    def post(self, shared, prep_res, exec_res_list):
        combined = "\n".join(exec_res_list)
        shared["summary"] = combined
        return "default"

map_summaries = MapSummaries()
flow = Flow(start=map_summaries)
flow.run(shared)
```

---

## 2. 批处理流

**批处理流**多次运行一个**流**，每次使用不同的`params`。可以将其视为一个循环，为每个参数集重播流。

### 与批处理节点的主要区别

**重要**: 与处理项并修改共享存储的批处理节点不同:

1. 批处理流返回**要传递给子流的参数**，而不是要处理的数据
2. 这些参数通过`self.params`在子节点中访问，而不是从共享存储中访问
3. 每个子流都独立运行，具有不同的参数集
4. 子节点可以是常规节点，而不是批处理节点(批处理发生在流级别)

### 示例: 汇总多个文件

```python
class SummarizeAllFiles(BatchFlow):
    def prep(self, shared):
        # IMPORTANT: Return a list of param dictionaries (not data for processing)
        filenames = list(shared["data"].keys())  # e.g., ["file1.txt", "file2.txt", ...]
        return [{"filename": fn} for fn in filenames]

# Child node that accesses filename from params, not shared store
class LoadFile(Node):
    def prep(self, shared):
        # Access filename from params (not from shared)
        filename = self.params["filename"]  # Important! Use self.params, not shared
        return filename
        
    def exec(self, filename):
        with open(filename, 'r') as f:
            return f.read()
            
    def post(self, shared, prep_res, exec_res):
        # Store file content in shared
        shared["current_file_content"] = exec_res
        return "default"

# Summarize node that works on the currently loaded file
class Summarize(Node):
    def prep(self, shared):
        return shared["current_file_content"]
        
    def exec(self, content):
        prompt = f"Summarize this file in 50 words: {content}"
        return call_llm(prompt)
        
    def post(self, shared, prep_res, exec_res):
        # Store summary in shared, indexed by current filename
        filename = self.params["filename"]  # Again, using params
        if "summaries" not in shared:
            shared["summaries"] = {}
        shared["summaries"][filename] = exec_res
        return "default"

# Create a per-file flow
load_file = LoadFile()
summarize = Summarize()
load_file >> summarize
summarize_file = Flow(start=load_file)

# Wrap in a BatchFlow to process all files
summarize_all_files = SummarizeAllFiles(start=summarize_file)
summarize_all_files.run(shared)
```

### 幕后
1. 批处理流中的`prep(shared)`返回一个参数字典列表——例如，`[{"filename": "file1.txt"}, {"filename": "file2.txt"}, ...]`。
2. **批处理流**遍历每个字典。对于每个字典:
   - 它将字典与批处理流自己的`params`(如果有的话)合并:`{**batch_flow.params, **dict_from_prep}`
   - 它使用合并后的参数调用`flow.run(shared)`
   - **重要**: 这些参数通过`self.params`传递给子流的节点，而不是通过共享存储
3. 这意味着子流会**重复**运行，每个参数字典运行一次，流中的每个节点都通过`self.params`访问参数。

---

## 3. 嵌套或多级批处理

您可以在另一个**批处理流**中嵌套一个**批处理流**。例如:
- **外部**批处理: 返回目录参数字典列表(例如，`{"directory": "/pathA"}`，`{"directory": "/pathB"}`，...)。
- **内部**批处理: 返回每个文件参数字典列表。

在每个级别，**批处理流**将其自己的参数字典与父级的参数字典合并。当您到达**最内层**节点时，最终的`params`是链中**所有**父级的合并结果。这样，嵌套结构可以同时跟踪整个上下文(例如，目录+文件名)。

```python

class FileBatchFlow(BatchFlow):
    def prep(self, shared):
        # Access directory from params (set by parent)
        directory = self.params["directory"]
        # e.g., files = ["file1.txt", "file2.txt", ...]
        files = [f for f in os.listdir(directory) if f.endswith(".txt")]
        return [{"filename": f} for f in files]

class DirectoryBatchFlow(BatchFlow):
    def prep(self, shared):
        directories = [ "/path/to/dirA", "/path/to/dirB"]
        return [{"directory": d} for d in directories]

# The actual processing node
class ProcessFile(Node):
    def prep(self, shared):
        # Access both directory and filename from params
        directory = self.params["directory"]  # From outer batch
        filename = self.params["filename"]    # From inner batch
        full_path = os.path.join(directory, filename)
        return full_path
        
    def exec(self, full_path):
        # Process the file...
        return f"Processed {full_path}"
        
    def post(self, shared, prep_res, exec_res):
        # Store results, perhaps indexed by path
        if "results" not in shared:
            shared["results"] = {}
        shared["results"][prep_res] = exec_res
        return "default"

# Set up the nested batch structure
process_node = ProcessFile()
inner_flow = FileBatchFlow(start=process_node)
outer_flow = DirectoryBatchFlow(start=inner_flow)

# Run it
outer_flow.run(shared)
```
