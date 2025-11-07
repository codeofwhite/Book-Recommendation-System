# config.py
import os

class Config:
    MONGO_HOST = os.getenv('MONGO_HOST', 'book_db_mongo')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_USER = os.getenv('MONGO_USER', 'book_user')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'book_password')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'book_manage_db')
    CSV_FILEPATH = "data/books.csv" # 假设CSV文件在项目的根目录
    
    # CSV 文件路径
    CSV_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'books.csv')

    # MinIO 配置 (新增)
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000') # 注意：本地开发时可能是 localhost:9000
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'epub-books') # 与 docker-compose.yml 保持一致
    MINIO_SECURE = False # 开发环境通常为 False (http)，生产环境可能为 True (https)