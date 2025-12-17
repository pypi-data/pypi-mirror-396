# Demo 模块说明

## 模块概述

Demo 模块是框架的示例模块，展示了如何创建一个完整的业务模块，包括后端 API 和前端界面。

## 目录结构

```
demo/
├── controller/         # 控制器层 - 处理 HTTP 请求和路由
│   ├── __init__.py    # 用户认证装饰器和请求钩子
│   ├── DemoController.py  # Demo 控制器
├── schema/            # 数据验证层 - 定义请求/响应数据结构
│   ├── __init__.py    # Schema 模块初始化
│   ├── DemoSchema.py  # Demo 数据验证模式
├── service/           # 服务层 - 处理业务逻辑
│   ├── __init__.py    # Service 模块初始化
│   ├── DemoService.py # Demo 服务类
├── frontend/          # 前端项目 - Vue 3 + TypeScript
│   ├── src/           # 前端源代码
│   ├── public/        # 静态资源
│   ├── README.md      # 前端项目通用说明
├── __init__.py        # 模块初始化 - Blueprint 注册
└── README.md          # 本文件 - 模块总体说明
```

## 架构说明

Demo 模块采用 MVC（Model-View-Controller）架构模式：

### 1. Controller（控制器层）
- **位置**：`controller/` 目录
- **职责**：处理 HTTP 请求、路由注册、参数验证、调用服务层
- **特点**：
  - 使用 Flask-Smorest 的 Blueprint 注册路由
  - 使用装饰器进行用户认证和权限验证
  - 使用 Schema 进行请求参数验证

### 2. Schema（数据验证层）
- **位置**：`schema/` 目录
- **职责**：定义请求和响应的数据结构，进行数据验证
- **特点**：
  - 使用 marshmallow 库定义数据模式
  - 自动验证请求参数的类型和格式
  - 验证失败时自动返回错误响应

### 3. Service（服务层）
- **位置**：`service/` 目录
- **职责**：处理业务逻辑，调用数据访问层
- **特点**：
  - 独立于 HTTP 请求处理
  - 可被多个控制器复用
  - 便于单元测试

### 4. Frontend（前端层）
- **位置**：`frontend/` 目录
- **职责**：提供用户界面，与后端 API 交互
- **特点**：
  - Vue 3 + TypeScript 开发
  - 使用 Vite 构建工具
  - 打包后输出到 `templates/demo/` 目录

## 模块注册

模块通过 `__init__.py` 文件自动注册到 Flask 应用：

```python
from flask_smorest import Blueprint

demo = Blueprint('demo', __name__, url_prefix="/demo")
```

- **Blueprint 名称**：`demo`（必须与目录名称相同）
- **URL 前缀**：`/demo`
- **自动注册**：框架会自动发现并注册所有模块的 Blueprint

## 路由规则

1. **路由定义**：
   - 所有路由必须在 `controller/` 目录下的控制器类中定义
   - 使用 `@demo.route()` 装饰器注册路由
   - 路由路径会自动添加 `/demo` 前缀

2. **认证要求**：
   - 使用 `@user_required` 装饰器进行用户认证
   - 验证 JWT token 和用户角色权限
   - 用户信息自动存储到 session 中

3. **参数验证**：
   - 使用 `@demo.arguments(DemoSchema)` 进行参数验证
   - 支持从查询参数（`location='query'`）或请求体（JSON）中获取数据

## 前端集成

1. **打包输出**：
   - 前端项目打包后输出到 `templates/demo/` 目录
   - Flask 框架会自动识别并服务这些静态文件

2. **API 调用**：
   - 前端通过 Axios 调用后端 API
   - API 路径会自动添加 `/demo` 前缀
   - 需要在 `src/api/config/service.ts` 中配置后端接口地址

3. **路由权限**：
   - 使用 Vue Router 进行路由管理
   - 支持动态路由权限拦截
   - 支持页面按钮权限控制

## 开发流程

### 创建新功能

1. **定义 Schema**（`schema/`）：
   - 创建或修改 Schema 类定义数据结构

2. **实现服务层**（`service/`）：
   - 在服务类中添加业务逻辑方法

3. **创建控制器**（`controller/`）：
   - 在控制器类中添加路由处理方法
   - 使用装饰器进行认证和参数验证
   - 调用服务层方法处理业务逻辑

4. **开发前端**（`frontend/`）：
   - 在 `src/views/` 中创建页面组件
   - 在 `src/api/` 中定义 API 接口
   - 在 `src/routers/` 中配置路由

### 测试

1. **后端测试**：
   - 测试控制器路由是否正确注册
   - 测试参数验证是否生效
   - 测试业务逻辑是否正确

2. **前端测试**：
   - 测试页面是否正常显示
   - 测试 API 调用是否成功
   - 测试权限控制是否生效

## 注意事项

1. **命名规范**：
   - Blueprint 变量名必须与目录名称相同
   - 路由路径建议使用 RESTful 风格
   - 文件命名使用大驼峰（PascalCase）

2. **依赖关系**：
   - Controller → Service → Data/ORM
   - Controller → Schema（用于参数验证）
   - Frontend → API → Backend

3. **代码组织**：
   - 控制器只处理路由，不处理业务逻辑
   - 业务逻辑放在服务层
   - 数据验证放在 Schema 层

4. **前端打包**：
   - 确保 `vite.config.ts` 中的 `outDir` 配置正确
   - 输出目录名称必须与模块名称一致
   - 打包前检查环境变量配置

## 相关文档

- [Controller 目录说明](./controller/README.md)
- [Schema 目录说明](./schema/README.md)
- [Service 目录说明](./service/README.md)
- [Frontend 目录说明](./frontend/README-DEMO.md)
