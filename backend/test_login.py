"""
test_login.py - Test admin login

This script tests if the admin account can login successfully.
Run this to verify login is working:
    python test_login.py
"""

from database import SessionLocal
from models import User
from auth import verify_password

def test_admin_login():
    """Test if admin can login with password admin123"""
    db = SessionLocal()
    try:
        # Find admin user
        admin = db.query(User).filter(User.first_name == "admin").first()
        
        if not admin:
            print("[ERROR] Admin user not found!")
            print("Run: python create_admin.py")
            return False
        
        # Test password
        password_correct = verify_password("admin123", admin.password)
        
        if password_correct:
            print("[SUCCESS] Admin login test PASSED!")
            print(f"   Username: admin")
            print(f"   Password: admin123 (CORRECT)")
            print(f"   Role: {admin.role}")
            print(f"   Active: {admin.active}")
            print(f"   User ID: {admin.id}")
            return True
        else:
            print("[ERROR] Password verification FAILED!")
            print("Password hash might be incorrect.")
            print("Run: python create_admin.py to reset password")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing admin login...")
    test_admin_login()

