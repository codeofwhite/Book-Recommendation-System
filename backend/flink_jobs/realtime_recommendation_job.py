import os
import json
from datetime import datetime
import logging
import pickle  # 导入 pickle 模块用于状态的序列化/反序列化 (注意：这里仍然用于 Flink 状态的序列化，而不是 Redis 中的向量)
import redis  # 在 Flink Job 内部也需要这个库来连接 Redis
import math    # 新增：导入 math 模块用于纯 Python 的数学运算

from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import KeyedProcessFunction, FlatMapFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common import Row
from pyflink.common import Configuration 

# --- 自定义配置类，所有配置集中在此文件内 ---
class FlinkJobConfig:
    # --- Redis 连接配置 ---
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '') # 新增：Redis 密码

    # --- Redis 键和前缀配置 ---
    # Flink 实时任务存储最近浏览的 Hash Key
    REDIS_RECENT_VIEWS_HASH_KEY = "user_recent_views_hash:" # 保持与 config.py 一致，使用 HASH KEY
    # 离线推荐存储的键前缀，与离线训练服务保持一致
    OFFLINE_RECOMMENDATIONS_KEY_PREFIX = "recommendations:user:"
    # 实时更新后的推荐结果存储的键前缀
    REDIS_REALTIME_UPDATED_RECOMMENDATIONS_PREFIX = os.getenv('REDIS_REALTIME_UPDATED_RECOMMENDATIONS_PREFIX', "realtime_updated_recommendations:user:")
    # 物品特征向量前缀
    REDIS_BOOK_FEATURES_PREFIX = os.getenv("REDIS_BOOK_FEATURES_PREFIX", "book_features:")
    # 用户画像向量前缀
    REDIS_USER_PROFILE_PREFIX = os.getenv("REDIS_USER_PROFILE_PREFIX", "user_profile:")


    # --- Flink 作业参数 ---
    # 实时更新推荐结果在 Redis 中的过期时间（秒）
    RECOMMENDATION_CACHE_EXPIRE_SECONDS = int(os.getenv('RECOMMENDATION_CACHE_EXPIRE_SECONDS', 3600 * 24))
    # 每个用户最多保留的最近浏览记录数量
    MAX_RECENT_VIEWS = int(os.getenv('MAX_RECENT_VIEWS', 20))
    # 从离线推荐中获取的最大数量，用于实时过滤和排序
    MAX_OFFLINE_RECOMMENDATIONS = int(os.getenv('MAX_OFFLINE_RECOMMENDATIONS', 400))
    # 最终输出给前端的推荐数量
    FINAL_RECOMMENDATION_COUNT = int(os.getenv('FINAL_RECOMMENDATION_COUNT', 12))

    # --- 实时推荐融合参数 ---
    # 当用户在图书详情页停留时间超过此阈值时，触发协同过滤 (CF) 权重提升（秒）
    REALTIME_CF_BOOST_DWELL_TIME_THRESHOLD = int(os.getenv('REALTIME_CF_BOOST_DWELL_TIME_THRESHOLD', 30))
    # 当触发 CF 权重提升时，CF 分数的额外增加量 (例如，0.1 表示 CF 权重从 0.7 变为 0.8)
    REALTIME_CF_BOOST_AMOUNT = float(os.getenv('REALTIME_CF_BOOST_AMOUNT', 0.1))
    # 离线推荐中协同过滤 (CF) 分数的默认权重 (与 models/trainer.py 中的 Config.CF_POPULARITY_MIX_ALPHA 保持一致)
    OFFLINE_CF_WEIGHT = float(os.getenv('OFFLINE_CF_WEIGHT', 0.7))
    
    # 协同过滤与内容相似度融合的权重 (与 config.py 中的 SIMILARITY_FUSION_ALPHA 保持一致)
    # 此参数用于融合“离线混合分数”和“综合内容分数”
    SIMILARITY_FUSION_ALPHA = float(os.getenv('SIMILARITY_FUSION_ALPHA', 0.5)) 

    # 新增：实时内容相似度融合权重
    # 用于融合用户画像与推荐物品的相似度，以及当前点击物品与推荐物品的相似度
    # 1.0 意味着只考虑用户画像相似度，0.0 意味着只考虑当前点击物品相似度
    REALTIME_CONTENT_FUSION_ALPHA = float(os.getenv('REALTIME_CONTENT_FUSION_ALPHA', 0.7)) # 默认值0.7，给用户画像更多权重

    # --- Kafka 配置 ---
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'user_behavior_logs')


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
env.enable_checkpointing(60000) # 每 60 秒进行一次检查点，确保状态的持久化和容错性

