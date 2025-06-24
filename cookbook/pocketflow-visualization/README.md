# PocketFlow Visualization

本目录包含使用交互式 D3.js 可视化工具来展示 PocketFlow 工作流图的工具。

## 概述

可视化工具允许您：

1. 将 PocketFlow 节点和工作流以交互式图表形式查看
2. 查看不同工作流之间的连接方式
3. 理解节点在工作流内的关系

## 功能

- **交互式图表**：可拖动节点重新组织布局
- **分组可视化**：工作流以虚线边框的分组形式显示
- **组间连接**：工作流之间的连接以连接组边界的虚线显示
- **动作标签**：边标签显示触发节点转换的动作

## 要求

- Python 3.6 或更高版本
- 现代网页浏览器（Chrome、Firefox、Edge）用于查看可视化效果

## Usage

### 1. 基本可视化

要可视化 PocketFlow 图，您可以使用 `visualize.py` 中的 `visualize_flow` 函数：

```python
from visualize import visualize_flow
from your_flow_module import your_flow

# 生成可视化
visualize_flow(your_flow, "您的流程名称")
```

这将：
1. 在控制台打印 Mermaid 图表
2. 在 `./viz` 目录中生成 D3.js 可视化文件

### 2. 运行示例

随附的示例展示了一个包含支付、库存和发货流程的订单处理管道：

```bash
# 导航到目录
cd cookbook/pocketflow-minimal-flow2flow

# 运行可视化脚本
python visualize.py
```

这将在 `./viz` 目录中生成可视化文件。

### 3. 查看可视化

运行脚本后：

1. 托管方式：
   ```
   cd ./viz/
   ```

2. 与可视化交互：
   - **拖动节点**以重新组织布局
   - **悬停在节点上**以查看节点名称
   - **观察节点和流程之间的连接**

## 自定义可视化

### 调整布局参数

您可以调整 `visualize.py` 中的力模拟参数，以改变节点和组的定位方式：

```javascript
// 创建力模拟
const simulation = d3.forceSimulation(data.nodes)
    // 控制连接节点之间的距离
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
    // 控制节点之间的排斥力——值越低，节点越靠近
    .force("charge", d3.forceManyBody().strength(-30))
    // 将整个图表居中于 SVG
    .force("center", d3.forceCenter(width / 2, height / 2))
    // 防止节点重叠——作用类似于最小距离
    .force("collide", d3.forceCollide().radius(50));
```

### 样式

调整 `create_d3_visualization` 函数中 HTML 模板内的 CSS 样式，以更改颜色、形状和其他视觉属性。

## 工作原理

可视化过程包括三个主要步骤：

1. **流程到 JSON 转换**：`flow_to_json` 函数遍历 PocketFlow 图，并将其转换为包含节点、链接和组信息的结构。

2. **D3.js 可视化**：JSON 数据用于创建交互式 D3.js 可视化，其中：
   - 节点表示为圆形
   - 流程表示为包含节点的虚线矩形
   - 链接显示流程内部和流程之间的连接

3. **组边界连接**：可视化计算与组边界的交点，以确保组间链接连接在边界而不是中心。

## 扩展可视化

您可以通过以下方式扩展可视化工具：

1. 添加新的节点形状
2. 实现额外的布局算法
3. 添加包含更详细信息的工具提示
4. 创建流程执行动画

## 故障排除

如果您遇到任何问题：

- 确保您的流程对象已正确构建，节点连接正确
- 检查浏览器控制台是否有任何 JavaScript 错误
- 验证生成的 JSON 数据结构是否与您预期的一致

## 示例输出

可视化显示：
- 支付处理流程节点
- 库存管理流程节点
- 发货流程节点
- 每个流程周围的组边界
- 流程之间的连接（支付 → 库存 → 发货）
