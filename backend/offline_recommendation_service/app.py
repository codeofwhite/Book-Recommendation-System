from flask import Flask, jsonify, request
import requests
from utils.redis_utils import RedisClient
from models.trainer import RecommendationTrainer
import threading
import time
from config import Config
# import schedule # <--- 暂时注释掉 schedule
import traceback
from data.data_loader import DataLoader # 确保导入路径正确

app = Flask(__name__)
redis_client = RedisClient()

# 检查 Redis 连接
if not redis_client.ping():
    print("Error: Could not connect to Redis. Recommendations might not be available.")

def run_offline_training_job():
    """
    运行离线推荐模型训练和生成任务。
    通常在后台或作为定时任务执行。
    """
    print("--- Starting offline recommendation job ---")
    try:
        # 实例化 RecommendationTrainer
        trainer = RecommendationTrainer()

        # 尝试训练模型
        print("Attempting to train model...")
        trainer.train_model()
        print("Model training attempt completed.")

        # 尝试生成推荐
        print("Attempting to generate recommendations...")
        trainer.generate_recommendations()
        print("Recommendation generation attempt completed.")

        print("--- Offline recommendation job finished successfully ---")

    except Exception as e:
        # 捕获所有可能的异常，并打印详细的错误信息和堆栈跟踪
        print(f"--- ERROR in offline recommendation job: {e} ---")
        print(traceback.format_exc()) # 打印完整的错误堆栈
        print("--- Offline recommendation job terminated with errors ---")

# def schedule_offline_job(): # <--- 暂时注释掉定时任务函数
#     """设置定时任务来运行离线推荐计算"""
#     print(f"Scheduling offline recommendation job to run at {Config.OFFLINE_CRON_SCHEDULE} daily.")
#     try:
#         cron_parts = Config.OFFLINE_CRON_SCHEDULE.split()
#         if len(cron_parts) >= 2:
#             schedule_hour = cron_parts[1]
#             schedule_minute = cron_parts[0]
#             schedule_time_str = f"{schedule_hour}:{schedule_minute}"
#             print(f"Parsed schedule time: {schedule_time_str}")
#             schedule.every().day.at(schedule_time_str).do(run_offline_training_job)
#         else:
#             print(f"Warning: OFFLINE_CRON_SCHEDULE format '{Config.OFFLINE_CRON_SCHEDULE}' is not as expected. Skipping daily scheduling.")
#             schedule.every(1).minutes.do(run_offline_training_job) # 默认设置为每分钟检查一次，方便调试

#     except Exception as e:
#         print(f"Error parsing OFFLINE_CRON_SCHEDULE: {e}")
#         print(traceback.format_exc())
#         print("Defaulting to schedule every 1 minute for debugging.")
#         schedule.every(1).minutes.do(run_offline_training_job) # 兜底，每分钟运行一次方便调试

#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# Define your Service B URL, just like you did for real-time recommendations
# Ensure this matches your Docker Compose service name (e.g., 'book_manage')
SERVICE_B_BASE_URL = "http://book_manage:5001" 

@app.route('/recommend/user/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """
    获取指定用户的推荐图书列表，并补充图书详情。
    """
    # Assuming redis_client.get_user_recommendations(user_id) returns a list of dicts like:
    # [{"book_id": "...", "score": ...}, ...]
    raw_recommendations = redis_client.get_user_recommendations(user_id) # This comes from your Redis client wrapper

    if not raw_recommendations:
        return jsonify({
            "user_id": user_id,
            "recommendations": [],
            "message": "No recommendations found for this user, or offline job not yet run."
        }), 404

    detailed_recommendations = []
    for rec_item in raw_recommendations:
        book_id = rec_item.get('book_id')
        if not book_id:
            continue # Skip if book_id is missing

        try:
            # Call Service B to get book details
            book_details_url = f"{SERVICE_B_BASE_URL}/api/books/{book_id}"
            print(f"Attempting to fetch details for offline recommendation: {book_details_url}") # Debug print
            response = requests.get(book_details_url)

            if response.status_code == 200:
                book_data = response.json()
                print(f"Successfully fetched book data for {book_id} (offline): {book_data}") # Debug print
                
                # Combine recommendation score with detailed book info
                detailed_rec = {
                    "bookId": book_data.get("bookId"), # Ensure it's 'bookId' for frontend
                    "title": book_data.get("title"),
                    "author": book_data.get("author"),
                    "coverImg": book_data.get("coverImg"),
                    "score": rec_item.get("score") # Keep the recommendation score
                }
                detailed_recommendations.append(detailed_rec)
            else:
                print(f"Failed to fetch details for book_id {book_id} (offline): Status {response.status_code}, Response: {response.text}")
                # Fallback if details fetching fails
                detailed_recommendations.append({
                    "bookId": book_id,
                    "title": rec_item.get('title', '未知标题'),
                    "author": "未知作者",
                    "coverImg": "https://via.placeholder.com/150",
                    "score": rec_item.get("score")
                })
        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for book_id {book_id} (offline): {e}")
            # Fallback if connection fails
            detailed_recommendations.append({
                "bookId": book_id,
                "title": rec_item.get('title', '未知标题'),
                "author": "未知作者",
                "coverImg": "https://via.placeholder.com/150",
                "score": rec_item.get("score")
            })

    return jsonify({
        "user_id": user_id,
        "recommendations": detailed_recommendations,
        "message": "Recommendations retrieved successfully."
    }), 200

@app.route('/recommend/trigger_offline_job', methods=['POST'])
def trigger_offline_job():
    """
    手动触发离线推荐计算（仅用于开发/测试环境）
    生产环境应由定时任务或CI/CD流程触发
    """
    print("Received request to trigger offline job. Starting new thread...")
    thread = threading.Thread(target=run_offline_training_job)
    thread.daemon = True
    thread.start()
    print("Offline job thread started.")
    return jsonify({"message": "Offline recommendation job triggered in background."}), 202

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    redis_status = redis_client.ping()
    status = "healthy" if redis_status else "unhealthy (Redis)"
    return jsonify({"status": status, "redis_connected": redis_status}), 200

# --- 新增的接口用于测试 ClickHouse 数据加载 ---
@app.route('/data/user_behavior_logs', methods=['GET'])
def get_user_behavior_logs_data():
    """
    从 ClickHouse 加载用户行为日志数据并返回。
    此接口仅用于调试和验证数据加载。
    """
    print("Received request to load user behavior logs from ClickHouse...")
    try:
        loader = DataLoader()
        df = loader.load_user_behavior_logs()

        if not df.empty:
            return jsonify({
                "status": "success",
                "message": f"Successfully loaded {len(df)} user behavior logs from ClickHouse.",
                "data": df.to_dict(orient='records')
            }), 200
        else:
            return jsonify({
                "status": "warning",
                "message": "No user behavior logs found in ClickHouse or query returned no data.",
                "data": []
            }), 200
    except Exception as e:
        print(f"Error loading user behavior logs from ClickHouse: {e}")
        print(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": "Failed to load user behavior logs from ClickHouse.",
            "error": str(e),
            "traceback": traceback.format_exc().splitlines() # 返回堆栈跟踪的每一行
        }), 500

if __name__ == '__main__':
    # 在 Flask 应用启动时，在单独的线程中启动离线计算的定时任务
    # offline_scheduler_thread = threading.Thread(target=schedule_offline_job) # <--- 暂时注释掉
    # offline_scheduler_thread.daemon = True
    # offline_scheduler_thread.start() # <--- 暂时注释掉

    app.run(host='0.0.0.0', port=5005, debug=True)