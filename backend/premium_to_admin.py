# premium_to_admin.py
from app import app, db, User

# Your premium user email
PREMIUM_EMAIL = "2300031563@kluniversity"  # Change this to your email

with app.app_context():
    user = User.query.filter_by(email=PREMIUM_EMAIL).first()
    
    if user:
        print(f"✅ Found: {user.email}")
        print(f"   Current role: {user.role}")
        
        user.role = "Admin"
        db.session.commit()
        
        print(f"   ✅ Changed to: {user.role}")
        print(f"\n🎉 Now you will see the Admin Panel button!")
    else:
        print(f"❌ User not found!")
        print(f"   Available users:")
        for u in User.query.all():
            print(f"   - {u.email}: {u.role}")