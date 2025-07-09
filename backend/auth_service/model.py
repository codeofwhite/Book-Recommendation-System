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
    
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url
        }

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
                        User.email.like(search_pattern)
                    )
                )
            
            # 分页
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            users = [user.to_dict() for user in pagination.items]
            
            return {
                'users': users,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }, None
            
        except Exception as e:
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
            user = User(
                username=username,
                email=email,
                password=password
            )
            
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
            allowed_fields = ['username', 'email', 'avatar_url']
            
            for field, value in update_data.items():
                if field in allowed_fields and hasattr(user, field):
                    # 检查用户名和邮箱的唯一性
                    if field == 'username' and value != user.username:
                        if User.query.filter_by(username=value).first():
                            return None, "Username already exists"
                    
                    if field == 'email' and value != user.email:
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
