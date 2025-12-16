# coding: utf-8
"""
定时任务日志记录工具
用于记录定时任务的执行时间到 sys_log 表
"""
import json
import importlib
import functools
from datetime import datetime
from typing import Callable, Any


class SchedulerLog:
	"""
	定时任务日志记录类
	"""

	@staticmethod
	def log_job_execution(job_id: str, job_name: str, start_time: datetime, end_time: datetime,
	                     success: bool, result: Any = None, error: str = None):
		"""
		记录定时任务执行日志到 sys_log 表

		:param job_id: 任务ID
		:param job_name: 任务名称
		:param start_time: 开始时间
		:param end_time: 结束时间
		:param success: 是否成功
		:param result: 执行结果
		:param error: 错误信息
		:return: None
		"""
		try:
			from fred_framework.common.Utils import Utils
			from flask import current_app
			# 加载模型模块
			Utils.import_project_models('db', 'SysLog', 'SysLogBody')
			# 直接导入模型
			from model.model import db, SysLog, SysLogBody

			# 计算执行时长（秒）
			duration = (end_time - start_time).total_seconds()

			# 构建 API 路径（使用任务ID作为标识）
			api = f"/scheduler/job/{job_id}"

			# 构建请求体（包含任务信息）
			request_body = {
				"job_id": job_id,
				"job_name": job_name,
				"start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
				"duration_seconds": round(duration, 2)
			}

			# 构建响应体（包含执行结果）
			response_body = {
				"success": success,
				"end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
				"duration_seconds": round(duration, 2)
			}

			if error:
				response_body["error"] = error
			elif result:
				# 如果结果太大，只记录摘要
				if isinstance(result, dict):
					# 只保留关键字段，避免数据过大
					summary = {}
					for key in ["success", "message", "target_date", "processed_count",
					           "inserted_count", "updated_count", "logged_count"]:
						if key in result:
							summary[key] = result[key]
					response_body["result"] = summary
				else:
					response_body["result"] = str(result)[:500]  # 限制长度

			# 创建日志记录
			sys_log = SysLog(
				user_id=0,  # 定时任务没有用户ID
				api=api,
				method="SCHEDULER",
				code=200 if success else 500,
				username=f"定时任务-{job_name}",
				created=end_time
			)
			db.session.add(sys_log)
			db.session.flush()  # 获取 sys_log.id

			# 保存请求和返回载体
			request_str = json.dumps(request_body, ensure_ascii=False)
			response_str = json.dumps(response_body, ensure_ascii=False)

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

	@staticmethod
	def wrap_job_function(original_func: Callable, job_id: str, job_name: str, app=None) -> Callable:
		"""
		包装定时任务函数，添加日志记录功能

		:param original_func: 原始任务函数
		:param job_id: 任务ID
		:param job_name: 任务名称
		:param app: Flask 应用实例（可选，如果不提供则尝试自动获取）
		:return: 包装后的函数
		"""
		@functools.wraps(original_func)
		def wrapped_func(*args, **kwargs):
			# 获取 Flask 应用实例
			# 优先使用传入的 app，否则尝试自动获取
			if app is None:
				from flask import current_app
				try:
					# 尝试获取当前应用上下文中的应用实例
					flask_app = current_app._get_current_object()
				except RuntimeError:
					# 如果没有应用上下文，尝试从 run 模块导入
					try:
						from run import app as flask_app
					except ImportError:
						# 如果 run 模块不存在，尝试从 flask_apscheduler 获取
						from flask_apscheduler import APScheduler
						scheduler = APScheduler()
						if hasattr(scheduler, 'app') and scheduler.app:
							flask_app = scheduler.app
						else:
							raise RuntimeError("无法获取 Flask 应用实例，请确保应用已正确初始化")
			else:
				flask_app = app

			start_time = datetime.now()
			success = False
			result = None
			error = None

			# 在应用上下文中执行任务函数和日志记录
			with flask_app.app_context():
				# 确保 db 实例已正确注册到 Flask 应用
				# 这可以解决虚拟环境和项目代码不在一个目录下时的问题
				try:
					from fred_framework.common.Utils import Utils
					# 确保模型已导入
					Utils.import_project_models('db', app=flask_app)
					from model.model import db

					# 检查 db 是否已经注册到 Flask app
					if hasattr(db, 'get_app'):
						registered_app = db.get_app()
						if registered_app is None or registered_app is not flask_app:
							# 如果 db 没有注册或注册到了其他 app，重新初始化
							db.init_app(flask_app)
					else:
						# 如果 db 没有 get_app 方法，直接初始化
						db.init_app(flask_app)

					# 确保 db 实例被注册到 app.extensions
					if 'sqlalchemy' not in flask_app.extensions:
						flask_app.extensions['sqlalchemy'] = db
					elif flask_app.extensions['sqlalchemy'] is not db:
						flask_app.extensions['sqlalchemy'] = db
				except Exception as db_init_error:
					# db 初始化失败不影响任务执行
					pass

				try:
					# 执行原始任务函数（在应用上下文中执行，确保 SQLAlchemy 可以访问 Flask app）
					result = original_func(*args, **kwargs)
					success = True

					# 如果返回结果是字典且包含 success 字段，使用该字段判断
					if isinstance(result, dict) and "success" in result:
						success = result.get("success", False)
						if not success:
							error = result.get("message", "任务执行失败")

				except Exception as e:
					error = str(e)
					success = False
					# 重新抛出异常，保持原有行为
					raise
				finally:
					# 无论成功或失败，都记录日志
					end_time = datetime.now()

					# 在应用上下文中记录日志到数据库
					try:
						SchedulerLog.log_job_execution(
							job_id=job_id,
							job_name=job_name,
							start_time=start_time,
							end_time=end_time,
							success=success,
							result=result,
							error=error
						)
					except Exception as log_error:
						# 日志记录失败不影响任务执行
						pass

		return wrapped_func

	@staticmethod
	def wrap_jobs_in_config(jobs: list, app=None) -> list:
		"""
		包装配置中的所有定时任务函数

		:param jobs: 任务配置列表
		:param app: Flask 应用实例（可选，如果不提供则尝试自动获取）
		:return: 包装后的任务配置列表
		"""
		wrapped_jobs = []

		for job in jobs:
			# 复制任务配置
			wrapped_job = job.copy()

			# 获取任务函数路径
			func_path = job.get('func')
			if not func_path:
				# 如果没有 func 路径，直接使用原配置
				wrapped_jobs.append(wrapped_job)
				continue

			# 解析函数路径：module:function_name
			if ':' not in func_path:
				# 格式不正确，直接使用原配置
				wrapped_jobs.append(wrapped_job)
				continue

			module_path, function_name = func_path.split(':', 1)

			try:
				# 动态导入模块
				module = importlib.import_module(module_path)

				# 获取原始函数
				original_func = getattr(module, function_name)

				# 获取任务ID和名称
				job_id = job.get('id', function_name)
				job_name = job.get('name', function_name)

				# 包装函数
				wrapped_func = SchedulerLog.wrap_job_function(
					original_func=original_func,
					job_id=job_id,
					job_name=job_name,
					app=app
				)

				# 将包装后的函数设置回模块（替换原函数）
				setattr(module, function_name, wrapped_func)

				# 使用包装后的函数路径（保持不变，因为已经替换了模块中的函数）
				wrapped_job['func'] = func_path

			except Exception as e:
				# 如果包装失败，记录错误但继续使用原配置
				pass

			wrapped_jobs.append(wrapped_job)

		return wrapped_jobs

