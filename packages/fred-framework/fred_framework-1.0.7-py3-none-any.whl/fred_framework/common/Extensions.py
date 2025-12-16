"""
 * @Author：cyg
 * @Package：Extensions
 * @Project：Default (Template) Project
 * @name：Extensions
 * @Date：2024/12/16 11:35
 * @Filename：使用的组件
"""

from flask import request

from fred_framework.common.Sqlacodegen import Sqlacodegen
from fred_framework.common.Utils import Utils
from flask_babelplus import Babel, Domain
import os

class Extensions:
	def __init__(self, app=None):
		self.app = app

	# 加载依赖并初始化扩展

	def load_requirements(self):
		"""
		加载依赖包列表

		默认加载所有支持的依赖包，用于扩展检测。
		"""
		self.app.logger.info('开始加载依赖包列表')
		# 直接返回默认的依赖列表，不检查 requirements.txt 文件
		default_requirements = [
			'flask',
			'flask_cors',
			'flask_jwt_extended',
			'flask_smorest',
			'flask_swagger_ui',
			'flask_apscheduler',
			'flask_babelplus',
			'flask_sqlalchemy',
			'flask_mail',
			'redis',
			'pymysql',
			'cryptography',
			'pillow',
			'requests',
			'pytz'
		]
		self.app.logger.info(f'成功加载 {len(default_requirements)} 个依赖包')
		return default_requirements

	def _extract_package_name(self, requirement: str) -> str:
		"""
		从依赖字符串中提取包名

		支持格式：
		- flask>=3.1.2
		- flask==3.1.2
		- flask~=3.1.2
		- flask
		- flask-cors>=6.0.1
		- flask[extra]>=3.1.2

		Args:
			requirement: 依赖字符串

		Returns:
			str: 提取的包名，如果无法提取则返回空字符串
		"""
		import re

		# 移除方括号中的额外依赖，如 flask[extra] -> flask
		package = re.sub(r'\[.*?\]', '', requirement)

		# 使用正则表达式匹配版本操作符
		# 支持 >=, ==, ~=, >, <, <=, != 等操作符
		version_pattern = r'[><=!~]+'
		parts = re.split(version_pattern, package)

		# 取第一部分作为包名
		package_name = parts[0].strip()

		return package_name if package_name else ''

	def initialize_extensions(self):
		"""
		初始化已加载的扩展。

		根据 requirements.txt 中的依赖包自动初始化对应的扩展。
		使用字典映射方式，提高代码可维护性和可读性。
		"""
		requirements = self.load_requirements()

		# 扩展初始化映射表：包名 -> 初始化方法
		extension_map = {
			'flask_mail': self.__initialize_mail,
			'flask_babelplus': self.__initialize_babel,
			'flask_apscheduler': self.__initialize_scheduler,
			'flask_jwt_extended': self.__initialize_jwt,
			'flask_sqlalchemy': self.__initialize_db,
			'redis': self.__initialize_redis,
		}

		# 遍历映射表，检查依赖并初始化扩展
		for package_name, init_func in extension_map.items():
			if package_name in requirements:
				init_func()

	def __initialize_models(self):
		self.app.logger.info("------开始生成模型文件------")
		Sqlacodegen().create_models(self.app)

	def __initialize_scheduler(self):
		"""初始化定时任务扩展"""
		from flask_apscheduler import APScheduler
		from fred_framework.common.SchedulerLog import SchedulerLog

		scheduled = APScheduler()
		if self.app.config.get('JOBS'):
			self.app.logger.info("------初始化定时任务扩展------")

			# 包装所有定时任务函数，添加日志记录功能
			# 注意：必须在 scheduled.init_app() 之前完成包装，否则 APScheduler 会使用原始函数引用
			original_jobs = self.app.config.get('JOBS', [])

			# 在应用上下文中执行包装，确保能正确访问 current_app
			with self.app.app_context():
				wrapped_jobs = SchedulerLog.wrap_jobs_in_config(original_jobs)

			# 更新配置中的任务列表
			self.app.config['JOBS'] = wrapped_jobs

			# 在包装完成后初始化调度器
			# 这样 APScheduler 会使用包装后的函数
			scheduled.init_app(self.app)
			scheduled.start()

	def __initialize_jwt(self):
		"""初始化 JWT 扩展"""
		from flask_jwt_extended import JWTManager
		jwt = JWTManager()
		self.app.config['JWT_SECRET_KEY'] = Utils.get_secret_key('jwt_secret_key')
		self.app.logger.info("------初始化 JWT 扩展------")
		jwt.init_app(self.app)

	def __initialize_babel(self):
		"""初始化 Babel 国际化扩展"""

		self.app.logger.info("------初始化 Babel 国际化扩展------")

		# 获取配置的翻译目录
		translation_dir = self.app.config.get('BABEL_TRANSLATION_DIRECTORIES', None)

		# 如果配置了翻译目录，创建自定义Domain
		default_domain = None
		if translation_dir:
			# 构建绝对路径
			if os.path.isabs(translation_dir):
				# 已经是绝对路径
				translation_path = translation_dir
			else:
				# 相对于 app.root_path
				translation_path = os.path.join(self.app.root_path, translation_dir)
			default_domain = Domain(dirname=translation_path)

		babel = Babel()
		# 必须配置默认语言
		if self.app.config.get('BABEL_DEFAULT_LOCALE'):
			babel.init_app(self.app, default_domain=default_domain)

			@babel.localeselector
			def get_locale():
				supported_languages = self.app.config.get('SUPPORTED_LANGUAGES')
				default_locale = self.app.config.get('BABEL_DEFAULT_LOCALE')
				# 如果浏览器发送的是 zh，直接映射到 zh
				locale = request.accept_languages.best_match(supported_languages, default_locale)
				return locale or default_locale

	def __initialize_db(self):
		"""初始化数据库扩展"""
		if self.app.config.get('SQLALCHEMY_DATABASE_URI'):
			# 在初始化数据库之前先生成模型文件
			self.__initialize_models()

			from fred_framework.common.Utils import Utils
			import sys
			import importlib
			
			# 加载模型模块
			Utils.import_project_models('db')
			# 直接导入模型
			from model.model import db
			
			self.app.logger.info("------初始化数据库扩展------")
			db.init_app(self.app)
			
			# 确保标准的 model.model 模块也使用已初始化的 db 实例
			# 这样可以避免 "The current Flask app is not registered with this 'SQLAlchemy' instance" 错误
			try:
				# 强制导入标准的 model.model 模块（如果还没有导入）
				if 'model.model' not in sys.modules:
					try:
						# 确保项目根目录在 sys.path 中
						project_root = Utils.get_project_root()
						
						if project_root and str(project_root) not in sys.path:
							sys.path.insert(0, str(project_root))
						
						# 导入标准的 model.model 模块
						standard_model_module = importlib.import_module('model.model')
						# 将已初始化的 db 实例设置到标准模块中
						setattr(standard_model_module, 'db', db)
						self.app.logger.debug("已同步 db 实例到标准的 model.model 模块（新导入）")
					except ImportError as e:
						self.app.logger.warning(f"无法导入标准的 model.model 模块: {str(e)}")
				else:
					# 如果标准模块已存在，将已初始化的 db 实例设置到标准模块中
					standard_model_module = sys.modules['model.model']
					# 将已初始化的 db 实例设置到标准模块中
					setattr(standard_model_module, 'db', db)
					self.app.logger.debug("已同步 db 实例到标准的 model.model 模块（已存在）")
				
				# 额外检查：确保所有可能导入 model.model 的地方都能使用已初始化的 db
				# 遍历 sys.modules，查找所有可能包含 model.model 的模块
				for module_name in list(sys.modules.keys()):
					if 'model' in module_name.lower():
						try:
							module = sys.modules[module_name]
							if hasattr(module, 'db') and isinstance(module.db, type(db)):
								# 如果模块中有 db 属性且类型相同，但不是同一个实例，则替换
								if module.db is not db:
									setattr(module, 'db', db)
									self.app.logger.debug(f"已同步 db 实例到模块: {module_name}")
						except Exception:
							pass
			except Exception as e:
				self.app.logger.warning(f"同步 db 实例到标准模块时出现警告: {str(e)}")

	def __initialize_mail(self):
		"""初始化邮件扩展"""
		if self.app.config.get('MAIL_SERVER'):
			from flask_mail import Mail
			self.app.logger.info("------初始化邮件扩展------")
			mail = Mail()
			mail.init_app(self.app)

	def __initialize_redis(self):
		"""初始化 Redis 扩展"""
		if self.app.config.get('REDIS_URL'):
			try:
				import redis
				from urllib.parse import urlparse

				self.app.logger.info("------初始化 Redis 扩展------")

				# 解析 Redis URL
				redis_url = self.app.config.get('REDIS_URL')
				parsed = urlparse(redis_url)

				# 创建 Redis 客户端
				redis_client = redis.from_url(
					redis_url,
					decode_responses=False  # 保持字节类型，与现有代码兼容
				)

				# 测试连接
				try:
					redis_client.ping()
				except Exception as e:
					self.app.logger.warning(f"Redis 连接测试失败: {str(e)}")
					return

				# 注册到 Flask extensions
				self.app.extensions['redis'] = redis_client
				self.app.logger.info("Redis 扩展初始化成功")
			except ImportError:
				self.app.logger.warning("redis 包未安装，跳过 Redis 扩展初始化。请安装: pip install redis")
			except Exception as e:
				self.app.logger.error(f"初始化 Redis 扩展失败: {str(e)}")
