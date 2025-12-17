# coding: utf-8
from marshmallow import Schema, fields

"""
 * @Author：PyCharm - yougangchen
 * @Package：PageSchema
 * @Project：fred-frame
 * @name：PageSchema
 * @Date：2025/7/2 11:33 - 星期三
 * @Filename：PageSchema
 
"""


class PageSchema(Schema):
	"""
        @desc : 公共分页参数，支持泛型和嵌套
    """
	total = fields.Int(metadata={'description': '总数'})
	pageNum = fields.Int(metadata={'description': '页码'})
	pageSize = fields.Int(metadata={'description': '每页数量'})
	
	def __init__(self, item_schema=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if item_schema is not None:
			# 支持传入schema类或实例
			if isinstance(item_schema, type) and issubclass(item_schema, Schema):
				self.declared_fields['records'] = fields.List(fields.Nested(item_schema), metadata={'description': '列表'})
			elif isinstance(item_schema, Schema):
				self.declared_fields['records'] = fields.List(fields.Nested(item_schema.__class__), metadata={'description': '列表'})
			else:
				raise ValueError('item_schema must be a marshmallow.Schema subclass or instance')
		else:
			self.declared_fields['records'] = fields.List(fields.Dict(), metadata={'description': '列表'})


def PageSchemaFactory(item_schema, custom_name=None):
    # 获取 item_schema 的名称用于生成唯一的 schema 名称
    if custom_name:
        schema_name = custom_name
    else:
        if hasattr(item_schema, '__name__'):
            base_name = item_schema.__name__
        elif hasattr(item_schema, '__class__'):
            base_name = item_schema.__class__.__name__
        else:
            base_name = "Item"
        
        schema_name = f"{base_name}Page"
    
    # 动态创建带有唯一名称的 schema 类
    class Meta:
        pass
    
    PageSchemaClass = type(
        schema_name,  # 类名
        (PageSchema,),  # 基类
        {
            'records': fields.List(fields.Nested(item_schema), metadata={'description': '列表'}),
            'Meta': Meta,
            '__module__': item_schema.__module__ if hasattr(item_schema, '__module__') else __name__
        }
    )
    
    return PageSchemaClass
