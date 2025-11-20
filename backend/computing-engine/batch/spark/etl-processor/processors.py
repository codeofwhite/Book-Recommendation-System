# processors.py
from pyspark.sql.functions import (
    from_json,
    col,
    lit,
    current_timestamp,
    when,
    year,
    coalesce,
)
from schemas import (
    mysql_record_schema,
    actual_mongodb_data_schema,
    mongodb_kafka_envelope_schema,
)
from config import REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
import pymysql.cursors  # Import for direct MySQL connection

# 导入新增的 Schema
from schemas import (
    book_favorite_schema,
    review_favorite_schema,
    book_like_schema,
    review_like_schema,
    review_schema,
    comment_schema,
)


def execute_jdbc_update(sql_query, db_host, db_name, db_user, db_password):
    """
    Executes a DML SQL query directly using pymysql.
    """
    conn = None
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
        conn.commit()
        print(f"SQL command executed successfully.")
    except Exception as e:
        print(f"Error executing SQL command: {e}")
        if conn:
            conn.rollback()  # Rollback on error
        raise  # Re-raise the exception to propagate it
    finally:
        if conn:
            conn.close()


def process_user_data(df, epoch_id, spark):
    """处理用户数据，加载到 Recommendation DB 的 user 表，支持 upsert"""
    print(f"Processing user data in batch {epoch_id}...")

    # 过滤操作类型并提取数据
    # 注意：这里先将 raw_registration_date 和 raw_last_login_date 提取为 LongType
    raw_users_df = (
        df.select(
            from_json(col("value").cast("string"), mysql_record_schema).alias("data")
        )
        .filter("data.payload.op IN ('c', 'u', 'r')")
        .select(
            col("data.payload.after.id").alias("id"),
            col("data.payload.after.username").alias("username"),
            col("data.payload.after.email").alias("email"),
            col("data.payload.after.password_hash").alias("password_hash"),
            col("data.payload.after.avatar_url").alias("avatar_url"),
            # 提取为 LongType
            col("data.payload.after.registration_date").alias("raw_registration_date"),
            col("data.payload.after.last_login_date").alias("raw_last_login_date"),
            col("data.payload.after.age").alias("age"),
            col("data.payload.after.gender").alias("gender"),
            col("data.payload.after.location").alias("location"),
            col("data.payload.after.occupation").alias("occupation"),
            col("data.payload.after.interest_tags").alias("interest_tags"),
            col("data.payload.after.preferred_book_types").alias(
                "preferred_book_types"
            ),
            col("data.payload.after.preferred_authors").alias("preferred_authors"),
            col("data.payload.after.preferred_genres").alias("preferred_genres"),
            col("data.payload.after.preferred_reading_duration").alias(
                "preferred_reading_duration"
            ),
            col("data.payload.after.is_profile_complete").alias(
                "is_profile_complete_raw"
            ),  # 临时别名
        )
        .filter(col("id").isNotNull())
    )

    # --- 对日期字段和布尔字段进行转换和清理 ---
    users_df = (
        raw_users_df.withColumn(
            "registration_date",
            # 将毫秒时间戳转换为 TimestampType，并处理可能的无效值
            when(
                col("raw_registration_date").isNotNull(),
                (col("raw_registration_date") / 1000).cast("timestamp"),
            ).otherwise(lit(None).cast("timestamp")),
        )
        .withColumn(
            "last_login_date",
            # 将毫秒时间戳转换为 TimestampType，并处理可能的无效值
            when(
                col("raw_last_login_date").isNotNull(),
                (col("raw_last_login_date") / 1000).cast("timestamp"),
            ).otherwise(lit(None).cast("timestamp")),
        )
        .withColumn(
            "is_profile_complete",
            # 确保 is_profile_complete 不为 NULL，如果为 NULL 则设置为 False (对应 TINYINT 0)
            coalesce(col("is_profile_complete_raw"), lit(False)),
        )
        .withColumn("last_sync_time", lit(current_timestamp()))  # 记录同步时间
        .drop("raw_registration_date", "raw_last_login_date", "is_profile_complete_raw")
    )  # 删除原始的 long 类型和临时别名列

    # 打印 DataFrame 内容以调试
    print(f"Batch {epoch_id} users_df schema:")
    users_df.printSchema()
    print(f"Batch {epoch_id} users_df content (showing max 10 rows):")
    users_df.show(10, truncate=False)

    if users_df.count() > 0:
        temp_table_name = "rec_user_profiles_temp"
        target_table_name = "rec_user_profiles"

        try:
            # 1. 将当前批次数据写入一个临时表 (覆盖模式)
            users_df.write.format("jdbc").option(
                "url", f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"
            ).option("dbtable", temp_table_name).option("user", REC_DB_USER).option(
                "password", REC_DB_PASSWORD
            ).option(
                "driver", "com.mysql.cj.jdbc.Driver"
            ).mode(
                "overwrite"
            ).save()
            print(
                f"Batch {epoch_id}: Wrote {users_df.count()} records to temporary table {temp_table_name}."
            )

            # 2. 执行 INSERT ... ON DUPLICATE KEY UPDATE 语句进行 upsert
            # 确保 SQL 语句中包含所有新字段
            upsert_sql = f"""
                INSERT INTO {target_table_name} (
                    id, username, email, password_hash, avatar_url,
                    registration_date, last_login_date, age, gender, location,
                    occupation, interest_tags, preferred_book_types, preferred_authors,
                    preferred_genres, preferred_reading_duration, is_profile_complete,
                    last_sync_time
                )
                SELECT
                    id, username, email, password_hash, avatar_url,
                    registration_date, last_login_date, age, gender, location,
                    occupation, interest_tags, preferred_book_types, preferred_authors,
                    preferred_genres, preferred_reading_duration, is_profile_complete,
                    last_sync_time
                FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    username = VALUES(username),
                    email = VALUES(email),
                    password_hash = VALUES(password_hash),
                    avatar_url = VALUES(avatar_url),
                    registration_date = VALUES(registration_date),
                    last_login_date = VALUES(last_login_date),
                    age = VALUES(age),
                    gender = VALUES(gender),
                    location = VALUES(location),
                    occupation = VALUES(occupation),
                    interest_tags = VALUES(interest_tags),
                    preferred_book_types = VALUES(preferred_book_types),
                    preferred_authors = VALUES(preferred_authors),
                    preferred_genres = VALUES(preferred_genres),
                    preferred_reading_duration = VALUES(preferred_reading_duration),
                    is_profile_complete = VALUES(is_profile_complete),
                    last_sync_time = VALUES(last_sync_time);
            """
            # 使用直接 JDBC 连接执行 DML
            execute_jdbc_update(
                upsert_sql, REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
            )
            print(
                f"Batch {epoch_id}: Successfully upserted records into {target_table_name}."
            )

        except Exception as e:
            print(f"Error processing user data in batch {epoch_id}: {e}")
    else:
        print(f"Batch {epoch_id} contained no valid user records after filtering.")


