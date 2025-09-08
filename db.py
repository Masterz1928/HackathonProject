import sqlite3
from datetime import datetime
from CRUD import load_expenses

records = ""

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
    # New table to store daily totals
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_totals (
            date TEXT PRIMARY KEY,
            total REAL
        )
    """)
    conn.commit()
    conn.close()

# MODIFIED: Added expense_date parameter
def save_expense(amount, description="Receipt from OCR", expense_date=None):
    """
    Saves a new expense record and updates the daily total in the database.
    """
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    # MODIFIED: Use the provided date, or default to the current date if none is provided.
    if expense_date is None:
        current_date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        current_date_str = expense_date

    cursor.execute("INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)",
                   (current_date_str, description, amount))
    
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date = ?", (current_date_str,))
    total_for_day = cursor.fetchone()[0]
    
    cursor.execute("INSERT OR REPLACE INTO daily_totals (date, total) VALUES (?, ?)",
                   (current_date_str, total_for_day))
    
    conn.commit()
    conn.close()
    
def load_expenses(search_date=None):
    """
    Loads all expenses from the database and returns them.
    """
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()

        if search_date:
            cursor.execute(
                "SELECT * FROM expenses WHERE date LIKE ? ORDER BY date DESC",
                (search_date + "%",),
            )
        else:
            cursor.execute("SELECT * FROM expenses ORDER BY date DESC")

        records = cursor.fetchall()

    return records

"""
    for record in table_view.get_children():
        table_view.delete(record)

    for record in records:
        table_view.insert("", "end", values=(record[0], record[1], f"${record[2]:.2f}"))

        
                
"""

data = load_expenses()
print(data)  # For testing purposes, print the loaded expenses