### JsonParser FlatMapFunction
class JsonParser(FlatMapFunction):
    """
    解析 Kafka 消息中的 JSON 字符串，并将其转换为 Flink Row 对象。
    如果 JSON 解析失败、数据结构不符合预期或缺少关键字段，则该记录会被跳过（不产生输出）。
    """
    def flat_map(self, json_str: str):
        try:
            data = json.loads(json_str)
            user_id = data.get('userId')
            event_type = data.get('eventType')
            timestamp = data.get('timestamp')
            page_url = data.get('pageUrl')
            payload_data = data.get('payload')

            # 检查关键字段是否存在
            if not all([user_id is not None, event_type, timestamp, page_url, payload_data is not None]):
                logger.debug(f"Skipping record: Missing essential fields in JSON: '{json_str}'")
                return

            # 确保 payload 是字典类型
            if not isinstance(payload_data, dict):
                logger.debug(
                    f"Skipping record: 'payload' is not a dictionary for JSON string: '{json_str}'. "
                    f"Payload content: {payload_data}"
                )
                return

            page_name = payload_data.get('pageName')
            dwell_time = payload_data.get('dwellTime')

            # 对 page_name 和 dwell_time 进行类型检查和默认值处理
            if not isinstance(page_name, str):
                page_name = None
            if not isinstance(dwell_time, (int, float)):
                dwell_time = None

            # 构造 Flink Row 对象并输出
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


