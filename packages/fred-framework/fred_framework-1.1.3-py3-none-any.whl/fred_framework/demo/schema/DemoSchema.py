# coding: utf-8
from marshmallow import Schema, fields

"""
 * @Author：PyCharm - yougangchen
 * @Package：DemoSchema
 * @Project：fred-frame
 * @name：DemoSchema
 * @Date：2025/7/2 15:42 - 星期三
 * @Filename：DemoSchema
 
"""


class DemoSchema(Schema):
	"""
        @desc : DemoSchema
    """
	id = fields.Int()
