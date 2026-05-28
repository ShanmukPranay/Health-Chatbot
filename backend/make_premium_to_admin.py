# make_premium_to_admin.py
from app import app, db, User

with app.app_context():
    # Find your premium user account
    user = User.query.filter_by(email="shanmukharaveeti77@gmail.com").first()
    
    if user:
        print(f"Found user: {user.email}")
        print(f"Current role: {user.role}")
        
        # Change from Premium User to Admin
        user.role = "Admin"
        db.session.commit()
        
        print(f"✅ Changed to: {user.role}")
        print(f"Now you will see the Admin Panel button!")
    else:
        print("❌ User not found!")
    
    # Show all users
    print("\n📊 All users:")
    for u in User.query.all():
        if u.role == "Admin":
            print(f"   👑 {u.email}: {u.role}")
        else:
            print(f"   👤 {u.email}: {u.role}")