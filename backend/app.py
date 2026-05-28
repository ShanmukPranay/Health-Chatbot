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
import sqlite3

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ========== GET CONFIGURATION FROM .ENV ==========
HOST_IP = os.environ.get("HOST_IP", "127.0.0.1")
FRONTEND_PORT = os.environ.get("FRONTEND_PORT", "5173")
BACKEND_PORT = os.environ.get("BACKEND_PORT", "5000")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5000").split(',')

# ========== CORS CONFIGURATION ==========
CORS(app, resources={r"/*": {
    "origins": ALLOWED_ORIGINS,
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
    "supports_credentials": True,
    "expose_headers": ["Content-Type", "Authorization"]
}})

# ========== SOCKET.IO CONFIGURATION ==========
socketio = SocketIO(app, 
                    cors_allowed_origins="*", 
                    async_mode='threading',
                    ping_timeout=60,
                    ping_interval=25,
                    logger=True,
                    engineio_logger=True)

# Store active connections
active_connections = {}

# ========== CONFIGURATION FROM .ENV ==========

# Security
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "health-ai-assistant-secret-key-2024-change-this-in-production")
OTP_EXPIRY_MINUTES = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))
TOKEN_EXPIRY_MINUTES = int(os.environ.get("TOKEN_EXPIRY_MINUTES", 15))
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", 24))

# ========== DATABASE CONFIGURATION (FIXED FOR SUPABASE) ==========
# Get DATABASE_URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# If no DATABASE_URL, use SQLite for development
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///health_ai.db"
    print("⚠️ DATABASE_URL not set. Using SQLite (development mode)")
    print("   For production, set DATABASE_URL environment variable")
else:
    # Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"✅ Using PostgreSQL database")

# Configure SQLAlchemy - REMOVED pool_size for Supabase compatibility
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Only add engine options for SQLite, not for Supabase PostgreSQL
if 'sqlite' in DATABASE_URL:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
else:
    # For Supabase/PostgreSQL, use minimal options (no pool_size)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True
    }
    print("✅ Supabase PostgreSQL detected - using compatible engine options")

# Email Configuration
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

# Application Settings
APP_NAME = os.environ.get("APP_NAME", "Health & AI Assistant")
APP_URL = os.environ.get("APP_URL", f"http://{HOST_IP}:{FRONTEND_PORT}")
API_URL = os.environ.get("API_URL", f"http://{HOST_IP}:{BACKEND_PORT}")
DEBUG_MODE = os.environ.get("DEBUG", "True").lower() == "true"

# Admin Settings
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "2300031563@kluniversity")
ADMIN_NAME = os.environ.get("ADMIN_NAME", "Admin User")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")

# Chat Settings
MAX_CHAT_HISTORY = int(os.environ.get("MAX_CHAT_HISTORY", 100))
CHAT_SESSION_TIMEOUT = int(os.environ.get("CHAT_SESSION_TIMEOUT", 30))
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 60))
RATE_LIMIT_PER_HOUR = int(os.environ.get("RATE_LIMIT_PER_HOUR", 1000))

# Initialize database
db = SQLAlchemy(app)

