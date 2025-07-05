# routes/book_routes.py
from flask import Blueprint, jsonify, request
from models.book_model import BookModel

# 创建一个Blueprint实例
book_bp = Blueprint('books', __name__, url_prefix='/api')

@book_bp.route('/books', methods=['GET'])
def get_books():
    """获取所有书籍，支持搜索和分页"""
    search = request.args.get('search', '').strip()
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    try:
        if search:
            books, error = BookModel.search_local_books(search)
        else:
            books, error = BookModel.get_all_books()
        
        if error:
            return jsonify({"error": error}), 500
        
        if books is None:
            books = []
        
        # 应用分页
        if limit is not None:
            books = books[offset:offset + limit]
        
        return jsonify(books)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve books: {str(e)}"}), 500

@book_bp.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """获取单本书籍 - bookId作为字符串处理"""
    try:
        book, error = BookModel.get_book_by_id(book_id)
        if error:
            return jsonify({"error": error}), 500
        if book:
            return jsonify(book)
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve book: {str(e)}"}), 500

@book_bp.route('/books', methods=['POST'])
def create_book():
    """创建新书籍"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # 验证必需字段
        if not data.get('title') or not data.get('author'):
            return jsonify({"error": "Title and author are required"}), 400
        
        book, error = BookModel.create_book(data)
        if error:
            return jsonify({"error": error}), 500
        
        return jsonify(book), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create book: {str(e)}"}), 500

@book_bp.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """更新书籍信息 - bookId作为字符串处理"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # 移除空值
        update_data = {k: v for k, v in data.items() if v is not None and v != ''}
        
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        updated_book, error = BookModel.update_book(book_id, update_data)
        if error:
            if error == "Book not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500
        
        return jsonify(updated_book)
    except Exception as e:
        return jsonify({"error": f"Failed to update book: {str(e)}"}), 500

@book_bp.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """删除书籍 - bookId作为字符串处理"""
    try:
        success, error = BookModel.delete_book(book_id)
        if error:
            if error == "Book not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500
        
        return jsonify({"message": "Book deleted successfully", "bookId": book_id})
    except Exception as e:
        return jsonify({"error": f"Failed to delete book: {str(e)}"}), 500

@book_bp.route('/books/batch', methods=['GET'])
def get_books_batch():
    """批量获取书籍"""
    ids_param = request.args.get('ids')
    if not ids_param:
        return jsonify({"error": "Missing 'ids' parameter"}), 400

    try:
        book_ids = ids_param.split(',')
        books, error = BookModel.get_books_by_ids(book_ids)
        if error:
            return jsonify({"error": error}), 500
        return jsonify(books)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve books: {str(e)}"}), 500

@book_bp.route('/books/import-csv', methods=['POST'])
def import_books_csv():
    """从CSV导入书籍"""
    try:
        success = BookModel.import_books_from_csv()
        if success:
            return jsonify({"message": "Books imported successfully from CSV"})
        else:
            return jsonify({"error": "Failed to import books from CSV"}), 500
    except Exception as e:
        return jsonify({"error": f"CSV import failed: {str(e)}"}), 500

@book_bp.route('/search_douban', methods=['GET'])
def search_douban():
    """搜索豆瓣书籍"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Please provide a search keyword"}), 400
    
    try:
        douban_books = BookModel.search_douban_books(keyword)
        return jsonify(douban_books)
    except Exception as e:
        return jsonify({"error": f"Douban search failed: {str(e)}"}), 500

@book_bp.route('/search_local_books', methods=['GET'])
def search_local_books():
    """搜索本地书籍"""
    keyword = request.args.get('keyword', '').strip()
    try:
        filtered_books, error = BookModel.search_local_books(keyword)
        if error:
            return jsonify({"error": error}), 500
        return jsonify(filtered_books)
    except Exception as e:
        return jsonify({"error": f"Local search failed: {str(e)}"}), 500