### UserRecentViewsProcessFunction
class UserRecentViewsProcessFunction(KeyedProcessFunction):
    """
    针对每个用户 ID 进行处理的 KeyedProcessFunction。
    它维护用户的最近浏览状态，并根据最新行为更新离线推荐结果。
    """
    def open(self, runtime_context):
        # 初始化 Redis 客户端
        self.redis_client = None
        try:
            self.redis_client = redis.StrictRedis(
                host=FlinkJobConfig.REDIS_HOST,
                port=FlinkJobConfig.REDIS_PORT,
                db=FlinkJobConfig.REDIS_DB,
                password=FlinkJobConfig.REDIS_PASSWORD, # 使用密码
                decode_responses=False # 不自动解码，因为从 Redis 获取的 JSON 字符串需要手动解码
            )
            self.redis_client.ping()
            logger.info(f"[{runtime_context.get_task_name()}] Successfully connected to Redis at {FlinkJobConfig.REDIS_HOST}:{FlinkJobConfig.REDIS_PORT}!")
        except Exception as e:
            logger.error(f"[{runtime_context.get_task_name()}] Error connecting to Redis at {FlinkJobConfig.REDIS_HOST}:{FlinkJobConfig.REDIS_PORT}: {e}")
            self.redis_client = None

        # 定义并获取 ValueState，用于存储每个用户的最近浏览列表
        # 使用 Types.PICKLED_BYTE_ARRAY() 来存储序列化后的 Python 对象（列表）
        self.recent_views_state = runtime_context.get_state(
            ValueStateDescriptor(
                "recent_views_list_state",
                Types.PICKLED_BYTE_ARRAY()
            )
        )
        self.MAX_RECENT_VIEWS = FlinkJobConfig.MAX_RECENT_VIEWS
        self.MAX_OFFLINE_RECOMMENDATIONS = FlinkJobConfig.MAX_OFFLINE_RECOMMENDATIONS
        self.FINAL_RECOMMENDATION_COUNT = FlinkJobConfig.FINAL_RECOMMENDATION_COUNT

        # 缓存用户画像和物品特征向量 (在 TaskManager 生命周期内复用，避免频繁查询 Redis)
        # 注意：这里仅作示例，如果特征向量经常更新，需要考虑更复杂的缓存策略或定时刷新。
        self.user_profile_cache = {} # {user_id: list_of_floats}
        self.book_features_cache = {} # {book_id: list_of_floats}

    def _get_user_profile_vector(self, user_id):
        """从 Redis 或缓存获取用户画像向量 (返回纯 Python 列表)。"""
        if user_id in self.user_profile_cache:
            return self.user_profile_cache[user_id]

        user_profile_key = f"{FlinkJobConfig.REDIS_USER_PROFILE_PREFIX}{user_id}"
        user_profile_bytes = self.redis_client.get(user_profile_key)
        if user_profile_bytes:
            try:
                # 假设 Redis 中存储的是 JSON 字符串，需要先解码
                profile_vector = json.loads(user_profile_bytes.decode('utf-8'))
                if isinstance(profile_vector, list):
                    self.user_profile_cache[user_id] = profile_vector
                    return profile_vector
                else:
                    logger.warning(f"User profile for {user_id} is not a list after JSON decoding. Type: {type(profile_vector)}")
                    return None
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to decode user profile JSON for {user_id}: {e}", exc_info=True)
                return None
        else:
            logger.debug(f"User profile not found for {user_id} at key {user_profile_key}.")
            return None

    def _get_book_feature_vector(self, book_id):
        """从 Redis 或缓存获取书籍特征向量 (返回纯 Python 列表)。"""
        if book_id in self.book_features_cache:
            return self.book_features_cache[book_id]

        book_feature_key = f"{FlinkJobConfig.REDIS_BOOK_FEATURES_PREFIX}{book_id}"
        book_features_bytes = self.redis_client.get(book_feature_key)
        if book_features_bytes:
            try:
                # 假设 Redis 中存储的是 JSON 字符串，需要先解码
                feature_vector = json.loads(book_features_bytes.decode('utf-8'))
                if isinstance(feature_vector, list):
                    self.book_features_cache[book_id] = feature_vector
                    return feature_vector
                else:
                    logger.warning(f"Book features for {book_id} is not a list after JSON decoding. Type: {type(feature_vector)}")
                    return None
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to decode book features JSON for {book_id}: {e}", exc_info=True)
                return None
        else:
            logger.debug(f"Book features not found for {book_id} at key {book_feature_key}.")
            return None

    def _cosine_similarity(self, vec1_list, vec2_list):
        """计算两个向量的余弦相似度（纯 Python 实现）。"""
        if not vec1_list or not vec2_list or len(vec1_list) != len(vec2_list):
            logger.debug(f"Cannot compute cosine similarity: Vectors are empty or have different lengths. Vec1 len: {len(vec1_list) if vec1_list else 0}, Vec2 len: {len(vec2_list) if vec2_list else 0}")
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1_list, vec2_list))
        norm_a = math.sqrt(sum(a**2 for a in vec1_list))
        norm_b = math.sqrt(sum(b**2 for b in vec2_list))

        if norm_a == 0 or norm_b == 0:
            logger.debug("Cannot compute cosine similarity: One or both vector norms are zero.")
            return 0.0
        return dot_product / (norm_a * norm_b)

    def process_element(self, value: Row, ctx: 'KeyedProcessFunction.Context'):
        if self.redis_client is None:
            logger.error(f"Redis client is not initialized for user {value.userId}. Cannot process element: {value}")
            return

        try:
            user_id = value.userId
            event_type = value.eventType
            timestamp_str = value.timestamp
            payload_row = value.payload

            # 获取当前事件的 item_id 和 dwellTime
            current_item_id = None
            current_dwell_time = getattr(payload_row, 'dwellTime', None)
            page_name = getattr(payload_row, 'pageName', None)

            # 1. 解析时间戳
            try:
                if timestamp_str.endswith('Z'):
                    dt_object = datetime.fromisoformat(timestamp_str[:-1] + '+00:00')
                else:
                    dt_object = datetime.fromisoformat(timestamp_str)
                event_timestamp_ms = int(dt_object.timestamp() * 1000)
            except (ValueError, TypeError) as e:
                event_timestamp_ms = int(datetime.utcnow().timestamp() * 1000) # 解析失败时使用当前 UTC 时间
                logger.warning(
                    f"Could not parse timestamp '{timestamp_str}' for user {user_id}. "
                    f"Error: {e}. Using current UTC time as fallback."
                )

            # 提取 item_id，只针对图书详情页的 page_view 事件
            if event_type == 'page_view' and isinstance(page_name, str) and page_name == 'BookDetails':
                page_url = value.pageUrl
                if page_url:
                    parts = page_url.split('/')
                    if len(parts) >= 2 and parts[-2] == 'books' and parts[-1]:
                        current_item_id = parts[-1]
                else:
                    logger.debug(f"pageUrl is missing for page_view event for user {user_id}. Skipping item_id extraction.")

            if not current_item_id:
                logger.debug(f"Skipping event: No valid item_id found for event: {value}")
                return # 如果没有有效的 item_id，则不进行后续的推荐更新

            # 2. 更新用户的最近浏览状态 (在 Flink 状态和 Redis 中同步更新)
            current_views_pickled = self.recent_views_state.value()
            current_views_list = []
            if current_views_pickled is not None:
                try:
                    # 反序列化 Flink 状态中的最近浏览列表
                    current_views_json_str = pickle.loads(current_views_pickled)
                    current_views_list = json.loads(current_views_json_str)
                    if not isinstance(current_views_list, list):
                        logger.warning(f"Recent views state for user {user_id} is not a list after deserialization. Resetting.")
                        current_views_list = []
                except (pickle.UnpicklingError, json.JSONDecodeError, TypeError) as e:
                    logger.error(f"Failed to deserialize recent views state for user {user_id}: {e}. Resetting state.", exc_info=True)
                    current_views_list = []

            new_view = {'item_id': current_item_id, 'timestamp': event_timestamp_ms}
            current_views_list = [view for view in current_views_list if view.get('item_id') != current_item_id] # 移除旧的相同 item_id
            current_views_list.append(new_view)
            current_views_list = sorted(current_views_list, key=lambda x: x.get('timestamp', 0), reverse=True)[:self.MAX_RECENT_VIEWS]

            # 更新 Flink 状态
            self.recent_views_state.update(pickle.dumps(json.dumps(current_views_list, ensure_ascii=False)))

            # 同时更新 Redis 中的最近浏览记录 (使用 HSET 将用户 ID 作为字段存储在统一的 Hash 中)
            self.redis_client.hset(
                FlinkJobConfig.REDIS_RECENT_VIEWS_HASH_KEY,
                str(user_id), # Redis Hash 的字段是用户 ID
                json.dumps(current_views_list, ensure_ascii=False) # Redis Hash 的值是最近浏览列表的 JSON 字符串
            )
            logger.info(f"[{ctx.get_current_key()}] Updated recent views for user {user_id}. Current views count: {len(current_views_list)}")

            # --- 3. 从 Redis 获取离线推荐结果 ---
            offline_recs_key = f"{FlinkJobConfig.OFFLINE_RECOMMENDATIONS_KEY_PREFIX}{user_id}"
            offline_recs_json = self.redis_client.get(offline_recs_key)
            offline_recommendations = []

            if offline_recs_json:
                try:
                    offline_recommendations = json.loads(offline_recs_json)
                    logger.debug(f"Retrieved {len(offline_recommendations)} offline recommendations for user {user_id}.")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode offline recommendations JSON for user {user_id}: {e}. Raw: {offline_recs_json}", exc_info=True)
                except Exception as e:
                    logger.error(f"Error processing offline recommendations for user {user_id}: {e}", exc_info=True)
            else:
                logger.info(f"No offline recommendations found for user {user_id} at key {offline_recs_key}. Using empty list.")

            # --- 4. 实时逻辑：结合用户最新行为更新离线推荐 ---
            # a) 过滤掉用户最近浏览过的商品
            recent_item_ids = {view.get('item_id') for view in current_views_list if view.get('item_id')}
            filtered_offline_recs = []
            for rec_item in offline_recommendations:
                rec_item_id = rec_item.get('book_id') or rec_item.get('item_id') # 适配不同的命名
                if rec_item_id and rec_item_id not in recent_item_ids:
                    filtered_offline_recs.append(rec_item)
                else:
                    logger.debug(f"Filtering out recently viewed item {rec_item_id} from offline recommendations for user {user_id}.")

            logger.debug(f"After filtering recent views, {len(filtered_offline_recs)} recommendations remain for user {user_id}.")

            # b) 基于当前事件的 dwellTime 动态调整 CF 和流行度权重
            realtime_cf_weight = FlinkJobConfig.OFFLINE_CF_WEIGHT
            realtime_popularity_weight = 1.0 - FlinkJobConfig.OFFLINE_CF_WEIGHT

            # 如果当前是图书详情页浏览事件，且停留时间超过阈值，则提升 CF 权重
            if event_type == 'page_view' and page_name == 'BookDetails' and current_dwell_time is not None and current_dwell_time >= FlinkJobConfig.REALTIME_CF_BOOST_DWELL_TIME_THRESHOLD:
                realtime_cf_weight = min(1.0, FlinkJobConfig.OFFLINE_CF_WEIGHT + FlinkJobConfig.REALTIME_CF_BOOST_AMOUNT)
                realtime_popularity_weight = 1.0 - realtime_cf_weight # 确保权重和为1
                logger.info(f"User {user_id} viewed {current_item_id} with high dwell time ({current_dwell_time}s). Boosting CF weight to {realtime_cf_weight:.2f}.")
            else:
                logger.debug(f"User {user_id} event (type: {event_type}, dwell: {current_dwell_time}s) not triggering CF boost. Weights remain default.")

            # --- c) 获取用户画像向量和当前浏览书籍的特征向量 ---
            user_profile_vec = self._get_user_profile_vector(user_id)
            # 获取当前点击书籍的特征向量
            current_book_feature_vec = self._get_book_feature_vector(current_item_id) 

            # 为每个推荐项计算新的实时分数
            for rec_item in filtered_offline_recs:
                rec_book_id = rec_item.get('book_id') or rec_item.get('item_id') # 确保使用正确的 ID
                raw_cf = rec_item.get('raw_cf_score', 0.0)
                raw_pop = rec_item.get('raw_popularity_score', 0.0)

                # 确保 raw_cf 和 raw_pop 是浮点数
                try:
                    raw_cf = float(raw_cf)
                except (ValueError, TypeError):
                    raw_cf = 0.0
                try:
                    raw_pop = float(raw_pop)
                except (ValueError, TypeError):
                    raw_pop = 0.0

                # 获取离线推荐的原始总分（通常是协同过滤和流行度的混合）
                offline_mixed_score = rec_item.get('score', (realtime_cf_weight * raw_cf) + (realtime_popularity_weight * raw_pop))
                try:
                    offline_mixed_score = float(offline_mixed_score)
                except (ValueError, TypeError):
                    offline_mixed_score = 0.0

                # --- 1. 计算基于用户画像的内容相似度 ---
                user_profile_content_similarity = 0.0
                if user_profile_vec is not None and rec_book_id is not None:
                    rec_book_feature_vec_for_profile = self._get_book_feature_vector(rec_book_id)
                    if rec_book_feature_vec_for_profile is not None:
                        user_profile_content_similarity = self._cosine_similarity(user_profile_vec, rec_book_feature_vec_for_profile)
                        logger.debug(f"User {user_id} profile to book {rec_book_id} content similarity: {user_profile_content_similarity:.4f}")
                    else:
                        logger.debug(f"No book feature vector found for recommended book {rec_book_id} for user profile sim. Content similarity will be 0.")
                else:
                    logger.debug(f"User profile ({'None' if user_profile_vec is None else 'Exists'}) or recommended book ID ({'None' if rec_book_id is None else 'Exists'}) is missing for user profile sim. Content similarity skipped.")

                # --- 2. 计算基于当前点击物品的内容相似度 ---
                last_clicked_item_content_similarity = 0.0
                # 只有当 current_item_id 有效且其特征向量可获取时才计算
                if current_item_id and current_book_feature_vec is not None and rec_book_id is not None:
                    rec_book_feature_vec_for_last_clicked = self._get_book_feature_vector(rec_book_id)
                    if rec_book_feature_vec_for_last_clicked is not None:
                        last_clicked_item_content_similarity = self._cosine_similarity(current_book_feature_vec, rec_book_feature_vec_for_last_clicked)
                        logger.debug(f"Last clicked item ({current_item_id}) to book {rec_book_id} content similarity: {last_clicked_item_content_similarity:.4f}")
                    else:
                        logger.debug(f"No book feature vector found for recommended book {rec_book_id} for last clicked sim. Content similarity will be 0.")
                else:
                    logger.debug(f"Last clicked item ({'None' if current_item_id is None else current_item_id}) or its features ({'None' if current_book_feature_vec is None else 'Exists'}) or recommended book ID ({'None' if rec_book_id is None else 'Exists'}) is missing for last clicked sim. Content similarity skipped.")

                # --- 3. 融合两种内容相似度，得到综合内容分数 ---
                # FlinkJobConfig.REALTIME_CONTENT_FUSION_ALPHA 控制用户画像相似度 (Profile Sim) 的权重
                # (1.0 - FlinkJobConfig.REALTIME_CONTENT_FUSION_ALPHA) 控制最新点击物品相似度 (Last Click Sim) 的权重
                combined_content_score = (
                    FlinkJobConfig.REALTIME_CONTENT_FUSION_ALPHA * user_profile_content_similarity +
                    (1.0 - FlinkJobConfig.REALTIME_CONTENT_FUSION_ALPHA) * last_clicked_item_content_similarity
                )
                logger.debug(f"Item {rec_book_id} combined content score: {combined_content_score:.4f} (Profile Sim: {user_profile_content_similarity:.4f}, Last Click Sim: {last_clicked_item_content_similarity:.4f})")

                # --- 4. 最终实时分数的融合 ---
                # FlinkJobConfig.SIMILARITY_FUSION_ALPHA 控制“综合内容分数”的权重
                # (1.0 - FlinkJobConfig.SIMILARITY_FUSION_ALPHA) 控制“离线混合分数”的权重
                rec_item['realtime_score'] = (FlinkJobConfig.SIMILARITY_FUSION_ALPHA * combined_content_score) + \
                                             ((1.0 - FlinkJobConfig.SIMILARITY_FUSION_ALPHA) * offline_mixed_score)
                
                logger.debug(f"Item {rec_book_id} realtime_score: {rec_item['realtime_score']:.4f} (Combined Content: {combined_content_score:.4f}, Offline Mix: {offline_mixed_score:.4f})")

            # c) 重新排序并截断最终推荐列表
            final_recommendations = sorted(filtered_offline_recs, key=lambda x: x.get('realtime_score', 0.0), reverse=True)
            final_recommendations = final_recommendations[:self.FINAL_RECOMMENDATION_COUNT]

            # 5. 将最终的实时更新推荐列表写回 Redis
            final_recs_redis_key = f"{FlinkJobConfig.REDIS_REALTIME_UPDATED_RECOMMENDATIONS_PREFIX}{user_id}"

            self.redis_client.setex(
                final_recs_redis_key,
                FlinkJobConfig.RECOMMENDATION_CACHE_EXPIRE_SECONDS,
                json.dumps(final_recommendations, ensure_ascii=False).encode('utf-8') # Redis 存储为字节，确保非 ASCII 字符正确编码
            )
            logger.info(f"[{ctx.get_current_key()}] Stored {len(final_recommendations)} real-time updated recommendations for user {user_id} at key: {final_recs_redis_key}.")


        except Exception as e:
            logger.error(f"Error processing element {value} for key {ctx.get_current_key()}: {e}", exc_info=True)


