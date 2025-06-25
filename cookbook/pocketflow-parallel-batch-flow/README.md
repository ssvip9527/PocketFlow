# 并行图像处理器

演示了 AsyncParallelBatchFlow 如何以比顺序处理快 8 倍以上的速度处理多张图像和多个过滤器。

## 功能

  ```mermaid
  graph TD
      subgraph AsyncParallelBatchFlow[图像处理流]
          subgraph AsyncFlow[每图像-过滤器流]
              A[加载图像] --> B[应用过滤器]
              B --> C[保存图像]
          end
      end
  ```
  
- 并行处理多张图像和多个过滤器
- 应用三种不同的过滤器（灰度、模糊、棕褐色）
- 显示出比顺序处理显著的速度提升
- 使用信号量管理系统资源

## 运行方式

```bash
pip install -r requirements.txt
python main.py
```

## 输出

```=== 并行处理图像 ===
并行图像处理器
------------------------------
找到 3 张图像：
- images/bird.jpg
- images/cat.jpg
- images/dog.jpg

正在运行顺序批量流...
正在处理 3 张图像和 3 个过滤器...
总组合数：9
正在加载图像：images/bird.jpg
正在应用灰度过滤器...
已保存：output/bird_grayscale.jpg
...等等

计时结果：
顺序批量处理：13.76 秒
并行批量处理：1.71 秒
加速比：8.04 倍

处理完成！请检查 output/ 目录以获取结果。
```

## 关键点

- **顺序**：总时间 = 所有项目时间的总和
  - 适用于：速率受限的 API，保持顺序

- **并行**：总时间 ≈ 最长单个项目时间
  - 适用于：I/O 密集型任务，独立操作
