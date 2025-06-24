# PocketFlow 通信示例

本示例演示了 PocketFlow 中的 [通信](https://the-pocket.github.io/PocketFlow/communication.html) 概念，特别关注共享存储模式。

## 概述

本示例实现了一个简单的单词计数器，展示了节点如何使用共享存储进行通信。它演示了：

- 如何初始化和构建共享存储
- 节点如何从共享存储中读取和写入
- 如何在多个节点执行中维护状态
- 共享存储使用的最佳实践

## 项目结构

```
pocketflow-communication/
├── README.md
├── requirements.txt
├── main.py
├── flow.py
└── nodes.py
```

## 安装

```bash
pip install -r requirements.txt
```

## 用法

```bash
python main.py
```

出现提示时输入文本。程序将：
1. 统计文本中的单词
2. 将统计信息存储在共享存储中
3. 显示运行统计信息（总文本数、总单词数、平均值）

输入 'q' 退出。

## 工作原理

本示例使用三个节点：

1. `TextInput`: 读取用户输入并初始化共享存储
2. `WordCounter`: 统计单词并更新共享存储中的统计信息
3. `ShowStats`: 显示共享存储中的统计信息

这演示了节点如何使用共享存储模式共享和维护状态。