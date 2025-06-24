# PocketFlow BatchNode Example

本示例通过实现一个 CSV 处理器来演示 PocketFlow 中的 BatchNode 概念，该处理器通过分块处理大型文件。

## 本示例演示了什么

- 如何使用 BatchNode 分块处理大型输入
- BatchNode 的三个关键方法：
  1. `prep`：将输入分割成块
  2. `exec`：独立处理每个块
  3. `post`：合并所有块的结果

## 项目结构
```
pocketflow-batch-node/
├── README.md
├── requirements.txt
├── data/
│   └── sales.csv      # 示例大型 CSV 文件
├── main.py            # 入口点
├── flow.py            # 流程定义
└── nodes.py           # BatchNode 实现
```

## 工作原理

本示例处理一个包含销售数据的大型 CSV 文件：

1. **分块 (prep)**：CSV 文件被读取并分割成 N 行的块
2. **处理 (exec)**：每个块被处理以计算：
   - 总销售额
   - 平均销售额
   - 交易数量
3. **合并 (post)**：所有块的结果被聚合成最终统计数据

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python main.py
```

## 示例输出

```
Processing sales.csv in chunks...

Final Statistics:
- Total Sales: $1,234,567.89
- Average Sale: $123.45
- Total Transactions: 10,000
```

## 关键概念说明

1. **基于分块的处理**：展示了 BatchNode 如何通过将大型输入分解为可管理的部分来处理它们
2. **独立处理**：演示了每个块如何独立处理
3. **结果聚合**：展示了如何将单个结果组合成最终输出