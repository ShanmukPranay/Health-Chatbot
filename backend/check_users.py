# check_users.py
from app import app, db, User

with app.app_context():
    print("=" * 60)
    print("📊 ALL USERS IN DATABASE:")
    print("=" * 60)
    
    all_users = User.query.all()
    
    if not all_users:
        print("No users found in database!")
    else:
        for user in all_users:
            print(f"   📧 {user.email} - Role: {user.role}")
    
    print("=" * 60)
    
    # Check specifically for your email
    your_user = User.query.filter_by(email="shanmukharaveeti77@gmail.com").first()
    if your_user:
        print(f"\n✅ Your account found!")
        print(f"   Email: {your_user.email}")
        print(f"   Role: {your_user.role}")
        print(f"   Name: {your_user.name}")
    else:
        print(f"\n❌ Your account 'shanmukharaveeti77@gmail.com' NOT found in database!")
        print(f"   You need to register this account first through the frontend.")
    
    print("=" * 60)