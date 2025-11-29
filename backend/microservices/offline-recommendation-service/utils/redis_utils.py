import pandas as pd
import redis
import json
import logging
import traceback # 用于打印详细的错误堆栈
from config import Config # 确保正确导入 Config

# 配置日志，设置为 INFO 级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RedisClient:
    def __init__(self):
        self.client = None # 初始化为 None
        try:
            self.client = redis.StrictRedis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                password=Config.REDIS_PASSWORD, # 从 Config 获取密码
                decode_responses=True # 自动解码为字符串
            )
            self.client.ping() # 尝试连接一次，如果失败会抛出异常
            logging.info("Successfully connected to Redis!")
        except redis.exceptions.ConnectionError as e:
            logging.error(f"Error connecting to Redis: {e}")
            logging.error(traceback.format_exc()) # 打印详细堆栈
            self.client = None # 连接失败时确保客户端为 None
        except Exception as e:
            logging.error(f"An unexpected error occurred during Redis client initialization: {e}")
            logging.error(traceback.format_exc())
            self.client = None

    def get_pipeline(self):
        """获取 Redis pipeline 以便批量操作。"""
        if self.client:
            return self.client.pipeline()
        logging.error("Redis client is not initialized. Cannot get pipeline.")
        return None

    def store_user_recommendations(self, user_id: str, recommendations: list, expire_time_seconds: int = None):
        """
        将用户的推荐列表存储到 Redis。
        Key: `recommendations:user:{user_id}` (与 trainer.py 中保持一致)
        Value: JSON 格式的推荐列表 (可以是包含字典的列表)
        expire_time_seconds: 可选，推荐结果的过期时间（秒）
        """
        if self.client is None:
            logging.error("Redis client is not initialized. Cannot store recommendations.")
            return False

        try:
            # 确保 user_id 是字符串，以匹配 key 的格式
            # 使用 Config.REDIS_RECOMMENDATIONS_PREFIX
            key = f"{Config.REDIS_RECOMMENDATIONS_PREFIX}{user_id}" 
            # 将推荐列表（可能包含字典）序列化为 JSON 字符串
            # ensure_ascii=False 以便正确存储中文字符
            # 检查 recommendations 是否是 Pandas Series，并将其转换为 list
            if isinstance(recommendations, pd.Series):
                data_to_store = recommendations.tolist()
            else:
                data_to_store = recommendations
                
            value = json.dumps(data_to_store, ensure_ascii=False)

            if expire_time_seconds is None:
                # 默认从 Config 中获取过期时间，使用 OFFLINE_RECOMMENDATION_CACHE_EXPIRE_SECONDS
                expire_time_seconds = getattr(Config, 'OFFLINE_RECOMMENDATION_CACHE_EXPIRE_SECONDS', 3600 * 24)
            
            # 使用 setex 设置键值并设置过期时间
            self.client.setex(key, expire_time_seconds, value)
            logging.debug(f"Stored {len(recommendations)} recommendations for user {user_id} in Redis. Key: {key}, Expire in {expire_time_seconds} seconds.")
            return True
        except Exception as e:
            logging.error(f"Error storing recommendations for user {user_id} in Redis: {e}")
            logging.error(traceback.format_exc()) # 打印详细堆栈
            return False

    def get_user_recommendations(self, user_id: str):
        """
        从 Redis 获取用户的推荐列表。
        """
        if self.client is None:
            logging.error("Redis client is not initialized. Cannot get recommendations.")
            return []
        
        try:
            # 使用 Config.REDIS_RECOMMENDATIONS_PREFIX
            key = f"{Config.REDIS_RECOMMENDATIONS_PREFIX}{user_id}"
            value = self.client.get(key)
            if value:
                # 将获取到的 JSON 字符串反序列化为 Python 列表
                return json.loads(value)
            return [] # 如果没有找到，返回空列表
        except Exception as e:
            logging.error(f"Error retrieving recommendations for user {user_id} from Redis: {e}")
            logging.error(traceback.format_exc())
            return []

    def store_book_feature_vector(self, book_id: str, vector: list):
        """存储单个物品特征向量到 Redis。"""
        if not self.client:
            logging.error("Redis client not connected. Cannot store book feature vector.")
            return False
        key = f"{Config.REDIS_BOOK_FEATURES_PREFIX}{book_id}"
        try:
            self.client.set(key, json.dumps(vector))
            logging.debug(f"Stored feature vector for book {book_id}.")
            return True
        except Exception as e:
            logging.error(f"Error storing feature vector for book {book_id}: {e}")
            logging.error(traceback.format_exc())
            return False

    def get_book_feature_vector(self, book_id: str):
        """从 Redis 获取单个物品特征向量。"""
        if not self.client:
            logging.error("Redis client not connected. Cannot get book feature vector.")
            return None
        key = f"{Config.REDIS_BOOK_FEATURES_PREFIX}{book_id}"
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logging.error(f"Error retrieving feature vector for book {book_id}: {e}")
            logging.error(traceback.format_exc())
            return None

    def store_user_profile_vector(self, user_id: str, vector: list):
        """存储用户画像向量到 Redis。"""
        if not self.client:
            logging.error("Redis client not connected. Cannot store user profile vector.")
            return False
        key = f"{Config.REDIS_USER_PROFILE_PREFIX}{user_id}"
        try:
            self.client.set(key, json.dumps(vector))
            logging.debug(f"Stored user profile vector for user {user_id}.")
            return True
        except Exception as e:
            logging.error(f"Error storing user profile for user {user_id}: {e}")
            logging.error(traceback.format_exc())
            return False

    def get_user_profile_vector(self, user_id: str):
        """从 Redis 获取用户画像向量。"""
        if not self.client:
            logging.error("Redis client not connected. Cannot get user profile vector.")
            return None
        key = f"{Config.REDIS_USER_PROFILE_PREFIX}{user_id}"
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logging.error(f"Error retrieving user profile for user {user_id}: {e}")
            logging.error(traceback.format_exc())
            return None

    def ping(self):
        """测试Redis连接，现在在 __init__ 中已经做了初步测试，这里主要用于外部调用检查"""
        if self.client is None:
            logging.warning("Redis client is not initialized. Ping failed.")
            return False
        try:
            self.client.ping()
            logging.info("Redis connection is active.")
            return True
        except redis.exceptions.ConnectionError as e:
            logging.error(f"Redis connection lost: {e}")
            logging.error(traceback.format_exc())
            self.client = None # 连接断开后将客户端设为 None
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred during Redis ping: {e}")
            logging.error(traceback.format_exc())
            return False

