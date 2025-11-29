import json
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np # 保持 NumPy 导入，因为它是其他库的基础
import logging
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer 
import math
# import pickle # 移除 pickle 导入，因为不再用于 Redis 向量存储，只在 Flink 状态中使用

# 确保导入路径正确
from data.data_loader import DataLoader
from utils.redis_utils import RedisClient
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RecommendationTrainer:
    def __init__(self):
        self.data_loader = DataLoader()
        self.redis_client = RedisClient()
        
        self.users_df = None
        self.books_df = None
        self.interactions_df = None 

        self.user_item_matrix = None
        self.item_cf_similarity_matrix = None 
        self.item_content_similarity_matrix = None 
        self.item_similarity_matrix = None 
        
        self.user_to_idx = {}
        self.idx_to_user = {}
        self.item_to_idx = {}
        self.idx_to_item = {}

        self.popular_books_list = []
        self.tfidf_vectorizer = None 
        self.content_matrix = None 

    def get_book_feature_vector_from_redis(self, book_id: str):
        """
        从 Redis 获取指定图书的特征向量。
        注意：此方法用于调试或特殊场景，实际训练时通常直接使用 self.content_matrix。
        如果需要从 Redis 读取，需要适配 Redis 中存储的 JSON 格式。
        """
        key = f"{Config.REDIS_BOOK_FEATURES_PREFIX}{book_id}"
        # 从 Redis 获取的是字节串
        json_bytes = self.redis_client.get(key)
        if json_bytes:
            try:
                # 解码为 UTF-8 字符串，然后解析为 Python 列表
                return json.loads(json_bytes.decode('utf-8'))
            except Exception as e:
                logging.error(f"Failed to decode JSON feature vector for book_id {book_id}: {e}", exc_info=True)
                return None
        return None

    def store_item_feature_vectors(self):
        """
        将物品特征向量存储到 Redis。
        关键修改：将 NumPy 数组转换为 Python 列表，再序列化为 JSON 字符串。
        """
        logging.info("Storing item feature vectors to Redis...")
        if self.content_matrix is None or self.books_df.empty:
            logging.warning("Content matrix or books_df is missing. Cannot store item feature vectors.")
            return

        pipe = self.redis_client.get_pipeline() 
        
        for i, item_id_idx in enumerate(self.idx_to_item):
            item_id = self.idx_to_item[item_id_idx]
            if i < self.content_matrix.shape[0]:
                # 获取特征向量，并转换为 Python 列表
                feature_vector_list = self.content_matrix[i].toarray().flatten().tolist() 
                key = f"{Config.REDIS_BOOK_FEATURES_PREFIX}{item_id}"
                # 将列表序列化为 JSON 字符串，并编码为 UTF-8 字节串存储
                pipe.set(key, json.dumps(feature_vector_list, ensure_ascii=False).encode('utf-8')) 
            else:
                logging.warning(f"Index {i} out of bounds for content_matrix (shape {self.content_matrix.shape}). Skipping item {item_id}.")
                
        pipe.execute()
        logging.info(f"Stored {len(self.idx_to_item)} item feature vectors to Redis.")

    def load_all_data(self):
        """加载所有需要的数据，包括用户、图书和多种交互数据。"""
        logging.info("Loading all necessary data...")
        try:
            self.users_df = self.data_loader.load_user_profiles()
            self.books_df = self.data_loader.load_book_data()
            
            if not self.books_df.empty:
                self.books_df['book_id'] = self.books_df['book_id'].astype(str)
                self.books_df['genres'] = self.books_df['genres'].fillna('').astype(str)
                self.books_df['author'] = self.books_df['author'].fillna('').astype(str)
            else:
                logging.warning("No book data loaded. This may affect filtering and recommendations.")
                self.books_df = pd.DataFrame(columns=['book_id', 'title', 'genres', 'author']) 
                return pd.DataFrame() 

            logging.info(f"Loaded {len(self.users_df)} users.")
            logging.info(f"Loaded {len(self.books_df)} books.")

            behavior_logs = self.data_loader.load_user_behavior_logs()
            book_favorites = self.data_loader.load_book_favorites()
            book_likes = self.data_loader.load_book_likes()
            book_reviews = self.data_loader.load_book_reviews()

            logging.info(f"Raw behavior logs: {len(behavior_logs)}")
            logging.info(f"Raw book favorites: {len(book_favorites)}")
            logging.info(f"Raw book likes: {len(book_likes)}")
            logging.info(f"Raw book reviews: {len(book_reviews)}")

            interactions_from_logs = pd.DataFrame(columns=['user_id', 'item_id', 'timestamp', 'interaction_value'])
            if not behavior_logs.empty:
                behavior_logs['item_id'] = behavior_logs['item_id'].astype(str)
                behavior_logs['user_id'] = behavior_logs['userId'].astype(str)
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

            valid_user_ids = self.users_df['id'].astype(str).unique() if self.users_df is not None else pd.Series([])
            valid_book_ids = self.books_df['book_id'].astype(str).unique() if self.books_df is not None else pd.Series([])

            logging.info(f"Unique users in raw interactions: {all_interactions['user_id'].nunique()}")
            logging.info(f"Unique items in raw interactions: {all_interactions['item_id'].nunique()}")

            all_interactions = all_interactions[
                all_interactions['user_id'].isin(valid_user_ids) & 
                all_interactions['item_id'].isin(valid_book_ids)
            ]
            
            logging.info(f"Total valid interactions after filtering: {len(all_interactions)}")
            logging.info(f"Unique users in valid interactions: {all_interactions['user_id'].nunique()}")
            logging.info(f"Unique items in valid interactions: {all_interactions['item_id'].nunique()}")

            if all_interactions.empty:
                logging.warning("No valid interactions after filtering. Model training might not be effective.")
                self.interactions_df = pd.DataFrame()
                self.popular_books_list = [] 
                return self.interactions_df

            min_val = all_interactions['interaction_value'].min()
            max_val = all_interactions['interaction_value'].max()
            
            logging.info(f"Debug: raw interaction_value min: {min_val}")
            logging.info(f"Debug: raw interaction_value max: {max_val}")
            logging.info(f"Debug: raw interaction_value unique values: {all_interactions['interaction_value'].unique()}") 

            if max_val > min_val:
                all_interactions['normalized_interaction'] = (all_interactions['interaction_value'] - min_val) / (max_val - min_val + 1e-6) 
            else:
                all_interactions['normalized_interaction'] = 0.5 
            
            logging.info(f"Debug: normalized_interaction min: {all_interactions['normalized_interaction'].min()}")
            logging.info(f"Debug: normalized_interaction max: {all_interactions['normalized_interaction'].max()}")
            logging.info(f"Debug: normalized_interaction mean: {all_interactions['normalized_interaction'].mean()}")
            logging.info(f"Debug: normalized_interaction head:\n{all_interactions[['user_id', 'item_id', 'interaction_value', 'normalized_interaction']].head()}")


            self.interactions_df = all_interactions 
            logging.info("Interactions DataFrame head after processing:")
            logging.info(self.interactions_df.head())
            
            self._precalculate_popular_books()

            return self.interactions_df
            
        except Exception as e:
            logging.error(f"Error loading all necessary data: {e}")
            logging.error(traceback.format_exc())
            self.interactions_df = pd.DataFrame()
            self.popular_books_list = [] 
            return self.interactions_df

    def create_user_item_matrix(self):
        """
        根据interactions_df创建用户-物品矩阵。
        同时创建并保存用户ID和物品ID的映射。
        """
        logging.info("Creating user-item matrix...")
        if self.interactions_df.empty:
            logging.warning("Interactions DataFrame is empty. Cannot create user-item matrix.")
            # 使用 list() 替代 np.array([])
            final_user_ids = list(self.users_df['id'].astype(str).unique()) if self.users_df is not None else []
            final_item_ids = list(self.books_df['book_id'].astype(str).unique()) if self.books_df is not None else []
            
            self.user_to_idx = {user: i for i, user in enumerate(final_user_ids)}
            self.idx_to_user = {i: user for user, i in self.user_to_idx.items()}
            self.item_to_idx = {item: i for i, item in enumerate(final_item_ids)}
            self.idx_to_item = {i: item for item, i in self.item_to_idx.items()}
            
            # csr_matrix 仍然需要 scipy.sparse，它依赖 NumPy
            self.user_item_matrix = csr_matrix((len(self.user_to_idx), len(self.item_to_idx))) 
            logging.warning(f"Created empty user-item matrix with shape: {self.user_item_matrix.shape}")
            return


        self.interactions_df['user_id'] = self.interactions_df['user_id'].astype(str)
        self.interactions_df['item_id'] = self.interactions_df['item_id'].astype(str)

        # 使用 list() 替代 np.array([])
        all_user_ids = list(self.users_df['id'].astype(str).unique()) if self.users_df is not None else []
        all_item_ids = list(self.books_df['book_id'].astype(str).unique()) if self.books_df is not None else []

        # np.union1d 替换为 Python set 操作
        final_user_ids = list(set(all_user_ids).union(set(self.interactions_df['user_id'].unique())))
        final_item_ids = list(set(all_item_ids).union(set(self.interactions_df['item_id'].unique())))
        
        # 对 union 后的列表进行排序，以确保索引一致性（如果需要）
        final_user_ids.sort()
        final_item_ids.sort()

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
        logging.info(f"User-item matrix sparsity: {self.user_item_matrix.nnz / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]):.6f}")

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
            # cosine_similarity 仍然依赖 sklearn 和 NumPy
            self.item_cf_similarity_matrix = cosine_similarity(item_user_matrix)
            logging.info(f"Item CF similarity matrix calculated with shape: {self.item_cf_similarity_matrix.shape}")
            logging.info(f"Item CF similarity matrix: Min={np.min(self.item_cf_similarity_matrix):.4f}, Max={np.max(self.item_cf_similarity_matrix):.4f}, Mean={np.mean(self.item_cf_similarity_matrix):.4f}")

        # --- 2. 计算基于内容的相似度 ---
        logging.info("Calculating Content-Based similarity...")
        if self.books_df.empty or 'genres' not in self.books_df.columns or 'author' not in self.books_df.columns:
            logging.warning("Book data or required content columns (genres, author) are missing for content-based similarity.")
            self.item_content_similarity_matrix = None
            self.content_matrix = None 
        else:
            self.books_df['content_features'] = self.books_df['genres'] + ' ' + self.books_df['author']
            
            ordered_content_features = []
            for i in range(len(self.idx_to_item)):
                item_id = self.idx_to_item[i]
                book_row = self.books_df[self.books_df['book_id'] == item_id]
                if not book_row.empty:
                    ordered_content_features.append(book_row['content_features'].iloc[0])
                else:
                    logging.warning(f"Item ID {item_id} from idx_to_item not found in books_df for content features. Using empty string.")
                    ordered_content_features.append('') 

            if not ordered_content_features:
                logging.warning("No ordered_content_features generated. Cannot calculate content-based similarity.")
                self.item_content_similarity_matrix = None
                self.content_matrix = None
                return

            # TfidfVectorizer 和 cosine_similarity 仍然依赖 sklearn 和 NumPy
            self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', min_df=1) 
            self.content_matrix = self.tfidf_vectorizer.fit_transform(ordered_content_features) 
            self.item_content_similarity_matrix = cosine_similarity(self.content_matrix)
            logging.info(f"Item Content similarity matrix calculated with shape: {self.item_content_similarity_matrix.shape}")
            logging.info(f"Item Content similarity matrix: Min={np.min(self.item_content_similarity_matrix):.4f}, Max={np.max(self.item_content_similarity_matrix):.4f}, Mean={np.mean(self.item_content_similarity_matrix):.4f}")


        # --- 3. 相似度融合 (如果两者都存在) ---
        if self.item_cf_similarity_matrix is not None and self.item_content_similarity_matrix is not None:
            logging.info("Fusing CF and Content-Based similarity matrices...")
            if self.item_cf_similarity_matrix.shape != self.item_content_similarity_matrix.shape:
                logging.error("CF and Content similarity matrices have different shapes! Cannot fuse.")
                self.item_similarity_matrix = self.item_cf_similarity_matrix if self.item_cf_similarity_matrix is not None else self.item_content_similarity_matrix
            else:
                self.item_similarity_matrix = (
                    Config.SIMILARITY_FUSION_ALPHA * self.item_cf_similarity_matrix +
                    (1 - Config.SIMILARITY_FUSION_ALPHA) * self.item_content_similarity_matrix
                )
                logging.info(f"Fused item similarity matrix created with shape: {self.item_similarity_matrix.shape}")
                logging.info(f"Fused item similarity matrix: Min={np.min(self.item_similarity_matrix):.4f}, Max={np.max(self.item_similarity_matrix):.4f}, Mean={np.mean(self.item_similarity_matrix):.4f}")
        elif self.item_cf_similarity_matrix is not None:
            self.item_similarity_matrix = self.item_cf_similarity_matrix
            logging.warning("Only CF similarity matrix available. Using CF similarity only.")
        elif self.item_content_similarity_matrix is not None:
            self.item_similarity_matrix = self.item_content_similarity_matrix
            logging.warning("Only Content-based similarity matrix available. Using Content-based similarity only.")
        else:
            self.item_similarity_matrix = None
            logging.error("No item similarity matrix could be calculated!")

    def calculate_user_profiles(self):
        """
        计算用户画像向量，并存储到 Redis。
        这里使用用户交互过的物品的特征向量的加权平均作为用户画像。
        关键修改：将 NumPy 数组转换为 Python 列表，再序列化为 JSON 字符串。
        """
        logging.info("Calculating user profiles...")
        if self.user_item_matrix is None or self.content_matrix is None or not self.idx_to_user or not self.idx_to_item:
            logging.warning("User-item matrix, content matrix, or index mappings are missing. Cannot calculate user profiles.")
            return

        pipe = self.redis_client.get_pipeline()
        
        for user_id_idx in range(len(self.idx_to_user)):
            user_id = self.idx_to_user[user_id_idx]
            
            user_interactions_sparse = self.user_item_matrix[user_id_idx, :]
            # .nonzero()[0] 返回的是 NumPy 数组，这里可以保持
            interacted_item_indices = user_interactions_sparse.nonzero()[0] 
            
            # .size 是 NumPy 数组的属性，对于 Python 列表需要用 len()
            if not interacted_item_indices.size: # 保持 .size 是因为它是 NumPy 数组
                logging.info(f"User {user_id} has no interactions, skipping profile calculation.")
                continue

            # .toarray().flatten() 仍然会产生 NumPy 数组
            user_item_scores = user_interactions_sparse.toarray().flatten()[interacted_item_indices]
            
            # np.zeros 替换为 Python 列表初始化
            user_profile_vector = [0.0] * self.content_matrix.shape[1] 
            total_weight = 0.0

            for i, item_idx in enumerate(interacted_item_indices):
                item_id = self.idx_to_item[item_idx]
                if item_idx < self.content_matrix.shape[0]:
                    # .toarray().flatten() 仍然会产生 NumPy 数组，这里需要转换为列表
                    book_feature_vector = self.content_matrix[item_idx].toarray().flatten().tolist()
                else:
                    logging.warning(f"Item index {item_idx} out of bounds for content_matrix. Skipping for user {user_id}.")
                    continue
                
                if book_feature_vector is not None:
                    weight = user_item_scores[i] 
                    # 向量加法和乘法使用列表推导式或循环
                    user_profile_vector = [x + y * weight for x, y in zip(user_profile_vector, book_feature_vector)]
                    total_weight += weight
            
            if total_weight > 0:
                # 向量除法使用列表推导式
                user_profile_vector = [x / total_weight for x in user_profile_vector]
                
                # 计算 L2 范数（模长）的纯 Python 实现
                norm = math.sqrt(sum(x**2 for x in user_profile_vector))
                if norm > 0:
                    user_profile_vector = [x / norm for x in user_profile_vector]
                
                key = f"{Config.REDIS_USER_PROFILE_PREFIX}{user_id}"
                # 将列表序列化为 JSON 字符串，并编码为 UTF-8 字节串存储
                pipe.set(key, json.dumps(user_profile_vector, ensure_ascii=False).encode('utf-8')) 
                logging.info(f"Stored user profile for user {user_id}.")
            else:
                logging.warning(f"Total weight is zero for user {user_id}. Cannot calculate normalized user profile.")
                
        pipe.execute()
        logging.info(f"Stored user profiles for {len(self.idx_to_user)} users to Redis.")

    def train_model(self):
        """
        训练推荐模型的主逻辑。
        """
        logging.info("Starting model training process...")
        
        self.load_all_data()

        self.create_user_item_matrix() 

        self.calculate_item_similarity()

        if self.item_similarity_matrix is None:
            logging.warning("No item similarity matrix could be calculated after all attempts. Model training might be incomplete.")
            return
        
        # 新增：保存物品特征向量到 Redis
        self.store_item_feature_vectors() 
        
        # 新增：保存用户画像向量到 Redis
        self.calculate_user_profiles()

        logging.info("Model training completed.")

    def get_top_n_recommendations_for_user(self, user_id, n=Config.TOP_N_RECOMMENDATIONS, 
                                           cf_weight=Config.CF_POPULARITY_MIX_ALPHA, 
                                           similarity_weight=Config.SIMILARITY_FUSION_ALPHA): 
        """
        为指定用户生成 Top-N 推荐。
        融合了协同过滤预测分数、内容相似度（通过 fused similarity matrix）和流行度。
        """
        logging.info(f"Generating top {n} recommendations for user {user_id}...")
        user_id_str = str(user_id)
        
        user_idx = self.user_to_idx.get(user_id_str)

        popular_books_n = self._get_popular_books(n)
        
        if user_idx is None: 
            logging.info(f"User {user_id_str} not found in user-item matrix mapping or has no interactions. Returning popular books.")
            return popular_books_n
        
        user_interactions_sparse = self.user_item_matrix[user_idx, :]
        # .toarray().flatten() 仍然会产生 NumPy 数组
        user_interactions_dense = user_interactions_sparse.toarray().flatten()
        # .nonzero()[0] 返回的是 NumPy 数组
        interacted_item_indices = user_interactions_dense.nonzero()[0]
        
        # .size 是 NumPy 数组的属性
        if len(interacted_item_indices) == 0: # 保持 len()
            logging.info(f"User {user_id_str} has no valid interactions. Returning popular books as fallback.")
            return popular_books_n
        
        if self.item_similarity_matrix is None:
            logging.warning("Item similarity matrix is missing. Returning popular books as fallback.")
            return popular_books_n


        logging.info(f"User {user_id_str} (idx: {user_idx}) has {len(interacted_item_indices)} non-zero interactions in matrix.")
        if user_id_str == '7': 
            for idx in interacted_item_indices:
                item_id = self.idx_to_item[idx]
                interaction_value = user_interactions_dense[idx]
                logging.info(f"  - User {user_id_str} interacted with item {item_id} (idx: {idx}) with normalized_interaction: {interaction_value:.4f}")

        # .dot() 仍然是 NumPy 矩阵乘法
        predicted_scores = user_interactions_dense.reshape(1, -1).dot(self.item_similarity_matrix).flatten()
        
        # np.min, np.max 替换为 Python 内置 min(), max()
        min_pred_score = float(predicted_scores.min()) # 转换为 Python float
        max_pred_score = float(predicted_scores.max()) # 转换为 Python float
        if max_pred_score > min_pred_score:
            # NumPy 数组操作，保持
            normalized_pred_scores = (predicted_scores - min_pred_score) / (max_pred_score - min_pred_score + 1e-6) 
        else:
            # np.full_like 替换为 NumPy 数组操作
            normalized_pred_scores = np.full_like(predicted_scores, 0.5) 

        logging.info(f"User {user_id_str} predicted scores (before filtering): Min={float(predicted_scores.min()):.4f}, Max={float(predicted_scores.max()):.4f}, Mean={float(predicted_scores.mean()):.4f}")
        logging.info(f"User {user_id_str} normalized scores (before filtering): Min={float(normalized_pred_scores.min()):.4f}, Max={float(normalized_pred_scores.max()):.4f}, Mean={float(normalized_pred_scores.mean()):.4f}")

        # np.zeros 替换为 NumPy 数组操作
        popular_scores = np.zeros(len(self.idx_to_item))
        if self.popular_books_list:
            pop_values = [book['raw_popularity_score'] for book in self.popular_books_list if 'raw_popularity_score' in book and book['raw_popularity_score'] is not None]
            
            min_pop_score = min(pop_values) if pop_values else 0
            max_pop_score = max(pop_values) if pop_values else 0
            
            logging.info(f"Popularity scores for normalization: pop_values={pop_values}, min_pop_score={min_pop_score}, max_pop_score={max_pop_score}")

            if max_pop_score > min_pop_score:
                norm_factor = max_pop_score - min_pop_score + 1e-6
            else:
                norm_factor = 1.0 

            for book in self.popular_books_list:
                item_id = book['book_id']
                if item_id in self.item_to_idx:
                    idx = self.item_to_idx[item_id]
                    raw_pop_score_val = book.get('raw_popularity_score', 0.0)
                    if raw_pop_score_val is None: 
                        raw_pop_score_val = 0.0

                    popular_scores[idx] = (raw_pop_score_val - min_pop_score) / norm_factor if norm_factor > 0 else 0.0 
                    logging.info(f"Item {item_id} (idx: {idx}) raw_pop_score_val={raw_pop_score_val:.4f}, normalized_pop_score={popular_scores[idx]:.4f}")
        else:
            logging.info("popular_books_list is empty. Popularity scores will remain zero.")
        
        # NumPy 数组操作，保持
        mixed_scores = cf_weight * normalized_pred_scores + (1 - cf_weight) * popular_scores

        # NumPy 数组操作，保持
        mixed_scores[interacted_item_indices] = -np.inf

        # np.argsort 仍然是 NumPy 操作，保持
        recommended_item_indices = np.argsort(mixed_scores)[::-1]
        
        final_top_n_item_indices = []
        for idx in recommended_item_indices:
            # np.inf 仍然是 NumPy 常量，保持
            if mixed_scores[idx] != -np.inf: 
                final_top_n_item_indices.append(idx)
                if len(final_top_n_item_indices) >= n:
                    break
        
        final_recommendations = []
        books_df_str_id = self.books_df.set_index('book_id', drop=False) 

        for idx in final_top_n_item_indices:
            item_id = self.idx_to_item[idx]
            current_raw_cf_score = float(normalized_pred_scores[idx]) if user_idx is not None else 0.0
            current_raw_popularity_score = float(popular_scores[idx]) 

            logging.info(f"Final Rec Item {item_id} (idx: {idx}): mixed_score={float(mixed_scores[idx]):.4f}, raw_cf_score={current_raw_cf_score:.4f}, raw_popularity_score={current_raw_popularity_score:.4f}")

            if item_id in books_df_str_id.index:
                book_info = books_df_str_id.loc[item_id]
                final_recommendations.append({
                    'book_id': item_id,
                    'title': str(book_info['title']), # 强制转换为字符串
                    'score': float(mixed_scores[idx]), # 确保分数是 float
                    'raw_cf_score': current_raw_cf_score, 
                    'raw_popularity_score': current_raw_popularity_score 
                })
            else:
                logging.warning(f"Book ID {item_id} from recommendations not found in books_df during final compilation. Using default info.")
                final_recommendations.append({
                    'book_id': item_id, 
                    'title': 'N/A', 
                    'score': float(mixed_scores[idx]),
                    'raw_cf_score': current_raw_cf_score,
                    'raw_popularity_score': current_raw_popularity_score
                })
        
        if len(final_recommendations) < n and Config.FALLBACK_TO_POPULAR_IF_LESS_THAN_N_CF_RECS:
            logging.info(f"User {user_id_str} generated {len(final_recommendations)} CF/Mixed recommendations. Supplementing with popular books to reach {n} items.")
            current_recommended_ids = {rec['book_id'] for rec in final_recommendations}
            interacted_ids_set = {self.idx_to_item[idx] for idx in interacted_item_indices}

            supplemented_count = 0
            for popular_book in self.popular_books_list:
                if popular_book['book_id'] not in current_recommended_ids and popular_book['book_id'] not in interacted_ids_set:
                    supplemented_book = {
                        'book_id': popular_book['book_id'],
                        'title': popular_book['title'],
                        'score': popular_book['score'], 
                        'raw_cf_score': popular_book.get('raw_cf_score', 0.0), 
                        'raw_popularity_score': popular_book.get('raw_popularity_score', 0.0) 
                    }
                    final_recommendations.append(supplemented_book)
                    supplemented_count += 1
                    if len(final_recommendations) >= n:
                        break
            logging.info(f"Supplemented {supplemented_count} popular books for user {user_id_str}.")

        final_recommendations = sorted(final_recommendations, key=lambda x: x['score'], reverse=True)[:n]

        logging.info(f"Generated {len(final_recommendations)} total recommendations for user {user_id_str}.")
        return final_recommendations

    def _precalculate_popular_books(self, n=Config.TOP_N_RECOMMENDATIONS * 2): 
        """
        预计算最热门的图书列表，存储在实例中，减少重复计算。
        热门定义：总交互值最高的图书。
        """
        logging.info(f"Precalculating top {n} popular books.")
        if self.interactions_df is None or self.interactions_df.empty:
            logging.warning("No interactions data available to precalculate popular books. Returning empty list.")
            self.popular_books_list = []
            return
        
        popular_items_df = self.interactions_df.groupby('item_id')['normalized_interaction'].sum().reset_index()
        popular_items_df = popular_items_df.sort_values(by='normalized_interaction', ascending=False)
        
        logging.info(f"Debug: popular_items_df head:\n{popular_items_df.head(10)}") 
        logging.info(f"Debug: popular_items_df describe:\n{popular_items_df['normalized_interaction'].describe()}") 

        popular_items_top_n = popular_items_df.head(n)

        precalculated_list = []
        if self.books_df is not None and not self.books_df.empty:
            books_df_str_id = self.books_df.set_index('book_id', drop=False)
            for _, row in popular_items_top_n.iterrows():
                item_id = row['item_id']
                score = row['normalized_interaction'] 
                
                logging.info(f"Debug: Precalc Popular Book: {item_id}, Raw Pop Score (sum of normalized interactions): {score:.4f}")

                if item_id in books_df_str_id.index:
                    book_info = books_df_str_id.loc[item_id]
                    precalculated_list.append({
                        'book_id': item_id,
                        'title': book_info['title'],
                        'score': float(score), 
                        'raw_cf_score': 0.0, 
                        'raw_popularity_score': float(score) 
                    })
                else:
                    logging.warning(f"Popular book ID {item_id} not found in books_df during precalculation. Using default info.")
                    precalculated_list.append({
                        'book_id': item_id,
                        'title': 'N/A',
                        'score': float(score),
                        'raw_cf_score': 0.0,
                        'raw_popularity_score': float(score)
                    })
        self.popular_books_list = precalculated_list

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
                    logging.info(f"Stored {len(recommendations_list)} recommendations for user {user_id}")
                else:
                    logging.info(f"No recommendations generated for user {user_id} after all strategies.")
            except Exception as e:
                logging.error(f"Error generating or storing recommendations for user {user_id}: {e}")
                logging.error(traceback.format_exc())

        logging.info("Recommendation generation completed for all users.")
