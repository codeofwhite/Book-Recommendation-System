## 项目后端文件结构与使用指南

本部分将详细介绍 `backend` 目录下的文件结构以及如何启动和使用整个推荐系统后端服务。

-----

### 1\. 文件目录概览

以下是 `backend` 目录下主要的文件和子目录：

  * **文档与配置**

      * `ClickHouse 初始化.md`: ClickHouse 数据库的初始化配置说明。
      * `README.md`: 后端项目的简介文档。
      * `curl.txt`: 示例 `curl` 命令集合，可能用于 API 测试。
      * `hadoop.env`: Hadoop 相关的环境变量配置。
      * `mysql_connector.json`: MySQL 连接器配置。
      * `mongodb_connector.json`: MongoDB 连接器配置。
      * `clickhouse_user_behavior_sink_connector.json`: ClickHouse 用户行为数据汇流连接器配置。
      * `mysql-user-engagement-connector.json`: MySQL 用户互动数据连接器配置。

  * **数据库初始化脚本**

      * `init_debezium_user.sql`: Debezium 用户表初始化脚本。
      * `init_debezium_user_engagement.sql`: Debezium 用户互动表初始化脚本。
      * `init_recommendation_db.sql`: 推荐系统数据库初始化脚本。

  * **Docker 相关**

      * `docker-compose.yml`: Docker Compose 配置文件，用于定义和运行多容器 Docker 应用。
      * `namenode-entrypoint.sh*`: HDFS Namenode 容器的启动脚本。
      * `mongo_custom_image/`: 用于构建自定义 MongoDB Docker 镜像的目录。
      * `flink_py_image/`: 用于构建 Flink Python 环境 Docker 镜像的目录。

  * **数据处理与集成**

      * `datax_jobs/`: DataX 数据同步任务配置目录。
      * `datax_logs/`: DataX 任务日志目录。
      * `datax_worker/`: DataX Worker 相关文件。
      * `flink_jars/`: Flink 作业的 JAR 包存放目录。
      * `flink_jobs/`: Flink 作业代码目录。
      * `spark_etl_processor/`: Spark ETL 处理相关的代码和配置。
      * `clickhouse-clickhouse-kafka-connect-v1.3.1/`: ClickHouse Kafka 连接器相关文件。

  * **微服务**

      * `auth_service/`: 认证服务模块。
      * `log_service/`: 日志服务模块。
      * `book_manage/`: 图书管理服务模块。
      * `user_engagement_service/`: 用户互动服务模块。
      * `offline_recommendation_service/`: 离线推荐服务模块。
      * `realtime_recommendation_service/`: 实时推荐服务模块。

-----

### 2\. 前提条件

在启动后端服务之前，请确保您的开发环境满足以下条件：

  * **方法一 (推荐):** 安装 **Windows Docker Desktop**。在 WSL (Windows Subsystem for Linux) 中安装 **Ubuntu** 作为您的开发环境。
  * **方法二:** 如果您更倾向于直接在 Windows 环境下开发，也可以直接安装 **Windows Docker Desktop**。

-----

### 3\. 如何使用后端服务

请按照以下步骤启动和运行整个后端服务及前端应用：

1.  **进入后端目录:**
    打开您的命令行工具（如 WSL Ubuntu 或 PowerShell），然后导航到 `backend` 目录：

    ```bash
    cd ~/book-recommendation-system/Book-Recommendation-System/backend/
    ```

2.  **启动 Docker 服务:**
    使用 Docker Compose 启动所有后端微服务和相关基础设施。`--build` 参数确保会重新构建任何有更新的镜像。

    ```bash
    docker compose up -d --build
    ```

3.  **验证服务状态:**
    打开 **Docker Desktop** 应用程序，您应该能看到所有微服务容器已成功启动并正在运行。

4.  **启动前端应用:**
    进入前端项目目录，并使用 npm 启动前端开发服务器：

    ```bash
    cd ../frontend/ # 从 backend 目录返回到项目根目录，再进入 frontend
    npm run dev
    ```

5.  **完成\!**
    现在，您可以通过浏览器访问前端页面，并开始与完整的推荐系统进行交互了。
