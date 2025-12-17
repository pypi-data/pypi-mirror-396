from flask_smorest import Blueprint
#
demo = Blueprint('demo', __name__, url_prefix="/demo")
# 变量demo 需要和目录名字相同才能自动注册
# 所有的路由 必须写在controller中 框架会自动引入路由
# 所有的前端打包文件必须放在templates文件夹中例如:templates/demo 其中demo 表示当前这个模块的名字
