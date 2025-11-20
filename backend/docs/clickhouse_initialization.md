```sql
CREATE DATABASE IF NOT EXISTS user_data;

CREATE TABLE user_data.user_behavior_logs_raw (
    event_id UUID DEFAULT generateUUIDv4(),
    user_id String DEFAULT '', -- <-- 关键修改：将 Nullable(String) 改为 String 并设置默认值
    event_type String,
    client_timestamp DateTime,
    server_receive_time DateTime64(3, 'Asia/Shanghai') DEFAULT now(),
    payload_raw String
)
ENGINE = MergeTree()
ORDER BY (user_id, client_timestamp, event_type)
PARTITION BY toYYYYMM(client_timestamp)
TTL client_timestamp + toIntervalYear(3);
```

# 用下面这个可以
```sql
CREATE TABLE IF NOT EXISTS default.user_behavior_logs_raw (
    event_id UUID DEFAULT generateUUIDv4(),  -- 自动生成 UUID，无需从 Kafka 接收
    user_id String DEFAULT '',               -- 字符串类型，默认空字符串
    event_type String,                       -- 行为类型（如 click/buy/collect）
    client_timestamp DateTime,               -- 客户端时间（需从 Kafka 消息中获取）
    server_receive_time DateTime64(3, 'Asia/Shanghai') DEFAULT now(),  -- 服务端接收时间，自动生成
    payload_raw String                       -- 原始 payload 数据（对应 Kafka 提取的 payload 字段）
)
ENGINE = MergeTree()
ORDER BY (user_id, client_timestamp, event_type)  -- 排序键
PARTITION BY toYYYYMM(client_timestamp)            -- 按年月分区
TTL client_timestamp + toIntervalYear(3);          -- 数据保留 3 年
```

```sql
CREATE TABLE IF NOT EXISTS default.user_behavior_logs (
    event_id UUID DEFAULT generateUUIDv4(),  -- 自动生成 UUID，无需从 Kafka 接收
    user_id String DEFAULT '',               -- 字符串类型，默认空字符串
    event_type String,                       -- 行为类型（如 click/buy/collect）
    client_timestamp DateTime,               -- 客户端时间（需从 Kafka 消息中获取）
    server_receive_time DateTime64(3, 'Asia/Shanghai') DEFAULT now(),  -- 服务端接收时间，自动生成
    payload_raw String                       -- 原始 payload 数据（对应 Kafka 提取的 payload 字段）
)
ENGINE = MergeTree()
ORDER BY (user_id, client_timestamp, event_type)  -- 排序键
PARTITION BY toYYYYMM(client_timestamp)            -- 按年月分区
TTL client_timestamp + toIntervalYear(3);          -- 数据保留 3 年
```

```bash
curl -X DELETE <http://localhost:8083/connectors/clickhouse-user-behavior-logs-sink>
```

```bash
curl -X POST -H "Content-Type: application/json" --data @clickhouse_user_behavior_sink_connector.json <http://localhost:8083/connectors>
```

```bash
curl <http://localhost:8083/connectors/clickhouse-user-behavior-logs-sink/status> | jq .
```