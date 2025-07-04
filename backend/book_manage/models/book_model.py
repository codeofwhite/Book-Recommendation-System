# models/book_model.py
import os
import csv
import json
import re
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import requests
from bs4 import BeautifulSoup
import random # 新增导入 random 模块

# 从config中导入配置
from config import Config

class BookModel:
    _books_collection = None # 私有类变量来存储MongoDB集合对象

    @classmethod
    def get_collection(cls):
        """
        获取 MongoDB 的 'books' 集合。
        返回:
            - 成功: 返回 Collection 对象
            - 失败: 返回 None
        """
        if cls._books_collection is not None:
            try:
                # 验证连接是否仍然有效
                cls._books_collection.database.client.admin.command('ping')
                return cls._books_collection
            except Exception as e:
                print(f"{datetime.now()} Existing MongoDB connection invalid: {e}. Attempting to reconnect.")
                cls._books_collection = None # 重置连接

        try:
            connection_uri = (
                f"mongodb://{Config.MONGO_USER}:{Config.MONGO_PASSWORD}@"
                f"{Config.MONGO_HOST}:{Config.MONGO_PORT}/{Config.MONGO_DB_NAME}"
                f"?authSource=admin&authMechanism=SCRAM-SHA-256"
                f"&connectTimeoutMS=5000&socketTimeoutMS=5000"
                f"&serverSelectionTimeoutMS=5000"
            )

            client = MongoClient(
                connection_uri,
                retryWrites=True,
                retryReads=True
            )

            client.admin.command('ping')

            db = client[Config.MONGO_DB_NAME]
            cls._books_collection = db.books

            if 'books' not in db.list_collection_names():
                db.create_collection('books')

            print(f"{datetime.now()} Successfully connected to MongoDB!")
            return cls._books_collection

        except Exception as e:
            print(f"{datetime.now()} Could not connect to MongoDB. Error: {str(e)}")
            print(f"Connection URI used: mongodb://{Config.MONGO_USER}:*****@{Config.MONGO_HOST}:{Config.MONGO_PORT}/{Config.MONGO_DB_NAME}?authSource=admin")
            return None

    @classmethod
    def import_books_from_csv(cls, csv_filepath=Config.CSV_FILEPATH):
        """
        从 CSV 文件读取书籍数据并导入到 MongoDB。
        这个函数只在数据库为空时运行一次。
        """
        collection = cls.get_collection()
        if collection is None:
            print(f"{datetime.now()} Failed to get MongoDB collection, cannot import data.")
            return False

        if collection.count_documents({}) > 0:
            print(f"{datetime.now()} MongoDB 'books' collection already contains data. Skipping CSV import.")
            return True

        print(f"{datetime.now()} MongoDB 'books' collection is empty. Importing data from {csv_filepath}...")

        if not os.path.exists(csv_filepath):
            print(f"{datetime.now()} Error: CSV file not found at {csv_filepath}. Please ensure '{os.path.basename(csv_filepath)}' is in the correct directory.")
            return False

        books_to_insert = []
        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    # 转换字符串表示的列表为实际列表，并处理可能的数值类型
                    row['genres'] = eval(row['genres']) if row['genres'] else []
                    row['characters'] = eval(row['characters']) if row['characters'] else []
                    row['awards'] = eval(row['awards']) if row['awards'] else []
                    row['ratingsByStars'] = eval(row['ratingsByStars']) if row['ratingsByStars'] else []
                    row['setting'] = eval(row['setting']) if row['setting'] else []
                    row['rating'] = float(row['rating']) if row.get('rating') else None
                    row['pages'] = int(row['pages']) if row.get('pages') else None
                    row['numRatings'] = int(row['numRatings']) if row.get('numRatings') else None
                    row['likedPercent'] = float(row['likedPercent']) if row.get('likedPercent') else None
                    row['bbeScore'] = int(row['bbeScore']) if row.get('bbeScore') else None
                    row['bbeVotes'] = int(row['bbeVotes']) if row.get('bbeVotes') else None
                    row['price'] = float(row['price']) if row.get('price') else None
                except Exception as e:
                    print(f"{datetime.now()} Warning: Could not parse row data for bookId {row.get('bookId')}: {e}. Skipping row.")
                    continue
                books_to_insert.append(row)

        if books_to_insert:
            try:
                result = collection.insert_many(books_to_insert)
                imported_count = len(result.inserted_ids)
                print(f"{datetime.now()} Successfully imported {imported_count} books into MongoDB.")
                return True
            except Exception as e:
                print(f"{datetime.now()} Error during bulk insert to MongoDB: {e}")
                return False
        else:
            print(f"{datetime.now()} No books to insert from CSV.")
            return True

    @classmethod
    def get_all_books(cls):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            books = list(collection.find({}, {'_id': 0}))
            return books, None
        except Exception as e:
            print(f"Error fetching books from MongoDB: {e}")
            return None, "Failed to retrieve books"

    @classmethod
    def get_book_by_id(cls, book_id):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            book = collection.find_one({"bookId": book_id}, {'_id': 0})
            return book, None
        except Exception as e:
            print(f"Error fetching single book from MongoDB: {e}")
            return None, "Failed to retrieve book"

    @classmethod
    def get_books_by_ids(cls, book_ids):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            books = list(collection.find({"bookId": {"$in": book_ids}}, {'_id': 0}))
            return books, None
        except Exception as e:
            print(f"Error fetching books in batch from MongoDB: {e}")
            return None, "Failed to retrieve books in batch"

    @classmethod
    def search_local_books(cls, keyword):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            query = {}
            if keyword:
                query = {
                    "$or": [
                        {"title": {"$regex": keyword, "$options": "i"}},
                        {"author": {"$regex": keyword, "$options": "i"}},
                        {"description": {"$regex": keyword, "$options": "i"}}
                    ]
                }
            filtered_books = list(collection.find(query, {'_id': 0}))
            return filtered_books, None
        except Exception as e:
            print(f"Error searching local books in MongoDB: {e}")
            return None, "Failed to search books"

    @staticmethod
    def search_douban_books(keyword):
        search_url = f"https://search.douban.com/book/subject_search?search_text={keyword}&cat=1001"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q;q=0.6',
            'Referer': 'https://www.douban.com/'
        }

        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"请求豆瓣失败：{e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = None
        for script in soup.find_all('script', type='text/javascript'):
            if '__DATA__' in str(script):
                script_tag = script
                break
        if not script_tag:
            print("未找到包含书籍数据的script标签。豆瓣页面结构可能已更改。")
            return []

        match = re.search(r'window\.__DATA__\s*=\s*({.*?});', script_tag.string, re.DOTALL)
        if not match:
            print("未能从script标签中解析出JSON数据。")
            return []

        json_data_str = match.group(1)
        try:
            data = json.loads(json_data_str)
            book_items_data = [item for item in data.get('items', []) if item.get('tpl_name') == 'search_subject']
        except json.JSONDecodeError as e:
            print(f"JSON数据解析失败：{e}")
            return []

        books_results = []
        for item_data in book_items_data:
            title = item_data.get('title')
            link = item_data.get('url')
            if title and link:
                books_results.append({'title': title, 'link': link})
        return books_results

    @classmethod
    def initialize_db_and_data(cls):
        """
        初始化 MongoDB 连接并导入数据
        """
        print(f"{datetime.now()} Attempting to initialize MongoDB connection and import data...")
        collection = cls.get_collection()
        if collection is not None:
            print(f"{datetime.now()} MongoDB connection established. Checking for data...")
            try:
                if collection.count_documents({}) == 0:
                    print(f"{datetime.now()} Importing data from CSV...")
                    cls.import_books_from_csv()
                else:
                    print(f"{datetime.now()} MongoDB already contains data. Skipping import.")
                return True
            except Exception as e:
                print(f"{datetime.now()} Error checking collection: {e}")
                return False
        else:
            print(f"{datetime.now()} MongoDB connection failed at startup. Data import skipped.")
            return False

    # --- 新增用于首页推荐和榜单的方法 ---

    @classmethod
    def get_popular_books(cls, limit=4):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            # 热门书籍：基于 'rating' 和 'numRatings' 综合排序，且有封面图
            # 聚合管道实现更复杂的排序，例如 (rating * numRatings) 作为一个指标
            # 或者简单地按 numRatings 降序，rating 降序
            books = list(collection.find(
                {"coverImg": {"$ne": None}, "rating": {"$ne": None}, "numRatings": {"$ne": None}},
                {'_id': 0, 'id': 1, 'bookId': 1, 'title': 1, 'author': 1, 'genres': 1, 'coverImg': 1, 'rating': 1, 'numRatings': 1}
            ).sort([
                ('numRatings', -1), # 首先按评分人数降序
                ('rating', -1)      # 然后按平均评分降序
            ]).limit(limit))
            return books, None
        except Exception as e:
            print(f"Error fetching popular books from MongoDB: {e}")
            return None, "Failed to retrieve popular books"

    @classmethod
    def get_new_books(cls, limit=5):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            # 新书榜：基于 'publishDate' 降序，且有封面图
            # 需要处理 publishDate 字段的格式，如果存储为字符串，需要排序时注意
            # 最佳实践是将其存储为 ISODate 类型
            books = list(collection.find(
                {"coverImg": {"$ne": None}, "publishDate": {"$ne": None}},
                {'_id': 0, 'id': 1, 'bookId': 1, 'title': 1, 'author': 1, 'genres': 1, 'coverImg': 1, 'publishDate': 1}
            ).sort([
                ('publishDate', -1) # 按出版日期降序
            ]).limit(limit))
            return books, None
        except Exception as e:
            print(f"Error fetching new books from MongoDB: {e}")
            return None, "Failed to retrieve new books"

    @classmethod
    def get_top_rated_books(cls, limit=5):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            # 高分榜：基于 'rating' 降序，且有封面图和足够的评分人数
            # 可以设置一个最低评分人数门槛，避免只有少数人高评导致不准确
            books = list(collection.find(
                {"coverImg": {"$ne": None}, "rating": {"$ne": None}, "numRatings": {"$gte": 500}}, # 假设至少有500人评分
                {'_id': 0, 'id': 1, 'bookId': 1, 'title': 1, 'author': 1, 'genres': 1, 'coverImg': 1, 'rating': 1, 'numRatings': 1}
            ).sort([
                ('rating', -1) # 按平均评分降序
            ]).limit(limit))
            return books, None
        except Exception as e:
            print(f"Error fetching top rated books from MongoDB: {e}")
            return None, "Failed to retrieve top rated books"

    @classmethod
    def get_personalized_books(cls, user_id=None, limit=4):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            # 这是一个简单的个性化推荐占位符
            # 在没有用户行为数据的情况下，可以随机选择一些非热门书籍
            # 或者根据用户喜爱的 genres 进行简单的筛选
            
            # 首先获取一些热门书籍的ID，以便排除它们，让个性化推荐看起来“不同”
            popular_books, _ = cls.get_popular_books(limit=limit * 2) # 获取多一点，确保随机选择时有足够选择
            popular_book_ids = [book.get('id') for book in popular_books if book.get('id')]

            # 随机从所有有封面且ID不在热门列表中的书籍中选择
            # 实际应用中，这里应该加入用户偏好、历史阅读等复杂逻辑
            query = {"coverImg": {"$ne": None}}
            if popular_book_ids:
                query["id"] = {"$nin": popular_book_ids} # 排除热门书籍

            # 使用 aggregate 管道进行随机采样，更适合大数据量
            pipeline = [
                {"$match": query},
                {"$sample": {"size": limit}}, # 随机采样指定数量
                {"$project": {
                    '_id': 0, 'id': 1, 'bookId': 1, 'title': 1, 'author': 1,
                    'genres': 1, 'coverImg': 1, 'rating': 1
                }}
            ]
            
            books = list(collection.aggregate(pipeline))
            
            if not books and popular_books: # 如果排除热门后没找到，就从热门里随机选
                books = random.sample(popular_books, min(limit, len(popular_books)))
                
            return books, None
        except Exception as e:
            print(f"Error fetching personalized books from MongoDB: {e}")
            return None, "Failed to retrieve personalized books"

    @classmethod
    def get_daily_book(cls):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            # 每日一书：可以每天随机选择一本，或者实现更复杂的逻辑
            # 使用日期作为随机种子，确保一天内多次请求返回同一本书
            today = datetime.now().day
            
            # 确保书籍有封面图
            books_with_cover = list(collection.find({"coverImg": {"$ne": None}}, {'_id': 0, 'id': 1, 'bookId': 1, 'title': 1, 'author': 1, 'genres': 1, 'coverImg': 1, 'description': 1, 'rating':1}))
            
            if books_with_cover:
                random.seed(today) # 使用当天的日期作为随机种子
                selected_book = random.choice(books_with_cover)
                return selected_book, None
            else:
                return None, "No books with cover images found for daily recommendation"
        except Exception as e:
            print(f"Error fetching daily book from MongoDB: {e}")
            return None, "Failed to retrieve daily book"