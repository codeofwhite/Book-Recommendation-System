'''
不接入 redis 测试 deep and wide 模型的训练和推荐功能
'''
'''
清华源 pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
'''
import json
import pandas as pd
import numpy as np
import logging
import math
from scipy.sparse import csr_matrix
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchmetrics import Accuracy
from torchmetrics.classification import BinaryAUROC
import intel_extension_for_pytorch as ipex

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# 设置设备：优先使用GPU
DEVICE = torch.device('xpu' if torch.xpu.is_available() else 'cpu')
logging.info(f"Using device: {DEVICE}")

# ===================== 配置参数（替代Config类）=====================
class Config:
    # 推荐配置
    TOP_N_RECOMMENDATIONS = 5
    FALLBACK_TO_POPULAR_IF_LESS_THAN_N_CF_RECS = True
    
    # Deep & Wide模型配置 (PyTorch)
    EMBEDDING_DIM = 128  # 简化维度，加快测试
    DEEP_HIDDEN_UNITS = [128, 64, 32, 16]  # 简化网络
    BATCH_SIZE = 32
    EPOCHS = 30  # 少量epoch用于测试
    LEARNING_RATE = 0.001
    MODEL_SAVE_PATH = "deep_wide_model_pytorch.pt"  # 简化路径，方便测试

