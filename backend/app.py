from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, timezone
import jwt
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CORS - Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "test-secret-key")
JWT_EXPIRY_HOURS = 24

# In-memory database (for testing)
users = []
chats = []

# Helper functions
def create_auth_token(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def find_user_by_email(email):
    for user in users:
        if user['email'] == email:
            return user
    return None

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
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        if find_user_by_email(email):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user_id = len(users) + 1
        new_user = {
            'id': user_id,
            'email': email,
            'name': name,
            'password_hash': generate_password_hash(password),
            'role': 'Admin' if email == "2300031563@kluniversity" else 'Regular User',
            'avatar': name[0].upper(),
            'is_active': True
        }
        users.append(new_user)
        
        token = create_auth_token(email)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'role': new_user['role'],
                'avatar': new_user['avatar'],
                'is_active': True
            },
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
        
        user = find_user_by_email(email)
        
        if user and check_password_hash(user['password_hash'], password):
            token = create_auth_token(email)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'role': user['role'],
                    'avatar': user['avatar'],
                    'is_active': user['is_active']
                },
                'token': token
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'users': len(users)})

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
    
    # Simple responses
    if 'fever' in msg.lower():
        response = "🌡️ **Fever Treatment**: Rest, drink fluids, and take paracetamol. See a doctor if fever > 103°F or lasts more than 3 days."
    elif 'headache' in msg.lower():
        response = "🤕 **Headache Relief**: Rest in a dark room, drink water, and try over-the-counter pain relievers."
    elif 'hello' in msg.lower() or 'hi' in msg.lower():
        response = "Hello! I'm your Health Assistant. How can I help you today?"
    else:
        response = f"I received your message. I can help with fever, headache, and general health questions. How can I assist you?"
    
    emit('bot_response', {'message': response})

# ========== INITIALIZE DEMO DATA ==========
# Create demo user
if not find_user_by_email("demo@example.com"):
    demo_user = {
        'id': 1,
        'email': "demo@example.com",
        'name': "Demo User",
        'password_hash': generate_password_hash("demo123"),
        'role': "Regular User",
        'avatar': "D",
        'is_active': True
    }
    users.append(demo_user)
    print("✅ Demo user created: demo@example.com / demo123")

# Create admin user
if not find_user_by_email("2300031563@kluniversity"):
    admin_user = {
        'id': 2,
        'email': "2300031563@kluniversity",
        'name': "Admin User",
        'password_hash': generate_password_hash("Admin@123"),
        'role': "Admin",
        'avatar': "A",
        'is_active': True
    }
    users.append(admin_user)
    print("✅ Admin user created: 2300031563@kluniversity / Admin@123")

print(f"📊 Total users: {len(users)}")

# ========== MAIN ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)