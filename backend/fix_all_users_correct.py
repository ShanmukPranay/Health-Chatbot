# fix_all_users_correct.py
from app import app, db, User

# YOUR admin email
ADMIN_EMAIL = "shanmukharaveeti77@gmail.com"

with app.app_context():
    print("=" * 60)
    print("🔧 FIXING ALL USER ROLES...")
    print("=" * 60)
    
    all_users = User.query.all()
    
    for user in all_users:
        old_role = user.role  # ← Define old_role here FIRST
        
        if user.email == ADMIN_EMAIL:
            # ONLY your account gets Admin
            if user.role != "Admin":
                user.role = "Admin"
                print(f"✅ {user.email}: {old_role} → Admin")
            else:
                print(f"✓ {user.email}: Already Admin")
        else:
            # EVERYONE else gets Regular User
            if user.role != "Regular User":
                user.role = "Regular User"
                print(f"✅ {user.email}: {old_role} → Regular User")
            else:
                print(f"✓ {user.email}: Already Regular User")
    
    db.session.commit()
    
    print("\n" + "=" * 60)
    print("📊 FINAL USER ROLES:")
    print("=" * 60)
    for user in User.query.all():
        role_display = "👑 ADMIN" if user.role == "Admin" else "Regular User"
        print(f"   {user.email}: {role_display}")
    print("=" * 60)