# ===================== Deep & Wide 模型定义 =====================
class DeepWideModel(nn.Module):
    def __init__(self, wide_feature_dim, deep_embedding_dims, deep_hidden_units):
        super(DeepWideModel, self).__init__()
        
        # Wide部分：线性层（逻辑回归）- 修复：增加隐藏层避免维度爆炸
        self.wide_layers = nn.Sequential(
            nn.Linear(wide_feature_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
        # Deep部分 - Embedding层（处理类别特征）
        self.embedding_layers = nn.ModuleDict()
        for feat_name, (vocab_size, embed_dim) in deep_embedding_dims.items():
            self.embedding_layers[feat_name] = nn.Embedding(
                num_embeddings=vocab_size + 1,  # +1 for unknown
                embedding_dim=embed_dim,
                padding_idx=None
            )
            # 初始化embedding权重
            nn.init.normal_(self.embedding_layers[feat_name].weight, mean=0, std=0.01)
        
        # Deep部分 - 全连接层
        # 计算Deep部分输入维度：所有embedding维度之和 + 数值特征维度
        total_embed_dim = sum([dim for _, dim in deep_embedding_dims.values()])
        deep_input_dim = total_embed_dim + 1  # +1 for numerical feature (age)
        
        self.deep_layers = nn.Sequential()
        in_dim = deep_input_dim
        for i, units in enumerate(deep_hidden_units):
            self.deep_layers.add_module(f'dense_{i}', nn.Linear(in_dim, units))
            self.deep_layers.add_module(f'relu_{i}', nn.ReLU())
            self.deep_layers.add_module(f'bn_{i}', nn.BatchNorm1d(units))
            self.deep_layers.add_module(f'dropout_{i}', nn.Dropout(0.2))
            in_dim = units
        
        # Deep部分输出层
        self.deep_output = nn.Linear(in_dim, 1)
        
        # 最终融合层
        self.final_linear = nn.Linear(2, 1)  # wide_out + deep_out
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, wide_input, deep_categorical_inputs, deep_numerical_inputs):
        # Wide部分前向传播
        wide_out = self.wide_layers(wide_input)  # [batch_size, 1]
        
        # Deep部分前向传播
        deep_embeds = []
        for feat_name, embed_layer in self.embedding_layers.items():
            # 获取该特征的输入 [batch_size]
            feat_input = deep_categorical_inputs[feat_name]
            # Embedding查找 [batch_size, embed_dim]
            embed_out = embed_layer(feat_input)
            deep_embeds.append(embed_out)
        
        # 拼接所有Embedding和数值特征
        deep_embed_concat = torch.cat(deep_embeds, dim=1)
        deep_concat = torch.cat([deep_embed_concat, deep_numerical_inputs], dim=1)
        
        # 经过全连接层
        deep_hidden_out = self.deep_layers(deep_concat)
        deep_out = self.deep_output(deep_hidden_out)  # [batch_size, 1]
        
        # 融合Wide和Deep输出
        concat_out = torch.cat([wide_out, deep_out], dim=1)  # [batch_size, 2]
        final_out = self.final_linear(concat_out)
        final_out = self.sigmoid(final_out)  # [batch_size, 1]
        
        return final_out

# ===================== 自定义数据集 =====================
class RecommendationDataset(Dataset):
    def __init__(self, wide_input, deep_categorical_inputs, deep_numerical_inputs, labels=None):
        self.wide_input = wide_input
        self.deep_categorical_inputs = deep_categorical_inputs
        self.deep_numerical_inputs = deep_numerical_inputs
        self.labels = labels
    
    def __len__(self):
        return len(self.wide_input)
    
    def __getitem__(self, idx):
        sample = {
            'wide_input': self.wide_input[idx],
            'deep_categorical_inputs': {k: v[idx] for k, v in self.deep_categorical_inputs.items()},
            'deep_numerical_inputs': self.deep_numerical_inputs[idx]
        }
        if self.labels is not None:
            sample['label'] = self.labels[idx]
        return sample

# ===================== 推荐训练器 =====================
class RecommendationTrainer:
    def __init__(self):
        # 数据存储
        self.users_df = None
        self.books_df = None
        self.interactions_df = None
        
        # 特征编码器（改为实例变量，保存拟合结果）
        self.user_le = LabelEncoder()
        self.item_le = LabelEncoder()
        self.author_le = LabelEncoder()
        self.genre_le = LabelEncoder()
        self.cross_le = LabelEncoder()
        self.age_scaler = MinMaxScaler()  # 新增：年龄归一化
        self.interaction_scaler = MinMaxScaler()
        
        # 模型相关
        self.model = None
        self.feature_columns = {}
        self.popular_books_list = []
        
        # 配置参数
        self.EMBEDDING_DIM = Config.EMBEDDING_DIM
        self.DEEP_HIDDEN_UNITS = Config.DEEP_HIDDEN_UNITS
        self.BATCH_SIZE = Config.BATCH_SIZE
        self.EPOCHS = Config.EPOCHS
        self.LEARNING_RATE = Config.LEARNING_RATE
        
        # 保存用户年龄信息（用于推荐）
        self.user_age_map = {}
    
    def _generate_sample_data(self):
        """生成增强版模拟数据（解决过拟合，强化偏好特征）"""
        logging.info("Generating enhanced sample data for testing...")
        
        # 1. 生成用户数据
        users_data = {
            'id': ['user_1', 'user_2', 'user_3', 'user_4', 'user_5', 'user_6', 'user_7', 'user_8'],
            'age': [25, 30, 35, 40, 45, 28, 32, 38],
            'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
            'preference': [
                'Classic Fiction',    # user_1：经典小说
                'Romance Fiction',    # user_2：浪漫小说
                'Fantasy/Adventure',  # user_3：奇幻冒险（哈利波特核心用户）
                'Philosophy',         # user_4：哲学
                'Mixed (Classic+Fantasy)',  # user_5：混合（经典+奇幻）
                'Tolkien Works',      # user_6：托尔金专属
                'Austen Romance',     # user_7：奥斯汀浪漫小说
                'Dystopian Fiction'   # user_8：反乌托邦小说
            ]
        }
        self.users_df = pd.DataFrame(users_data)
        self.user_age_map = dict(zip(self.users_df['id'], self.users_df['age']))
        
        # 2. 生成图书数据（强化哈利波特特征）
        books_data = {
            'book_id': [f'book_{i}' for i in range(1, 20)],  # 增加书籍数量
            'title': [
                # 经典小说类
                'The Great Gatsby', '1984', 'To Kill a Mockingbird', 'Brave New World', 'Animal Farm',
                # 浪漫小说类
                'Pride and Prejudice', 'Sense and Sensibility', 'Emma', 'Jane Eyre', 'Wuthering Heights',
                # 奇幻冒险类（强化哈利波特系列）
                'Harry Potter and the Sorcerer\'s Stone', 'Harry Potter and the Chamber of Secrets',
                'Harry Potter and the Prisoner of Azkaban', 'The Hobbit', 'Lord of the Rings: The Fellowship',
                'Lord of the Rings: The Two Towers', 'Lord of the Rings: The Return',
                # 哲学/人生类
                'The Alchemist', 'Man\'s Search for Meaning'
            ],
            'author': [
                # 经典小说作者
                'F. Scott Fitzgerald', 'George Orwell', 'Harper Lee', 'Aldous Huxley', 'George Orwell',
                # 浪漫小说作者
                'Jane Austen', 'Jane Austen', 'Jane Austen', 'Charlotte Brontë', 'Emily Brontë',
                # 奇幻冒险作者（哈利波特统一标注）
                'J.K. Rowling', 'J.K. Rowling', 'J.K. Rowling', 'J.R.R. Tolkien', 'J.R.R. Tolkien',
                'J.R.R. Tolkien', 'J.R.R. Tolkien',
                # 哲学类作者
                'Paulo Coelho', 'Viktor E. Frankl'
            ],
            'genres': [
                # 经典小说标签
                'Fiction,Classic', 'Fiction,Dystopian', 'Fiction,Drama,Classic',
                'Fiction,Dystopian', 'Fiction,Dystopian',
                # 浪漫小说标签
                'Fiction,Romance,Classic', 'Fiction,Romance,Classic', 'Fiction,Romance,Classic',
                'Fiction,Romance,Classic', 'Fiction,Romance,Classic',
                # 奇幻冒险标签（强化哈利波特特征）
                'Fantasy,Adventure,HarryPotter', 'Fantasy,Adventure,HarryPotter', 'Fantasy,Adventure,HarryPotter',
                'Fantasy,Adventure,Tolkien', 'Fantasy,Adventure,Tolkien',
                'Fantasy,Adventure,Tolkien', 'Fantasy,Adventure,Tolkien',
                # 哲学类标签
                'Fiction,Philosophy', 'Non-Fiction,Philosophy'
            ]
        }
        self.books_df = pd.DataFrame(books_data)
        
        # 3. 生成交互数据（增加样本量，强化偏好规律）
        interactions_data = []
        
        # ===== user_1：经典小说偏好（增加样本）=====
        interactions_data.extend([
            {'user_id': 'user_1', 'item_id': 'book_1', 'interaction_value': 5.0},
            {'user_id': 'user_1', 'item_id': 'book_2', 'interaction_value': 4.8},
            {'user_id': 'user_1', 'item_id': 'book_3', 'interaction_value': 4.7},
            {'user_id': 'user_1', 'item_id': 'book_4', 'interaction_value': 4.6},
            {'user_id': 'user_1', 'item_id': 'book_5', 'interaction_value': 4.5},
            {'user_id': 'user_1', 'item_id': 'book_11', 'interaction_value': 2.0},  # 非偏好低分
            {'user_id': 'user_1', 'item_id': 'book_6', 'interaction_value': 1.5},   # 非偏好低分
        ])
        
        # ===== user_2：浪漫小说偏好（增加样本）=====
        interactions_data.extend([
            {'user_id': 'user_2', 'item_id': 'book_6', 'interaction_value': 5.0},
            {'user_id': 'user_2', 'item_id': 'book_7', 'interaction_value': 4.9},
            {'user_id': 'user_2', 'item_id': 'book_8', 'interaction_value': 4.8},
            {'user_id': 'user_2', 'item_id': 'book_9', 'interaction_value': 4.7},
            {'user_id': 'user_2', 'item_id': 'book_10', 'interaction_value': 4.6},
            {'user_id': 'user_2', 'item_id': 'book_2', 'interaction_value': 1.5},   # 非偏好低分
            {'user_id': 'user_2', 'item_id': 'book_11', 'interaction_value': 1.0},  # 非偏好低分
        ])
        
        # ===== user_3：奇幻冒险偏好（哈利波特核心用户，强化偏好）=====
        interactions_data.extend([
            {'user_id': 'user_3', 'item_id': 'book_11', 'interaction_value': 5.0},  # 哈利波特1
            {'user_id': 'user_3', 'item_id': 'book_12', 'interaction_value': 4.9},  # 哈利波特2
            # 看看能不能推荐到 book3。
            # {'user_id': 'user_3', 'item_id': 'book_13', 'interaction_value': 4.8},  # 哈利波特3
            {'user_id': 'user_3', 'item_id': 'book_14', 'interaction_value': 4.7},  # 霍比特人
            {'user_id': 'user_3', 'item_id': 'book_15', 'interaction_value': 4.6},  # 魔戒1
            {'user_id': 'user_3', 'item_id': 'book_16', 'interaction_value': 1.0},  # 非偏好低分
            {'user_id': 'user_3', 'item_id': 'book_6', 'interaction_value': 0.5},   # 非偏好低分
        ])
        
        # ===== 其他用户同理，增加样本量 =====
        # user_4：哲学偏好
        interactions_data.extend([
            {'user_id': 'user_4', 'item_id': 'book_18', 'interaction_value': 5.0},
            {'user_id': 'user_4', 'item_id': 'book_19', 'interaction_value': 4.9},
            {'user_id': 'user_4', 'item_id': 'book_1', 'interaction_value': 2.0},
            {'user_id': 'user_4', 'item_id': 'book_11', 'interaction_value': 1.0},
        ])
        
        # user_5：混合偏好
        interactions_data.extend([
            {'user_id': 'user_5', 'item_id': 'book_1', 'interaction_value': 4.5},
            {'user_id': 'user_5', 'item_id': 'book_2', 'interaction_value': 4.0},
            {'user_id': 'user_5', 'item_id': 'book_11', 'interaction_value': 4.5},
            {'user_id': 'user_5', 'item_id': 'book_12', 'interaction_value': 4.0},
            {'user_id': 'user_5', 'item_id': 'book_6', 'interaction_value': 2.0},
        ])
        
        # user_6：托尔金专属
        interactions_data.extend([
            {'user_id': 'user_6', 'item_id': 'book_14', 'interaction_value': 5.0},
            {'user_id': 'user_6', 'item_id': 'book_15', 'interaction_value': 5.0},
            {'user_id': 'user_6', 'item_id': 'book_16', 'interaction_value': 5.0},
            {'user_id': 'user_6', 'item_id': 'book_17', 'interaction_value': 5.0},
            {'user_id': 'user_6', 'item_id': 'book_11', 'interaction_value': 2.5},
        ])
        
        # user_7：奥斯汀浪漫
        interactions_data.extend([
            {'user_id': 'user_7', 'item_id': 'book_6', 'interaction_value': 5.0},
            {'user_id': 'user_7', 'item_id': 'book_7', 'interaction_value': 5.0},
            {'user_id': 'user_7', 'item_id': 'book_8', 'interaction_value': 5.0},
            {'user_id': 'user_7', 'item_id': 'book_9', 'interaction_value': 2.0},
            {'user_id': 'user_7', 'item_id': 'book_11', 'interaction_value': 1.0},
        ])
        
        # user_8：反乌托邦
        interactions_data.extend([
            # {'user_id': 'user_8', 'item_id': 'book_2', 'interaction_value': 5.0},
            # 先注释掉，看能不能推荐到 book4。
            {'user_id': 'user_8', 'item_id': 'book_4', 'interaction_value': 4.9},
            {'user_id': 'user_8', 'item_id': 'book_5', 'interaction_value': 5}
        ])
        
        interactions_df = pd.DataFrame(interactions_data)
        
        # 调整负采样比例（从3降到2，减少噪声）
        self.interactions_df = self._build_pos_neg_samples(interactions_df, neg_ratio=2)
        
        # 预计算热门图书
        self._precalculate_popular_books()
    
    def load_all_data(self):
        """加载数据（这里使用模拟数据）"""
        self._generate_sample_data()
        return self.interactions_df
    
    def _build_pos_neg_samples(self, interactions_df, neg_ratio=2):
        """构建正负样本：正样本=有交互，负样本=无交互（负采样）"""
        # 正样本
        pos_samples = interactions_df.copy()
        pos_samples['label'] = 1
        
        # 构建用户-物品交互矩阵
        user_item_pairs = set(zip(pos_samples['user_id'], pos_samples['item_id']))
        all_users = pos_samples['user_id'].unique() if not pos_samples.empty else []
        all_items = pos_samples['item_id'].unique() if not pos_samples.empty else []
        
        # 负采样
        neg_samples = []
        for user_id in all_users:
            # 该用户已交互的物品
            interacted_items = pos_samples[pos_samples['user_id'] == user_id]['item_id'].tolist()
            # 未交互的物品
            non_interacted_items = [item for item in all_items if item not in interacted_items]
            # 随机采样负样本
            if len(non_interacted_items) > 0:
                sample_size = min(neg_ratio * len(interacted_items), len(non_interacted_items))
                sampled_neg_items = np.random.choice(non_interacted_items, size=sample_size, replace=False)
                for item_id in sampled_neg_items:
                    neg_samples.append({
                        'user_id': user_id,
                        'item_id': item_id,
                        'interaction_value': 0.0,
                        'label': 0
                    })
        
        neg_samples_df = pd.DataFrame(neg_samples)
        # 合并正负样本
        all_samples = pd.concat([pos_samples, neg_samples_df], ignore_index=True)
        
        # 合并图书特征和用户特征
        all_samples = all_samples.merge(
            self.books_df[['book_id', 'author', 'genres']],
            left_on='item_id',
            right_on='book_id',
            how='left'
        )
        all_samples = all_samples.drop('book_id', axis=1)
        
        # 合并用户年龄特征
        all_samples['age'] = all_samples['user_id'].map(self.user_age_map)
        
        return all_samples
    
    def _preprocess_features(self):
        """特征预处理：编码类别特征，归一化数值特征"""
        df = self.interactions_df.copy()
        
        # 1. 类别特征编码（fit_transform保存映射关系）
        df['user_id_encoded'] = self.user_le.fit_transform(df['user_id'])
        df['item_id_encoded'] = self.item_le.fit_transform(df['item_id'])
        df['author_encoded'] = self.author_le.fit_transform(df['author'].fillna('unknown'))
        
        # 处理多标签的genres（取第一个genre）
        df['main_genre'] = df['genres'].apply(lambda x: x.split(',')[0] if x and x != 'unknown' else 'unknown')
        df['genre_encoded'] = self.genre_le.fit_transform(df['main_genre'])
        
        # 2. 数值特征归一化
        df['interaction_norm'] = self.interaction_scaler.fit_transform(df[['interaction_value']])
        df['age_norm'] = self.age_scaler.fit_transform(df[['age']])  # 年龄归一化
        
        # 3. 构建Wide特征（修复：使用低维特征，避免one-hot爆炸）
        # Wide特征：user_id_encoded + item_id_encoded + genre_encoded (拼接成低维特征)
        df['wide_feature'] = df['user_id_encoded'] * 100 + df['item_id_encoded']
        # 只保留前1000维，避免维度爆炸
        df['wide_feature'] = df['wide_feature'].clip(0, 999)
        
        # 保存特征维度信息
        self.feature_columns = {
            'wide': {
                'dim': 1000  # 固定维度，避免one-hot爆炸
            },
            'deep_categorical': {
                'user_id': (len(self.user_le.classes_), self.EMBEDDING_DIM),
                'item_id': (len(self.item_le.classes_), self.EMBEDDING_DIM),
                'author': (len(self.author_le.classes_), self.EMBEDDING_DIM),
                'genre': (len(self.genre_le.classes_), self.EMBEDDING_DIM)
            },
            'deep_numerical_dim': 1  # 使用年龄作为数值特征（更有意义）
        }
        
        return df
    
    def build_model(self):
        """构建Deep & Wide模型 (PyTorch)"""
        # 获取特征维度
        wide_dim = self.feature_columns['wide']['dim']
        deep_embedding_dims = self.feature_columns['deep_categorical']
        
        # 创建模型
        self.model = DeepWideModel(
            wide_feature_dim=wide_dim,
            deep_embedding_dims=deep_embedding_dims,
            deep_hidden_units=self.DEEP_HIDDEN_UNITS
        ).to(DEVICE)
        
        logging.info("Deep & Wide model (PyTorch) built successfully!")
    
    def train_model(self):
        """训练Deep & Wide模型 (PyTorch)"""
        logging.info("Starting Deep & Wide model training (PyTorch)...")
        
        # 1. 数据加载和预处理
        self.load_all_data()
        if self.interactions_df.empty:
            logging.error("No data to train!")
            return
        
        # 2. 特征预处理
        processed_df = self._preprocess_features()
        
        # 3. 拆分训练集和验证集
        train_df, val_df = train_test_split(processed_df, test_size=0.2, random_state=42)
        
        # 4. 准备模型输入数据
        def prepare_tensor_data(df, is_train=True):
            # Wide输入：one-hot编码低维特征
            wide_input = torch.nn.functional.one_hot(
                torch.tensor(df['wide_feature'].values, dtype=torch.long),
                num_classes=self.feature_columns['wide']['dim']
            ).float()
            
            # Deep类别特征输入
            deep_categorical_inputs = {
                'user_id': torch.tensor(df['user_id_encoded'].values, dtype=torch.long),
                'item_id': torch.tensor(df['item_id_encoded'].values, dtype=torch.long),
                'author': torch.tensor(df['author_encoded'].values, dtype=torch.long),
                'genre': torch.tensor(df['genre_encoded'].values, dtype=torch.long)
            }
            
            # Deep数值特征输入：使用年龄（更有意义）
            deep_numerical_inputs = torch.tensor(df['age_norm'].values, dtype=torch.float32).unsqueeze(1)
            
            if is_train:
                labels = torch.tensor(df['label'].values, dtype=torch.float32).unsqueeze(1)
                return wide_input, deep_categorical_inputs, deep_numerical_inputs, labels
            else:
                return wide_input, deep_categorical_inputs, deep_numerical_inputs
        
        # 准备训练和验证数据
        train_wide, train_deep_cat, train_deep_num, train_labels = prepare_tensor_data(train_df)
        val_wide, val_deep_cat, val_deep_num, val_labels = prepare_tensor_data(val_df)
        
        # 创建数据集和数据加载器
        train_dataset = RecommendationDataset(train_wide, train_deep_cat, train_deep_num, train_labels)
        val_dataset = RecommendationDataset(val_wide, val_deep_cat, val_deep_num, val_labels)
        
        train_loader = DataLoader(train_dataset, batch_size=self.BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.BATCH_SIZE, shuffle=False)
        
        # 5. 构建模型
        self.build_model()
        
        # 6. 定义损失函数和优化器
        criterion = nn.BCELoss()  # 二分类交叉熵损失
        optimizer = optim.Adam(self.model.parameters(), lr=self.LEARNING_RATE)
        
        # ====== 新增：IPEX 优化 ======
        self.model, optimizer = ipex.optimize(self.model, optimizer=optimizer)

        # 定义评估指标
        train_accuracy = Accuracy(task='binary').to(DEVICE)
        val_accuracy = Accuracy(task='binary').to(DEVICE)
        train_auc = BinaryAUROC().to(DEVICE)
        val_auc = BinaryAUROC().to(DEVICE)
        
        # 7. 训练循环
        best_val_auc = 0.0
        for epoch in range(self.EPOCHS):
            # 训练阶段
            self.model.train()
            train_loss = 0.0
            train_accuracy.reset()
            train_auc.reset()
            
            for batch in train_loader:
                # 数据移到设备上
                wide_input = batch['wide_input'].to(DEVICE)
                deep_cat_inputs = {k: v.to(DEVICE) for k, v in batch['deep_categorical_inputs'].items()}
                deep_num_inputs = batch['deep_numerical_inputs'].to(DEVICE)
                labels = batch['label'].to(DEVICE)
                
                # 前向传播
                optimizer.zero_grad()
                outputs = self.model(wide_input, deep_cat_inputs, deep_num_inputs)
                
                # 计算损失
                loss = criterion(outputs, labels)
                
                # 反向传播和优化
                loss.backward()
                optimizer.step()
                
                # 累计损失和更新指标
                train_loss += loss.item() * wide_input.size(0)
                train_accuracy.update(outputs, labels.int())
                train_auc.update(outputs, labels.int())
            
            # 验证阶段
            self.model.eval()
            val_loss = 0.0
            val_accuracy.reset()
            val_auc.reset()
            
            with torch.no_grad():
                for batch in val_loader:
                    wide_input = batch['wide_input'].to(DEVICE)
                    deep_cat_inputs = {k: v.to(DEVICE) for k, v in batch['deep_categorical_inputs'].items()}
                    deep_num_inputs = batch['deep_numerical_inputs'].to(DEVICE)
                    labels = batch['label'].to(DEVICE)
                    
                    outputs = self.model(wide_input, deep_cat_inputs, deep_num_inputs)
                    loss = criterion(outputs, labels)
                    
                    val_loss += loss.item() * wide_input.size(0)
                    val_accuracy.update(outputs, labels.int())
                    val_auc.update(outputs, labels.int())
            
            # 计算平均损失和指标
            train_loss /= len(train_loader.dataset)
            val_loss /= len(val_loader.dataset)
            
            # 打印日志
            logging.info(f"Epoch [{epoch+1}/{self.EPOCHS}]")
            logging.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_accuracy.compute():.4f}, Train AUC: {train_auc.compute():.4f}")
            logging.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy.compute():.4f}, Val AUC: {val_auc.compute():.4f}")
            
            # 保存最佳模型
            current_val_auc = val_auc.compute().item()
            if current_val_auc > best_val_auc:
                best_val_auc = current_val_auc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'best_val_auc': best_val_auc,
                }, Config.MODEL_SAVE_PATH)
                logging.info(f"Saved best model with Val AUC: {best_val_auc:.4f}")
        
        # 加载最佳模型
        checkpoint = torch.load(Config.MODEL_SAVE_PATH, map_location=DEVICE)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        logging.info(f"Loaded best model with Val AUC: {checkpoint['best_val_auc']:.4f}")
        
        return {
            'best_val_auc': best_val_auc,
            'final_train_loss': train_loss,
            'final_val_loss': val_loss
        }
    
    def _safe_transform(self, le, value):
        """安全的LabelEncoder转换，处理未知值"""
        if value in le.classes_:
            return le.transform([value])[0]
        else:
            return len(le.classes_)  # 未知值返回最后一个索引
    
    def get_top_n_recommendations_for_user(self, user_id, n=Config.TOP_N_RECOMMENDATIONS):
        """为用户生成Top-N推荐 (PyTorch版)，输出格式兼容原有Redis格式"""
        logging.info(f"Generating top {n} recommendations for user {user_id}...")
        
        user_id_str = str(user_id)
        # 如果用户不存在，返回热门图书
        if user_id_str not in self.user_le.classes_:
            logging.info(f"User {user_id_str} not found, returning popular books")
            return self._get_popular_books(n)
        
        # 1. 准备待推荐的物品列表（排除已交互的）
        interacted_items = self.interactions_df[
            (self.interactions_df['user_id'] == user_id_str) & 
            (self.interactions_df['label'] == 1)
        ]['item_id'].tolist() if not self.interactions_df.empty else []
        
        all_items = self.books_df['book_id'].unique() if not self.books_df.empty else []
        candidate_items = [item for item in all_items if item not in interacted_items]
        
        if not candidate_items:
            logging.info("No candidate items, returning popular books")
            return self._get_popular_books(n)
        
        # 2. 构建候选物品的特征
        candidate_df = pd.DataFrame({
            'user_id': [user_id_str] * len(candidate_items),
            'item_id': candidate_items,
            'age': [self.user_age_map.get(user_id_str, 30)] * len(candidate_items)  # 用户年龄
        })
        
        # 合并图书特征
        candidate_df = candidate_df.merge(
            self.books_df[['book_id', 'author', 'genres']],
            left_on='item_id',
            right_on='book_id',
            how='left'
        )
        candidate_df = candidate_df.drop('book_id', axis=1)
        
        # 特征编码（使用训练好的Encoder）
        # 用户ID编码
        candidate_df['user_id_encoded'] = self._safe_transform(self.user_le, user_id_str)
        
        # 物品ID编码
        candidate_df['item_id_encoded'] = candidate_df['item_id'].apply(
            lambda x: self._safe_transform(self.item_le, x)
        )
        
        # 作者编码
        candidate_df['author'] = candidate_df['author'].fillna('unknown')
        candidate_df['author_encoded'] = candidate_df['author'].apply(
            lambda x: self._safe_transform(self.author_le, x)
        )
        
        # 类型编码
        candidate_df['main_genre'] = candidate_df['genres'].apply(lambda x: x.split(',')[0] if x and x != 'unknown' else 'unknown')
        candidate_df['genre_encoded'] = candidate_df['main_genre'].apply(
            lambda x: self._safe_transform(self.genre_le, x)
        )
        
        # Wide特征（低维，避免爆炸）
        candidate_df['wide_feature'] = candidate_df['user_id_encoded'] * 100 + candidate_df['item_id_encoded']
        candidate_df['wide_feature'] = candidate_df['wide_feature'].clip(0, 999)
        
        # 数值特征：用户年龄（归一化）
        candidate_df['age_norm'] = self.age_scaler.transform(candidate_df[['age']])
        
        # 3. 准备模型输入
        def prepare_prediction_data(df):
            # Wide输入
            wide_input = torch.nn.functional.one_hot(
                torch.tensor(df['wide_feature'].values, dtype=torch.long),
                num_classes=self.feature_columns['wide']['dim']
            ).float().to(DEVICE)
            
            # Deep类别特征
            deep_categorical_inputs = {
                'user_id': torch.tensor(df['user_id_encoded'].values, dtype=torch.long).to(DEVICE),
                'item_id': torch.tensor(df['item_id_encoded'].values, dtype=torch.long).to(DEVICE),
                'author': torch.tensor(df['author_encoded'].values, dtype=torch.long).to(DEVICE),
                'genre': torch.tensor(df['genre_encoded'].values, dtype=torch.long).to(DEVICE)
            }
            
            # Deep数值特征：用户年龄
            deep_numerical_inputs = torch.tensor(df['age_norm'].values, dtype=torch.float32).unsqueeze(1).to(DEVICE)
            
            return wide_input, deep_categorical_inputs, deep_numerical_inputs
        
        pred_wide, pred_deep_cat, pred_deep_num = prepare_prediction_data(candidate_df)
        
        # 4. 模型预测
        self.model.eval()
        with torch.no_grad():
            predictions = self.model(pred_wide, pred_deep_cat, pred_deep_num)
            predictions = predictions.cpu().numpy().flatten()
        
        # 5. 生成推荐列表（保持原有Redis格式）
        candidate_df['score'] = predictions
        candidate_df = candidate_df.sort_values('score', ascending=False).head(n)
        
        # 合并图书标题
        candidate_df = candidate_df.merge(
            self.books_df[['book_id', 'title']],
            left_on='item_id',
            right_on='book_id',
            how='left'
        )
        
        # 构建最终推荐结果（完全兼容原有Redis格式）
        recommendations = []
        for _, row in candidate_df.iterrows():
            recommendations.append({
                'book_id': row['item_id'],
                'title': row['title'] if pd.notna(row['title']) else 'N/A',
                'score': float(row['score']),
                'raw_cf_score': 0.0,  # 兼容原有格式
                'raw_popularity_score': 0.0
            })
        
        # 打印个性化得分（验证修复效果）
        logging.info(f"\n{user_id_str} 的个性化推荐得分：")
        for rec in recommendations:
            logging.info(f"  {rec['title']}: {rec['score']:.4f}")
        
        # 如果推荐数量不足，补充热门图书
        if len(recommendations) < n:
            logging.info(f"Supplementing with popular books to reach {n} recommendations")
            current_ids = {rec['book_id'] for rec in recommendations}
            popular_books = self._get_popular_books(n - len(recommendations))
            
            for book in popular_books:
                if book['book_id'] not in current_ids:
                    recommendations.append(book)
        
        return recommendations[:n]
    
    def _precalculate_popular_books(self, n=Config.TOP_N_RECOMMENDATIONS * 2):
        """预计算热门图书"""
        if self.interactions_df.empty:
            self.popular_books_list = []
            return
        
        # 按交互次数计算热门
        popular_items = self.interactions_df[self.interactions_df['label']==1].groupby('item_id').size().reset_index(name='count')
        popular_items = popular_items.sort_values('count', ascending=False).head(n)
        
        # 合并图书信息
        popular_items = popular_items.merge(
            self.books_df[['book_id', 'title']],
            left_on='item_id',
            right_on='book_id',
            how='left'
        )
        
        self.popular_books_list = []
        for _, row in popular_items.iterrows():
            self.popular_books_list.append({
                'book_id': row['item_id'],
                'title': row['title'] if pd.notna(row['title']) else 'N/A',
                'score': float(row['count']),
                'raw_cf_score': 0.0,
                'raw_popularity_score': float(row['count'])
            })
    
    def _get_popular_books(self, n=Config.TOP_N_RECOMMENDATIONS):
        """获取热门图书"""
        return self.popular_books_list[:n]
    
    def generate_recommendations(self):
        """为所有用户生成推荐（模拟存储到Redis的逻辑）"""
        logging.info("Generating recommendations for all users...")
        
        if self.users_df is None or self.model is None:
            logging.error("Model not trained or user data missing!")
            return
        
        # 存储所有用户的推荐结果（模拟Redis存储）
        all_recommendations = {}
        
        for user_id in self.users_df['id'].unique():
            try:
                recs = self.get_top_n_recommendations_for_user(user_id)
                all_recommendations[str(user_id)] = recs
                # 打印推荐结果
                logging.info(f"\nRecommendations for user {user_id}:")
                for i, rec in enumerate(recs, 1):
                    logging.info(f"{i}. {rec['title']} (book_id: {rec['book_id']}, score: {rec['score']:.4f})")
            except Exception as e:
                logging.error(f"Error for user {user_id}: {e}")
        
        # 模拟Redis存储：将推荐结果序列化为JSON格式（和原有格式一致）
        logging.info("\n=== All recommendations (JSON format compatible with Redis) ===")
        for user_id, recs in all_recommendations.items():
            json_recs = json.dumps(recs, ensure_ascii=False, indent=2)
            logging.info(f"User {user_id}:\n{json_recs}")
        
        logging.info("Recommendation generation completed!")
        return all_recommendations

# ===================== 测试运行 =====================
if __name__ == "__main__":
    # 设置随机种子，保证结果可复现
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.xpu.is_available():
        torch.xpu.manual_seed(42)
    
    # 创建训练器实例
    trainer = RecommendationTrainer()
    
    # 训练模型
    trainer.train_model()
    
    # 为所有用户生成推荐
    all_recs = trainer.generate_recommendations()
    
    # 单独测试为某个用户生成推荐
    test_user_id = 'user_1'
    test_recs = trainer.get_top_n_recommendations_for_user(test_user_id, n=5)
    logging.info(f"\n=== Final recommendations for {test_user_id} ===")
    logging.info(json.dumps(test_recs, ensure_ascii=False, indent=2))