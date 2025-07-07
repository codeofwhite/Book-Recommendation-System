# config.py
import os

# 从环境变量获取数据库和 Kafka 配置
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka:29092")
REC_DB_HOST = os.getenv("REC_DB_HOST", "recommendation_db")
REC_DB_USER = os.getenv("REC_DB_USER", "rec_user")
REC_DB_PASSWORD = os.getenv("REC_DB_PASSWORD", "rec_password")
REC_DB_NAME = os.getenv("REC_DB_NAME", "recommendation_db")

# JDBC URL for MySQL Recommendation DB
REC_DB_JDBC_URL = f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"

# Spark 包依赖
SPARK_PACKAGES = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,mysql:mysql-connector-java:8.0.28,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1"
# Spark 驱动额外类路径
SPARK_DRIVER_EXTRA_CLASSPATH = "/opt/bitnami/spark/jars/mysql-connector-java-8.0.28.jar:/opt/bitnami/spark/jars/mongo-spark-connector_2.12-3.0.1.jar"
