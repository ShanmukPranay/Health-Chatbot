from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import logging
import sqlite3

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.environ.get("APP_URL", "http://localhost:3000")}})

# ========== CONFIGURATION FROM .ENV ==========

# Security
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "health-ai-assistant-secret-key-2024-change-this-in-production")
OTP_EXPIRY_MINUTES = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))
TOKEN_EXPIRY_MINUTES = int(os.environ.get("TOKEN_EXPIRY_MINUTES", 15))
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", 24))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///health_ai.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

# Application Settings
APP_NAME = os.environ.get("APP_NAME", "Health & AI Assistant")
APP_URL = os.environ.get("APP_URL", "http://localhost:3000")
API_URL = os.environ.get("API_URL", "http://localhost:5000")
DEBUG_MODE = os.environ.get("DEBUG", "True").lower() == "true"

# ========== HARDCODED ADMIN EMAIL ==========
# ONLY THIS EMAIL WILL BE ADMIN
ADMIN_EMAIL = "2300031563@kluniversity"
ADMIN_PASSWORD = "Admin@123"  # You can change this
ADMIN_NAME = "Admin User"

# Chat Settings
MAX_CHAT_HISTORY = int(os.environ.get("MAX_CHAT_HISTORY", 100))
CHAT_SESSION_TIMEOUT = int(os.environ.get("CHAT_SESSION_TIMEOUT", 30))

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 60))
RATE_LIMIT_PER_HOUR = int(os.environ.get("RATE_LIMIT_PER_HOUR", 1000))

# Initialize database
db = SQLAlchemy(app)

# ========== DATABASE MODELS ==========

class User(db.Model):
    """User model for authentication and profile"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='Regular User')  # Default is Regular User
    avatar = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'Admin'
    
    def is_premium(self):
        """Check if user is premium"""
        return self.role == 'Premium User'
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'avatar': self.avatar or self.name[0].upper(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'chat_count': Chat.query.filter_by(user_id=self.id).count()
        }

class Chat(db.Model):
    """Chat history model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # 'health', 'text_analytics', 'general'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_message': self.user_message,
            'bot_response': self.bot_response,  # FIXED: Changed from bot_response to self.bot_response
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OTP(db.Model):
    """OTP storage model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(50), default='password_reset')
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='otps', lazy=True)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return datetime.utcnow() < self.expires_at and not self.is_used
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'email': self.email,
            'purpose': self.purpose,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Feedback(db.Model):
    """User feedback model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    email = db.Column(db.String(120))
    rating = db.Column(db.Integer)  # 1-5
    message = db.Column(db.Text)
    feedback_type = db.Column(db.String(50))  # 'bug', 'feature', 'general'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'rating': self.rating,
            'message': self.message,
            'feedback_type': self.feedback_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ========== HELPER FUNCTIONS ==========

def delete_database():
    """Delete the database file and start fresh"""
    db_path = 'health_ai.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"🗑️  Database deleted: {db_path}")
            return True
        except Exception as e:
            print(f"❌ Error deleting database: {str(e)}")
            return False
    else:
        print("ℹ️  Database file not found, will create new one")
        return True

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(email=data['email']).first()
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            if not current_user.is_active:
                return jsonify({'error': 'User account is deactivated'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def send_email(to_email, subject, body):
    """Send email using SMTP"""
    try:
        # If no email credentials, simulate sending
        if not EMAIL_USER or not EMAIL_PASSWORD:
            print(f"📧 [SIMULATED] Email to {to_email}: {subject}")
            print(f"Body preview: {body[:100]}...")
            return True
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add HTML body
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email sending error: {str(e)}")
        return False

def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))

