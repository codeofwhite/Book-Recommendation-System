# user_profile_service/app.py

import os
from flask import Flask
from flask_cors import CORS
from models import db # 从 models.py 导入 db 实例
from routes.book_engagement import book_engagement_bp # 导入书籍互动蓝图
from routes.review_engagement import review_engagement_bp # 导入书评互动蓝图
from routes.review_content import review_content_bp # **新增：导入书评内容蓝图**
from routes.review_routes import review_bp # 如果有书评提交的蓝图
# from routes.review_submission import review_submission_bp # 如果有书评提交的蓝图

app = Flask(__name__)

# 允许跨域请求
CORS(app)

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:your_mysql_password@localhost/book_engagement'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 db 实例
db.init_app(app)

# --- 注册蓝图 ---
# 注意：蓝图的 url_prefix 是在蓝图文件内部定义的，这里只需要注册蓝图对象
app.register_blueprint(book_engagement_bp)
app.register_blueprint(review_engagement_bp)
app.register_blueprint(review_content_bp) # **新增：注册书评内容蓝图**
app.register_blueprint(review_bp) # 如果有书评提交的蓝图
# app.register_blueprint(review_submission_bp) # 如果有书评提交的蓝图

# --- Database Initialization (Run once to create tables) ---
@app.cli.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    with app.app_context(): # 在应用上下文中执行数据库操作
        db.drop_all()
        db.create_all()
        print("Initialized the database for book favorites, review favorites, book likes, and review likes.")

if __name__ == '__main__':
    # 确保 app.run 监听在 0.0.0.0，以便 Docker 容器可以从外部访问
    # 端口保持 5003，与 docker-compose.yml 中的映射一致
    app.run(host='0.0.0.0', debug=True, port=5003)