from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, BookFavorite, BookLike 

book_engagement_bp = Blueprint('book_engagement', __name__, url_prefix='/api/books')

# --- 获取书籍总收藏数 ---
@book_engagement_bp.route('/<string:book_id>/total_favorites', methods=['GET'])
def get_book_total_favorites(book_id):
    favorite_count = BookFavorite.query.filter_by(book_id=book_id).count()
    return jsonify({"totalFavoriteCount": favorite_count})

# --- 获取书籍总点赞数 ---
@book_engagement_bp.route('/<string:book_id>/total_likes', methods=['GET'])
def get_book_total_likes(book_id):
    like_count = BookLike.query.filter_by(book_id=book_id).count()
    return jsonify({"totalLikeCount": like_count})

# --- Book Favorite Endpoints (书籍收藏) ---

@book_engagement_bp.route('/<string:book_id>/favorite_status', methods=['GET'])
def get_book_favorite_status(book_id):
    user_id = request.args.get('userId')
    
    # 无论是否传入 userId，都计算总收藏数
    favorite_count = BookFavorite.query.filter_by(book_id=book_id).count()

    is_favorited = False
    if user_id: # 只有当 userId 存在时，才查询用户个人状态
        is_favorited = BookFavorite.query.filter_by(user_id=user_id, book_id=book_id).first() is not None
    else:
        # 如果没有 userId，可以打印一条日志或者直接返回总数，不包含 isFavorited 字段，或者 isFavorited 始终为 False
        print(f"Warning: userId not provided for favorite_status on book {book_id}. Only total count will be returned for personal status.")
        
    return jsonify({"isFavorited": is_favorited, "favoriteCount": favorite_count}) # favoriteCount 始终返回

@book_engagement_bp.route('/<string:book_id>/favorite', methods=['POST'])
def toggle_book_favorite(book_id):
    data = request.get_json()
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required to toggle favorite"}), 400 # 切换状态必须登录

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
    
    # 无论是否传入 userId，都计算总点赞数
    like_count = BookLike.query.filter_by(book_id=book_id).count()

    is_liked = False
    if user_id: # 只有当 userId 存在时，才查询用户个人状态
        is_liked = BookLike.query.filter_by(user_id=user_id, book_id=book_id).first() is not None
    else:
        print(f"Warning: userId not provided for like_status on book {book_id}. Only total count will be returned for personal status.")

    return jsonify({"isLiked": is_liked, "likeCount": like_count}) # likeCount 始终返回

@book_engagement_bp.route('/<string:book_id>/like', methods=['POST'])
def toggle_book_like(book_id):
    data = request.get_json()
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required to toggle like"}), 400 # 切换状态必须登录

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

# 获取用户收藏的书籍列表
@book_engagement_bp.route('/favorite_books', methods=['GET'])
def get_user_favorite_books():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    # 查询该用户收藏的所有书籍
    favorite_entries = BookFavorite.query.filter_by(user_id=user_id).all()

    # 这里只返回了 book_id。前端需要根据这些 book_id 再去 Book Management Service (service-b) 获取书籍的详细信息。
    book_ids = [entry.book_id for entry in favorite_entries]

    return jsonify(book_ids)