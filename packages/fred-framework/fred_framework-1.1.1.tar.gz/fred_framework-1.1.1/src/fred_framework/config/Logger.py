#!/usr/bin/env python3  
# coding: utf-8
"""  
@author: Administrator  
@date: 2024/12/19 21:03  
@desc: 
"""
import logging
import os
from logging.handlers import RotatingFileHandler


class Logger:
	@staticmethod
	def set_logger(app):
		"""
		日志记录配置
		"""
		# 获取日志文件路径
		log_file_path = app.config.get('LOG_FILE', '')
		if log_file_path == '':
			return None
		
		# 确保日志目录存在
		log_dir = os.path.dirname(log_file_path)
		if not os.path.exists(log_dir):
			os.makedirs(log_dir)
		log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
		handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=100000, backupCount=3)
		handler.setLevel(log_level)
		formatter = logging.Formatter(app.config['LOG_FORMAT'])
		handler.setFormatter(formatter)
		
		app.logger.addHandler(handler)
