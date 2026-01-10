# offline_precompute_similar_books.py
import redis
import json
import os

redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    password=os.getenv("REDIS_PASSWORD", ""),
    decode_responses=True
)

def precompute_similar_books():
    # 这里替换为你的相似图书计算逻辑（比如基于图书标签/分类/内容向量）
    # 示例：模拟数据
    book_similar_data = {
        "1001": ["1002", "1003", "1004", "1005"],
        "1002": ["1001", "1006", "1007", "1008"]
    }
    for book_id, similar_books in book_similar_data.items():
        redis_client.set(
            f"book_similar:{book_id}",
            json.dumps(similar_books, ensure_ascii=False)
        )
    print("Similar books precomputed successfully")

if __name__ == "__main__":
    precompute_similar_books()