from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.egg_info import egg_info
import sys
import os
from pathlib import Path

# 读取代码规范.md内容作为long_description
# 优先使用代码规范.md，如果不存在则尝试README.md
long_description = ""
readme_files = ["代码规范.md", "README.md"]
for readme_file in readme_files:
    try:
        with open(readme_file, "r", encoding="utf-8") as fh:
            long_description = fh.read()
            break
    except FileNotFoundError:
        continue

# 如果两个文件都不存在，使用默认描述
if not long_description:
    long_description = "A Flask-based web framework with built-in utilities and extensions"

# 依赖从 pyproject.toml 中读取，不再从 requirements.txt 读取
# with open("requirements.txt", "r", encoding="utf-8") as fh:
#     requirements = [line.strip() for line in fh.readlines() if line.strip() and not line.startswith("#")]


class EggInfoCommand(egg_info):
    """
    自定义 egg_info 命令，将 egg-info 目录生成到项目根目录而不是 src 目录
    """
    def initialize_options(self):
        egg_info.initialize_options(self)
        # 设置 egg_base 为项目根目录（setup.py 所在目录），使用相对路径
        self.egg_base = '.'


class PostInstallCommand(install):
    """
    安装后执行的自定义命令
    在项目根目录创建必要的目录结构
    """
    def _find_project_root(self):
        """
        查找项目根目录（包含 setup.py 或 run.py 的目录）
        """
        # 从当前工作目录开始查找
        current = Path.cwd()
        
        # 检查当前目录是否是项目根目录
        if (current / 'setup.py').exists() or (current / 'run.py').exists():
            return current
        
        # 向上查找，最多查找 5 层
        for _ in range(5):
            if (current / 'setup.py').exists() or (current / 'run.py').exists():
                return current
            parent = current.parent
            if parent == current:  # 已到达根目录
                break
            current = parent
        
        # 如果找不到，返回当前工作目录
        return Path.cwd()
    
    def run(self):
        # 执行标准安装
        install.run(self)
        
        # 不再在安装时自动创建目录结构
        # 用户需要使用 fred-init 命令来初始化项目


setup(
    name="fred_framework",
    version="1.0.6",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Flask-based web framework with built-in utilities and extensions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fred-framework",  # 请替换为实际的仓库地址
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    # install_requires 从 pyproject.toml 的 dependencies 中读取
    entry_points={
        "console_scripts": [
            "fred-init=fred_framework.install_hook:main",
            "fred-create=fred_framework.create_module:main",
        ],
    },
    include_package_data=True,
    package_data={
        "fred_framework": [
            "demo/**/*",
            "fonts/**/*",
            "代码规范.md",
        ],
    },
    cmdclass={
        'egg_info': EggInfoCommand,
        'install': PostInstallCommand,
    },
)