import os
import json
from datetime import datetime
import logging
import pickle # 导入 pickle 模块用于状态的序列化/反序列化
import redis # 在 TaskManager 侧也需要这个库

from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import KeyedProcessFunction, FlatMapFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common import Row
from pyflink.common import Configuration

# --- 自定义配置类，用于 Flink Job 内部使用 ---
# 这样就不需要依赖外部的 config.py 文件了
class FlinkJobConfig:
    # 实时更新推荐结果在 Redis 中的过期时间（秒）
    # 你可以根据实际需求调整这个值，例如 24 小时 (3600 * 24)
    RECOMMENDATION_CACHE_EXPIRE_SECONDS = 3600 * 24 

# --- 引入日志模块 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Flink 环境配置 ---
config = Configuration()
config.set_string("jobmanager.rpc.address", "flink-jobmanager")
config.set_string("jobmanager.rpc.port", "6123")
config.set_string("rest.address", "flink-jobmanager")
config.set_string("rest.port", "8081")
config.set_string("python.executable", "/usr/bin/python3")

env = StreamExecutionEnvironment.get_execution_environment(configuration=config)

# --- Redis 配置 ---
# Real-time Recent Views Redis Config
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_RECENT_VIEWS_HASH_KEY = "user_recent_views" # Flink 实时任务存储最近浏览的键

# Offline Recommendations Redis Config
# 确保这里也从环境变量或配置中获取离线推荐的 Redis 信息，如果和实时推荐是同一个 Redis 实例，可以复用
OFFLINE_REDIS_HOST = os.getenv('OFFLINE_REDIS_HOST', REDIS_HOST) # 假设和实时 Redis 相同
OFFLINE_REDIS_PORT = int(os.getenv('OFFLINE_REDIS_PORT', REDIS_PORT))
OFFLINE_REDIS_DB = int(os.getenv('OFFLINE_REDIS_DB', REDIS_DB))
OFFLINE_RECOMMENDATIONS_KEY_PREFIX = "recommendations:user:" # 离线推荐存储的键前缀，与 utils/redis_utils.py 保持一致

