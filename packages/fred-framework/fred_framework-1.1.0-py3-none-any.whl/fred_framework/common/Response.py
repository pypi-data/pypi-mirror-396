"""
 * @Author：cyg
 * @Package：response
 * @Project：Default (Template) Project
 * @name：response
 * @Date：2024/9/26 16:36
 * @Filename：response
"""
import http
import json
import time

from flask import request, jsonify, current_app, g
from marshmallow import Schema, fields

from fred_framework.common.Utils import Utils
from fred_framework.common.SystemLog import SystemLog


class Response(Schema):
	code = fields.Int(load_default=200, metadata={'description': '状态码'})
	data = fields.Raw(load_default=None, metadata={'description': '返回数据'})
	message = fields.Str(load_default='', metadata={'description': '说明消息'})
	execution_time = fields.Float(load_default=0.0, metadata={'description': '执行时间'})
	
	def format_response(self, json_data, code):
		"""
		格式化输出
		"""
		return_data = Response().dump(json_data)
		return_data['code'] = code
		if code == http.HTTPStatus.OK:
			encrypt = current_app.config.get('ENCRYPT_DATA', False)
			the_data = json_data
			# 检查 json_data 是否为字典类型
			if isinstance(json_data, dict):
				if 'message' in json_data:
					return_data['message'] = json_data['message']
					# 如果只有 message，则 data 设置为空字符串
					if len(json_data) == 1:
						the_data = ""
					else:
						if encrypt:
							the_data = Utils.fernet_encrypt(json.dumps(the_data))
				else:
					if encrypt:
						the_data = Utils.fernet_encrypt(json.dumps(json_data))
			else:
				# 如果 json_data 不是字典（如整数、字符串等），直接作为 data
				if encrypt:
					the_data = Utils.fernet_encrypt(json.dumps(json_data))
			return_data['data'] = the_data
			return return_data
		return return_data
	
	def custom_response(self, app):
		"""
		自定义输出返回格式
		"""
		
		@app.before_request  # 新增before_request钩子
		def record_start_time():
			g.start_time = time.time()
			# 保存请求数据用于日志记录
			g.request_body = None
			try:
				if request.is_json:
					g.request_body = request.get_json()
				elif request.form:
					g.request_body = dict(request.form)
				elif request.args:
					g.request_body = dict(request.args)
			except:
				pass
		
		@app.after_request
		def after_request(response):
			# 检查是否是swagger请求
			
			swagger_ui_path = app.config.get('OPENAPI_URL_PREFIX', '') + app.config.get('OPENAPI_SWAGGER_UI_PATH', '')
			if request.path.startswith(swagger_ui_path) or request.path.startswith('/openapi'):
				return response
			# 检查响应是否为JSON类型
			if response.mimetype == 'application/json':
				# 尝试将响应转换为字典
				json_response = response.get_json()
				# 格式化响应
				code = response.status_code
				# 如果 json_response 为 None，设置为空字典
				if json_response is None:
					json_response = {}
				# 如果响应中没有 message 字段且状态码不是 200，添加默认 message
				if code != http.HTTPStatus.OK and 'message' not in json_response:
					json_response['message'] = ''
				serialized_response = self.format_response(json_response, code)
				execution_time = time.time() - g.get('start_time', time.time())
				if app.debug:
					serialized_response['execution_time'] = round(execution_time, 5)
				else:
					#先判断execution_time是否存在在移除
					if 'execution_time' in serialized_response:
						del (serialized_response['execution_time'])
				response = jsonify(serialized_response)
				response.status_code = code
				if app.debug:
					response.headers.add('Access-Control-Allow-Origin', '*')
				
				# 记录系统日志（所有接口）
				try:
					from flask import session
					from fred_framework.common.Utils import Utils
					# 加载模型模块
					Utils.import_project_models('Admin')
					# 直接导入模型
					from model.model import Admin
					
					user_id = 0
					username = ''
					
					# 根据不同的模块获取用户信息
					if request.path.startswith('/admin'):
						# admin 模块：从 session['admin_user_info'] 获取
						admin_info = session.get('admin_user_info', None)
						if admin_info:
							if isinstance(admin_info, dict):
								user_id = admin_info.get('id', 0)
								username = admin_info.get('username', '')
							else:
								user_id = getattr(admin_info, 'id', 0)
								username = getattr(admin_info, 'username', '')
					else:
						# 其他模块：从 session 中获取用户ID，然后查询用户名
						# 尝试从不同模块的 session key 获取用户ID
						user_info = None
						if request.path.startswith('/server'):
							user_info = session.get('server_user_info', None)
						elif request.path.startswith('/terminal'):
							user_info = session.get('terminal_user_info', None)
						elif request.path.startswith('/algorithm'):
							user_info = session.get('algorithm_user_info', None)
						elif request.path.startswith('/demo'):
							user_info = session.get('demo_user_info', None)
						else:
							# 尝试从其他可能的 session key 获取
							for key in session.keys():
								if key.endswith('_user_info'):
									user_info = session.get(key, None)
									break
						
						# 转换为整数
						if user_info is not None:
							try:
								user_id = int(user_info)
							except (ValueError, TypeError):
								user_id = 0
						
						# 如果有用户ID，查询用户名
						if user_id > 0:
							try:
								admin = Admin.query.filter_by(id=user_id).first()
								if admin:
									username = admin.username or ''
							except:
								username = ''
					
					# 获取请求数据
					request_body = g.get('request_body')
					# 获取返回数据
					response_body = serialized_response
					# 调用日志记录方法
					SystemLog.save_sys_log(
						user_id=user_id,
						api=request.path,
						method=request.method,
						code=code,
						username=username,
						request_body=request_body,
						response_body=response_body
					)
				except Exception as e:
					# 记录日志失败不影响主流程
					pass
			return response
	
	def swagger_responses(self, spec, schemas):
		"""
		定义swagger默认显示的格式
		"""
		for path in spec['paths'].values():
			for method in path.values():
				if type(method) is not dict:
					continue
				responses = method.setdefault('responses', {})
				for key, value in responses.items():
					if key == '200':
						continue
					try:
						code = int(key)
					except ValueError:
						# 处理无法转换的情况，例如赋值一个默认值或者记录日志
						code = 200
					responses[key] = {
						'content': {
							'application/json': {
								'schema': schemas.get('Response'),
								'example': Response().dump({'code': code})
							}
						}
					}
		
		return None