# ... (process_book_data 函数保持不变)
def process_book_data(df, epoch_id, spark):
    """处理图书数据，加载到 Recommendation DB 的 book 表，支持 upsert"""
    print(f"Processing book data in batch {epoch_id}...")

    # 第一层解析：解析 Kafka 消息的 envelope
    parsed_df = df.select(
        from_json(col("value").cast("string"), mongodb_kafka_envelope_schema).alias(
            "data"
        )
    )

    # 过滤操作类型并提取 'after' 字段（它现在是字符串）
    # 然后，对 'after' 字符串进行第二次 JSON 解析
    books_df = (
        parsed_df.filter("data.payload.op IN ('c', 'u', 'r')")
        .select(
            from_json(col("data.payload.after"), actual_mongodb_data_schema).alias(
                "book_data"
            )
        )
        .select(
            col("book_data.bookId").alias("book_id"),
            col("book_data.title").alias("title"),
            col("book_data.category").alias("category"),
            # 新增字段映射
            col("book_data.series").alias("series"),
            col("book_data.author").alias("author"),
            col("book_data.rating").alias("rating"),
            col("book_data.description").alias("description"),
            col("book_data.language").alias("language"),
            col("book_data.isbn").alias("isbn"),
            col("book_data.genres").alias("genres"),
            col("book_data.characters").alias("characters"),
            col("book_data.bookFormat").alias("book_format"),  # 注意映射到下划线命名
            col("book_data.edition").alias("edition"),
            col("book_data.pages").alias("pages"),
            col("book_data.publisher").alias("publisher"),
            col("book_data.publishDate").alias("publish_date"),  # 注意映射到下划线命名
            col("book_data.firstPublishDate").alias(
                "first_publish_date"
            ),  # 注意映射到下划线命名
            col("book_data.awards").alias("awards"),
            col("book_data.numRatings").alias("num_ratings"),  # 注意映射到下划线命名
            col("book_data.ratingsByStars").alias(
                "ratings_by_stars"
            ),  # 注意映射到下划线命名
            col("book_data.likedPercent").alias(
                "liked_percent"
            ),  # 注意映射到下划线命名
            col("book_data.setting").alias("setting"),
            col("book_data.coverImg").alias("cover_img"),  # 注意映射到下划线命名
            col("book_data.bbeScore").alias("bbe_score"),  # 注意映射到下划线命名
            col("book_data.bbeVotes").alias("bbe_votes"),  # 注意映射到下划线命名
            col("book_data.price").alias("price"),
            lit(current_timestamp()).alias("last_sync_time"),
        )
        .filter(col("book_id").isNotNull())
    )

    # 打印 DataFrame 内容以调试
    print(f"Batch {epoch_id} books_df schema:")
    books_df.printSchema()
    print(f"Batch {epoch_id} books_df content (showing max 10 rows):")
    books_df.show(10, truncate=False)

    if books_df.count() > 0:
        temp_table_name = "rec_books_temp"
        target_table_name = "rec_books"

        try:
            # 1. 将当前批次数据写入一个临时表 (覆盖模式)
            books_df.write.format("jdbc").option(
                "url", f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"
            ).option("dbtable", temp_table_name).option("user", REC_DB_USER).option(
                "password", REC_DB_PASSWORD
            ).option(
                "driver", "com.mysql.cj.jdbc.Driver"
            ).mode(
                "overwrite"
            ).save()
            print(
                f"Batch {epoch_id}: Wrote {books_df.count()} records to temporary table {temp_table_name}."
            )

            # 2. 执行 INSERT ... ON DUPLICATE KEY UPDATE 语句进行 upsert
            # 确保 SQL 语句中包含所有新字段
            upsert_sql = f"""
                INSERT INTO {target_table_name} (
                    book_id, title, category, series, author, rating, description,
                    language, isbn, genres, characters, book_format, edition, pages,
                    publisher, publish_date, first_publish_date, awards, num_ratings,
                    ratings_by_stars, liked_percent, setting, cover_img, bbe_score,
                    bbe_votes, price, last_sync_time
                )
                SELECT
                    book_id, title, category, series, author, rating, description,
                    language, isbn, genres, characters, book_format, edition, pages,
                    publisher, publish_date, first_publish_date, awards, num_ratings,
                    ratings_by_stars, liked_percent, setting, cover_img, bbe_score,
                    bbe_votes, price, last_sync_time
                FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    category = VALUES(category),
                    series = VALUES(series),
                    author = VALUES(author),
                    rating = VALUES(rating),
                    description = VALUES(description),
                    language = VALUES(language),
                    isbn = VALUES(isbn),
                    genres = VALUES(genres),
                    characters = VALUES(characters),
                    book_format = VALUES(book_format),
                    edition = VALUES(edition),
                    pages = VALUES(pages),
                    publisher = VALUES(publisher),
                    publish_date = VALUES(publish_date),
                    first_publish_date = VALUES(first_publish_date),
                    awards = VALUES(awards),
                    num_ratings = VALUES(num_ratings),
                    ratings_by_stars = VALUES(ratings_by_stars),
                    liked_percent = VALUES(liked_percent),
                    setting = VALUES(setting),
                    cover_img = VALUES(cover_img),
                    bbe_score = VALUES(bbe_score),
                    bbe_votes = VALUES(bbe_votes),
                    price = VALUES(price),
                    last_sync_time = VALUES(last_sync_time);
            """
            # 使用直接 JDBC 连接执行 DML
            execute_jdbc_update(
                upsert_sql, REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
            )
            print(
                f"Batch {epoch_id}: Successfully upserted records into {target_table_name}."
            )

        except Exception as e:
            print(f"Error processing book data in batch {epoch_id}: {e}")
    else:
        print(f"Batch {epoch_id} contained no valid book records after filtering.")


