"""
安装后钩子：在项目根目录创建必要的目录结构
"""
import os
import sys
import shutil
from pathlib import Path


def create_project_directories():
    """
    在项目根目录创建必要的目录结构
    """
    # 获取当前工作目录（通常是项目根目录）
    # 如果是在安装时，需要找到项目根目录
    current_dir = Path.cwd()
    
    # 定义要创建的目录及其说明
    directories = {
        'model': {
            'description': '数据模型目录',
            'details': '''此目录用于存放数据库模型文件。

功能说明：
- 存放 SQLAlchemy 模型定义
- 存放数据模型相关的业务逻辑
- 存放模型验证和序列化相关代码

使用示例：
```python
from model.model import db, YourModel
```
'''
        },
        'config': {
            'description': '配置文件目录',
            'details': '''此目录用于存放项目配置文件。

功能说明：
- 存放自定义配置类（继承自 fred_framework.config.Config）
- 存放环境相关的配置文件
- 存放敏感信息配置文件（建议加入 .gitignore）

使用示例：
在 config/Config.py 中定义：
```python
from fred_framework.config.Config import Config

class CustomConfig(Config):
    # 自定义配置项
    CUSTOM_SETTING = 'value'
```
'''
        },
        'translations': {
            'description': '国际化翻译文件目录',
            'details': '''此目录用于存放多语言翻译文件。

功能说明：
- 存放 Babel 翻译文件（.po, .mo）
- 支持多语言切换
- 配合 flask_babelplus 使用

使用示例：
```python
from flask_babelplus import gettext as _

_('Hello World')  # 根据当前语言返回翻译
```
'''
        },
        'scheduler': {
            'description': '定时任务目录',
            'details': '''此目录用于存放定时任务定义。

功能说明：
- 存放 APScheduler 定时任务函数
- 存放任务调度相关配置
- 存放任务执行逻辑

使用示例：
在 scheduler/tasks.py 中定义：
```python
from flask_apscheduler import APScheduler

def my_scheduled_task():
    # 任务逻辑
    pass

# 在配置中注册任务
# SCHEDULER_JOBS = [
#     {
#         'id': 'job1',
#         'func': 'scheduler.tasks:my_scheduled_task',
#         'trigger': 'interval',
#         'seconds': 60
#     }
# ]
```
'''
        }
    }
    
    created_dirs = []
    skipped_dirs = []
    
    for dir_name, info in directories.items():
        dir_path = current_dir / dir_name
        
        # 检查目录是否已存在
        dir_exists = dir_path.exists() and dir_path.is_dir()
        
        # 创建目录（如果不存在）
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            if not dir_exists:
                created_dirs.append(dir_name)
            else:
                skipped_dirs.append(dir_name)
            
            # 创建 README.md 说明文件（如果不存在）
            readme_path = dir_path / 'README.md'
            if not readme_path.exists():
                readme_content = f'''# {dir_name.upper()} 目录

## {info['description']}

{info['details']}

---
*此目录由 fred_framework 自动创建*
'''
                readme_path.write_text(readme_content, encoding='utf-8')
            
            # 创建 __init__.py 文件（如果是 Python 包）
            if dir_name in ['model', 'config', 'scheduler']:
                init_path = dir_path / '__init__.py'
                if not init_path.exists():
                    init_path.write_text('# -*- coding: utf-8 -*-\n', encoding='utf-8')
            
        except Exception as e:
            pass
    
    # 复制 Config.py 到 config 目录
    copy_config_file(current_dir)
    
    # 创建 run.py 文件
    create_run_file(current_dir)
    
    # 复制 demo 目录到项目根目录
    copy_demo_directory(current_dir)
    
    # 创建命令使用文档
    create_commands_documentation(current_dir)
    
    # 复制 README.md 文档到项目根目录
    copy_readme_file(current_dir)
    
    # 创建 requirements.txt 文件
    create_requirements_file(current_dir)
    
    # 创建 .gitignore 文件
    create_gitignore_file(current_dir)
    
    return len(created_dirs) > 0


def copy_demo_directory(project_root):
    """
    将 src/demo 目录复制到项目根目录，支持无限级目录递归复制
    
    功能特点：
    - 支持无限级目录结构
    - 如果目标目录已存在，会合并复制（只复制不存在的文件/目录）
    - 保留目标目录中已存在的文件
    """
    try:
        # 获取当前文件所在的目录
        current_file_path = Path(__file__)
        # 构建源 demo 目录路径
        source_demo_path = current_file_path.parent / 'demo'
        # 目标路径为项目根目录下的 demo 目录
        target_demo_path = project_root / 'demo'
        
        # 检查源目录是否存在
        if not source_demo_path.exists() or not source_demo_path.is_dir():
            return
        
        # 如果目标目录不存在，直接复制整个目录树
        if not target_demo_path.exists():
            shutil.copytree(source_demo_path, target_demo_path)
            return
        
        # 目标目录已存在，进行递归合并复制
        copied_count = _copy_directory_recursive(source_demo_path, target_demo_path)
            
    except Exception as e:
        pass


