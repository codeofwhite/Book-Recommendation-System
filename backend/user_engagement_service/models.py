# user_profile_service/models.py

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# db 实例将在 app.py 中创建并传入
db = SQLAlchemy()

# 图书收藏表 (BOOK_FAVORITE)
class BookFavorite(db.Model):
    __tablename__ = 'BOOK_FAVORITE'
    favorite_id = db.Column(db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16])
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    book_id = db.Column(db.CHAR(255), nullable=False) # 增加长度以适应长ID
    add_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='_user_book_favorite_uc'),)

    def __repr__(self):
        return f"<BookFavorite favorite_id={self.favorite_id} user_id={self.user_id} book_id={self.book_id}>"

# 书评收藏表 (REVIEW_FAVORITE)
class ReviewFavorite(db.Model):
    __tablename__ = 'REVIEW_FAVORITE'
    favorite_id = db.Column(db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16])
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    review_id = db.Column(db.CHAR(255), nullable=False) # 增加长度以适应长ID
    add_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'review_id', name='_user_review_favorite_uc'),)

    def __repr__(self):
        return f"<ReviewFavorite favorite_id={self.favorite_id} user_id={self.user_id} review_id={self.review_id}>"

# 图书点赞表 (BOOK_LIKE)
class BookLike(db.Model):
    __tablename__ = 'BOOK_LIKE'
    like_id = db.Column(db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16])
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    book_id = db.Column(db.CHAR(255), nullable=False) # 增加长度以适应长ID
    like_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='_user_book_like_uc'),)

    def __repr__(self):
        return f"<BookLike like_id={self.like_id} user_id={self.user_id} book_id={self.book_id}>"

# 书评点赞表 (REVIEW_LIKE)
class ReviewLike(db.Model):
    __tablename__ = 'REVIEW_LIKE'
    like_id = db.Column(db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16])
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    review_id = db.Column(db.CHAR(255), nullable=False) # 增加长度以适应长ID
    like_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'review_id', name='_user_review_like_uc'),)

    def __repr__(self):
        return f"<ReviewLike like_id={self.like_id} user_id={self.user_id} review_id={self.review_id}>"
    
# 新增：书评表 (REVIEW)
class Review(db.Model):
    __tablename__ = 'REVIEW'
    review_id = db.Column(db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16])
    book_id = db.Column(db.CHAR(255), nullable=False)
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    rating = db.Column(db.FLOAT(2,1), nullable=False)
    like_count = db.Column(db.Integer, default=0)
    post_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)
    # 将 db.TINYINT 修改为 db.SmallInteger
    status = db.Column(db.SmallInteger, default=0) # 0: 正常, 1: 待审核, 2: 已删除/封禁等

    def __repr__(self):
        return f"<Review review_id={self.review_id} book_id={self.book_id} user_id={self.user_id}>"

    def to_dict(self):
        return {
            'id': self.review_id,
            'bookId': self.book_id,
            'userId': self.user_id,
            'content': self.content,
            'rating': self.rating,
            'likeCount': self.like_count,
            'postTime': self.post_time.isoformat(),
            'status': self.status
        }

# 新增：评论表 (COMMENT) - 这是对书评的评论
class Comment(db.Model):
    __tablename__ = 'COMMENT'
    comment_id = db.Column(db.CHAR(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16])
    review_id = db.Column(db.CHAR(16), nullable=False)
    user_id = db.Column(db.VARCHAR(20), nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    like_count = db.Column(db.Integer, default=0) # 初始点赞数
    comment_time = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Comment comment_id={self.comment_id} review_id={self.review_id} user_id={self.user_id}>"

    def to_dict(self):
        return {
            'id': self.comment_id,
            'reviewId': self.review_id,
            'userId': self.user_id,
            'content': self.content,
            'likeCount': self.like_count,
            'commentTime': self.comment_time.isoformat()
        }