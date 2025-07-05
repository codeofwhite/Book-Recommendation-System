import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from data.data_loader import DataLoader
from utils.redis_utils import RedisClient
from config import Config
import numpy as np

class RecommendationTrainer:
    def __init__(self):
        self.data_loader = DataLoader()
        self.redis_client = RedisClient()
        self.user_similarity_matrix = None
        self.user_item_matrix = None
        self.all_user_ids = []
        self.all_book_ids = []

    def _prepare_data(self):
        """加载数据并构建用户-物品矩阵"""
        users_df = self.data_loader.load_user_profiles()
        books_df = self.data_loader.load_book_data()
        interactions_df = self.data_loader.load_user_book_interactions() # 假设这里有真实数据

        if interactions_df.empty:
            print("No interaction data available. Cannot train collaborative filtering model.")
            return False

        # 为了简化示例，假设 interactions_df 已经包含 'user_id' 和 'book_id'
        # 并且我们只关心用户是否与图书有“交互”（即一个隐式反馈）
        # 实际中，可以有评分、购买次数等显式反馈

        # 创建用户-物品矩阵
        # pivot_table 会聚合重复的 user_id-book_id 对，这里用 count 示例
        self.user_item_matrix = interactions_df.pivot_table(
            index='user_id',
            columns='book_id',
            aggfunc=lambda x: 1, # 简单标记用户是否与图书有交互
            fill_value=0
        )
        self.all_user_ids = self.user_item_matrix.index.tolist()
        self.all_book_ids = self.user_item_matrix.columns.tolist()
        print(f"User-Item matrix created with {len(self.all_user_ids)} users and {len(self.all_book_ids)} books.")
        return True

    def train_model(self):
        """
        训练推荐模型 (这里是基于用户的协同过滤)
        计算用户之间的相似度
        """
        if not self._prepare_data():
            return

        print("Training recommendation model (User-based Collaborative Filtering)...")
        # 计算用户之间的余弦相似度
        self.user_similarity_matrix = cosine_similarity(self.user_item_matrix)
        self.user_similarity_df = pd.DataFrame(
            self.user_similarity_matrix,
            index=self.all_user_ids,
            columns=self.all_user_ids
        )
        print("User similarity matrix calculated.")

    def generate_recommendations(self):
        """为所有用户生成推荐并存储到Redis"""
        if self.user_similarity_matrix is None or self.user_item_matrix is None:
            print("Model not trained. Please run train_model() first.")
            return

        print("Generating recommendations for all users...")
        for user_id in self.all_user_ids:
            # 找到最相似的用户
            similar_users = self.user_similarity_df[user_id].sort_values(ascending=False)
            similar_users = similar_users[similar_users.index != user_id] # 排除自己

            recommended_books = set()
            user_seen_books = set(
                self.user_item_matrix.loc[user_id][self.user_item_matrix.loc[user_id] == 1].index.tolist()
            )

            # 从相似用户那里获取他们交互过的、当前用户未交互过的图书
            for s_user_id, similarity_score in similar_users.items():
                if similarity_score > 0: # 只有相似度大于0才考虑
                    similar_user_items = self.user_item_matrix.loc[s_user_id][self.user_item_matrix.loc[s_user_id] == 1].index.tolist()
                    for book_id in similar_user_items:
                        if book_id not in user_seen_books:
                            recommended_books.add(book_id)
                        if len(recommended_books) >= Config.TOP_N_RECOMMENDATIONS:
                            break
                if len(recommended_books) >= Config.TOP_N_RECOMMENDATIONS:
                    break

            # 将推荐结果存入 Redis
            self.redis_client.set_user_recommendations(user_id, list(recommended_books)[:Config.TOP_N_RECOMMENDATIONS])
        print("Recommendations generated and stored in Redis for all users.")

if __name__ == '__main__':
    trainer = RecommendationTrainer()
    trainer.train_model()
    trainer.generate_recommendations()
    print("Offline recommendation process completed.")

    # 验证某个用户的推荐
    test_user_id = trainer.all_user_ids[0] if trainer.all_user_ids else None
    if test_user_id:
        rec_books = RedisClient().get_user_recommendations(test_user_id)
        print(f"\nExample: Recommendations for user {test_user_id}: {rec_books}")