def _copy_directory_recursive(source_path, target_path):
    """
    递归复制目录，支持无限级目录结构
    
    参数:
        source_path: 源目录路径
        target_path: 目标目录路径
    
    返回:
        int: 复制的文件/目录数量
    """
    copied_count = 0
    
    # 确保目标目录存在
    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)
        copied_count += 1
    
    # 遍历源目录中的所有项目
    for item in source_path.iterdir():
        source_item = source_path / item.name
        target_item = target_path / item.name
        
        try:
            if source_item.is_file():
                # 如果是文件，且目标文件不存在，则复制
                if not target_item.exists():
                    shutil.copy2(source_item, target_item)
                    copied_count += 1
                # 如果目标文件已存在，跳过（保留用户自定义的文件）
            
            elif source_item.is_dir():
                # 如果是目录，递归复制
                if not target_item.exists():
                    # 目标目录不存在，直接复制整个目录树
                    # 使用 dirs_exist_ok=True 参数（Python 3.8+）以避免目标目录已存在的错误
                    try:
                        shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                        # 统计复制的文件数量（包括目录本身）
                        file_count = sum(1 for _ in target_item.rglob('*') if _.is_file())
                        dir_count = sum(1 for _ in target_item.rglob('*') if _.is_dir())
                        copied_count += file_count + dir_count if (file_count + dir_count) > 0 else 1
                    except Exception as copytree_error:
                        # 如果 copytree 失败，尝试使用递归方式
                        target_item.mkdir(parents=True, exist_ok=True)
                        sub_copied = _copy_directory_recursive(source_item, target_item)
                        copied_count += sub_copied if sub_copied > 0 else 1
                else:
                    # 目标目录已存在，递归合并
                    sub_copied = _copy_directory_recursive(source_item, target_item)
                    copied_count += sub_copied
        
        except Exception as e:
            # 单个文件/目录复制失败不影响整体流程
            continue
    
    return copied_count


def copy_config_file(project_root):
    """
    将 fred_framework.config.Config 复制到项目根目录的 config 目录中
    """
    config_dir = project_root / 'config'
    target_config_file = config_dir / 'Config.py'
    
    # 如果目标文件已存在，询问是否覆盖（这里默认不覆盖，保留用户的自定义配置）
    if target_config_file.exists():
        return
    
    # 尝试从多个可能的路径找到源 Config.py 文件
    source_paths = [
        # 方式1: 从已安装的包中查找
        Path(__file__).parent.parent / 'config' / 'Config.py',
        # 方式2: 从当前文件位置推断（开发模式）
        Path(__file__).parent.parent.parent.parent / 'src' / 'fred_framework' / 'config' / 'Config.py',
        # 方式3: 尝试导入模块获取路径
    ]
    
    # 方式3: 通过导入模块获取路径
    try:
        import fred_framework.config.Config as config_module
        if hasattr(config_module, '__file__'):
            source_paths.insert(0, Path(config_module.__file__))
    except Exception:
        pass
    
    source_config_file = None
    for path in source_paths:
        if path.exists() and path.is_file():
            source_config_file = path
            break
    
    if source_config_file is None:
        return
    
    # 确保 config 目录存在
    if not config_dir.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return
    
    # 复制文件
    try:
        shutil.copy2(source_config_file, target_config_file)
        
        # 在文件开头添加说明注释
        try:
            content = target_config_file.read_text(encoding='utf-8')
            if not content.startswith('# -*- coding: utf-8 -*-'):
                header = '''# -*- coding: utf-8 -*-
"""
配置文件 - 从 fred_framework.config.Config 复制而来
你可以在此文件中自定义配置项，继承或覆盖默认配置
"""
'''
                target_config_file.write_text(header + content, encoding='utf-8')
        except Exception as e:
            pass
            
    except Exception as e:
        pass


def create_run_file(project_root):
    """
    在项目根目录创建 run.py 文件
    """
    run_file_path = project_root / 'run.py'
    
    # 如果文件已存在，跳过（保留用户自定义的 run.py）
    if run_file_path.exists():
        return
    
    # run.py 文件内容（只包含指定行的内容）
    run_file_content = '''from fred_framework import create_app
# 创建应用
app = create_app()

if __name__ == '__main__':
    app.run()
'''
    
    try:
        run_file_path.write_text(run_file_content, encoding='utf-8')
    except Exception as e:
        pass


