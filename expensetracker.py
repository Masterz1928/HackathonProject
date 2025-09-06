from PIL import Image
import customtkinter as ctk
import pytesseract
from tkinter import filedialog, ttk
from tkcalendar import Calendar
import re
import sqlite3
from datetime import datetime
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

root = ctk.CTk()
root.title("Expense Tracker")
root.geometry("750x550")

scrollable_frame = ctk.CTkScrollableFrame(root)
scrollable_frame.pack(fill="both", expand=True)

global text

label = ctk.CTkLabel(scrollable_frame, text="Expense Tracker", font=("Helvetica", 20))
label.pack()


def select_receipt():
    global text
    filepath = filedialog.askopenfilename(
        initialdir="/",
        title="Select a file",
        filetypes=(("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*"))
        )
    if filepath:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        Output.delete("1.0", "end")
        Output.insert("end", text)
    
select_recipt_button = ctk.CTkButton(scrollable_frame, text="Select a recipt", font=("Helventica", 20), command=select_receipt)
select_recipt_button.pack()


Output = ctk.CTkTextbox(scrollable_frame, width=500, height=300)
Output.pack()

def parse_receipt(text):
    """
    Parses the OCR text from a receipt to find the total amount.
    It now has a two-step approach for better accuracy.
    """
    # Attempt 1: Look for keywords like "total", "grand total", etc.
    keyword_pattern = r'(?:total|grand total|balance due|amount)\s*\D*(\d+\.?\d{2})'
    found_amounts = re.findall(keyword_pattern, text, re.IGNORECASE)
    
    if found_amounts:
        # If a keyword is found, return the last number found.
        return float(found_amounts[-1])
    else:
        # Attempt 2 (Fallback): Find a currency symbol (RM, S$, MYR, etc.) and pick the largest number after it.
        # This handles receipts without "Total" keywords and ignores account numbers.
        currency_pattern = r'\b(?:RM|MYR|S\$|USD|SGD|€)\s*(\d+\.?\d{2})'
        all_currency_amounts = re.findall(currency_pattern, text, re.IGNORECASE)
        
        if all_currency_amounts:
            # Convert to floats and return the maximum value.
            return max(float(n) for n in all_currency_amounts)
        else:
            return None

def parsing_and_display():
    text = Output.get("1.0", "end")
    parsed_total = parse_receipt(text)

    Output.delete("1.0", "end")
    if parsed_total is not None:
        Output.insert("end", f"Total Amount Found: ${parsed_total:.2f}")
        save_expense(parsed_total)
        load_expenses()
    else:
        Output.insert("end", "Could not find a total amount.")

parse_text = ctk.CTkButton(scrollable_frame, text="Parse", font=("Helventica", 20), command=parsing_and_display)
parse_text.pack()


# --- DATABASE SETUP AND FUNCTIONS ---
def setup_database():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            date TEXT,
            description TEXT,
            amount REAL
        )
    """)
    conn.commit()
    conn.close()

def save_expense(amount, description="Receipt from OCR"):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)",
                   (current_date, description, amount))
    conn.commit()
    conn.close()
    
def load_expenses(search_date=None):
    """
    Loads expenses from the database, either all or filtered by a date.
    If no records are found for the search date, it loads all records.
    """
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    records = []
    # Check if a search date was provided
    if search_date:
        # First, try to get records for the specific date.
        cursor.execute("SELECT * FROM expenses WHERE date LIKE ? ORDER BY date DESC", (search_date + '%',))
        records = cursor.fetchall()
    
    # Check if the list of records is empty. This handles both no search date and a search with no results.
    if not records:
        # If no records were found, load all records as a fallback.
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        records = cursor.fetchall()
    
    conn.close()
    
    # Clear the old data from the treeview
    for record in table_view.get_children():
        table_view.delete(record)
    
    # Group records by date for the daily summary
    daily_expenses = {}
    for record in records:
        date_only = record[0].split(' ')[0] # Extract the date part (YYYY-MM-DD)
        if date_only not in daily_expenses:
            daily_expenses[date_only] = {'total': 0.0, 'records': []}
        daily_expenses[date_only]['total'] += record[2]
        daily_expenses[date_only]['records'].append(record)
    
    # Insert the grouped records into the Treeview
    for date, data in daily_expenses.items():
        # Create a parent item for each date with the daily total
        parent_item = table_view.insert("", "end", text=date, open=True, values=(date, "Daily Total:", f"${data['total']:.2f}"))
        
        # Insert each individual expense as a child of the date parent
        for record in data['records']:
            table_view.insert(parent_item, "end", values=(record[0], record[1], f"${record[2]:.2f}"))

def on_treeview_scroll(event):
    """
    Handles mouse wheel events on the treeview to prevent them from bubbling up to the parent.
    """
    if event.delta > 0:
        table_view.yview_scroll(-1, "units")
    else:
        table_view.yview_scroll(1, "units")
    # Return 'break' to stop the event from propagating to the parent frame
    return "break"


table_label = ctk.CTkLabel(scrollable_frame, text="All Expenses", font=("Helvetica", 20, "bold"))
table_label.pack(pady=(10, 5))

table_frame = ctk.CTkFrame(scrollable_frame)
table_frame.pack(pady=5, padx=20, fill="x", expand=True)

table_view = ttk.Treeview(table_frame, columns=("Date", "Description", "Amount"), show="headings", height=15)
table_view.pack(side="left", fill="both", expand=True)
table_view.bind("<MouseWheel>", on_treeview_scroll)

# Style the Treeview to match the dark theme
style = ttk.Style()
style.theme_use("default") # Use a base theme to build upon
style.configure("Treeview",
                background="#2a2d2e",
                foreground="#fff",
                rowheight=25,
                fieldbackground="#343638",
                bordercolor="#343638",
                font=("Helvetica", 16)) # Set the font for the data rows
style.map('Treeview',
          background=[('selected', '#2b6e6e')])
style.configure("Treeview.Heading",
                font=("Helvetica", 12, "bold"),
                background="#343638",
                foreground="#fff")


table_view.heading("Date", text="Date")
table_view.heading("Description", text="Description")
table_view.heading("Amount", text="Amount")

table_view.column("Date", width=150, anchor="center")
table_view.column("Description", width=250, anchor="w")
table_view.column("Amount", width=100, anchor="e")

scrollbar = ctk.CTkScrollbar(table_frame, command=table_view.yview)
scrollbar.pack(side="right", fill="y")
table_view.configure(yscrollcommand=scrollbar.set)

CalanderDisplay = Calendar(scrollable_frame, width=150, height=300)
CalanderDisplay.pack()

def Get_date():
    selected_date_str = CalanderDisplay.get_date()
    print(f"{selected_date_str}")
    date_object = datetime.strptime(selected_date_str, '%m/%d/%y')
    database_date = date_object.strftime('%Y-%m-%d')
    load_expenses(search_date=database_date)

Search_date = ctk.CTkButton(scrollable_frame, text="Search date", command=Get_date)
Search_date.pack()


setup_database()
load_expenses()

root.mainloop()
