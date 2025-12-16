# coding: utf-8
"""
 * @Author：cyg
 * @Package：DemoController
 * @Project：Default (Template) Project
 * @name：DemoController
 * @Date：2025/7/2 15:40
 * @Filename：DemoController
"""
from flask.views import MethodView

from demo import demo
from demo.controller import user_required
from demo.schema.DemoSchema import DemoSchema
from demo.service.DemoService import DemoService


@demo.route("/demo")
class DemoController(MethodView):
	
	@user_required
	@demo.arguments(DemoSchema, location='query')
	@demo.response(200)
	def get(self,args):
		"""
		获取信息
		"""
		data = DemoService().demo(args)
		return data
	
	@user_required
	@demo.arguments(DemoSchema)
	@demo.response(200)
	def post(self,args):
		"""
		新增内容
		"""
		data = DemoService().demo(args)
		return data
	
	@user_required
	@demo.arguments(DemoSchema, location='query')
	@demo.response(200)
	def put(self,args):
		"""
		修改内容
		"""
		data = DemoService().demo(args)
		return data
	
	@user_required
	@demo.arguments(DemoSchema, location='query')
	@demo.response(200)
	def delete(self,args):
		"""
		删除内容
		"""
		data = DemoService().demo(args)
		return data
