---
layout: default
title: "文本分块"
parent: "实用函数"
nav_order: 4
---

# 文本分块

我们推荐一些常用的文本分块方法的实现。


> 文本分块更多是一种微观优化，与流程设计相比。
> 
> 建议从朴素分块开始，之后再进行优化。
{: .best-practice }

---

## Python 代码示例

### 1. 朴素（固定大小）分块
按固定字数分割文本，忽略句子或语义边界。

```python
def fixed_size_chunk(text, chunk_size=100):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks
```

然而，句子经常被不自然地截断，导致连贯性丧失。

### 2. 基于句子的分块

```python
import nltk

def sentence_based_chunk(text, max_sentences=2):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunks.append(" ".join(sentences[i : i + max_sentences]))
    return chunks
```

然而，可能无法很好地处理非常长的句子或段落。

### 3. 其他分块

- **基于段落**: 按段落（例如，换行符）分割文本。大段落会创建大块。
- **语义**: 使用嵌入或主题建模按语义边界分块。
- **智能体**: 使用大型语言模型（LLM）根据上下文或含义决定分块边界。