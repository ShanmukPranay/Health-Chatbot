#!/usr/bin/env python
# fix_roles.py - Run this to fix user roles

from app import app, db, User
from dotenv import load_dotenv
import os

load_dotenv()

# Your admin email - ONLY this email stays as Admin
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "2300031563@kluniversity")

def fix_roles():
    with app.app_context():
        print("=" * 60)
        print("🔧 Fixing User Roles...")
        print("=" * 60)
        
        all_users = User.query.all()
        fixed_count = 0
        
        for user in all_users:
            old_role = user.role
            
            if user.email == ADMIN_EMAIL:
                # This is the admin - must be Admin
                if user.role != 'Admin':
                    user.role = 'Admin'
                    fixed_count += 1
                    print(f"✅ Fixed {user.email}: {old_role} → Admin")
                else:
                    print(f"✓ {user.email}: Already Admin (correct)")
            else:
                # Everyone else must be Regular User
                if user.role != 'Regular User':
                    user.role = 'Regular User'
                    fixed_count += 1
                    print(f"✅ Fixed {user.email}: {old_role} → Regular User")
                else:
                    print(f"✓ {user.email}: Already Regular User (correct)")
        
        if fixed_count > 0:
            db.session.commit()
            print(f"\n✅ Fixed {fixed_count} user(s)")
        else:
            print("\n✅ No fixes needed - all roles are correct!")
        
        print("\n" + "=" * 60)
        print("📊 Final User Roles:")
        print("=" * 60)
        for user in User.query.all():
            print(f"   📧 {user.email} → {user.role}")
        print("=" * 60)

if __name__ == "__main__":
    fix_roles()