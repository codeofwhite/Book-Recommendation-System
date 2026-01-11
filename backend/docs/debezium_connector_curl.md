## MySQL
- auth_db
```bash
curl -X POST -H "Content-Type: application/json" --data @backend\data-pipeline\cdc\debezium\connectors\mysql_connector.json http://localhost:8083/connectors
```

- mysql_user_engagement_connector:
```bash
curl -X POST -H "Content-Type: application/json" --data @backend\data-pipeline\cdc\debezium\connectors\mysql_user_engagement_connector.json http://localhost:8083/connectors
```

## MongoDB
```bash
curl -X POST -H "Content-Type: application/json" --data @backend\data-pipeline\cdc\debezium\connectors\mongodb_connector.json http://localhost:8083/connectors
```

## ClickHouse
```bash
curl -X POST -H "Content-Type: application/json" --data @backend\data-pipeline\cdc\debezium\connectors\clickhouse_user_behavior_sink_connector.json http://localhost:8083/connectors
```

# 删除指令
```bash
curl -X DELETE http://localhost:8083/connectors/
```

# 查看所有已创建的Connector列表
```bash
curl http://localhost:8083/connectors
```

1. MySQL Connector 状态:
```bash
curl http://localhost:8083/connectors/mysql-auth-connector/status
```

2. MongoDB Connector 状态:
```bash
curl http://localhost:8083/connectors/mongodb-book-connector/status
```

3. ClickHouse Connector 状态:
```bash
curl http://localhost:8083/connectors/clickhouse-user-behavior-logs-sink/status
```