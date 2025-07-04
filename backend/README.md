# 前提条件
1. 方法一：安装 Windows Docker Desktop。安装 WSL，然后开发环境选择 Ubuntu。
2. 方法二：安装 Windows Docker Desktop。直接在 Windows 上开发也无所谓。

# 怎么用这个后端？
1. 首先命令行 cd 到 backend
2. 使用命令 启动 docker 服务
```bash
docker compose up -d --build
```
3. 查看你的 Docker Destop 然后可以看到各个微服务的启动
4. cd 到 frontend 里面，写入命令
```bash
npm run dev
```
5. 结束！可以看到完整的页面显示了

# 1. 进入 Kafka 容器
docker exec -it kafka bash

查看 Kafka topic：docker exec kafka kafka-topics --bootstrap-server kafka:29092 --list
创建 docker exec kafka kafka-topics --create --topic user_book_interactions --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1
发送 kafka-console-producer --topic user_book_interactions --bootstrap-server kafka:29092
看数据 docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:29092 --topic user_book_interactions --from-beginning --max-messages 5

{"user_id": "user_A", "item_id": "book_001", "event_type": "view", "timestamp": 1678886400}
{"user_id": "user_B", "item_id": "book_002", "event_type": "view", "timestamp": 1678886410}
{"user_id": "user_A", "item_id": "book_003", "event_type": "view", "timestamp": 1678886420}
{"user_id": "user_C", "item_id": "book_004", "event_type": "view", "timestamp": 1678886430}
{"user_id": "user_B", "item_id": "book_005", "event_type": "view", "timestamp": 1678886440}
{"user_id": "user_A", "item_id": "book_001", "event_type": "view", "timestamp": 1678886450}
{"user_id": "user_A", "item_id": "book_006", "event_type": "view", "timestamp": 1678886460}
{"user_id": "user_A", "item_id": "book_007", "event_type": "view", "timestamp": 1678886470}
{"user_id": "user_D", "item_id": "book_008", "event_type": "view", "timestamp": 1678886480}
{"user_id": "user_A", "item_id": "book_009", "event_type": "view", "timestamp": 1678886490}
{"user_id": "user_A", "item_id": "book_010", "event_type": "view", "timestamp": 1678886500}