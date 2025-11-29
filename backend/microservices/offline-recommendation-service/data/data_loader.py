import pandas as pd
from sqlalchemy import create_engine
from config import Config
import re  # 导入正则表达式模块


class DataLoader:
    def __init__(self):
        # 初始化 MySQL 引擎
        self.mysql_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        # 初始化 ClickHouse 引擎
        self.clickhouse_engine = create_engine(Config.CLICKHOUSE_DATABASE_URI)

    def load_user_profiles(self):
        """从 rec_user_profiles 表加载用户数据 (使用 MySQL)"""
        print("Loading user profiles from rec_user_profiles (MySQL)...")
        # 确保这里查询的是你的用户表实际名称，例如 rec_user_profiles 或直接是 user 表
        df = pd.read_sql(
            "SELECT id, username, email, age, gender, location, interest_tags, preferred_book_types, preferred_authors, preferred_genres FROM rec_user_profiles",
            self.mysql_engine,
        )
        # 注意：如果 interest_tags, preferred_book_types, preferred_authors, preferred_genres 是字符串，可能需要进一步处理（如分割成列表）
        print(f"Loaded {len(df)} user profiles.")
        return df

    def load_book_data(self):
        """从 rec_books 表加载图书数据 (使用 MySQL)"""
        print("Loading book data from rec_books (MySQL)...")
        df = pd.read_sql(
            """
            SELECT 
                book_id, title, category, author, rating, description, language, isbn, genres, 
                characters, book_format, edition, pages, publisher, publish_date, 
                first_publish_date, awards, num_ratings, ratings_by_stars, liked_percent, 
                setting, cover_img, bbe_score, bbe_votes, price
            FROM rec_books
        """,
            self.mysql_engine,
        )
        print(f"Loaded {len(df)} book data.")
        return df

    def load_user_behavior_logs(self):
        """
        从 ClickHouse 的 default.user_behavior_logs 表加载用户行为日志数据。
        根据提供的字段示例，提取 user_id, book_id (作为 item_id), event_type, 和交互强度。
        """
        
        print(
            "Loading user behavior logs from ClickHouse default.user_behavior_logs..."
        )

        query = """
                SELECT
                    -- 【修正】使用 CamelCase 字段名
                    userId,
                    -- 【修正】使用 CamelCase 字段名
                    extract(
                        pageUrl,
                        '/books/([^/]+)' 
                    ) AS item_id, 
                    
                    -- 【修正】使用 CamelCase 字段名 (您在表中可能使用的是 timestamp)
                    timestamp, 
                    -- 【修正】使用 CamelCase 字段名
                    eventType,              

                    -- 计算交互值 (字段名也必须修正)
                    CASE
                        WHEN eventType = 'page_view_duration' AND JSONHas(payload, 'dwellTime') THEN
                            toInt32(JSONExtractString(payload, 'dwellTime')) + 1 
                        WHEN eventType = 'button_click' THEN
                            CASE JSONExtractString(payload, 'buttonName')
                                WHEN 'LikeButton' THEN 10 
                                WHEN 'CollectButton' THEN 15 
                                WHEN 'SubmitReview' THEN 20 
                                ELSE 5 
                            END
                        WHEN eventType = 'page_view' AND JSONExtractString(payload, 'pageName') = 'BookDetails' THEN
                            2
                        WHEN eventType = 'page_view' AND JSONExtractString(payload, 'pageName') = 'BookList' THEN
                            1
                        ELSE
                            0 
                    END AS interaction_value
                -- 确保您的表名是正确的 (user_behavior_logs 或 user_behavior_logs_raw)
                FROM default.user_behavior_logs 
                WHERE
                    (pageUrl LIKE '%%/books/%%' OR eventType = 'button_click')
                    AND userId IS NOT NULL
                    AND userId != 0 
                    AND extract(pageUrl, '/books/([^/]+)') != '' 
                ORDER BY userId, timestamp
        """

        df = pd.read_sql(query, self.clickhouse_engine)

        df = df.dropna(subset=["item_id"])
        df = df[df["item_id"] != ""]
        df["interaction_value"] = df["interaction_value"].astype(int)

        if not df.empty:
            print(f"Loaded {len(df)} user behavior logs.")
        else:
            print("No user behavior logs loaded from ClickHouse.")
        return df

    def load_book_favorites(self):
        """从 MySQL 的 BOOK_FAVORITE 表加载图书收藏数据"""
        print("Loading book favorite data from BOOK_FAVORITE (MySQL)...")
        # 收藏是强烈的正向反馈，可以给较高的交互值
        df = pd.read_sql(
            "SELECT user_id, book_id, add_time AS timestamp, 20 AS interaction_value FROM BOOK_FAVORITE",
            self.mysql_engine,
        )
        if not df.empty:
            print(f"Loaded {len(df)} book favorites.")
        else:
            print("No book favorite data loaded.")
        return df

    def load_book_likes(self):
        """从 MySQL 的 BOOK_LIKE 表加载图书点赞数据"""
        print("Loading book like data from BOOK_LIKE (MySQL)...")
        # 点赞也是强烈的正向反馈，可以给较高的交互值
        df = pd.read_sql(
            "SELECT user_id, book_id, like_time AS timestamp, 18 AS interaction_value FROM BOOK_LIKE",
            self.mysql_engine,
        )
        if not df.empty:
            print(f"Loaded {len(df)} book likes.")
        else:
            print("No book like data loaded.")
        return df

    def load_book_reviews(self):
        """从 MySQL 的 REVIEW 表加载书评数据 (作为评分和交互)"""
        print("Loading book review data from REVIEW (MySQL)...")
        # 评论包含评分，这是非常直接的显式反馈
        # 我们将 rating 映射到 interaction_value，并加上一个基础值，例如 rating * 5
        df = pd.read_sql(
            "SELECT user_id, book_id, post_time AS timestamp, rating * 5 AS interaction_value FROM REVIEW WHERE rating IS NOT NULL",
            self.mysql_engine,
        )
        if not df.empty:
            print(f"Loaded {len(df)} book reviews.")
        else:
            print("No book review data loaded.")
        return df


