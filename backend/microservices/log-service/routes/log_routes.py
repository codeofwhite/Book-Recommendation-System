# log_service/app.py (假设你的 Flask 日志服务文件)
import os
import json
from flask import Blueprint, request, jsonify
from kafka import KafkaProducer # <-- 新增

# 创建蓝图
log_bp = Blueprint('log', __name__)

# 定义日志文件路径（可选，作为备份或调试）
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'frontend_logs.jsonl')
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# 初始化 Kafka Producer
# 这里的 KAFKA_BROKER_URL 应该指向你的 Kafka 服务地址，例如 'kafka:29092'
# 可以在环境变量中配置
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL', 'kafka:29092') # 确保你的Docker Compose网络中Kafka是可达的
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER_URL],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

@log_bp.route('/api/log', methods=['POST'])
def receive_frontend_log():
    try:
        log_data = request.json
        if not log_data:
            return jsonify({"error": "No log data received"}), 400

        # **发送日志到 Kafka Topic**
        topic_name = "user_behavior_logs" # 定义一个专门用于用户行为日志的 Topic
        producer.send(topic_name, log_data)
        producer.flush() # 确保消息被发送

        print(f"--- Log Received from Frontend and Sent to Kafka Topic '{topic_name}' ---")
        print(json.dumps(log_data, indent=2, ensure_ascii=False))
        print("---------------------------------------------------------------------")

        # （可选）保留写入文件作为备份
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            json_line = json.dumps(log_data, ensure_ascii=False)
            f.write(json_line + '\n')

        return jsonify({"message": "Log received and processed"}), 200

    except Exception as e:
        print(f"[ERROR] Failed to process log: {e}")
        return jsonify({"error": str(e)}), 500