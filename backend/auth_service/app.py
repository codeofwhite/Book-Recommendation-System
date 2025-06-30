# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # 用于处理跨域请求
from models import db, bcrypt, User, Admin
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 初始化 SQLAlchemy 和 Bcrypt
db.init_app(app)
bcrypt.init_app(app)

# 允许跨域请求，例如你的 Vue 应用在不同端口
CORS(app)

# 确保在应用上下文中使用 db.create_all() 来创建表
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "Hello from Flask API!"

# --- 认证路由 ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing username, email, or password'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409 # Conflict
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 409 # Conflict

    try:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully!'}), 201 # Created
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {e}")
        return jsonify({'message': 'Registration failed due to server error'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    # User could be found by username or email.
    # The frontend is sending 'username' which could be either in your current setup.
    # Let's try to find by username first, then by email if not found.
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User.query.filter_by(email=username).first() # Try finding by email if username not found

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401 # Unauthorized

    # If login is successful, prepare the user data to send back
    # In a real application, you'd generate a JWT token here.
    # For now, we'll use a dummy token as you have.
    # You might also want a 'nickname' field in your User model,
    # but for now, we'll just use the username as a nickname.
    
    # --- IMPORTANT: ADD THESE FIELDS TO THE RESPONSE ---
    return jsonify({
        'message': 'Login successful',
        'token': 'dummy_token_for_now', # Replace with real JWT later
        'user_id': user.id,            # Get the user's ID
        'nickname': user.username,     # Using username as nickname for now (consider adding a 'nickname' column)
        'email': user.email,           # Get the user's email
        'avatar_url': 'https://via.placeholder.com/150' # Provide a default or actual avatar URL
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True 在开发环境使用