# 实时推荐逻辑

## 准实时同步
Spark structrued streaming: 通过这种方式，recommendation_db 中的 rec_user_profiles 和 rec_books 表能够保持最新，为后续的离线特征工程和模型训练提供新鲜的数据基础。

## 实时推荐