# --- 新增：处理 BookFavorite 数据 ---
def process_book_favorite_data(df, epoch_id, spark):
    print(f"Processing book favorite data in batch {epoch_id}...")
    favorite_df = (
        df.select(
            from_json(col("value").cast("string"), book_favorite_schema).alias("data")
        )
        .filter("data.payload.op IN ('c', 'u', 'r')")
        .select(
            col("data.payload.after.favorite_id").alias("favorite_id"),
            col("data.payload.after.user_id").alias("user_id"),
            col("data.payload.after.book_id").alias("book_id"),
            (col("data.payload.after.add_time") / 1000)
            .cast("timestamp")
            .alias("add_time"),
            lit(current_timestamp()).alias("last_sync_time"),
        )
        .filter(col("favorite_id").isNotNull())
    )

    print(f"Batch {epoch_id} book_favorite_df schema:")
    favorite_df.printSchema()
    print(f"Batch {epoch_id} book_favorite_df content (showing max 10 rows):")
    favorite_df.show(10, truncate=False)

    if favorite_df.count() > 0:
        temp_table_name = "rec_book_favorite_temp"
        target_table_name = "BOOK_FAVORITE"  # 与模型中的 __tablename__ 匹配

        try:
            favorite_df.write.format("jdbc").option(
                "url", f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"
            ).option("dbtable", temp_table_name).option("user", REC_DB_USER).option(
                "password", REC_DB_PASSWORD
            ).option(
                "driver", "com.mysql.cj.jdbc.Driver"
            ).mode(
                "overwrite"
            ).save()
            print(
                f"Batch {epoch_id}: Wrote {favorite_df.count()} records to temporary table {temp_table_name}."
            )

            upsert_sql = f"""
                INSERT INTO {target_table_name} (favorite_id, user_id, book_id, add_time, last_sync_time)
                SELECT favorite_id, user_id, book_id, add_time, last_sync_time FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    user_id = VALUES(user_id),
                    book_id = VALUES(book_id),
                    add_time = VALUES(add_time),
                    last_sync_time = VALUES(last_sync_time);
            """
            execute_jdbc_update(
                upsert_sql, REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
            )
            print(
                f"Batch {epoch_id}: Successfully upserted records into {target_table_name}."
            )
        except Exception as e:
            print(f"Error processing book favorite data in batch {epoch_id}: {e}")
    else:
        print(
            f"Batch {epoch_id} contained no valid book favorite records after filtering."
        )


