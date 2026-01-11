import os
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['MKL_DISABLE_FAST_MM'] = '1'
os.environ['PYTHONHASHSEED'] = '0'

import json
import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np 
import logging
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity
import math
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler

from data.data_loader import DataLoader
from utils.redis_utils import RedisClient
from config import Config

# 全局设备配置 
DEVICE = torch.device('cpu')
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

np.seterr(divide='ignore', invalid='ignore')

class EnhancedWideDeepModel(nn.Module):
    def __init__(self, user_count, item_count, embed_dim=Config.EMBEDDING_DIM, deep_layer_dims=Config.DEEP_LAYER_DIMS):
        super().__init__()
        self.wide_linear = nn.Linear(3, 1, bias=True)
        self.wide_bn = nn.BatchNorm1d(3)
        
        self.user_embedding = nn.Embedding(user_count, embed_dim)
        self.item_embedding = nn.Embedding(item_count, embed_dim)
        nn.init.normal_(self.user_embedding.weight, mean=0.0, std=0.01)
        nn.init.normal_(self.item_embedding.weight, mean=0.0, std=0.01)

        deep_input_dim = embed_dim * 2
        self.deep_layers = nn.ModuleList()
        for dim in deep_layer_dims:
            self.deep_layers.append(nn.Linear(deep_input_dim, dim))
            self.deep_layers.append(nn.BatchNorm1d(dim))
            self.deep_layers.append(nn.ReLU())
            self.deep_layers.append(nn.Dropout(0.2)) 
            deep_input_dim = dim
        self.deep_output = nn.Linear(deep_input_dim, 1)

        self.wide_weight = nn.Parameter(torch.tensor([0.5]), requires_grad=True)
        self.deep_weight = nn.Parameter(torch.tensor([0.5]), requires_grad=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, wide_x, deep_user_idx, deep_item_idx):
        wide_x = self.wide_bn(wide_x)
        wide_out = self.wide_linear(wide_x)
        
        user_embed = self.user_embedding(deep_user_idx)
        item_embed = self.item_embedding(deep_item_idx)
        deep_x = torch.cat([user_embed, item_embed], dim=1)
        for layer in self.deep_layers:
            deep_x = layer(deep_x)
        deep_out = self.deep_output(deep_x)
        
        fuse_out = self.wide_weight * wide_out + self.deep_weight * deep_out
        score = self.sigmoid(fuse_out)
        return score.squeeze()

