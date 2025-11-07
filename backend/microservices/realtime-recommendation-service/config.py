# config.py

class Config:
    # ... (其他现有配置) ...

    # Redis Keys
    REDIS_RECOMMENDATIONS_KEY_PREFIX = "user_recommendations:" # 离线推荐存储的 Key 前缀
    REDIS_RECENT_VIEWS_KEY_PREFIX = "user_recent_views:"      # 用户最近浏览存储的 Key 前缀

    # 实时修正相关配置
    RECENT_VIEWS_WEIGHT = 0.8 # 实时浏览过的图书的相似图书的提升权重 (0-1)
    MAX_RECENT_VIEWS_TO_CONSIDER = 10 # 考虑最近浏览的图书数量
    EXCLUDE_RECENTLY_VIEWED = True # 是否在实时推荐中排除用户最近浏览过的图书