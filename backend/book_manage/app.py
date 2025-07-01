from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import re
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import csv # 导入 csv 模块
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- MongoDB 配置 ---
MONGO_HOST = os.getenv('MONGO_HOST', 'book_db_mongo')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_USER = os.getenv('MONGO_USER', 'book_user')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'book_password')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'book_manage_db')

# 全局变量来存储 MongoDB 集合对象，避免每次请求都重新连接
books_collection = None

def get_mongo_collection():
    """
    获取 MongoDB 的 'books' 集合。
    返回: 
        - 成功: 返回 Collection 对象
        - 失败: 返回 None
    """
    global books_collection
    
    # 如果已连接且连接仍然有效，直接返回
    if books_collection is not None:
        try:
            # 验证连接是否仍然有效
            books_collection.database.client.admin.command('ping')
            return books_collection
        except:
            # 如果连接失效，重置并尝试重新连接
            books_collection = None

    try:
        # 使用更健壮的连接配置
        connection_uri = (
            f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@"
            f"{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}"
            f"?authSource=admin&authMechanism=SCRAM-SHA-256"
            f"&connectTimeoutMS=5000&socketTimeoutMS=5000"
            f"&serverSelectionTimeoutMS=5000"
        )
        
        client = MongoClient(
            connection_uri,
            # 添加重试配置
            retryWrites=True,
            retryReads=True
        )
        
        # 验证连接
        client.admin.command('ping')
        
        # 获取数据库和集合
        db = client[MONGO_DB_NAME]
        books_collection = db.books
        
        # 确保集合存在（如果不存在会自动创建）
        if 'books' not in db.list_collection_names():
            db.create_collection('books')
        
        print(f"{datetime.now()} Successfully connected to MongoDB!")
        return books_collection
        
    except Exception as e:
        print(f"{datetime.now()} Could not connect to MongoDB. Error: {str(e)}")
        print(f"Connection URI used: mongodb://{MONGO_USER}:*****@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}?authSource=admin")
        return None
    
def import_books_from_csv(csv_filepath="books.csv"):
    """
    从 CSV 文件读取书籍数据并导入到 MongoDB。
    这个函数只在数据库为空时运行一次。
    """
    collection = get_mongo_collection()
    if collection is None:
        print(f"{datetime.now()} Failed to get MongoDB collection, cannot import data.")
        return False

    # 检查集合是否已经有数据，如果已经有数据则不进行导入
    if collection.count_documents({}) > 0:
        print(f"{datetime.now()} MongoDB 'books' collection already contains data. Skipping CSV import.")
        return True

    print(f"{datetime.now()} MongoDB 'books' collection is empty. Importing data from {csv_filepath}...")
    
    if not os.path.exists(csv_filepath):
        print(f"{datetime.now()} Error: CSV file not found at {csv_filepath}. Please ensure 'books.csv' is in the 'book_manage' directory.")
        return False

    imported_count = 0
    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        books_to_insert = []
        for row in csv_reader:
            # 转换字符串表示的列表为实际列表，并处理可能的数值类型
            try:
                row['genres'] = eval(row['genres']) if row['genres'] else []
                row['characters'] = eval(row['characters']) if row['characters'] else []
                row['awards'] = eval(row['awards']) if row['awards'] else []
                row['ratingsByStars'] = eval(row['ratingsByStars']) if row['ratingsByStars'] else []
                row['setting'] = eval(row['setting']) if row['setting'] else []
                # 尝试将数值字段转换为合适的类型
                row['rating'] = float(row['rating']) if row.get('rating') else None
                row['pages'] = int(row['pages']) if row.get('pages') else None
                row['numRatings'] = int(row['numRatings']) if row.get('numRatings') else None
                row['likedPercent'] = float(row['likedPercent']) if row.get('likedPercent') else None
                row['bbeScore'] = int(row['bbeScore']) if row.get('bbeScore') else None
                row['bbeVotes'] = int(row['bbeVotes']) if row.get('bbeVotes') else None
                row['price'] = float(row['price']) if row.get('price') else None
            except Exception as e:
                print(f"{datetime.now()} Warning: Could not parse row data for bookId {row.get('bookId')}: {e}. Skipping row.")
                continue # 跳过当前行，继续处理下一行
            
            books_to_insert.append(row)

        if books_to_insert:
            try:
                # 批量插入数据以提高效率
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


