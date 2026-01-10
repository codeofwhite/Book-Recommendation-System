import os
import json
import logging
import pickle
import redis

from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import KeyedProcessFunction, FlatMapFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common import Row
from pyflink.common import Configuration

class FlinkJobConfig:
    # --- Redis 连接配置 ---
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    # --- Redis 键和前缀配置 ---
    REDIS_RECENT_VIEWS_HASH_KEY = "user_recent_views_hash:"
    # 准实时任务写入的原始推荐列表 KEY
    OFFLINE_RECOMMENDATIONS_KEY_PREFIX = "recommendations:user:"
    # 最终过滤后的推荐列表 KEY → 和你的前端接口完全匹配，不用改前端代码
    REDIS_REALTIME_UPDATED_RECOMMENDATIONS_PREFIX = os.getenv(
        "REDIS_REALTIME_UPDATED_RECOMMENDATIONS_PREFIX",
        "realtime_updated_recommendations:user:",
    )

    # --- Flink 作业参数 ---
    MAX_RECENT_VIEWS = int(os.getenv("MAX_RECENT_VIEWS", 20))
    FINAL_RECOMMENDATION_COUNT = int(os.getenv("FINAL_RECOMMENDATION_COUNT", 12))
    RECOMMENDATION_CACHE_EXPIRE_SECONDS = int(os.getenv("RECOMMENDATION_CACHE_EXPIRE_SECONDS", 3600 * 24))

    # --- Kafka 配置 ---
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user_behavior_logs")

# ======================== 日志配置 ========================
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ======================== Flink环境配置 ========================
config = Configuration()
config.set_string("jobmanager.rpc.address", "flink-jobmanager")
config.set_string("jobmanager.rpc.port", "6123")
config.set_string("rest.address", "flink-jobmanager")
config.set_string("rest.port", "8081")
config.set_string("python.executable", "/usr/bin/python3")

env = StreamExecutionEnvironment.get_execution_environment(configuration=config)
env.enable_checkpointing(60000)

