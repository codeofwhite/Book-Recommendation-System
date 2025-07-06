# models/trainer.py

import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer # 用于文本特征提取

# 确保导入路径正确
from data.data_loader import DataLoader
from utils.redis_utils import RedisClient
from config import Config

# 配置日志，设置为 DEBUG 级别以便更详细的输出
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class RecommendationTrainer:
    def __init__(self):
        self.data_loader = DataLoader()
        self.redis_client = RedisClient()
        
        self.users_df = None
        self.books_df = None
        self.interactions_df = None # 用于存储合并后的交互数据

        self.user_item_matrix = None
        self.item_cf_similarity_matrix = None # Item-Item协同过滤相似度
        self.item_content_similarity_matrix = None # 基于内容的相似度
        
        self.user_to_idx = {}
        self.idx_to_user = {}
        self.item_to_idx = {}
        self.idx_to_item = {}

        self.popular_books_list = []

    def load_all_data(self):
        """加载所有需要的数据，包括用户、图书和多种交互数据。"""
        logging.info("Loading all necessary data...")
        try:
            self.users_df = self.data_loader.load_user_profiles()
            self.books_df = self.data_loader.load_book_data()
            
            if not self.books_df.empty:
                self.books_df['book_id'] = self.books_df['book_id'].astype(str)
                # 确保 genres 和 author 字段存在且是字符串，方便后续处理
                self.books_df['genres'] = self.books_df['genres'].fillna('').astype(str)
                self.books_df['author'] = self.books_df['author'].fillna('').astype(str)
            else:
                logging.warning("No book data loaded. This may affect filtering and recommendations.")
                return pd.DataFrame() 

            logging.debug(f"Loaded {len(self.users_df)} users.")
            logging.debug(f"Loaded {len(self.books_df)} books.")

            behavior_logs = self.data_loader.load_user_behavior_logs()
            book_favorites = self.data_loader.load_book_favorites()
            book_likes = self.data_loader.load_book_likes()
            book_reviews = self.data_loader.load_book_reviews()

            logging.debug(f"Raw behavior logs: {len(behavior_logs)}")
            logging.debug(f"Raw book favorites: {len(book_favorites)}")
            logging.debug(f"Raw book likes: {len(book_likes)}")
            logging.debug(f"Raw book reviews: {len(book_reviews)}")

            interactions_from_logs = pd.DataFrame(columns=['user_id', 'item_id', 'timestamp', 'interaction_value'])
            if not behavior_logs.empty:
                behavior_logs['item_id'] = behavior_logs['item_id'].astype(str)
                behavior_logs['user_id'] = behavior_logs['user_id'].astype(str)
                interactions_from_logs = behavior_logs[['user_id', 'item_id', 'timestamp', 'interaction_value']]
            
            interactions_from_favorites = pd.DataFrame(columns=['user_id', 'item_id', 'timestamp', 'interaction_value'])
            if not book_favorites.empty:
                book_favorites['book_id'] = book_favorites['book_id'].astype(str)
                book_favorites['user_id'] = book_favorites['user_id'].astype(str)
                interactions_from_favorites = book_favorites[['user_id', 'book_id', 'timestamp', 'interaction_value']].rename(columns={'book_id': 'item_id'})

            interactions_from_likes = pd.DataFrame(columns=['user_id', 'item_id', 'timestamp', 'interaction_value'])
            if not book_likes.empty:
                book_likes['book_id'] = book_likes['book_id'].astype(str)
                book_likes['user_id'] = book_likes['user_id'].astype(str)
                interactions_from_likes = book_likes[['user_id', 'book_id', 'timestamp', 'interaction_value']].rename(columns={'book_id': 'item_id'})

            interactions_from_reviews = pd.DataFrame(columns=['user_id', 'item_id', 'timestamp', 'interaction_value'])
            if not book_reviews.empty:
                book_reviews['book_id'] = book_reviews['book_id'].astype(str)
                book_reviews['user_id'] = book_reviews['user_id'].astype(str)
                interactions_from_reviews = book_reviews[['user_id', 'book_id', 'timestamp', 'interaction_value']].rename(columns={'book_id': 'item_id'})
            
            all_interactions = pd.concat([
                interactions_from_logs,
                interactions_from_favorites,
                interactions_from_likes,
                interactions_from_reviews
            ], ignore_index=True)

            logging.info(f"Total raw interactions loaded: {len(all_interactions)}")

            valid_user_ids = self.users_df['id'].astype(str).unique() if not self.users_df.empty else pd.Series([])
            valid_book_ids = self.books_df['book_id'].astype(str).unique() if not self.books_df.empty else pd.Series([])

            logging.debug(f"Unique users in raw interactions: {all_interactions['user_id'].nunique()}")
            logging.debug(f"Unique items in raw interactions: {all_interactions['item_id'].nunique()}")

            all_interactions = all_interactions[
                all_interactions['user_id'].isin(valid_user_ids) & 
                all_interactions['item_id'].isin(valid_book_ids)
            ]
            
            logging.info(f"Total valid interactions after filtering: {len(all_interactions)}")
            logging.debug(f"Unique users in valid interactions: {all_interactions['user_id'].nunique()}")
            logging.debug(f"Unique items in valid interactions: {all_interactions['item_id'].nunique()}")

            if all_interactions.empty:
                logging.warning("No valid interactions after filtering. Model training might not be effective.")
                self.interactions_df = pd.DataFrame()
                return self.interactions_df

            # 对交互值进行归一化或加权
            # 修正：确保归一化结果在 0-1 之间，并且处理 max_val == min_val 的情况
            # 引入一个小的 epsilon 防止除零
            min_val = all_interactions['interaction_value'].min()
            max_val = all_interactions['interaction_value'].max()
            
            if max_val > min_val:
                all_interactions['normalized_interaction'] = (all_interactions['interaction_value'] - min_val) / (max_val - min_val + 1e-6) # + 1e-6 epsilon
            else:
                all_interactions['normalized_interaction'] = 0.5 # 所有值都相同，给一个中间值

            self.interactions_df = all_interactions # 存储到实例属性
            logging.debug("Interactions DataFrame head after processing:")
            logging.debug(self.interactions_df.head())
            
            self._precalculate_popular_books()

            return self.interactions_df
        
        except Exception as e:
            logging.error(f"Error loading all necessary data: {e}")
            logging.error(traceback.format_exc())
            self.interactions_df = pd.DataFrame()
            return self.interactions_df

    def create_user_item_matrix(self):
        """
        根据interactions_df创建用户-物品矩阵。
        同时创建并保存用户ID和物品ID的映射。
        """
        logging.info("Creating user-item matrix...")
        if self.interactions_df.empty:
            logging.warning("Interactions DataFrame is empty. Cannot create user-item matrix.")
            # 确保映射至少包含所有已知用户和图书，即使没有交互数据
            final_user_ids = self.users_df['id'].astype(str).unique()
            final_item_ids = self.books_df['book_id'].astype(str).unique()
            self.user_to_idx = {user: i for i, user in enumerate(final_user_ids)}
            self.idx_to_user = {i: user for user, i in self.user_to_idx.items()}
            self.item_to_idx = {item: i for i, item in enumerate(final_item_ids)}
            self.idx_to_item = {i: item for item, i in self.item_to_idx.items()}
            self.user_item_matrix = csr_matrix((len(self.user_to_idx), len(self.item_to_idx))) # 创建空矩阵
            logging.warning(f"Created empty user-item matrix with shape: {self.user_item_matrix.shape}")
            return


        self.interactions_df['user_id'] = self.interactions_df['user_id'].astype(str)
        self.interactions_df['item_id'] = self.interactions_df['item_id'].astype(str)

        all_user_ids = self.users_df['id'].astype(str).unique()
        all_item_ids = self.books_df['book_id'].astype(str).unique()

        final_user_ids = np.union1d(all_user_ids, self.interactions_df['user_id'].unique())
        final_item_ids = np.union1d(all_item_ids, self.interactions_df['item_id'].unique())

        self.user_to_idx = {user: i for i, user in enumerate(final_user_ids)}
        self.idx_to_user = {i: user for user, i in self.user_to_idx.items()}
        
        self.item_to_idx = {item: i for i, item in enumerate(final_item_ids)}
        self.idx_to_item = {i: item for item, i in self.item_to_idx.items()}

        self.interactions_df['user_idx'] = self.interactions_df['user_id'].map(self.user_to_idx)
        self.interactions_df['item_idx'] = self.interactions_df['item_id'].map(self.item_to_idx)

        num_users = len(self.user_to_idx)
        num_items = len(self.item_to_idx)

        self.user_item_matrix = csr_matrix(
            (self.interactions_df['normalized_interaction'], 
             (self.interactions_df['user_idx'], self.interactions_df['item_idx'])),
            shape=(num_users, num_items)
        )
        logging.info(f"User-item matrix created with shape: {self.user_item_matrix.shape}")
        logging.debug(f"User-item matrix sparsity: {self.user_item_matrix.nnz / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]):.6f}")

    def calculate_item_similarity(self):
        """
        计算物品之间的协同过滤相似度，并新增基于内容的相似度。
        最后进行相似度融合。
        """
        logging.info("Calculating item similarities...")

        # --- 1. 计算 Item-Item 协同过滤相似度 ---
        logging.info("Calculating Item-Item Collaborative Filtering similarity...")
        if self.user_item_matrix is None or self.user_item_matrix.shape[1] == 0:
            logging.warning("User-item matrix is not available or has no items for CF similarity.")
            self.item_cf_similarity_matrix = None
        else:
            item_user_matrix = self.user_item_matrix.T.tocsr()
            self.item_cf_similarity_matrix = cosine_similarity(item_user_matrix)
            logging.info(f"Item CF similarity matrix calculated with shape: {self.item_cf_similarity_matrix.shape}")
            logging.debug(f"Item CF similarity matrix: Min={np.min(self.item_cf_similarity_matrix):.4f}, Max={np.max(self.item_cf_similarity_matrix):.4f}, Mean={np.mean(self.item_cf_similarity_matrix):.4f}")

        # --- 2. 计算基于内容的相似度 ---
        logging.info("Calculating Content-Based similarity...")
        if self.books_df.empty or 'genres' not in self.books_df.columns or 'author' not in self.books_df.columns:
            logging.warning("Book data or required content columns (genres, author) are missing for content-based similarity.")
            self.item_content_similarity_matrix = None
        else:
            # 创建用于 TF-IDF 的文档：将 genres 和 author 拼接起来
            # 注意：如果 genres 是列表，需要先 join 成字符串
            self.books_df['content_features'] = self.books_df['genres'] + ' ' + self.books_df['author']
            
            # 确保 books_df 的索引与 self.item_to_idx 的顺序一致
            # 或者更稳妥的做法是，使用 item_to_idx 的顺序来构建 content_features_array
            
            # 构建一个与 item_to_idx 顺序一致的特征列表
            ordered_content_features = [
                self.books_df[self.books_df['book_id'] == self.idx_to_item[i]]['content_features'].iloc[0]
                for i in range(len(self.idx_to_item))
                if self.idx_to_item[i] in self.books_df['book_id'].values
            ]
            
            # Handle cases where item_id from idx_to_item might not be in books_df (shouldn't happen with proper filtering)
            if len(ordered_content_features) != len(self.idx_to_item):
                 logging.warning("Mismatch in item_to_idx and books_df for content features. Some items might be missing.")
                 # Fallback: create content features only for items present in books_df, then handle missing in similarity matrix
                 # For simplicity, if this happens, we might need a more robust mapping or default empty strings
                 # For now, assume all items in idx_to_item are in books_df for content features
                 pass

            tfidf_vectorizer = TfidfVectorizer(stop_words='english', min_df=1) # min_df=1 包含所有词
            content_matrix = tfidf_vectorizer.fit_transform(ordered_content_features)
            self.item_content_similarity_matrix = cosine_similarity(content_matrix)
            logging.info(f"Item Content similarity matrix calculated with shape: {self.item_content_similarity_matrix.shape}")
            logging.debug(f"Item Content similarity matrix: Min={np.min(self.item_content_similarity_matrix):.4f}, Max={np.max(self.item_content_similarity_matrix):.4f}, Mean={np.mean(self.item_content_similarity_matrix):.4f}")
            
            # 打印哈利波特系列书之间的内容相似度
            self._debug_harry_potter_content_similarity()


        # --- 3. 相似度融合 (如果两者都存在) ---
        if self.item_cf_similarity_matrix is not None and self.item_content_similarity_matrix is not None:
            logging.info("Fusing CF and Content-Based similarity matrices...")
            # 确保两个矩阵维度一致
            if self.item_cf_similarity_matrix.shape != self.item_content_similarity_matrix.shape:
                logging.error("CF and Content similarity matrices have different shapes! Cannot fuse.")
                # Fallback to CF only or content only
                self.item_similarity_matrix = self.item_cf_similarity_matrix if self.item_cf_similarity_matrix is not None else self.item_content_similarity_matrix
            else:
                # 简单加权平均融合
                # Config.SIMILARITY_FUSION_ALPHA 控制 CF 相似度的权重
                self.item_similarity_matrix = (
                    Config.SIMILARITY_FUSION_ALPHA * self.item_cf_similarity_matrix +
                    (1 - Config.SIMILARITY_FUSION_ALPHA) * self.item_content_similarity_matrix
                )
                logging.info(f"Fused item similarity matrix created with shape: {self.item_similarity_matrix.shape}")
                logging.debug(f"Fused item similarity matrix: Min={np.min(self.item_similarity_matrix):.4f}, Max={np.max(self.item_similarity_matrix):.4f}, Mean={np.mean(self.item_similarity_matrix):.4f}")
        elif self.item_cf_similarity_matrix is not None:
            self.item_similarity_matrix = self.item_cf_similarity_matrix
            logging.warning("Only CF similarity matrix available. Using CF similarity only.")
        elif self.item_content_similarity_matrix is not None:
            self.item_similarity_matrix = self.item_content_similarity_matrix
            logging.warning("Only Content-based similarity matrix available. Using Content-based similarity only.")
        else:
            self.item_similarity_matrix = None
            logging.error("No item similarity matrix could be calculated!")

    def _debug_harry_potter_content_similarity(self):
        """
        调试：打印哈利波特系列书籍之间的内容相似度。
        假设哈利波特系列书籍的 ID 包含 "Harry_Potter"。
        """
        if self.item_content_similarity_matrix is None:
            return

        hp_book_ids = [
            item_id for item_id in self.books_df['book_id'].unique()
            if "Harry_Potter" in str(item_id) # 确保是字符串比较
        ]
        
        if len(hp_book_ids) > 1:
            logging.debug(f"Found {len(hp_book_ids)} Harry Potter books: {hp_book_ids}")
            logging.debug("Content similarity between Harry Potter books:")
            for i, hp1_id in enumerate(hp_book_ids):
                for j, hp2_id in enumerate(hp_book_ids):
                    if i < j: # Only print unique pairs
                        if hp1_id in self.item_to_idx and hp2_id in self.item_to_idx:
                            idx1 = self.item_to_idx[hp1_id]
                            idx2 = self.item_to_idx[hp2_id]
                            sim = self.item_content_similarity_matrix[idx1, idx2]
                            logging.debug(f"  - {hp1_id} vs {hp2_id}: {sim:.4f}")
                        else:
                            logging.warning(f"Harry Potter book ID not found in item_to_idx: {hp1_id} or {hp2_id}")
            logging.debug("--- End Harry Potter Content Similarity Debug ---")
        elif len(hp_book_ids) == 1:
            logging.debug(f"Only one Harry Potter book found: {hp_book_ids[0]}. Cannot calculate pairwise content similarity.")
        else:
            logging.debug("No Harry Potter books found for content similarity debug.")


    def train_model(self):
        """
        训练推荐模型的主逻辑。
        """
        logging.info("Starting model training process...")
        
        self.load_all_data()

        # 确保 interactions_df 不为空，否则 create_user_item_matrix 会创建空矩阵
        # 即使 interactions_df 为空，也需要创建映射和空矩阵，以便后续内容相似度计算
        self.create_user_item_matrix() 

        # 即使 user_item_matrix 是空的，我们也可以尝试计算内容相似度
        self.calculate_item_similarity()

        if self.item_similarity_matrix is None:
            logging.warning("No item similarity matrix could be calculated after all attempts. Model training might be incomplete.")
            return

        logging.info("Model training completed.")

    def get_top_n_recommendations_for_user(self, user_id, n=Config.TOP_N_RECOMMENDATIONS, 
                                            cf_weight=Config.CF_POPULARITY_MIX_ALPHA, 
                                            similarity_weight=Config.SIMILARITY_FUSION_ALPHA): # cf_weight 是用于 CF vs Popularity
        """
        为指定用户生成 Top-N 推荐。
        融合了协同过滤预测分数、内容相似度（通过 fused similarity matrix）和流行度。
        """
        logging.info(f"Generating top {n} recommendations for user {user_id}...")
        user_id_str = str(user_id)
        
        if self.item_similarity_matrix is None:
            logging.warning("Item similarity matrix is missing. Returning popular books as fallback.")
            return self._get_popular_books(n)
        
        # 获取用户索引
        user_idx = self.user_to_idx.get(user_id_str)

        # 预先获取热门图书列表（如果模型训练失败，则直接返回此列表）
        popular_books_n = self._get_popular_books(n)
        
        if user_idx is None: # 用户不在训练数据中 (新用户或无交互用户)
            logging.info(f"User {user_id_str} not found in user-item matrix mapping or has no interactions. Returning popular books.")
            return popular_books_n
        
        user_interactions_sparse = self.user_item_matrix[user_idx, :]
        user_interactions_dense = user_interactions_sparse.toarray().flatten()
        interacted_item_indices = user_interactions_dense.nonzero()[0]
        
        if len(interacted_item_indices) == 0:
            logging.info(f"User {user_id_str} has no valid interactions. Returning popular books as fallback.")
            return popular_books_n

        logging.debug(f"User {user_id_str} (idx: {user_idx}) has {len(interacted_item_indices)} non-zero interactions in matrix.")
        if user_id_str == '7': # Specific debug for user 7
             for idx in interacted_item_indices:
                 item_id = self.idx_to_item[idx]
                 interaction_value = user_interactions_dense[idx]
                 logging.debug(f"  - User {user_id_str} interacted with item {item_id} (idx: {idx}) with normalized_interaction: {interaction_value:.4f}")

        # 计算预测分数：使用融合后的相似度矩阵
        predicted_scores = user_interactions_dense.reshape(1, -1).dot(self.item_similarity_matrix).flatten()
        
        # 对预测分数进行归一化，使其范围在0到1之间，方便与流行度混合
        min_pred_score = np.min(predicted_scores)
        max_pred_score = np.max(predicted_scores)
        if max_pred_score > min_pred_score:
            normalized_pred_scores = (predicted_scores - min_pred_score) / (max_pred_score - min_pred_score + 1e-6) # add epsilon
        else:
            normalized_pred_scores = np.full_like(predicted_scores, 0.5)

        logging.debug(f"User {user_id_str} predicted scores (before filtering): Min={np.min(predicted_scores):.4f}, Max={np.max(predicted_scores):.4f}, Mean={np.mean(predicted_scores):.4f}")
        logging.debug(f"User {user_id_str} normalized scores (before filtering): Min={np.min(normalized_pred_scores):.4f}, Max={np.max(normalized_pred_scores):.4f}, Mean={np.mean(normalized_pred_scores):.4f}")

        # 获取所有物品的流行度分数 (0-1归一化)
        popular_scores = np.zeros(len(self.idx_to_item))
        if self.popular_books_list:
            # 找到流行度分数的最大最小值来做归一化
            pop_values = [book['score'] for book in self.popular_books_list]
            min_pop_score = min(pop_values) if pop_values else 0
            max_pop_score = max(pop_values) if pop_values else 0
            
            if max_pop_score > min_pop_score:
                norm_factor = max_pop_score - min_pop_score + 1e-6
            else:
                norm_factor = 1.0 # 如果所有流行度分数都相同

            for book in self.popular_books_list:
                item_id = book['book_id']
                if item_id in self.item_to_idx:
                    idx = self.item_to_idx[item_id]
                    popular_scores[idx] = (book['score'] - min_pop_score) / norm_factor if norm_factor > 0 else 0.5
        
        # 混合预测分数： predicted_score = cf_weight * normalized_pred_score + (1 - cf_weight) * popular_score
        mixed_scores = cf_weight * normalized_pred_scores + (1 - cf_weight) * popular_scores

        # 将已交互的物品的预测分数设置为负无穷，避免重复推荐
        mixed_scores[interacted_item_indices] = -np.inf

        # 获取得分最高的 Top-N 物品索引
        recommended_item_indices = np.argsort(mixed_scores)[::-1]
        
        final_top_n_item_indices = []
        for idx in recommended_item_indices:
            if mixed_scores[idx] != -np.inf: # 确保不是已交互物品
                final_top_n_item_indices.append(idx)
                if len(final_top_n_item_indices) >= n:
                    break
        
        final_recommendations = []
        books_df_str_id = self.books_df.set_index('book_id', drop=False) # 创建一个以book_id为索引的副本

        for idx in final_top_n_item_indices:
            item_id = self.idx_to_item[idx]
            if item_id in books_df_str_id.index:
                book_info = books_df_str_id.loc[item_id]
                final_recommendations.append({
                    'book_id': item_id,
                    'title': book_info['title'],
                    'score': float(mixed_scores[idx]) # 返回混合后的分数
                })
            else:
                logging.warning(f"Book ID {item_id} from recommendations not found in books_df during final compilation.")
                final_recommendations.append({'book_id': item_id, 'title': 'N/A', 'score': float(mixed_scores[idx])})
        
        # 如果协同过滤推荐不足，且设置了兜底，则补充热门图书
        if len(final_recommendations) < n and Config.FALLBACK_TO_POPULAR_IF_LESS_THAN_N_CF_RECS:
            logging.info(f"User {user_id_str} generated {len(final_recommendations)} CF/Mixed recommendations. Supplementing with popular books to reach {n} items.")
            current_recommended_ids = {rec['book_id'] for rec in final_recommendations}
            interacted_ids_set = {self.idx_to_item[idx] for idx in interacted_item_indices}

            supplemented_count = 0
            for popular_book in self.popular_books_list:
                if popular_book['book_id'] not in current_recommended_ids and popular_book['book_id'] not in interacted_ids_set:
                    final_recommendations.append(popular_book)
                    supplemented_count += 1
                    if len(final_recommendations) >= n:
                        break
            logging.debug(f"Supplemented {supplemented_count} popular books for user {user_id_str}.")

        # 最后按分数降序排序，即使补充了热门书，也保持一致的排序逻辑
        final_recommendations = sorted(final_recommendations, key=lambda x: x['score'], reverse=True)[:n]

        logging.info(f"Generated {len(final_recommendations)} total recommendations for user {user_id_str}.")
        return final_recommendations

    def _precalculate_popular_books(self, n=Config.TOP_N_RECOMMENDATIONS * 2): # 预计算多一些以备补充
        """
        预计算最热门的图书列表，存储在实例中，减少重复计算。
        热门定义：总交互值最高的图书。
        """
        logging.debug(f"Precalculating top {n} popular books.")
        if self.interactions_df is None or self.interactions_df.empty:
            logging.warning("No interactions data available to precalculate popular books.")
            self.popular_books_list = []
            return
        
        popular_items_df = self.interactions_df.groupby('item_id')['normalized_interaction'].sum().reset_index()
        popular_items_df = popular_items_df.sort_values(by='normalized_interaction', ascending=False)
        
        # 获取 Top-N 热门图书 ID 和它们的聚合分数
        # 使用 .head(n) 获取前 n 个热门项
        popular_items_top_n = popular_items_df.head(n)

        precalculated_list = []
        if self.books_df is not None and not self.books_df.empty:
            books_df_str_id = self.books_df.set_index('book_id', drop=False)
            for _, row in popular_items_top_n.iterrows():
                item_id = row['item_id']
                score = row['normalized_interaction']
                if item_id in books_df_str_id.index:
                    book_info = books_df_str_id.loc[item_id]
                    precalculated_list.append({
                        'book_id': item_id,
                        'title': book_info['title'],
                        'score': float(score) 
                    })
                else:
                    logging.warning(f"Popular book ID {item_id} not found in books_df during precalculation.")
        else:
            logging.warning("Book data not available for popular books precalculation.")
            precalculated_list = [{'book_id': row['item_id'], 'title': 'N/A', 'score': float(row['normalized_interaction'])} for _, row in popular_items_top_n.iterrows()]
        
        self.popular_books_list = precalculated_list
        logging.debug(f"Precalculated {len(self.popular_books_list)} popular books.")


    def _get_popular_books(self, n=Config.TOP_N_RECOMMENDATIONS):
        """
        从预计算的列表中返回最热门的图书。
        """
        logging.info(f"Returning top {n} popular books as fallback recommendation.")
        if not self.popular_books_list:
            logging.warning("Popular books list is empty. Cannot provide fallback recommendations.")
            return []
        
        return self.popular_books_list[:n]

    def generate_recommendations(self):
        """为所有用户生成推荐并存储到 Redis。"""
        logging.info("Starting recommendation generation for all users...")
        if self.users_df is None or self.item_similarity_matrix is None:
            logging.warning("Model not trained or required data/matrices are missing. Cannot generate recommendations.")
            return

        all_user_ids = self.users_df['id'].unique()
        
        for user_id in all_user_ids:
            try:
                recommendations_list = self.get_top_n_recommendations_for_user(user_id, Config.TOP_N_RECOMMENDATIONS)
                
                if recommendations_list:
                    self.redis_client.store_user_recommendations(str(user_id), recommendations_list)
                    logging.debug(f"Stored {len(recommendations_list)} recommendations for user {user_id}")
                else:
                    logging.info(f"No recommendations generated for user {user_id} after all strategies.")
            except Exception as e:
                logging.error(f"Error generating or storing recommendations for user {user_id}: {e}")
                logging.error(traceback.format_exc())

        logging.info("Recommendation generation completed for all users.")

# --- 离线训练任务的入口点 ---
def run_offline_training_job():
    """
    运行离线推荐模型训练和生成任务。
    通常在后台或作为定时任务执行。
    """
    print("--- Starting offline recommendation job ---")
    logging.info("--- Starting offline recommendation job ---")
    try:
        trainer = RecommendationTrainer()

        print("Attempting to train model...")
        logging.info("Attempting to train model...")
        trainer.train_model()
        print("Model training attempt completed.")
        logging.info("Model training attempt completed.")

        print("Attempting to generate recommendations...")
        logging.info("Attempting to generate recommendations...")
        trainer.generate_recommendations()
        print("Recommendation generation attempt completed.")
        logging.info("Recommendation generation attempt completed.")

        print("--- Offline recommendation job finished successfully ---")
        logging.info("--- Offline recommendation job finished successfully ---")
    except Exception as e:
        print(f"--- Offline recommendation job failed with error: {e} ---")
        logging.error(f"--- Offline recommendation job failed with error: {e} ---")
        logging.error(traceback.format_exc())