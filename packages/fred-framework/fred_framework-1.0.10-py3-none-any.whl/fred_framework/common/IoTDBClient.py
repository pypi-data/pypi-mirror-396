from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import current_app
from iotdb.Session import Session
from iotdb.utils.IoTDBConstants import TSDataType


class IoTDBClient:
	"""
	IoTDB 数据库操作工具类
	封装 IoTDB 的增删改查操作
	"""

	def __init__(self):
		"""
		初始化 IoTDB 连接
		"""
		self.iotdb_client = None
		self._connection_error = None
		self._init_iotdb_connection()

	def _init_iotdb_connection(self):
		"""
		初始化 IoTDB 数据库连接
		"""
		try:
			# 获取 IoTDB 配置
			iotdb_config = current_app.config.get('IOTDB_CONFIG', {})
			host = iotdb_config.get('host', '127.0.0.1')
			port = iotdb_config.get('port', 6667)
			username = iotdb_config.get('username', 'root')
			password = iotdb_config.get('password', 'root')

			# 建立连接
			self.iotdb_client = Session(host, port, username, password)
			self.iotdb_client.open()
		except Exception as e:
			# 连接失败时，将 iotdb_client 设置为 None，并记录错误信息
			self.iotdb_client = None
			self._connection_error = str(e)

	def _check_connection(self):
		"""
		检查 IoTDB 连接状态
		如果连接失败，抛出异常
		"""
		if self.iotdb_client is None:
			error_msg = self._connection_error or "IoTDB 连接失败"
			from flask import abort
			from flask_babelplus import gettext
			abort(500, gettext(f"IoTDB 连接失败: {error_msg}"))

	def _get_data_type(self, data_type_str: str):
		"""
		获取数据类型常量
		:param data_type_str: 数据类型字符串，如 'INT32', 'INT64', 'FLOAT', 'DOUBLE', 'TEXT', 'BOOLEAN', 'INT'
		:return: TSDataType 常量
		"""
		type_map = {
			'INT32': TSDataType.INT32,
			'INT64': TSDataType.INT64,
			'FLOAT': TSDataType.FLOAT,
			'DOUBLE': TSDataType.DOUBLE,
			'TEXT': TSDataType.TEXT,
			'BOOLEAN': TSDataType.BOOLEAN,
			'INT': TSDataType.INT64,  # INT 映射到 INT64
		}
		return type_map.get(data_type_str.upper(), TSDataType.TEXT)

	def create_device(self, device_path: str, measurements: list, data_types: list) -> bool:
		"""
		创建设备时序数据（如果时序已存在则跳过）
		:param device_path: 设备路径，如 'root.inference.camera_1_inference'
		:param measurements: 测量项列表
		:param data_types: 数据类型列表
		:return: 操作成功与否
		"""
		self._check_connection()
		try:
			# 确保设备路径以 root 开头
			if not device_path.startswith('root.'):
				device_path = f'root.{device_path}'

			created_count = 0
			skipped_count = 0

			# 为每个测量项创建时序
			for measurement, data_type in zip(measurements, data_types):
				# IoTDB 需要完整的路径格式：root.xxx.xxx.measurement
				full_path = f"{device_path}.{measurement}"
				# 将字符串类型转换为 IoTDB 数据类型
				iotdb_data_type = self._get_data_type(data_type).name
				create_sql = f"CREATE TIMESERIES {full_path} WITH DATATYPE={iotdb_data_type} ENCODING=PLAIN"

				try:
					# 使用 execute_non_query_statement 执行非查询语句
					self.iotdb_client.execute_non_query_statement(create_sql)
					created_count += 1
				except Exception as e:
					error_msg = str(e)
					# 如果时序已存在（错误码 503），则跳过
					if "already exist" in error_msg or "503" in error_msg:
						skipped_count += 1
						continue
					else:
						# 其他错误则抛出
						raise

			return True
		except Exception as e:
			return False

	def insert_data(self, device_path: str, timestamp: int, measurements: list, types_lst: list, values: list) -> bool:
		"""
		插入数据
		:param device_path: 设备路径，如 'root.inference.camera_1_inference'
		:param timestamp: 时间戳（时序值，单位由 Config.TIMESTAMP_TO_MS_MULTIPLIER 决定）
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000，则为毫秒
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000000，则为微秒
		:param measurements: 测量项列表
		:param types_lst: 数据类型列表
		:param values: 数据值列表（单条记录）
		:return: 插入是否成功
		"""
		self._check_connection()
		try:
			# 确保设备路径以 root 开头
			if not device_path.startswith('root.'):
				device_path = f'root.{device_path}'

			# 将数据类型字符串转换为 TSDataType 常量
			data_types = [self._get_data_type(dt) for dt in types_lst]

			# 使用 insert_record 插入单条数据
			# 参数顺序：device_path, timestamp, measurements, data_types, values
			self.iotdb_client.insert_record(
				device_path,
				timestamp,
				measurements,
				data_types,
				values
			)
			return True
		except Exception as e:
			return False

	def _build_query_sql(self, device_path: str, start_time: Optional[int] = None,
						 end_time: Optional[int] = None, limit: Optional[int] = None,
						 order_by: Optional[str] = None, offset: Optional[int] = None,
						 enable_tracing: bool = False) -> str:
		"""
		构建查询 SQL 语句
		:param device_path: 设备路径，支持通配符如 'root.inference.**'
		:param start_time: 开始时间戳（时序值，单位由 Config.TIMESTAMP_TO_MS_MULTIPLIER 决定）
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000，则为毫秒
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000000，则为微秒
			通过时序值（timestamp）进行时间区间查询
		:param end_time: 结束时间戳（时序值，单位由 Config.TIMESTAMP_TO_MS_MULTIPLIER 决定）
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000，则为毫秒
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000000，则为微秒
			通过时序值（timestamp）进行时间区间查询
		:param limit: 返回结果数量限制
		:param order_by: 排序方式，如 'time DESC' 或 'time ASC'，默认为 None（不排序）
		:param offset: 跳过前 N 行，用于分页查询
		:param enable_tracing: 是否启用性能追踪（TRACING），用于分析查询性能
		:return: SQL 语句
		"""
		# 确保设备路径以 root 开头
		if not device_path.startswith('root.'):
			device_path = f'root.{device_path}'

		# 构建 WHERE 子句
		where_parts = []

		# 时间区间查询：使用时序值（timestamp）进行过滤
		# IoTDB 的 time 字段是时序值，这是最有效的查询方式
		if start_time is not None:
			where_parts.append(f"time >= {start_time}")
		if end_time is not None:
			where_parts.append(f"time <= {end_time}")

		# 注意：IoTDB 的 WHERE 子句主要用于时间范围查询（通过时序值 timestamp）
		# 对于测量值的过滤，IoTDB 支持有限，通常需要在应用层（内存中）进行过滤
		# 如果需要过滤测量值，建议在查询结果返回后在应用层进行过滤

		where_clause = f" WHERE {' AND '.join(where_parts)}" if where_parts else ""

		# 构建 ORDER BY 子句
		order_by_clause = f" ORDER BY {order_by}" if order_by else ""

		# 构建 LIMIT 和 OFFSET 子句
		# IoTDB 支持 LIMIT N OFFSET M 语法进行分页查询
		if limit is not None:
			if offset is not None and offset > 0:
				limit_clause = f" LIMIT {limit} OFFSET {offset}"
			else:
				limit_clause = f" LIMIT {limit}"
		else:
			limit_clause = ""

		# 使用 SELECT * 语法，支持通配符路径
		# IoTDB 支持使用 ** 进行递归查询
		# 注意：在 IoTDB 中，SELECT * FROM device_path 会自动查询该设备下的所有测量值
		# 不需要添加 .* 后缀，添加 .* 反而可能导致查询失败
		# 如果路径已经以 .* 结尾，去掉它
		if device_path.endswith('.*'):
			device_path = device_path[:-2]

		# 如果启用追踪，在 SQL 前添加 TRACING 关键词
		tracing_prefix = "TRACING " if enable_tracing else ""
		sql = f"{tracing_prefix}SELECT * FROM {device_path}{where_clause}{order_by_clause}{limit_clause}"
		return sql.strip()

	@staticmethod
	def _extract_measurement_name(col_name: str) -> str:
		"""
		从列名提取测量值名称（移除设备路径前缀）
		:param col_name: 列名，如 'root.inference.camera_1_inference.frame_stamp'
		:return: 测量值名称，如 'frame_stamp'
		"""
		return col_name.split('.')[-1] if '.' in col_name else col_name

	def _convert_field_value(self, field_obj, data_type) -> Any:
		"""
		根据数据类型转换字段值为 Python 原生类型
		:param field_obj: IoTDB 字段对象
		:param data_type: 数据类型
		:return: 转换后的值
		"""
		try:
			if field_obj.is_null():
				return None

			if data_type == TSDataType.BOOLEAN:
				return bool(field_obj.get_bool_value())
			elif data_type == TSDataType.INT32:
				return int(field_obj.get_int_value())
			elif data_type == TSDataType.INT64:
				return int(field_obj.get_long_value())
			elif data_type == TSDataType.FLOAT:
				return float(field_obj.get_float_value())
			elif data_type == TSDataType.DOUBLE:
				return float(field_obj.get_double_value())
			elif data_type == TSDataType.TEXT:
				return str(field_obj.get_string_value())
			else:
				value = field_obj.get_object_value(data_type)
				if value is not None:
					type_name = value.__class__.__name__.lower()
					if 'int' in type_name:
						return int(value)
					elif 'float' in type_name or 'double' in type_name:
						return float(value)
					elif 'bool' in type_name:
						return bool(value)
					elif not isinstance(value, (str, int, float, bool, type(None))):
						return str(value)
				return value
		except Exception:
			return None

	def _parse_query_result(self, session_data_set, measurements: Optional[List[str]] = None) -> List[Dict[str, Any]]:
		"""
		解析查询结果集
		:param session_data_set: IoTDB 查询结果集
		:param measurements: 要查询的测量值列表，如果为 None 则查询所有测量值
		:return: 查询结果列表
		"""
		results = []
		column_names = session_data_set.get_column_names()

		# 如果指定了 measurements，转换为集合以提高查找效率
		measurements_set = set(measurements) if measurements else None

		while session_data_set.has_next():
			row = session_data_set.next()
			# 确保 timestamp 是整数类型
			timestamp = row.get_timestamp()
			record = {'timestamp': int(timestamp) if timestamp is not None else None}
			fields = row.get_fields()

			# 构建列名到字段值的映射（不包括 Time 列）
			col_name_to_field = {}
			field_index = 0
			for col_name in column_names:
				if col_name == 'Time':
					continue

				if field_index < len(fields):
					col_name_to_field[col_name] = fields[field_index]
					field_index += 1

			# 遍历所有列名（除了 Time），提取 measurement 名称并处理值
			for col_name in column_names:
				if col_name == 'Time':
					continue

				if col_name not in col_name_to_field:
					continue

				field_obj = col_name_to_field[col_name]
				data_type = field_obj.get_data_type()

				# 转换字段值
				value = self._convert_field_value(field_obj, data_type)

				# 提取测量值名称
				measurement_name = self._extract_measurement_name(col_name)

				# 如果指定了 measurements，只处理指定的测量值
				if measurements_set is None or measurement_name in measurements_set:
					# 对于同一个 measurement_name，优先保留非 None 值
					if measurement_name in record:
						if record[measurement_name] is not None:
							if value is not None:
								pass  # 保留旧值
						else:
							record[measurement_name] = value
					else:
						record[measurement_name] = value

			results.append(record)

		return results

	def list_timeseries(self, path_pattern: str = "root.**") -> List[str]:
		"""
		列出所有时序路径
		:param path_pattern: 路径模式，如 'root.inference.**'
		:return: 时序路径列表
		"""
		self._check_connection()
		try:
			# 确保路径以 root 开头
			if not path_pattern.startswith('root.'):
				path_pattern = f'root.{path_pattern}'

			# 使用 SHOW TIMESERIES 查询
			# IoTDB 的 SHOW TIMESERIES 语法：SHOW TIMESERIES [pathPattern]
			sql = f"SHOW TIMESERIES {path_pattern}"

			session_data_set = self.iotdb_client.execute_query_statement(sql)
			session_data_set.set_fetch_size(10000)

			timeseries_list = []
			while session_data_set.has_next():
				row = session_data_set.next()
				# SHOW TIMESERIES 返回的列：timeseries, alias, storage group, dataType, encoding, compression, tags, attributes
				fields = row.get_fields()
				if fields and len(fields) > 0:
					timeseries_path = fields[0].get_string_value()
					timeseries_list.append(timeseries_path)

			session_data_set.close_operation_handle()
			return timeseries_list
		except Exception as e:
			return []

	def query_count(self, device_path: str, start_time: Optional[int] = None,
					end_time: Optional[int] = None) -> int:
		"""
		使用 COUNT 聚合查询获取记录总数（优化性能）
		:param device_path: 设备路径，如 'root.inference.camera_1_inference' 或 'root.inference.**'
		:param start_time: 开始时间戳（时序值）
		:param end_time: 结束时间戳（时序值）
		:return: 记录总数，如果查询失败返回 0
		"""
		self._check_connection()
		try:
			# 确保设备路径以 root 开头
			if not device_path.startswith('root.'):
				device_path = f'root.{device_path}'

			# 构建 WHERE 子句
			where_parts = []
			if start_time is not None:
				where_parts.append(f"time >= {start_time}")
			if end_time is not None:
				where_parts.append(f"time <= {end_time}")
			where_clause = f" WHERE {' AND '.join(where_parts)}" if where_parts else ""

			# 构建 COUNT 查询 SQL
			# 注意：IoTDB 的 COUNT 查询需要指定具体的测量值，不能使用 COUNT(*)
			# 对于通配符路径，需要指定一个具体的测量值，比如第一个测量值
			# 这里尝试使用一个常见的测量值（如 frame_stamp）来统计记录数
			# 如果 device_path 包含通配符，需要先获取一个具体的测量值
			if '**' in device_path or '*' in device_path:
				# 对于通配符路径，尝试使用 COUNT(第一个测量值)
				# 先尝试使用 frame_stamp（推理日志中常见的字段）
				sql = f"SELECT COUNT(frame_stamp) FROM {device_path}{where_clause}"
			else:
				# 对于具体路径，可以使用任意测量值
				sql = f"SELECT COUNT(frame_stamp) FROM {device_path}{where_clause}"

			# 执行查询
			session_data_set = self.iotdb_client.execute_query_statement(sql)
			session_data_set.set_fetch_size(10000)

			# 解析结果
			count = 0
			if session_data_set.has_next():
				row = session_data_set.next()
				fields = row.get_fields()
				if fields and len(fields) > 0:
					# COUNT 查询返回的是聚合结果
					count_value = fields[0].get_long_value() if hasattr(fields[0], 'get_long_value') else fields[0].get_int_value()
					count = int(count_value) if count_value is not None else 0

			session_data_set.close_operation_handle()
			return count
		except Exception as e:
			return -1  # 返回 -1 表示 COUNT 查询失败，需要使用其他方法

	def query_data(self, device_path: str, measurements: Optional[List[str]] = None,
				   start_time: Optional[int] = None, end_time: Optional[int] = None,
				   limit: Optional[int] = None, order_by: Optional[str] = None,
				   offset: Optional[int] = None, enable_tracing: bool = False) -> List[Dict[str, Any]]:
		"""
		查询数据
		:param device_path: 设备路径，如 'root.inference.camera_1_inference' 或 'root.inference.**'
		:param measurements: 要查询的测量值列表，如果为 None 则查询所有测量值
		:param start_time: 开始时间戳（时序值，单位由 Config.TIMESTAMP_TO_MS_MULTIPLIER 决定）
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000，则为毫秒
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000000，则为微秒
			通过时序值（timestamp）进行时间区间查询，如果为 None 则不限制开始时间
		:param end_time: 结束时间戳（时序值，单位由 Config.TIMESTAMP_TO_MS_MULTIPLIER 决定）
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000，则为毫秒
			如果 TIMESTAMP_TO_MS_MULTIPLIER = 1000000，则为微秒
			通过时序值（timestamp）进行时间区间查询，如果为 None 则不限制结束时间
		:param limit: 返回结果数量限制
		:param order_by: 排序方式，如 'time DESC' 或 'time ASC'，默认为 None（不排序）
		:param offset: 跳过前 N 行，用于分页查询
		:param enable_tracing: 是否启用性能追踪（TRACING），用于分析查询性能
		:return: 查询结果列表，每个元素是一个字典，包含 timestamp 和各个测量值
		"""
		self._check_connection()
		try:
			# 构建 SQL 语句
			sql = self._build_query_sql(device_path, start_time, end_time, limit, order_by, offset, enable_tracing)

			# 执行查询
			session_data_set = self.iotdb_client.execute_query_statement(sql)
			session_data_set.set_fetch_size(10000)

			# 解析结果
			results = self._parse_query_result(session_data_set, measurements)

			session_data_set.close_operation_handle()

			return results
		except Exception as e:
			return []

	def delete_data(self, device_path: str, start_time: Optional[int] = None,
					end_time: Optional[int] = None, measurements: Optional[List[str]] = None) -> bool:
		"""
		删除数据
		:param device_path: 设备路径，如 'root.inference.camera_1_inference' 或 'root.inference.**'
		:param start_time: 开始时间戳（毫秒），如果为 None 则删除所有数据
		:param end_time: 结束时间戳（毫秒），如果为 None 则删除到最新
		:param measurements: 要删除的测量值列表，如果为 None 则删除所有测量值
		:return: 删除是否成功
		"""
		self._check_connection()
		try:
			# 确保设备路径以 root 开头
			if not device_path.startswith('root.'):
				device_path = f'root.{device_path}'

			# 如果使用通配符路径，需要先列出所有时序路径，然后逐个删除
			if '**' in device_path or '*' in device_path:
				# 列出所有时序路径
				timeseries_list = self.list_timeseries(device_path)

				if not timeseries_list:
					return True  # 没有数据可删，返回成功

				# 提取所有唯一的设备路径（用于统计）
				device_paths = set()
				for ts_path in timeseries_list:
					# 时序路径格式：root.inference.camera_1_inference.frame_stamp
					# 提取设备路径：root.inference.camera_1_inference
					parts = ts_path.split('.')
					if len(parts) >= 3:
						device_path_extracted = '.'.join(parts[:3])
						device_paths.add(device_path_extracted)

				# 如果指定了 measurements，只删除指定的测量值
				# 否则删除所有时序路径
				if measurements:
					# 只删除指定测量值的时序路径
					paths_to_delete = []
					for ts_path in timeseries_list:
						measurement_name = ts_path.split('.')[-1]  # 获取测量值名称
						if measurement_name in measurements:
							paths_to_delete.append(ts_path)
				else:
					# 删除所有时序路径
					paths_to_delete = timeseries_list

				# 按设备路径分组删除（更高效）
				device_path_to_timeseries = {}
				for ts_path in paths_to_delete:
					parts = ts_path.split('.')
					if len(parts) >= 3:
						dev_path = '.'.join(parts[:3])
						if dev_path not in device_path_to_timeseries:
							device_path_to_timeseries[dev_path] = []
						device_path_to_timeseries[dev_path].append(ts_path)

				# 直接删除所有时序路径（IoTDB 的 DELETE FROM 需要精确的时序路径）
				# 因为时序路径格式复杂（如 root.inference.camera_1.model_5.tag_1.xxx），
				# 删除设备路径可能无法删除子路径数据，所以直接删除所有时序路径
				# 注意：IoTDB 的 DELETE FROM 只删除数据点，不删除时序路径定义
				for ts_path in paths_to_delete:
					try:
						if start_time is not None and end_time is not None:
							delete_sql = f"DELETE FROM {ts_path} WHERE time >= {start_time} AND time <= {end_time}"
						elif start_time is not None:
							delete_sql = f"DELETE FROM {ts_path} WHERE time >= {start_time}"
						elif end_time is not None:
							delete_sql = f"DELETE FROM {ts_path} WHERE time <= {end_time}"
						else:
							# 删除所有数据，使用 DELETE FROM 或 DELETE DATABASE
							# 对于单个时序路径，使用 DELETE FROM
							delete_sql = f"DELETE FROM {ts_path}"

						self.iotdb_client.execute_non_query_statement(delete_sql)
					except Exception as e:
						pass
			else:
				# 构建删除路径列表
				if measurements:
					# 删除指定测量值
					paths = [f"{device_path}.{measurement}" for measurement in measurements]
				else:
					# 删除整个设备的所有数据
					paths = [device_path]

				# 构建删除 SQL
				if start_time is not None and end_time is not None:
					# 删除指定时间范围的数据
					for path in paths:
						delete_sql = f"DELETE FROM {path} WHERE time >= {start_time} AND time <= {end_time}"
						self.iotdb_client.execute_non_query_statement(delete_sql)
				elif start_time is not None:
					# 删除从开始时间到现在的数据
					for path in paths:
						delete_sql = f"DELETE FROM {path} WHERE time >= {start_time}"
						self.iotdb_client.execute_non_query_statement(delete_sql)
				elif end_time is not None:
					# 删除到结束时间的数据
					for path in paths:
						delete_sql = f"DELETE FROM {path} WHERE time <= {end_time}"
						self.iotdb_client.execute_non_query_statement(delete_sql)
				else:
					# 删除所有数据
					for path in paths:
						delete_sql = f"DELETE FROM {path}"
						self.iotdb_client.execute_non_query_statement(delete_sql)

			return True
		except Exception as e:
			return False

	def clear_all_data(self, path_pattern: str = "root.inference.**") -> bool:
		"""
		清空所有数据
		:param path_pattern: 路径模式，如 'root.inference.**'
		:return: 清空是否成功
		"""
		self._check_connection()
		try:
			# 列出所有时序路径
			timeseries_list = self.list_timeseries(path_pattern)

			if not timeseries_list:
				return True

			# 提取所有唯一的设备路径
			device_paths = set()
			for ts_path in timeseries_list:
				parts = ts_path.split('.')
				if len(parts) >= 3:
					device_path = '.'.join(parts[:3])
					device_paths.add(device_path)

			# 逐个清空每个设备的所有数据
			for device_path in device_paths:
				try:
					delete_sql = f"DELETE FROM {device_path}"
					self.iotdb_client.execute_non_query_statement(delete_sql)
				except Exception as e:
					pass

			return True
		except Exception as e:
			return False

	def delete_timeseries(self, path_pattern: str) -> bool:
		"""
		删除时序路径定义（删除路径结构，不仅仅是数据）
		:param path_pattern: 路径模式，支持通配符，如 'root.inference.**' 或 'root.inference.camera_1.label_2.**'
		:return: 删除是否成功
		"""
		self._check_connection()
		try:
			# 确保路径以 root 开头
			if not path_pattern.startswith('root.'):
				path_pattern = f'root.{path_pattern}'

			# 如果使用通配符路径，需要先列出所有时序路径，然后逐个删除
			if '**' in path_pattern or '*' in path_pattern:
				# 列出所有匹配的时序路径
				timeseries_list = self.list_timeseries(path_pattern)

				if not timeseries_list:
					return True  # 没有路径可删，返回成功

				# 逐个删除每个时序路径
				for ts_path in timeseries_list:
					try:
						delete_sql = f"DELETE TIMESERIES {ts_path}"
						self.iotdb_client.execute_non_query_statement(delete_sql)
					except Exception as e:
						error_msg = str(e)
						# 如果路径不存在（508错误）或由设备模板表示，视为成功（幂等性）
						if "508" in error_msg or "does not exist" in error_msg or "device template" in error_msg.lower():
							continue
						# 其他错误记录警告但继续删除其他路径
						continue
			else:
				# 对于具体路径，判断是设备路径还是时序路径
				# 先尝试列出该路径下的所有时序路径（使用通配符）
				# 如果路径以 .** 结尾，直接使用；否则添加 .** 来匹配该路径下的所有时序路径
				if path_pattern.endswith('.**'):
					search_pattern = path_pattern
				else:
					# 对于设备路径（如 root.inference.camera_1.tag_1），添加 .** 来匹配所有时序路径
					search_pattern = f"{path_pattern}.**"

				# 列出该路径下的所有时序路径
				timeseries_list = self.list_timeseries(search_pattern)

				if not timeseries_list:
					# 如果没有找到时序路径，可能是：
					# 1. 路径不存在（已删除）
					# 2. 传入的是完整的时序路径，尝试直接删除
					if not path_pattern.endswith('.**'):
						# 尝试作为完整的时序路径直接删除
						try:
							delete_sql = f"DELETE TIMESERIES {path_pattern}"
							self.iotdb_client.execute_non_query_statement(delete_sql)
							return True
						except Exception as e:
							error_msg = str(e)
							# 如果路径不存在（508错误）或由设备模板表示，视为成功（幂等性）
							if "508" in error_msg or "does not exist" in error_msg or "device template" in error_msg.lower():
								return True
							# 其他错误才视为失败
							return False
					else:
						# 路径下没有时序路径，视为删除成功
						return True

				# 逐个删除每个时序路径
				success_count = 0
				fail_count = 0
				for ts_path in timeseries_list:
					try:
						delete_sql = f"DELETE TIMESERIES {ts_path}"
						self.iotdb_client.execute_non_query_statement(delete_sql)
						success_count += 1
					except Exception as e:
						error_msg = str(e)
						# 如果路径不存在（508错误）或由设备模板表示，视为成功（幂等性）
						if "508" in error_msg or "does not exist" in error_msg or "device template" in error_msg.lower():
							success_count += 1
						else:
							# 其他错误记录警告
							fail_count += 1

				# 如果至少有一个成功，或者所有都因为不存在而跳过，视为成功
				if success_count > 0 or fail_count == 0:
					return True
				else:
					return False

			return True
		except Exception as e:
			return False

	def close_connection(self):
		"""关闭 IoTDB 连接"""
		try:
			self.iotdb_client.close()
		except Exception as e:
			pass
