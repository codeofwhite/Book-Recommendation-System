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