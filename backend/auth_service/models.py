from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func # 导入 func 用于获取当前时间

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users' # 定义表名
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # 存储哈希后的密码
    avatar_url = db.Column(db.String(255), nullable=True, default='https://th.bing.com/th/id/OIP.cTPVthB0oT1RXrEcSHaaTwHaHa?w=191&h=191&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3')

    # --- 新增字段 ---
    registration_date = db.Column(db.DateTime, nullable=False, default=func.now()) # 注册时间，自动设置为当前时间
    last_login_date = db.Column(db.DateTime, nullable=True) # 最后登录时间，首次登录时可为空
    
    # 用户属性数据 (来自问卷)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True) # 例如 'male', 'female', 'other'
    location = db.Column(db.String(100), nullable=True) # 例如 'Taipei', 'Kaohsiung'
    occupation = db.Column(db.String(100), nullable=True)

    # 用户偏好/兴趣信息 (来自问卷，使用Text类型存储逗号分隔的字符串或JSON字符串)
    interest_tags = db.Column(db.Text, nullable=True) # 例如 'fantasy,sci-fi,history'
    preferred_book_types = db.Column(db.Text, nullable=True) # 例如 'fiction,non-fiction'
    preferred_authors = db.Column(db.Text, nullable=True) # 例如 'J.K. Rowling,George R.R. Martin'
    preferred_genres = db.Column(db.Text, nullable=True) # 例如 'mystery,thriller'
    preferred_reading_duration = db.Column(db.String(50), nullable=True) # 例如 'short', 'medium', 'long'

    # 标记用户是否已完成资料填写 (用于引导问卷)
    is_profile_complete = db.Column(db.Boolean, nullable=False, default=False)
    # --- 新增字段结束 ---
     
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        # registration_date 会由 default=func.now() 自动设置

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    # --- 添加 to_dict 方法 ---
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            # 'password_hash': self.password_hash, # 通常不应该将哈希密码返回到前端
            'avatar_url': self.avatar_url,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'last_login_date': self.last_login_date.isoformat() if self.last_login_date else None,
            'age': self.age,
            'gender': self.gender,
            'location': self.location,
            'occupation': self.occupation,
            'interest_tags': self.interest_tags,
            'preferred_book_types': self.preferred_book_types,
            'preferred_authors': self.preferred_authors,
            'preferred_genres': self.preferred_genres,
            'preferred_reading_duration': self.preferred_reading_duration,
            'is_profile_complete': self.is_profile_complete
        }
    # --- to_dict 方法结束 ---

# --- 添加 ADMIN 模型 ---
class Admin(db.Model):
    __tablename__ = 'ADMIN' # 确保表名与你的SQL创建语句一致
    admin_id = db.Column(db.String(20), primary_key=True, comment='管理员账号')
    password = db.Column(db.CHAR(64), nullable=False, comment='密码') # 存储哈希后的密码
    verification_info = db.Column(db.Text, comment='验证信息')

    def __init__(self, admin_id, raw_password, verification_info=None):
        self.admin_id = admin_id
        # 使用 bcrypt 对密码进行哈希
        self.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')
        self.verification_info = verification_info

    def check_password(self, raw_password):
        # 验证密码
        return bcrypt.check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f'<Admin {self.admin_id}>'
    
class UserModel:
    """用户管理的业务逻辑类"""

    @staticmethod
    def get_all_users(search_keyword=None, page=1, per_page=10):
        """获取所有用户，支持搜索和分页"""
        try:
            query = User.query

            if search_keyword:
                search_pattern = f"%{search_keyword}%"
                query = query.filter(
                    db.or_(
                        User.username.like(search_pattern),
                        User.email.like(search_pattern),
                    )
                )

            # 分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            users = [user.to_dict() for user in pagination.items]

            return {
                "users": users,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "per_page": per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }, None

        except Exception as e:
            # 这里的 print 语句只打印到控制台，如果需要写入文件或更持久的日志，请使用 logging 模块
            print(f"Error fetching users: {e}")
            return None, str(e)

    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        try:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), None
            return None, "User not found"
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None, str(e)

    @staticmethod
    def create_user(username, email, password):
        """创建新用户"""
        try:
            # 检查用户名和邮箱是否已存在
            if User.query.filter_by(username=username).first():
                return None, "Username already exists"

            if User.query.filter_by(email=email).first():
                return None, "Email already exists"

            # 创建新用户
            user = User(username=username, email=email, password=password)

            db.session.add(user)
            db.session.commit()

            return user.to_dict(), None

        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")
            return None, str(e)

    @staticmethod
    def update_user(user_id, update_data):
        """更新用户信息"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"

            # 更新允许的字段
            allowed_fields = ["username", "email", "avatar_url"]

            for field, value in update_data.items():
                if field in allowed_fields and hasattr(user, field):
                    # 检查用户名和邮箱的唯一性
                    if field == "username" and value != user.username:
                        if User.query.filter_by(username=value).first():
                            return None, "Username already exists"

                    if field == "email" and value != user.email:
                        if User.query.filter_by(email=value).first():
                            return None, "Email already exists"

                    setattr(user, field, value)

            db.session.commit()

            return user.to_dict(), None

        except Exception as e:
            db.session.rollback()
            print(f"Error updating user: {e}")
            return None, str(e)

    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            db.session.delete(user)
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting user: {e}")
            return False, str(e)