# ========== KNOWLEDGE BASE FOR CHATBOT ==========
knowledge_base = {
    "health": {
        "fever": "🌡️ **Fever Treatment**:\n• Rest and sleep\n• Drink plenty of fluids\n• Take paracetamol or ibuprofen as directed\n• Use cool compresses\n\n⚠️ **See a doctor if:**\n- Fever > 103°F (39.4°C)\n- Lasts more than 3 days\n- Difficulty breathing",
        
        "headache": "🤕 **Headache Relief**:\n• Rest in a dark, quiet room\n• Apply cold compress\n• Drink plenty of water\n• Try OTC pain relievers\n\n💊 **For migraines:** Avoid bright lights and loud noises",
        
        "cough": "🤧 **Cough Remedies**:\n• Drink warm liquids (honey lemon tea)\n• Use a humidifier\n• Gargle with salt water\n• Avoid irritants\n\n🏥 **See doctor if:**\n- Cough with blood\n- Lasts > 2 weeks\n- Difficulty breathing",
        
        "cold": "😷 **Cold & Flu Care**:\n• Rest and stay hydrated\n• Vitamin C supplements\n• Warm salt water gargle\n• Chicken soup\n\n⚠️ **Seek medical help if:**\n- High fever > 101°F\n- Symptoms worsen after 5 days",
        
        "stress": "🧠 **Stress Management**:\n• Deep breathing exercises\n• Regular exercise (30 min daily)\n• Meditation\n• Adequate sleep (7-9 hours)\n• Talk to friends/family",
        
        "diabetes": "🩸 **Diabetes Care**:\n• Monitor blood sugar regularly\n• Balanced diet (low sugar, high fiber)\n• Regular exercise\n• Take medications as prescribed\n\n📊 **Target blood sugar:** 80-130 mg/dL before meals",
        
        "covid": "🦠 **COVID-19 Care**:\n• Isolate for 5 days\n• Rest and stay hydrated\n• Monitor oxygen levels\n• Take paracetamol for fever\n\n🚑 **Emergency signs:**\n- Difficulty breathing\n- Chest pain\n- Oxygen < 94%"
    },
    
    "text_analytics": {
        "introduction": "📚 **Introduction to Text Analytics**\n\n**Definition:** Extracting meaningful information from unstructured text using computational methods.\n\n**Applications:**\n• Customer feedback analysis\n• Medical report analysis\n• Social media monitoring\n• Document classification",
        
        "preprocessing": "🔧 **Text Preprocessing Techniques**\n\n**1. Tokenization:** Splitting text into words\n**2. Stop-word Removal:** Removing common words (the, is, and)\n**3. Stemming:** Reducing words to root form ('running' → 'run')\n**4. Lemmatization:** Proper word reduction using dictionary\n**5. Case Normalization:** Convert to lowercase",
        
        "representation": "📊 **Text Representation Models**\n\n**1. Bag-of-Words (BoW):** Word frequency vectors\n**2. TF-IDF:** Term Frequency-Inverse Document Frequency\n**3. Word Embeddings:** Word2Vec, GloVe, BERT",
        
        "ner": "🏷️ **Named Entity Recognition (NER)**\n\nIdentifies entities in text:\n• **PERSON:** People's names\n• **ORG:** Organizations\n• **LOC:** Locations\n• **DATE:** Dates\n• **MONEY:** Monetary values",
        
        "sentiment": "😊 **Sentiment Analysis**\n\nDetermines emotional tone (positive, negative, neutral).\n\n**Methods:**\n• Lexicon-based (word dictionaries)\n• Machine Learning (Logistic Regression, SVM)\n• Deep Learning (LSTM, BERT)",
        
        "books": "📖 **Recommended Books**\n\n1. **'Speech and Language Processing'** - Jurafsky & Martin\n2. **'Natural Language Processing with Python'** - Bird, Klein, Loper\n3. **'Text Mining'** - Srivastava & Sahami\n\n**Free Resources:**\n• Hugging Face: https://huggingface.co/\n• NLTK: https://www.nltk.org/\n• spaCy: https://spacy.io/",
        
        "career": "🚀 **Career in NLP**\n\n**Skills Required:**\n• Python programming\n• Statistics & Probability\n• Machine Learning\n• Deep Learning\n\n**Career Paths:**\n1. NLP Engineer ($120k-$180k)\n2. Data Scientist ($100k-$150k)\n3. Research Scientist ($130k-$200k)\n4. ML Engineer ($110k-$170k)"
    },
    
    "general": {
        "greeting": "👋 **Welcome to Health & Text Analytics Assistant!**\n\nI can help you with:\n\n🏥 **Health Issues:**\n• Fever, headache, cough\n• Cold, stress, diabetes\n• COVID-19 guidance\n\n📚 **Text Analytics & NLP:**\n• Introduction to Text Analytics\n• Text preprocessing\n• Text representation (BoW, TF-IDF, BERT)\n• Named Entity Recognition (NER)\n• Sentiment Analysis\n• Books & career guidance\n\n💡 **Try asking:**\n• 'fever treatment'\n• 'what is NER?'\n• 'sentiment analysis'\n• 'NLP career'\n\nHow can I help you today?",
        
        "help": "ℹ️ **How I Can Help**\n\n**🏥 Health Topics:**\n• 'fever treatment'\n• 'headache remedies'\n• 'stress management'\n• 'diabetes care'\n• 'covid care'\n\n**📚 Text Analytics Topics:**\n• 'text analytics intro'\n• 'text preprocessing'\n• 'text representation'\n• 'what is NER'\n• 'sentiment analysis'\n• 'NLP books'\n• 'NLP career'\n\n**💻 Code Examples:**\n• 'show me code'\n\nJust type your question!",
        
        "code": "💻 **Python Code Examples for NLP**\n\n**1. Text Preprocessing:**\n```python\nimport re\nfrom nltk.corpus import stopwords\n\ndef preprocess_text(text):\n    text = text.lower()\n    text = re.sub(r'[^a-zA-Z\\s]', '', text)\n    tokens = text.split()\n    tokens = [w for w in tokens if w not in stopwords.words('english')]\n    return ' '.join(tokens)\n```\n\n**2. Sentiment Analysis:**\n```python\nfrom textblob import TextBlob\n\ndef analyze_sentiment(text):\n    blob = TextBlob(text)\n    sentiment = blob.sentiment.polarity\n    if sentiment > 0: return 'Positive 😊'\n    elif sentiment < 0: return 'Negative 😞'\n    else: return 'Neutral 😐'\n```\n\n**3. Named Entity Recognition:**\n```python\nimport spacy\nnlp = spacy.load('en_core_web_sm')\n\ndef extract_entities(text):\n    doc = nlp(text)\n    return [(ent.text, ent.label_) for ent in doc.ents]\n```"
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
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'chat_count': Chat.query.filter_by(user_id=self.id).count()
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

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        # Only users with role exactly 'Admin' can access
        if current_user.role != 'Admin':
            return jsonify({
                'error': f'Admin access required. Your role: {current_user.role}'
            }), 403
        return f(current_user, *args, **kwargs)
    return decorated

def create_auth_token(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def generate_bot_response(user_message, user_name="User"):
    msg = user_message.lower().strip()
    
    # Health queries
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
    
    # Text Analytics queries
    elif 'text analytics' in msg or 'nlp' in msg:
        if 'intro' in msg:
            return knowledge_base["text_analytics"]["introduction"]
        elif 'preprocess' in msg or 'token' in msg:
            return knowledge_base["text_analytics"]["preprocessing"]
        elif 'represent' in msg or 'tfidf' in msg or 'embedding' in msg:
            return knowledge_base["text_analytics"]["representation"]
        elif 'ner' in msg or 'named entity' in msg:
            return knowledge_base["text_analytics"]["ner"]
        elif 'sentiment' in msg:
            return knowledge_base["text_analytics"]["sentiment"]
        elif 'book' in msg or 'resource' in msg:
            return knowledge_base["text_analytics"]["books"]
        elif 'career' in msg or 'job' in msg:
            return knowledge_base["text_analytics"]["career"]
        else:
            return knowledge_base["text_analytics"]["introduction"]
    
    # Code examples
    elif 'code' in msg or 'example' in msg:
        return knowledge_base["general"]["code"]
    
    # Greetings
    elif any(word in msg for word in ['hello', 'hi', 'hey']):
        return knowledge_base["general"]["greeting"]
    
    # Help
    elif 'help' in msg:
        return knowledge_base["general"]["help"]
    
    # Default
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
            from sqlalchemy import inspect
            
            # Create tables if they don't exist
            db.create_all()
            print("✅ Database tables created/verified")
            
            # For PostgreSQL, enable UUID extension (optional)
            if DATABASE_URL and 'postgresql' in DATABASE_URL:
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                        conn.commit()
                        print("✅ UUID extension enabled")
                except Exception as e:
                    print(f"⚠️ Could not enable UUID extension: {e}")
            
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
            else:
                print(f"✅ Admin user already exists: {ADMIN_EMAIL}")
            
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
            else:
                print("✅ Demo user already exists: demo@example.com")
            
            db.session.commit()
            print("✅ Database initialization complete")
            
            # Print statistics
            admin_count = User.query.filter_by(role='Admin').count()
            regular_count = User.query.filter_by(role='Regular User').count()
            print(f"📊 Users: Admin={admin_count}, Regular={regular_count}")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            db.session.rollback()

# ========== API ROUTES ==========

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": f"{APP_NAME} API with Socket.IO is running!",
        "websocket": "enabled",
        "version": "2.0.0",
        "frontend_url": APP_URL,
        "api_url": API_URL
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
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
            
            # Update last login time
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

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        
        if not email or not name or not password:
            return jsonify({'error': 'All fields required'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Role assignment - ONLY admin email gets Admin role
        if email == ADMIN_EMAIL:
            role = "Admin"
            print(f"👑 Admin user registering: {email}")
        else:
            role = "Regular User"
            print(f"👤 Regular user registering: {email} as {role}")
        
        # Create new user
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
        
        # Create auth token
        token = create_auth_token(email)
        
        print(f"✅ Registration successful: {email} ({role})")
        
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

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({'success': True, 'user': current_user.to_dict()})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'app': APP_NAME,
        'websocket': 'enabled',
        'active_connections': len(active_connections),
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
    print(f"🔌 WebSocket: ws://{HOST_IP}:{BACKEND_PORT}")
    print(f"📡 Allowed Origins: {ALLOWED_ORIGINS}")
    print(f"🗄️ Database: {'PostgreSQL (Supabase)' if DATABASE_URL and 'postgresql' in DATABASE_URL else 'SQLite'}")
    print("=" * 70)
    print("✅ Socket.IO enabled - Real-time chat active!")
    print("=" * 70)
    
    init_database()
    
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(BACKEND_PORT),
        debug=DEBUG_MODE,
        allow_unsafe_werkzeug=True
    )