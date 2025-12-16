"""
 * @Author：cyg
 * @Package：Blueprints
 * @Project：Default (Template) Project
 * @name：Blueprints
 * @Date：2024/12/16 11:42
 * @Filename：自动注册蓝图
"""
import importlib
import pkgutil

import flask_smorest
from flask import Blueprint

from fred_framework.common.Response import Response
from fred_framework.common.Utils import Utils


class Blueprints:
	def __init__(self, app):
		"""
		初始化 BlueprintManager 类
		:param app: Flask 应用对象
		"""
		self.app = app
		self.blp = flask_smorest.Api(app)
	
	def register_blueprints(self):
		"""
		自动注册蓝图
		"""
		self.blp.spec.components.security_scheme("Authorization", {"type": "http", "scheme": "bearer"})
		self.blp.spec.options["security"] = [{"Authorization": []}]
		self.blp.spec.components.schema('Response', schema=Response)
		registered_blueprints = set()
		# self.__method_name("app", registered_blueprints)
		self.__method_name("", registered_blueprints)
		# 仅仅优化swagger显示内容
		Response().swagger_responses(self.blp.spec.to_dict(), self.blp.spec.components.schemas)
		
		return self.blp
	
	def __method_name(self, app_directory, registered_blueprints):
		new_app_directory = ""
		if app_directory != "":
			new_app_directory = app_directory + '.'
		for _, module_name, is_pkg in pkgutil.iter_modules([app_directory]):
			# 跳过非Python模块文件，例如setup.py
			if module_name in ['setup', 'pyproject']:
				continue
			# 动态导入模块
			try:
				module = importlib.import_module(f'{new_app_directory}{module_name}'.replace('app.', 'fred_framework.'))
				for attr_name in dir(module):
					if attr_name.startswith('__'):
						continue
					attr = getattr(module, attr_name)
					modules = self.app.config.get('LOAD_CUSTOM_MODULES', None)
					if new_app_directory == "" and modules != None and attr_name not in modules:
						continue
					if isinstance(attr, Blueprint) and attr.name not in registered_blueprints:
						Utils.import_controller(f'{new_app_directory}{attr.name}.controller'.replace('app.', 'fred_framework.'))
						self.blp.register_blueprint(attr)
						registered_blueprints.add(attr.name)
			except Exception as e:
				pass
