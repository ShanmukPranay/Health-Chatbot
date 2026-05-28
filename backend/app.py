from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc, text
import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ========== CORS CONFIGURATION - Allow all origins for Render ==========
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:5173", "https://health-chatbot-delta.vercel.app", "https://health-chatbot-backend-w4dl.onrender.com"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}})

# ========== SOCKET.IO CONFIGURATION ==========
socketio = SocketIO(app, 
                    cors_allowed_origins="*", 
                    async_mode='threading',
                    ping_timeout=60,
                    ping_interval=25)

# Store active connections
active_connections = {}

# ========== CONFIGURATION ==========
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "health-ai-assistant-secret-key-2024")
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", 24))

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///health_ai.db"
    print("⚠️ Using SQLite (development mode)")
else:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"✅ Using PostgreSQL database")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Application Settings
APP_NAME = os.environ.get("APP_NAME", "Health & AI Assistant")
APP_URL = os.environ.get("APP_URL", "https://health-chatbot-delta.vercel.app")
API_URL = os.environ.get("API_URL", "https://health-chatbot-backend-w4dl.onrender.com")
DEBUG_MODE = os.environ.get("DEBUG", "False").lower() == "true"

# Admin Settings
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "2300031563@kluniversity")
ADMIN_NAME = os.environ.get("ADMIN_NAME", "Admin User")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")

db = SQLAlchemy(app)

# ========== KNOWLEDGE BASE ==========
knowledge_base = {
    "health": {
        "fever": "🌡️ **Fever Treatment**:\n• Rest and sleep\n• Drink plenty of fluids\n• Take paracetamol or ibuprofen as directed\n• Use cool compresses\n\n⚠️ **See a doctor if:**\n- Fever > 103°F (39.4°C)\n- Lasts more than 3 days\n- Difficulty breathing",
        "headache": "🤕 **Headache Relief**:\n• Rest in a dark, quiet room\n• Apply cold compress\n• Drink plenty of water\n• Try OTC pain relievers",
        "cough": "🤧 **Cough Remedies**:\n• Drink warm liquids (honey lemon tea)\n• Use a humidifier\n• Gargle with salt water\n• Avoid irritants",
        "cold": "😷 **Cold & Flu Care**:\n• Rest and stay hydrated\n• Vitamin C supplements\n• Warm salt water gargle\n• Chicken soup",
        "stress": "🧠 **Stress Management**:\n• Deep breathing exercises\n• Regular exercise (30 min daily)\n• Meditation\n• Adequate sleep (7-9 hours)",
        "diabetes": "🩸 **Diabetes Care**:\n• Monitor blood sugar regularly\n• Balanced diet (low sugar, high fiber)\n• Regular exercise\n• Take medications as prescribed",
        "covid": "🦠 **COVID-19 Care**:\n• Isolate for 5 days\n• Rest and stay hydrated\n• Monitor oxygen levels\n• Take paracetamol for fever\n\n🚑 **Emergency signs:**\n- Difficulty breathing\n- Chest pain\n- Oxygen < 94%"
    },
    "text_analytics": {
        "introduction": "📚 **Introduction to Text Analytics**\n\nExtracting meaningful information from unstructured text using computational methods.\n\n**Applications:** Customer feedback analysis, Medical report analysis, Social media monitoring",
        "preprocessing": "🔧 **Text Preprocessing Techniques**\n\n1. Tokenization\n2. Stop-word Removal\n3. Stemming & Lemmatization\n4. Case Normalization",
        "representation": "📊 **Text Representation Models**\n\n1. Bag-of-Words (BoW)\n2. TF-IDF\n3. Word Embeddings (Word2Vec, GloVe, BERT)",
        "ner": "🏷️ **Named Entity Recognition (NER)**\n\nIdentifies: Persons, Organizations, Locations, Dates, Monetary values",
        "sentiment": "😊 **Sentiment Analysis**\n\nDetermines emotional tone (positive, negative, neutral)"
    },
    "general": {
        "greeting": "👋 **Welcome to Health & Text Analytics Assistant!**\n\nI can help you with:\n\n🏥 **Health Issues:** Fever, headache, cough, cold, stress, diabetes, COVID-19\n📚 **Text Analytics & NLP:** Introduction, preprocessing, NER, sentiment analysis\n\nHow can I help you today?",
        "help": "ℹ️ Try asking:\n• 'fever treatment'\n• 'headache relief'\n• 'what is NER?'\n• 'sentiment analysis'",
        "code": "💻 **Python Code Example for NLP**\n\n```python\nfrom textblob import TextBlob\n\ndef analyze_sentiment(text):\n    blob = TextBlob(text)\n    sentiment = blob.sentiment.polarity\n    if sentiment > 0: return 'Positive 😊'\n    elif sentiment < 0: return 'Negative 😞'\n    else: return 'Neutral 😐'\n```"
    }
}

# ========== DATABASE MODELS ==========

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='Regular User')
    avatar = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'Admin'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'avatar': self.avatar or self.name[0].upper(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OTP(db.Model):
    __tablename__ = 'otp'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(50), default='password_reset')
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    email = db.Column(db.String(120))
    rating = db.Column(db.Integer)
    message = db.Column(db.Text)
    feedback_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# ========== HELPER FUNCTIONS ==========

