# user_profile_service/models.py

from operator import and_, or_
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# db 实例将在 app.py 中创建并传入
db = SQLAlchemy()


# 图书收藏表 (BOOK_FAVORITE)
class BookFavorite(db.Model):
    __tablename__ = "BOOK_FAVORITE"
    favorite_id = db.Column(
        db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16]
    )
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    book_id = db.Column(db.CHAR(255), nullable=False)  # 增加长度以适应长ID
    add_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "book_id", name="_user_book_favorite_uc"),
    )

    def __repr__(self):
        return f"<BookFavorite favorite_id={self.favorite_id} user_id={self.user_id} book_id={self.book_id}>"


# 书评收藏表 (REVIEW_FAVORITE)
class ReviewFavorite(db.Model):
    __tablename__ = "REVIEW_FAVORITE"
    favorite_id = db.Column(
        db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16]
    )
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    review_id = db.Column(db.CHAR(255), nullable=False)  # 增加长度以适应长ID
    add_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "review_id", name="_user_review_favorite_uc"),
    )

    def __repr__(self):
        return f"<ReviewFavorite favorite_id={self.favorite_id} user_id={self.user_id} review_id={self.review_id}>"


# 图书点赞表 (BOOK_LIKE)
class BookLike(db.Model):
    __tablename__ = "BOOK_LIKE"
    like_id = db.Column(
        db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16]
    )
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    book_id = db.Column(db.CHAR(255), nullable=False)  # 增加长度以适应长ID
    like_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "book_id", name="_user_book_like_uc"),
    )

    def __repr__(self):
        return f"<BookLike like_id={self.like_id} user_id={self.user_id} book_id={self.book_id}>"


# 书评点赞表 (REVIEW_LIKE)
class ReviewLike(db.Model):
    __tablename__ = "REVIEW_LIKE"
    like_id = db.Column(
        db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16]
    )
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    review_id = db.Column(db.CHAR(255), nullable=False)  # 增加长度以适应长ID
    like_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "review_id", name="_user_review_like_uc"),
    )

    def __repr__(self):
        return f"<ReviewLike like_id={self.like_id} user_id={self.user_id} review_id={self.review_id}>"


# 新增：书评表 (REVIEW)
class Review(db.Model):
    __tablename__ = "REVIEW"
    review_id = db.Column(
        db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16]
    )
    book_id = db.Column(db.CHAR(255), nullable=False)
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    rating = db.Column(db.FLOAT(2, 1), nullable=False)
    like_count = db.Column(db.Integer, default=0)
    post_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)
    # 将 db.TINYINT 修改为 db.SmallInteger
    status = db.Column(
        db.SmallInteger, default=0
    )  # 0: 正常, 1: 待审核, 2: 已删除/封禁等

    def __repr__(self):
        return f"<Review review_id={self.review_id} book_id={self.book_id} user_id={self.user_id}>"

    def to_dict(self):
        return {
            "id": self.review_id,
            "bookId": self.book_id,
            "userId": self.user_id,
            "content": self.content,
            "rating": self.rating,
            "likeCount": self.like_count,
            "postTime": self.post_time.isoformat(),
            "status": self.status,
        }


# 新增：评论表 (COMMENT) - 这是对书评的评论
class Comment(db.Model):
    __tablename__ = "COMMENT"
    comment_id = db.Column(
        db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16]
    )
    review_id = db.Column(db.CHAR(16), nullable=False)
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    like_count = db.Column(db.Integer, default=0)  # 初始点赞数
    comment_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Comment comment_id={self.comment_id} review_id={self.review_id} user_id={self.user_id}>"

    def to_dict(self):
        return {
            "id": self.comment_id,
            "reviewId": self.review_id,
            "userId": self.user_id,
            "content": self.content,
            "likeCount": self.like_count,
            "commentTime": self.comment_time.isoformat(),
        }


