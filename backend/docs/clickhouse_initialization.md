# 用下面这个可以，创建这个表
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

- 删除 connector 操作
```bash
curl -X DELETE http://localhost:8083/connectors/clickhouse-user-behavior-logs-sink
```

- 添加 connecotr 操作
```bash
curl -X POST -H "Content-Type: application/json" --data @backend\data-pipeline\cdc\debezium\connectors\clickhouse_user_behavior_sink_connector.json http://localhost:8083/connectors
```