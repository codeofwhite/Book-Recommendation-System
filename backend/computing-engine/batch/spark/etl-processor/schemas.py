# schemas.py
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, TimestampType, DoubleType, BooleanType

# --- 定义 Kafka 消息的 Schema ---
# Debezium 产生的 MySQL binlog 事件通常包含 'before' 和 'after' 字段
mysql_record_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StructType([ # before 和 after 的结构应该相同
            StructField("id", IntegerType(), True),
            StructField("username", StringType(), True),
            StructField("email", StringType(), True),
            StructField("password_hash", StringType(), True),
            StructField("avatar_url", StringType(), True),
            # 将 TimestampType() 改为 LongType()
            StructField("registration_date", LongType(), True), # 预期 Debezium 发送毫秒时间戳
            StructField("last_login_date", LongType(), True),   # 预期 Debezium 发送毫秒时间戳
            StructField("age", IntegerType(), True),
            StructField("gender", StringType(), True),
            StructField("location", StringType(), True),
            StructField("occupation", StringType(), True),
            StructField("interest_tags", StringType(), True),
            StructField("preferred_book_types", StringType(), True),
            StructField("preferred_authors", StringType(), True),
            StructField("preferred_genres", StringType(), True),
            StructField("preferred_reading_duration", StringType(), True),
            StructField("is_profile_complete", BooleanType(), True)
        ]), True),
        StructField("after", StructType([
            StructField("id", IntegerType(), True),         
            StructField("username", StringType(), True),     
            StructField("email", StringType(), True),       
            StructField("password_hash", StringType(), True),
            StructField("avatar_url", StringType(), True),   
            # 将 TimestampType() 改为 LongType()
            StructField("registration_date", LongType(), True), 
            StructField("last_login_date", LongType(), True),   
            StructField("age", IntegerType(), True),
            StructField("gender", StringType(), True),
            StructField("location", StringType(), True),
            StructField("occupation", StringType(), True),
            StructField("interest_tags", StringType(), True),
            StructField("preferred_book_types", StringType(), True),
            StructField("preferred_authors", StringType(), True),
            StructField("preferred_genres", StringType(), True),
            StructField("preferred_reading_duration", StringType(), True),
            StructField("is_profile_complete", BooleanType(), True)
        ]), True), # New value (for inserts/updates)
        StructField("source", StringType(), True),
        StructField("op", StringType(), True), # Operation type: 'c' (create), 'u' (update), 'd' (delete), 'r' (read - snapshot)
        StructField("ts_ms", LongType(), True) # Timestamp
    ]), True)
])

# MongoDB Debezium 消息的 Schema - payload.after 是一个JSON字符串
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

# BookFavorite 表的 Schema
book_favorite_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StructType([
            StructField("favorite_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("book_id", StringType(), True),
            StructField("add_time", LongType(), True) # DATETIME 通常转为 LongType (毫秒时间戳)
        ]), True),
        StructField("after", StructType([
            StructField("favorite_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("book_id", StringType(), True),
            StructField("add_time", LongType(), True)
        ]), True),
        StructField("source", StringType(), True),
        StructField("op", StringType(), True),
        StructField("ts_ms", LongType(), True)
    ]), True)
])

# ReviewFavorite 表的 Schema
review_favorite_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StructType([
            StructField("favorite_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("review_id", StringType(), True),
            StructField("add_time", LongType(), True)
        ]), True),
        StructField("after", StructType([
            StructField("favorite_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("review_id", StringType(), True),
            StructField("add_time", LongType(), True)
        ]), True),
        StructField("source", StringType(), True),
        StructField("op", StringType(), True),
        StructField("ts_ms", LongType(), True)
    ]), True)
])

# BookLike 表的 Schema
book_like_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StructType([
            StructField("like_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("book_id", StringType(), True),
            StructField("like_time", LongType(), True)
        ]), True),
        StructField("after", StructType([
            StructField("like_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("book_id", StringType(), True),
            StructField("like_time", LongType(), True)
        ]), True),
        StructField("source", StringType(), True),
        StructField("op", StringType(), True),
        StructField("ts_ms", LongType(), True)
    ]), True)
])

# ReviewLike 表的 Schema
review_like_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StructType([
            StructField("like_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("review_id", StringType(), True),
            StructField("like_time", LongType(), True)
        ]), True),
        StructField("after", StructType([
            StructField("like_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("review_id", StringType(), True),
            StructField("like_time", LongType(), True)
        ]), True),
        StructField("source", StringType(), True),
        StructField("op", StringType(), True),
        StructField("ts_ms", LongType(), True)
    ]), True)
])

# Review 表的 Schema
review_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StructType([
            StructField("review_id", StringType(), True),
            StructField("book_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("content", StringType(), True),
            StructField("rating", DoubleType(), True),
            StructField("like_count", IntegerType(), True),
            StructField("post_time", LongType(), True),
            StructField("status", IntegerType(), True) # SmallInteger 映射为 IntegerType
        ]), True),
        StructField("after", StructType([
            StructField("review_id", StringType(), True),
            StructField("book_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("content", StringType(), True),
            StructField("rating", DoubleType(), True),
            StructField("like_count", IntegerType(), True),
            StructField("post_time", LongType(), True),
            StructField("status", IntegerType(), True)
        ]), True),
        StructField("source", StringType(), True),
        StructField("op", StringType(), True),
        StructField("ts_ms", LongType(), True)
    ]), True)
])

# Comment 表的 Schema
comment_schema = StructType([
    StructField("schema", StringType(), True),
    StructField("payload", StructType([
        StructField("before", StructType([
            StructField("comment_id", StringType(), True),
            StructField("review_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("content", StringType(), True),
            StructField("like_count", IntegerType(), True),
            StructField("comment_time", LongType(), True)
        ]), True),
        StructField("after", StructType([
            StructField("comment_id", StringType(), True),
            StructField("review_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("content", StringType(), True),
            StructField("like_count", IntegerType(), True),
            StructField("comment_time", LongType(), True)
        ]), True),
        StructField("source", StringType(), True),
        StructField("op", StringType(), True),
        StructField("ts_ms", LongType(), True)
    ]), True)
])

