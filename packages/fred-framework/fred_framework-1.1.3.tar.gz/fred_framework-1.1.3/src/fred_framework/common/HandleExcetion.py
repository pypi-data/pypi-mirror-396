"""
 * @Author：cyg
 * @Package：HandleExcetion
 * @Project：Default (Template) Project
 * @name：HandleExcetion
 * @Date：2024/12/16 11:47
 * @Filename：全局异常处理
"""
from http.client import NOT_FOUND
from flask_babelplus import gettext
from sqlite3 import OperationalError
from sqlalchemy.exc import OperationalError as SAOperationalError

from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException, Unauthorized


class HandleException():
	def __init__(self, app):
		@app.errorhandler(NOT_FOUND)
		def handle_404_error(e):
			exception_message = {'message': gettext("您访问的地址溜走了!")}
			response = jsonify(exception_message)
			response.status_code = e.code
			return response
		
		@app.errorhandler(400)
		def handle_400_error(e):
			# 使用 abort(400,description =gettext("验证码有误!"))使用其自带的状态码和描述
			code = e.code
			message = e.description
			exception_message = {'message': message}
			response = jsonify(exception_message)
			response.status_code = code
			return response
		
		@app.errorhandler(401)
		def handle_401_error(e):
			code = e.code
			exception_message = {'message': gettext("登录失效或登录过期!")}
			response = jsonify(exception_message)
			response.status_code = code
			return response
		
		@app.errorhandler(422)
		def handle_422_error(e):
			code = e.code
			# 尝试提取 Marshmallow 的 ValidationError 错误信息
			errors = getattr(e, 'exc', None)  # 获取原始异常对象
			error_details = []
			
			def extract_error_messages(messages, prefix=''):
				"""
				递归提取错误消息，支持嵌套结构（列表验证、字典验证等）
				"""
				result = []
				if isinstance(messages, dict):
					for key, value in messages.items():
						# 构建字段路径
						if isinstance(key, int):
							# 列表索引，使用更友好的格式
							if prefix:
								field_path = f"{prefix}[第{key + 1}项]"
							else:
								field_path = f"第{key + 1}项"
						elif isinstance(key, str):
							# 字符串键（字段名）
							if prefix:
								field_path = f"{prefix}.{key}"
							else:
								field_path = key
						else:
							# 其他类型的键
							if prefix:
								field_path = f"{prefix}[{key}]"
							else:
								field_path = f"[{key}]"
						
						if isinstance(value, list):
							# 如果是列表，说明是错误消息列表
							for msg in value:
								if isinstance(msg, str):
									result.append(f"{field_path}: {msg}")
								elif isinstance(msg, dict):
									# 嵌套字典，继续递归
									result.extend(extract_error_messages(msg, field_path))
						elif isinstance(value, dict):
							# 嵌套字典，继续递归
							result.extend(extract_error_messages(value, field_path))
						elif isinstance(value, str):
							# 直接是字符串错误消息
							result.append(f"{field_path}: {value}")
				elif isinstance(messages, list):
					# 如果是列表，直接处理
					for msg in messages:
						if isinstance(msg, str):
							if prefix:
								result.append(f"{prefix}: {msg}")
							else:
								result.append(msg)
						elif isinstance(msg, dict):
							result.extend(extract_error_messages(msg, prefix))
				elif isinstance(messages, str):
					# 直接是字符串
					if prefix:
						result.append(f"{prefix}: {messages}")
					else:
						result.append(messages)
				
				return result
			
			if isinstance(errors, ValidationError):
				# 提取 ValidationError 的 messages 属性
				all_messages = extract_error_messages(errors.messages)
				error_details.extend(all_messages)
			
			# 如果没有提取到错误信息，使用默认消息
			if not error_details:
				error_details.append(gettext('参数验证失败'))
			
			text = '; '.join(error_details)
			exception_message = {'message': gettext(f'参数验证错误: {text}')}
			response = jsonify(exception_message)
			response.status_code = code
			return response
		
		@app.errorhandler(OperationalError)
		def handle_operational_error(e):
			# 自定义错误消息和状态码
			error_message = gettext("数据库连接失败，请稍后重试！")
			# if "Lost connection to MySQL server" in str(e):
			# 	error_message = "与数据库的连接已丢失，请稍后重试！"
			# elif "Operation timed out" in str(e):
			# 	error_message = "数据库操作超时，请检查网络或服务器状态！"
			
			exception_message = {'message': error_message}
			response = jsonify(exception_message)
			response.status_code = 500  # 使用 500 表示服务器内部错误
			return response

		@app.errorhandler(SAOperationalError)
		def handle_sqlalchemy_operational_error(e):
			# 默认使用通用错误信息
			error_message = gettext("数据库操作失败，请检查SQL语句或数据库状态！")

			# 尝试从原始异常 e.orig 中提取更具体的信息
			# (pymysql.err.OperationalError) (1170, "BLOB/TEXT column 't2' used in key specification without a key length")
			# e.orig.args -> (1170, "BLOB/TEXT column 't2' used in key specification without a key length")
			if hasattr(e, 'orig') and e.orig and hasattr(e.orig, 'args') and len(e.orig.args) > 1:
				# 提取具体的错误描述，通常是元组的第二个元素
				error_detail = e.orig.args[1]
				error_message = f"{gettext('数据库操作失败')}: {error_detail}"

			exception_message = {'message': error_message}
			response = jsonify(exception_message)
			response.status_code = 500
			return response
		
		@app.errorhandler(500)
		def handle_500_error(e):
			"""
			处理 500 错误，确保错误信息能够正确返回
			"""
			code = 500
			# 尝试获取错误描述，如果没有则使用默认消息
			message = getattr(e, 'description', None) or str(e) or gettext("服务器内部错误")
			exception_message = {'message': message}
			response = jsonify(exception_message)
			response.status_code = code
			return response
		
		@app.errorhandler(HTTPException)
		def handle_http_exception(e):
			"""
			处理其他 HTTP 异常
			"""
			code = e.code if hasattr(e, 'code') else 500
			message = getattr(e, 'description', None) or str(e) or gettext("请求处理失败")
			exception_message = {'message': message}
			response = jsonify(exception_message)
			response.status_code = code
			return response
		
		@app.errorhandler(Exception)
		def handle_general_exception(e):
			"""
			处理所有未捕获的异常
			"""
			# 如果是 HTTPException，应该已经被上面的处理器处理了
			if isinstance(e, HTTPException):
				code = e.code if hasattr(e, 'code') else 500
				message = getattr(e, 'description', None) or str(e) or gettext("请求处理失败")
				exception_message = {'message': message}
				response = jsonify(exception_message)
				response.status_code = code
				return response
			
			# 其他异常，记录错误信息
			error_message = str(e) if str(e) else gettext("服务器内部错误")
			exception_message = {'message': error_message}
			response = jsonify(exception_message)
			response.status_code = 500
			return response