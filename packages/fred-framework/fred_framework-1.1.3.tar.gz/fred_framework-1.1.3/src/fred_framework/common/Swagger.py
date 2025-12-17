"""
 * @Author：cyg
 * @Package：Swagger
 * @Project：Default (Template) Project
 * @name：Swagger
 * @Date：2025/5/12 16:44
 * @Filename：Swagger
"""
from flask import render_template_string
from flask_swagger_ui import get_swaggerui_blueprint


class Swagger:
    def __init__(self, app):
        """
		初始化 Swagger 类
		:param app: Flask 应用对象
		"""
        # 创建Swagger UI蓝图
        enable_swagger = app.config.get('ENABLE_SWAGGER', False)
        if not enable_swagger:
            return
        swagger_path = app.config.get('OPENAPI_SWAGGER_UI_PATH', "")
        name = app.config.get('API_TITLE', "")
        swagger_ui_blueprint = get_swaggerui_blueprint(swagger_path, '/openapi.json', config={'app_name': name})
        app.register_blueprint(swagger_ui_blueprint, url_prefix=swagger_path)
        
        ELEMENTS_TEMPLATE = """

        <!doctype html>
        
        <html>
        
        <head>
        
          <title>API 文档 - Scalar</title>
        
          <meta charset="utf-8" />
        
          <meta name="viewport" content="width=device-width, initial-scale=1" />
        
        </head>
        
        <body>
        
          <!-- 引入 Scalar 客户端 -->
        
          <script
        
            id="api-reference"
        
            data-url="{{ spec_url }}"
        
            data-proxy-url="https://proxy.scalar.com"
        
            data-show-sidebar="true"
        
            data-theme="default"
        
            data-hide-authentication-button="false"
        
            data-default-http-verb="get"
        
          ></script>
        
          <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
        
        </body>
        
        </html>
        
        """
        
        @app.route('/doc')
        def docs():
            return render_template_string(ELEMENTS_TEMPLATE, spec_url='/openapi.json')
    