import os
from urllib.parse import quote_plus

class Config:
    # 数据库配置 - 现在从环境变量获取，在docker-compose中设置
    DB_USER = os.environ.get('DB_USER', 'cqu123')  # 默认使用普通用户
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    DB_HOST = os.environ.get('DB_HOST', 'mysql_db')  # 关键变化：使用服务名
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'book_app_db')
    
    # 安全地处理密码中的特殊字符
    encoded_password = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 修正拼写错误
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 5  # 添加连接超时
        }
    }

    # 密码哈希配置
    BCRYPT_LOG_ROUNDS = 13  # 推荐值，数字越大越安全，但计算时间越长

    # JWT 或其他安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key_that_you_should_change')
    # 生产环境应该设置为 True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', False)