# --- 新增：处理 ReviewFavorite 数据 ---
def process_review_favorite_data(df, epoch_id, spark):
    print(f"Processing review favorite data in batch {epoch_id}...")
    favorite_df = (
        df.select(
            from_json(col("value").cast("string"), review_favorite_schema).alias("data")
        )
        .filter("data.payload.op IN ('c', 'u', 'r')")
        .select(
            col("data.payload.after.favorite_id").alias("favorite_id"),
            col("data.payload.after.user_id").alias("user_id"),
            col("data.payload.after.review_id").alias("review_id"),
            (col("data.payload.after.add_time") / 1000)
            .cast("timestamp")
            .alias("add_time"),
            lit(current_timestamp()).alias("last_sync_time"),
        )
        .filter(col("favorite_id").isNotNull())
    )

    print(f"Batch {epoch_id} review_favorite_df schema:")
    favorite_df.printSchema()
    print(f"Batch {epoch_id} review_favorite_df content (showing max 10 rows):")
    favorite_df.show(10, truncate=False)

    if favorite_df.count() > 0:
        temp_table_name = "rec_review_favorite_temp"
        target_table_name = "REVIEW_FAVORITE"  # 与模型中的 __tablename__ 匹配

        try:
            favorite_df.write.format("jdbc").option(
                "url", f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"
            ).option("dbtable", temp_table_name).option("user", REC_DB_USER).option(
                "password", REC_DB_PASSWORD
            ).option(
                "driver", "com.mysql.cj.jdbc.Driver"
            ).mode(
                "overwrite"
            ).save()
            print(
                f"Batch {epoch_id}: Wrote {favorite_df.count()} records to temporary table {temp_table_name}."
            )

            upsert_sql = f"""
                INSERT INTO {target_table_name} (favorite_id, user_id, review_id, add_time, last_sync_time)
                SELECT favorite_id, user_id, review_id, add_time, last_sync_time FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    user_id = VALUES(user_id),
                    review_id = VALUES(review_id),
                    add_time = VALUES(add_time),
                    last_sync_time = VALUES(last_sync_time);
            """
            execute_jdbc_update(
                upsert_sql, REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
            )
            print(
                f"Batch {epoch_id}: Successfully upserted records into {target_table_name}."
            )
        except Exception as e:
            print(f"Error processing review favorite data in batch {epoch_id}: {e}")
    else:
        print(
            f"Batch {epoch_id} contained no valid review favorite records after filtering."
        )


