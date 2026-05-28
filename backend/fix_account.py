# fix_account.py
from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email="shanmukharaveeti77@gmail.com").first()
    
    if user:
        print(f"Found: {user.email}")
        print(f"Current role: {user.role}")
        user.role = "Admin"
        db.session.commit()
        print(f"✅ Updated to: {user.role}")
    else:
        print("❌ User not found!")
    
    print("\n📊 All users:")
    for u in User.query.all():
        print(f"   {u.email}: {u.role}")