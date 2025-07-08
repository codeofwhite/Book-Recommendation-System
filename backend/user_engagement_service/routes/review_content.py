# user_profile_service/routes/review_content.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import (
    ReviewFavorite,
    ReviewLike,
    db,
    Review,
    Comment,
)  # 导入 Review 和 Comment 模型
import uuid
from datetime import datetime

# 创建一个蓝图，处理书评和评论内容相关的API
# 注意这里的 url_prefix，它将用于处理 /api/books/<book_id>/reviews 和 /api/reviews/<review_id>/comments
review_content_bp = Blueprint("review_content", __name__)

# --- 书评相关 API ---


# Endpoint: GET /api/books/<book_id>/reviews - 获取某本书的书评列表
@review_content_bp.route("/api/books/<string:book_id>/reviews", methods=["GET"])
def get_book_reviews(book_id):
    # 可以根据post_time排序，或者根据like_count排序等
    reviews = (
        Review.query.filter_by(book_id=book_id, status=0)
        .order_by(Review.post_time.desc())
        .all()
    )
    # 返回字典列表，方便JSON序列化
    return jsonify([review.to_dict() for review in reviews])


# Endpoint: POST /api/books/<book_id>/reviews - 提交新书评
@review_content_bp.route("/api/books/<string:book_id>/reviews", methods=["POST"])
def submit_review(book_id):
    data = request.get_json()
    user_id = data.get("userId")
    content = data.get("content")
    rating = data.get("rating")
    # reviewerNickname = data.get('reviewerNickname') # 这些信息不直接存入Review表
    # reviewerAvatarUrl = data.get('reviewerAvatarUrl') # 通常是从用户服务获取或前端展示

    if not all([user_id, content, rating is not None]):
        return (
            jsonify({"error": "Missing required fields: userId, content, rating"}),
            400,
        )
    if not (0 <= rating <= 5):
        return jsonify({"error": "Rating must be between 0 and 5"}), 400

    new_review = Review(
        book_id=book_id,
        user_id=user_id,
        content=content,
        rating=rating,
        # like_count 和 post_time 有默认值
    )
    db.session.add(new_review)

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Review submitted successfully",
                    "reviewId": new_review.review_id,
                }
            ),
            201,
        )
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: could not submit review"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Endpoint: DELETE /api/reviews/<review_id> - 删除书评
@review_content_bp.route("/api/reviews/<string:review_id>", methods=["DELETE"])
def delete_review(review_id):
    # 通常需要验证用户身份，确保只有书评的作者或管理员才能删除
    # 这里为了简化，只实现删除功能，实际应用中需添加认证逻辑
    # 例如：user_id = request.args.get('userId') 或从token获取
    # review_to_delete = Review.query.filter_by(review_id=review_id, user_id=user_id).first()

    review_to_delete = Review.query.get(review_id)
    if not review_to_delete:
        return jsonify({"error": "Review not found"}), 404

    # 软删除：改变状态而不是真正删除，保留数据
    # review_to_delete.status = 3 # 例如，3表示已删除
    # db.session.add(review_to_delete)

    # 硬删除：直接从数据库移除
    db.session.delete(review_to_delete)

    try:
        db.session.commit()
        # 同时删除该书评关联的点赞和收藏（如果直接删除书评）
        ReviewLike.query.filter_by(review_id=review_id).delete()
        ReviewFavorite.query.filter_by(review_id=review_id).delete()
        Comment.query.filter_by(review_id=review_id).delete()  # 删除所有相关评论
        db.session.commit()  # 再次提交以保存关联删除
        return jsonify({"message": "Review deleted successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: could not delete review"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# --- 评论相关 API (对书评的评论) ---


# Endpoint: GET /api/reviews/<review_id>/comments - 获取某条书评的评论列表
@review_content_bp.route("/api/reviews/<string:review_id>/comments", methods=["GET"])
def get_review_comments(review_id):
    comments = (
        Comment.query.filter_by(review_id=review_id)
        .order_by(Comment.comment_time.asc())
        .all()
    )
    return jsonify([comment.to_dict() for comment in comments])


# Endpoint: POST /api/reviews/<review_id>/comments - 提交新评论
@review_content_bp.route("/api/reviews/<string:review_id>/comments", methods=["POST"])
def submit_comment(review_id):
    data = request.get_json()
    user_id = data.get("userId")
    content = data.get("content")

    if not all([user_id, content]):
        return jsonify({"error": "Missing required fields: userId, content"}), 400

    new_comment = Comment(
        review_id=review_id,
        user_id=user_id,
        content=content,
        # like_count 和 comment_time 有默认值
    )
    db.session.add(new_comment)

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Comment submitted successfully",
                    "commentId": new_comment.comment_id,
                }
            ),
            201,
        )
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: could not submit comment"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Endpoint: DELETE /api/comments/<comment_id> - 删除评论
@review_content_bp.route("/api/comments/<string:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    # 同样需要认证和授权
    comment_to_delete = Comment.query.get(comment_id)
    if not comment_to_delete:
        return jsonify({"error": "Comment not found"}), 404

    db.session.delete(comment_to_delete)
    try:
        db.session.commit()
        return jsonify({"message": "Comment deleted successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error: could not delete comment"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
