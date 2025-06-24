# SQLite Database with PocketFlow

本示例演示了如何将 SQLite 数据库操作与 PocketFlow 正确集成，重点关注：

1. 清晰的代码组织和关注点分离：
   - 用于数据库操作的工具层 (`tools/database.py`)
   - 用于 PocketFlow 集成的节点实现 (`nodes.py`)
   - 流程配置 (`flow.py`)
   - 使用参数绑定安全执行 SQL 查询

2. 数据库操作的最佳实践：
   - 连接管理和正确关闭
   - 使用参数化查询防止 SQL 注入
   - 错误处理和资源清理
   - 简单的模式管理

3. 示例任务管理系统：
   - 数据库初始化
   - 任务创建
   - 任务列表
   - 状态跟踪

## 项目结构

```
pocketflow-tool-database/
├── tools/
│   └── database.py    # SQLite 数据库操作
├── nodes.py          # PocketFlow 节点实现
├── flow.py          # 流程配置
└── main.py          # 示例用法
```

## 设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # 在 Windows 上: venv\Scripts\activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 用法

运行示例：
```bash
python main.py
```

这将：
1. 初始化一个包含任务表的 SQLite 数据库
2. 创建一个示例任务
3. 列出数据库中的所有任务
4. 显示结果

## 演示的关键概念

1. **数据库操作**
   - 安全连接处理
   - 查询参数化
   - 模式管理

2. **代码组织**
   - 数据库操作和 PocketFlow 组件之间清晰分离
   - 模块化项目结构
   - 类型提示和文档

3. **PocketFlow 集成**
   - 具有 prep->exec->post 生命周期的节点实现
   - 流程配置
   - 共享存储用于数据传递

## 示例输出

```
数据库状态: 数据库已初始化
任务状态: 任务创建成功

所有任务:
- ID: 1
  标题: 示例任务
  描述: 这是使用 PocketFlow 创建的示例任务
  状态: pending
  创建时间: 2024-03-02 12:34:56
```
