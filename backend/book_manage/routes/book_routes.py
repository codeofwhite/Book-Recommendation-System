# routes/book_routes.py
from flask import Blueprint, jsonify, request

# 从models中导入BookModel
from models.book_model import BookModel

# 创建一个Blueprint实例
book_bp = Blueprint('books', __name__, url_prefix='/api')

@book_bp.route('/books', methods=['GET'])
def get_books():
    books, error = BookModel.get_all_books()
    if error:
        return jsonify({"error": error}), 500
    return jsonify(books)

@book_bp.route('/books/<bookId>', methods=['GET'])
def get_book(bookId):
    book, error = BookModel.get_book_by_id(bookId)
    if error:
        return jsonify({"error": error}), 500
    if book:
        return jsonify(book)
    else:
        return jsonify({"error": "Book not found"}), 404

@book_bp.route('/books/batch', methods=['GET'])
def get_books_batch():
    ids_param = request.args.get('ids')
    if not ids_param:
        return jsonify({"error": "Missing 'ids' parameter"}), 400

    book_ids = ids_param.split(',')
    books, error = BookModel.get_books_by_ids(book_ids)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(books)

@book_bp.route('/search_douban', methods=['GET'])
def search_douban():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Please provide a search keyword"}), 400
    douban_books = BookModel.search_douban_books(keyword)
    return jsonify(douban_books)

@book_bp.route('/search_local_books', methods=['GET'])
def search_local_books():
    keyword = request.args.get('keyword', '').strip()
    filtered_books, error = BookModel.search_local_books(keyword)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(filtered_books)

@book_bp.route('/books/popular', methods=['GET'])
def get_popular_books_route():
    limit = request.args.get('limit', 20, type=int) # 默认获取4本
    books, error = BookModel.get_popular_books(limit)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(books)

@book_bp.route('/books/personalized', methods=['GET'])
def get_personalized_books_route():
    limit = request.args.get('limit', 4, type=int)
    # 实际应用中，这里会根据用户ID进行个性化推荐
    # user_id = request.args.get('user_id') # 如果有用户认证系统的话
    books, error = BookModel.get_personalized_books(limit=limit) # 暂时不传user_id
    if error:
        return jsonify({"error": error}), 500
    return jsonify(books)

@book_bp.route('/books/rankings/<ranking_type>', methods=['GET'])
def get_book_rankings_route(ranking_type):
    limit = request.args.get('limit', 5, type=int) # 榜单默认获取5本
    books = []
    error = None
    if ranking_type == 'bestselling': # 畅销榜
        # 假设畅销榜就是热门书籍
        books, error = BookModel.get_popular_books(limit)
    elif ranking_type == 'new_releases': # 新书榜
        books, error = BookModel.get_new_books(limit)
    elif ranking_type == 'top_rated': # 高分榜
        books, error = BookModel.get_top_rated_books(limit)
    else:
        return jsonify({"error": "Invalid ranking type"}), 400

    if error:
        return jsonify({"error": error}), 500
    return jsonify(books)

@book_bp.route('/books/daily', methods=['GET'])
def get_daily_book_route():
    book, error = BookModel.get_daily_book()
    if error:
        return jsonify({"error": error}), 500
    if book:
        return jsonify(book)
    else:
        return jsonify({"error": "Daily book not found"}), 404