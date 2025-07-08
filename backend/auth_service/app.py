from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model import db, bcrypt, User, UserModel  # 确保 User 和 Admin 在 models.py 中定义
from config import Config
import os  # 用于文件路径操作
import uuid  # 用于生成唯一文件名
from datetime import datetime  # 导入 datetime 用于处理时间

app = Flask(__name__)
app.config.from_object(Config)

# 初始化 SQLAlchemy 和 Bcrypt
db.init_app(app)
bcrypt.init_app(app)

# 允许跨域请求
CORS(app)

# --- 配置上传文件路径 ---
# 获取当前脚本的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))
# 定义头像上传目录
UPLOAD_FOLDER = os.path.join(basedir, "uploads", "avatars")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # 如果目录不存在则创建
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB 上传限制

# 允许的头像文件扩展名
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 确保在应用上下文中使用 db.create_all() 来创建表
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return "Hello from Flask API!"


# --- 认证路由 ---
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Missing username, email, or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409

    try:
        new_user = User(username=username, email=email, password=password)
        # registration_date will be set automatically by the model's default=func.now()
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {e}")
        return jsonify({"message": "Registration failed due to server error"}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User.query.filter_by(email=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    # --- 登录成功，更新最后登录时间 ---
    user.last_login_date = datetime.now()
    db.session.commit()  # 提交更新

    # --- 返回更详细的用户信息，包括新字段 ---
    return (
        jsonify(
            {
                "message": "Login successful",
                "token": "dummy_token_for_now",  # 在实际应用中应生成JWT
                "user_id": user.id,
                "nickname": user.username,  # 目前使用username作为nickname
                "email": user.email,
                "avatar_url": user.avatar_url,
                "registration_date": (
                    user.registration_date.isoformat()
                    if user.registration_date
                    else None
                ),  # 转换为ISO格式字符串
                "last_login_date": (
                    user.last_login_date.isoformat() if user.last_login_date else None
                ),  # 转换为ISO格式字符串
                "age": user.age,
                "gender": user.gender,
                "location": user.location,
                "occupation": user.occupation,
                "interest_tags": user.interest_tags,
                "preferred_book_types": user.preferred_book_types,
                "preferred_authors": user.preferred_authors,
                "preferred_genres": user.preferred_genres,
                "preferred_reading_duration": user.preferred_reading_duration,
                "is_profile_complete": user.is_profile_complete,
            }
        ),
        200,
    )


# --- 用户信息相关路由 ---


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user_info(user_id):
    """
    获取指定用户ID的用户信息。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # 返回用户数据，不包含敏感信息如密码哈希
    return (
        jsonify(
            {
                "user_id": user.id,
                "nickname": user.username,  # 这里仍然使用username作为nickname
                "email": user.email,
                "avatar_url": user.avatar_url,
                "registration_date": (
                    user.registration_date.isoformat()
                    if user.registration_date
                    else None
                ),
                "last_login_date": (
                    user.last_login_date.isoformat() if user.last_login_date else None
                ),
                "age": user.age,
                "gender": user.gender,
                "location": user.location,
                "occupation": user.occupation,
                "interest_tags": user.interest_tags,
                "preferred_book_types": user.preferred_book_types,
                "preferred_authors": user.preferred_authors,
                "preferred_genres": user.preferred_genres,
                "preferred_reading_duration": user.preferred_reading_duration,
                "is_profile_complete": user.is_profile_complete,
            }
        ),
        200,
    )


# --- 新增：更新用户资料接口 (用于问卷提交) ---
@app.route("/api/users/<int:user_id>/profile", methods=["PUT"])
def update_user_profile(user_id):
    """
    更新用户的详细资料（年龄、性别、地域、职业、兴趣偏好等）。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    # 遍历数据并更新用户模型字段
    # 使用 .get(key, user.key) 可以确保如果某个字段未提供，则保留其原有值
    user.age = data.get("age", user.age)
    user.gender = data.get("gender", user.gender)
    user.location = data.get("location", user.location)
    user.occupation = data.get("occupation", user.occupation)
    user.interest_tags = data.get("interest_tags", user.interest_tags)
    user.preferred_book_types = data.get(
        "preferred_book_types", user.preferred_book_types
    )
    user.preferred_authors = data.get("preferred_authors", user.preferred_authors)
    user.preferred_genres = data.get("preferred_genres", user.preferred_genres)
    user.preferred_reading_duration = data.get(
        "preferred_reading_duration", user.preferred_reading_duration
    )

    # 如果用户提交了资料，则标记为已完成
    user.is_profile_complete = True  # 假设提交此接口即视为完成资料

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "User profile updated successfully!",
                    "is_profile_complete": True,
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user profile: {e}")
        return (
            jsonify({"message": "Failed to update user profile due to server error"}),
            500,
        )


@app.route("/api/users/<int:user_id>/nickname", methods=["PUT"])
def update_nickname(user_id):
    """
    更新用户昵称。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    new_nickname = data.get("nickname")

    if not new_nickname:
        return jsonify({"message": "Nickname is required"}), 400

    # 在你的User模型中，nickname目前就是username
    # 如果你想区分，你需要给User模型添加一个nickname字段
    # 这里我们假设更新的是username作为nickname
    if (
        User.query.filter_by(username=new_nickname).first()
        and user.username != new_nickname
    ):
        return jsonify({"message": "Nickname already in use"}), 409

    try:
        user.username = new_nickname  # 更新 username
        db.session.commit()
        return (
            jsonify(
                {"message": "Nickname updated successfully!", "nickname": user.username}
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        print(f"Error updating nickname: {e}")
        return jsonify({"message": "Failed to update nickname"}), 500


@app.route("/api/users/<int:user_id>/avatar", methods=["POST"])
def upload_avatar(user_id):
    """
    上传用户头像。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if "avatar" not in request.files:
        return jsonify({"message": "No avatar file part in the request"}), 400

    file = request.files["avatar"]

    if file.filename == "":
        return jsonify({"message": "No selected avatar file"}), 400

    if file and allowed_file(file.filename):
        # 使用UUID生成唯一文件名，防止冲突
        filename = str(uuid.uuid4()) + "." + file.filename.rsplit(".", 1)[1].lower()
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        try:
            file.save(filepath)

            # 保存头像URL到数据库 (需要 User 模型有 avatar_url 字段)
            # 在 models.py User 模型中添加: avatar_url = db.Column(db.String(255), nullable=True)
            user.avatar_url = (
                f"/uploads/avatars/{filename}"  # 假设可以通过 /uploads/avatars/ 访问
            )
            db.session.commit()

            return (
                jsonify(
                    {
                        "message": "Avatar uploaded successfully!",
                        "avatar_url": user.avatar_url,
                    }
                ),
                200,
            )
        except Exception as e:
            db.session.rollback()
            print(f"Error saving avatar: {e}")
            return jsonify({"message": "Failed to upload avatar"}), 500
    else:
        return jsonify({"message": "File type not allowed"}), 400


# --- 提供上传的静态文件服务 ---
@app.route("/uploads/avatars/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# --- 假设的收藏管理路由 (需要对应数据库模型) ---
# 这些API需要你进一步定义数据库模型和业务逻辑
# 这里只是提供一个骨架，返回模拟数据


@app.route("/api/users/<int:user_id>/favorite_books", methods=["GET"])
def get_favorite_books(user_id):
    """
    获取用户收藏的图书列表。
    目前返回模拟数据。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # 实际应用中，你需要从数据库中查询该用户的收藏图书
    # 假设你有一个 FavoriteBook 模型，并与 User 关联
    # favorite_books = FavoriteBook.query.filter_by(user_id=user_id).all()
    # return jsonify([book.to_dict() for book in favorite_books]), 200

    # 模拟数据
    mock_books = [
        {
            "book_id": 1,
            "title": "Python编程从入门到实践",
            "author": "Eric Matthes",
            "cover_img": "https://via.placeholder.com/100x150?text=Python",
            "add_time": "2024-01-15T10:00:00Z",
            "rating": 5,
        },
        {
            "book_id": 2,
            "title": "深入理解JavaScript",
            "author": "Kyle Simpson",
            "cover_img": "https://via.placeholder.com/100x150?text=JS",
            "add_time": "2024-02-20T14:30:00Z",
            "rating": 4,
        },
    ]
    return jsonify(mock_books), 200


@app.route("/api/users/<int:user_id>/favorite_reviews", methods=["GET"])
def get_favorite_reviews(user_id):
    """
    获取用户收藏的书评列表。
    目前返回模拟数据。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # 实际应用中，你需要从数据库中查询该用户的收藏书评
    # 假设你有一个 FavoriteReview 模型，并与 User 关联
    # favorite_reviews = FavoriteReview.query.filter_by(user_id=user_id).all()
    # return jsonify([review.to_dict() for review in favorite_reviews]), 200

    # 模拟数据
    mock_reviews = [
        {
            "review_id": 101,
            "book_auther": "Eric Matthes",
            "book_title": "Python编程从入门到实践",
            "title": "非常实用的Python入门书籍",
            "content": "这本书深入浅出，非常适合初学者，跟着例子一步步做很有成就感。",
            "rating": 5,
            "like_count": 25,
            "add_time": "2024-03-01T09:15:00Z",
        },
        {
            "review_id": 102,
            "book_title": "深入理解JavaScript",
            "book_auther": "Kyle Simpson",
            "title": "JavaScript的深度解析",
            "content": "对于JavaScript的高级概念讲解得很透彻，需要反复阅读。",
            "rating": 4,
            "like_count": 12,
            "add_time": "2024-04-10T11:45:00Z",
        },
    ]
    return jsonify(mock_reviews), 200


@app.route("/api/users/<int:user_id>/favorite_books/<int:book_id>", methods=["DELETE"])
def remove_favorite_book(user_id, book_id):
    """
    从用户收藏中移除一本图书。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # 实际应用中，执行删除收藏图书的逻辑
    # favorite_book = FavoriteBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    # if favorite_book:
    #     db.session.delete(favorite_book)
    #     db.session.commit()
    #     return jsonify({'message': 'Book removed from favorites successfully'}), 200
    # else:
    #     return jsonify({'message': 'Favorite book not found'}), 404

    print(f"DEBUG: Attempting to remove book {book_id} for user {user_id}")
    # 模拟删除成功
    return jsonify({"message": "Book removed from favorites (simulated)"}), 200


@app.route(
    "/api/users/<int:user_id>/favorite_reviews/<int:review_id>", methods=["DELETE"]
)
def remove_favorite_review(user_id, review_id):
    """
    从用户收藏中移除一条书评。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # 实际应用中，执行删除收藏书评的逻辑
    # favorite_review = FavoriteReview.query.filter_by(user_id=user_id, review_id=review_id).first()
    # if favorite_review:
    #     db.session.delete(favorite_review)
    #     db.session.commit()
    #     return jsonify({'message': 'Review removed from favorites successfully'}), 200
    # else:
    #     return jsonify({'message': 'Favorite review not found'}), 404

    print(f"DEBUG: Attempting to remove review {review_id} for user {user_id}")
    # 模拟删除成功
    return jsonify({"message": "Review removed from favorites (simulated)"}), 200


# --- 用户管理接口（整合自 user_routes.py） ---


@app.route("/api/users", methods=["GET"])
def get_users():
    """获取所有用户，支持搜索和分页"""
    try:
        search_keyword = request.args.get("search", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)

        result, error = UserModel.get_all_users(
            search_keyword=search_keyword if search_keyword else None,
            page=page,
            per_page=per_page,
        )

        if error:
            return jsonify({"error": error}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve users: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """获取单个用户信息"""
    try:
        user, error = UserModel.get_user_by_id(user_id)
        if error:
            if error == "User not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500

        return jsonify(user)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve user: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """更新用户信息"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        forbidden_fields = ["id", "password_hash"]
        update_data = {
            k: v
            for k, v in data.items()
            if v is not None and v != "" and k not in forbidden_fields
        }

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        updated_user, error = UserModel.update_user(user_id, update_data)
        if error:
            if error == "User not found":
                return jsonify({"error": error}), 404
            if "already exists" in error:
                return jsonify({"error": error}), 409
            return jsonify({"error": error}), 500

        return jsonify(updated_user)

    except Exception as e:
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """删除用户"""
    try:
        success, error = UserModel.delete_user(user_id)
        if error:
            if error == "User not found":
                return jsonify({"error": error}), 404
            return jsonify({"error": error}), 500

        return jsonify({"message": "User deleted successfully", "userId": user_id})

    except Exception as e:
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500


@app.route("/api/users", methods=["POST"])
def create_user():
    """创建新用户"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        user, error = UserModel.create_user(
            username=data["username"], email=data["email"], password=data["password"]
        )

        if error:
            if "already exists" in error:
                return jsonify({"error": error}), 409
            return jsonify({"error": error}), 500

        return jsonify(user), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
