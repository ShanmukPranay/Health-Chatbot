# fix_premium_to_regular.py
from app import app, db, User

with app.app_context():
    # Find the user aspranay77@gmail.com
    user = User.query.filter_by(email="aspranay77@gmail.com").first()
    
    if user:
        print(f"Found user: {user.email}")
        print(f"Current role: {user.role}")
        
        # Change from "Premium User" to "Regular User"
        user.role = "Regular User"
        db.session.commit()
        
        print(f"✅ Changed to: {user.role}")
    else:
        print("❌ User not found!")
    
    # Show all users
    print("\n📊 All users now:")
    for u in User.query.all():
        print(f"   {u.email}: {u.role}")