def copy_readme_file(project_root):
    """
    将 fred_framework 包的 README.md 复制到项目根目录
    """
    target_readme_file = project_root / 'README.md'
    
    # 如果目标文件已存在，跳过（保留用户自定义的文档）
    if target_readme_file.exists():
        return
    
    # 尝试从多个可能的路径找到源 README.md 文件
    source_paths = []
    
    # 方式1: 通过导入包获取路径（已安装的包）
    try:
        import fred_framework
        if hasattr(fred_framework, '__file__'):
            # 包的安装位置
            package_dir = Path(fred_framework.__file__).parent.parent
            readme_path = package_dir / 'README.md'
            if readme_path.exists():
                source_paths.append(readme_path)
            
            # 尝试在包的父目录查找（某些安装方式）
            parent_readme = package_dir.parent / 'README.md'
            if parent_readme.exists():
                source_paths.append(parent_readme)
    except Exception:
        pass
    
    # 方式2: 从当前文件位置推断（开发模式）
    current_file_path = Path(__file__)
    # 开发模式：src/fred_framework/install_hook.py -> 项目根目录/README.md
    dev_readme_path = current_file_path.parent.parent.parent.parent / 'README.md'
    if dev_readme_path.exists():
        source_paths.append(dev_readme_path)
    
    # 方式3: 尝试使用 pkg_resources 查找（如果可用）
    try:
        import pkg_resources
        try:
            dist = pkg_resources.get_distribution('fred_framework')
            if dist.location:
                pkg_readme = Path(dist.location) / 'README.md'
                if pkg_readme.exists():
                    source_paths.insert(0, pkg_readme)
        except Exception:
            pass
    except ImportError:
        pass
    
    # 方式4: 尝试使用 importlib.metadata 查找（Python 3.8+）
    try:
        from importlib.metadata import files, PackageNotFoundError
        try:
            package_files = files('fred_framework')
            for file in package_files:
                if file.name == 'README.md':
                    readme_path = Path(file.locate())
                    if readme_path.exists():
                        source_paths.insert(0, readme_path)
                        break
        except (PackageNotFoundError, Exception):
            pass
    except ImportError:
        pass
    
    source_readme_file = None
    for path in source_paths:
        if path.exists() and path.is_file():
            source_readme_file = path
            break
    
    if source_readme_file is None:
        return
    
    # 复制文件
    try:
        shutil.copy2(source_readme_file, target_readme_file)
    except Exception as e:
        pass


def create_requirements_file(project_root):
    """
    在项目根目录创建 requirements.txt 文件
    """
    requirements_file_path = project_root / 'requirements.txt'
    
    # 如果文件已存在，跳过（保留用户自定义的依赖）
    if requirements_file_path.exists():
        return
    
    # requirements.txt 文件内容
    requirements_content = 'fred_framework\n'
    
    try:
        requirements_file_path.write_text(requirements_content, encoding='utf-8')
    except Exception as e:
        pass


def create_gitignore_file(project_root):
    """
    在项目根目录创建 .gitignore 文件
    """
    gitignore_file_path = project_root / '.gitignore'
    
    # 如果文件已存在，跳过（保留用户自定义的 .gitignore）
    if gitignore_file_path.exists():
        return
    
    # .gitignore 文件内容
    gitignore_content = '''__pycache__
.idea
venv
logs
dist
dist-ssr
*.spec
.DS_Store
coverage
*.local

# Python build artifacts
*.egg-info
build/
*.egg

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules

/cypress/videos/
/cypress/screenshots/

# Editor directories and files
!.vscode/extensions.json
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
*.tsbuildinfo
.venv
.ipynb_checkpoints
config/Config.py
docker-compose.override.yml
model/*
'''
    
    try:
        gitignore_file_path.write_text(gitignore_content, encoding='utf-8')
    except Exception as e:
        pass


