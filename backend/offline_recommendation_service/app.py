from flask import Flask, jsonify, request
from utils.redis_utils import RedisClient
from models.trainer import RecommendationTrainer
import threading
import time
from config import Config
import schedule
import traceback # 导入 traceback 模块用于打印完整的错误堆栈

app = Flask(__name__)
redis_client = RedisClient()

# 检查 Redis 连接
# 这里的打印会在 Flask 应用启动时执行
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

def schedule_offline_job():
    """设置定时任务来运行离线推荐计算"""
    print(f"Scheduling offline recommendation job to run at {Config.OFFLINE_CRON_SCHEDULE} daily.")
    # 确保 OFFLINE_CRON_SCHEDULE 格式正确，例如 "0 2 * * *"
    # 这里的 split()[-2] 和 split()[-3] 假设格式是 "minute hour * * *"
    # 如果你的格式是 "hour:minute"，需要调整解析逻辑
    try:
        cron_parts = Config.OFFLINE_CRON_SCHEDULE.split()
        if len(cron_parts) >= 2:
            schedule_hour = cron_parts[1] # 小时
            schedule_minute = cron_parts[0] # 分钟
            schedule_time_str = f"{schedule_hour}:{schedule_minute}"
            print(f"Parsed schedule time: {schedule_time_str}")
            schedule.every().day.at(schedule_time_str).do(run_offline_training_job)
        else:
            print(f"Warning: OFFLINE_CRON_SCHEDULE format '{Config.OFFLINE_CRON_SCHEDULE}' is not as expected. Skipping daily scheduling.")
            # 默认设置为每分钟检查一次，方便调试
            schedule.every(1).minutes.do(run_offline_training_job)

    except Exception as e:
        print(f"Error parsing OFFLINE_CRON_SCHEDULE: {e}")
        print(traceback.format_exc())
        print("Defaulting to schedule every 1 minute for debugging.")
        schedule.every(1).minutes.do(run_offline_training_job) # 兜底，每分钟运行一次方便调试

    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/recommend/user/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """
    获取指定用户的推荐图书列表
    """
    recommendations = redis_client.get_user_recommendations(user_id)
    if recommendations:
        return jsonify({
            "user_id": user_id,
            "recommendations": recommendations,
            "message": "Recommendations retrieved successfully."
        }), 200
    else:
        return jsonify({
            "user_id": user_id,
            "recommendations": [],
            "message": "No recommendations found for this user, or offline job not yet run."
        }), 404

@app.route('/recommend/trigger_offline_job', methods=['POST'])
def trigger_offline_job():
    """
    手动触发离线推荐计算（仅用于开发/测试环境）
    生产环境应由定时任务或CI/CD流程触发
    """
    # 避免重复触发，可以在生产环境加入权限验证
    print("Received request to trigger offline job. Starting new thread...")
    thread = threading.Thread(target=run_offline_training_job)
    thread.daemon = True # 确保线程在主程序退出时也能退出
    thread.start()
    print("Offline job thread started.")
    return jsonify({"message": "Offline recommendation job triggered in background."}), 202

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    redis_status = redis_client.ping()
    status = "healthy" if redis_status else "unhealthy (Redis)"
    return jsonify({"status": status, "redis_connected": redis_status}), 200

if __name__ == '__main__':
    # 在 Flask 应用启动时，在单独的线程中启动离线计算的定时任务
    offline_scheduler_thread = threading.Thread(target=schedule_offline_job)
    offline_scheduler_thread.daemon = True
    offline_scheduler_thread.start()

    app.run(host='0.0.0.0', port=5005, debug=True)