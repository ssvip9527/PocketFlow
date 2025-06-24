# PocketFlow BatchFlow Example

本示例演示了 PocketFlow 中的 BatchFlow 概念，通过实现一个图像处理器，对多张图像应用不同的滤镜。

## 本示例演示了什么

- 如何使用 BatchFlow 以不同参数多次运行一个 Flow
- BatchFlow 的关键概念：
  1. 创建用于单项处理的基础 Flow
  2. 使用 BatchFlow 处理具有不同参数的多个项目
  3. 管理多个 Flow 执行中的参数

## 项目结构
```
pocketflow-batch-flow/
├── README.md
├── requirements.txt
├── images/
│   ├── cat.jpg        # 示例图片 1
│   ├── dog.jpg        # 示例图片 2
│   └── bird.jpg       # 示例图片 3
├── main.py            # 入口点
├── flow.py            # Flow 和 BatchFlow 定义
└── nodes.py           # 图像处理的节点实现
```

## 工作原理

本示例使用不同的滤镜处理多张图像：

1. **基础 Flow**：处理单张图像
   - 加载图像
   - 应用滤镜（灰度、模糊或棕褐色）
   - 保存处理后的图像

2. **BatchFlow**：处理多个图像-滤镜组合
   - 接收参数列表（图像 + 滤镜组合）
   - 为每个参数集运行基础 Flow
   - 以结构化方式组织输出

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
Processing images with filters...

Processing cat.jpg with grayscale filter...
Processing cat.jpg with blur filter...
Processing dog.jpg with sepia filter...
...

All images processed successfully!
Check the 'output' directory for results.
```

## 关键概念说明

1. **参数管理**：展示了 BatchFlow 如何管理不同的参数集
2. **Flow 重用**：演示了如何多次运行同一个 Flow
3. **批处理**：展示了如何高效处理多个项目
4. **实际应用**：提供了批处理的实际示例