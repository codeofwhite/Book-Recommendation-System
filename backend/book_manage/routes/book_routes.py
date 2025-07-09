# routes/book_routes.py
import os
from flask import Blueprint, jsonify, request, send_from_directory
from models.book_model import BookModel

# 创建一个Blueprint实例
book_bp = Blueprint("books", __name__, url_prefix="/api")


@book_bp.route("/books", methods=["GET"])
def get_books():
    """获取所有书籍，支持搜索和分页"""
    search = request.args.get("search", "").strip()
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", default=0, type=int)

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
            books = books[offset : offset + limit]

        return jsonify(books)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve books: {str(e)}"}), 500


@book_bp.route("/books/<book_id>", methods=["GET"])
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


@book_bp.route("/books", methods=["POST"])
def create_book():
    """创建新书籍"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # 验证必需字段
        if not data.get("title") or not data.get("author"):
            return jsonify({"error": "Title and author are required"}), 400

        book, error = BookModel.create_book(data)
        if error:
            return jsonify({"error": error}), 500

        return jsonify(book), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create book: {str(e)}"}), 500


@book_bp.route("/books/<book_id>", methods=["PUT"])
def update_book(book_id):
    """更新书籍信息 - bookId作为字符串处理"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # 移除空值
        update_data = {k: v for k, v in data.items() if v is not None and v != ""}

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


@book_bp.route("/books/<book_id>", methods=["DELETE"])
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


@book_bp.route("/books/batch", methods=["GET"])
def get_books_batch():
    """批量获取书籍"""
    ids_param = request.args.get("ids")
    if not ids_param:
        return jsonify({"error": "Missing 'ids' parameter"}), 400

    try:
        book_ids = ids_param.split(",")
        books, error = BookModel.get_books_by_ids(book_ids)
        if error:
            return jsonify({"error": error}), 500
        return jsonify(books)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve books: {str(e)}"}), 500


@book_bp.route("/books/import-csv", methods=["POST"])
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


@book_bp.route("/search_douban", methods=["GET"])
def search_douban():
    """搜索豆瓣书籍"""
    keyword = request.args.get("keyword", "")
    if not keyword:
        return jsonify({"error": "Please provide a search keyword"}), 400

    try:
        douban_books = BookModel.search_douban_books(keyword)
        return jsonify(douban_books)
    except Exception as e:
        return jsonify({"error": f"Douban search failed: {str(e)}"}), 500


@book_bp.route("/search_local_books", methods=["GET"])
def search_local_books():
    """搜索本地书籍"""
    keyword = request.args.get("keyword", "").strip()
    filtered_books, error = BookModel.search_local_books(keyword)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(filtered_books)


@book_bp.route("/books/popular", methods=["GET"])
def get_popular_books_route():
    limit = request.args.get("limit", 20, type=int)  # 默认获取4本
    books, error = BookModel.get_popular_books(limit)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(books)


@book_bp.route("/books/personalized", methods=["GET"])
def get_personalized_books_route():
    limit = request.args.get("limit", 4, type=int)
    # 实际应用中，这里会根据用户ID进行个性化推荐
    # user_id = request.args.get('user_id') # 如果有用户认证系统的话
    books, error = BookModel.get_personalized_books(limit=limit)  # 暂时不传user_id
    if error:
        return jsonify({"error": error}), 500
    return jsonify(books)


@book_bp.route("/books/rankings/<ranking_type>", methods=["GET"])
def get_book_rankings_route(ranking_type):
    limit = request.args.get("limit", 5, type=int)  # 榜单默认获取5本
    books = []
    error = None
    if ranking_type == "bestselling":  # 畅销榜
        # 假设畅销榜就是热门书籍
        books, error = BookModel.get_popular_books(limit)
    elif ranking_type == "new_releases":  # 新书榜
        books, error = BookModel.get_new_books(limit)
    elif ranking_type == "top_rated":  # 高分榜
        books, error = BookModel.get_top_rated_books(limit)
    else:
        return jsonify({"error": "Invalid ranking type"}), 400

    if error:
        return jsonify({"error": error}), 500
    return jsonify(books)


@book_bp.route("/books/daily", methods=["GET"])
def get_daily_book_route():
    book, error = BookModel.get_daily_book()
    if error:
        return jsonify({"error": error}), 500
    if book:
        return jsonify(book)
    else:
        return jsonify({"error": "Daily book not found"}), 404


# ==================== 新增：EPUB 文件上传和提供服务路由 ====================


# ==================== MinIO EPUB 文件上传路由 (修改) ====================

@book_bp.route('/books/<book_id>/upload_epub', methods=['POST'])
def upload_epub_for_book(book_id):
    """
    为指定书籍上传EPUB文件到 MinIO。
    文件通过 FormData 形式上传。
    """
    if 'epub_file' not in request.files:
        return jsonify({"error": "No epub_file part in the request"}), 400

    file = request.files['epub_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.lower().endswith('.epub'):
        return jsonify({"error": "Invalid file type, only .epub files are allowed"}), 400

    # 1. 上传 EPUB 文件到 MinIO
    epub_minio_url, error = BookModel.upload_epub_to_minio(file, book_id)
    if error:
        return jsonify({"error": f"Failed to upload EPUB to MinIO: {error}"}), 500

    # 2. 更新书籍的 epubUrl 字段到 MongoDB
    update_data = {"epubUrl": epub_minio_url}
    updated_book, error = BookModel.update_book(book_id, update_data)

    if error:
        # 如果更新数据库失败，考虑从 MinIO 删除已上传的文件
        # 实际操作中，为了简单起见，可以忽略此处的 MinIO 删除，依赖 MinIO 的生命周期策略
        # 或者实现一个异步清理机制
        print(f"Warning: EPUB file uploaded to MinIO ({epub_minio_url}) but failed to update DB: {error}")
        return jsonify({"error": f"Failed to update book with EPUB URL: {error}"}), 500

    return jsonify({"message": "EPUB uploaded to MinIO and book updated successfully", "book": updated_book}), 200
