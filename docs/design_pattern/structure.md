---
layout: default
title: "结构化输出"
parent: "设计模式"
nav_order: 5
---

# 结构化输出

在许多用例中，您可能希望 LLM 输出特定的结构，例如带有预定义键的列表或字典。

有几种方法可以实现结构化输出：
- **提示** LLM 严格返回定义的结构。
- 使用原生支持 **模式强制** 的 LLM。
- **后处理** LLM 的响应以提取结构化内容。

实际上，对于现代 LLM 来说，**提示** 既简单又可靠。

### 示例用例

- 提取关键信息

```yaml
product:
  name: Widget Pro
  price: 199.99
  description: |
    专为专业人士设计的高质量小部件。
    推荐给高级用户。
```

- 将文档总结为要点

```yaml
summary:
  - 该产品易于使用。
  - 具有成本效益。
  - 适用于所有技能水平。
```

- 生成配置文件

```yaml
server:
  host: 127.0.0.1
  port: 8080
  ssl: true
```

## 提示工程

当提示 LLM 生成 **结构化** 输出时：
1. 将结构 **包装** 在代码围栏中（例如，`yaml`）。
2. **验证** 所有必需字段是否存在（并让 `Node` 处理重试）。

### 示例文本摘要

```python
class SummarizeNode(Node):
    def exec(self, prep_res):
        # 假设 `prep_res` 是要总结的文本。
        prompt = f"""
请将以下文本总结为 YAML 格式，精确包含 3 个要点

{prep_res}

现在，输出：
```yaml
summary:
  - 要点 1
  - 要点 2
  - 要点 3
```"""
        response = call_llm(prompt)
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()

        import yaml
        structured_result = yaml.safe_load(yaml_str)

        assert "summary" in structured_result
        assert isinstance(structured_result["summary"], list)

        return structured_result
```

> 除了使用 `assert` 语句外，另一种验证模式的流行方法是 [Pydantic](https://github.com/pydantic/pydantic)
{: .note }

### 为什么选择 YAML 而不是 JSON？

当前的 LLM 在转义方面存在困难。YAML 处理字符串更容易，因为它们不总是需要引号。

**在 JSON 中**

```json
{
  "dialogue": "Alice 说：\"你好 Bob。\n你好吗？\n我很好。\""
}
```

- 字符串中的每个双引号都必须用 `\"` 转义。
- 对话中的每个换行符都必须表示为 `\n`。

**在 YAML 中**

```yaml
dialogue: |
  Alice 说："你好 Bob。
  你好吗？
  我很好。"
```

- 无需转义内部引号——只需将整个文本放在块字面量 (`|`) 下。
- 换行符自然保留，无需 `\n`。