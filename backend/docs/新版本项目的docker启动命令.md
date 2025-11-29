```bash
# 停止服务
docker compose -f compose/base.yml -f compose/auth-service.yml down

# 删除旧数据卷（替换成上面查到的卷名）
docker volume rm compose_auth_mysql_data

# 2. 启动 auth-service 模块（组合 base.yml + 模块.yml，自动创建网络/卷/执行脚本）
docker compose -f compose/base.yml -f compose/auth-service.yml up -d
```

多模块启动
```bash
docker compose \
  -f compose/base.yml \
  -f compose/auth-service.yml \
  -f compose/book-service.yml \
  -f compose/data-pipeline.yml \
  up -d
```

启动所有模块
```bash
# 启动所有核心模块（根据实际模块名调整）
docker compose \
  -f compose/base.yml \
  -f compose/auth-service.yml \
  -f compose/book-service.yml \
  -f compose/user-engagement.yml \
  -f compose/data-pipeline.yml \
  -f compose/recommendation.yml \
  -f compose/storage.yml \
  up -d
```

```bash
# 删除所有项目相关的卷（对应 base.yml 中的 volumes 列表）
docker volume rm \
  auth_mysql_data \
  book_mongo_data \
  zookeeper_data \
  kafka_data \
  recommendation_mysql_data \
  user_engagement_mysql_data \
  clickhouse_data \
  clickhouse_logs \
  redis_data \
  minio_data 2>/dev/null
```