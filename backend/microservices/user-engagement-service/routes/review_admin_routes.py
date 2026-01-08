# routes/review_admin_routes.py
from flask import Blueprint, jsonify, request
from models import ReviewModel, CommentModel

review_bp = Blueprint("reviews", __name__, url_prefix="/api/admin")


# 书评相关路由
@review_bp.route("/reviews", methods=["GET"])
def get_reviews():
    """获取所有书评，支持筛选、搜索和分页"""
    try:
        # 获取查询参数
        status_filter = request.args.get("status", "all")
        search_keyword = request.args.get("search", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # 限制每页数量
        per_page = min(per_page, 100)

        result, error = ReviewModel.get_all_reviews(
            status_filter=status_filter if status_filter != "all" else None,
            search_keyword=search_keyword if search_keyword else None,
            page=page,
            per_page=per_page,
        )

        if error:
            return jsonify({"error": error}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve reviews: {str(e)}"}), 500


@review_bp.route("/reviews/<review_id>", methods=["GET"])
def get_review(review_id):
    """获取单个书评信息"""
    try:
        review, error = ReviewModel.get_review_by_id(review_id)
        if error:
            if error == "Review not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500

        return jsonify(review)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve review: {str(e)}"}), 500


@review_bp.route("/reviews", methods=["POST"])
def create_review():
    """创建新书评"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # 验证必需字段
        required_fields = ["bookId", "userId", "content", "rating"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        # 验证评分范围
        rating = float(data["rating"])
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        review, error = ReviewModel.create_review(
            book_id=data["bookId"],
            user_id=data["userId"],
            content=data["content"],
            rating=rating,
        )

        if error:
            return jsonify({"error": error}), 500

        return jsonify(review), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create review: {str(e)}"}), 500


@review_bp.route("/reviews/<review_id>/status", methods=["PUT"])
def update_review_status(review_id):
    """更新书评状态"""
    try:
        data = request.get_json()
        if not data or "status" not in data:
            return jsonify({"error": "Status is required"}), 400

        status = data["status"]
        if status not in ["pending", "approved", "rejected"]:
            return jsonify({"error": "Invalid status"}), 400

        updated_review, error = ReviewModel.update_review_status(review_id, status)
        if error:
            if error == "Review not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500

        return jsonify(updated_review)

    except Exception as e:
        return jsonify({"error": f"Failed to update review status: {str(e)}"}), 500


@review_bp.route("/reviews/<review_id>", methods=["DELETE"])
def delete_review(review_id):
    """删除书评"""
    try:
        success, error = ReviewModel.delete_review(review_id)
        if error:
            if error == "Review not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500

        return jsonify(
            {"message": "Review deleted successfully", "reviewId": review_id}
        )

    except Exception as e:
        return jsonify({"error": f"Failed to delete review: {str(e)}"}), 500


@review_bp.route("/books/<book_id>/reviews", methods=["GET"])
def get_reviews_by_book(book_id):
    """根据书籍ID获取书评"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)

        result, error = ReviewModel.get_reviews_by_book(book_id, page, per_page)
        if error:
            return jsonify({"error": error}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve reviews: {str(e)}"}), 500


@review_bp.route("/reviews/stats", methods=["GET"])
def get_review_stats():
    """获取书评统计信息"""
    try:
        stats, error = ReviewModel.get_review_stats()
        if error:
            return jsonify({"error": error}), 500

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve review stats: {str(e)}"}), 500



# 评论相关路由
@review_bp.route("/reviews/<review_id>/comments", methods=["POST"])
def create_comment(review_id):
    """为书评创建新评论"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # 验证必需字段
        required_fields = ["userId", "content"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        comment, error = CommentModel.create_comment(
            review_id=review_id, user_id=data["userId"], content=data["content"]
        )

        if error:
            return jsonify({"error": error}), 500

        return jsonify(comment), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create comment: {str(e)}"}), 500


@review_bp.route("/comments/<comment_id>", methods=["GET"])
def get_comment(comment_id):
    """获取单个评论信息"""
    try:
        comment, error = CommentModel.get_comment_by_id(comment_id)
        if error:
            if error == "Comment not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500

        return jsonify(comment)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve comment: {str(e)}"}), 500


@review_bp.route("/comments/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    """删除评论"""
    try:
        success, error = CommentModel.delete_comment(comment_id)
        if error:
            if error == "Comment not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500

        return jsonify(
            {"message": "Comment deleted successfully", "commentId": comment_id}
        )

    except Exception as e:
        return jsonify({"error": f"Failed to delete comment: {str(e)}"}), 500


@review_bp.route("/comments", methods=["GET"])
def get_all_comments():
    """获取所有评论（管理员用）"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)

        result, error = CommentModel.get_all_comments(page, per_page)
        if error:
            return jsonify({"error": error}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve comments: {str(e)}"}), 500
