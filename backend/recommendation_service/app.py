# recommendation_service/app.py

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text # 用于执行原生 SQL
import pandas as pd # 用于数据处理，方便聚合
from datetime import datetime, timedelta
import random # 用于随机推荐

app = Flask(__name__)

# --- 数据库配置 ---
# 从环境变量获取数据库连接信息
DB_HOST = os.getenv('REC_DB_HOST', 'recommendation_db')
DB_USER = os.getenv('REC_DB_USER', 'rec_user')
DB_PASSWORD = os.getenv('REC_DB_PASSWORD', 'rec_password')
DB_NAME = os.getenv('REC_DB_NAME', 'recommendation_db')
DB_PORT = os.getenv('REC_DB_PORT', '3306') # MySQL 默认端口

# SQLAlchemy 数据库 URI
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 禁用事件系统，节省内存

db = SQLAlchemy(app)

# --- SQLAlchemy 模型定义 (映射 ETL 后加载到 recommendation_db 的表) ---
# 注意：这些模型需要与你的 ETL 脚本将数据加载到的表结构一致
class RecBook(db.Model):
    __tablename__ = 'rec_books' # 对应 ETL 加载的图书表
    book_id = db.Column(db.String(10), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    last_sync_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'category': self.category
        }

class RecUserProfile(db.Model): # 新增用户配置文件模型
    __tablename__ = 'rec_user_profiles' # 对应 ETL 加载的用户表
    user_id = db.Column(db.String(20), primary_key=True)
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    last_sync_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'nickname': self.nickname,
            'email': self.email,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None
        }


# --- 简单的推荐逻辑 (仅用于验证数据同步) ---
def get_random_books_from_db(top_n=10):
    """
    从 recommendation_db 获取随机图书列表，用于验证 rec_books 数据是否成功同步。
    这是一个临时验证函数，没有实际推荐算法逻辑。
    """
    print(f"Fetching {top_n} random books from 'rec_books' for ETL verification...")
    try:
        # 获取所有图书的 ID 列表
        all_book_ids = db.session.query(RecBook.book_id).all()
        all_book_ids = [book_id[0] for book_id in all_book_ids] # 提取元组中的 ID

        if not all_book_ids:
            return []

        # 随机选择 top_n 个图书 ID (如果总数不足 top_n，则返回所有)
        selected_book_ids = random.sample(all_book_ids, min(top_n, len(all_book_ids)))

        # 查询这些图书的详细信息
        recommendations = db.session.query(RecBook).filter(RecBook.book_id.in_(selected_book_ids)).all()
        
        # 转换为字典列表
        result = [book.to_dict() for book in recommendations]
        
        # 增加一个备注，表明这是随机推荐用于验证
        for item in result:
            item['reason'] = '随机推荐（用于验证ETL）'
        
        return result

    except Exception as e:
        print(f"Error fetching random books: {e}")
        return [] # 返回空列表表示获取失败或无推荐

# --- Flask 路由 ---

@app.route('/')
def home():
    """
    根路径健康检查或欢迎信息。
    """
    return "Welcome to the Recommendation Service!"

@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口，检查数据库连接。
    """
    try:
        # 尝试执行一个简单的查询来检查数据库连接
        db.session.execute(text("SELECT 1")).scalar()
        return jsonify({"status": "UP", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "DOWN", "database": "disconnected", "error": str(e)}), 500

@app.route('/verify/books', methods=['GET'])
def verify_books_etl():
    """
    验证图书数据 ETL 是否成功。
    返回从 rec_books 表中随机获取的图书列表。
    """
    top_n = request.args.get('top_n', 10, type=int)
    books = get_random_books_from_db(top_n=top_n)
    
    if not books:
        return jsonify({"message": "No books found in 'rec_books' table. ETL might not be complete or data is empty.", "books": []}), 200

    return jsonify({"message": "ETL verification for books: SUCCESS", "books": books}), 200

@app.route('/verify/users', methods=['GET'])
def verify_users_etl():
    """
    验证用户数据 ETL 是否成功。
    返回 rec_user_profiles 表中的部分用户数据。
    """
    top_n = request.args.get('top_n', 10, type=int)
    
    try:
        users = db.session.query(RecUserProfile).limit(top_n).all()
        if not users:
            return jsonify({"message": "No users found in 'rec_user_profiles' table. ETL might not be complete or data is empty.", "users": []}), 200
        
        result = [user.to_dict() for user in users]
        return jsonify({"message": "ETL verification for users: SUCCESS", "users": result}), 200

    except Exception as e:
        print(f"Error fetching users for verification: {e}")
        return jsonify({"message": "Error fetching user data.", "error": str(e), "users": []}), 500

@app.route('/recommendations/offline/<user_id>', methods=['GET'])
def get_user_offline_recommendations(user_id):
    """
    为指定用户提供离线推荐。
    在当前没有行为日志的情况下，作为占位符返回随机图书。
    """
    top_n = request.args.get('top_n', 10, type=int)
    recommendations = get_random_books_from_db(top_n=top_n)

    if not recommendations:
        return jsonify({"user_id": user_id, "message": "No recommendations found. 'rec_books' table might be empty.", "recommendations": []}), 200

    return jsonify({"user_id": user_id, "recommendations": recommendations}), 200

# --- 应用启动 ---
if __name__ == '__main__':
    with app.app_context():
        try:
            # 检查并创建 rec_books 和 rec_user_profiles 表
            if not db.engine.dialect.has_table(db.engine, 'rec_books'):
                db.create_all() # 这会创建所有定义的模型对应的表
                print("Tables 'rec_books' and 'rec_user_profiles' created in recommendation_db.")
            else:
                print("Tables already exist in recommendation_db.")
        except Exception as e:
            print(f"Error checking/creating tables: {e}")
            print("Ensure recommendation_db is reachable and credentials are correct.")

    app.run(host='0.0.0.0', port=5002, debug=True)