# --- 处理 BookLike 数据 ---
def process_book_like_data(df, epoch_id, spark):
    print(f"Processing book like data in batch {epoch_id}...")
    like_df = (
        df.select(
            from_json(col("value").cast("string"), book_like_schema).alias("data")
        )
        .filter("data.payload.op IN ('c', 'u', 'r')")
        .select(
            col("data.payload.after.like_id").alias("like_id"),
            col("data.payload.after.user_id").alias("user_id"),
            col("data.payload.after.book_id").alias("book_id"),
            (col("data.payload.after.like_time") / 1000)
            .cast("timestamp")
            .alias("like_time"),
            lit(current_timestamp()).alias("last_sync_time"),
        )
        .filter(col("like_id").isNotNull())
    )

    print(f"Batch {epoch_id} book_like_df schema:")
    like_df.printSchema()
    print(f"Batch {epoch_id} book_like_df content (showing max 10 rows):")
    like_df.show(10, truncate=False)

    if like_df.count() > 0:
        temp_table_name = "rec_book_like_temp"
        target_table_name = "BOOK_LIKE"  # 与模型中的 __tablename__ 匹配

        try:
            like_df.write.format("jdbc").option(
                "url", f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"
            ).option("dbtable", temp_table_name).option("user", REC_DB_USER).option(
                "password", REC_DB_PASSWORD
            ).option(
                "driver", "com.mysql.cj.jdbc.Driver"
            ).mode(
                "overwrite"
            ).save()
            print(
                f"Batch {epoch_id}: Wrote {like_df.count()} records to temporary table {temp_table_name}."
            )

            upsert_sql = f"""
                INSERT INTO {target_table_name} (like_id, user_id, book_id, like_time, last_sync_time)
                SELECT like_id, user_id, book_id, like_time, last_sync_time FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    user_id = VALUES(user_id),
                    book_id = VALUES(book_id),
                    like_time = VALUES(like_time),
                    last_sync_time = VALUES(last_sync_time);
            """
            execute_jdbc_update(
                upsert_sql, REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
            )
            print(
                f"Batch {epoch_id}: Successfully upserted records into {target_table_name}."
            )
        except Exception as e:
            print(f"Error processing book like data in batch {epoch_id}: {e}")
    else:
        print(f"Batch {epoch_id} contained no valid book like records after filtering.")


