# user_profile_service/app.py

import os
from flask import Flask
from flask_cors import CORS
from models import db  
from routes.book_engagement import book_engagement_bp 
from routes.review_engagement import review_engagement_bp 
from routes.review_content import review_content_bp  
from routes.review_admin_routes import review_bp  

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "mysql+pymysql://root:your_mysql_password@localhost/book_engagement"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# --- 注册蓝图 ---
app.register_blueprint(book_engagement_bp)
app.register_blueprint(review_engagement_bp)
app.register_blueprint(review_content_bp)  
app.register_blueprint(review_bp)  


# --- Database Initialization (Run once to create tables) ---
@app.cli.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    with app.app_context():  # 在应用上下文中执行数据库操作
        db.drop_all()
        db.create_all()
        print(
            "Initialized the database for book favorites, review favorites, book likes, and review likes."
        )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # 扫描 models.py 中的所有模型，创建对应表

    app.run(host="0.0.0.0", debug=True, port=5003)
