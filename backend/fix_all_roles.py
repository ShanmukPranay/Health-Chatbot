#!/usr/bin/env python
# fix_all_roles.py - Fix ALL users to correct roles

from app import app, db, User
from dotenv import load_dotenv
import os

load_dotenv()

# Your admin email - ONLY this email stays as Admin
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "2300031563@kluniversity")

def fix_all_roles():
    with app.app_context():
        print("=" * 70)
        print("🔧 FIXING ALL USER ROLES...")
        print("=" * 70)
        
        all_users = User.query.all()
        changes = []
        
        for user in all_users:
            old_role = user.role
            new_role = old_role  # Default no change
            
            # RULE 1: Only ONE specific email can be Admin
            if user.email == ADMIN_EMAIL:
                if old_role != "Admin":
                    new_role = "Admin"
                    changes.append(f"   {user.email}: {old_role} → Admin")
                else:
                    print(f"✓ {user.email}: Already Admin (CORRECT)")
            else:
                # RULE 2: Everyone else must be "Regular User"
                if old_role != "Regular User":
                    new_role = "Regular User"
                    changes.append(f"   {user.email}: {old_role} → Regular User")
                else:
                    print(f"✓ {user.email}: Already Regular User (CORRECT)")
            
            # Apply the change if needed
            if new_role != old_role:
                user.role = new_role
        
        if changes:
            db.session.commit()
            print("\n" + "=" * 70)
            print("✅ CHANGES MADE:")
            print("=" * 70)
            for change in changes:
                print(change)
        else:
            print("\n✅ No changes needed - all roles are correct!")
        
        print("\n" + "=" * 70)
        print("📊 FINAL USER ROLES:")
        print("=" * 70)
        for user in User.query.all():
            badge = "👑 ADMIN" if user.role == "Admin" else "👤 Regular User"
            print(f"   {user.email}: {user.role} {badge}")
        print("=" * 70)

if __name__ == "__main__":
    fix_all_roles()