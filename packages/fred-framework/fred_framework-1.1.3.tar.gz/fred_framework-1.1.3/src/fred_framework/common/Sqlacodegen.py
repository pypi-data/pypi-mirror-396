# coding: utf-8
"""
 * @Author：cyg
 * @Package：Sqlacodegen
 * @Project：Default (Template) Project
 * @name：Sqlacodegen
 * @Date：2024/12/31 09:48
 * @Filename：自动生成模型文件
"""
import os
import subprocess

from sqlalchemy import create_engine, inspect


class Sqlacodegen:
	def create_models(self, app, delay_seconds=0):
		"""
		创建模型文件
		:param app: Flask应用实例
		:param delay_seconds: 延迟秒数，用于异步生成
		"""
		if delay_seconds > 0:
			import time
			time.sleep(delay_seconds)
		
		# 获取主数据库的 URI
		main_database_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
		# 获取绑定的其他数据库 URI
		binds = app.config.get('SQLALCHEMY_BINDS', {})
		
		# 确保model目录存在
		model_dir = 'model'
		if not os.path.exists(model_dir):
			os.makedirs(model_dir)
		
		
		# 创建主数据库的模型文件
		if main_database_uri:
			self.__generate_model(app, main_database_uri, '')
		
		# 为每个绑定的数据库生成模型文件
		for bind_name, bind_uri in binds.items():
			self.__generate_model(app, bind_uri, bind_name)

	def __get_tables_with_pk(self, database_uri):
		engine = create_engine(database_uri)
		inspector = inspect(engine)
		tables = []
		for table_name in inspector.get_table_names():
			primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
			if primary_keys:
				tables.append(table_name)
		return tables

	def __generate_model(self, app, database_uri, bind_name):
		# 定义模型文件路径
		if bind_name:
			file_name = f'{bind_name}_model.py'
		else:
			file_name = 'model.py'
		model_dir = 'model'
		if not os.path.exists(model_dir):
			os.makedirs(model_dir)
		
		model_path = os.path.join(model_dir, file_name)
		tables = self.__get_tables_with_pk(database_uri)
		if not tables:
			return
		
		# 构造 sqlacodegen 命令
		command = [
			"flask-sqlacodegen",
			database_uri,
			"--outfile", model_path,
			"--tables", ",".join(tables),
			"--flask"
		]
		
		# 执行命令
		result = subprocess.run(command, capture_output=True, text=True)
		if result.returncode != 0:
			return
			
		# 自动为模型类添加 __bind_key__
		if bind_name:
			self.__add_bind_key_to_models(model_path, bind_name)

	def __add_bind_key_to_models(self, file_path, bind_key):
		with open(file_path, 'r', encoding='utf-8') as file:
			content = file.read()
		
		# 使用正则表达式匹配 class 定义，并插入 __bind_key__
		updated_content = content.replace("__tablename__", f'__bind_key__ = "{bind_key}" \n    __tablename__')
		
		new_content = updated_content.split('db = SQLAlchemy()')
		if len(new_content) >= 2:
			last_content = "from model.model import db \n " + new_content[1]
			# 写回更新后的内容
			with open(file_path, 'w', encoding='utf-8') as file:
				file.write(last_content)