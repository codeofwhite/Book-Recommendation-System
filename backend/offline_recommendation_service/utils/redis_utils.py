import redis
import json
from config import Config

class RedisClient:
    def __init__(self):
        self.client = redis.StrictRedis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            decode_responses=True # 自动解码为字符串
        )

    def set_user_recommendations(self, user_id, book_ids):
        """
        存储用户推荐列表。
        Key: `user_rec:{user_id}`
        Value: JSON 格式的图书ID列表
        """
        key = f"user_rec:{user_id}"
        value = json.dumps(book_ids)
        self.client.set(key, value)
        # print(f"Stored recommendations for user {user_id}")

    def get_user_recommendations(self, user_id):
        """获取用户推荐列表"""
        key = f"user_rec:{user_id}"
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return []

    def ping(self):
        """测试Redis连接"""
        try:
            self.client.ping()
            print("Successfully connected to Redis!")
            return True
        except redis.exceptions.ConnectionError as e:
            print(f"Could not connect to Redis: {e}")
            return False

if __name__ == '__main__':
    # 简单测试
    redis_client = RedisClient()
    if redis_client.ping():
        test_user_id = 1
        test_books = ["book_id_101", "book_id_102", "book_id_103"]
        redis_client.set_user_recommendations(test_user_id, test_books)
        retrieved_books = redis_client.get_user_recommendations(test_user_id)
        print(f"Retrieved recommendations for user {test_user_id}: {retrieved_books}")