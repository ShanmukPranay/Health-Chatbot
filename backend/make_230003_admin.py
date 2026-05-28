# fix_230003_admin.py
from app import app, db, User

with app.app_context():
    print("=" * 60)
    print("🔧 FIXING 230003 ADMIN ACCOUNT")
    print("=" * 60)
    
    # Check for both possible email formats
    user1 = User.query.filter_by(email="2300031563@kluniversity").first()
    user2 = User.query.filter_by(email="2300031563@kluniversity.in").first()
    user3 = User.query.filter_by(email="2300031563").first()
    
    if user1:
        print(f"\n✅ Found: {user1.email}")
        print(f"   Current role: {user1.role}")
        user1.role = "Admin"
        db.session.commit()
        print(f"   ✅ Updated to: Admin")
    elif user2:
        print(f"\n✅ Found: {user2.email}")
        print(f"   Current role: {user2.role}")
        user2.role = "Admin"
        db.session.commit()
        print(f"   ✅ Updated to: Admin")
    elif user3:
        print(f"\n✅ Found: {user3.email}")
        print(f"   Current role: {user3.role}")
        user3.role = "Admin"
        db.session.commit()
        print(f"   ✅ Updated to: Admin")
    else:
        print("\n❌ No user found with email containing '2300031563'")
        print("\n📋 Available users in database:")
        all_users = User.query.all()
        for u in all_users:
            print(f"   - {u.email}: {u.role}")
    
    # Show all users after fix
    print("\n" + "=" * 60)
    print("📊 ALL USERS AFTER FIX:")
    print("=" * 60)
    for u in User.query.all():
        if u.role == "Admin":
            print(f"   👑 {u.email}: {u.role}")
        else:
            print(f"   👤 {u.email}: {u.role}")
    print("=" * 60)