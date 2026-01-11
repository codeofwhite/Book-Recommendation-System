import json
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np 
import logging
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer 
import math
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler

from data.data_loader import DataLoader
from utils.redis_utils import RedisClient
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
np.seterr(divide='ignore', invalid='ignore')
DEVICE = torch.device('cpu')
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

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

        self.wide_deep_model = None
        self.inter_scaler = MinMaxScaler(feature_range=(0,1))
        self.model_trained = False

    class LightWideDeep(nn.Module):
        def __init__(self, user_count, item_count, embed_dim=8):
            super().__init__()
            self.wide_linear = nn.Linear(3, 1, bias=True)
            self.wide_bn = nn.BatchNorm1d(3)

            self.user_emb = nn.Embedding(user_count, embed_dim)
            self.item_emb = nn.Embedding(item_count, embed_dim)
            nn.init.normal_(self.user_emb.weight, mean=0.0, std=0.01)
            nn.init.normal_(self.item_emb.weight, mean=0.0, std=0.01)

            self.deep_net = nn.Sequential(
                nn.Linear(embed_dim*2, 16),
                nn.ReLU(),
                nn.Dropout(0.15),
                nn.Linear(16, 8),
                nn.ReLU(),
                nn.Dropout(0.15),
                nn.Linear(8, 1)
            )

            self.wide_weight = nn.Parameter(torch.tensor([0.5]), requires_grad=True)
            self.deep_weight = nn.Parameter(torch.tensor([0.5]), requires_grad=True)
            self.sigmoid = nn.Sigmoid()

        def forward(self, wide_x, user_idx, item_idx):
            wide_out = self.wide_bn(wide_x)
            wide_out = self.wide_linear(wide_out)
            u_emb = self.user_emb(user_idx)
            i_emb = self.item_emb(item_idx)
            deep_in = torch.cat([u_emb, i_emb], dim=1)
            deep_out = self.deep_net(deep_in)
            fuse = self.wide_weight * wide_out + self.deep_weight * deep_out
            return self.sigmoid(fuse).squeeze()

    def get_book_feature_vector_from_redis(self, book_id: str):
        key = f"{Config.REDIS_BOOK_FEATURES_PREFIX}{book_id}"
        json_bytes = self.redis_client.get(key)
        if json_bytes:
            try:
                return json.loads(json_bytes.decode('utf-8'))
            except Exception as e:
                logging.error(f"Failed to decode JSON feature vector for book_id {book_id}: {e}", exc_info=True)
                return None
        return None

    def store_item_feature_vectors(self):
        logging.info("Storing item feature vectors to Redis...")
        if self.content_matrix is None or self.books_df.empty:
            logging.warning("Content matrix or books_df is missing. Cannot store item feature vectors.")
            return

        pipe = self.redis_client.get_pipeline() 
        for i, item_id_idx in enumerate(self.idx_to_item):
            item_id = self.idx_to_item[item_id_idx]
            if i < self.content_matrix.shape[0]:
                feature_vector_list = self.content_matrix[i].toarray().flatten().tolist() 
                key = f"{Config.REDIS_BOOK_FEATURES_PREFIX}{item_id}"
                pipe.set(key, json.dumps(feature_vector_list, ensure_ascii=False).encode('utf-8')) 
            else:
                logging.warning(f"Index {i} out of bounds for content_matrix (shape {self.content_matrix.shape}). Skipping item {item_id}.")
        pipe.execute()
        logging.info(f"Stored {len(self.idx_to_item)} item feature vectors to Redis.")

    def load_all_data(self):
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
                all_interactions['normalized_interaction'] = 1.0 
            
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
        logging.info("Creating user-item matrix...")
        if self.interactions_df.empty:
            logging.warning("Interactions DataFrame is empty. Cannot create user-item matrix.")
            final_user_ids = list(self.users_df['id'].astype(str).unique()) if self.users_df is not None else []
            final_item_ids = list(self.books_df['book_id'].astype(str).unique()) if self.books_df is not None else []
            
            self.user_to_idx = {user: i for i, user in enumerate(final_user_ids)}
            self.idx_to_user = {i: user for user, i in self.user_to_idx.items()}
            self.item_to_idx = {item: i for i, item in enumerate(final_item_ids)}
            self.idx_to_item = {i: item for item, i in self.item_to_idx.items()}
            
            self.user_item_matrix = csr_matrix((len(self.user_to_idx), len(self.item_to_idx))) 
            logging.warning(f"Created empty user-item matrix with shape: {self.user_item_matrix.shape}")
            return

        self.interactions_df['user_id'] = self.interactions_df['user_id'].astype(str)
        self.interactions_df['item_id'] = self.interactions_df['item_id'].astype(str)

        all_user_ids = list(self.users_df['id'].astype(str).unique()) if self.users_df is not None else []
        all_item_ids = list(self.books_df['book_id'].astype(str).unique()) if self.books_df is not None else []

        final_user_ids = list(set(all_user_ids).union(set(self.interactions_df['user_id'].unique())))
        final_item_ids = list(set(all_item_ids).union(set(self.interactions_df['item_id'].unique())))
        
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
        logging.info("Calculating item similarities...")
        logging.info("Calculating Item-Item Collaborative Filtering similarity...")
        if self.user_item_matrix is None or self.user_item_matrix.shape[1] == 0:
            logging.warning("User-item matrix is not available or has no items for CF similarity.")
            self.item_cf_similarity_matrix = None
        else:
            item_user_matrix = self.user_item_matrix.T.tocsr()
            self.item_cf_similarity_matrix = cosine_similarity(item_user_matrix)
            logging.info(f"Item CF similarity matrix calculated with shape: {self.item_cf_similarity_matrix.shape}")
            logging.info(f"Item CF similarity matrix: Min={np.min(self.item_cf_similarity_matrix):.4f}, Max={np.max(self.item_cf_similarity_matrix):.4f}, Mean={np.mean(self.item_cf_similarity_matrix):.4f}")

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

            self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', min_df=1) 
            self.content_matrix = self.tfidf_vectorizer.fit_transform(ordered_content_features) 
            self.item_content_similarity_matrix = cosine_similarity(self.content_matrix)
            logging.info(f"Item Content similarity matrix calculated with shape: {self.item_content_similarity_matrix.shape}")
            logging.info(f"Item Content similarity matrix: Min={np.min(self.item_content_similarity_matrix):.4f}, Max={np.max(self.item_content_similarity_matrix):.4f}, Mean={np.mean(self.item_content_similarity_matrix):.4f}")

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
        logging.info("Calculating user profiles...")
        if self.user_item_matrix is None or self.content_matrix is None or not self.idx_to_user or not self.idx_to_item:
            logging.warning("User-item matrix, content matrix, or index mappings are missing. Cannot calculate user profiles.")
            return

        pipe = self.redis_client.get_pipeline()
        feature_dim = self.content_matrix.shape[1]
        
        for user_id_idx in range(len(self.idx_to_user)):
            user_id = self.idx_to_user[user_id_idx]
            user_interactions_sparse = self.user_item_matrix[user_id_idx, :]
            interacted_item_indices = user_interactions_sparse.nonzero()[0] 
            
            if not interacted_item_indices.size: 
                logging.info(f"User {user_id} has no interactions, skipping profile calculation.")
                continue

            user_item_scores = user_interactions_sparse.toarray().flatten()[interacted_item_indices]
            user_profile_vector = [0.0] * feature_dim
            total_weight = 0.0

            for i, item_idx in enumerate(interacted_item_indices):
                item_id = self.idx_to_item[item_idx]
                weight = user_item_scores[i]
                # 权重小于0的话强制赋值0.1，杜绝负权重
                if weight < 0.1:
                    weight = 0.1
                # 索引越界/无特征时，用全0向量，不中断累加
                if item_idx < self.content_matrix.shape[0]:
                    book_feature_vector = self.content_matrix[item_idx].toarray().flatten().tolist()
                else:
                    book_feature_vector = [0.0] * feature_dim
                
                # 累加特征和权重
                user_profile_vector = [x + y * weight for x, y in zip(user_profile_vector, book_feature_vector)]
                total_weight += weight
            
            if total_weight <= 1e-8:
                # 权重总和为0时，强制赋值 交互书籍数量*0.1，绝对不会再触发警告
                total_weight = len(interacted_item_indices) * 0.1
                logging.info(f"User {user_id} total_weight is zero, force set to {total_weight:.4f}")
            
            # 归一化用户画像
            user_profile_vector = [x / total_weight for x in user_profile_vector]
            norm = math.sqrt(sum(x**2 for x in user_profile_vector))
            if norm > 0:
                user_profile_vector = [x / norm for x in user_profile_vector]
            
            key = f"{Config.REDIS_USER_PROFILE_PREFIX}{user_id}"
            pipe.set(key, json.dumps(user_profile_vector, ensure_ascii=False).encode('utf-8')) 
            logging.info(f"Stored user profile for user {user_id}, total_weight={total_weight:.4f}")
                
        pipe.execute()
        logging.info(f"Stored user profiles for {len(self.idx_to_user)} users to Redis.")

    def _negative_sampling(self):
        logging.info("Wide&Deep: Doing negative sampling (small data optimized)...")
        pos_data = self.interactions_df[['user_idx', 'item_idx', 'normalized_interaction']].dropna().values
        if len(pos_data) == 0:
            return pos_data
        
        neg_samples = []
        item_count = len(self.item_to_idx)
        for user_idx, item_idx, inter_val in pos_data:
            user_idx = int(user_idx)
            interacted_items = set(self.user_item_matrix[user_idx].indices)
            neg_count = 0
            while neg_count <5:
                candidate = np.random.randint(0, item_count)
                if candidate not in interacted_items and candidate != item_idx:
                    neg_samples.append([user_idx, candidate, 0.0])
                    neg_count +=1
        neg_data = np.array(neg_samples)
        train_data = np.vstack([pos_data, neg_data])
        logging.info(f"Wide&Deep: Positive samples: {len(pos_data)}, Negative samples: {len(neg_data)}, Total train samples: {len(train_data)}")
        return train_data

    def _train_wide_deep(self):
        logging.info("Wide&Deep: Starting light model training (cpu single thread)...")
        if self.interactions_df.empty:
            return
        
        user_count = len(self.user_to_idx)
        item_count = len(self.item_to_idx)
        self.wide_deep_model = self.LightWideDeep(user_count, item_count).to(DEVICE)
        
        train_data = self._negative_sampling()
        user_idx = train_data[:, 0].astype(np.int64)
        item_idx = train_data[:, 1].astype(np.int64)
        inter_vals = train_data[:, 2].reshape(-1, 1)
        norm_inter_vals = self.inter_scaler.fit_transform(inter_vals).flatten()

        wide_x = np.column_stack([user_idx, item_idx, norm_inter_vals]).astype(np.float32)
        labels = np.where(train_data[:, 2] > 0.0, 1.0, 0.0)

        wide_x_tensor = torch.FloatTensor(wide_x).to(DEVICE)
        user_idx_tensor = torch.LongTensor(user_idx).to(DEVICE)
        item_idx_tensor = torch.LongTensor(item_idx).to(DEVICE)
        label_tensor = torch.FloatTensor(labels).to(DEVICE)

        optimizer = optim.Adam(self.wide_deep_model.parameters(), lr=0.001, weight_decay=1e-5)
        loss_fn = nn.BCELoss()
        epochs = 60
        batch_size = 16

        self.wide_deep_model.train()
        total_samples = len(wide_x_tensor)
        for epoch in range(epochs):
            total_loss = 0.0
            permutation = torch.randperm(total_samples)
            for i in range(0, total_samples, batch_size):
                idx = permutation[i:i+batch_size]
                w_x = wide_x_tensor[idx]
                u_idx = user_idx_tensor[idx]
                i_idx = item_idx_tensor[idx]
                y = label_tensor[idx]

                optimizer.zero_grad()
                pred = self.wide_deep_model(w_x, u_idx, i_idx)
                loss = loss_fn(pred, y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * len(idx)
            
            avg_loss = total_loss / total_samples
            if (epoch+1) %5 ==0:
                logging.info(f"Wide&Deep: Epoch [{epoch+1}/{epochs}], Avg Loss: {avg_loss * 10:.6f}")
        
        self.wide_deep_model.eval()
        self.model_trained = True
        logging.info("Wide&Deep model training completed!")

    def train_model(self):
        logging.info("Starting model training process...")
        
        self.load_all_data()
        self.create_user_item_matrix() 
        self.calculate_item_similarity()

        if self.item_similarity_matrix is None:
            logging.warning("No item similarity matrix could be calculated after all attempts. Model training might be incomplete.")
            return
        
        self.store_item_feature_vectors() 
        self.calculate_user_profiles()

        if not self.interactions_df.empty:
            self._train_wide_deep()

        logging.info("All training completed")

    def get_top_n_recommendations_for_user(self, user_id, n=Config.TOP_N_RECOMMENDATIONS, 
                                           cf_weight=Config.CF_POPULARITY_MIX_ALPHA, 
                                           similarity_weight=Config.SIMILARITY_FUSION_ALPHA): 
        logging.info(f"Generating top {n} recommendations for user {user_id} (CF+Content+Wide&Deep 三模融合)...")
        user_id_str = str(user_id)
        
        user_idx = self.user_to_idx.get(user_id_str)
        popular_books_n = self._get_popular_books(n)
        
        if user_idx is None: 
            logging.info(f"User {user_id_str} not found. Returning popular books.")
            return popular_books_n
        
        user_interactions_sparse = self.user_item_matrix[user_idx, :]
        user_interactions_dense = user_interactions_sparse.toarray().flatten()
        interacted_item_indices = user_interactions_dense.nonzero()[0]
        
        if len(interacted_item_indices) == 0:
            logging.info(f"User {user_id_str} has no valid interactions. Returning popular books.")
            return popular_books_n
        
        if self.item_similarity_matrix is None:
            logging.warning("Item similarity matrix is missing. Returning popular books.")
            return popular_books_n

        logging.info(f"User {user_id_str} (idx: {user_idx}) has {len(interacted_item_indices)} non-zero interactions in matrix.")
        if user_id_str == '7': 
            for idx in interacted_item_indices:
                item_id = self.idx_to_item[idx]
                interaction_value = user_interactions_dense[idx]
                logging.info(f"  - User {user_id_str} interacted with item {item_id} (idx: {idx}) with normalized_interaction: {interaction_value:.4f}")

        predicted_scores = user_interactions_dense.reshape(1, -1).dot(self.item_similarity_matrix).flatten()
        min_pred_score = float(predicted_scores.min())
        max_pred_score = float(predicted_scores.max())
        
        # 防止max-min=0导致除零
        if max_pred_score - min_pred_score > 1e-8:
            normalized_pred_scores = (predicted_scores - min_pred_score) / (max_pred_score - min_pred_score + 1e-6) 
        else:
            normalized_pred_scores = np.full_like(predicted_scores, 0.8) 

        logging.info(f"User {user_id_str} CF+Content scores: Min={float(normalized_pred_scores.min()):.4f}, Max={float(normalized_pred_scores.max()):.4f}")

        popular_scores = np.zeros(len(self.idx_to_item))
        if self.popular_books_list:
            pop_values = [book['raw_popularity_score'] for book in self.popular_books_list if 'raw_popularity_score' in book and book['raw_popularity_score'] is not None]
            min_pop_score = min(pop_values) if pop_values else 0
            max_pop_score = max(pop_values) if pop_values else 0
            norm_factor = max_pop_score - min_pop_score + 1e-6 if max_pop_score > min_pop_score else 1.0 

            for book in self.popular_books_list:
                item_id = book['book_id']
                if item_id in self.item_to_idx:
                    idx = self.item_to_idx[item_id]
                    raw_pop_score_val = book.get('raw_popularity_score', 0.0)
                    popular_scores[idx] = (raw_pop_score_val - min_pop_score) / norm_factor if norm_factor > 0 else 0.0 

        wd_model_scores = np.zeros(len(self.idx_to_item))
        if self.model_trained and self.wide_deep_model is not None:
            all_item_indices = np.arange(len(self.idx_to_item))
            user_idx_batch = np.full_like(all_item_indices, user_idx, dtype=np.int64)
            inter_val_batch = np.zeros_like(all_item_indices, dtype=np.float32)
            norm_inter_batch = self.inter_scaler.transform(inter_val_batch.reshape(-1,1)).flatten()
            wide_x_batch = np.column_stack([user_idx_batch, all_item_indices, norm_inter_batch]).astype(np.float32)
            
            with torch.no_grad():
                wide_x_tensor = torch.FloatTensor(wide_x_batch).to(DEVICE)
                user_idx_tensor = torch.LongTensor(user_idx_batch).to(DEVICE)
                item_idx_tensor = torch.LongTensor(all_item_indices).to(DEVICE)
                wd_model_scores = self.wide_deep_model(wide_x_tensor, user_idx_tensor, item_idx_tensor).cpu().numpy()
            
            # 模型分安全归一化
            if wd_model_scores.max() - wd_model_scores.min() > 1e-8:
                wd_model_scores = (wd_model_scores - wd_model_scores.min()) / (wd_model_scores.max() - wd_model_scores.min() + 1e-6)
            else:
                wd_model_scores = np.full_like(wd_model_scores, 0.7)
            logging.info(f"User {user_id_str} Wide&Deep scores: Min={float(wd_model_scores.min()):.4f}, Max={float(wd_model_scores.max()):.4f}")

        CF_CONTENT_WEIGHT = 0.5
        WIDE_DEEP_WEIGHT = 0.4
        POPULAR_WEIGHT = 0.1
        mixed_scores = (CF_CONTENT_WEIGHT * normalized_pred_scores) + \
                       (WIDE_DEEP_WEIGHT * wd_model_scores) + \
                       (POPULAR_WEIGHT * popular_scores)

        mixed_scores[interacted_item_indices] = -np.inf
        mixed_scores = np.nan_to_num(mixed_scores, nan=-np.inf, posinf=-np.inf, neginf=-np.inf)
        recommended_item_indices = np.argsort(mixed_scores)[::-1]
        
        final_top_n_item_indices = []
        for idx in recommended_item_indices:
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
            current_wd_score = float(wd_model_scores[idx])
            
            if item_id in books_df_str_id.index:
                book_info = books_df_str_id.loc[item_id]
                final_recommendations.append({
                    'book_id': item_id,
                    'title': str(book_info['title']),
                    'score': float(mixed_scores[idx]),
                    'raw_cf_score': current_raw_cf_score, 
                    'raw_popularity_score': current_raw_popularity_score,
                    'raw_wd_score': current_wd_score
                })
            else:
                logging.warning(f"Book ID {item_id} not found in books_df. Using default info.")
                final_recommendations.append({
                    'book_id': item_id, 
                    'title': 'N/A', 
                    'score': float(mixed_scores[idx]),
                    'raw_cf_score': current_raw_cf_score,
                    'raw_popularity_score': current_raw_popularity_score,
                    'raw_wd_score': current_wd_score
                })
        
        if len(final_recommendations) < n and Config.FALLBACK_TO_POPULAR_IF_LESS_THAN_N_CF_RECS:
            logging.info(f"User {user_id_str} generated {len(final_recommendations)} recommendations. Supplementing with popular books.")
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
                        'raw_popularity_score': popular_book.get('raw_popularity_score', 0.0),
                        'raw_wd_score': 0.0
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
                    logging.warning(f"Popular book ID {item_id} not found in books_df. Using default info.")
                    precalculated_list.append({
                        'book_id': item_id,
                        'title': 'N/A',
                        'score': float(score),
                        'raw_cf_score': 0.0,
                        'raw_popularity_score': float(score)
                    })
        self.popular_books_list = precalculated_list

    def _get_popular_books(self, n=Config.TOP_N_RECOMMENDATIONS):
        logging.info(f"Returning top {n} popular books as fallback recommendation.")
        if not self.popular_books_list:
            logging.warning("Popular books list is empty. Cannot provide fallback recommendations.")
            return []
        
        return self.popular_books_list[:n]

    def generate_recommendations(self):
        logging.info("Starting recommendation generation for all users (CF+Content+Wide&Deep)...")
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

        logging.info("Recommendation generation completed for all users")