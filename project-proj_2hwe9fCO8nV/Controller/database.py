import sqlite3
import os

# 1. Setup Folder & Connection Path
# __file__ is a special Python variable that gets the exact path of this current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level ('..') and into the 'Storage' folder, just like in your JS
storage_dir = os.path.join(current_dir, '..', 'Storage')

# Create the folder if it doesn't exist (Python's version of fs.existsSync + fs.mkdrSync)
os.makedirs(storage_dir, exist_ok=True)

# The final path to your database file
db_path = os.path.join(storage_dir, 'databasefinance.db')

def get_db_connection():
    """Establishes the connection and enables foreign keys."""
    try:
        conn = sqlite3.connect(db_path)
        
        # This formats the data perfectly for your React frontend
        conn.row_factory = sqlite3.Row 
        
        # Enable Foreign Keys for cascading deletes (Crucial for your junction table!)
        conn.execute("PRAGMA foreign_keys = ON")
        
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None