# --- 处理 ReviewLike 数据 ---
def process_review_like_data(df, epoch_id, spark):
    print(f"Processing review like data in batch {epoch_id}...")
    like_df = (
        df.select(
            from_json(col("value").cast("string"), review_like_schema).alias("data")
        )
        .filter("data.payload.op IN ('c', 'u', 'r')")
        .select(
            col("data.payload.after.like_id").alias("like_id"),
            col("data.payload.after.user_id").alias("user_id"),
            col("data.payload.after.review_id").alias("review_id"),
            (col("data.payload.after.like_time") / 1000)
            .cast("timestamp")
            .alias("like_time"),
            lit(current_timestamp()).alias("last_sync_time"),
        )
        .filter(col("like_id").isNotNull())
    )

    print(f"Batch {epoch_id} review_like_df schema:")
    like_df.printSchema()
    print(f"Batch {epoch_id} review_like_df content (showing max 10 rows):")
    like_df.show(10, truncate=False)

    if like_df.count() > 0:
        temp_table_name = "rec_review_like_temp"
        target_table_name = "REVIEW_LIKE"  # 与模型中的 __tablename__ 匹配

        try:
            like_df.write.format("jdbc").option(
                "url", f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"
            ).option("dbtable", temp_table_name).option("user", REC_DB_USER).option(
                "password", REC_DB_PASSWORD
            ).option(
                "driver", "com.mysql.cj.jdbc.Driver"
            ).mode(
                "overwrite"
            ).save()
            print(
                f"Batch {epoch_id}: Wrote {like_df.count()} records to temporary table {temp_table_name}."
            )

            upsert_sql = f"""
                INSERT INTO {target_table_name} (like_id, user_id, review_id, like_time, last_sync_time)
                SELECT like_id, user_id, review_id, like_time, last_sync_time FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    user_id = VALUES(user_id),
                    review_id = VALUES(review_id),
                    like_time = VALUES(like_time),
                    last_sync_time = VALUES(last_sync_time);
            """
            execute_jdbc_update(
                upsert_sql, REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
            )
            print(
                f"Batch {epoch_id}: Successfully upserted records into {target_table_name}."
            )
        except Exception as e:
            print(f"Error processing review like data in batch {epoch_id}: {e}")
    else:
        print(
            f"Batch {epoch_id} contained no valid review like records after filtering."
        )


# --- 处理 Review 数据 ---
def process_review_data(df, epoch_id, spark):
    print(f"Processing review data in batch {epoch_id}...")
    review_df = (
        df.select(from_json(col("value").cast("string"), review_schema).alias("data"))
        .filter("data.payload.op IN ('c', 'u', 'r')")
        .select(
            col("data.payload.after.review_id").alias("review_id"),
            col("data.payload.after.book_id").alias("book_id"),
            col("data.payload.after.user_id").alias("user_id"),
            col("data.payload.after.content").alias("content"),
            col("data.payload.after.rating").alias("rating"),
            col("data.payload.after.like_count").alias("like_count"),
            (col("data.payload.after.post_time") / 1000)
            .cast("timestamp")
            .alias("post_time"),
            col("data.payload.after.status").alias("status"),
            lit(current_timestamp()).alias("last_sync_time"),
        )
        .filter(col("review_id").isNotNull())
    )

    print(f"Batch {epoch_id} review_df schema:")
    review_df.printSchema()
    print(f"Batch {epoch_id} review_df content (showing max 10 rows):")
    review_df.show(10, truncate=False)

    if review_df.count() > 0:
        temp_table_name = "rec_review_temp"
        target_table_name = "REVIEW"  # 与模型中的 __tablename__ 匹配

        try:
            review_df.write.format("jdbc").option(
                "url", f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"
            ).option("dbtable", temp_table_name).option("user", REC_DB_USER).option(
                "password", REC_DB_PASSWORD
            ).option(
                "driver", "com.mysql.cj.jdbc.Driver"
            ).mode(
                "overwrite"
            ).save()
            print(
                f"Batch {epoch_id}: Wrote {review_df.count()} records to temporary table {temp_table_name}."
            )

            upsert_sql = f"""
                INSERT INTO {target_table_name} (
                    review_id, book_id, user_id, content, rating, like_count, post_time, status, last_sync_time
                )
                SELECT
                    review_id, book_id, user_id, content, rating, like_count, post_time, status, last_sync_time
                FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    book_id = VALUES(book_id),
                    user_id = VALUES(user_id),
                    content = VALUES(content),
                    rating = VALUES(rating),
                    like_count = VALUES(like_count),
                    post_time = VALUES(post_time),
                    status = VALUES(status),
                    last_sync_time = VALUES(last_sync_time);
            """
            execute_jdbc_update(
                upsert_sql, REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
            )
            print(
                f"Batch {epoch_id}: Successfully upserted records into {target_table_name}."
            )
        except Exception as e:
            print(f"Error processing review data in batch {epoch_id}: {e}")
    else:
        print(f"Batch {epoch_id} contained no valid review records after filtering.")


