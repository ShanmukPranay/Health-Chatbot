from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, timezone
import jwt
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CORS - Allow all for now
CORS(app, resources={r"/*": {"origins": "*"}})

# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "test-secret-key")
JWT_EXPIRY_HOURS = 24

# Database - Use SQLite for simplicity first
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"✅ Using PostgreSQL")
else:
    DATABASE_URL = "sqlite:///health_ai.db"
    print(f"✅ Using SQLite")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========== DATABASE MODELS ==========
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='Regular User')
    avatar = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'avatar': self.avatar or self.name[0].upper(),
            'is_active': self.is_active
        }

class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_id = db.Column(db.String(100))
    user_message = db.Column(db.Text)
    bot_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# ========== HELPER FUNCTIONS ==========
def create_auth_token(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# ========== API ROUTES ==========
@app.route('/')
def home():
    return jsonify({'status': 'success', 'message': 'API is running!'})

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        
        if not email or not name or not password:
            return jsonify({'error': 'All fields required'}), 400
        
        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Only admin email gets Admin role
        if email == "2300031563@kluniversity":
            role = "Admin"
        else:
            role = "Regular User"
        
        new_user = User(
            email=email,
            name=name,
            role=role,
            avatar=name[0].upper(),
            is_active=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        token = create_auth_token(email)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': new_user.to_dict(),
            'token': token
        })
        
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            token = create_auth_token(email)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': token
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

# ========== SOCKET.IO ==========
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('user_connected')
def handle_user_connected(data):
    print(f'User: {data.get("userName")}')
    emit('bot_response', {'message': 'Hello! How can I help you today?'})

@socketio.on('user_message')
def handle_user_message(data):
    msg = data.get('message', '')
    print(f'Message: {msg[:50]}')
    emit('bot_typing', {})
    emit('bot_response', {'message': f'I received: "{msg[:100]}". How can I help with your health?'})

# ========== INIT DATABASE ==========
def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database created")
        
        # Create demo user
        if not User.query.filter_by(email="demo@example.com").first():
            demo = User(email="demo@example.com", name="Demo User", role="Regular User", avatar="D")
            demo.set_password("demo123")
            db.session.add(demo)
            db.session.commit()
            print("✅ Demo user created")

# ========== MAIN ==========
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)