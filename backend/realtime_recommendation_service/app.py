import os
import json
from flask import Flask, jsonify, request
import redis

app = Flask(__name__)

# --- Redis 配置 ---
# 从环境变量获取 Redis 连接信息
# REDIS_HOST 应该与 docker-compose.yaml 中 Redis 服务的名称一致
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

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

# --- 应用启动 ---
if __name__ == '__main__':
    # 在应用运行之前调用 setup_redis_client 来初始化 Redis 客户端
    setup_redis_client()
    app.run(host='0.0.0.0', port=5004, debug=True)