def create_commands_documentation(project_root):
    """
    在项目根目录创建命令使用文档
    """
    commands_doc_path = project_root / 'FRED_COMMANDS.md'
    
    # 如果文件已存在，跳过（保留用户自定义的文档）
    if commands_doc_path.exists():
        return
    
    # 命令使用文档内容
    commands_doc_content = '''# Fred Framework 命令使用文档

本文档介绍 Fred Framework 提供的所有命令行工具及其使用方法。

## 可用命令

### 1. fred-init

初始化 Fred Framework 项目，创建必要的目录结构和配置文件。

**用法：**
```bash
fred-init [--path PATH]
```

**参数：**
- `--path PATH` (可选): 指定项目根目录路径，默认为当前工作目录

**功能：**
- 创建项目目录结构：
  - `model/` - 数据模型目录
  - `config/` - 配置文件目录（包含 `Config.py`）
  - `translations/` - 国际化翻译文件目录
  - `scheduler/` - 定时任务目录
- 创建 `run.py` 应用启动文件
- 复制 demo 模块到项目根目录（如果不存在）

**示例：**
```bash
# 在当前目录初始化项目
fred-init

# 在指定目录初始化项目
fred-init --path /path/to/your/project
```

**注意：**
- 如果目录或文件已存在，不会覆盖，保留现有内容
- 建议在项目根目录下运行此命令

---

### 2. fred-create

创建新的业务模块，自动生成模块的目录结构和基础文件。

**用法：**
```bash
fred-create MODULE_NAME [--path PATH]
```

**参数：**
- `MODULE_NAME` (必需): 模块名称（只能包含字母、数字和下划线）
- `--path PATH` (可选): 指定项目根目录路径，默认为当前工作目录

**功能：**
自动创建以下目录结构和文件：
```
模块名/
├── __init__.py              # Blueprint 定义
├── controller/
│   ├── __init__.py          # 路由控制和用户验证
│   └── {ModuleName}Controller.py  # 控制器（包含 GET/POST/PUT/DELETE 方法）
├── service/
│   ├── __init__.py
│   └── {ModuleName}Service.py  # 服务层
├── model/
│   └── {ModuleName}Model.py    # 数据模型
├── schema/
│   ├── __init__.py
│   └── {ModuleName}Schema.py   # Schema 定义
└── html/                     # 前端文件目录
    └── README.md              # 前端项目说明
```

**示例：**
```bash
# 创建名为 user 的模块
fred-create user

# 创建名为 user_management 的模块（支持下划线）
fred-create user_management

# 在指定项目目录创建模块
fred-create mymodule --path /path/to/project
```

**说明：**
- 模块名称会自动转换为首字母大写的格式用于类名（如：`user` → `User`，`user_management` → `UserManagement`）
- 生成的模块会自动注册到框架中，可以直接使用
- 所有文件都按照 demo 模块的模板生成，包含必要的导入和基本结构
- 控制器默认包含 GET、POST、PUT、DELETE 四个方法，可根据需要修改

**注意事项：**
- 模块名只能包含字母、数字和下划线
- 如果模块已存在，命令会失败并提示错误
- 建议在项目根目录下运行此命令

---

## 快速开始

### 1. 初始化项目

```bash
# 安装框架后，首先初始化项目
fred-init
```

### 2. 创建业务模块

```bash
# 创建你的第一个模块
fred-create user
```

### 3. 启动应用

```bash
# 启动开发服务器
python run.py
```

---

## 常见问题

### Q: 命令找不到怎么办？

A: 确保已正确安装 Fred Framework：
```bash
pip install fred_framework
# 或开发模式安装
pip install -e .
```

### Q: 如何查看命令帮助？

A: 使用 `--help` 参数：
```bash
fred-init --help
fred-create --help
```

### Q: 模块创建后如何修改？

A: 可以直接编辑生成的文件，框架会自动加载修改后的代码。

### Q: 可以删除已创建的模块吗？

A: 可以，直接删除模块目录即可。但请注意：
- 如果模块中有数据库模型，需要处理数据迁移
- 如果模块已注册路由，需要确保没有其他代码依赖

---

## 更多信息

- 项目文档：查看项目 README.md
- 配置说明：查看 `config/Config.py`
- 示例代码：查看 `demo/` 目录

---

*本文档由 Fred Framework 自动生成*
'''
    
    try:
        commands_doc_path.write_text(commands_doc_content, encoding='utf-8')
    except Exception as e:
        pass


def main():
    """
    命令行入口函数，用于初始化项目目录和文件
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='初始化 fred_framework 项目目录和文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  fred-init                    # 在当前目录初始化项目
  fred-init --path /path/to/project  # 在指定目录初始化项目
        '''
    )
    
    parser.add_argument(
        '--path',
        type=str,
        default=None,
        help='项目根目录路径（默认为当前工作目录）'
    )
    
    args = parser.parse_args()
    
    # 如果指定了路径，切换到该目录
    if args.path:
        target_path = Path(args.path).resolve()
        if not target_path.exists():
            sys.exit(1)
        if not target_path.is_dir():
            sys.exit(1)
        os.chdir(target_path)
    
    # 执行初始化
    try:
        create_project_directories()
    except Exception as e:
        sys.exit(1)


if __name__ == '__main__':
    main()

