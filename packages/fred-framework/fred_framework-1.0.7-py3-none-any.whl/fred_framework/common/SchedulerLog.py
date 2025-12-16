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
			try:
				current_app.logger.error(
					f"[定时任务日志] 保存任务 {job_id} ({job_name}) 日志失败: {str(e)}"
				)
			except:
				pass
			# 回滚事务
			try:
				db.session.rollback()
			except:
				pass

	@staticmethod
	def wrap_job_function(original_func: Callable, job_id: str, job_name: str) -> Callable:
		"""
		包装定时任务函数，添加日志记录功能

		:param original_func: 原始任务函数
		:param job_id: 任务ID
		:param job_name: 任务名称
		:return: 包装后的函数
		"""
		@functools.wraps(original_func)
		def wrapped_func(*args, **kwargs):
			# 确保在应用上下文中执行
			from run import app

			start_time = datetime.now()
			success = False
			result = None
			error = None

			try:
				# 执行原始任务函数（保持原有的应用上下文逻辑）
				result = original_func(*args, **kwargs)
				success = True

				# 如果返回结果是字典且包含 success 字段，使用该字段判断
				if isinstance(result, dict) and "success" in result:
					success = result.get("success", False)
					if not success:
						error = result.get("message", "任务执行失败")

				return result
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
					with app.app_context():
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
					try:
						with app.app_context():
							app.logger.error(
								f"[定时任务日志] 记录任务 {job_id} ({job_name}) 日志异常: {str(log_error)}"
							)
					except:
						pass

		return wrapped_func

	@staticmethod
	def wrap_jobs_in_config(jobs: list) -> list:
		"""
		包装配置中的所有定时任务函数

		:param jobs: 任务配置列表
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
					job_name=job_name
				)

				# 将包装后的函数设置回模块（替换原函数）
				setattr(module, function_name, wrapped_func)

				# 使用包装后的函数路径（保持不变，因为已经替换了模块中的函数）
				wrapped_job['func'] = func_path

			except Exception as e:
				# 如果包装失败，记录错误但继续使用原配置
				try:
					from flask import current_app
					if current_app:
						current_app.logger.warning(f"包装定时任务 {func_path} 失败: {str(e)}，将使用原函数")
				except:
					pass

			wrapped_jobs.append(wrapped_job)

		return wrapped_jobs

