#!/usr/bin/env python3  
# -*- coding: utf-8 -*-  
"""  
@author: cyg  
@date: 2024/7/28 下午10:35  
"""
# -*- coding: utf-8 -*-
from flask import current_app


class AliyunSms:
	"""
		发送短信
	"""
	
	@staticmethod
	def create_client():
		"""
		使用AK&SK初始化账号Client
		@param access_key_id:
		@param access_key_secret:
		@return: Client
		@throws Exception
		"""
		key_id = current_app.config.get("ALIBABA_KEY_ID", "")
		if key_id == '':
			return None
		from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
		from alibabacloud_tea_openapi import models as open_api_models
		config = open_api_models.Config(
			access_key_id=current_app.config.get("ALIBABA_KEY_ID"),
			access_key_secret=current_app.config.get("ALIBABA_KEY_SECRET")
		)
		# 访问的域名
		config.endpoint = f'dysmsapi.aliyuncs.com'
		return Dysmsapi20170525Client(config)
	
	@staticmethod
	def send_code(phone, code):
		"""
		发送短信验证码
		:param phone:手机号
		:param code: 验证码 （4位数字）
		:return: bool
		"""
		client = AliyunSms.create_client()
		if client is None:
			raise Exception("请先配置短信配置信息")
		from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
		from alibabacloud_tea_util import models as util_models
		from alibabacloud_tea_util.client import Client as UtilClient
		send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
			sign_name=current_app.config.get("ALIBABA_SIGN_NAME"),
			template_code=current_app.config.get("ALIBABA_TEMPLATE_CODE"),
			phone_numbers=phone,
			template_param='{"code":"' + code + '"}'
		)
		try:
			result = client.send_sms_with_options(send_sms_request, util_models.RuntimeOptions())
			code = result.to_map()['body']['Code']
			if code != "OK":
				raise Exception("发送失败！")
			return True
		except Exception as error:
			UtilClient.assert_as_string(str(error))
			return False
