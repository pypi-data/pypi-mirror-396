# coding: utf-8
"""
 * @Author：cyg
 * @Package：Route
 * @Project：Default (Template) Project
 * @name：Route
 * @Date：2025/6/1 11:25
 * @Filename：Route
"""

import os

from flask import current_app, send_from_directory, render_template, abort
from jinja2 import ChoiceLoader, FileSystemLoader


class Route:
    @staticmethod
    def _get_project_root():
        """
        获取项目根目录（使用当前工作目录）
        
        :return: 项目根目录路径
        """
        return os.getcwd()
    
    def __init__(self, app):
        self.app = app
        

        # 注册上传文件路由
        @app.route('/upload/<path:path>')
        def uploads(path):
            # 使用项目根目录，因为 upload 目录在项目根目录下
            path_config = current_app.config.get('PATH_CONFIG', {})
            upload_folder = path_config.get('UPLOAD_FOLDER', 'upload')
            project_root = self._get_project_root()
            upload_dir = os.path.join(project_root, upload_folder)
            return send_from_directory(upload_dir, path)
        

    def set_routes(self):
        sys_blueprints = ['api-docs', 'swagger_ui']
        i = 0
        project_root = self._get_project_root()
        jinja_loader_arr = [self.app.jinja_loader]
        home_modules = self.app.config.get('HOME_MODULES', None)
        for blueprint_name in self.app.blueprints:
            if blueprint_name in sys_blueprints:
                continue
            jinja_loader_arr.append(FileSystemLoader(f'{blueprint_name}/templates'))
            is_home = False
            web_path = os.path.join(project_root, f'{blueprint_name}/templates/{blueprint_name}')
            index_path = os.path.join(project_root, f'{blueprint_name}/templates/{blueprint_name}/index.html')
            if not os.path.exists(web_path) or not os.path.exists(index_path):
                continue
            if not home_modules and i == 0:
                is_home = True
            elif home_modules == blueprint_name:
                is_home = True
            if is_home:
                self.register_static_route(blueprint_name, is_home)
            self.register_static_route(blueprint_name, False)
            i += 1
        self.app.jinja_loader = ChoiceLoader(jinja_loader_arr)

    def register_static_route(self, blueprint_name, is_home):
        assets_path_pre = "/" if is_home else f"/{blueprint_name}"

        # 动态生成唯一 endpoint 名称
        if is_home:
            assets_endpoint = f"{blueprint_name}_home_assets"
            index_endpoint = f"{blueprint_name}_home_index"
        else:
            assets_endpoint = f"{blueprint_name}_assets"
            index_endpoint = f"{blueprint_name}_index"

        @self.app.route(f"{assets_path_pre}/assets/<path:path>", endpoint=assets_endpoint)
        def send_assets(path):
            # 使用项目根目录
            project_root = self._get_project_root()
            assets_dir = os.path.join(project_root, f"{blueprint_name}/templates/{blueprint_name}/assets")
            return send_from_directory(assets_dir, path)

        @self.app.route(f"{assets_path_pre}", endpoint=f"{index_endpoint}_root")
        def module_index_root():
            return render_template(f"{blueprint_name}/index.html")

        # 处理非assets路径的请求
        @self.app.route(f"{assets_path_pre}/<path:path>", endpoint=index_endpoint)
        def module_index_path(path):
            # 如果是上传文件路径，跳过处理，让上传路由处理
            if path.startswith('upload/'):
                abort(404, "Not Found")
            # 如果是下载文件路径，跳过处理，让下载路由处理
            if path.startswith('download/'):
                abort(404, "Not Found")
            # 如果是资源文件路径，跳过处理，让资源路由处理
            if path.startswith('resource/'):
                abort(404, "Not Found")
            
            # 使用项目根目录
            project_root = self._get_project_root()
            # 检查是否是文件请求
            file_path = os.path.join(project_root, f'{blueprint_name}/templates/{blueprint_name}', path)
            if os.path.isfile(file_path):
                # 如果是文件，直接返回文件内容
                return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))
            # 只在路径是目录或特定路径时返回index.html
            if path.endswith('/') or path == 'index.html':
                return render_template(f"{blueprint_name}/index.html")
            # 对于其他请求，返回404
            abort(404, "Not Found")
