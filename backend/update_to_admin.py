# update_to_admin.py
from app import app, db, User

with app.app_context():
    print("=" * 60)
    print("🔧 UPDATING YOUR ACCOUNT TO ADMIN...")
    print("=" * 60)
    
    # Find your account
    your_account = User.query.filter_by(email="shanmukharaveeti77@gmail.com").first()
    
    if your_account:
        print(f"✅ Account found!")
        print(f"   Email: {your_account.email}")
        print(f"   Current role: {your_account.role}")
        
        # Update to Admin
        your_account.role = "Admin"
        db.session.commit()
        
        print(f"\n✅ Role updated to: {your_account.role}")
        print(f"   Now you have Admin access!")
    else:
        print(f"❌ Account not found!")
        print(f"   Please make sure you're logged in with this email")
    
    # Show all users with their roles
    print("\n" + "=" * 60)
    print("📊 ALL USER ROLES:")
    print("=" * 60)
    all_users = User.query.all()
    for user in all_users:
        if user.role == "Admin":
            print(f"   👑 {user.email}: {user.role} (ADMIN)")
        else:
            print(f"   👤 {user.email}: {user.role}")
    print("=" * 60)