def initialize_mongo_connection():
    """
    初始化 MongoDB 连接并导入数据
    """
    print(f"{datetime.now()} Attempting to initialize MongoDB connection and import data...")
    
    collection = get_mongo_collection()
    if collection is not None:
        print(f"{datetime.now()} MongoDB connection established. Checking for data...")
        try:
            if collection.count_documents({}) == 0:
                print(f"{datetime.now()} Importing data from CSV...")
                import_books_from_csv()
            else:
                print(f"{datetime.now()} MongoDB already contains data. Skipping import.")
            return True
        except Exception as e:
            print(f"{datetime.now()} Error checking collection: {e}")
            return False
    else:
        print(f"{datetime.now()} MongoDB connection failed at startup. Data import skipped.")
        return False

# --- 原有的辅助函数：搜索豆瓣图书 (无需修改) ---
def search_douban_books_backend(keyword):
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

# --- API 路由：获取所有本地书籍 (从 MongoDB) ---
@app.route('/api/books', methods=['GET'])
def get_books():
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        books = list(collection.find({}, {'_id': 0}))
        return jsonify(books)
    except Exception as e:
        print(f"Error fetching books from MongoDB: {e}")
        return jsonify({"error": "Failed to retrieve books"}), 500

# --- API 路由：获取单本本地书籍 (从 MongoDB) ---
@app.route('/api/books/<bookId>', methods=['GET'])
def get_book(bookId):
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        book = collection.find_one({"bookId": bookId}, {'_id': 0})
        if book:
            return jsonify(book)
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        print(f"Error fetching single book from MongoDB: {e}")
        return jsonify({"error": "Failed to retrieve book"}), 500

# --- 新增 API 路由：批量获取本地书籍 (从 MongoDB) ---
@app.route('/api/books/batch', methods=['GET'])
def get_books_batch():
    # 获取查询参数中的 'ids' 字符串，例如: ids=bookId1,bookId2,bookId3
    ids_param = request.args.get('ids')
    if not ids_param:
        return jsonify({"error": "Missing 'ids' parameter"}), 400

    # 将逗号分隔的字符串转换为列表
    book_ids = ids_param.split(',')
    
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # 使用 $in 操作符查询所有匹配的 bookId
        # {'_id': 0} 用于排除 MongoDB 自动生成的 _id 字段
        books = list(collection.find({"bookId": {"$in": book_ids}}, {'_id': 0}))
        return jsonify(books)
    except Exception as e:
        print(f"Error fetching books in batch from MongoDB: {e}")
        return jsonify({"error": "Failed to retrieve books in batch"}), 500

# --- API 路由：搜索豆瓣图书 (无需修改) ---
@app.route('/api/search_douban', methods=['GET'])
def search_douban():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Please provide a search keyword"}), 400
    douban_books = search_douban_books_backend(keyword)
    return jsonify(douban_books)

# --- API 路由：搜索本地图书 (从 MongoDB) ---
@app.route('/api/search_local_books', methods=['GET'])
def search_local_books():
    keyword = request.args.get('keyword', '').strip()
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({"error": "Database connection failed"}), 500
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
        return jsonify(filtered_books)
    except Exception as e:
        print(f"Error searching local books in MongoDB: {e}")
        return jsonify({"error": "Failed to search books"}), 500

if __name__ == '__main__':
    # 在 Flask 应用启动前执行数据导入检查
    initialize_mongo_connection()
    app.run(host='0.0.0.0', port=5001, debug=True)