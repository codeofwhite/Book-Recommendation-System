# user_profile_service/routes/review_content.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import (
    CommentModel,
    ReviewFavorite,
    ReviewLike,
    ReviewModel,
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


@review_content_bp.route("/api/reviews/user/<string:user_id>", methods=["GET"])
def get_reviews_for_user(user_id):
    """
    根据用户ID获取该用户发布的所有书评。
    ---
    responses:
      200:
        description: 成功获取用户书评列表
      400:
        description: 请求参数错误
      500:
        description: 服务器内部错误
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    reviews_data, error = ReviewModel.get_reviews_by_user(user_id, page, per_page)

    if error:
        return jsonify({"message": "Error fetching reviews", "error": error}), 500
    if not reviews_data["reviews"] and reviews_data["total"] == 0:
        return (
            jsonify({"message": "No reviews found for this user", "reviews": []}),
            200,
        )  # Or 404 if you prefer for no results

    return jsonify(reviews_data), 200


# --- 评论相关 API (对书评的评论) ---


# Endpoint: GET /api/reviews/<review_id>/comments - 获取某条书评的评论列表
@review_content_bp.route("/api/reviews/<string:review_id>/comments", methods=["GET"])
def get_review_comments(review_id):
    """根据书评ID获取评论，使用 CommentModel 分页逻辑"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)  # 限制每页数量

        # 调用 CommentModel 的方法来获取数据
        result, error = CommentModel.get_comments_by_review(review_id, page, per_page)

        if error:
            print(f"Error fetching comments from CommentModel: {error}")  # 调试日志
            return jsonify({"error": error}), 500

        # CommentModel 已经返回了前端期望的 {'comments': [...], 'total': ...} 结构
        return jsonify(result)

    except Exception as e:
        print(f"Exception in get_review_comments route: {e}")  # 调试日志
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to retrieve comments: {str(e)}"}), 500


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


@review_content_bp.route("/api/comments/user/<string:user_id>", methods=["GET"])
def get_comments_for_user(user_id):
    """
    根据用户ID获取该用户发布的所有评论。
    ---
    responses:
      200:
        description: 成功获取用户评论列表
      400:
        description: 请求参数错误
      500:
        description: 服务器内部错误
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    comments_data, error = CommentModel.get_comments_by_user(user_id, page, per_page)

    if error:
        return jsonify({"message": "Error fetching comments", "error": error}), 500
    if not comments_data["comments"] and comments_data["total"] == 0:
        return (
            jsonify({"message": "No comments found for this user", "comments": []}),
            200,
        )  # Or 404

    return jsonify(comments_data), 200
