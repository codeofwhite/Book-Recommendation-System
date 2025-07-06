# config.py
import os

class Config:
    # --- MySQL/通用数据库配置 (保留现有，以防其他部分仍需) ---
    REC_DB_HOST = os.getenv("REC_DB_HOST", "recommendation_db")
    REC_DB_USER = os.getenv("REC_DB_USER", "rec_user")
    REC_DB_PASSWORD = os.getenv("REC_DB_PASSWORD", "rec_password")
    REC_DB_NAME = os.getenv("REC_DB_NAME", "recommendation_db")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{REC_DB_USER}:{REC_DB_PASSWORD}@{REC_DB_HOST}:3306/{REC_DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- ClickHouse 数据库配置 (新增) ---
    CH_HOST = os.getenv("CH_HOST", "clickhouse") # 你的ClickHouse服务地址
    CH_PORT = int(os.getenv("CH_PORT", 8123)) # ClickHouse HTTP 端口，通常是8123
    CH_USER = os.getenv("CH_USER", "default")
    CH_PASSWORD = os.getenv("CH_PASSWORD", "") # 如果有密码，请设置
    CH_DB_NAME = os.getenv("CH_DB_NAME", "default") # 你的数据库名

    # ClickHouse SQLAlchemy 连接 URI
    # 'clickhouse://user:password@host:port/database'
    CLICKHOUSE_DATABASE_URI = (
        f"clickhouse://{CH_USER}:{CH_PASSWORD}@{CH_HOST}:{CH_PORT}/{CH_DB_NAME}"
    )

    # --- Redis 配置 (重点修改) ---
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    # ---> 新增或修改：添加 REDIS_PASSWORD <---
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "") # 如果Redis没有密码，设置为空字符串 ''
                                                     # 如果有密码，请替换为你的实际密码
    # ---> 新增：推荐结果缓存过期时间 <---
    RECOMMENDATION_CACHE_EXPIRE_SECONDS = 3600 * 24 # 推荐结果在 Redis 中缓存一天 (秒)

    # --- 推荐系统相关配置 (不变) ---
    TOP_N_RECOMMENDATIONS = 100
    
    # 协同过滤与流行度混合的权重
    # alpha 越大，越偏向协同过滤；alpha 越小，越偏向流行度
    # 0.7 是一个常用起点，可以根据实际效果调整
    CF_POPULARITY_MIX_ALPHA = 0.7 
    
    # 当协同过滤（或混合推荐）生成的推荐数量不足 TOP_N_RECOMMENDATIONS 时，
    # 是否补充热门图书直到达到 N
    FALLBACK_TO_POPULAR_IF_LESS_THAN_N_CF_RECS = True

    # 新增：协同过滤相似度与内容相似度融合的权重
    # 0.5 表示各占一半，可以根据数据量和内容丰富度调整
    # 如果交互数据极度稀疏，可以适当提高内容相似度的权重（SIMILARITY_FUSION_ALPHA < 0.5）
    SIMILARITY_FUSION_ALPHA = 0.5 
    
    OFFLINE_CRON_SCHEDULE = "0 2 * * *"