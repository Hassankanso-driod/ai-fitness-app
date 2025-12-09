"""
create_admin.py - Script to create admin user in database

This script creates an admin user with:
- Username: admin
- Password: admin123
- Role: admin

Run this script once to set up the admin account:
    python create_admin.py

Note: Make sure MySQL database is running and configured in database.py
"""

from database import SessionLocal
from models import User
from auth import hash_password

def create_admin_user():
    """
    Create admin user if it doesn't exist
    Calculates BMI and BMR automatically like regular users
    """
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.first_name == "admin").first()
        
        if admin:
            # Reset password to ensure it's correct
            print("[INFO] Admin user already exists. Resetting password...")
            admin.password = hash_password("admin123")
            admin.active = True
            admin.role = "admin"
            db.commit()
            db.refresh(admin)
            print("[SUCCESS] Admin password reset successfully!")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"   Role: {admin.role}")
            print(f"   Active: {admin.active}")
            return admin
        
        # Admin user details
        first_name = "admin"
        password = "admin123"
        sex = "male"
        age = 30
        height_cm = 175.0
        weight_kg = 75.0
        goal = "maintain"
        
        # Calculate water intake
        water_intake = round(weight_kg * 0.033, 2)
        
        # Calculate BMI
        height_m = height_cm / 100
        bmi = round(weight_kg / (height_m ** 2), 2)
        
        # Calculate BMR (Mifflin-St Jeor Equation for male)
        bmr = round(10 * weight_kg + 6.25 * height_cm - 5 * age + 5, 0)
        
        # Create new admin user
        admin_user = User(
            first_name=first_name,
            password=hash_password(password),
            role="admin",
            sex=sex,
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            goal=goal,
            active=True,
            water_intake_l=water_intake,
            bmi=bmi,
            bmr=bmr,
            email=None  # Email is optional
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("[SUCCESS] Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Role: admin")
        print(f"   BMI: {bmi}")
        print(f"   BMR: {bmr} kcal")
        print(f"   Water Intake: {water_intake}L/day")
        return admin_user
        
    except Exception as e:
        print(f"[ERROR] Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating admin user...")
    create_admin_user()
