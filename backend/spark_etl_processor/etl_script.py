import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, TimestampType, DoubleType, BooleanType

# 从环境变量获取数据库和 Kafka 配置
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka:29092")
REC_DB_HOST = os.getenv("REC_DB_HOST", "recommendation_db")
REC_DB_USER = os.getenv("REC_DB_USER", "rec_user")
REC_DB_PASSWORD = os.getenv("REC_DB_PASSWORD", "rec_password")
REC_DB_NAME = os.getenv("REC_DB_NAME", "recommendation_db")

# JDBC URL for MySQL Recommendation DB
REC_DB_JDBC_URL = f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"

# Spark Session
spark = SparkSession.builder \
    .appName("RecommendationDataETL") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,mysql:mysql-connector-java:8.0.28,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .config("spark.driver.extraClassPath", "/opt/bitnami/spark/jars/mysql-connector-java-8.0.28.jar:/opt/bitnami/spark/jars/mongo-spark-connector_2.12-3.0.1.jar") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- 定义 Kafka 消息的 Schema ---
# Debezium 产生的 MySQL binlog 事件通常包含 'before' 和 'after' 字段
# 根据你提供的 auth_db.users 表结构进行调整
mysql_record_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StructType([ # before 和 after 的结构应该相同
            StructField("id", IntegerType(), True),
            StructField("username", StringType(), True),
            StructField("email", StringType(), True),
            StructField("password_hash", StringType(), True),
            StructField("avatar_url", StringType(), True) # 新增字段
        ]), True),
        StructField("after", StructType([
            StructField("id", IntegerType(), True),         # 匹配 MySQL 的 'id' 字段
            StructField("username", StringType(), True),     # 匹配 MySQL 的 'username' 字段
            StructField("email", StringType(), True),        # 匹配 MySQL 的 'email' 字段
            StructField("password_hash", StringType(), True),# 匹配 MySQL 的 'password_hash' 字段
            StructField("avatar_url", StringType(), True)    # 新增字段
        ]), True), # New value (for inserts/updates)
        StructField("source", StringType(), True),
        StructField("op", StringType(), True), # Operation type: 'c' (create), 'u' (update), 'd' (delete), 'r' (read - snapshot)
        StructField("ts_ms", LongType(), True) # Timestamp
    ]), True)
])

# MongoDB Debezium 消息的 Schema - payload.after 是一个JSON字符串
# 我们需要定义这个JSON字符串内部的Schema
actual_mongodb_data_schema = StructType([
    StructField("_id", StructType([StructField("oid", StringType(), True)]), True),
    StructField("bookId", StringType(), True), # 注意：这里是 "bookId" (驼峰命名)
    StructField("title", StringType(), True),
    StructField("category", StringType(), True),
    StructField("series", StringType(), True), 
    StructField("author", StringType(), True), 
    StructField("rating", DoubleType(), True), 
    StructField("description", StringType(), True), 
    StructField("language", StringType(), True), 
    StructField("isbn", StringType(), True), 
    StructField("genres", StringType(), True), 
    StructField("characters", StringType(), True), 
    StructField("bookFormat", StringType(), True), 
    StructField("edition", StringType(), True), 
    StructField("pages", IntegerType(), True), 
    StructField("publisher", StringType(), True), 
    StructField("publishDate", StringType(), True), 
    StructField("firstPublishDate", StringType(), True), 
    StructField("awards", StringType(), True), 
    StructField("numRatings", LongType(), True), 
    StructField("ratingsByStars", StringType(), True), 
    StructField("likedPercent", DoubleType(), True), 
    StructField("setting", StringType(), True), 
    StructField("coverImg", StringType(), True), 
    StructField("bbeScore", LongType(), True), 
    StructField("bbeVotes", LongType(), True), 
    StructField("price", DoubleType(), True) 
])

# 外部的 Kafka 消息 Schema
mongodb_kafka_envelope_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StringType(), True), 
        StructField("after", StringType(), True),  
        StructField("op", StringType(), True),
        StructField("ts_ms", LongType(), True),
        StructField("source", StringType(), True) 
    ]), True)
])

