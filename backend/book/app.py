from flask import Flask, jsonify, request
import csv
import os
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import re

app = Flask(__name__)
CORS(app)  

def load_books():
    books = []
    with open('backend/book/data/books.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert string representations of lists to actual lists
            row['genres'] = eval(row['genres']) if row['genres'] else []
            row['characters'] = eval(row['characters']) if row['characters'] else []
            row['awards'] = eval(row['awards']) if row['awards'] else []
            row['ratingsByStars'] = eval(row['ratingsByStars']) if row['ratingsByStars'] else []
            books.append(row)
    return books

# 辅助函数：搜索豆瓣图书
def search_douban_books_backend(keyword):
    """
    根据关键词搜索豆瓣书籍，并返回书籍列表及其详情页链接。
    此函数为后端专用，不进行用户交互或直接打开浏览器。
    """
    search_url = f"https://search.douban.com/book/subject_search?search_text={keyword}&cat=1001"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Referer': 'https://www.douban.com/'
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10) # 增加超时
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

@app.route('/api/books', methods=['GET'])
def get_books():
    books = load_books()
    return jsonify(books)

@app.route('/api/books/<bookId>', methods=['GET'])
def get_book(bookId):
    books = load_books()
    # 确保 bookId 是字符串类型进行比较（因为 CSV 读取的可能都是字符串）
    book = next((book for book in books if str(book['bookId']) == str(bookId)), None)
    
    if book:
        return jsonify(book)
    else:
        return jsonify({"error": "Book not found"}), 404

# API 路由：搜索豆瓣图书
@app.route('/api/search_douban', methods=['GET'])
def search_douban():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Please provide a search keyword"}), 400

    douban_books = search_douban_books_backend(keyword)
    return jsonify(douban_books)

# 新增 API 路由：搜索本地图书
@app.route('/api/search_local_books', methods=['GET'])
def search_local_books():
    keyword = request.args.get('keyword', '').lower() # 获取关键词并转为小写
    if not keyword:
        # 如果关键词为空，返回所有图书
        books = load_books()
        return jsonify(books)

    all_books = load_books()
    
    # 过滤图书，实现模糊搜索
    # 可以根据书名、作者、简介等字段进行匹配
    filtered_books = [
        book for book in all_books 
        if keyword in book.get('title', '').lower() or
           keyword in book.get('author', '').lower() or
           keyword in book.get('description', '').lower()
           # 可以根据需要添加更多字段进行模糊匹配
    ]
    
    return jsonify(filtered_books)

if __name__ == '__main__':
    app.run(debug=True, port=5000)