def create_reset_token(email):
    """Create JWT reset token"""
    payload = {
        'email': email,
        'purpose': 'password_reset',
        'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def create_auth_token(email):
    """Create JWT authentication token"""
    payload = {
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# ========== DATABASE INITIALIZATION ==========

def init_database():
    """Initialize database and create default data - RUNS ONLY ONCE"""
    with app.app_context():
        try:
            # Check if database already exists and has tables
            table_exists = False
            try:
                # Try to query a user to check if tables exist
                User.query.first()
                table_exists = True
                print("✅ Database tables already exist")
            except:
                table_exists = False
            
            if not table_exists:
                # Create all tables
                db.create_all()
                print("✅ Database tables created successfully")
            
            # ========== CREATE ADMIN USER ==========
            # Check if admin user already exists
            admin_user = User.query.filter_by(email=ADMIN_EMAIL).first()
            if not admin_user:
                admin_user = User(
                    email=ADMIN_EMAIL,
                    name=ADMIN_NAME,
                    role='Admin',  # Only Admin role
                    avatar='A',
                    is_active=True
                )
                admin_user.set_password(ADMIN_PASSWORD)
                db.session.add(admin_user)
                print(f"✅ Admin user created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
                print(f"   Role: Admin (Only this user has admin access)")
            else:
                print(f"✅ Admin user already exists: {ADMIN_EMAIL}")
            
            # ========== CREATE DEMO USER ==========
            # Check if demo user already exists
            demo_user = User.query.filter_by(email="demo@example.com").first()
            if not demo_user:
                demo_user = User(
                    email="demo@example.com",
                    name="Demo User",
                    role='Regular User',  # Always Regular User
                    avatar='D',
                    is_active=True
                )
                demo_user.set_password("demo123")
                db.session.add(demo_user)
                print("✅ Demo user created: demo@example.com / demo123")
                print(f"   Role: Regular User (No admin access)")
            else:
                print("✅ Demo user already exists: demo@example.com")
            
            # Only commit if we made changes
            if not admin_user or not demo_user:
                db.session.commit()
            
            # Verify setup
            admin_count = User.query.filter_by(role='Admin').count()
            regular_count = User.query.filter_by(role='Regular User').count()
            
            print(f"\n📊 Verification:")
            print(f"   ✅ Admins: {admin_count} (Only: {ADMIN_EMAIL})")
            print(f"   ✅ Regular Users: {regular_count}")
            print(f"\n🔐 Admin Panel Access:")
            print(f"   ✅ ONLY {ADMIN_EMAIL} can access admin routes")
            print(f"   ❌ All other users: Regular User role only")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

# Initialize database on startup - but only if not already initialized
with app.app_context():
    try:
        # Check if we've already initialized by checking if users table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables_exist = inspector.has_table('user')
        
        if not tables_exist:
            print("🔧 Initializing database for the first time...")
            init_database()
        else:
            print("✅ Database already initialized")
    except Exception as e:
        print(f"⚠️ Could not check database status: {e}")
        # Create tables if they don't exist
        db.create_all()
        init_database()

# ========== ROUTES ==========

# Home route
@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": f"{APP_NAME} API is running!",
        "app": APP_NAME,
        "frontend_url": APP_URL,
        "api_url": API_URL,
        "database": "SQLite" if "sqlite" in app.config['SQLALCHEMY_DATABASE_URI'] else "PostgreSQL/MySQL",
        "admin_email": ADMIN_EMAIL,
        "roles_info": {
            "Admin": f"ONLY for {ADMIN_EMAIL}",
            "Premium User": "By admin upgrade only",
            "Regular User": "Default for all other users"
        },
        "endpoints": {
            "auth": {
                "POST /api/auth/register": "Register new user (Regular User by default)",
                "POST /api/auth/login": "User login",
                "POST /api/auth/request-otp": "Request password reset OTP",
                "POST /api/auth/verify-otp": "Verify OTP",
                "POST /api/auth/reset-password": "Reset password"
            },
            "user": {
                "GET /api/user/profile": "Get user profile (Token required)",
                "PUT /api/user/profile": "Update profile (Token required)",
                "GET /api/user/chats": "Get chat history (Token required)",
                "POST /api/user/chat": "Save chat message (Token required)",
                "DELETE /api/user/chats/clear": "Clear chat history (Token required)"
            },
            "admin": {
                "GET /api/admin/dashboard": f"Admin dashboard (ONLY for {ADMIN_EMAIL})",
                "GET /api/admin/user/<email>": f"Get user details by email (ONLY for {ADMIN_EMAIL})",
                "GET /api/admin/users": f"Get all users (ONLY for {ADMIN_EMAIL})",
                "PUT /api/admin/user/role": f"Update user role (ONLY for {ADMIN_EMAIL})"
            },
            "system": {
                "GET /api/health": "Health check",
                "GET /api/stats": "System statistics",
                "POST /api/feedback": "Submit feedback"
            }
        }
    })

# ========== AUTHENTICATION ROUTES ==========

# 1. User Registration
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        
        if not email or not name or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check password length
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # ========== IMPORTANT: ROLE ASSIGNMENT ==========
        # ONLY your email gets Admin role, everyone else gets Regular User
        if email == ADMIN_EMAIL:
            role = "Admin"
        else:
            role = "Regular User"  # Default for everyone else
        
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
        auth_token = create_auth_token(email)
        
        print(f"✅ New user registered: {email} ({name}) as {role}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': new_user.to_dict(),
            'token': auth_token
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in register: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 2. User Login - NO ROLE CHANGES
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        print(f"🔑 Login attempt: {email}")
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        # Check user credentials
        if user and user.check_password(password):
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403
            
            # Update last login
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Create auth token
            auth_token = create_auth_token(email)
            
            print(f"✅ Login successful: {email} as {user.role}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': auth_token
            })
        else:
            print(f"❌ Login failed: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"❌ Error in login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 3. Request OTP for password reset
@app.route('/api/auth/request-otp', methods=['POST'])
def request_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        # Delete old OTPs for this email
        OTP.query.filter_by(email=email, purpose='password_reset', is_used=False).delete()
        
        # Store new OTP
        new_otp = OTP(
            email=email,
            user_id=user.id,
            otp_code=otp_code,
            purpose='password_reset',
            expires_at=expires_at
        )
        
        db.session.add(new_otp)
        db.session.commit()
        
        # Email HTML template
        email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f8fafc; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px 10px 0 0; color: white; text-align: center; }}
                .otp-box {{ background: #f8fafc; padding: 25px; text-align: center; margin: 20px 0; border-radius: 10px; border: 2px dashed #667eea; }}
                .otp-code {{ font-size: 40px; font-weight: bold; color: #667eea; letter-spacing: 10px; margin: 10px 0; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #666; font-size: 14px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{APP_NAME}</h1>
                    <p>Password Reset OTP</p>
                </div>
                <h2>Hello {user.name},</h2>
                <p>You requested to reset your password. Use the OTP below:</p>
                
                <div class="otp-box">
                    <p style="color: #666; margin-bottom: 10px;">Your OTP Code:</p>
                    <div class="otp-code">{otp_code}</div>
                    <p style="color: #888; font-size: 14px; margin-top: 10px;">Valid for {OTP_EXPIRY_MINUTES} minutes</p>
                </div>
                
                <p>If you didn't request this, please ignore this email.</p>
                <p style="color: #ff6b6b; font-size: 14px; margin-top: 20px;">
                    ⚠️ For security, never share this OTP with anyone.
                </p>
                
                <div class="footer">
                    <p>{APP_NAME} Team<br>
                    <small>This is an automated message, please do not reply.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        if send_email(email, f"Password Reset OTP - {APP_NAME}", email_html):
            # Print OTP to console for testing
            print(f"📧 OTP for {email}: {otp_code}")
            print(f"⏰ Expires at: {expires_at}")
            
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully',
                'expires_in': f'{OTP_EXPIRY_MINUTES} minutes',
                'note': 'Check console for OTP (in development)'
            })
        else:
            # In development, still return success but with note
            print(f"📧 [DEV MODE] OTP for {email}: {otp_code}")
            return jsonify({
                'success': True,
                'message': 'OTP generated (email simulation)',
                'otp': otp_code,  # Only in development!
                'expires_in': f'{OTP_EXPIRY_MINUTES} minutes',
                'note': 'Running in development mode - check console for OTP'
            })
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in request_otp: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 4. Verify OTP
@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        otp_code = data.get('otp')
        
        if not email or not otp_code:
            return jsonify({'error': 'Email and OTP required'}), 400
        
        print(f"🔍 Verifying OTP for {email}: {otp_code}")
        
        # Find valid OTP
        otp_record = OTP.query.filter_by(
            email=email, 
            otp_code=otp_code, 
            purpose='password_reset',
            is_used=False
        ).first()
        
        if not otp_record:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        
        # Check if OTP is expired
        if datetime.utcnow() > otp_record.expires_at:
            otp_record.is_used = True
            db.session.commit()
            return jsonify({'error': 'OTP expired'}), 400
        
        # Mark OTP as used
        otp_record.is_used = True
        
        # Create reset token
        reset_token = create_reset_token(email)
        
        db.session.commit()
        
        print(f"✅ OTP verified for {email}")
        
        return jsonify({
            'success': True,
            'message': 'OTP verified successfully',
            'reset_token': reset_token
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in verify_otp: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 5. Reset Password
@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        reset_token = data.get('reset_token')
        new_password = data.get('new_password')
        
        if not reset_token or not new_password:
            return jsonify({'error': 'Token and new password required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Verify token
        try:
            payload = jwt.decode(reset_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            if payload['purpose'] != 'password_reset':
                return jsonify({'error': 'Invalid token'}), 400
            
            email = payload['email']
            
            # Find user
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Update password
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            print(f"✅ Password reset for {email}")
            
            return jsonify({
                'success': True,
                'message': 'Password reset successful'
            })
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Reset token expired'}), 400
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in reset_password: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ========== USER PROFILE ROUTES (Token Required) ==========

# 6. Get user profile
@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })
    except Exception as e:
        print(f"❌ Error in get_profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 7. Update user profile
@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            current_user.name = data['name']
            current_user.avatar = data['name'][0].upper()
        
        if 'avatar' in data:
            current_user.avatar = data['avatar']
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        print(f"✅ Profile updated for {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in update_profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 8. Get user chat history
@app.route('/api/user/chats', methods=['GET'])
@token_required
def get_chats(current_user):
    try:
        # Get chats for current user (limited by MAX_CHAT_HISTORY from .env)
        chats = Chat.query.filter_by(user_id=current_user.id)\
            .order_by(Chat.created_at.desc())\
            .limit(MAX_CHAT_HISTORY)\
            .all()
        
        chats_list = [chat.to_dict() for chat in chats]
        
        return jsonify({
            'success': True,
            'chats': chats_list,
            'count': len(chats_list),
            'max_history': MAX_CHAT_HISTORY
        })
        
    except Exception as e:
        print(f"❌ Error in get_chats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 9. Save chat message
@app.route('/api/user/chat', methods=['POST'])
@token_required
def save_chat(current_user):
    try:
        data = request.get_json()
        
        session_id = data.get('session_id')
        user_message = data.get('user_message')
        bot_response = data.get('bot_response')
        category = data.get('category', 'general')
        
        if not all([session_id, user_message, bot_response]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new chat record
        new_chat = Chat(
            user_id=current_user.id,
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            category=category
        )
        
        db.session.add(new_chat)
        db.session.commit()
        
        print(f"💾 Chat saved for {current_user.email} (session: {session_id})")
        
        return jsonify({
            'success': True,
            'message': 'Chat saved successfully',
            'chat_id': new_chat.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in save_chat: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 10. Delete user chat history
@app.route('/api/user/chats/clear', methods=['DELETE'])
@token_required
def clear_chats(current_user):
    try:
        # Delete all chats for current user
        deleted_count = Chat.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        print(f"🗑️ Cleared {deleted_count} chats for {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} chat messages',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in clear_chats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ========== ADMIN ROUTES (Admin Only) ==========

# 11. Admin dashboard - get all user details (Admin only)
@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard(current_user):
    try:
        # Get all users with their stats
        users = User.query.all()
        
        user_list = []
        for user in users:
            # Get user's chat count
            chat_count = Chat.query.filter_by(user_id=user.id).count()
            
            # Get user's last activity
            last_chat = Chat.query.filter_by(user_id=user.id)\
                .order_by(Chat.created_at.desc())\
                .first()
            
            user_list.append({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'avatar': user.avatar,
                'is_active': user.is_active,
                'chat_count': chat_count,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'last_active': last_chat.created_at.isoformat() if last_chat else None
            })
        
        # Get system statistics
        total_users = len(user_list)
        active_users = len([u for u in user_list if u['is_active']])
        total_chats = Chat.query.count()
        
        return jsonify({
            'success': True,
            'admin_info': {
                'email': current_user.email,
                'name': current_user.name,
                'role': current_user.role
            },
            'users': user_list,
            'statistics': {
                'total_users': total_users,
                'active_users': active_users,
                'total_chats': total_chats,
                'users_with_chats': len([u for u in user_list if u['chat_count'] > 0]),
                'admin_users': len([u for u in user_list if u['role'] == 'Admin']),
                'premium_users': len([u for u in user_list if u['role'] == 'Premium User']),
                'regular_users': len([u for u in user_list if u['role'] == 'Regular User'])
            },
            'config': {
                'max_chat_history': MAX_CHAT_HISTORY,
                'chat_session_timeout': CHAT_SESSION_TIMEOUT,
                'rate_limit_per_minute': RATE_LIMIT_PER_MINUTE,
                'rate_limit_per_hour': RATE_LIMIT_PER_HOUR
            }
        })
        
    except Exception as e:
        print(f"❌ Error in admin_dashboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 12. Get user details by email (Admin only)
@app.route('/api/admin/user/<email>', methods=['GET'])
@admin_required
def get_user_details(current_user, email):
    try:
        # Find by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's recent chats
        recent_chats = Chat.query.filter_by(user_id=user.id)\
            .order_by(Chat.created_at.desc())\
            .limit(10)\
            .all()
        
        # Get user's OTPs
        user_otps = OTP.query.filter_by(user_id=user.id)\
            .order_by(OTP.created_at.desc())\
            .limit(5)\
            .all()
        
        user_data = {
            'basic_info': user.to_dict(),
            'activity': {
                'total_chats': Chat.query.filter_by(user_id=user.id).count(),
                'recent_chats': [chat.to_dict() for chat in recent_chats],
                'last_login': user.updated_at.isoformat() if user.updated_at else None
            },
            'security': {
                'otp_count': OTP.query.filter_by(user_id=user.id).count(),
                'recent_otps': [otp.to_dict() for otp in user_otps]
            }
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        print(f"❌ Error in get_user_details: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 13. Get all users (Admin only)
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users(current_user):
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users],
            'count': len(users),
            'role_counts': {
                'admin': User.query.filter_by(role='Admin').count(),
                'premium': User.query.filter_by(role='Premium User').count(),
                'regular': User.query.filter_by(role='Regular User').count()
            }
        })
    except Exception as e:
        print(f"❌ Error in get_all_users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 14. Update user role (Admin only) - Strict rules
@app.route('/api/admin/user/role', methods=['PUT'])
@admin_required
def update_user_role(current_user):
    try:
        data = request.get_json()
        email = data.get('email')
        new_role = data.get('role')
        
        if not email or not new_role:
            return jsonify({'error': 'Email and role are required'}), 400
        
        # Validate role
        valid_roles = ['Admin', 'Premium User', 'Regular User']
        if new_role not in valid_roles:
            return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # ========== STRICT RULES ==========
        # RULE 1: Only ONE user can be Admin (YOUR EMAIL)
        if new_role == 'Admin':
            if email != ADMIN_EMAIL:
                return jsonify({'error': f'Only {ADMIN_EMAIL} can be Admin'}), 403
        
        # RULE 2: Cannot change role of the primary admin
        if email == ADMIN_EMAIL and new_role != 'Admin':
            return jsonify({'error': f'Cannot change role of {ADMIN_EMAIL}'}), 403
        
        # RULE 3: Cannot demote yourself if you're the admin
        if email == current_user.email and new_role != 'Admin':
            return jsonify({'error': 'Cannot remove admin role from yourself'}), 403
        
        # Update role
        old_role = user.role
        user.role = new_role
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        print(f"✅ Role updated for {email}: {old_role} → {new_role} by {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': f'User role updated to {new_role}',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in update_user_role: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ========== SYSTEM ROUTES ==========

# 15. Health Check
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        user_count = User.query.count()
        chat_count = Chat.query.count()
        
        # Check admin user exists
        admin_exists = User.query.filter_by(email=ADMIN_EMAIL, role='Admin').first() is not None
        
        # Check user roles distribution
        admin_count = User.query.filter_by(role='Admin').count()
        premium_count = User.query.filter_by(role='Premium User').count()
        regular_count = User.query.filter_by(role='Regular User').count()
        
        return jsonify({
            'status': 'healthy',
            'app': APP_NAME,
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'environment': 'development' if DEBUG_MODE else 'production',
            'admin': {
                'exists': admin_exists,
                'email': ADMIN_EMAIL if admin_exists else 'Not found',
                'count': admin_count
            },
            'user_roles': {
                'admin': admin_count,
                'premium': premium_count,
                'regular': regular_count
            },
            'statistics': {
                'users': user_count,
                'chats': chat_count,
                'otps': OTP.query.filter_by(is_used=False).count()
            },
            'config': {
                'max_chat_history': MAX_CHAT_HISTORY,
                'session_timeout': CHAT_SESSION_TIMEOUT,
                'otp_expiry': OTP_EXPIRY_MINUTES,
                'jwt_expiry': JWT_EXPIRY_HOURS
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'app': APP_NAME,
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

# 16. System Statistics
@app.route('/api/stats', methods=['GET'])
def system_stats():
    try:
        # Get today's date
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # User statistics
        total_users = User.query.count()
        active_today = User.query.filter(
            User.updated_at >= today_start
        ).count()
        
        # Chat statistics
        total_chats = Chat.query.count()
        chats_today = Chat.query.filter(
            Chat.created_at >= today_start
        ).count()
        
        # Category distribution
        from sqlalchemy import func
        categories = db.session.query(
            Chat.category, 
            func.count(Chat.id).label('count')
        ).group_by(Chat.category).all()
        
        category_dist = {str(cat): cnt for cat, cnt in categories if cat}
        
        # Role distribution
        admin_count = User.query.filter_by(role='Admin').count()
        premium_count = User.query.filter_by(role='Premium User').count()
        regular_count = User.query.filter_by(role='Regular User').count()
        
        return jsonify({
            'success': True,
            'app': APP_NAME,
            'statistics': {
                'users': {
                    'total': total_users,
                    'active_today': active_today,
                    'roles': {
                        'admin': admin_count,
                        'premium': premium_count,
                        'regular': regular_count
                    }
                },
                'chats': {
                    'total': total_chats,
                    'today': chats_today,
                    'categories': category_dist,
                    'max_history_per_user': MAX_CHAT_HISTORY
                },
                'system': {
                    'database': 'SQLite' if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'] else 'PostgreSQL/MySQL',
                    'environment': 'development' if DEBUG_MODE else 'production',
                    'frontend_url': APP_URL,
                    'api_url': API_URL,
                    'admin_email': ADMIN_EMAIL,
                    'last_updated': datetime.utcnow().isoformat()
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Error in system_stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 17. Submit feedback
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        
        email = data.get('email')
        rating = data.get('rating')
        message = data.get('message')
        feedback_type = data.get('feedback_type', 'general')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user if logged in
        user_id = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                    user = User.query.filter_by(email=payload['email']).first()
                    if user:
                        user_id = user.id
                        email = user.email
                except:
                    pass
        
        # Create feedback
        feedback = Feedback(
            user_id=user_id,
            email=email,
            rating=rating,
            message=message,
            feedback_type=feedback_type
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        print(f"📝 Feedback submitted by {email or 'anonymous'}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in submit_feedback: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ========== MAIN ==========

if __name__ == "__main__":
    print("=" * 70)
    print(f"🚀 Starting {APP_NAME} API Server...")
    print("=" * 70)
    print(f"📦 Application: {APP_NAME}")
    print(f"👑 ADMIN USER: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"   ⚠️  ONLY THIS EMAIL HAS ADMIN ACCESS")
    print(f"👤 DEMO USER: demo@example.com / demo123 (Regular User)")
    print(f"🌐 Frontend URL: {APP_URL}")
    print(f"🔧 API URL: {API_URL}")
    print(f"📊 Database: SQLite (health_ai.db) - FRESH START")
    print(f"📧 Email Service: {'Enabled' if EMAIL_USER else 'Simulation Mode'}")
    print(f"⚙️ Config: Max Chat History={MAX_CHAT_HISTORY}, Session Timeout={CHAT_SESSION_TIMEOUT}min")
    print("=" * 70)
    print("🌐 API Endpoints:")
    print("  - GET  /                    - API Information")
    print("  - POST /api/auth/register   - Register new user (Regular User by default)")
    print("  - POST /api/auth/login      - User login (NO role changes)")
    print("  - POST /api/auth/request-otp - Request OTP")
    print("  - POST /api/auth/verify-otp - Verify OTP")
    print("  - POST /api/auth/reset-password - Reset password")
    print("  - GET  /api/user/profile    - Get profile (Token)")
    print("  - PUT  /api/user/profile    - Update profile (Token)")
    print("  - GET  /api/user/chats      - Get chat history (Token)")
    print("  - POST /api/user/chat       - Save chat (Token)")
    print("  - DELETE /api/user/chats/clear - Clear chats (Token)")
    print(f"  - GET  /api/admin/dashboard - Admin dashboard (ONLY for {ADMIN_EMAIL})")
    print(f"  - GET  /api/admin/user/<email> - User details (ONLY for {ADMIN_EMAIL})")
    print(f"  - GET  /api/admin/users     - All users (ONLY for {ADMIN_EMAIL})")
    print(f"  - PUT  /api/admin/user/role - Update user role (ONLY for {ADMIN_EMAIL})")
    print("  - POST /api/feedback        - Submit feedback")
    print("  - GET  /api/health          - Health check")
    print("  - GET  /api/stats           - System statistics")
    print("=" * 70)
    print("🔒 STRICT ROLE RULES:")
    print(f"   1. ONLY '{ADMIN_EMAIL}' gets Admin role")
    print("   2. All other users get 'Regular User' role")
    print("   3. Only Admin can upgrade users to 'Premium User'")
    print("   4. Login does NOT change user roles")
    print("=" * 70)
    print(f"✅ Server running on {API_URL}")
    print(f"📞 Frontend should connect from {APP_URL}")
    print("=" * 70)
    
    app.run(
        host="127.0.0.1", 
        port=5000, 
        debug=DEBUG_MODE
    )