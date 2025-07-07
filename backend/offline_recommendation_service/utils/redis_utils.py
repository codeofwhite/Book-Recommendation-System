# utils/redis_utils.py
import redis
import json
import logging
import traceback # 用于打印详细的错误堆栈
from config import Config # 确保正确导入 Config

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

    # 重命名并修改此方法以匹配 trainer.py 中的调用
    def store_user_recommendations(self, user_id: str, recommendations: list, expire_time_seconds: int = None):
        """
        将用户的推荐列表存储到 Redis。
        Key: `recommendations:user:{user_id}` (与 trainer.py 中保持一致)
        Value: JSON 格式的推荐列表 (可以是包含字典的列表)
        expire_time_seconds: 可选，推荐结果的过期时间（秒）
        """
        if self.client is None:
            logging.error("Redis client is not initialized. Cannot store recommendations.")
            return

        try:
            # 确保 user_id 是字符串，以匹配 key 的格式
            key = f"recommendations:user:{user_id}" 
            # 将推荐列表（可能包含字典）序列化为 JSON 字符串
            # ensure_ascii=False 以便正确存储中文字符
            value = json.dumps(recommendations, ensure_ascii=False) 

            if expire_time_seconds is None:
                # 默认从 Config 中获取过期时间
                expire_time_seconds = getattr(Config, 'RECOMMENDATION_CACHE_EXPIRE_SECONDS', 3600 * 24)
            
            # 使用 setex 设置键值并设置过期时间
            self.client.setex(key, expire_time_seconds, value)
            logging.debug(f"Stored {len(recommendations)} recommendations for user {user_id} in Redis. Expire in {expire_time_seconds} seconds.")
        except Exception as e:
            logging.error(f"Error storing recommendations for user {user_id} in Redis: {e}")
            logging.error(traceback.format_exc()) # 打印详细堆栈

    def get_user_recommendations(self, user_id: str):
        """
        从 Redis 获取用户的推荐列表。
        """
        if self.client is None:
            logging.error("Redis client is not initialized. Cannot get recommendations.")
            return []
        
        try:
            key = f"recommendations:user:{user_id}"
            value = self.client.get(key)
            if value:
                # 将获取到的 JSON 字符串反序列化为 Python 列表
                return json.loads(value)
            return [] # 如果没有找到，返回空列表
        except Exception as e:
            logging.error(f"Error retrieving recommendations for user {user_id} from Redis: {e}")
            logging.error(traceback.format_exc())
            return []

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

# 如果你需要在本地单独测试这个文件，可以保留下面的 __main__ 块
# 但请确保 Config 能够被正确模拟或导入
if __name__ == '__main__':
    # 简单的测试用例
    # 注意：在实际运行前，请确保 config.py 中的 REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD 已正确配置
    # 并且 Redis 服务正在运行
    
    # 初始化日志
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # 模拟 Config 类以供独立测试
    class MockConfig:
        REDIS_HOST = 'localhost'
        REDIS_PORT = 6379
        REDIS_DB = 0
        REDIS_PASSWORD = '' # 如果没有密码，留空字符串
        RECOMMENDATION_CACHE_EXPIRE_SECONDS = 60 # 示例：60秒过期

    # 将 MockConfig 赋值给 Config，以便 RedisClient 可以使用
    # 在生产环境中，你会直接从真正的 config.py 导入
    from unittest.mock import patch
    with patch('config.Config', MockConfig):
        redis_client = RedisClient()
        
        if redis_client.ping():
            test_user_id = "user_test_1" # 建议使用字符串作为 user_id
            # 模拟推荐数据，现在可以是字典列表
            test_recommendations = [
                {"book_id": "book_A", "title": "Great Book A", "score": 0.95},
                {"book_id": "book_B", "title": "Interesting Read B", "score": 0.88}
            ]
            
            # 存储推荐
            redis_client.store_user_recommendations(test_user_id, test_recommendations, expire_time_seconds=300) # 5分钟过期
            
            # 获取推荐
            retrieved_recs = redis_client.get_user_recommendations(test_user_id)
            print(f"\nRetrieved recommendations for user {test_user_id}:")
            for rec in retrieved_recs:
                print(f"  - Book ID: {rec.get('book_id')}, Title: {rec.get('title')}, Score: {rec.get('score')}")
            
            # 测试不存在的用户
            non_existent_user = "user_non_existent"
            retrieved_empty = redis_client.get_user_recommendations(non_existent_user)
            print(f"\nRetrieved recommendations for non-existent user {non_existent_user}: {retrieved_empty}")
        else:
            print("Redis connection failed, cannot run test.")