# ======================== JsonParser解析器 ========================
class JsonParser(FlatMapFunction):
    def flat_map(self, json_str: str):
        try:
            data = json.loads(json_str)
            user_id = data.get("userId")
            event_type = data.get("eventType")
            timestamp = data.get("timestamp")
            page_url = data.get("pageUrl")
            payload_data = data.get("payload")

            if not all([user_id is not None, event_type, timestamp, page_url, payload_data is not None,]):
                logger.info(f"Skipping record: Missing essential fields in JSON: '{json_str}'")
                return

            if not isinstance(payload_data, dict):
                logger.info(f"Skipping record: 'payload' is not a dictionary for JSON string: '{json_str}'. Payload content: {payload_data}")
                return

            page_name = payload_data.get("pageName")
            dwell_time = payload_data.get("dwellTime")

            if not isinstance(page_name, str):
                page_name = None
            if not isinstance(dwell_time, (int, float)):
                dwell_time = None

            yield Row(
                userId=int(user_id),
                sessionId=data.get("sessionId"),
                eventType=str(event_type),
                timestamp=str(timestamp),
                pageUrl=str(page_url),
                payload=Row(pageName=page_name, dwellTime=int(dwell_time) if dwell_time is not None else None,),
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Skipping record: Failed to decode JSON string: '{json_str}'. Error: {e}")
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Skipping record due to data format inconsistency or type error: '{json_str}'. Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing JSON string: '{json_str}'. Error: {e}",exc_info=True,)

# ======================== 过滤已读图书，保留完整推荐列表 ========================
class PureRealtimeFilterProcessFunction(KeyedProcessFunction):
    """
    1. 消费用户行为事件 → 提取图书ID → 记录用户【最近浏览过的图书ID】
    2. 从Redis读取【准实时任务生成的完整推荐列表】(带score/book_id等所有字段)
    3. 过滤：移除推荐列表中「用户已经浏览过的图书ID」
    4. 把过滤后的完整推荐列表 重新写入Redis → 供前端接口读取
    """
    def open(self, runtime_context):
        # Redis连接
        self.redis_client = None
        try:
            self.redis_client = redis.StrictRedis(
                host=FlinkJobConfig.REDIS_HOST,
                port=FlinkJobConfig.REDIS_PORT,
                db=FlinkJobConfig.REDIS_DB,
                password=FlinkJobConfig.REDIS_PASSWORD,
                decode_responses=False,
            )
            self.redis_client.ping()
            logger.info(f"[{runtime_context.get_task_name()}] Redis连接成功!")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None

        # 保存用户最近浏览的图书ID列表
        self.recent_books_state = runtime_context.get_state(
            ValueStateDescriptor("recent_books_state", Types.PICKLED_BYTE_ARRAY())
        )
        self.MAX_RECENT_VIEWS = FlinkJobConfig.MAX_RECENT_VIEWS
        self.FINAL_RECOMMENDATION_COUNT = FlinkJobConfig.FINAL_RECOMMENDATION_COUNT

    def process_element(self, value: Row, ctx: "KeyedProcessFunction.Context"):
        if self.redis_client is None:
            logger.error(f"用户 {value.userId} Redis未初始化，跳过处理")
            return

        try:
            user_id = value.userId
            page_name = getattr(value.payload, "pageName", None)
            page_url = value.pageUrl

            # 只处理【图书详情页】的事件
            if not (isinstance(page_name, str) and page_name == "BookDetails"):
                return

            # 提取当前浏览的图书ID
            current_book_id = None
            if page_url:
                parts = page_url.split("/")
                valid_parts = [p for p in parts if p.strip()]
                if len(valid_parts) >= 2 and valid_parts[-2] == "books" and valid_parts[-1]:
                    current_book_id = valid_parts[-1]
            
            if not current_book_id:
                logger.info(f"用户 {user_id} 无有效图书ID，跳过")
                return

            # 更新用户【最近浏览的图书ID列表】+ 去重
            current_books_pickled = self.recent_books_state.value()
            current_books_list = []
            if current_books_pickled is not None:
                try:
                    current_books_json_str = pickle.loads(current_books_pickled)
                    current_books_list = json.loads(current_books_json_str)
                    if not isinstance(current_books_list, list):
                        current_books_list = []
                except Exception as e:
                    logger.warning(f"用户 {user_id} 状态解析失败，重置: {e}")
                    current_books_list = []

            # 相同图书ID只保留最新一次
            current_books_list = [bid for bid in current_books_list if bid != current_book_id]
            current_books_list.append(current_book_id)
            current_books_list = current_books_list[-self.MAX_RECENT_VIEWS:] # 只保留最新20本
            self.recent_books_state.update(pickle.dumps(json.dumps(current_books_list, ensure_ascii=False)))
            
            # 同步更新Redis的浏览记录 (和准实时一致)
            self.redis_client.hset(
                FlinkJobConfig.REDIS_RECENT_VIEWS_HASH_KEY,
                str(user_id),
                json.dumps(current_books_list, ensure_ascii=False)
            )
            logger.info(f"用户 {user_id} 浏览记录更新: {current_book_id} | 已浏览列表: {current_books_list}")

            # 读取准实时任务生成的
            offline_rec_key = f"{FlinkJobConfig.OFFLINE_RECOMMENDATIONS_KEY_PREFIX}{user_id}"
            offline_rec_json = self.redis_client.get(offline_rec_key)
            if not offline_rec_json:
                logger.info(f"用户 {user_id} Redis中无推荐列表，跳过过滤")
                return
            
            # 解析完整的推荐列表 (带book_id/score等所有字段)
            offline_rec_list = json.loads(offline_rec_json.decode("utf-8"))
            if not isinstance(offline_rec_list, list) or len(offline_rec_list) == 0:
                logger.info(f"用户 {user_id} 推荐列表为空，跳过过滤")
                return
            logger.info(f"用户 {user_id} 原始推荐列表数量: {len(offline_rec_list)}")

            # 移除推荐列表中「用户已浏览过的图书」
            filtered_rec_list = []
            for rec_item in offline_rec_list:
                # 兼容推荐列表中的book_id字段命名 (book_id / item_id)
                rec_book_id = rec_item.get("book_id") or rec_item.get("item_id")
                if rec_book_id and rec_book_id not in current_books_list:
                    filtered_rec_list.append(rec_item)

            # 截断到指定数量，返回给前端
            filtered_rec_list = filtered_rec_list[:self.FINAL_RECOMMENDATION_COUNT]
            logger.info(f"用户 {user_id} 过滤后推荐列表数量: {len(filtered_rec_list)} (已移除{len(offline_rec_list)-len(filtered_rec_list)}本已读图书)")

            # 写入Redis → KEY
            final_rec_key = f"{FlinkJobConfig.REDIS_REALTIME_UPDATED_RECOMMENDATIONS_PREFIX}{user_id}"
            self.redis_client.setex(
                final_rec_key,
                FlinkJobConfig.RECOMMENDATION_CACHE_EXPIRE_SECONDS,
                json.dumps(filtered_rec_list, ensure_ascii=False).encode("utf-8")
            )

            logger.info(f"✅ 成功！用户 {user_id} 过滤后的推荐列表已写入Redis")

        except Exception as e:
            logger.error(f"处理用户 {value.userId} 数据失败: {e}", exc_info=True)

# ======================== main方法 ========================
def main():
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(1)

    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(FlinkJobConfig.KAFKA_BOOTSTRAP_SERVERS)
        .set_topics(FlinkJobConfig.KAFKA_TOPIC)
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    json_row_type_info = Types.ROW_NAMED(
        ["userId", "sessionId", "eventType", "timestamp", "pageUrl", "payload"],
        [Types.INT(),Types.STRING(),Types.STRING(),Types.STRING(),Types.STRING(),Types.ROW_NAMED(["pageName", "dwellTime"], [Types.STRING(), Types.INT()]),],
    )

    data_stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="Kafka User Behavior Logs Source",
        type_info=Types.STRING(),
    ).flat_map(JsonParser(), output_type=json_row_type_info)

    data_stream.key_by(lambda x: x.userId, key_type=Types.INT()).process(
        PureRealtimeFilterProcessFunction()
    )

    logger.info("Starting PyFlink Pure Realtime Job (Filter Read Books) ...")
    env.execute("PyFlink Pure Realtime - Filter Read Books From Recommend List")

if __name__ == "__main__":
    main()