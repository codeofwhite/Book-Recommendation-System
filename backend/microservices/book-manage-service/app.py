# app.py
from flask import Flask
from flask_cors import CORS

# 导入我们的Blueprint和Model
from routes.book_routes import book_bp
from models.book_model import BookModel

app = Flask(__name__)
CORS(app)

# 将配置从Config类加载到Flask应用中（如果需要的话）
# app.config.from_object(Config)

# 注册Blueprint
app.register_blueprint(book_bp)

if __name__ == '__main__':
    # 在 Flask 应用启动前执行数据导入检查
    # 注意：这里调用的是BookModel中的类方法
    BookModel.initialize_db_and_data()
    app.run(host='0.0.0.0', port=5001, debug=True)