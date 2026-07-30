from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, timezone
import jwt
import os
import re
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import hashlib
import secrets

load_dotenv()

app = Flask(__name__)

# ========== SECURE CORS CONFIGURATION ==========
ALLOWED_ORIGINS = [
    "https://health-chatbot-delta.vercel.app",
    "https://health-chatbot-git-main-shanmukhpranays-projects.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000"
]

CORS(app, resources={r"/*": {
    "origins": ALLOWED_ORIGINS,
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "expose_headers": ["Content-Type"],
    "max_age": 3600
}})

# SocketIO with secure settings
socketio = SocketIO(app, 
                    cors_allowed_origins=ALLOWED_ORIGINS,
                    async_mode='threading',
                    ping_timeout=60,
                    ping_interval=25,
                    max_http_buffer_size=1e6)  # 1MB max message size

# ========== SECURE CONFIGURATION ==========
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
JWT_EXPIRY_HOURS = 24
RATE_LIMIT_REQUESTS = 60  # Max requests per minute
RATE_LIMIT_WINDOW = 60  # Window in seconds
MAX_MESSAGE_LENGTH = 500  # Max characters per message
MAX_USERNAME_LENGTH = 50
MAX_EMAIL_LENGTH = 120

# In-memory storage (replace with database in production)
users = []
chats = []
rate_limit_store = {}

# ========== HELPER FUNCTIONS ==========

def rate_limit_check(ip_address):
    """Rate limiting to prevent brute force attacks"""
    now = datetime.now(timezone.utc).timestamp()
    if ip_address not in rate_limit_store:
        rate_limit_store[ip_address] = []
    
    # Clean old requests
    rate_limit_store[ip_address] = [
        req_time for req_time in rate_limit_store[ip_address] 
        if now - req_time < RATE_LIMIT_WINDOW
    ]
    
    if len(rate_limit_store[ip_address]) >= RATE_LIMIT_REQUESTS:
        return False
    
    rate_limit_store[ip_address].append(now)
    return True

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None and len(email) <= MAX_EMAIL_LENGTH

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def sanitize_input(text, max_length=MAX_MESSAGE_LENGTH):
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Limit length
    text = text[:max_length]
    return text.strip()

