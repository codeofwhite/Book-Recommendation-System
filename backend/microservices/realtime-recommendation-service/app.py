import os
import json
from flask import Flask, jsonify, request
import redis
import requests

app = Flask(__name__)

# --- Redis 配置 ---
# 从环境变量获取 Redis 连接信息
# REDIS_HOST 应该与 docker-compose.yaml 中 Redis 服务的名称一致
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

redis_client = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)

# 全局 Redis 客户端对象
r = None

def setup_redis_client():
    """
    初始化 Redis 客户端。
    这个函数会在 Flask 应用启动时被调用一次。
    """
    global r
    try:
        # decode_responses=True 会自动将 Redis 返回的字节数据解码为字符串
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        # 尝试执行一个简单的命令来测试连接
        r.ping()
        print(f"成功连接到 Redis: {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"连接 Redis 失败: {e}")
        r = None

# --- Flask 路由 ---

@app.route('/')
def home():
    """
    根路径欢迎信息。
    """
    return "欢迎来到 Redis 数据查看器！请访问 /redis/all_recent_views 或 /redis/recent_views/<user_id>"

@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口，检查 Redis 连接。
    """
    if r:
        try:
            r.ping()
            return jsonify({"status": "UP", "redis": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "DOWN", "redis": "disconnected", "error": str(e)}), 500
    else:
        return jsonify({"status": "DOWN", "redis": "not initialized"}), 500

@app.route('/redis/all_recent_views', methods=['GET'])
def get_all_recent_views():
    """
    从 Redis 的 'user_recent_views' 哈希表中获取所有用户的最近浏览记录。
    """
    if not r:
        return jsonify({"error": "Redis 未初始化或连接失败"}), 500
    
    try:
        # HGETALL 返回哈希表中所有字段和值
        # 由于 decode_responses=True，这里的 user_id 和 views_json 已经是字符串
        all_views_raw = r.hgetall('user_recent_views')
        
        if not all_views_raw:
            return jsonify({"message": "Redis 中 'user_recent_views' 为空或无数据。"}), 200
        
        all_views_parsed = {}
        for user_id, views_json in all_views_raw.items():
            try:
                # 将 JSON 字符串解析为 Python 列表
                all_views_parsed[user_id] = json.loads(views_json)
            except json.JSONDecodeError:
                print(f"警告: 用户 '{user_id}' 的 JSON 解码失败。原始数据: {views_json}")
                all_views_parsed[user_id] = views_json # 返回原始数据以便调试
        
        return jsonify({"message": "成功获取所有用户最近浏览数据", "data": all_views_parsed}), 200

    except Exception as e:
        print(f"从 Redis 获取所有最近浏览数据时出错: {e}")
        return jsonify({"error": "获取数据失败", "details": str(e)}), 500

@app.route('/redis/recent_views/<user_id>', methods=['GET'])
def get_user_recent_views(user_id):
    """
    从 Redis 的 'user_recent_views' 哈希表中获取特定用户的最近浏览记录。
    """
    if not r:
        return jsonify({"error": "Redis 未初始化或连接失败"}), 500
    
    try:
        # HGET 获取哈希表中指定字段的值
        # 由于 decode_responses=True，这里的 views_json 已经是字符串
        views_json = r.hget('user_recent_views', user_id)
        
        if not views_json:
            return jsonify({"message": f"用户 '{user_id}' 在 Redis 中没有最近浏览记录。"}), 200
        
        try:
            views_list = json.loads(views_json)
        except json.JSONDecodeError:
            print(f"警告: 用户 '{user_id}' 的 JSON 解码失败。原始数据: {views_json}")
            views_list = views_json # 返回原始数据以便调试
            
        return jsonify({"message": f"成功获取用户 '{user_id}' 的最近浏览数据", "user_id": user_id, "recent_views": views_list}), 200

    except Exception as e:
        print(f"从 Redis 获取用户 '{user_id}' 最近浏览数据时出错: {e}")
        return jsonify({"error": "获取数据失败", "details": str(e)}), 500

# 新增路由：获取所有用户的实时更新推荐
@app.route('/redis/all_realtime_updated_recommendations', methods=['GET'])
def get_all_realtime_updated_recommendations():
    """
    从 Redis 中获取所有用户由 Flink 实时更新后的推荐列表。
    这些数据由 Flink Job 写入，键以 'realtime_recs:user:' 开头。
    """
    if not r:
        return jsonify({"error": "Redis 未初始化或连接失败"}), 500
    
    try:
        # 使用 SCAN 命令迭代所有匹配 'realtime_updated_recommendations:user:*' 的键
        # 注意：这里不能用 HGETALL，因为 Flink 是用 SETEX 存储每个用户的推荐，而不是哈希表
        all_recs_parsed = {}
        # scan_iter 允许我们安全地迭代大量键
        for key in r.scan_iter("realtime_updated_recommendations:user:*"):
            # Redis 的 key 是字节串，decode_responses=True 应该已经处理
            # 确保 key 是字符串，并从中提取 user_id
            user_id = key.split(':')[-1] 
            value = r.get(key)
            if value:
                try:
                    # 将获取到的 JSON 字符串反序列化为 Python 列表
                    all_recs_parsed[user_id] = json.loads(value)
                except json.JSONDecodeError:
                    print(f"警告: 键 '{key}' 的 JSON 解码失败。原始数据: {value}")
                    # 如果解码失败，返回原始数据以便调试
                    all_recs_parsed[user_id] = value 
            
        if not all_recs_parsed:
            return jsonify({"message": "Redis 中没有实时更新的推荐数据。"}), 200
        
        return jsonify({"message": "成功获取所有用户实时更新的推荐数据", "data": all_recs_parsed}), 200

    except Exception as e:
        print(f"从 Redis 获取所有实时更新推荐数据时出错: {e}")
        return jsonify({"error": "获取数据失败", "details": str(e)}), 500

# 【重点】定义你的书籍服务（service-b）的URL。请根据你的实际部署修改。
SERVICE_B_BASE_URL = "http://book_manage:5001" 

@app.route('/realtime_updated_recommendations/<user_id>', methods=['GET'])
def get_realtime_recommendations(user_id):
    redis_key = f"realtime_updated_recommendations:user:{user_id}"
    recommendations_data_str = redis_client.get(redis_key)

    if not recommendations_data_str:
        return jsonify({"message": "Redis 中没有实时更新的推荐数据。", "recommendations": []}), 200

    # Redis 中存储的原始推荐数据，例如： [{"book_id": "...", "score": ...}]
    raw_recommendations_list = json.loads(recommendations_data_str)

    detailed_recommendations = []
    for rec_item in raw_recommendations_list:
        # 从原始推荐数据中获取 book_id (Redis可能存储的是book_id, 但前端需要bookId)
        book_id = rec_item.get('book_id')
        if not book_id: # 检查是否存在 book_id
            continue # 如果没有 book_id，跳过此项

        try:
            # 调用 service-b 的书籍详情接口
            book_details_url = f"{SERVICE_B_BASE_URL}/api/books/{book_id}"
            print(f"Attempting to fetch book details from: {book_details_url}") # 新增：打印正在请求的URL
            response = requests.get(book_details_url)

            if response.status_code == 200:
                # 【修正：先赋值，再打印】
                book_data = response.json()
                print(f"Successfully fetched book data for {book_id}: {book_data}") # 打印Service B返回的完整JSON
                # 整合推荐分数和书籍详情
                detailed_rec = {
                    "bookId": book_data.get("bookId"), # 确保使用 "bookId" 字段
                    "title": book_data.get("title"),
                    "author": book_data.get("author"), # 【新增】获取作者信息
                    "coverImg": book_data.get("coverImg"), # 【新增】获取封面图片信息
                    "score": rec_item.get("score") # 保留推荐分数
                }
                detailed_recommendations.append(detailed_rec)
            else:
                print(f"Failed to fetch details for book_id {book_id}: Status {response.status_code}, Response: {response.text}")
                # 如果获取详情失败，至少返回现有信息并提供默认值
                detailed_recommendations.append({
                    "bookId": book_id,
                    "title": rec_item.get('title', '未知标题'),
                    "author": "未知作者", # 默认作者
                    "coverImg": "https://via.placeholder.com/150", # 默认封面
                    "score": rec_item.get("score")
                })
        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for book_id {book_id}: {e}")
            # 如果请求本身失败，也提供默认值
            detailed_recommendations.append({
                "bookId": book_id,
                "title": rec_item.get('title', '未知标题'),
                "author": "未知作者",
                "coverImg": "https://via.placeholder.com/150",
                "score": rec_item.get("score")
            })

    return jsonify({
        "message": f"成功获取用户 '{user_id}' 的实时更新推荐数据",
        "recommendations": detailed_recommendations,
        "user_id": user_id
    })

# --- 应用启动 ---
if __name__ == '__main__':
    # 在应用运行之前调用 setup_redis_client 来初始化 Redis 客户端
    setup_redis_client()
    app.run(host='0.0.0.0', port=5004, debug=True)