### JsonParser FlatMapFunction (保持不变)
class JsonParser(FlatMapFunction):
    """
    解析 JSON 字符串并转换为 Flink Row。
    如果解析失败或数据不符合预期结构，则不产生任何输出（即跳过）。
    """
    def flat_map(self, json_str: str):
        try:
            data = json.loads(json_str)
            user_id = data.get('userId')
            event_type = data.get('eventType')
            timestamp = data.get('timestamp')
            page_url = data.get('pageUrl')
            payload_data = data.get('payload')

            if not all([user_id is not None, event_type, timestamp, page_url, payload_data is not None]):
                logger.debug(f"Skipping record: Missing essential fields in JSON: '{json_str}'")
                return

            if not isinstance(payload_data, dict):
                logger.debug(
                    f"Skipping record: 'payload' is not a dictionary for JSON string: '{json_str}'. "
                    f"Payload content: {payload_data}"
                )
                return

            page_name = payload_data.get('pageName')
            dwell_time = payload_data.get('dwellTime')

            if not isinstance(page_name, str):
                page_name = None
            if not isinstance(dwell_time, (int, float)):
                dwell_time = None

            yield Row(
                userId=int(user_id),
                sessionId=data.get('sessionId'),
                eventType=str(event_type),
                timestamp=str(timestamp),
                pageUrl=str(page_url),
                payload=Row(
                    pageName=page_name,
                    dwellTime=int(dwell_time) if dwell_time is not None else None
                )
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Skipping record: Failed to decode JSON string: '{json_str}'. Error: {e}")
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Skipping record due to data format inconsistency or type error: '{json_str}'. Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing JSON string: '{json_str}'. Error: {e}", exc_info=True)


### `UserRecentViewsProcessFunction`
class UserRecentViewsProcessFunction(KeyedProcessFunction):
    def open(self, runtime_context):
        # 初始化实时推荐 Redis 客户端（用于最近浏览）
        self.realtime_redis_client = None
        try:
            self.realtime_redis_client = redis.StrictRedis(
                host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
            )
            self.realtime_redis_client.ping()
            logger.info(f"[{runtime_context.get_task_name()}] Successfully connected to Realtime Redis at {REDIS_HOST}:{REDIS_PORT}!")
        except Exception as e:
            logger.error(f"[{runtime_context.get_task_name()}] Error connecting to Realtime Redis at {REDIS_HOST}:{REDIS_PORT}: {e}")
            self.realtime_redis_client = None

        # 初始化离线推荐 Redis 客户端 (注意：如果和实时 Redis 是同一个实例，可以只用一个客户端)
        self.offline_redis_client = None
        try:
            self.offline_redis_client = redis.StrictRedis(
                host=OFFLINE_REDIS_HOST, port=OFFLINE_REDIS_PORT, db=OFFLINE_REDIS_DB, decode_responses=True
            )
            self.offline_redis_client.ping()
            logger.info(f"[{runtime_context.get_task_name()}] Successfully connected to Offline Redis at {OFFLINE_REDIS_HOST}:{OFFLINE_REDIS_PORT}!")
        except Exception as e:
            logger.error(f"[{runtime_context.get_task_name()}] Error connecting to Offline Redis at {OFFLINE_REDIS_HOST}:{OFFLINE_REDIS_PORT}: {e}")
            self.offline_redis_client = None


        self.recent_views_state = runtime_context.get_state(
            ValueStateDescriptor(
                "recent_views_list_state",
                Types.PICKLED_BYTE_ARRAY()
            )
        )
        self.MAX_RECENT_VIEWS = 5
        self.MAX_OFFLINE_RECOMMENDATIONS = 10 # 从离线推荐中获取的最大数量
        self.FINAL_RECOMMENDATION_COUNT = 5 # 最终输出给前端的推荐数量

    def process_element(self, value: Row, ctx: 'KeyedProcessFunction.Context'):
        # 确保 Redis 客户端可用
        if self.realtime_redis_client is None or self.offline_redis_client is None:
            logger.error(f"One or both Redis clients are not initialized for user {value.userId}. Cannot process element: {value}")
            return

        try:
            user_id = value.userId
            event_type = value.eventType
            timestamp_str = value.timestamp
            payload_row = value.payload

            # 1. 解析时间戳 (与之前逻辑相同)
            try:
                if timestamp_str.endswith('Z'):
                    dt_object = datetime.fromisoformat(timestamp_str[:-1] + '+00:00')
                else:
                    dt_object = datetime.fromisoformat(timestamp_str)
                event_timestamp_ms = int(dt_object.timestamp() * 1000)
            except (ValueError, TypeError) as e:
                event_timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
                logger.warning(
                    f"Could not parse timestamp '{timestamp_str}' for user {user_id}. "
                    f"Error: {e}. Using current UTC time as fallback."
                )

            item_id = None
            page_name = getattr(payload_row, 'pageName', None)

            if event_type == 'page_view' and isinstance(page_name, str) and page_name == 'BookDetails':
                page_url = value.pageUrl
                if page_url:
                    parts = page_url.split('/')
                    if len(parts) >= 2 and parts[-2] == 'books' and parts[-1]:
                        item_id = parts[-1]
                else:
                    logger.debug(f"pageUrl is missing for page_view event for user {user_id}. Skipping item_id extraction.")

            if not item_id:
                logger.debug(f"Skipping event: No valid item_id found for event: {value}")
                # 即使没有 item_id，我们可能仍然想更新推荐列表，
                # 但这里为了简洁，假设只有有效 item_id 才触发推荐更新
                return

            # 2. 更新用户的最近浏览状态 (与之前逻辑相同)
            current_views_pickled = self.recent_views_state.value()
            current_views_list = []
            if current_views_pickled is not None:
                try:
                    current_views_json_str = pickle.loads(current_views_pickled)
                    current_views_list = json.loads(current_views_json_str)
                    if not isinstance(current_views_list, list):
                        logger.warning(f"Recent views state for user {user_id} is not a list after deserialization. Resetting.")
                        current_views_list = []
                except (pickle.UnpicklingError, json.JSONDecodeError, TypeError) as e:
                    logger.error(f"Failed to deserialize recent views state for user {user_id}: {e}. Resetting state.", exc_info=True)
                    current_views_list = []

            new_view = {'item_id': item_id, 'timestamp': event_timestamp_ms}
            current_views_list = [view for view in current_views_list if view.get('item_id') != item_id]
            current_views_list.append(new_view)
            current_views_list = sorted(current_views_list, key=lambda x: x.get('timestamp', 0), reverse=True)[:self.MAX_RECENT_VIEWS]
            self.recent_views_state.update(pickle.dumps(json.dumps(current_views_list)))

            # 同时更新 Redis 中的最近浏览
            self.realtime_redis_client.hset(
                REDIS_RECENT_VIEWS_HASH_KEY,
                str(user_id),
                json.dumps(current_views_list)
            )
            logger.info(f"[{ctx.get_current_key()}] Updated recent views for user {user_id}.")

            # --- 3. 从离线 Redis 获取推荐并进行实时更新 ---
            offline_recs_key = f"{OFFLINE_RECOMMENDATIONS_KEY_PREFIX}{user_id}"
            offline_recs_json = self.offline_redis_client.get(offline_recs_key)
            offline_recommendations = []

            if offline_recs_json:
                try:
                    offline_recommendations = json.loads(offline_recs_json)
                    logger.debug(f"Retrieved {len(offline_recommendations)} offline recommendations for user {user_id}.")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode offline recommendations JSON for user {user_id}: {e}. Raw: {offline_recs_json}", exc_info=True)
                except Exception as e:
                    logger.error(f"Error processing offline recommendations for user {user_id}: {e}", exc_info=True)

            # 4. 实时逻辑：结合用户最新行为更新离线推荐
            # 这是一个示例性的逻辑，你可以根据实际需求调整：

            # a) 过滤掉用户最近浏览过的商品（如果它们在离线推荐中）
            # 假设离线推荐列表中的每个元素都有一个 'book_id' 或 'item_id'
            recent_item_ids = {view.get('item_id') for view in current_views_list if view.get('item_id')}

            # 过滤掉最近浏览过的项目，或者你可能想给它们降权
            filtered_offline_recs = []
            for rec_item in offline_recommendations:
                # 假设离线推荐的格式是 {"book_id": "...", "title": "...", "score": ...}
                rec_item_id = rec_item.get('book_id') or rec_item.get('item_id') # 适配不同的命名
                if rec_item_id and rec_item_id not in recent_item_ids:
                    filtered_offline_recs.append(rec_item)
                else:
                    logger.debug(f"Filtering out recently viewed item {rec_item_id} from offline recommendations for user {user_id}.")

            # b) 考虑新发生的行为（当前 event_type 和 page_name）
            # 如果当前事件是针对某个书籍详情页的深度浏览 (dwellTime 较高)，可以考虑将相关书籍推到前面
            # 甚至可以将当前浏览的 item_id 相似的 item 从离线推荐中提取并提升权重

            # 示例：将当前浏览的 item 提升到推荐列表首位 (如果它在过滤后的离线推荐中存在)
            if item_id: # item_id 是当前事件产生的
                found_current_item = False
                for i, rec in enumerate(filtered_offline_recs):
                    rec_item_id = rec.get('book_id') or rec.get('item_id')
                    if rec_item_id == item_id:
                        # 找到，将其移动到列表最前面，并增加一个 "实时相关性" 标记
                        moved_rec = filtered_offline_recs.pop(i)
                        # moved_rec['realtime_boost'] = True # 可以添加额外信息
                        filtered_offline_recs.insert(0, moved_rec)
                        found_current_item = True
                        logger.debug(f"Boosted current viewed item {item_id} in recommendations for user {user_id}.")
                        break
                # 如果当前浏览的商品不在离线推荐中，但你想把它作为高优先级推荐，可以考虑添加
                # else:
                #     # 这里你需要知道 item_id 对应的书名等信息来构建一个完整的推荐 item 字典
                #     # 这可能需要一个查找表或者另一个 Redis 查询
                #     pass


            # c) 最终的推荐列表可能需要截断或融合其他实时因素
            final_recommendations = filtered_offline_recs[:self.FINAL_RECOMMENDATION_COUNT]

            # 5. 将最终的实时更新推荐列表写回 Redis
            # 可以写到另一个键，或者覆盖离线推荐的键（如果离线更新周期很长且实时更新是主要的）
            # 建议使用一个新的键，例如 "realtime_updated_recommendations:user:{user_id}"
            REALTIME_UPDATED_RECS_KEY_PREFIX = "realtime_updated_recommendations:user:"
            final_recs_redis_key = f"{REALTIME_UPDATED_RECS_KEY_PREFIX}{user_id}"

            self.realtime_redis_client.setex(
                final_recs_redis_key,
                FlinkJobConfig.RECOMMENDATION_CACHE_EXPIRE_SECONDS, 
                json.dumps(final_recommendations, ensure_ascii=False)
            )
            logger.info(f"[{ctx.get_current_key()}] Stored {len(final_recommendations)} real-time updated recommendations for user {user_id}.")


        except Exception as e:
            logger.error(f"Error processing element {value} for key {ctx.get_current_key()}: {e}", exc_info=True)


### `main` 函数 (保持不变，因为修改在 ProcessFunction 内部)
def main():
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(1) # 根据你的集群资源和数据量调整并行度

    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers(os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')) \
        .set_topics(os.getenv('KAFKA_TOPIC', 'user_behavior_logs')) \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    json_row_type_info = Types.ROW_NAMED(
        ["userId", "sessionId", "eventType", "timestamp", "pageUrl", "payload"],
        [
            Types.INT(),
            Types.STRING(),
            Types.STRING(),
            Types.STRING(),
            Types.STRING(),
            Types.ROW_NAMED(
                ["pageName", "dwellTime"],
                [Types.STRING(), Types.INT()]
            )
        ]
    )

    data_stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="Kafka User Behavior Logs Source",
        type_info=Types.STRING()
    ).flat_map(
        JsonParser(),
        output_type=json_row_type_info
    )

    data_stream \
        .key_by(lambda x: x.userId, key_type=Types.INT()) \
        .process(UserRecentViewsProcessFunction())

    logger.info("Starting PyFlink Realtime User Recent Views Aggregation and Hybrid Recommendation Job...")
    env.execute("PyFlink Realtime User Recent Views Aggregator and Hybrid Recommendation")


if __name__ == '__main__':
    # 仅在直接运行脚本时导入 redis，避免与 Flink 运行时环境冲突
    import redis
    main()