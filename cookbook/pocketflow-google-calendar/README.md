# Pocket Google Calendar

一个基于 Pocket Flow 框架的 Google 日历集成应用程序。

## 📋 描述

该项目使用 Pocket Flow 框架实现了 Google 日历集成，通过简单直观的界面高效管理事件和约会。

## 🚀 功能

- Google 日历 API 集成
- 事件管理
- 约会查看
- 使用 Pocket Flow 的基于流的界面

## 🛠️ 使用的技术

- Python
- Pocket Flow 框架
- Google 日历 API
- Pipenv 用于依赖管理

## 📦 安装

1. 克隆仓库：
```bash
git clone [REPOSITORY_URL]
cd pocket-google-calendar
```

2. 使用 Pipenv 安装依赖：
```bash
pipenv install
```

## 🔑 凭据设置

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 为您的项目启用 Google 日历 API
4. 创建凭据：
   - 转到“API 和服务”>“凭据”
   - 点击“创建凭据”>“OAuth 客户端 ID”
   - 选择“桌面应用程序”作为应用程序类型
   - 下载凭据文件
   - 将其重命名为 `credentials.json`
   - 将其放置在项目的根目录中

## 🌍 环境变量

在根目录中创建 `.env` 文件，包含以下变量：

```env
# Google Calendar API 配置
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# 应用程序配置
TIMEZONE=America/Sao_Paulo  # 或您偏好的时区
```

## 🔧 配置

1. 激活虚拟环境：
```bash
pipenv shell
```

2. 运行应用程序：
```bash
python main.py
```

## 预期输出

运行示例时，您将看到类似以下的输出：

```
=== 列出您的日历 ===
- 主要日历
- 工作
- 个人

=== 创建一个示例事件 ===
事件创建成功！
事件 ID: abc123xyz
```


## 📁 项目结构

```
pocket-google-calendar/
├── main.py           # 应用程序入口点
├── nodes.py          # Pocket Flow 节点定义
├── utils/            # 实用工具和辅助函数
├── Pipfile           # Pipenv 配置
├── credentials.json  # Google 日历 API 凭据
├── .env             # 环境变量
└── token.pickle      # Google 日历身份验证令牌
```

## 🤝 贡献

1. Fork 项目
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交拉取请求

## 📝 许可证

本项目采用 MIT 许可证。更多详情请参阅 [LICENSE](LICENSE) 文件。

## ✨ 致谢

- [Pocket Flow](https://github.com/ssvip9527/PocketFlow) - 使用的框架
- [Google Calendar API](https://developers.google.com/calendar) - 集成 API