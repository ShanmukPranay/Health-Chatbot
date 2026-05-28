# fix_my_admin.py
from app import app, db, User

# YOUR email
MY_EMAIL = "shanmukharaveeti77@gmail.com"

with app.app_context():
    print("=" * 60)
    print("🔧 FIXING YOUR ACCOUNT TO ADMIN...")
    print("=" * 60)
    
    # Find your account
    user = User.query.filter_by(email=MY_EMAIL).first()
    
    if user:
        print(f"✅ Account found: {user.email}")
        print(f"   Current role: {user.role}")
        
        # Change to Admin (NOT Premium User)
        user.role = "Admin"
        db.session.commit()
        
        print(f"\n✅ Role changed to: {user.role}")
        print(f"   Now you should see Admin Panel button!")
    else:
        print(f"❌ Account not found!")
    
    # Show all users
    print("\n" + "=" * 60)
    print("📊 ALL USER ROLES NOW:")
    print("=" * 60)
    all_users = User.query.all()
    for u in all_users:
        if u.role == "Admin":
            print(f"   👑 {u.email}: {u.role}")
        else:
            print(f"   👤 {u.email}: {u.role}")
    print("=" * 60)