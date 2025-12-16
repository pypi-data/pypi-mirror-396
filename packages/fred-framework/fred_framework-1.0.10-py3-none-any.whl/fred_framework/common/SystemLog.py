# coding: utf-8
"""
 * @Author：cyg
 * @Package：SystemLog
 * @Project：Default (Template) Project
 * @name：SystemLog
 * @Date：2025/1/26
 * @Filename：SystemLog
"""
import json
from datetime import datetime


class SystemLog:
	@staticmethod
	def save_sys_log(user_id, api, method, code, username=None, request_body=None, response_body=None):
		"""
		保存系统日志到数据库
		:param user_id: 用户ID
		:param api: 接口地址
		:param method: 请求方式
		:param code: 状态码
		:param username: 用户名
		:param request_body: 请求载体
		:param response_body: 返回载体
		:return: None
		"""
		try:
			from fred_framework.common.Utils import Utils
			# 加载模型模块
			Utils.import_project_models('db', 'SysLog', 'SysLogBody')
			# 直接导入模型
			from model.model import db, SysLog, SysLogBody
			
			# 创建日志记录
			sys_log = SysLog(
				user_id=user_id or 0,
				api=api,
				method=method,
				code=code,
				username=username or '',
				created=datetime.now()
			)
			db.session.add(sys_log)
			db.session.flush()  # 获取 sys_log.id
			
			# 如果有请求或返回载体，保存到 sys_log_body 表
			if request_body is not None or response_body is not None:
				# 将请求和返回载体转换为 JSON 字符串
				request_str = None
				response_str = None
				
				if request_body is not None:
					if isinstance(request_body, (dict, list)):
						request_str = json.dumps(request_body, ensure_ascii=False)
					else:
						request_str = str(request_body)
				
				if response_body is not None:
					if isinstance(response_body, (dict, list)):
						response_str = json.dumps(response_body, ensure_ascii=False)
					else:
						response_str = str(response_body)
				
				sys_log_body = SysLogBody(
					sys_log_id=sys_log.id,
					request=request_str,
					response=response_str
				)
				db.session.add(sys_log_body)
			
			db.session.commit()
		except Exception as e:
			# 记录日志失败不影响主流程
			# 回滚事务
			try:
				db.session.rollback()
			except:
				pass

