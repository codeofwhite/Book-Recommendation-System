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