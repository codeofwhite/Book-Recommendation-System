# config.py
import os

class Config:
    # Deep & Wide 模型配置【小数据黄金超参，无脑用】
    EMBEDDING_DIM = 16          # 从32→16，小样本必改，防止过拟合
    DEEP_LAYER_DIMS = [32, 16]  # 从64,32→32,16，轻量化网络，学核心特征
    TRAIN_EPOCHS = 80           # 从120→80，训够为止，不训到过拟合
    BATCH_SIZE = 32             # 从64→32，小批次训练更稳
    LEARNING_RATE = 0.001       # 从0.0006→0.001，收敛速度适中，不磨洋工
    
    # --- MySQL 数据库配置 ---
    REC_DB_HOST = os.getenv("REC_DB_HOST", "recommendation_db")
    REC_DB_USER = os.getenv("REC_DB_USER", "rec_user")
    REC_DB_PASSWORD = os.getenv("REC_DB_PASSWORD", "rec_password")
    REC_DB_NAME = os.getenv("REC_DB_NAME", "recommendation_db")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{REC_DB_USER}:{REC_DB_PASSWORD}@{REC_DB_HOST}:3306/{REC_DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- ClickHouse 数据库配置 ---
    CH_HOST = os.getenv("CH_HOST", "clickhouse_db") 
    CH_PORT = int(os.getenv("CH_PORT", 8123)) 
    CH_USER = os.getenv("CH_USER", "default")
    CH_PASSWORD = os.getenv("CH_PASSWORD", "") 
    CH_DB_NAME = os.getenv("CH_DB_NAME", "default") 

    # ClickHouse SQLAlchemy 连接 URI
    CLICKHOUSE_DATABASE_URI = (
        f"clickhouse://{CH_USER}:{CH_PASSWORD}@{CH_HOST}:{CH_PORT}/{CH_DB_NAME}"
    )

    # --- Redis 配置 ---
    REDIS_HOST = os.getenv("REDIS_HOST", "redis_cache")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "") 
    RECOMMENDATION_CACHE_EXPIRE_SECONDS = 3600 * 24 # 推荐结果在 Redis 中缓存一天 (秒)

    # Redis Key 前缀
    REDIS_RECOMMENDATIONS_PREFIX = "recommendations:user:" # 离线推荐结果
    REDIS_BOOK_FEATURES_PREFIX = "book_features:" # 物品特征向量
    REDIS_USER_PROFILE_PREFIX = "user_profile:" # 离线用户画像向量
    REDIS_REALTIME_UPDATED_RECOMMENDATIONS_PREFIX = "realtime_updated_recommendations:user:" # Flink 实时更新后的推荐列表
    REDIS_USER_RECENT_VIEWS_HASH_KEY = "user_recent_views_hash:" # Flink 存储用户最近浏览的 hash key

    TOP_N_RECOMMENDATIONS = 200 # 每个用户推荐的书籍数量
    
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
    
    # 物品特征向量的维度 (假设 TF-IDF 向量的维度)
    # 实际维度会根据语料库的词汇量动态变化，但可以取一个上限或通过 tfidf_vectorizer.vocabulary_size 来获取
    # 这个值在 TF-IDF 的情况下其实是词汇表的大小，在实际使用时可能需要动态获取
    # 这里只是一个占位符，如果模型输出是固定维度的嵌入，这个就很重要
    # For TF-IDF, it's typically derived from the vocabulary size after fitting
    ITEM_EMBEDDING_DIMENSION = 20000 

    # Deep & Wide 模型相关配置
    EMBEDDING_DIM = 16
    DEEP_HIDDEN_UNITS = [128, 64, 32]
    BATCH_SIZE = 256
    EPOCHS = 10
    LEARNING_RATE = 0.001
    MODEL_SAVE_PATH = "./deep_wide_model_pytorch.pt"  # PyTorch模型后缀用.pt