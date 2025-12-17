"""
 * @Author：cyg
 * @Package：WechatLoginService
 * @Project：Default (Template) Project
 * @name：WechatLoginService
 * @Date：2025/4/2 15:34
 * @Filename：WechatLoginService
"""
import uuid
from urllib.parse import urlencode

import requests
from flask import current_app


class WechatLogin:
	def generate_qr(self):
		"""
		获取微信二维码接口
		"""
		# 生成唯一标识（用于关联二维码和用户）
		state = str(uuid.uuid4())  # 防止 CSRF
		data = {
			"state": state,
			"code": None,
			"openid": None
		}
		# TODO 通过auth_url将data存入redis 然后再wechat_callback 设置其他值
		# 构造微信授权 URL（二维码内容指向该 URL）
		params = {
			"appid": current_app.config.get("WECHAT_APP_ID"),
			"redirect_uri": current_app.config.get("SITE_NAME") + f"/web/wechat/callback",
			"response_type": "code",
			"scope": "snsapi_login",
			"state": state
		}
		auth_url = f"https://open.weixin.qq.com/connect/qrconnect?{urlencode(params)}#wechat_redirect"
		
		return {
			"state": state,
			"auth_url": auth_url  # 前端生成二维码
		}
	
	def wechat_callback(self, args):
		"""
		微信回调
		"""
		code = args["code"]
		state = args["state"]
		# TODO 通过state获取redis中的值并修改data中的code和openid
		# 通过 code 换取 access_token 和 openid
		token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
		params = {
			"appid": current_app.config.get("WECHAT_APP_ID"),
			"secret": current_app.config.get("WECHAT_APP_SECRET"),
			"code": code,
			"grant_type": "authorization_code"
		}
		response = requests.get(token_url, params=params).json()
		
		if "openid" not in response:
			raise ValueError("Failed to get openid")
		
		openid = response["openid"]
		access_token = response["access_token"]
		#获取用户信息
		info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}"
		user_info = requests.get(info_url).json()
		""""
		获取用户信息返回的数据:
			{
				"openid":"OPENID",
				"nickname":"NICKNAME",
				"sex":1,
				"province":"PROVINCE",
				"city":"CITY",
				"country":"COUNTRY",
				"headimgurl": "https://thirdwx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/0",
				"privilege":[
				"PRIVILEGE1",
				"PRIVILEGE2"
				],
				"unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"

			}

		"""
		# 更新扫码状态（标记为已授权）
		
		return ""
	
	def check_login(self, args):
		"""
		异步轮询检查是否登录成功
		"""
		# TODO  前端轮询 检查微信是否回调成功
		pass
