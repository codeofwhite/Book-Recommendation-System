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

curl -X DELETE <http://localhost:8083/connectors/clickhouse-user-behavior-logs-sink>

curl -X POST -H "Content-Type: application/json" --data @clickhouse_user_behavior_sink_connector.json <http://localhost:8083/connectors>

curl <http://localhost:8083/connectors/clickhouse-user-behavior-logs-sink/status> | jq .