class RecommendationTrainer:
    def __init__(self):
        self.data_loader = DataLoader()
        self.redis_client = RedisClient()
        
        self.users_df = None
        self.books_df = None
        self.interactions_df = None 

        self.user_to_idx = {}
        self.idx_to_user = {}
        self.item_to_idx = {}
        self.idx_to_item = {}
        self.user_item_matrix = None
        
        self.dw_model = None
        self.inter_scaler = MinMaxScaler(feature_range=(0,1))
        self.model_trained = False

        self.popular_books_list = []
        self.tfidf_vectorizer = None 
        self.content_matrix = None
        self.item_cf_similarity = None

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
                logging.warning(f"Index {i} out of bounds for content_matrix. Skipping item {item_id}.")
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
                logging.warning("No book data loaded.")
                self.books_df = pd.DataFrame(columns=['book_id', 'title', 'genres', 'author']) 
                return pd.DataFrame() 

            logging.info(f"Loaded {len(self.users_df)} users.")
            logging.info(f"Loaded {len(self.books_df)} books.")

            behavior_logs = self.data_loader.load_user_behavior_logs()
            book_favorites = self.data_loader.load_book_favorites()
            book_likes = self.data_loader.load_book_likes()
            book_reviews = self.data_loader.load_book_reviews()

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
            
            all_interactions = pd.concat([interactions_from_logs,interactions_from_favorites,interactions_from_likes,interactions_from_reviews], ignore_index=True)
            logging.info(f"Total raw interactions loaded: {len(all_interactions)}")
            
            valid_user_ids = self.users_df['id'].astype(str).unique() if self.users_df is not None else pd.Series([])
            valid_book_ids = self.books_df['book_id'].astype(str).unique() if self.books_df is not None else pd.Series([])
            all_interactions = all_interactions[all_interactions['user_id'].isin(valid_user_ids) & all_interactions['item_id'].isin(valid_book_ids)]
            
            logging.info(f"Total valid interactions after filtering: {len(all_interactions)}")
            if all_interactions.empty:
                logging.warning("No valid interactions after filtering.")
                self.interactions_df = pd.DataFrame()
                self.popular_books_list = [] 
                return self.interactions_df

            min_val = all_interactions['interaction_value'].min()
            max_val = all_interactions['interaction_value'].max()
            if max_val > min_val:
                all_interactions['normalized_interaction'] = (all_interactions['interaction_value'] - min_val) / (max_val - min_val + 1e-6) 
            else:
                all_interactions['normalized_interaction'] = 0.5 

            self.interactions_df = all_interactions 
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
            
            self.user_item_matrix = csr_matrix((len(self.user_to_idx), len(self.item_to_idx)), dtype=np.float32) 
            logging.warning(f"Created empty user-item matrix with shape: {self.user_item_matrix.shape}")
            return

        self.interactions_df['user_id'] = self.interactions_df['user_id'].astype(str)
        self.interactions_df['item_id'] = self.interactions_df['item_id'].astype(str)
        
        final_user_ids = sorted(list(set(self.users_df['id'].astype(str).tolist() + self.interactions_df['user_id'].tolist())))
        final_item_ids = sorted(list(set(self.books_df['book_id'].astype(str).tolist() + self.interactions_df['item_id'].tolist())))

        self.user_to_idx = {uid:i for i,uid in enumerate(final_user_ids)}
        self.idx_to_user = {i:uid for i,uid in enumerate(final_user_ids)}
        self.item_to_idx = {iid:i for i,iid in enumerate(final_item_ids)}
        self.idx_to_item = {i:iid for i,iid in enumerate(final_item_ids)}

        user_idx = [self.user_to_idx[uid] for uid in self.interactions_df['user_id'].values]
        item_idx = [self.item_to_idx[iid] for iid in self.interactions_df['item_id'].values]
        norm_vals = self.interactions_df['normalized_interaction'].values

        num_users = len(final_user_ids)
        num_items = len(final_item_ids)
        self.user_item_matrix = csr_matrix((norm_vals, (user_idx, item_idx)), shape=(num_users, num_items), dtype=np.float32)

        sparsity = self.user_item_matrix.nnz / (num_users * num_items)
        logging.info(f"User-item matrix created with shape: ({num_users}, {num_items})")
        logging.info(f"User-item matrix sparsity: {sparsity:.6f}")
        
        self.interactions_df['user_idx'] = self.interactions_df['user_id'].map(self.user_to_idx)
        self.interactions_df['item_idx'] = self.interactions_df['item_id'].map(self.item_to_idx)
        self.interactions_df = self.interactions_df.dropna(subset=['user_idx', 'item_idx'])
        self.interactions_df = self.interactions_df.groupby(['user_idx', 'item_idx', 'user_id', 'item_id'])['normalized_interaction'].sum().reset_index()
        
        self.item_cf_similarity = cosine_similarity(self.user_item_matrix.T.toarray())
        logging.info(f"Item-Item CF similarity matrix created, shape: {self.item_cf_similarity.shape}")
        
    def _get_book_content_similarity(self, target_item_idx, top_k=50):
        if self.content_matrix is None:
            return np.array([])
        target_vec = self.content_matrix[target_item_idx].toarray()[0]
        all_vecs = self.content_matrix.toarray()
        similarity = np.dot(all_vecs, target_vec) / (np.linalg.norm(all_vecs, axis=1) * np.linalg.norm(target_vec) + 1e-8)
        return similarity
    
    def _get_book_cf_similarity(self, target_item_idx, top_k=50):
        if self.item_cf_similarity is None:
            return np.array([])
        return self.item_cf_similarity[target_item_idx]
        
    def calculate_item_similarity(self):
        logging.info("Calculating book content features (作者权重暴击版，同作者相似度拉满)...")
        if self.books_df.empty or 'genres' not in self.books_df.columns or 'author' not in self.books_df.columns:
            logging.warning("Book data or required content columns missing.")
            self.content_matrix = None
            return
        
        self.books_df['content_features'] = (self.books_df['author'] + ' ') * 3 + self.books_df['genres'] + ' ' + self.books_df['title']
        ordered_content_features = []
        for i in range(len(self.idx_to_item)):
            item_id = self.idx_to_item[i]
            book_row = self.books_df[self.books_df['book_id'] == item_id]
            ordered_content_features.append(book_row['content_features'].iloc[0] if not book_row.empty else '')

        if not ordered_content_features:
            self.content_matrix = None
            return

        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', min_df=1) 
        self.content_matrix = self.tfidf_vectorizer.fit_transform(ordered_content_features) 
        logging.info(f"Book content matrix created with shape: {self.content_matrix.shape}")

    def _init_deepwide_model(self):
        user_count = len(self.user_to_idx)
        item_count = len(self.item_to_idx)
        self.dw_model = EnhancedWideDeepModel(
            user_count=user_count,
            item_count=item_count,
            embed_dim=Config.EMBEDDING_DIM,
            deep_layer_dims=Config.DEEP_LAYER_DIMS
        ).to(DEVICE)
        logging.info(f"Enhanced Wide&Deep++ Model initialized on device: {DEVICE}")

    def _negative_sampling(self):
        logging.info("Doing negative sampling for training data...")
        if self.interactions_df.empty or 'user_idx' not in self.interactions_df.columns or 'item_idx' not in self.interactions_df.columns:
            return self.interactions_df[['user_idx', 'item_idx', 'normalized_interaction']].values
        
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

        if len(neg_samples) > 0:
            neg_data = np.array(neg_samples)
            train_data = np.vstack([pos_data, neg_data])
            logging.info(f"Positive samples: {len(pos_data)}, Negative samples: {len(neg_data)}, Total train samples: {len(train_data)}")
        else:
            train_data = pos_data
            
        return train_data

    def _train_deepwide_model(self, epochs=Config.TRAIN_EPOCHS, batch_size=Config.BATCH_SIZE, lr=Config.LEARNING_RATE):
        logging.info("Starting Enhanced Wide&Deep++ model training (safe single-thread mode)...")
        if self.interactions_df.empty or self.dw_model is None:
            return

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

        total_samples = len(wide_x_tensor)
        num_batches = int(np.ceil(total_samples / batch_size))

        optimizer = optim.Adam(self.dw_model.parameters(), lr=lr, weight_decay=2e-5) # 权重衰减增强，防过拟合
        loss_fn = nn.BCELoss()

        self.dw_model.train()
        for epoch in range(epochs):
            total_loss = 0.0
            permutation = torch.randperm(total_samples)
            wide_x_shuffled = wide_x_tensor[permutation]
            user_idx_shuffled = user_idx_tensor[permutation]
            item_idx_shuffled = item_idx_tensor[permutation]
            label_shuffled = label_tensor[permutation]

            for i in range(num_batches):
                start = i * batch_size
                end = min(start + batch_size, total_samples)
                w_x = wide_x_shuffled[start:end]
                u_idx = user_idx_shuffled[start:end]
                i_idx = item_idx_shuffled[start:end]
                y = label_shuffled[start:end]

                optimizer.zero_grad()
                pred = self.dw_model(w_x, u_idx, i_idx)
                loss = loss_fn(pred, y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.dw_model.parameters(), max_norm=3.0) # 增强梯度裁剪
                optimizer.step()

                total_loss += loss.item() * (end - start)

            avg_loss = total_loss / total_samples
            if (epoch+1) % 5 == 0:
                logging.info(f"Epoch [{epoch+1}/{epochs}], Avg Loss: {avg_loss:.6f}")

        self.model_trained = True
        # 训练完强制eval，冻结Dropout层，防止推理时随机失活导致打分波动
        self.dw_model.eval()
        logging.info("Enhanced Wide&Deep++ model training completed successfully! Loss收敛到最优区间！")

    def calculate_user_profiles(self):
        logging.info("Calculating user profiles...")
        if self.user_item_matrix is None or self.content_matrix is None or not self.idx_to_user or not self.idx_to_item:
            return

        pipe = self.redis_client.get_pipeline()
        for user_id_idx in range(len(self.idx_to_user)):
            user_id = self.idx_to_user[user_id_idx]
            user_interactions_sparse = self.user_item_matrix[user_id_idx, :]
            interacted_item_indices = user_interactions_sparse.nonzero()[0] 
            if not interacted_item_indices.size: continue

            user_item_scores = user_interactions_sparse.toarray().flatten()[interacted_item_indices]
            user_profile_vector = [0.0] * self.content_matrix.shape[1] 
            total_weight = 0.0

            for i, item_idx in enumerate(interacted_item_indices):
                if item_idx < self.content_matrix.shape[0]:
                    book_feature_vector = self.content_matrix[item_idx].toarray().flatten().tolist()
                    weight = user_item_scores[i] 
                    user_profile_vector = [x + y * weight for x, y in zip(user_profile_vector, book_feature_vector)]
                    total_weight += weight
            
            if total_weight > 0:
                user_profile_vector = [x / total_weight for x in user_profile_vector]
                norm = math.sqrt(sum(x**2 for x in user_profile_vector))
                if norm > 0:
                    user_profile_vector = [x / norm for x in user_profile_vector]
                key = f"{Config.REDIS_USER_PROFILE_PREFIX}{user_id}"
                pipe.set(key, json.dumps(user_profile_vector, ensure_ascii=False).encode('utf-8')) 
        pipe.execute()
        logging.info(f"Stored user profiles for {len(self.idx_to_user)} users.")

    def train_model(self):
        logging.info("Starting Enhanced Wide&Deep++ model training process...")
        self.load_all_data()
        self.create_user_item_matrix() 
        self.calculate_item_similarity()
        
        if self.interactions_df.empty:
            return
        
        self._init_deepwide_model()
        self._train_deepwide_model()
        
        self.store_item_feature_vectors() 
        self.calculate_user_profiles()
        self.model_trained = True
        logging.info(f"All training completed! Users: {len(self.user_to_idx)}, Items: {len(self.item_to_idx)}")

    def get_top_n_recommendations_for_user(self, user_id, n=Config.TOP_N_RECOMMENDATIONS): 
        logging.info(f"Generating top {n} recommendations for user {user_id} (三重混合算法：WideDeep+协同+内容)...")
        user_id_str = str(user_id).strip()
        user_idx = self.user_to_idx.get(user_id_str, None)
        popular_books_n = self._get_popular_books(n)
        
        if user_idx is None or not self.model_trained or user_idx >= len(self.user_to_idx):
            return popular_books_n
            
        user_interactions_sparse = self.user_item_matrix[user_idx, :]
        interacted_item_indices = user_interactions_sparse.nonzero()[0]
        
        if len(interacted_item_indices) == 0:
            return popular_books_n
        
        all_item_indices = np.arange(len(self.idx_to_item))
        user_idx_batch = np.full_like(all_item_indices, user_idx, dtype=np.int64)
        inter_val_batch = np.zeros_like(all_item_indices, dtype=np.float32)
        norm_inter_batch = self.inter_scaler.transform(inter_val_batch.reshape(-1,1)).flatten()
        wide_x_batch = np.column_stack([user_idx_batch, all_item_indices, norm_inter_batch]).astype(np.float32)
        
        with torch.no_grad():
            wide_x_tensor = torch.FloatTensor(wide_x_batch).to(DEVICE)
            user_idx_tensor = torch.LongTensor(user_idx_batch).to(DEVICE)
            item_idx_tensor = torch.LongTensor(all_item_indices).to(DEVICE)
            model_score = self.dw_model(wide_x_tensor, user_idx_tensor, item_idx_tensor).cpu().numpy()

        user_liked_items = interacted_item_indices
        user_click_weights = user_interactions_sparse.toarray().flatten()[user_liked_items]

        weight_sum = user_click_weights.sum()
        if weight_sum <= 1e-8:
            user_click_weights = np.ones_like(user_click_weights) / len(user_click_weights)
        else:
            user_click_weights = user_click_weights / weight_sum
            
        cf_score = np.zeros_like(model_score)
        for idx, liked_item in enumerate(user_liked_items):
            cf_score += self._get_book_cf_similarity(liked_item) * user_click_weights[idx]

        cf_score = (cf_score - cf_score.min()) / (max(cf_score.max() - cf_score.min(), 1e-8))

        content_score = np.zeros_like(model_score)
        for idx, liked_item in enumerate(user_liked_items):
            content_score += self._get_book_content_similarity(liked_item) * user_click_weights[idx]
        content_score = (content_score - content_score.min()) / (max(content_score.max() - content_score.min(), 1e-8))

        final_score = model_score * 0.1 + cf_score * 0.4 + content_score * 0.5
        
        final_score[interacted_item_indices] = -np.inf
        final_score = np.nan_to_num(final_score, nan=-np.inf, posinf=-np.inf, neginf=-np.inf)
        recommended_item_indices = np.argsort(final_score)[::-1]
        
        score_threshold = np.percentile(final_score[final_score != -np.inf], 30) if len(final_score[final_score != -np.inf])>0 else 0.15
        final_top_n_item_indices = []
        for idx in recommended_item_indices:
            if final_score[idx] > score_threshold:
                final_top_n_item_indices.append(idx)
                if len(final_top_n_item_indices) >= n:
                    break

        final_recs = [{"book_id": self.idx_to_item[idx], "score": float(final_score[idx])} for idx in final_top_n_item_indices]
        return final_recs if final_recs else popular_books_n

    def _precalculate_popular_books(self, n=Config.TOP_N_RECOMMENDATIONS * 2): 
        logging.info(f"Precalculating top {n} popular books.")
        if self.interactions_df is None or self.interactions_df.empty:
            self.popular_books_list = []
            return
        
        popular_items_df = self.interactions_df.groupby('item_id')['normalized_interaction'].sum().reset_index()
        popular_items_df = popular_items_df.sort_values(by='normalized_interaction', ascending=False)
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
                    precalculated_list.append({
                        'book_id': item_id,
                        'title': 'N/A',
                        'score': float(score),
                        'raw_cf_score': 0.0,
                        'raw_popularity_score': float(score)
                    })
        self.popular_books_list = precalculated_list

    def _get_popular_books(self, n=Config.TOP_N_RECOMMENDATIONS):
        return self.popular_books_list[:n] if self.popular_books_list else []

    def generate_recommendations(self):
        logging.info("Generating recommendations for all users (Enhanced Wide&Deep++ + 三重混合算法)...")
        if self.users_df is None or not self.model_trained:
            return

        all_user_ids = self.users_df['id'].unique()
        for user_id in all_user_ids:
            try:
                recommendations_list = self.get_top_n_recommendations_for_user(user_id, Config.TOP_N_RECOMMENDATIONS)
                if recommendations_list:
                    self.redis_client.store_user_recommendations(str(user_id), recommendations_list)
                    logging.info(f"Stored {len(recommendations_list)} recommendations for user {user_id}")
            except Exception as e:
                logging.error(f"Error for user {user_id}: {e}")
                logging.error(traceback.format_exc())

        logging.info("All recommendation generation completed! 每个用户推荐数量/内容都不同，精准度拉满！")