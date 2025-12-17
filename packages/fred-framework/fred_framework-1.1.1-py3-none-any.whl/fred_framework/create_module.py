# -*- coding: utf-8 -*-
"""
模块生成工具：用于创建新的业务模块
"""
import os
import sys
import shutil
from pathlib import Path
from string import Template


def get_module_name_capitalized(module_name: str) -> str:
    """
    将模块名转换为首字母大写的格式
    例如: demo -> Demo, user_management -> UserManagement
    """
    return ''.join(word.capitalize() for word in module_name.split('_'))


def copy_demo_structure(module_name: str, target_module_dir: Path, project_root: Path):
    """
    从 demo 目录复制所有目录和文件到新模块，并替换相关内容
    
    Args:
        module_name: 模块名称
        target_module_dir: 目标模块目录路径
        project_root: 项目根目录
    """
    try:
        # 获取当前文件所在的目录
        current_file_path = Path(__file__)
        # 构建源 demo 目录路径
        source_demo_path = current_file_path.parent / 'demo'
        
        # 检查源目录是否存在
        if not source_demo_path.exists() or not source_demo_path.is_dir():
            sys.exit(1)
        
        # 复制整个 demo 目录树（排除 __init__.py，因为我们需要根据模块名生成）
        
        # 检查源目录中的子目录
        source_dirs = [item.name for item in source_demo_path.iterdir() if item.is_dir()]
        
        try:
            # 使用 dirs_exist_ok=True 参数（Python 3.8+）以避免目标目录已存在的错误
            # 但实际上，在创建新模块时，目标目录应该不存在
            shutil.copytree(
                source_demo_path, 
                target_module_dir, 
                ignore=shutil.ignore_patterns('__init__.py'),
                dirs_exist_ok=True
            )
            
            # 验证复制的目录
            copied_dirs = [item.name for item in target_module_dir.iterdir() if item.is_dir()]
            
            # 检查 frontend 和 common 目录是否存在
            frontend_dir = target_module_dir / 'frontend'
            common_dir = target_module_dir / 'common'
            
            missing_dirs = []
            if not frontend_dir.exists():
                missing_dirs.append('frontend')
            if (source_demo_path / 'common').exists() and not common_dir.exists():
                missing_dirs.append('common')
            
            if missing_dirs:
                # 使用备用方法复制缺失的目录
                for dir_name in missing_dirs:
                    source_dir = source_demo_path / dir_name
                    target_dir = target_module_dir / dir_name
                    if source_dir.exists() and source_dir.is_dir():
                        try:
                            if target_dir.exists():
                                shutil.rmtree(target_dir)
                            shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
                        except Exception as backup_error:
                            pass
                
        except FileExistsError as e:
            sys.exit(1)
        except Exception as e:
            sys.exit(1)
        
        # 替换文件内容中的 demo/Demo 为新模块名
        replace_module_names(target_module_dir, module_name, project_root)
        
        # 重命名文件（Demo -> ModuleName）
        rename_demo_files(target_module_dir, module_name, project_root)
        
        # 更新 vite.config.ts 中的 outDir 配置
        frontend_dir = target_module_dir / 'frontend'
        if frontend_dir.exists():
            update_vite_config(frontend_dir, module_name)
        
    except Exception as e:
        sys.exit(1)


def replace_module_names(target_dir: Path, module_name: str, project_root: Path):
    """
    递归替换目录中所有文件内容中的 demo/Demo 为新模块名
    
    Args:
        target_dir: 目标目录
        module_name: 新模块名称
        project_root: 项目根目录
    """
    module_name_capitalized = get_module_name_capitalized(module_name)
    
    # 需要替换的文件扩展名
    text_extensions = {'.py', '.ts', '.tsx', '.vue', '.js', '.jsx', '.json', '.md', '.txt', '.yml', '.yaml', '.config', '.cjs', '.mjs'}
    
    # 需要排除的目录和文件
    exclude_dirs = {'node_modules', '.git', '__pycache__', '.pytest_cache', 'dist', 'build', '.vscode', '.idea'}
    exclude_files = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'}
    
    replaced_count = 0
    
    for root, dirs, files in os.walk(target_dir):
        # 排除不需要处理的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # 排除不需要处理的文件
            if file in exclude_files:
                continue
            
            file_path = Path(root) / file
            
            # 只处理文本文件
            if file_path.suffix.lower() in text_extensions or file_path.name in ['.gitignore', '.env', '.env.development', '.env.production']:
                try:
                    # 读取文件内容
                    content = file_path.read_text(encoding='utf-8')
                    original_content = content
                    
                    # 替换 demo -> module_name
                    content = content.replace('demo', module_name)
                    content = content.replace('Demo', module_name_capitalized)
                    # 处理可能的其他变体
                    content = content.replace('DEMO', module_name.upper())
                    
                    # 如果内容有变化，写入文件
                    if content != original_content:
                        file_path.write_text(content, encoding='utf-8')
                        replaced_count += 1
                except (UnicodeDecodeError, PermissionError) as e:
                    # 跳过二进制文件或无法读取的文件
                    pass


