import sqlite3
from datetime import datetime 

def setup_database():
    """
    Initializes the SQLite database and creates both the expenses and daily_totals tables.
    """
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            date TEXT,
            description TEXT,
            amount REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_totals (
            date TEXT PRIMARY KEY,
            total REAL
        )
    """)
    conn.commit()
    conn.close()

def save_expense(amount, description="Receipt from OCR", expense_date=None):
    """
    Saves a new expense record and updates the daily total in the database.
    """
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    if expense_date is None:
        current_date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        current_date_str = expense_date

    try:
        cursor.execute("INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)",
                       (current_date_str, description, float(amount)))
        
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date = ?", (current_date_str,))
        total_for_day = cursor.fetchone()[0]
        
        cursor.execute("INSERT OR REPLACE INTO daily_totals (date, total) VALUES (?, ?)",
                       (current_date_str, total_for_day))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
    
def load_expenses(search_date=None):
    """
    Loads expenses from the database, optionally filtered by date.
    Returns a list of records.
    """
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        if search_date:
            # Using an exact match for date, which is more robust
            cursor.execute(
                "SELECT * FROM expenses WHERE date = ? ORDER BY date DESC",
                (search_date,),
            )
        else:
            cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        records = cursor.fetchall()
    return records
    
def get_daily_totals():
    """
    Loads daily totals from the database, ordered by date.
    Returns a list of records.
    """
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_totals ORDER BY date ASC")
        records = cursor.fetchall()
    return records