def create_auth_token(email):
    """Create secure JWT token with more claims"""
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        'iat': datetime.now(timezone.utc),
        'iss': 'health-chatbot-api'
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]  # FIXED: Using double quotes
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Verify token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'], issuer='health-chatbot-api')
            current_user = find_user_by_email(data['email'])
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            if not current_user.get('is_active', True):
                return jsonify({'error': 'Account is deactivated'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def find_user_by_email(email):
    for user in users:
        if user['email'].lower() == email.lower():
            return user
    return None

# ========== API ROUTES ==========

@app.route('/')
def home():
    return jsonify({
        'status': 'success', 
        'message': 'Health Assistant API is running!',
        'version': '2.0.0',
        'secure': True
    })

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Rate limiting
    client_ip = request.remote_addr
    if not rate_limit_check(client_ip):
        return jsonify({'error': 'Too many requests. Please try again later.'}), 429
    
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        password = data.get('password', '')
        
        # Validate email
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate name
        if not name or len(name) < 2:
            return jsonify({'error': 'Name must be at least 2 characters'}), 400
        if len(name) > MAX_USERNAME_LENGTH:
            return jsonify({'error': f'Name must be less than {MAX_USERNAME_LENGTH} characters'}), 400
        
        # Validate password
        is_valid, password_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': password_msg}), 400
        
        # Check if user exists
        if find_user_by_email(email):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user_id = len(users) + 1
        new_user = {
            'id': user_id,
            'email': email,
            'name': sanitize_input(name),
            'password_hash': generate_password_hash(password, method='pbkdf2:sha256'),
            'role': 'Admin' if email == "2300031563@kluniversity" else 'Regular User',
            'avatar': name[0].upper(),
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_login': None,
            'preferences': {}
        }
        users.append(new_user)
        
        token = create_auth_token(email)
        
        print(f"🆕 NEW USER REGISTERED: {email} | Name: {name} | Role: {new_user['role']}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user_id,
                'email': email,
                'name': new_user['name'],
                'role': new_user['role'],
                'avatar': new_user['avatar'],
                'is_active': True
            },
            'token': token
        }), 201
        
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Rate limiting
    client_ip = request.remote_addr
    if not rate_limit_check(client_ip):
        return jsonify({'error': 'Too many login attempts. Please try again later.'}), 429
    
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = find_user_by_email(email)
        
        if not user:
            # Don't reveal that user doesn't exist for security
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated. Contact support.'}), 403
        
        # Update last login
        user['last_login'] = datetime.now(timezone.utc).isoformat()
        
        token = create_auth_token(email)
        
        print(f"✅ User logged in: {email}")
        
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
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'users': len(users),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/admin/users-list', methods=['GET'])
def get_users_list():
    """Get all registered users (protected in production)"""
    # In production, add authentication here
    
    user_list = [{
        'id': u['id'],
        'email': u['email'],
        'name': u['name'],
        'role': u['role'],
        'avatar': u['avatar'],
        'is_active': u['is_active'],
        'created_at': u.get('created_at', 'N/A'),
        'last_login': u.get('last_login', 'Never')
    } for u in users]
    
    return jsonify({
        'users': user_list,
        'count': len(user_list),
        'admins': len([u for u in users if u['role'] == 'Admin']),
        'regular_users': len([u for u in users if u['role'] == 'Regular User'])
    })

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile - requires authentication"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user['id'],
            'email': current_user['email'],
            'name': current_user['name'],
            'role': current_user['role'],
            'avatar': current_user['avatar'],
            'created_at': current_user.get('created_at'),
            'last_login': current_user.get('last_login')
        }
    })

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile - requires authentication"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if name and len(name) >= 2:
            current_user['name'] = sanitize_input(name)
            current_user['avatar'] = name[0].upper()
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'name': current_user['name'],
                    'avatar': current_user['avatar']
                }
            })
        
        return jsonify({'error': 'Invalid name'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/user/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change user password - requires authentication"""
    try:
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        # Verify old password
        if not check_password_hash(current_user['password_hash'], old_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        is_valid, password_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': password_msg}), 400
        
        # Update password
        current_user['password_hash'] = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout user (client should discard token)"""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

# ========== SOCKET.IO WITH SECURITY ==========
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to secure server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('user_connected')
def handle_user_connected(data):
    user_name = sanitize_input(data.get('userName', 'User'), 50)
    print(f'User connected: {user_name}')
    emit('bot_response', {'message': 'Hello! How can I help you today?'})

@socketio.on('user_message')
def handle_user_message(data):
    msg = sanitize_input(data.get('message', ''))
    print(f'Message received: {msg[:50]}')
    
    emit('bot_typing', {})
    
    # Generate secure response
    response = generate_secure_response(msg)
    emit('bot_response', {'message': response})

def generate_secure_response(msg):
    """Generate secure response based on user message"""
    msg_lower = msg.lower()
    
    if 'fever' in msg_lower:
        return "🌡️ **Fever Treatment**: Rest, drink fluids, and take paracetamol. See a doctor if fever > 103°F or lasts more than 3 days."
    elif 'headache' in msg_lower:
        return "🤕 **Headache Relief**: Rest in a dark room, drink water, and try over-the-counter pain relievers."
    elif 'hello' in msg_lower or 'hi' in msg_lower:
        return "Hello! I'm your secure Health Assistant. How can I help you today?"
    else:
        return f"I received your message. I can help with fever, headache, and general health questions. How can I assist you?"

# ========== INITIALIZE DEMO DATA ==========
if not find_user_by_email("demo@example.com"):
    demo_user = {
        'id': 1,
        'email': "demo@example.com",
        'name': "Demo User",
        'password_hash': generate_password_hash("demo123", method='pbkdf2:sha256'),
        'role': "Regular User",
        'avatar': "D",
        'is_active': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'last_login': None,
        'preferences': {}
    }
    users.append(demo_user)
    print("✅ Demo user created: demo@example.com / demo123")

if not find_user_by_email("2300031563@kluniversity"):
    admin_user = {
        'id': 2,
        'email': "2300031563@kluniversity",
        'name': "Admin User",
        'password_hash': generate_password_hash("Admin@123", method='pbkdf2:sha256'),
        'role': "Admin",
        'avatar': "A",
        'is_active': True,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'last_login': None,
        'preferences': {}
    }
    users.append(admin_user)
    print("✅ Admin user created: 2300031563@kluniversity / Admin@123")

print(f"📊 Total users: {len(users)}")
print("🔒 Security features enabled: Rate limiting, Input sanitization, Password validation")

# ========== MAIN ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)