class ReviewModel:

    @classmethod
    def get_all_reviews(
        cls, status_filter=None, search_keyword=None, page=1, per_page=10
    ):
        """获取所有书评，支持筛选、搜索和分页"""
        try:
            query = Review.query

            # 状态筛选
            if status_filter and status_filter != "all":
                status_map = {"pending": 1, "approved": 0, "rejected": 2}
                if status_filter in status_map:
                    query = query.filter(Review.status == status_map[status_filter])

            # 搜索关键词
            if search_keyword:
                search_pattern = f"%{search_keyword}%"
                query = query.filter(
                    or_(
                        Review.content.like(search_pattern),
                        Review.user_id.like(search_pattern),
                        Review.book_id.like(search_pattern),
                    )
                )

            # 按发布时间倒序排列
            query = query.order_by(Review.post_time.desc())

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            reviews = []
            for review in pagination.items:
                review_dict = {
                    "id": review.review_id,
                    "bookId": review.book_id,
                    "userId": review.user_id,
                    "content": review.content,
                    "rating": float(review.rating),
                    "likeCount": review.like_count,
                    "postTime": (
                        review.post_time.isoformat() if review.post_time else None
                    ),
                    "status": cls._get_status_text(review.status),
                }
                reviews.append(review_dict)

            return {
                "reviews": reviews,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }, None

        except Exception as e:
            print(f"Error fetching reviews: {e}")
            return None, str(e)

    @classmethod
    def get_review_by_id(cls, review_id):
        """根据ID获取书评"""
        try:
            review = Review.query.filter_by(review_id=review_id).first()
            if review:
                review_dict = {
                    "id": review.review_id,
                    "bookId": review.book_id,
                    "userId": review.user_id,
                    "content": review.content,
                    "rating": float(review.rating),
                    "likeCount": review.like_count,
                    "postTime": (
                        review.post_time.isoformat() if review.post_time else None
                    ),
                    "status": cls._get_status_text(review.status),
                }
                return review_dict, None
            return None, "Review not found"

        except Exception as e:
            print(f"Error fetching review by ID: {e}")
            return None, str(e)

    @classmethod
    def create_review(cls, book_id, user_id, content, rating):
        """创建新书评"""
        try:
            # 生成16位review_id
            review_id = uuid.uuid4().hex[:16]

            # 创建书评对象
            review = Review(
                review_id=review_id,
                book_id=book_id,
                user_id=user_id,
                content=content,
                rating=float(rating),
                like_count=0,
                post_time=datetime.utcnow(),
                status=1,  # 默认待审核
            )

            # 保存到数据库
            db.session.add(review)
            db.session.commit()

            # 返回创建的书评信息
            review_dict = {
                "id": review_id,
                "bookId": book_id,
                "userId": user_id,
                "content": content,
                "rating": float(rating),
                "likeCount": 0,
                "postTime": review.post_time.isoformat(),
                "status": "pending",
            }

            return review_dict, None

        except Exception as e:
            db.session.rollback()
            print(f"Error creating review: {e}")
            return None, str(e)

    @classmethod
    def update_review_status(cls, review_id, status):
        """更新书评状态"""
        try:
            # 状态映射
            status_map = {"pending": 1, "approved": 0, "rejected": 2}

            if status not in status_map:
                return None, "Invalid status"

            # 查找书评
            review = Review.query.filter_by(review_id=review_id).first()
            if not review:
                return None, "Review not found"

            # 更新状态
            review.status = status_map[status]
            db.session.commit()

            # 返回更新后的书评信息
            review_dict = {
                "id": review.review_id,
                "bookId": review.book_id,
                "userId": review.user_id,
                "content": review.content,
                "rating": float(review.rating),
                "likeCount": review.like_count,
                "postTime": review.post_time.isoformat() if review.post_time else None,
                "status": status,
            }

            return review_dict, None

        except Exception as e:
            db.session.rollback()
            print(f"Error updating review status: {e}")
            return None, str(e)

    @classmethod
    def delete_review(cls, review_id):
        """删除书评"""
        try:
            # 查找书评
            review = Review.query.filter_by(review_id=review_id).first()
            if not review:
                return False, "Review not found"

            # 删除相关评论
            Comment.query.filter_by(review_id=review_id).delete()

            # 删除书评
            db.session.delete(review)
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting review: {e}")
            return False, str(e)

    @classmethod
    def get_reviews_by_book(cls, book_id, page=1, per_page=10):
        """根据书籍ID获取书评"""
        try:
            # 只获取已审核通过的书评
            query = Review.query.filter(
                and_(Review.book_id == book_id, Review.status == 0)
            ).order_by(Review.post_time.desc())

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            reviews = []
            for review in pagination.items:
                review_dict = {
                    "id": review.review_id,
                    "bookId": review.book_id,
                    "userId": review.user_id,
                    "content": review.content,
                    "rating": float(review.rating),
                    "likeCount": review.like_count,
                    "postTime": (
                        review.post_time.isoformat() if review.post_time else None
                    ),
                    "status": "approved",
                }
                reviews.append(review_dict)

            return {
                "reviews": reviews,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }, None

        except Exception as e:
            print(f"Error fetching reviews by book: {e}")
            return None, str(e)

    @classmethod
    def get_review_stats(cls):
        """获取书评统计信息"""
        try:
            total_reviews = Review.query.count()
            pending_reviews = Review.query.filter_by(status=1).count()
            approved_reviews = Review.query.filter_by(status=0).count()
            rejected_reviews = Review.query.filter_by(status=2).count()

            # 计算本周新增书评（简化计算）
            from datetime import datetime, timedelta

            week_ago = datetime.utcnow() - timedelta(days=7)
            new_this_week = Review.query.filter(Review.post_time >= week_ago).count()

            return {
                "total_reviews": total_reviews,
                "pending_reviews": pending_reviews,
                "approved_reviews": approved_reviews,
                "rejected_reviews": rejected_reviews,
                "new_this_week": new_this_week,
            }, None

        except Exception as e:
            print(f"Error fetching review stats: {e}")
            return None, str(e)

    @classmethod
    def _get_status_text(cls, status_code):
        """将状态码转换为文本"""
        status_map = {0: "approved", 1: "pending", 2: "rejected"}
        return status_map.get(status_code, "unknown")
    
    # --- 新增方法：根据用户ID获取书评 ---
    @classmethod
    def get_reviews_by_user(cls, user_id, page=1, per_page=10):
        """根据用户ID获取其发布的所有书评，支持分页"""
        try:
            query = Review.query.filter_by(user_id=user_id).order_by(
                Review.post_time.desc()
            )

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            reviews = []
            for review in pagination.items:
                review_dict = {
                    "id": review.review_id,
                    "bookId": review.book_id,
                    "userId": review.user_id,
                    "content": review.content,
                    "rating": float(review.rating),
                    "likeCount": review.like_count,
                    "postTime": (
                        review.post_time.isoformat() if review.post_time else None
                    ),
                    "status": cls._get_status_text(review.status),
                }
                reviews.append(review_dict)

            return {
                "reviews": reviews,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }, None

        except Exception as e:
            print(f"Error fetching reviews by user ID: {e}")
            return None, str(e)


