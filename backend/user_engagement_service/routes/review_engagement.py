# user_profile_service/routes/review_engagement.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, ReviewFavorite, ReviewLike # 从 models.py 导入 db 和模型

# 创建一个蓝图
review_engagement_bp = Blueprint('review_engagement', __name__, url_prefix='/api/reviews')

# --- Review Favorite Endpoints (书评收藏) ---

@review_engagement_bp.route('/<string:review_id>/favorite_status', methods=['GET'])
def get_review_favorite_status(review_id):
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    is_favorited = ReviewFavorite.query.filter_by(user_id=user_id, review_id=review_id).first() is not None
    favorite_count = ReviewFavorite.query.filter_by(review_id=review_id).count()

    return jsonify({"isFavorited": is_favorited, "favoriteCount": favorite_count})

@review_engagement_bp.route('/<string:review_id>/favorite', methods=['POST'])
def toggle_review_favorite(review_id):
    data = request.get_json()
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    favorite_entry = ReviewFavorite.query.filter_by(user_id=user_id, review_id=review_id).first()
    if favorite_entry:
        db.session.delete(favorite_entry)
        is_favorited = False
    else:
        new_favorite = ReviewFavorite(user_id=user_id, review_id=review_id)
        db.session.add(new_favorite)
        is_favorited = True

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: could not toggle review favorite"}), 500
    
    favorite_count = ReviewFavorite.query.filter_by(review_id=review_id).count()
    return jsonify({"isFavorited": is_favorited, "favoriteCount": favorite_count})

# --- Review Like Endpoints (书评点赞) ---

@review_engagement_bp.route('/<string:review_id>/like_status', methods=['GET'])
def get_review_like_status(review_id):
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    is_liked = ReviewLike.query.filter_by(user_id=user_id, review_id=review_id).first() is not None
    like_count = ReviewLike.query.filter_by(review_id=review_id).count()

    return jsonify({"isLiked": is_liked, "likeCount": like_count})

@review_engagement_bp.route('/<string:review_id>/like', methods=['POST'])
def toggle_review_like(review_id):
    data = request.get_json()
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    like_entry = ReviewLike.query.filter_by(user_id=user_id, review_id=review_id).first()
    if like_entry:
        db.session.delete(like_entry)
        is_liked = False
    else:
        new_like = ReviewLike(user_id=user_id, review_id=review_id)
        db.session.add(new_like)
        is_liked = True

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: could not toggle review like"}), 500
    
    like_count = ReviewLike.query.filter_by(review_id=review_id).count()
    return jsonify({"isLiked": is_liked, "likeCount": like_count})

# 新增：获取用户收藏的书评列表
@review_engagement_bp.route('/favorite_reviews', methods=['GET'])
def get_user_favorite_reviews():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    # 查询该用户收藏的所有书评
    favorite_entries = ReviewFavorite.query.filter_by(user_id=user_id).all()
    # 提取所有收藏书评的 review_id
    # 注意：这里只返回了 review_id。前端可能需要根据这些 review_id 再去 Review Content Service (service-c) 获取书评的详细信息。
    review_ids = [entry.review_id for entry in favorite_entries]

    return jsonify(review_ids) # 返回一个书评ID的列表