import os

class Config:
    # 数据库配置 (从你的实时同步目标数据库获取数据)
    REC_DB_HOST = os.getenv("REC_DB_HOST", "recommendation_db")
    REC_DB_USER = os.getenv("REC_DB_USER", "rec_user")
    REC_DB_PASSWORD = os.getenv("REC_DB_PASSWORD", "rec_password")
    REC_DB_NAME = os.getenv("REC_DB_NAME", "recommendation_db")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{REC_DB_USER}:{REC_DB_PASSWORD}@{REC_DB_HOST}:3306/{REC_DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis 配置 (存储推荐结果)
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    # 推荐系统相关配置
    TOP_N_RECOMMENDATIONS = 100 # 每个用户推荐多少个物品
    OFFLINE_CRON_SCHEDULE = "0 2 * * *" # 每天凌晨2点运行离线计算 (Crontab 格式)