from datetime import timedelta
from pathlib import Path


class Config:
	"""
	 appliction config
	 custom config use CUSTOM_ For prefix
	"""
	# session配置
	# SECRET_KEY = "Gb1oUTNr7kLg5ZlzDXX0hpeTrYycKVsgkaFvbgsuTug="
	# SESSION_TYPE = 'redis'  # 指定Session存储类型为Redis
	# SESSION_PERMANENT = False  # Session是否永久有效
	# SESSION_USE_SIGNER = True  # 是否对发送到浏览器的Session cookie进行加密签名
	# SESSION_REDIS = redis.StrictRedis(host='localhost', port=6379, db=0, password='如果有')
	# Redis连接配置
	REDIS_URL = ""
	#返回数据是否加密
	ENCRYPT_DATA = False
	#是否启用swagger文档
	ENABLE_SWAGGER = True
	#默认密码
	DEFAULT_PASSWORD = 'Fred@2025'
	
	# 配置邮件发送
	MAIL_SERVER = ''  # 你的邮件服务器地址
	MAIL_PORT = 25  # 你的邮件服务器端口
	MAIL_USE_TLS = True  # 是否使用 TLS
	MAIL_USERNAME = ''  # 你的邮箱用户名
	MAIL_PASSWORD = ''  # 你的邮箱密码
	MAIL_DEFAULT_SENDER = ''  # 默认发件人
	
	# JWT 配置
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=2)  # 有效时长
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
	
	# 数据库信息 配置
	SQLALCHEMY_DATABASE_URI = ''
	SQLALCHEMY_BINDS = {}
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	# 国际化默认配置
	BABEL_DEFAULT_LOCALE = 'zh'
	BABEL_DEFAULT_TIMEZONE = 'UTC'
	# 使用绝对路径指向项目根目录下的translations目录
	import os
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
	BABEL_TRANSLATION_DIRECTORIES = os.path.join(BASE_DIR, 'translations')
	SUPPORTED_LANGUAGES = ['en', 'zh']
	
	# Swagger UI 使用flask_smorest
	API_TITLE = 'FredFrameApi'
	API_VERSION = 'v1'
	OPENAPI_VERSION = '3.0.2'
	OPENAPI_URL_PREFIX = '/'
	OPENAPI_SWAGGER_UI_PATH = '/docs' #swagger 访问地址

	
	# Swagger  参数配置
	SPEC_KWARGS = {
		'components': {
			'securitySchemes': {
				'bearerAuth': {
					'type': 'http',
					'scheme': 'bearer',
					'bearerFormat': 'JWT'
				}
			}
		},
		'security': [{'bearerAuth': []}]  # 配置了默认方案 header中才会有Authorization
	}
	
	# aliyun Sms
	ALIBABA_SIGN_NAME = ''
	ALIBABA_KEY_ID = ''
	ALIBABA_KEY_SECRET = ''
	ALIBABA_TEMPLATE_CODE = ''
	
	# 日志配置
	LOG_LEVEL = 'DEBUG'
	LOG_FILE = 'logs/app.log'
	LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	
	#  定时任务 scheduler 配置
	SCHEDULER_API_ENABLED = True
	SCHEDULER_TIMEZONE = 'Asia/Shanghai'
	JOBS = []
	# 是否启用swagger 默认启用
	# ENABLE_SWAGGER = False
	#  加载自定义模块 如果没有指定 将自动加载所有模块
	# LOAD_CUSTOM_MODULES = ['fic_data']
	
	# 首页加载模块 如果不配置 默认根目录下第一个模块
	# HOME_MODULES = ""
	
	# PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)  # 项目根目录（配置文件在 项目根目录/config/Config.py）

	PATH_CONFIG = {
		'UPLOAD_FOLDER': 'upload'  # 上传文件基础路径配置
	}