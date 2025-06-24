---
layout: default
title: "MapReduce"
parent: "设计模式"
nav_order: 4
---

# Map Reduce

MapReduce 是一种设计模式，适用于以下情况：
- 大量输入数据（例如，要处理的多个文件），或者
- 大量输出数据（例如，要填写的多个表单）

并且存在一种逻辑方式将任务分解为更小、理想情况下独立的部分。

<div align="center">
  <img src="https://github.com/the-pocket/.github/raw/main/assets/mapreduce.png?raw=true" width="400"/>
</div>

您首先在映射阶段使用 [BatchNode](../core_abstraction/batch.md) 分解任务，然后在归约阶段进行聚合。

### 示例：文档摘要

```python
class SummarizeAllFiles(BatchNode):
    def prep(self, shared):
        files_dict = shared["files"]  # 例如 10 个文件
        return list(files_dict.items())  # [("file1.txt", "aaa..."), ("file2.txt", "bbb..."), ...]

    def exec(self, one_file):
        filename, file_content = one_file
        summary_text = call_llm(f"总结以下文件：\n{file_content}")
        return (filename, summary_text)

    def post(self, shared, prep_res, exec_res_list):
        shared["file_summaries"] = dict(exec_res_list)

class CombineSummaries(Node):
    def prep(self, shared):
        return shared["file_summaries"]

    def exec(self, file_summaries):
        # 格式为："文件1：摘要\n文件2：摘要...\n"
        text_list = []
        for fname, summ in file_summaries.items():
            text_list.append(f"{fname} 摘要：\n{summ}\n")
        big_text = "\n---\n".join(text_list)

        return call_llm(f"将这些文件摘要合并为一个最终摘要：\n{big_text}")

    def post(self, shared, prep_res, final_summary):
        shared["all_files_summary"] = final_summary

batch_node = SummarizeAllFiles()
combine_node = CombineSummaries()
batch_node >> combine_node

flow = Flow(start=batch_node)

shared = {
    "files": {
        "file1.txt": "爱丽丝开始对坐在她姐姐旁边感到非常厌倦...",
        "file2.txt": "其他一些有趣的文本...",
        # ...
    }
}
flow.run(shared)
print("单独摘要：", shared["file_summaries"])
print("\n最终摘要：\n", shared["all_files_summary"])
```

> **性能提示**：上面的示例是顺序执行的。您可以通过并行运行来加快映射阶段。有关详细信息，请参阅[(高级) 并行](../core_abstraction/parallel.md)。
{: .note }