class CommentModel:

    @classmethod
    def get_comments_by_review(cls, review_id, page=1, per_page=10):
        """根据书评ID获取评论"""
        try:
            query = Comment.query.filter_by(review_id=review_id).order_by(
                Comment.comment_time.asc()
            )

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            comments = []
            for comment in pagination.items:
                comment_dict = {
                    "id": comment.comment_id,
                    "reviewId": comment.review_id,
                    "userId": comment.user_id,
                    "content": comment.content,
                    "likeCount": comment.like_count,
                    "commentTime": (
                        comment.comment_time.isoformat()
                        if comment.comment_time
                        else None
                    ),
                }
                comments.append(comment_dict)

            return {
                "comments": comments,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }, None

        except Exception as e:
            print(f"Error fetching comments by review: {e}")
            return None, str(e)

    @classmethod
    def create_comment(cls, review_id, user_id, content):
        """创建新评论"""
        try:
            # 生成16位comment_id
            comment_id = uuid.uuid4().hex[:16]

            # 创建评论对象
            comment = Comment(
                comment_id=comment_id,
                review_id=review_id,
                user_id=user_id,
                content=content,
                like_count=0,
                comment_time=datetime.utcnow(),
            )

            # 保存到数据库
            db.session.add(comment)
            db.session.commit()

            # 返回创建的评论信息
            comment_dict = {
                "id": comment_id,
                "reviewId": review_id,
                "userId": user_id,
                "content": content,
                "likeCount": 0,
                "commentTime": comment.comment_time.isoformat(),
            }

            return comment_dict, None

        except Exception as e:
            db.session.rollback()
            print(f"Error creating comment: {e}")
            return None, str(e)

    @classmethod
    def delete_comment(cls, comment_id):
        """删除评论"""
        try:
            # 查找评论
            comment = Comment.query.filter_by(comment_id=comment_id).first()
            if not comment:
                return False, "Comment not found"

            # 删除评论
            db.session.delete(comment)
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting comment: {e}")
            return False, str(e)

    @classmethod
    def get_comment_by_id(cls, comment_id):
        """根据ID获取评论"""
        try:
            comment = Comment.query.filter_by(comment_id=comment_id).first()
            if comment:
                comment_dict = {
                    "id": comment.comment_id,
                    "reviewId": comment.review_id,
                    "userId": comment.user_id,
                    "content": comment.content,
                    "likeCount": comment.like_count,
                    "commentTime": (
                        comment.comment_time.isoformat()
                        if comment.comment_time
                        else None
                    ),
                }
                return comment_dict, None
            return None, "Comment not found"

        except Exception as e:
            print(f"Error fetching comment by ID: {e}")
            return None, str(e)

    @classmethod
    def get_all_comments(cls, page=1, per_page=10):
        """获取所有评论（管理员用）"""
        try:
            query = Comment.query.order_by(Comment.comment_time.desc())

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            comments = []
            for comment in pagination.items:
                comment_dict = {
                    "id": comment.comment_id,
                    "reviewId": comment.review_id,
                    "userId": comment.user_id,
                    "content": comment.content,
                    "likeCount": comment.like_count,
                    "commentTime": (
                        comment.comment_time.isoformat()
                        if comment.comment_time
                        else None
                    ),
                }
                comments.append(comment_dict)

            return {
                "comments": comments,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }, None

        except Exception as e:
            print(f"Error fetching all comments: {e}")
            return None, str(e)
        
# --- 新增方法：根据用户ID获取评论 ---
    @classmethod
    def get_comments_by_user(cls, user_id, page=1, per_page=10):
        """根据用户ID获取其发布的所有评论，支持分页"""
        try:
            query = Comment.query.filter_by(user_id=user_id).order_by(
                Comment.comment_time.desc()
            )

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            comments = []
            for comment in pagination.items:
                comment_dict = {
                    "id": comment.comment_id,
                    "reviewId": comment.review_id,
                    "userId": comment.user_id,
                    "content": comment.content,
                    "likeCount": comment.like_count,
                    "commentTime": (
                        comment.comment_time.isoformat()
                        if comment.comment_time
                        else None
                    ),
                }
                comments.append(comment_dict)

            return {
                "comments": comments,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }, None

        except Exception as e:
            print(f"Error fetching comments by user ID: {e}")
            return None, str(e)