# --- 数据流处理函数 ---
def process_user_data(df, epoch_id):
    """处理用户数据，加载到 Recommendation DB 的 user 表"""
    print(f"Processing user data in batch {epoch_id}...")
    
    # 过滤操作类型并提取数据
    users_df = df.select(from_json(col("value").cast("string"), mysql_record_schema).alias("data")) \
                 .filter("data.payload.op IN ('c', 'u', 'r')") \
                 .select(
                     col("data.payload.after.id").alias("id"),                 # 直接映射为 'id'
                     col("data.payload.after.username").alias("username"),     # 直接映射为 'username'
                     col("data.payload.after.email").alias("email"),
                     col("data.payload.after.password_hash").alias("password_hash"), # 新增映射
                     col("data.payload.after.avatar_url").alias("avatar_url"),     # 新增映射
                     lit(current_timestamp()).alias("last_sync_time") # 记录同步时间
                 ) \
                 .filter(col("id").isNotNull()) # 添加过滤器，确保 id 不为空

    # 打印 DataFrame 内容以调试
    print(f"Batch {epoch_id} users_df schema:")
    users_df.printSchema()
    print(f"Batch {epoch_id} users_df content (showing max 10 rows):")
    users_df.show(10, truncate=False)
    
    if users_df.count() > 0:
        # 将数据写入 Recommendation DB 的 user 表
        users_df.write \
            .format("jdbc") \
            .option("url", REC_DB_JDBC_URL) \
            .option("dbtable", "rec_user_profiles") \
            .option("user", REC_DB_USER) \
            .option("password", REC_DB_PASSWORD) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode("append") \
            .save()
        print(f"Processed {users_df.count()} user records.")
    else:
        print(f"Batch {epoch_id} contained no valid user records after filtering.")

def process_book_data(df, epoch_id):
    """处理图书数据，加载到 Recommendation DB 的 book 表"""
    print(f"Processing book data in batch {epoch_id}...")

    # 第一层解析：解析 Kafka 消息的 envelope
    parsed_df = df.select(from_json(col("value").cast("string"), mongodb_kafka_envelope_schema).alias("data"))

    # 过滤操作类型并提取 'after' 字段（它现在是字符串）
    # 然后，对 'after' 字符串进行第二次 JSON 解析
    books_df = parsed_df.filter("data.payload.op IN ('c', 'u', 'r')") \
                        .select(from_json(col("data.payload.after"), actual_mongodb_data_schema).alias("book_data")) \
                        .select(
                            col("book_data.bookId").alias("book_id"), 
                            col("book_data.title").alias("title"),
                            col("book_data.category").alias("category"),
                            lit(current_timestamp()).alias("last_sync_time")
                        ) \
                        .filter(col("book_id").isNotNull()) # <--- 保留过滤器

    # 打印 DataFrame 内容以调试
    print(f"Batch {epoch_id} books_df schema:")
    books_df.printSchema()
    print(f"Batch {epoch_id} books_df content (showing max 10 rows):")
    books_df.show(10, truncate=False)

    if books_df.count() > 0:
        books_df.write \
            .format("jdbc") \
            .option("url", REC_DB_JDBC_URL) \
            .option("dbtable", "rec_books") \
            .option("user", REC_DB_USER) \
            .option("password", REC_DB_PASSWORD) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode("append") \
            .save()
        print(f"Processed {books_df.count()} book records.")
    else:
        print(f"Batch {epoch_id} contained no valid book records after filtering.")

# --- Kafka 数据源配置 ---
def create_kafka_stream(topic_name, schema):
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER_URL) \
        .option("subscribe", topic_name) \
        .option("startingOffsets", "earliest") \
        .load() \
        .selectExpr("CAST(value AS STRING)")

# 创建数据流
# 修改这部分的 topic 名称
user_stream = create_kafka_stream("auth_db_cdc.auth_db.users", mysql_record_schema) # <--- 解除注释并使用新的mysql_record_schema
book_stream = create_kafka_stream("book_db_cdc.book_manage_db.books", mongodb_kafka_envelope_schema) 

# --- 启动流式查询 ---
# 用户数据流
user_query = user_stream.writeStream \
    .foreachBatch(process_user_data) \
    .outputMode("update") \
    .trigger(processingTime="10 seconds") \
    .start()

# 图书数据流
book_query = book_stream.writeStream \
    .foreachBatch(process_book_data) \
    .outputMode("update") \
    .trigger(processingTime="10 seconds") \
    .start()


print("Spark streaming ETL started. Waiting for data...")
spark.streams.awaitAnyTermination()