# --- 处理 Comment 数据 ---
def process_comment_data(df, epoch_id, spark):
    print(f"Processing comment data in batch {epoch_id}...")
    comment_df = (
        df.select(from_json(col("value").cast("string"), comment_schema).alias("data"))
        .filter("data.payload.op IN ('c', 'u', 'r')")
        .select(
            col("data.payload.after.comment_id").alias("comment_id"),
            col("data.payload.after.review_id").alias("review_id"),
            col("data.payload.after.user_id").alias("user_id"),
            col("data.payload.after.content").alias("content"),
            col("data.payload.after.like_count").alias("like_count"),
            (col("data.payload.after.comment_time") / 1000)
            .cast("timestamp")
            .alias("comment_time"),
            lit(current_timestamp()).alias("last_sync_time"),
        )
        .filter(col("comment_id").isNotNull())
    )

    print(f"Batch {epoch_id} comment_df schema:")
    comment_df.printSchema()
    print(f"Batch {epoch_id} comment_df content (showing max 10 rows):")
    comment_df.show(10, truncate=False)

    if comment_df.count() > 0:
        temp_table_name = "rec_comment_temp"
        target_table_name = "COMMENT"  # 与模型中的 __tablename__ 匹配

        try:
            comment_df.write.format("jdbc").option(
                "url", f"jdbc:mysql://{REC_DB_HOST}:3306/{REC_DB_NAME}"
            ).option("dbtable", temp_table_name).option("user", REC_DB_USER).option(
                "password", REC_DB_PASSWORD
            ).option(
                "driver", "com.mysql.cj.jdbc.Driver"
            ).mode(
                "overwrite"
            ).save()
            print(
                f"Batch {epoch_id}: Wrote {comment_df.count()} records to temporary table {temp_table_name}."
            )

            upsert_sql = f"""
                INSERT INTO {target_table_name} (
                    comment_id, review_id, user_id, content, like_count, comment_time, last_sync_time
                )
                SELECT
                    comment_id, review_id, user_id, content, like_count, comment_time, last_sync_time
                FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    review_id = VALUES(review_id),
                    user_id = VALUES(user_id),
                    content = VALUES(content),
                    like_count = VALUES(like_count),
                    comment_time = VALUES(comment_time),
                    last_sync_time = VALUES(last_sync_time);
            """
            execute_jdbc_update(
                upsert_sql, REC_DB_HOST, REC_DB_NAME, REC_DB_USER, REC_DB_PASSWORD
            )
            print(
                f"Batch {epoch_id}: Successfully upserted records into {target_table_name}."
            )
        except Exception as e:
            print(f"Error processing comment data in batch {epoch_id}: {e}")
    else:
        print(f"Batch {epoch_id} contained no valid comment records after filtering.")
