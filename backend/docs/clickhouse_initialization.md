1. ClickHouse 目标表创建

为了接收用户行为数据流，必须在 ClickHouse 中手动创建 user_behavior_logs 表。请执行以下 SQL 语句：

```sql
DROP TABLE IF EXISTS user_behavior_logs; 

CREATE TABLE user_behavior_logs (
    userId UInt32,
    sessionId String,
    eventType String, -- 【关键修正】改为普通 String
    timestamp String,
    pageUrl String,
    payload String,
    event_date Date DEFAULT today(),
    server_receive_time DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, userId);
```

- 删除现有 Sink Connector
```bash
curl -X DELETE http://localhost:8083/connectors/clickhouse-user-behavior-logs-sink
```

- 部署新的 Sink Connector
```bash
curl -X POST -H "Content-Type: application/json" --data @backend\data-pipeline\cdc\debezium\connectors\clickhouse_user_behavior_sink_connector.json http://localhost:8083/connectors
```
