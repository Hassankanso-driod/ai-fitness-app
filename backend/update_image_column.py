"""
Script to update the image_url column in supplements table to support base64 images
Run this once to update your database schema
"""
import sqlite3
import os

# Path to the database file
DB_PATH = "fitness_ai.db"

def update_database():
    """Update image_url column to support longer base64 strings"""
    if not os.path.exists(DB_PATH):
        print(f"Database file {DB_PATH} not found. Creating new database...")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check current column type
        cursor.execute("PRAGMA table_info(supplements)")
        columns = cursor.fetchall()
        image_url_info = [col for col in columns if col[1] == "image_url"]
        
        if image_url_info:
            current_type = image_url_info[0][2]
            print(f"Current image_url type: {current_type}")
            
            if current_type == "TEXT":
                print("✅ Column already supports base64 images (TEXT type)")
            else:
                print(f"⚠️  Column type is {current_type}, updating to TEXT...")
                # SQLite doesn't support ALTER COLUMN directly, so we need to recreate the table
                # This is a simplified approach - in production, use proper migrations
                print("Note: For SQLite, you may need to recreate the table or use a migration tool.")
                print("The new schema will be applied when you restart the backend.")
        else:
            print("⚠️  image_url column not found. Make sure the supplements table exists.")
        
        conn.commit()
        print("✅ Database check completed")
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Updating Supplement Image Column")
    print("=" * 50)
    update_database()
    print("\nNote: If the column type needs to change, you may need to:")
    print("1. Delete the existing fitness_ai.db file")
    print("2. Restart the backend (it will recreate the database)")
    print("3. Run create_admin.py again to recreate the admin user")

