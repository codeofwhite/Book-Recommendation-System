# config.py
import os

class Config:
    MONGO_HOST = os.getenv('MONGO_HOST', 'book_db_mongo')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_USER = os.getenv('MONGO_USER', 'book_user')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'book_password')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'book_manage_db')
    CSV_FILEPATH = "data/books.csv" # 假设CSV文件在项目的根目录