### `main` 函数
def main():
    # 设置 Flink 作业为流处理模式
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    # 设置并行度，可以根据集群资源调整，例如设置为 Kafka topic 的分区数
    env.set_parallelism(1)

    # 构建 Kafka Source 连接器
    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers(FlinkJobConfig.KAFKA_BOOTSTRAP_SERVERS) \
        .set_topics(FlinkJobConfig.KAFKA_TOPIC) \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    # 定义 Kafka 消息解析后的 Flink Row 类型信息
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

    # 从 Kafka Source 读取数据流，并使用 JsonParser 进行解析
    data_stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(), # 简单示例，不使用水印
        source_name="Kafka User Behavior Logs Source",
        type_info=Types.STRING()
    ).flat_map(
        JsonParser(),
        output_type=json_row_type_info
    )

    # 对数据流按 userId 进行 KeyBy 操作，确保同一用户的事件由同一个 Task 处理，以便维护状态
    # 然后应用 UserRecentViewsProcessFunction 进行实时处理
    data_stream \
        .key_by(lambda x: x.userId, key_type=Types.INT()) \
        .process(UserRecentViewsProcessFunction())

    logger.info("Starting PyFlink Realtime User Recent Views Aggregation and Hybrid Recommendation Job...")
    # 执行 Flink 作业，并指定作业名称
    env.execute("PyFlink Realtime User Recent Views Aggregator and Hybrid Recommendation")


if __name__ == '__main__':
    main()
