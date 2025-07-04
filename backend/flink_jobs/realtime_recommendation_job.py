import os
import json

from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import KeyedProcessFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common import Row # 确保 Row 导入正确
from pyflink.common import Configuration

# --- 关键修改部分开始 ---
config = Configuration()
config.set_string("jobmanager.rpc.address", "flink-jobmanager")
config.set_string("jobmanager.rpc.port", "6123")
config.set_string("rest.address", "flink-jobmanager")
config.set_string("rest.port", "8081")

# 在 JobManager 和 TaskManager 中明确指定 Python 解释器
# 这通常通过 docker-compose.yaml 或 Flink 配置文件设置
# 但在 Python 脚本中设置这个配置项不会有副作用，甚至可能更稳妥
config.set_string("python.executable", "/usr/bin/python3") # 确保 Flink 知道使用 python3
# --- 关键修改部分结束 ---

env = StreamExecutionEnvironment.get_execution_environment(configuration=config)

import redis

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

class UserRecentViewsProcessFunction(KeyedProcessFunction):
    """
    Processes user view events, maintains a list of recently viewed books for each user,
    and writes this list to Redis.
    """
    def open(self, runtime_context):
        self.redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        try:
            self.redis_client.ping()
            print(f"[{runtime_context.get_task_name()}] Successfully connected to Redis!")
        except Exception as e:
            print(f"[{runtime_context.get_task_name()}] Error connecting to Redis: {e}")
            self.redis_client = None

        self.recent_views_state = runtime_context.get_state(
            ValueStateDescriptor(
                "recent_views",
                Types.LIST(Types.STRING()),
            )
        )
        self.MAX_RECENT_VIEWS = 5

    # process_element 的输入 'value' 现在是一个 Row 对象
    def process_element(self, value: Row, ctx: 'KeyedProcessFunction.Context'):
        # 直接使用 Row 对象的属性访问方式，这和你的预期一致
        user_id = value.user_id
        item_id = value.item_id
        event_type = value.event_type

        # 打印一下接收到的数据，帮助调试
        print(f"Processing event: user_id={user_id}, item_id={item_id}, event_type={event_type}")

        if not user_id or not item_id or event_type != 'view':
            return

        current_views = self.recent_views_state.value()
        if current_views is None:
            current_views = []

        if item_id in current_views:
            current_views.remove(item_id)
        current_views.insert(0, item_id)

        if len(current_views) > self.MAX_RECENT_VIEWS:
            current_views = current_views[:self.MAX_RECENT_VIEWS]

        self.recent_views_state.update(current_views)

        if self.redis_client:
            try:
                self.redis_client.hset("user_recent_views", user_id, json.dumps(current_views))
                print(f"[{ctx.get_current_key()}] Updated recent views for user {user_id}: {current_views}")
            except Exception as e:
                print(f"[{ctx.get_current_key()}] Error writing to Redis for user {user_id}: {e}")

def main():
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(1)

    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers("kafka:29092") \
        .set_topics("user_book_interactions") \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    # 定义 RowTypeInfo 应该包含所有 JSON 中的字段，才能正确映射
    # 注意，你的 JSON 还有 'timestamp' 字段，所以也应该包含进来
    json_row_type_info = Types.ROW_NAMED(
        ["user_id", "item_id", "event_type", "timestamp"], # 包含所有字段
        [Types.STRING(), Types.STRING(), Types.STRING(), Types.LONG()] # 对应类型，timestamp 通常是long
    )

    # 2. Read from Kafka data stream and parse JSON
    data_stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="Kafka User Interaction Source",
        type_info=Types.STRING() # KafkaSource的value_only_deserializer返回的是SimpleStringSchema，所以这里是Types.STRING()
    ).map(
        # 修正 map 函数：将解析后的字典转换为 Flink Row 对象
        # 确保顺序与 json_row_type_info 的字段顺序一致
        lambda x: Row(**json.loads(x)), # 使用 **json.loads(x) 将字典解包为 Row 的命名参数
        output_type=json_row_type_info
    )

    # 3. Key the stream by user_id, and apply ProcessFunction
    # key_by 的 lambda 函数仍然从 Row 对象中取 user_id
    data_stream \
        .key_by(lambda x: x.user_id, key_type=Types.STRING()) \
        .process(UserRecentViewsProcessFunction(), output_type=Types.TUPLE([Types.STRING(), Types.LIST(Types.STRING())]))
        # 修正 output_type: UserRecentViewsProcessFunction 并没有实际输出一个 tuple(user_id, current_views)
        # 如果你的 process_element 函数没有 yield 任何数据，那么 output_type 应该是 Types.VOID()。
        # 如果你确实想输出 (user_id, current_views) 这样的元组，
        # 那么你的 process_element 函数需要添加 yield (user_id, current_views)
        # 这里假设你最终没有 yield，只是往 Redis 写，所以暂时注释掉 output_type 或者改为 Types.VOID()。
        # 如果需要输出，应该根据实际输出类型来定义。
        # 例如，如果你要输出 (user_id, current_views)，那么应该在 ProcessFunction 里 yield 并且 output_type 是 Types.TUPLE([Types.STRING(), Types.LIST(Types.STRING())])

    print("Starting PyFlink Realtime Recommendation Job...")
    env.execute("PyFlink Realtime Recommendation Job: User Recent Views")


if __name__ == '__main__':
    main()