def create_auth_token(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(email=data['email']).first()
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            if not current_user.is_active:
                return jsonify({'error': 'Account deactivated'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def generate_bot_response(user_message, user_name="User"):
    msg = user_message.lower().strip()
    
    if 'fever' in msg:
        return knowledge_base["health"]["fever"]
    elif 'headache' in msg:
        return knowledge_base["health"]["headache"]
    elif 'cough' in msg:
        return knowledge_base["health"]["cough"]
    elif 'cold' in msg or 'flu' in msg:
        return knowledge_base["health"]["cold"]
    elif 'stress' in msg or 'anxiety' in msg:
        return knowledge_base["health"]["stress"]
    elif 'diabet' in msg or 'sugar' in msg:
        return knowledge_base["health"]["diabetes"]
    elif 'covid' in msg or 'corona' in msg:
        return knowledge_base["health"]["covid"]
    elif 'text analytics' in msg or 'nlp' in msg:
        if 'intro' in msg:
            return knowledge_base["text_analytics"]["introduction"]
        elif 'preprocess' in msg:
            return knowledge_base["text_analytics"]["preprocessing"]
        elif 'represent' in msg or 'tfidf' in msg:
            return knowledge_base["text_analytics"]["representation"]
        elif 'ner' in msg:
            return knowledge_base["text_analytics"]["ner"]
        elif 'sentiment' in msg:
            return knowledge_base["text_analytics"]["sentiment"]
        else:
            return knowledge_base["text_analytics"]["introduction"]
    elif 'code' in msg or 'example' in msg:
        return knowledge_base["general"]["code"]
    elif any(word in msg for word in ['hello', 'hi', 'hey']):
        return knowledge_base["general"]["greeting"]
    elif 'help' in msg:
        return knowledge_base["general"]["help"]
    else:
        return f"Thanks for your message! I'm here to help with health issues and text analytics.\n\n💡 Try asking:\n• 'fever treatment'\n• 'what is NER?'\n• 'sentiment analysis'"

# ========== SOCKET.IO EVENT HANDLERS ==========

@socketio.on('connect')
def handle_connect():
    print(f'🔌 Client connected: {request.sid}')
    active_connections[request.sid] = {
        'user_id': None,
        'user_name': None,
        'connected_at': datetime.now(timezone.utc)
    }
    emit('connected', {'message': 'Connected to server', 'socket_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'🔌 Client disconnected: {request.sid}')
    if request.sid in active_connections:
        del active_connections[request.sid]

@socketio.on('user_connected')
def handle_user_connected(data):
    print(f'👤 User connected: {data.get("userName")}')
    if request.sid in active_connections:
        active_connections[request.sid]['user_id'] = data.get('userId')
        active_connections[request.sid]['user_name'] = data.get('userName')
    
    welcome_msg = generate_bot_response("hello", data.get('userName', 'User'))
    emit('bot_response', {'message': welcome_msg})

@socketio.on('user_message')
def handle_user_message(data):
    user_message = data.get('message', '')
    user_name = data.get('userName', 'User')
    
    print(f'📨 Message from {user_name}: {user_message[:50]}...')
    
    emit('bot_typing', {}, room=request.sid)
    bot_response = generate_bot_response(user_message, user_name)
    emit('bot_response', {'message': bot_response}, room=request.sid)

# ========== DATABASE INITIALIZATION ==========

def init_database():
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Create admin user
            admin_user = User.query.filter_by(email=ADMIN_EMAIL).first()
            if not admin_user:
                admin_user = User(
                    email=ADMIN_EMAIL,
                    name=ADMIN_NAME,
                    role='Admin',
                    avatar='A',
                    is_active=True
                )
                admin_user.set_password(ADMIN_PASSWORD)
                db.session.add(admin_user)
                print(f"✅ Admin user created: {ADMIN_EMAIL}")
            
            # Create demo user
            demo_user = User.query.filter_by(email="demo@example.com").first()
            if not demo_user:
                demo_user = User(
                    email="demo@example.com",
                    name="Demo User",
                    role='Regular User',
                    avatar='D',
                    is_active=True
                )
                demo_user.set_password("demo123")
                db.session.add(demo_user)
                print("✅ Demo user created: demo@example.com")
            
            db.session.commit()
            print("✅ Database initialization complete")
            
        except Exception as e:
            print(f"❌ Database init failed: {str(e)}")
            db.session.rollback()

# ========== API ROUTES ==========

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": f"{APP_NAME} API with Socket.IO is running!",
        "websocket": "enabled",
        "version": "2.0.0"
    })

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
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403
            
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            token = create_auth_token(email)
            
            print(f"✅ Login successful: {email} (Role: {user.role})")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': token
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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
        
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Role assignment - ONLY admin email gets Admin role
        if email == ADMIN_EMAIL:
            role = "Admin"
            print(f"👑 Admin user registering: {email}")
        else:
            role = "Regular User"
            print(f"👤 Regular user registering: {email}")
        
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
        db.session.rollback()
        print(f"❌ Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'app': APP_NAME,
        'websocket': 'enabled',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

# ========== MAIN ==========
if __name__ == "__main__":
    print("=" * 70)
    print(f"🚀 Starting {APP_NAME} API Server with WebSocket...")
    print("=" * 70)
    print(f"👑 ADMIN: {ADMIN_EMAIL}")
    print(f"👤 DEMO: demo@example.com / demo123")
    print(f"🌐 Frontend URL: {APP_URL}")
    print(f"🔧 API URL: {API_URL}")
    print("=" * 70)
    print("✅ Socket.IO enabled - Real-time chat active!")
    print("=" * 70)
    
    init_database()
    
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=DEBUG_MODE,
        allow_unsafe_werkzeug=True
    )