if __name__ == "__main__":
    # 简单测试所有数据加载
    loader = DataLoader()
    users_df = loader.load_user_profiles()
    books_df = loader.load_book_data()
    user_behavior_logs_df = loader.load_user_behavior_logs()
    book_favorites_df = loader.load_book_favorites()
    book_likes_df = loader.load_book_likes()
    book_reviews_df = loader.load_book_reviews()

    print("\nUsers Head:")
    print(users_df.head())
    print("\nBooks Head:")
    print(books_df.head())
    print("\nUser Behavior Logs Head (from ClickHouse):")
    print(user_behavior_logs_df.head())
    print("\nBook Favorites Head (from MySQL):")
    print(book_favorites_df.head())
    print("\nBook Likes Head (from MySQL):")
    print(book_likes_df.head())
    print("\nBook Reviews Head (from MySQL):")
    print(book_reviews_df.head())

    # 示例：合并所有交互数据
    all_interactions = pd.concat(
        [
            user_behavior_logs_df[
                ["user_id", "item_id", "timestamp", "interaction_value"]
            ],
            book_favorites_df[
                ["user_id", "book_id", "timestamp", "interaction_value"]
            ].rename(columns={"book_id": "item_id"}),
            book_likes_df[
                ["user_id", "book_id", "timestamp", "interaction_value"]
            ].rename(columns={"book_id": "item_id"}),
            book_reviews_df[
                ["user_id", "book_id", "timestamp", "interaction_value"]
            ].rename(columns={"book_id": "item_id"}),
        ],
        ignore_index=True,
    )

    print("\nAll Interactions Head (Combined):")
    print(all_interactions.head())
    print(f"Total interactions loaded: {len(all_interactions)}")