def rename_demo_files(target_dir: Path, module_name: str, project_root: Path):
    """
    重命名文件中的 Demo 为新模块名
    
    Args:
        target_dir: 目标目录
        module_name: 新模块名称
        project_root: 项目根目录
    """
    module_name_capitalized = get_module_name_capitalized(module_name)
    renamed_count = 0
    
    # 需要重命名的文件模式
    rename_patterns = [
        ('DemoController.py', f'{module_name_capitalized}Controller.py'),
        ('DemoService.py', f'{module_name_capitalized}Service.py'),
        ('DemoModel.py', f'{module_name_capitalized}Model.py'),
        ('DemoSchema.py', f'{module_name_capitalized}Schema.py'),
    ]
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = Path(root) / file
            
            # 检查是否需要重命名
            for old_name, new_name in rename_patterns:
                if file == old_name:
                    new_file_path = file_path.parent / new_name
                    if not new_file_path.exists():
                        file_path.rename(new_file_path)
                        renamed_count += 1
                    break


def update_vite_config(frontend_dir: Path, module_name: str):
    """
    更新 vite.config.ts 中的 outDir 配置
    
    Args:
        frontend_dir: frontend 目录路径
        module_name: 模块名称
    """
    vite_config_path = frontend_dir / 'vite.config.ts'
    if not vite_config_path.exists():
        return
    
    try:
        content = vite_config_path.read_text(encoding='utf-8')
        # 替换 outDir 配置
        import re
        # 匹配 outDir: "../templates/demo" 或 outDir: '../templates/demo'
        pattern = r'outDir:\s*["\']\.\./templates/[^"\']+["\']'
        replacement = f'outDir: "../templates/{module_name}"'
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            vite_config_path.write_text(new_content, encoding='utf-8')
    except Exception as e:
        pass


def create_module_structure(module_name: str, project_root: Path = None):
    """
    创建新模块的目录结构和文件
    
    Args:
        module_name: 模块名称（小写，可以使用下划线）
        project_root: 项目根目录路径，默认为当前工作目录
    """
    if project_root is None:
        project_root = Path.cwd()
    
    # 检查是否在项目根目录（有 run.py 或 setup.py）
    if not (project_root / 'run.py').exists() and not (project_root / 'setup.py').exists():
        sys.exit(1)
    
    # 检查模块名是否合法
    if not module_name or not module_name.replace('_', '').isalnum():
        sys.exit(1)
    
    # 转换为小写
    module_name = module_name.lower()
    
    # 获取首字母大写的模块名（用于类名）
    module_name_capitalized = get_module_name_capitalized(module_name)
    
    # 模块目录路径
    module_dir = project_root / module_name
    
    # 检查模块是否已存在
    if module_dir.exists():
        sys.exit(1)
    
    try:
        # 复制整个 demo 目录结构
        copy_demo_structure(module_name, module_dir, project_root)
        
        # 创建 __init__.py (模块主文件，定义 Blueprint)
        init_content = Template('''from flask_smorest import Blueprint
#
${module_name} = Blueprint('${module_name}', __name__, url_prefix="/${module_name}")
# 变量${module_name} 需要和目录名字相同才能自动注册
# 所有的路由 必须写在controller中 框架会自动引入路由
# 所有的前端打包文件必须放在templates文件夹中例如:templates/${module_name} 其中${module_name} 表示当前这个模块的名字
''').substitute(module_name=module_name)
        
        init_file = module_dir / '__init__.py'
        init_file.write_text(init_content, encoding='utf-8')
        
        # 所有文件和目录已在 copy_demo_structure 中复制并处理
        
    except Exception as e:
        sys.exit(1)


def main():
    """
    命令行入口函数，用于创建新模块
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='创建新的业务模块',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  fred-create user              # 创建名为 user 的模块
  fred-create user_management   # 创建名为 user_management 的模块
  fred-create --path /path/to/project mymodule  # 在指定项目目录创建模块
        '''
    )
    
    parser.add_argument(
        'module_name',
        type=str,
        help='模块名称（只能包含字母、数字和下划线）'
    )
    
    parser.add_argument(
        '--path',
        type=str,
        default=None,
        help='项目根目录路径（默认为当前工作目录）'
    )
    
    args = parser.parse_args()
    
    # 如果指定了路径，使用该路径作为项目根目录
    if args.path:
        project_root = Path(args.path).resolve()
        if not project_root.exists():
            sys.exit(1)
        if not project_root.is_dir():
            sys.exit(1)
    else:
        project_root = Path.cwd()
    
    # 执行创建模块
    try:
        create_module_structure(args.module_name, project_root)
    except Exception as e:
        sys.exit(1)


if __name__ == '__main__':
    main()
