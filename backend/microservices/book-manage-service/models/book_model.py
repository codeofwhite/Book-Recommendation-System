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
import random
from minio import Minio # 新增导入 Minio 客户端
from minio.error import S3Error # 新增导入 S3Error

# 从config中导入配置
from config import Config

class BookModel:
    _books_collection = None # 私有类变量来存储MongoDB集合对象
    _minio_client = None # 新增私有类变量来存储 MinIO 客户端

    @classmethod
    def get_minio_client(cls):
        """
        获取 MinIO 客户端实例。
        并确保 bucket 存在。
        """
        if cls._minio_client is None:
            try:
                cls._minio_client = Minio(
                    Config.MINIO_ENDPOINT,
                    access_key=Config.MINIO_ACCESS_KEY,
                    secret_key=Config.MINIO_SECRET_KEY,
                    secure=Config.MINIO_SECURE # 根据你的 MinIO 配置设置 HTTPS
                )
                # 检查 bucket 是否存在，如果不存在则创建
                if not cls._minio_client.bucket_exists(Config.MINIO_BUCKET_NAME):
                    cls._minio_client.make_bucket(Config.MINIO_BUCKET_NAME)
                    print(f"{datetime.now()} MinIO bucket '{Config.MINIO_BUCKET_NAME}' created successfully.")
                else:
                    print(f"{datetime.now()} MinIO bucket '{Config.MINIO_BUCKET_NAME}' already exists.")
            except S3Error as e:
                print(f"{datetime.now()} Error connecting to MinIO or creating bucket: {e}")
                cls._minio_client = None
            except Exception as e:
                print(f"{datetime.now()} Unexpected error initializing MinIO client: {e}")
                cls._minio_client = None
        return cls._minio_client

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
                    row['bookId'] = str(row['bookId']) if row.get('bookId') else None
                    row['epubUrl'] = row.get('epubUrl', '') # 确保 epubUrl 字段在导入时存在，即使为空

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
            book_id = str(book_id)
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
            book_ids = [str(bid) for bid in book_ids]
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
                        {"description": {"$regex": keyword, "$options": "i"}},
                        {"isbn": {"$regex": keyword, "$options": "i"}},
                        {"bookId": {"$regex": keyword, "$options": "i"}}
                    ]
                }
            filtered_books = list(collection.find(query, {'_id': 0}))
            return filtered_books, None
        except Exception as e:
            print(f"Error searching local books in MongoDB: {e}")
            return None, "Failed to search books"

    @classmethod
    def create_book(cls, book_data):
        """创建新书籍"""
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            try:
                all_books = list(collection.find({}, {"bookId": 1, "_id": 0}))
                numeric_ids = []
                for book in all_books:
                    try:
                        numeric_ids.append(int(book["bookId"]))
                    except (ValueError, TypeError):
                        continue

                if numeric_ids:
                    next_id = str(max(numeric_ids) + 1)
                else:
                    next_id = "1"
            except Exception:
                next_id = str(int(datetime.now().timestamp()))

            book_data["bookId"] = next_id
            book_data["rating"] = book_data.get("rating", 0.0)
            book_data["numRatings"] = book_data.get("numRatings", 0)
            book_data["createdAt"] = datetime.now().isoformat()
            book_data["epubUrl"] = book_data.get("epubUrl", "") # 确保 create_book 时包含 epubUrl，默认为空

            result = collection.insert_one(book_data)
            if result.inserted_id:
                created_book = collection.find_one({"bookId": next_id}, {'_id': 0})
                return created_book, None
            else:
                return None, "Failed to create book"
        except Exception as e:
            print(f"Error creating book in MongoDB: {e}")
            return None, str(e)

    @classmethod
    def update_book(cls, book_id, update_data):
        """更新书籍信息"""
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            book_id = str(book_id)

            update_data["updatedAt"] = datetime.now().isoformat()

            result = collection.update_one(
                {"bookId": book_id},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return None, "Book not found"

            updated_book = collection.find_one({"bookId": book_id}, {'_id': 0})
            return updated_book, None
        except Exception as e:
            print(f"Error updating book in MongoDB: {e}")
            return None, str(e)

    @classmethod
    def delete_book(cls, book_id):
        """删除书籍"""
        collection = cls.get_collection()
        if collection is None:
            return False, "Database connection failed"
        minio_client = cls.get_minio_client()
        if minio_client is None:
            print(f"{datetime.now()} MinIO client not available, cannot delete associated EPUB file.")
            # return False, "MinIO connection failed, cannot delete associated file" # 生产环境可能需要更严格的错误处理

        try:
            book_id = str(book_id)

            # 在删除数据库记录之前，先获取书籍信息以删除关联的EPUB文件
            book_to_delete, error_fetch = cls.get_book_by_id(book_id)
            if error_fetch:
                # 如果找不到书，返回错误，不尝试删除 MinIO 文件
                return False, error_fetch

            result = collection.delete_one({"bookId": book_id})
            if result.deleted_count == 0:
                return False, "Book not found"

            # 如果数据库记录删除成功，尝试删除关联的EPUB文件
            if book_to_delete and book_to_delete.get('epubUrl') and minio_client:
                # 从 MinIO URL 中解析出对象名称 (filename)
                # 例如：http://minio-endpoint:9000/bucket-name/bookId.epub
                object_name = book_to_delete['epubUrl'].split('/')[-1]
                try:
                    minio_client.remove_object(Config.MINIO_BUCKET_NAME, object_name)
                    print(f"Deleted EPUB file from MinIO: {Config.MINIO_BUCKET_NAME}/{object_name}")
                except S3Error as minio_error:
                    print(f"Error deleting EPUB file from MinIO {Config.MINIO_BUCKET_NAME}/{object_name}: {minio_error}")
                    # 这里可以选择返回错误，或者仅仅记录日志，因为数据库记录已删除

            return True, None
        except Exception as e:
            print(f"Error deleting book from MongoDB: {e}")
            return False, str(e)

    @classmethod
    def get_dashboard_stats(cls):
        """获取仪表板统计数据"""
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            total_books = collection.count_documents({})

            pipeline = [
                {"$match": {"rating": {"$ne": None, "$gt": 0}}},
                {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
            ]
            avg_result = list(collection.aggregate(pipeline))
            avg_rating = round(avg_result[0]["avgRating"], 1) if avg_result else 0.0

            recent_books = list(collection.find(
                {"createdAt": {"$exists": True}},
                {'_id': 0, 'title': 1, 'createdAt': 1, 'bookId': 1}
            ).sort("createdAt", -1).limit(5))

            stats = {
                "totalBooks": total_books,
                "averageRating": avg_rating,
                "totalUsers": 156,
                "totalReviews": 423,
                "recentBooks": recent_books
            }

            return stats, None
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return None, str(e)

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
        初始化 MongoDB 连接和 MinIO 客户端，并导入数据。
        """
        print(f"{datetime.now()} Attempting to initialize MongoDB connection, MinIO client and import data...")
        collection = cls.get_collection()
        minio_client = cls.get_minio_client() # 初始化 MinIO 客户端
        if collection is not None and minio_client is not None:
            print(f"{datetime.now()} MongoDB and MinIO connections established. Checking for data...")
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
            print(f"{datetime.now()} MongoDB or MinIO connection failed at startup. Data import skipped.")
            return False

    @classmethod
    def get_popular_books(cls, limit=4):
        collection = cls.get_collection()
        if collection is None:
            return None, "Database connection failed"
        try:
            books = list(collection.find(
                {"coverImg": {"$ne": None}, "rating": {"$ne": None}, "numRatings": {"$ne": None}},
                {'_id': 0, 'id': 1, 'bookId': 1, 'title': 1, 'author': 1, 'genres': 1, 'coverImg': 1, 'rating': 1, 'numRatings': 1}
            ).sort([
                ('numRatings', -1),
                ('rating', -1)
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
            books = list(collection.find(
                {"coverImg": {"$ne": None}, "publishDate": {"$ne": None}},
                {'_id': 0, 'id': 1, 'bookId': 1, 'title': 1, 'author': 1, 'genres': 1, 'coverImg': 1, 'publishDate': 1}
            ).sort([
                ('publishDate', -1)
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
            books = list(collection.find(
                {"coverImg": {"$ne": None}, "rating": {"$ne": None}, "numRatings": {"$gte": 500}},
                {'_id': 0, 'id': 1, 'bookId': 1, 'title': 1, 'author': 1, 'genres': 1, 'coverImg': 1, 'rating': 1, 'numRatings': 1}
            ).sort([
                ('rating', -1)
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
            popular_books, _ = cls.get_popular_books(limit=limit * 2)
            popular_book_ids = [book.get('bookId') for book in popular_books if book.get('bookId')]

            query = {"coverImg": {"$ne": None}}
            if popular_book_ids:
                query["bookId"] = {"$nin": popular_book_ids}

            pipeline = [
                {"$match": query},
                {"$sample": {"size": limit}},
                {"$project": {
                    '_id': 0, 'bookId': 1, 'title': 1, 'author': 1,
                    'genres': 1, 'coverImg': 1, 'rating': 1
                }}
            ]

            books = list(collection.aggregate(pipeline))

            if not books and popular_books:
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
            today = datetime.now().day

            books_with_cover = list(collection.find({"coverImg": {"$ne": None}}, {'_id': 0, 'bookId': 1, 'title': 1, 'author': 1, 'genres': 1, 'coverImg': 1, 'description': 1, 'rating':1}))

            if books_with_cover:
                random.seed(today)
                selected_book = random.choice(books_with_cover)
                return selected_book, None
            else:
                return None, "No books with cover images found for daily recommendation"
        except Exception as e:
            print(f"Error fetching daily book from MongoDB: {e}")
            return None, "Failed to retrieve daily book"

    # --- MinIO 文件处理方法 ---
    @classmethod
    def upload_epub_to_minio(cls, file, book_id):
        """
        上传 EPUB 文件到 MinIO 并返回公开访问链接。
        参数:
            file (werkzeug.datastructures.FileStorage): 上传的文件对象。
            book_id (str): 书籍的唯一ID，用于命名 MinIO 中的对象。
        返回:
            tuple: (public_url, error_message)
        """
        minio_client = cls.get_minio_client()
        if minio_client is None:
            return None, "MinIO client not initialized. Cannot upload file."

        # 使用 book_id 作为 MinIO 中的对象名称，确保唯一性
        # 如果文件类型不是 .epub，确保添加正确的扩展名
        object_name = f"{book_id}.epub"

        # Flask 的 FileStorage 对象可以直接传递给 MinIO 的 put_object
        try:
            # MinIO 的 put_object 需要文件大小，file.seek(0, os.SEEK_END) 获取大小
            # file.seek(0) 重置文件指针到开头
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0) # 重置文件指针到开头

            minio_client.put_object(
                Config.MINIO_BUCKET_NAME,
                object_name,
                file,
                file_size, # 必须提供文件大小
                content_type="application/epub+zip" # 明确指定 MIME 类型
            )
            print(f"{datetime.now()} Successfully uploaded {object_name} to MinIO bucket {Config.MINIO_BUCKET_NAME}")

            # 生成 MinIO 的公开访问 URL
            # 对于 MinIO，通常是 http://<MinIO_ENDPOINT>/<bucket_name>/<object_name>
            # 在 Docker Compose 环境中，MinIO_ENDPOINT 是 `minio:9000`
            # 但前端需要通过 Docker 宿主机的 IP 或配置好的域名来访问
            # 这里我们返回的 URL 应该是前端可直接访问的，所以用 host:port
            # 如果是本地开发，MinIO 通常在 localhost:9000
            # 如果在部署到服务器后，minio 服务会暴露在宿主机的 9000 端口
            # 那么前端访问地址会是 http://your_server_ip:9000/epub-books/bookId.epub
            # 更好的做法是在配置中定义一个 PUBLIC_MINIO_ENDPOINT
            public_minio_endpoint = os.getenv('PUBLIC_MINIO_ENDPOINT', f"http://{Config.MINIO_ENDPOINT}")
            # 如果 Config.MINIO_SECURE 为 True，则应为 https
            if Config.MINIO_SECURE:
                 public_minio_endpoint = public_minio_endpoint.replace("http://", "https://")

            # 确保端口正确暴露在宿主机上，例如 9000 端口
            # 假设你希望前端通过宿主机的 9000 端口访问 MinIO
            minio_host_port = Config.MINIO_ENDPOINT.split(':')[0] + ":" + str(9002) # 假设MinIO的外部端口总是9000
            
            # 使用 PUBLIC_MINIO_ENDPOINT 来构造前端可访问的链接
            # 注意：这里需要根据实际部署环境来决定 MinIO 的可访问地址
            # 如果你的前端和后端都在同一个 Docker 网络中，那么前端直接用 http://minio:9000 就行
            # 但通常前端是浏览器，它需要访问宿主机暴露出来的端口
            # 最简单的处理是：后端返回一个相对路径或者一个简化的路径，前端自己拼接 MinIO 基础 URL
            # 或者后端直接返回一个带有 MinIO 宿主机端口的完整 URL

            # 为了简化，我们假设前端可以直接访问 MinIO 的公开端口 (9000)
            # 在 docker-compose 中，MinIO 端口映射为 "9000:9000"，所以外部访问也是 9000
            minio_base_url = f"{'https' if Config.MINIO_SECURE else 'http'}://{Config.MONGO_HOST if Config.MONGO_HOST != 'mongodb' else 'localhost'}:9002" # 适配本地和 docker-compose
            # 实际部署时，你可能需要用服务器的公共 IP 或域名替换 localhost
            public_url = f"{minio_base_url}/{Config.MINIO_BUCKET_NAME}/{object_name}"


            # 更好的方案：在Config中增加一个 PUBLIC_MINIO_BASE_URL
            # public_url = f"{Config.PUBLIC_MINIO_BASE_URL}/{Config.MINIO_BUCKET_NAME}/{object_name}"
            # 然后在 .env 或 Config 中设置 PUBLIC_MINIO_BASE_URL=http://localhost:9000 (本地) 或 http://your_domain:9000 (生产)

            return public_url, None
        except S3Error as e:
            print(f"{datetime.now()} MinIO S3Error during upload for {object_name}: {e}")
            return None, f"MinIO S3 error: {str(e)}"
        except Exception as e:
            print(f"{datetime.now()} Error during MinIO upload for {object_name}: {e}")
            return None, f"Failed to upload EPUB to MinIO: {str(e)}"