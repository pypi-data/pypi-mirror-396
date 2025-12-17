import importlib
import os
from pathlib import Path

from flask import Flask
from flask_cors import CORS

from fred_framework.common.Blueprints import Blueprints
from fred_framework.common.Extensions import Extensions
from fred_framework.common.HandleExcetion import HandleException
from fred_framework.common.Response import Response
from fred_framework.common.Route import Route
from fred_framework.common.Swagger import Swagger
from fred_framework.common.Utils import Utils
from fred_framework.config.Config import Config
from fred_framework.config.Logger import Logger

def create_app():
    """
    创建应用
    """
    app = Flask(__name__)
    
    app.config.from_object(Config)
    try:
        config_module = importlib.import_module('config.Config')
        Custom_Config = getattr(config_module, 'Config')
        config_msg = "加载自定义Config,自定义配置会覆盖默认配置"
        app.config.from_object(Custom_Config)
    except (ImportError, AttributeError) as e:
        # 可以选择记录日志或者静默跳过
        config_msg = "没有配置自定义Config"
    app.config['SECRET_KEY'] = Utils.get_secret_key('session_secret_key',app)
    if app.config['ENCRYPT_DATA']:  # 如果启用数据加密才生成fernet_key
        app.config['FERNET_KEY'] = Utils.get_secret_key('fernet_key',app)
    # 配置app.logger
    Logger.set_logger(app)
    app.logger.info(config_msg)
    
    # 初始化组件
    Extensions(app).initialize_extensions()
    
    # 注册蓝图
    Blueprints(app).register_blueprints()
    
    # 设置默认路由 后端和swagger
    Route(app).set_routes()
    
    # 启用 swagger
    Swagger(app)
    # 全局异常处理
    HandleException(app)
    # 重新定义模板文件路径
    
    # 自定义输出格式
    Response().custom_response(app)
    
    if app.debug:
        app.logger.info("开启debug模式，并允许跨域请求")
        CORS(app, supports_credentials=True)
    
    return app


def main():
    """
    主函数，用于启动应用
    """
    app = create_app()
    app.run()


if __name__ == '__main__':
    main()
