-----

## Kafka 操作指南

本指南将演示如何在 Docker 容器中执行常见的 Kafka 操作，包括进入容器、管理 Topic 以及发送和查看消息。

-----

### 1\. 进入 Kafka 容器

要与 Kafka 容器进行交互，首先需要进入它的 shell 环境。

```bash
docker exec -it kafka bash
```

-----

### 2\. 管理 Kafka Topics

#### 查看现有 Topic

列出 Kafka 集群中所有可用的 Topic。

```bash
docker exec kafka kafka-topics --bootstrap-server kafka:29092 --list
```

#### 创建新 Topic

创建一个名为 `user_book_interactions` 的新 Topic，并设置分区和副本因子。

```bash
docker exec kafka kafka-topics --create --topic user_book_interactions --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1
```

-----

### 3\. 发送数据到 Topic

使用 `kafka-console-producer` 向 `user_book_interactions` Topic 发送消息。启动此命令后，您可以在控制台输入消息，每行一条。

```bash
docker exec -it kafka kafka-console-producer --topic user_book_interactions --bootstrap-server kafka:29092
```

-----

### 4\. 查看 Topic 数据

使用 `kafka-console-consumer` 从 `user_book_interactions` Topic 消费消息。`--from-beginning` 表示从 Topic 的起始位置开始读取，`--max-messages 5` 则限制只显示最新的 5 条消息。

```bash
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:29092 --topic user_book_interactions --from-beginning --max-messages 5
```

以下是发送到 Kafka Topic 的示例数据格式：

```json
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
```
