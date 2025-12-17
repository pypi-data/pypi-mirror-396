import importlib
import os
import pkgutil
import re
import secrets
import string
import hashlib
import base64
from datetime import datetime, timedelta
from decimal import Decimal
from random import randint
from time import time

from cryptography.fernet import Fernet
from flask import current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token


class Utils:
	@staticmethod
	def get_project_root(app=None):
		"""
		获取项目根目录
		
		获取优先级：
		1. 如果提供了 app 参数，从 app.config 中读取 PROJECT_ROOT
		2. 如果存在应用上下文，从 current_app.config 中读取 PROJECT_ROOT
		3. 使用当前工作目录（Path.cwd()）
		
		:param app: Flask 应用实例（可选）
		:return: 项目根目录的 Path 对象
		"""
		from pathlib import Path
		
		# 优先使用传入的 app 参数
		if app is not None:
			project_root_raw = app.config.get('PROJECT_ROOT')
			if project_root_raw:
				# 确保转换为 Path 对象（配置中可能是字符串）
				project_root = Path(project_root_raw) if not isinstance(project_root_raw, Path) else project_root_raw
			else:
				project_root = Path.cwd()
		else:
			# 尝试使用 current_app（需要应用上下文）
			try:
				project_root_raw = current_app.config.get('PROJECT_ROOT')
				if project_root_raw:
					# 确保转换为 Path 对象（配置中可能是字符串）
					project_root = Path(project_root_raw) if not isinstance(project_root_raw, Path) else project_root_raw
				else:
					project_root = Path.cwd()
			except RuntimeError:
				# 没有应用上下文，使用当前工作目录
				project_root = Path.cwd()
		
		# 确保返回的是 Path 对象
		if not isinstance(project_root, Path):
			project_root = Path(project_root)
		
		return project_root

	@staticmethod
	def import_project_models(*model_names, app=None):
		"""
		从项目根目录的 model 目录加载模型模块到 sys.modules
		
		只从项目根目录的 model 目录导入，不会从 fred_framework.model.model 导入
		使用文件系统路径直接导入，确保不会从已安装的包中导入
		加载后，可以通过 `from model.model import xxx` 直接使用模型
		
		:param model_names: 要验证的模型名称列表（可选，用于验证模型是否存在）
		:param app: Flask 应用实例（可选，用于获取项目根目录）
		"""
		import sys
		import importlib.util
		from pathlib import Path
		
		# 获取项目根目录
		project_root = Utils.get_project_root(app)
		
		# 确保 project_root 是 Path 对象（双重保险）
		if not isinstance(project_root, Path):
			project_root = Path(project_root)
		
		model_file = project_root / 'model' / 'model.py'
		if not model_file.exists():
			raise ImportError(f"无法找到模型文件: {model_file}。请确保项目根目录存在 model/model.py 文件，或运行 'fred-init' 命令初始化项目。")
		
		# 使用文件系统路径直接导入，避免从已安装的包中导入
		try:
			# 生成唯一的模块名，基于项目根目录路径，避免与已安装的包冲突
			module_name = f'_project_model_{hash(str(project_root))}'
			
			# 检查是否已经加载过该模块
			if module_name in sys.modules:
				model_module = sys.modules[module_name]
			else:
				# 确保项目根目录在 sys.path 的最前面，避免从已安装的包中导入
				project_root_str = str(project_root)
				if project_root_str in sys.path:
					sys.path.remove(project_root_str)
				sys.path.insert(0, project_root_str)
				
				# 临时移除 fred_framework 相关的路径，避免导入已安装的包
				original_path = sys.path.copy()
				filtered_path = [p for p in sys.path if 'fred_framework' not in p or project_root_str in p]
				sys.path[:] = filtered_path
				
				try:
					# 从文件路径加载模块
					spec = importlib.util.spec_from_file_location(module_name, model_file)
					if spec is None or spec.loader is None:
						raise ImportError(f"无法从文件路径创建模块规范: {model_file}")
					
					model_module = importlib.util.module_from_spec(spec)
					# 设置模块的 __file__ 和 __name__ 属性
					model_module.__file__ = str(model_file)
					model_module.__name__ = module_name
					# 设置 __path__ 为项目根目录，确保相对导入指向正确位置
					model_module.__path__ = [str(project_root / 'model')]
					
					sys.modules[module_name] = model_module
					spec.loader.exec_module(model_module)
					
					# 同时将模块注册为标准的 model.model 模块，确保所有地方使用同一个模块实例
					# 这样可以避免 "The current Flask app is not registered with this 'SQLAlchemy' instance" 错误
					if 'model.model' not in sys.modules:
						sys.modules['model.model'] = model_module
				finally:
					# 恢复原始 sys.path
					sys.path[:] = original_path
			
			# 如果标准的 model.model 模块已存在但不是同一个实例，则同步 db 实例
			if 'model.model' in sys.modules and sys.modules['model.model'] is not model_module:
				# 如果新模块有 db 实例，同步到标准模块
				if hasattr(model_module, 'db'):
					setattr(sys.modules['model.model'], 'db', model_module.db)
			
			# 如果提供了模型名称，验证它们是否存在
			if model_names:
				for name in model_names:
					if not hasattr(model_module, name):
						raise AttributeError(f"模型 '{model_file}' 中没有找到 '{name}'")
		except Exception as e:
			error_msg = str(e)
			# 如果错误信息中包含 fred_framework.model.model，提供更清晰的错误提示
			if 'fred_framework.model.model' in error_msg:
				raise ImportError(
					f"无法导入模型模块 '{model_file}'。检测到尝试从已安装的包 'fred_framework.model.model' 导入。"
					f"请确保项目根目录存在 model/model.py 文件，并且该文件不包含从 'fred_framework.model.model' 导入的语句。"
					f"原始错误: {error_msg}"
				)
			raise ImportError(f"无法导入模型模块 '{model_file}'。错误: {error_msg}")

	@staticmethod
	def reform_decimal(s, num=2) -> float:
		"""
		# 四舍五入
		:param s: 小数字符串和 浮点数
		:param num: 保留位数
		:return: 返回浮点数
		"""
		if not s:
			return 0.0
		if s != "None":
			result = round(float(s), num)
			return result
		else:
			return s

	@staticmethod
	def check_type(data) -> str:
		"""
		查询数据类型
		:param data:
		:return: 返回字符串 如果未找到返回unknown
		"""
		type_map = {
			int: "int",
			str: "str",
			float: "float",
			list: "list",
			tuple: "tuple",
			dict: "dict",
			set: "set"
		}
		return type_map.get(type(data), "unknown")

	@staticmethod
	def check_password(pwd: str, min=6, max=20) -> bool:
		"""
		检查密码格式是否正确 大小写和数字特殊符号
		:param pwd: 密码字符串
		:param min: 最小长度
		:param max: 最大长度
		:return: 密码格式是否正确
		"""
		match_str = r'^(?=.*[a-z])(?=.*\d)(?=.*[A-Z])[A-Za-z\d#@!~%_^&*!]{'
		r = match_str + str(min) + ',' + str(max) + '}$'
		pattern = re.compile(r)
		return bool(pattern.match(pwd))

	@staticmethod
	def hash_encrypt(text: str, salt: str = None) -> dict:
		"""
		使用SHA-256算法对给定的密码进行哈希处理，并可以选择性地添加盐值。

		:param text: 需要哈希的字符串
		:param salt: 可选的盐值，如果未提供，则自动生成
		:return: 包含哈希后的字符串和盐值的字典
		"""
		if not text:
			return {}

		# 如果没有提供盐值，则生成一个随机的4字符长的字符串作为盐值
		if salt is None:
			salt = ''.join(secrets.choice(string.printable) for _ in range(4))  # 生成4个字符的随机字符串

		# 将盐值和密码组合后进行哈希
		hashed_text = hashlib.sha256(salt.encode('utf-8') + text.encode('utf-8')).hexdigest()
		return {"salt": salt, "hashed_text": hashed_text}

	@staticmethod
	def generate_secret_key(key_file_path: str) -> None:
		"""
		生成一个安全的 Fernet 密钥，并将其保存在 config 目录下的 fernet_key 文件中。
		"""
		# 检查文件是否存在
		if os.path.exists(key_file_path):
			return
		# 生成 Fernet 密钥
		key = Fernet.generate_key()
		# 将密钥保存到 config/fernet_key 文件中
		with open(key_file_path, 'w', encoding='utf-8') as key_file:
			key_file.write(key.decode('utf-8'))

	@staticmethod
	def get_secret_key(filename: str = 'fernet_key',app=None) -> bytes:
		# 使用相对路径查找config目录

		project_root = Utils.get_project_root(app)
		config_dir = os.path.join(project_root, 'config')
		key_file_path = os.path.join(config_dir, filename)
		if not os.path.exists(key_file_path):
			Utils.generate_secret_key(key_file_path)
		with open(key_file_path, 'r', encoding='utf-8') as key_file:
			key_str = key_file.read()
			key = key_str.encode()  # 转换回字节串
		return key

	@staticmethod
	def fernet_encrypt(text: str) -> str:
		"""
		使用 Fernet 加密文本。 同样的数据 每次加密都不一样

		:param text: 需要加密的文本 字符串
		:return: 加密后的文本
		"""
		key = Utils.get_secret_key()
		cipher = Fernet(key)
		cipher_text = cipher.encrypt(text.encode())
		encrypted_text = base64.b64encode(cipher_text).decode()
		return encrypted_text

	@staticmethod
	def fernet_decrypt(ciphertext: str) -> str:
		"""
		使用 Fernet 解密文本。

		:param ciphertext: 加密后的文本
		:return: 解密后的文本
		"""
		key = Utils.get_secret_key()
		the_code = base64.b64decode(ciphertext)
		cipher = Fernet(key)
		decrypted_text = cipher.decrypt(the_code).decode()
		return decrypted_text

	@staticmethod
	def validate_phone(phone_number) -> bool:
		"""
		检查手机格式是否正确。

		:param phone_number: 手机号码
		:return: 是否符合中国大陆手机号格式
		"""
		pattern = r'^1[3-9]\d{9}$'
		return bool(re.match(pattern, phone_number))

	@staticmethod
	def validate_email(email: str) -> bool:
		"""
		检查邮箱格式是否正确。

		:param email: 邮箱地址
		:return: 是否符合邮箱格式
		"""
		pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		return bool(re.match(pattern, email))

	@staticmethod
	def create_token(identity, claims=None, is_refresh=False, expires_delta=None) -> dict:
		"""
		为用户端生成令牌。

		:param identity: 用户身份标识
		:param claims: 其他声明信息
		:param is_refresh: 是否生成刷新令牌
		:param expires_delta: 过期时间，可以是 timedelta 对象或 datetime 对象，如果为 None 则使用默认配置
		:return: 包含访问令牌和可选的刷新令牌的字典
		"""
		if claims is None:
			claims = {"role": "admin"}
		access_token = create_access_token(identity=identity, additional_claims=claims, expires_delta=expires_delta)
		if is_refresh:
			return {"access_token": access_token}
		refresh_token = create_refresh_token(identity=identity, additional_claims=claims, expires_delta=expires_delta)
		return {"access_token": access_token, "refresh_token": refresh_token}

	@staticmethod
	def _get_fields(item) -> list:
		"""
		获取查询结果项的字段名。
		:param item: 查询结果项
		:return: 字段名列表
		"""
		if hasattr(item, '__table__'):
			return item.__table__.columns.keys()
		elif hasattr(item, '_asdict'):
			return item._asdict().keys()
		elif isinstance(item, tuple):
			# 如果是命名元组，则返回其._fields属性；否则，使用索引作为键
			return getattr(item, '_fields', None) or range(len(item))
		else:
			return ['value']

	@staticmethod
	def query_to_dict(item) -> dict:
		"""
		将单个查询结果转换为字典。
		:param item: 查询结果对象
		:return: 字典
		"""
		fields = Utils._get_fields(item)
		if not fields:
			return {}
		return {field: getattr(item, field, item[field] if isinstance(item, (list, tuple)) else item) for field in
				fields}

	@staticmethod
	def sanitize_field_name(field) -> None:
		# 如果字段名以数字开头，则添加前缀'_'
		return '_' + field if field[0].isdigit() else field

	@staticmethod
	def query_to_dict_list(data: any) -> list:
		"""
		将查询结果列表转换为字典列表。
		:param data: 查询结果列表
		:return: 字典列表
		"""
		if not data:
			return []

		# 获取字段名（假设 Utils._get_fields 是提取对象/行中的字段名）
		fields = Utils._get_fields(data[0])

		result = []
		for item in data:
			item_dict = {}
			for field in fields:
				# 处理字段名，如果以数字开头则添加'_'
				sanitized_field = Utils.sanitize_field_name(field)

				# 根据item的类型获取值
				if isinstance(item, (list, tuple)):
					# 如果是列表或元组，则用索引访问
					value = item[fields.index(sanitized_field)] if sanitized_field in fields else None
				else:
					# 如果是对象或其他结构，尝试 getattr
					value = getattr(item, sanitized_field, None)

				if isinstance(value, Decimal):
					value = float(value)

				item_dict[field] = value
			result.append(item_dict)

		return result

	@staticmethod
	def import_controller(package_name) -> None:
		# 获取包内所有模块的名字
		package_path = package_name.replace('.', '/')
		module_names = [name for _, name, _ in pkgutil.iter_modules([str(package_path)])]
		# 遍历所有模块名并尝试导入
		for module_name in module_names:
			full_module_path = f"{package_name}.{module_name}".replace('app.', 'fred_framework.')
			importlib.import_module(full_module_path)

	@staticmethod
	def timestamp_to_utc(timestamp):
		"""
		时间戳转时区时间
		"""
		return datetime.utcfromtimestamp(timestamp) if timestamp else None

	@staticmethod
	def md5_encrypt(text: str) -> str:
		# 创建一个 MD5 对象
		md5 = hashlib.md5()

		# 更新 MD5 对象的内容（需要将字符串编码为字节）
		md5.update(text.encode('utf-8'))

		# 获取加密后的十六进制字符串
		encrypted_text = md5.hexdigest()

		return encrypted_text

	@staticmethod
	def timestamp_format(timestamp: int, formatted: str = '%Y-%m-%d %H:%M:%S') -> str:
		"""
		时间戳转时间
		"""
		# 如果没有给时间戳则返回当前时间
		if not timestamp:
			return datetime.now().strftime(formatted)
		return datetime.fromtimestamp(timestamp).strftime(formatted)

	@staticmethod
	def time_to_timestamp(time_string: str, formatted: str = '%Y-%m-%d %H:%M:%S') -> int:
		"""
		时间字符串转时间戳
		"""
		try:
			return int(datetime.strptime(time_string, formatted).timestamp())
		except Exception as e:
			return 0

	@staticmethod
	def datetime_to_timestamp(dt: datetime) -> int:
		"""
		日期转时间戳
		"""
		try:
			return int(dt.timestamp())
		except Exception as e:
			return 0

	@staticmethod
	def get_n_days_ago(n: int, formatted: str = "%Y-%m-%d %H:%M:%S"):
		"""
		获取N天前的时间
		params formatted :如果为空返回时间戳
		"""
		# 获取当前日期时间
		n_days_ago = datetime.now() - timedelta(days=n)
		if formatted == "":
			# 返回时间戳
			return int(n_days_ago.timestamp())
		else:
			# 格式化时间为 年-月-日 时:分:秒 的形式
			return n_days_ago.strftime(formatted)

	@staticmethod
	def format_time(dt, formatted: str = '%Y-%m-%d %H:%M:%S') -> str:
		"""
		格式化时间对象为字符串
		:param dt: datetime 对象或时间戳
		:param formatted: 格式化字符串
		:return: 格式化后的时间字符串
		"""
		if dt is None:
			return ''
		if isinstance(dt, datetime):
			return dt.strftime(formatted)
		elif isinstance(dt, int):
			return Utils.timestamp_format(dt, formatted)
		else:
			return str(dt)

	@staticmethod
	def format_frame_stamp(frame_stamp: str = None, formatted: str = '%Y-%m-%d %H:%M:%S') -> str:
		"""
		格式化帧时间戳为指定格式
		支持多种时间格式：ISO 格式、标准格式等
		:param frame_stamp: 帧时间戳字符串（ISO 格式或标准格式），如：
			- ISO 格式: 2025-01-01T12:00:00 或 2025-01-01T12:00:00.000
			- 标准格式: 2025-01-01 12:00:00 或 2025-01-01 12:00:00.000
		:param formatted: 目标格式化字符串，默认为 '%Y-%m-%d %H:%M:%S'
		:return: 格式化后的时间字符串，如果无法解析则返回原始值
		"""
		if not frame_stamp:
			return None

		try:
			# 处理多种时间格式
			normalized_stamp = frame_stamp.strip()
			date = None

			# 如果是 ISO 格式（包含 T）
			if "T" in normalized_stamp:
				try:
					# 尝试解析 ISO 格式
					if "." in normalized_stamp:
						date = datetime.strptime(normalized_stamp, "%Y-%m-%dT%H:%M:%S.%f")
					else:
						date = datetime.strptime(normalized_stamp, "%Y-%m-%dT%H:%M:%S")
				except ValueError:
					pass
			# 如果是标准格式（包含空格）
			elif " " in normalized_stamp:
				try:
					# 尝试解析标准格式
					if "." in normalized_stamp:
						date = datetime.strptime(normalized_stamp, "%Y-%m-%d %H:%M:%S.%f")
					else:
						date = datetime.strptime(normalized_stamp, "%Y-%m-%d %H:%M:%S")
				except ValueError:
					pass

			# 如果成功解析，格式化为指定格式
			if date:
				return date.strftime(formatted)

			# 如果无法解析，返回原始值
			return frame_stamp
		except Exception:
			# 如果解析失败，返回原始值
			return frame_stamp

	@staticmethod
	def sort_json_recursively(data):
		"""
		递归对 JSON 对象按照 key 进行排序
		:param data: 需要排序的数据（dict、list 或其他类型）
		:return: 排序后的数据
		"""
		if isinstance(data, dict):
			# 对字典的 key 进行排序，然后递归处理每个值
			return {key: Utils.sort_json_recursively(value) for key, value in sorted(data.items())}
		elif isinstance(data, list):
			# 对列表中的每个元素递归处理
			return [Utils.sort_json_recursively(item) for item in data]
		else:
			# 对于其他类型（字符串、数字、布尔值等），直接返回
			return data

	@staticmethod
	def upload_file(upload_folder: str, file_type: list = None, filesize: int = 10) -> dict:
		"""
		上传文件
		:param upload_folder: 上传文件夹名称（相对于UPLOAD_FOLDER配置的路径）
		:param file_type: 允许的文件类型列表，默认：['jpeg', 'jpg', 'png', 'gif']
		:param filesize: 文件大小限制（MB），默认：10MB
		:return: 包含file_name和msg的字典
		"""
		data = {
			"file_name": "",
			"msg": ""
		}

		# 检查请求方法
		if request.method != "POST":
			data["msg"] = "上传失败：仅支持POST请求"
			return data

		# 获取上传路径配置（独立路径，不使用RESOURCE_PATH）
		path_config = current_app.config.get('PATH_CONFIG', {})
		upload_base_folder = path_config.get('UPLOAD_FOLDER', 'upload')

		# 处理上传文件夹路径
		if not upload_folder:
			upload_folder = "default"

		# 构建完整的上传路径
		upload_path = os.path.join(upload_base_folder, upload_folder).replace('\\', '/')

		# 设置默认文件类型
		if file_type is None:
			file_type = ['jpeg', 'jpg', 'png', 'gif']

		# 检查文件大小
		if request.content_length and request.content_length > filesize * 1024 * 1024:
			data["msg"] = f"上传文件不能超过{filesize}M"
			return data

		# 检查文件是否存在
		if 'file' not in request.files:
			data["msg"] = "未找到上传文件"
			return data

		f = request.files['file']
		if not f or f.filename == '':
			data["msg"] = "文件名为空"
			return data

		# 检查文件扩展名
		file_suffix = f.filename.rsplit('.', 1)[-1] if '.' in f.filename else ''
		if not file_suffix or file_suffix.lower() not in file_type:
			data["msg"] = f"文件格式错误！仅支持：{', '.join(file_type)}"
			return data

		# 确保上传目录存在（支持多级目录）
		os.makedirs(upload_path, exist_ok=True)

		# 生成唯一文件名
		filename = f"{int(time())}_{randint(1000, 9000)}.{file_suffix}"

		# 保存文件
		try:
			file_path = os.path.join(upload_path, filename)
			f.save(file_path)

			# 构建返回的文件路径（相对路径）
			data["file_name"] = f"{upload_path}/{filename}".replace('\\', '/')

			# 如果保存文件目录以../开头，保存到数据库的路径改成/开头
			if data["file_name"].startswith("../"):
				data["file_name"] = "/" + data["file_name"][3:]

			return data
		except Exception as e:
			data["msg"] = f"文件保存失败：{str(e)}"
			return data

	@staticmethod
	def get_api_urls_from_files(controller_dir: str = None) -> list:
		"""
		从文件扫描方式获取接口URL列表，支持扫描所有模块的controller目录
		:param controller_dir: 控制器目录路径，如果为None则自动扫描所有模块
		:return: 接口URL列表，每个元素包含url、method、summary等字段
		"""
		api_urls = []

		# 获取项目根目录
		project_root = str(Utils.get_project_root())

		# 如果指定了controller_dir，只扫描该目录
		if controller_dir is not None:
			if not os.path.exists(controller_dir):
				return api_urls
			module_dirs = [(controller_dir, 'admin')]  # 默认使用admin作为蓝图名
		else:
			# 自动扫描所有模块目录
			module_dirs = Utils._get_module_directories(project_root)

		# 遍历所有模块的controller目录
		for controller_dir_path, blueprint_name in module_dirs:
			if not os.path.exists(controller_dir_path):
				continue

			# 遍历所有控制器文件
			for filename in os.listdir(controller_dir_path):
				if filename.endswith('.py') and not filename.startswith('__'):
					file_path = os.path.join(controller_dir_path, filename)
					try:
						with open(file_path, 'r', encoding='utf-8') as f:
							content = f.read()

						# 匹配蓝图装饰器：@blueprint_name.route("path")
						# 优化正则表达式，允许装饰器和类定义之间有多个空行或空白字符
						# 使用 \s+ 匹配一个或多个空白字符（包括空格、制表符、换行符等）
						route_class_pattern = rf'@{re.escape(blueprint_name)}\.route\(["\']([^"\']+)["\']\)\s+class\s+(\w+)'
						route_class_matches = re.findall(route_class_pattern, content, re.MULTILINE)
						
						# 调试：检查 SystemLogController 是否被扫描到
						if 'SystemLogController' in filename:
							# 临时调试输出（生产环境可以移除）
							pass

						for route_path, class_name in route_class_matches:
							# 规范化路径：确保以/开头
							normalized_route_path = route_path.strip()
							if not normalized_route_path.startswith('/'):
								normalized_route_path = '/' + normalized_route_path

							# 获取模块的url_prefix（从__init__.py中读取）
							module_name = os.path.basename(os.path.dirname(controller_dir_path))
							url_prefix = Utils._get_module_url_prefix(project_root, module_name)

							# 组合完整路径：url_prefix + route_path
							full_path = url_prefix + normalized_route_path

							# 找到这个类的完整定义
							# 使用更精确的类匹配模式，确保能匹配到类的完整内容
							class_pattern = rf'class\s+{re.escape(class_name)}\s*\([^)]*\)\s*:(.*?)(?=class\s+\w+|@\w+\.route|\Z)'
							class_match = re.search(class_pattern, content, re.MULTILINE | re.DOTALL)

							if class_match:
								class_content = class_match.group(1)
								# 在类内容中查找所有方法
								# 优化方法匹配，允许方法参数中有空格
								method_pattern = r'def\s+(\w+)\s*\([^)]*self'
								methods = re.findall(method_pattern, class_content)

								# 为每个方法创建接口
								for method in methods:
									# 检查方法名是否为HTTP方法（不区分大小写）
									method_upper = method.upper()
									if method_upper in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
										# 尝试从代码注释中提取接口描述
										summary = Utils.extract_api_summary_from_code(class_content, method)

										api_urls.append({
											'url': full_path,
											'method': method_upper,
											'summary': summary,
											'description': summary,
											'operation_id': f"{class_name}_{method}",
											'tags': [class_name],
											'label': f"{method_upper} {full_path} - {summary}"
										})

					except Exception as e:
						# 静默跳过有问题的文件，避免影响整体扫描
						# 如果某个文件解析失败，只记录但不中断整个扫描过程
						continue

		# 去重（同一路径和方法的接口）
		unique_api_urls = []
		seen = set()
		for api in api_urls:
			key = (api['url'], api['method'])
			if key not in seen:
				seen.add(key)
				unique_api_urls.append(api)

		# 按URL和方法排序
		unique_api_urls.sort(key=lambda x: (x['url'], x['method']))

		return unique_api_urls

	@staticmethod
	def _get_module_directories(project_root: str) -> list:
		"""
		获取所有模块的controller目录路径和蓝图名称
		:param project_root: 项目根目录
		:return: [(controller_dir_path, blueprint_name), ...]
		"""
		module_dirs = []
		# 需要扫描的模块目录列表
		modules_to_scan = ['admin', 'terminal', 'algorithm', 'demo', 'server']

		for module_name in modules_to_scan:
			module_path = os.path.join(project_root, module_name)
			controller_path = os.path.join(module_path, 'controller')

			# 检查目录是否存在
			if os.path.exists(controller_path) and os.path.isdir(controller_path):
				# 从__init__.py中获取蓝图变量名
				init_file = os.path.join(module_path, '__init__.py')
				blueprint_name = Utils._get_blueprint_name_from_init(init_file, module_name)
				module_dirs.append((controller_path, blueprint_name))

		return module_dirs

	@staticmethod
	def _get_blueprint_name_from_init(init_file_path: str, default_name: str) -> str:
		"""
		从模块的__init__.py文件中获取蓝图变量名
		:param init_file_path: __init__.py文件路径
		:param default_name: 默认蓝图名称
		:return: 蓝图变量名
		"""
		if not os.path.exists(init_file_path):
			return default_name

		try:
			with open(init_file_path, 'r', encoding='utf-8') as f:
				content = f.read()

			# 匹配 Blueprint('name', ...) 或 variable = Blueprint(...)
			# 优先匹配 variable = Blueprint(...) 格式
			blueprint_pattern = r'(\w+)\s*=\s*Blueprint\(["\'](\w+)["\']'
			match = re.search(blueprint_pattern, content)
			if match:
				return match.group(1)  # 返回变量名

			# 如果没有找到，返回默认名称
			return default_name
		except Exception:
			return default_name

	@staticmethod
	def _get_module_url_prefix(project_root: str, module_name: str) -> str:
		"""
		从模块的__init__.py文件中获取url_prefix
		:param project_root: 项目根目录
		:param module_name: 模块名称
		:return: url_prefix
		"""
		init_file = os.path.join(project_root, module_name, '__init__.py')
		if not os.path.exists(init_file):
			return f'/{module_name}'

		try:
			with open(init_file, 'r', encoding='utf-8') as f:
				content = f.read()

			# 匹配 url_prefix="/xxx"
			url_prefix_pattern = r'url_prefix\s*=\s*["\']([^"\']+)["\']'
			match = re.search(url_prefix_pattern, content)
			if match:
				prefix = match.group(1)
				# 确保以/开头
				if not prefix.startswith('/'):
					prefix = '/' + prefix
				return prefix

			# 如果没有找到，返回默认前缀
			return f'/{module_name}'
		except Exception:
			return f'/{module_name}'

	@staticmethod
	def extract_api_summary_from_code(class_content: str, method: str) -> str:
		"""
		从代码注释中提取接口描述，支持多种注释格式
		:param class_content: 类的内容字符串
		:param method: 方法名
		:return: 接口描述
		"""
		# 查找方法的定义和注释
		method_pattern = rf'def\s+{method}\s*\([^)]*\):.*?(?=def|\Z)'
		method_match = re.search(method_pattern, class_content, re.MULTILINE | re.DOTALL)

		if not method_match:
			return f"{method.title()}方法"

		method_code = method_match.group(0)

		# 尝试提取多种格式的注释
		patterns = [
			# Flask-Smorest 格式: """接口描述"""
			r'"""(.*?)"""',
			# 普通注释格式: # 接口描述
			r'#\s*(.+?)(?:\n|$)',
			# 多行注释格式: """\n接口描述\n"""
			r'"""\s*\n\s*(.+?)\s*\n\s*"""',
			# 单行注释: # 接口描述
			r'#\s*([^\n]+)',
		]

		for pattern in patterns:
			matches = re.findall(pattern, method_code, re.MULTILINE | re.DOTALL)
			for match in matches:
				# 清理注释内容
				summary = match.strip()
				# 移除多余的空白字符
				summary = re.sub(r'\s+', ' ', summary)
				# 如果找到有效的描述，返回
				if summary and len(summary) > 2:
					return summary

		# 如果没有找到注释，直接显示方法名
		return method.title()

	@staticmethod
	def get_api_summary_by_url_and_method(api_url: str, method: str, api_list: list = None) -> str:
		"""
		根据接口URL和方法获取接口说明
		:param api_url: 接口URL（可能包含模块前缀，如/admin、/terminal等）
		:param method: 请求方法
		:param api_list: 接口列表，如果为None则自动获取
		:return: 接口说明
		"""
		if not api_url or not method:
			return ''

		if api_list is None:
			api_list = Utils.get_api_urls_from_files()

		# 规范化API URL：保留完整路径（包含模块前缀）
		normalized_url = api_url.strip()
		# 确保以/开头
		if not normalized_url.startswith('/'):
			normalized_url = '/' + normalized_url
		# 移除末尾的斜杠（如果有）用于比较
		normalized_url_compare = normalized_url.rstrip('/')

		# 规范化method（转换为大写）
		normalized_method = method.strip().upper() if method else ''

		# 查找匹配的接口
		for api in api_list:
			api_url_in_list = api.get('url', '').strip()
			api_method = str(api.get('method', '')).strip().upper()

			# 匹配方法（必须完全匹配）
			if api_method != normalized_method:
				continue

			# 规范化列表中的URL用于比较
			if not api_url_in_list.startswith('/'):
				api_url_in_list = '/' + api_url_in_list
			api_url_normalized = api_url_in_list.rstrip('/')

			# 精确匹配路径（忽略末尾斜杠）
			if api_url_normalized == normalized_url_compare:
				summary = api.get('summary', '')
				return summary if summary else ''

		return ''
