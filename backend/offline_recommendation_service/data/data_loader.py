import pandas as pd
from sqlalchemy import create_engine
from config import Config

class DataLoader:
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    def load_user_profiles(self):
        """从 rec_user_profiles 表加载用户数据"""
        print("Loading user profiles from rec_user_profiles...")
        df = pd.read_sql("SELECT id, username, email FROM rec_user_profiles", self.engine)
        print(f"Loaded {len(df)} user profiles.")
        return df

    def load_book_data(self):
        """从 rec_books 表加载图书数据"""
        print("Loading book data from rec_books...")
        df = pd.read_sql("SELECT book_id, title, category FROM rec_books", self.engine)
        print(f"Loaded {len(df)} book data.")
        return df

    def load_user_book_interactions(self):
        """
        加载用户与图书的交互数据。
        这里假设你有一个名为 'user_book_interactions' 的表，
        包含 user_id, book_id, interaction_type 和 rating (如果适用)。
        """
        print("Loading user-book interactions...")
        # 修改这里的 SQL 查询，以匹配你实际的交互表结构
        # 建议加载 user_id, book_id, 以及一个代表“强度”的列（例如 rating 或一个表示交互的常量）
        # 如果是隐式反馈（如点赞、浏览），可以简单地查询 user_id 和 book_id
        df = pd.read_sql("SELECT user_id, book_id, 1 as interaction_value FROM user_book_interactions", self.engine)
        # 或者如果你有评分数据，可以使用 rating:
        # df = pd.read_sql("SELECT user_id, book_id, rating FROM user_book_interactions WHERE rating IS NOT NULL", self.engine)

        if not df.empty:
            print(f"Loaded {len(df)} user-book interactions.")
        else:
            print("No user-book interactions loaded. Please ensure 'user_book_interactions' table exists and has data.")
        return df

if __name__ == '__main__':
    # 简单测试
    loader = DataLoader()
    users_df = loader.load_user_profiles()
    books_df = loader.load_book_data()
    interactions_df = loader.load_user_book_interactions()

    print("\nUsers Head:")
    print(users_df.head())
    print("\nBooks Head:")
    print(books_df.head())
    print("\nInteractions Head:")
    print(interactions_df.head())
