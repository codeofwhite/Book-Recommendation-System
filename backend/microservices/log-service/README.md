## 用户行为日志处理与推荐系统数据流架构

本文档概述了前端用户行为日志的采集、传输和处理策略，旨在构建一个统一的数据管道以同时支持**准实时**和**离线**推荐系统。

### 1\. 整体数据流策略

核心思路是将前端日志从简单的本地存储模式升级为**集中式、可消费的数据流**。所有前端行为日志将统一发布到 **Apache Kafka** 消息队列，作为推荐系统数据处理的单一可信来源。

| 推荐类型 | 数据源 | 消费者 | 存储/服务 |
| :--- | :--- | :--- | :--- |
| **实时推荐 (NRT)** | Kafka `user_behavior_logs` | **Flink Streaming** | Redis（实时特征/推荐结果） |
| **离线推荐 (Batch)** | Kafka (通过 Connect) | **ClickHouse/HDFS & Spark** | OLAP 仓库/HDFS（历史数据） |

-----

### 2\. 具体实施步骤与数据流向细节

#### 2.1. 📤 前端日志采集与入队：`receive_frontend_log` 服务

当前的 Flask 服务（`receive_frontend_log`）将功能重心从文件写入转移到 **Kafka 生产**。

  * **职责变更：** 接收前端 POST 请求的日志数据，并立即将其发送至 Kafka Topic。
  * **Kafka Producer 配置：**
      * 在 Flask 应用中实例化 `KafkaProducer`，并配置 JSON 序列化器。
      * **目标 Topic：** `user_behavior_logs`。
      * *（保留文件写入作为调试或本地备份的次要功能。）*

**代码示例要点 (Python/Flask):**

  * 引入 `KafkaProducer`。
  * 使用环境变量 `KAFKA_BROKER_URL`（例如 `kafka:29092`）确保容器间连接。
  * 在 `receive_frontend_log` 函数中，使用 `producer.send(topic_name, log_data)` 实现数据入队。

**Docker Compose 更新要点:**

  * 添加独立的 `log_service` 定义，并配置其依赖于 `kafka` 服务的健康状态。
  * 暴露服务端口（例如 `5006:5006`）并设置 `KAFKA_BROKER_URL` 环境变量。

<!-- end list -->

```yaml
  # New Log Ingestion Service (Frontend Logs to Kafka)
  log_service:
    build: ./log_service
    container_name: frontend_log_ingestion
    ports:
      - "5006:5006"
    environment:
      KAFKA_BROKER_URL: kafka:29092
    depends_on:
      kafka:
        condition: service_healthy
    networks:
      - default
```

#### 2.2. ⚡ 实时推荐数据流：Flink 与 Redis

采用 **Apache Flink** 构建低延迟的数据处理管道，支持准实时推荐。

  * **实时消费：** Flink 作业（例如 `realtime_recommendation_job.py`）消费 `user_behavior_logs` Kafka Topic。
  * **实时特征工程：** 在 Flink 中执行轻量级、窗口化的特征计算，包括：
      * 用户**短期兴趣**（例如，最近 N 分钟内的浏览/点击类别分布）。
      * **商品热度**的即时波动追踪。
      * 用户最近浏览的 N 个商品列表。
  * **结果存储与服务：** 实时计算得到的推荐列表（`user_id` $\rightarrow$ `[book_id1, ...]`）直接存储到 **Redis** 高速缓存中，供 **`realtime_recommendation_service`** 快速查询和响应前端。

#### 2.3. ⏳ 离线推荐数据流：Spark 与数据仓库

利用 Spark 进行复杂的批量处理和模型训练，以支持深度推荐。

1.  **数据持久化至数据仓库 (DW/DL):**

      * **Kafka Connect Sink：** 使用 **ClickHouse Sink Connector** 将 **`user_behavior_logs`** Topic 的数据流以及 **Debezium** 捕获的数据库变更日志（来自 `auth_db`, `book_db_mongo`, `user_engagement_db`）实时同步到 **ClickHouse**（作为 OLAP/事件日志数据仓库）。
      * ClickHouse 适合存储和高效查询海量事件日志，为离线特征计算提供基础。

2.  **Spark 批量处理 (ETL Processor):**

      * **离线特征工程：** Spark ETL Processor 读取 ClickHouse/HDFS 中的**全量历史数据**，进行复杂的特征计算：
          * 构建用户**长期兴趣画像**。
          * 计算书籍的长期流行度和活跃度。
          * 构建用户-物品交互矩阵。
      * **模型训练：** 使用 **Spark MLlib** 或其他框架训练复杂的离线推荐模型（如矩阵分解、深度学习模型）。

3.  **结果服务化：**

      * 将训练好的推荐结果（如全量用户推荐列表、物品相似度矩阵）存储到 **`recommendation_db` (MySQL)**，作为 **`offline_recommendation_service`** 的数据源。