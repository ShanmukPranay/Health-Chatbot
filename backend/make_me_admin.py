# make_me_admin.py
from app import app, db, User

ADMIN_EMAIL = "shanmukharaveeti77@gmail.com"  # YOUR email

with app.app_context():
    print("=" * 60)
    print("🔧 SETTING ADMIN FOR YOUR ACCOUNT...")
    print("=" * 60)
    
    # Find your account
    your_user = User.query.filter_by(email=ADMIN_EMAIL).first()
    
    if your_user:
        print(f"✅ Found your account: {your_user.email}")
        print(f"   Current role: {your_user.role}")
        
        # Set ONLY you as Admin
        your_user.role = "Admin"
        
        # Make sure everyone else is Regular User
        all_users = User.query.all()
        for user in all_users:
            if user.email != ADMIN_EMAIL and user.role != "Regular User":
                user.role = "Regular User"
                print(f"   Fixed: {user.email} → Regular User")
        
        db.session.commit()
        
        print(f"\n✅ Your role updated to: {your_user.role}")
        print(f"   Now only YOU have Admin access!")
    else:
        print(f"❌ Account {ADMIN_EMAIL} not found!")
        print("   Please register this account first through the frontend.")
        print("   Then run this script again.")
    
    print("\n" + "=" * 60)
    print("📊 FINAL USER ROLES:")
    print("=" * 60)
    for user in User.query.all():
        if user.role == "Admin":
            print(f"   👑 {user.email}: {user.role} (ADMIN)")
        else:
            print(f"   👤 {user.email}: {user.role}")
    print("=" * 60)