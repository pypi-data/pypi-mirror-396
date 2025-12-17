# Fred Framework

Fred是一个基于Flask的Web框架，内置了常用的工具和扩展，帮助开发者快速构建Web应用程序。

## 功能特性

- 基于Flask的轻量级Web框架
- 内置JWT认证支持
- 数据库ORM支持（SQLAlchemy）
- Redis集成
- 邮件发送功能
- 定时任务调度
- 国际化支持
- Swagger API文档
- 图片验证码生成
- 阿里云短信服务集成
- 微信登录集成
- 数据加密功能
- 日志系统

## 安装

```bash
pip install fred_framework
```

## 快速开始

### 1. 初始化项目

安装后，在项目目录中运行初始化命令来创建必要的目录和文件：

```bash
# 在当前目录初始化项目
fred-init

# 或在指定目录初始化项目
fred-init --path /path/to/your/project
```

初始化命令会自动创建以下目录和文件：
- `model/` - 数据模型目录
- `config/` - 配置文件目录（包含 `Config.py`）
- `translations/` - 国际化翻译文件目录
- `scheduler/` - 定时任务目录
- `run.py` - 应用启动文件

### 2. 使用框架

直接使用生成的 `run.py` 文件：

```bash
python run.py
```

## 配置

在使用Fred框架前，请根据需要修改`config/Config.py`中的配置项。

## 依赖

Fred框架依赖以下第三方库：

- Flask >= 3.1.2
- flask_cors >= 6.0.1
- flask_jwt_extended >= 4.7.1
- Pillow >= 11.3.0
- flask_smorest >= 0.46.2
- flask_swagger_ui >= 5.21.0
- cryptography >= 46.0.0
- requests >= 2.32.5
- flask_apscheduler >= 1.13.1
- flask_babelplus >= 2.2.0
- flask_sqlacodegen >= 2.0.0
- flask_sqlalchemy >= 3.1.1
- pymysql >= 1.1.2
- pytz >= 2025.2
- flask_mail >= 0.10.0
- redis >= 7.0.0

## 许可证

MIT License
