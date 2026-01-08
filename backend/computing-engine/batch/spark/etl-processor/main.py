# main.py
from pyspark.sql import SparkSession
from config import KAFKA_BROKER_URL, SPARK_PACKAGES, SPARK_DRIVER_EXTRA_CLASSPATH
from schemas import mysql_record_schema, mongodb_kafka_envelope_schema
from processors import process_user_data, process_book_data

# 导入新增的 Schema
from schemas import (
    book_favorite_schema,
    review_favorite_schema,
    book_like_schema,
    review_like_schema,
    review_schema,
    comment_schema,
)

# 导入新增的处理器函数
from processors import (
    process_book_favorite_data,
    process_review_favorite_data,
    process_book_like_data,
    process_review_like_data,
    process_review_data,
    process_comment_data,
)


# Spark Session
spark = (
    SparkSession.builder.appName("RecommendationDataETL")
    .config("spark.jars.packages", SPARK_PACKAGES)
    .config("spark.driver.extraClassPath", SPARK_DRIVER_EXTRA_CLASSPATH)
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# --- Kafka 数据源配置函数 ---
def create_kafka_stream(topic_name):
    """
    创建从 Kafka 读取数据的 Spark Structured Streaming DataFrame。

    Args:
        topic_name (str): 要订阅的 Kafka 主题名称。

    Returns:
        pyspark.sql.DataFrame: 从 Kafka 读取的 DataFrame。
    """
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER_URL)
        .option("subscribe", topic_name)
        .option("startingOffsets", "earliest")
        .load()
        .selectExpr("CAST(value AS STRING)")
    )


# 创建数据流
user_stream = create_kafka_stream("auth_db_cdc.auth_db.users")
book_stream = create_kafka_stream("book_db_cdc.book_manage_db.books")

# 创建数据流
book_favorite_stream = create_kafka_stream(
    "user_engagement_db_cdc.book_engagement.BOOK_FAVORITE"
)
review_favorite_stream = create_kafka_stream(
    "user_engagement_db_cdc.book_engagement.REVIEW_FAVORITE"
)
book_like_stream = create_kafka_stream(
    "user_engagement_db_cdc.book_engagement.BOOK_LIKE"
)
review_like_stream = create_kafka_stream(
    "user_engagement_db_cdc.book_engagement.REVIEW_LIKE"
)
review_stream = create_kafka_stream("user_engagement_db_cdc.book_engagement.REVIEW")
comment_stream = create_kafka_stream("user_engagement_db_cdc.book_engagement.COMMENT")

# --- 启动流式查询 ---
# 用户数据流
# 我这里将 spark 对象作为额外参数传递给 foreachBatch 函数
user_query = (
    user_stream.writeStream.foreachBatch(
        lambda df, epoch_id: process_user_data(df, epoch_id, spark)
    )
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .start()
)

# 图书数据流
book_query = (
    book_stream.writeStream.foreachBatch(
        lambda df, epoch_id: process_book_data(df, epoch_id, spark)
    )
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .start()
)

# --- 启动流式查询 (新增部分) ---
book_favorite_query = (
    book_favorite_stream.writeStream.foreachBatch(
        lambda df, epoch_id: process_book_favorite_data(df, epoch_id, spark)
    )
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .start()
)

review_favorite_query = (
    review_favorite_stream.writeStream.foreachBatch(
        lambda df, epoch_id: process_review_favorite_data(df, epoch_id, spark)
    )
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .start()
)

book_like_query = (
    book_like_stream.writeStream.foreachBatch(
        lambda df, epoch_id: process_book_like_data(df, epoch_id, spark)
    )
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .start()
)

review_like_query = (
    review_like_stream.writeStream.foreachBatch(
        lambda df, epoch_id: process_review_like_data(df, epoch_id, spark)
    )
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .start()
)

review_query = (
    review_stream.writeStream.foreachBatch(
        lambda df, epoch_id: process_review_data(df, epoch_id, spark)
    )
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .start()
)

comment_query = (
    comment_stream.writeStream.foreachBatch(
        lambda df, epoch_id: process_comment_data(df, epoch_id, spark)
    )
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .start()
)

print("Spark streaming ETL started. Waiting for data...")
spark.streams.awaitAnyTermination()
