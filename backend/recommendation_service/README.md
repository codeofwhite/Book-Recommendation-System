# 准实时同步测试服务，主要用于查看同步是否顺利
Spark structrued streaming: 通过这种方式，recommendation_db 中的 rec_user_profiles 和 rec_books 表能够保持最新，为后续的离线特征工程和模型训练提供新鲜的数据基础。