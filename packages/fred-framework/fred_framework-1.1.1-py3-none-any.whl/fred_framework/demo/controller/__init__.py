# 路由控制
"""
基本的登录验证
"""
from functools import wraps

from flask import session
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from werkzeug.exceptions import Unauthorized

from demo import demo


def user_required(f):
    @wraps(f)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != demo.name:
            raise Unauthorized()
        return f(*args, **kwargs)

    return wrapper


@demo.before_request
def get_user_info():
    try:
        # 尝试验证JWT
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != demo.name:
            user_info = None
        else:
            user_info = get_jwt_identity()
    except Exception as e:
        user_info = None
    key=f'{demo.name}_user_info'
    session[key] = user_info
    return None
