import os
import json
from datetime import datetime
import logging
import pickle # 导入 pickle 模块用于状态的序列化/反序列化

from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import KeyedProcessFunction, FlatMapFunction # 引入 FlatMapFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common import Row
from pyflink.common import Configuration

# 配置日志
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
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_RECENT_VIEWS_HASH_KEY = "user_recent_views"


### JsonParser FlatMapFunction
class JsonParser(FlatMapFunction):
    """
    解析 JSON 字符串并转换为 Flink Row。
    如果解析失败或数据不符合预期结构，则不产生任何输出（即跳过）。
    """
    def flat_map(self, json_str: str):
        try:
            data = json.loads(json_str)

            # 检查必要字段是否存在，并且类型符合预期
            # 注意：原始数据中 userId 是 int，你的 Types.INT() 是匹配的
            # 但如果你需要强制转换为字符串，可以在这里做。
            user_id = data.get('userId')
            event_type = data.get('eventType')
            timestamp = data.get('timestamp')
            page_url = data.get('pageUrl')
            payload_data = data.get('payload')

            # 核心业务逻辑：只处理包含特定字段且符合格式的事件
            if not all([user_id is not None, event_type, timestamp, page_url, payload_data is not None]):
                logger.debug(f"Skipping record: Missing essential fields in JSON: '{json_str}'")
                return # 不产生输出

            if not isinstance(payload_data, dict):
                logger.debug(
                    f"Skipping record: 'payload' is not a dictionary for JSON string: '{json_str}'. "
                    f"Payload content: {payload_data}"
                )
                return # 不产生输出

            # 检查 payload 内部结构，适配 Types.ROW_NAMED(["pageName", "dwellTime"], [Types.STRING(), Types.INT()])
            page_name = payload_data.get('pageName')
            dwell_time = payload_data.get('dwellTime') # 注意：如果 dwellTime 可能不存在，处理成 None 或默认值

            # 确保 pageName 是字符串，dwellTime 是数字
            if not isinstance(page_name, str):
                page_name = None # 或默认值
            if not isinstance(dwell_time, (int, float)): # 允许浮点数，但最终会转为 int
                dwell_time = None # 或默认值

            # Yield 对应的 Row
            # 确保这里的字段名和类型与 main 函数中 json_row_type_info 定义的严格匹配
            yield Row(
                userId=int(user_id), # 确保转换为正确的类型
                sessionId=data.get('sessionId'),
                eventType=str(event_type),
                timestamp=str(timestamp),
                pageUrl=str(page_url),
                payload=Row(
                    pageName=page_name,
                    dwellTime=int(dwell_time) if dwell_time is not None else None # 转换为 int
                )
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Skipping record: Failed to decode JSON string: '{json_str}'. Error: {e}")
            # 不产生输出
        except (ValueError, TypeError, AttributeError) as e:
            # 捕获因数据类型不匹配、字段不存在等导致的更具体的错误
            logger.warning(f"Skipping record due to data format inconsistency or type error: '{json_str}'. Error: {e}")
            # 不产生输出
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing JSON string: '{json_str}'. Error: {e}", exc_info=True)
            # 不产生输出

### `UserRecentViewsProcessFunction`
class UserRecentViewsProcessFunction(KeyedProcessFunction):
    """
    Processes user behavior logs (specifically 'page_view' events for 'BookDetails' pages),
    extracts user and item IDs, maintains a list of recently viewed items (with timestamps) for each user,
    and writes this list to Redis.
    """
    def open(self, runtime_context):
        self.redis_client = None
        try:
            import redis
            self.redis_client = redis.StrictRedis(
                host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
            )
            self.redis_client.ping()
            logger.info(f"[{runtime_context.get_task_name()}] Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}!")
        except Exception as e:
            logger.error(f"[{runtime_context.get_task_name()}] Error connecting to Redis at {REDIS_HOST}:{REDIS_PORT}: {e}")
            self.redis_client = None # 显式设置为 None

        self.recent_views_state = runtime_context.get_state(
            ValueStateDescriptor(
                "recent_views_list_state",
                Types.PICKLED_BYTE_ARRAY() # 存储 Python 对象的序列化字节数组
            )
        )
        self.MAX_RECENT_VIEWS = 5

    def process_element(self, value: Row, ctx: 'KeyedProcessFunction.Context'):
        # 在处理元素前，首先检查 Redis 客户端是否可用
        if self.redis_client is None:
            logger.error(f"Redis client is not initialized for user {value.userId}. Cannot process element: {value}")
            return # 如果 Redis 不可用，则跳过处理，避免后续操作报错

        try:
            user_id = value.userId # userId 现在是 Int 类型
            event_type = value.eventType
            timestamp_str = value.timestamp
            payload_row = value.payload # payload 是一个 Flink Row 对象

            # 解析时间戳字符串为 Unix 毫秒时间戳
            try:
                # 尝试解析 ISO 格式带 Z 或不带 Z 的时间戳
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
            # 从 payload_row 中获取 pageName，确保健壮性
            page_name = getattr(payload_row, 'pageName', None)

            # 只有当 eventType 是 'page_view' 并且 pageName 是 'BookDetails' 时才提取 item_id
            if event_type == 'page_view' and isinstance(page_name, str) and page_name == 'BookDetails':
                page_url = value.pageUrl # pageUrl 在这里应该始终是字符串
                if page_url: # 检查 pageUrl 是否非空
                    parts = page_url.split('/')
                    # 检查 URL 结构是否符合 /books/{item_id}
                    if len(parts) >= 2 and parts[-2] == 'books' and parts[-1]:
                        item_id = parts[-1]
                else:
                    logger.debug(f"pageUrl is missing for page_view event for user {user_id}. Skipping item_id extraction.")

            logger.debug(
                f"Processing event: user_id={user_id}, event_type={event_type}, "
                f"item_id={item_id}, page_url={value.pageUrl}, timestamp={event_timestamp_ms}"
            )

            if not item_id: # 如果 item_id 无法提取，则不处理
                logger.debug(f"Skipping event: No valid item_id found for event: {value}")
                return

            # 获取和处理状态
            current_views_pickled = self.recent_views_state.value()
            current_views_list = []
            if current_views_pickled is not None:
                try:
                    # 首先反序列化 pickle 字节数组得到 JSON 字符串
                    current_views_json_str = pickle.loads(current_views_pickled)
                    # 然后反序列化 JSON 字符串得到 Python 列表
                    current_views_list = json.loads(current_views_json_str)
                    if not isinstance(current_views_list, list):
                        logger.warning(f"Recent views state for user {user_id} is not a list after deserialization. Resetting.")
                        current_views_list = [] # 确保是列表
                except (pickle.UnpicklingError, json.JSONDecodeError, TypeError) as e:
                    logger.error(f"Failed to deserialize recent views state for user {user_id}: {e}. Resetting state.", exc_info=True)
                    current_views_list = []

            new_view = {'item_id': item_id, 'timestamp': event_timestamp_ms}

            # 移除旧的同 item_id 记录，并添加新的
            current_views_list = [view for view in current_views_list if view.get('item_id') != item_id]
            current_views_list.append(new_view)

            # 按时间戳降序排序，并截取最新 n 条
            current_views_list = sorted(current_views_list, key=lambda x: x.get('timestamp', 0), reverse=True)[:self.MAX_RECENT_VIEWS] # 使用 .get 防止键不存在

            # 序列化并更新状态
            # 先将列表转换为 JSON 字符串，再 pickle 序列化为字节数组
            self.recent_views_state.update(pickle.dumps(json.dumps(current_views_list)))

            # 更新 Redis (这里已经检查过 self.redis_client 是否为 None)
            try:
                self.redis_client.hset(
                    REDIS_RECENT_VIEWS_HASH_KEY,
                    str(user_id), # Redis key 应该总是字符串
                    json.dumps(current_views_list)
                )
                logger.info(f"[{ctx.get_current_key()}] Updated recent views for user {user_id}: {current_views_list}")
            except Exception as e:
                logger.error(f"[{ctx.get_current_key()}] Error writing to Redis for user {user_id}: {e}", exc_info=True)

        except Exception as e:
            # 捕获更上层的异常，确保所有处理元素时的错误都能被记录
            logger.error(f"Error processing element {value} for key {ctx.get_current_key()}: {e}", exc_info=True)


### `main` 函数
def main():
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(1)

    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers(os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')) \
        .set_topics(os.getenv('KAFKA_TOPIC', 'user_behavior_logs')) \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    # 定义完整的 Row 类型信息
    # 确保这个类型信息与 JsonParser 中 yield 的 Row 的结构严格一致
    json_row_type_info = Types.ROW_NAMED(
        ["userId", "sessionId", "eventType", "timestamp", "pageUrl", "payload"],
        [
            Types.INT(), # userId 是 INT
            Types.STRING(),
            Types.STRING(),
            Types.STRING(),
            Types.STRING(),
            # payload 是嵌套的 Row
            Types.ROW_NAMED(
                ["pageName", "dwellTime"],
                [Types.STRING(), Types.INT()] # dwellTime 是 INT
            )
        ]
    )

    data_stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="Kafka User Behavior Logs Source",
        type_info=Types.STRING() # Kafka source 输出的是字符串
    ).flat_map( # <--- 关键修改：使用 flat_map
        JsonParser(), # 使用我们新定义的 JsonParser FlatMapFunction
        output_type=json_row_type_info # 明确定义输出类型
    )

    data_stream \
        .key_by(lambda x: x.userId, key_type=Types.INT()) \
        .process(UserRecentViewsProcessFunction())

    logger.info("Starting PyFlink Realtime User Recent Views Aggregation Job (from user_behavior_logs)...")
    env.execute("PyFlink Realtime User Recent Views Aggregator from Behavior Logs")


if __name__ == '__main__':
    # 仅在直接运行脚本时导入 redis，避免与 Flink 运行时环境冲突
    import redis 
    main()