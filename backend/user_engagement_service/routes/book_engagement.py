# user_profile_service/routes/book_engagement.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, BookFavorite, BookLike # 从 models.py 导入 db 和模型

# 创建一个蓝图
book_engagement_bp = Blueprint('book_engagement', __name__, url_prefix='/api/books')

# --- Book Favorite Endpoints (书籍收藏) ---

@book_engagement_bp.route('/<string:book_id>/favorite_status', methods=['GET'])
def get_book_favorite_status(book_id):
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    is_favorited = BookFavorite.query.filter_by(user_id=user_id, book_id=book_id).first() is not None
    favorite_count = BookFavorite.query.filter_by(book_id=book_id).count()

    return jsonify({"isFavorited": is_favorited, "favoriteCount": favorite_count})

@book_engagement_bp.route('/<string:book_id>/favorite', methods=['POST'])
def toggle_book_favorite(book_id):
    data = request.get_json()
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    favorite_entry = BookFavorite.query.filter_by(user_id=user_id, book_id=book_id).first()
    if favorite_entry:
        db.session.delete(favorite_entry)
        is_favorited = False
    else:
        new_favorite = BookFavorite(user_id=user_id, book_id=book_id)
        db.session.add(new_favorite)
        is_favorited = True

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: could not toggle book favorite"}), 500
    
    favorite_count = BookFavorite.query.filter_by(book_id=book_id).count()
    return jsonify({"isFavorited": is_favorited, "favoriteCount": favorite_count})

# --- Book Like Endpoints (书籍点赞) ---

@book_engagement_bp.route('/<string:book_id>/like_status', methods=['GET'])
def get_book_like_status(book_id):
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    is_liked = BookLike.query.filter_by(user_id=user_id, book_id=book_id).first() is not None
    like_count = BookLike.query.filter_by(book_id=book_id).count()

    return jsonify({"isLiked": is_liked, "likeCount": like_count})

@book_engagement_bp.route('/<string:book_id>/like', methods=['POST'])
def toggle_book_like(book_id):
    data = request.get_json()
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    like_entry = BookLike.query.filter_by(user_id=user_id, book_id=book_id).first()
    if like_entry:
        db.session.delete(like_entry)
        is_liked = False
    else:
        new_like = BookLike(user_id=user_id, book_id=book_id)
        db.session.add(new_like)
        is_liked = True

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: could not toggle book like"}), 500
    
    like_count = BookLike.query.filter_by(book_id=book_id).count()
    return jsonify({"isLiked": is_liked, "likeCount": like_count})

# 新增：获取用户收藏的书籍列表
@book_engagement_bp.route('/favorite_books', methods=['GET'])
def get_user_favorite_books():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    # 查询该用户收藏的所有书籍
    favorite_entries = BookFavorite.query.filter_by(user_id=user_id).all()
    # 提取所有收藏书籍的 book_id
    # 注意：这里只返回了 book_id。前端可能需要根据这些 book_id 再去 Book Management Service (service-b) 获取书籍的详细信息。
    book_ids = [entry.book_id for entry in favorite_entries]

    return jsonify(book_ids) # 返回一个书籍ID的列表