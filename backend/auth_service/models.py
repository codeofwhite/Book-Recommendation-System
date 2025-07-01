# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users' # 定义表名
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # 存储哈希后的密码
    avatar_url = db.Column(db.String(255), nullable=True, default='https://via.placeholder.com/150') 
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

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