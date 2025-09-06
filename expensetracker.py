from PIL import Image
import customtkinter as ctk
import pytesseract
from tkinter import filedialog, ttk
import re
import sqlite3
import datetime

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

root = ctk.CTk()
root.title("Expense Tracker")
root.geometry("750x550")

global text

label = ctk.CTkLabel(root, text="Expense Tracker", font=("Helvetica", 20))
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
    
select_recipt_button = ctk.CTkButton(root, text="Select a recipt", font=("Helventica", 20), command=select_receipt)
select_recipt_button.pack()

Output = ctk.CTkTextbox(root, width=500, height=300)
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

parse_text = ctk.CTkButton(root, text="Parse", font=("Helventica", 20), command=parsing_and_display)
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
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)",
                   (current_date, description, amount))
    conn.commit()
    conn.close()
    
def load_expenses():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY amount DESC")
    records = cursor.fetchall()
    conn.close()
    
    # Clear the old data from the treeview
    for record in table_view.get_children():
        table_view.delete(record)
    
    # Add each record to the table view
    for record in records:
        table_view.insert("", "end", values=record)


table_label = ctk.CTkLabel(root, text="All Expenses", font=("Helvetica", 20, "bold"))
table_label.pack(pady=(10, 5))

table_frame = ctk.CTkFrame(root)
table_frame.pack(pady=5, padx=20, fill="x", expand=True)

table_view = ttk.Treeview(table_frame, columns=("Date", "Description", "Amount"), show="headings")
table_view.pack(side="left", fill="both", expand=True)

table_view.heading("Date", text="Date")
table_view.heading("Description", text="Description")
table_view.heading("Amount", text="Amount")

table_view.column("Date", width=150, anchor="center")
table_view.column("Description", width=250, anchor="w")
table_view.column("Amount", width=100, anchor="e")

scrollbar = ctk.CTkScrollbar(table_frame, command=table_view.yview)
scrollbar.pack(side="right", fill="y")
table_view.configure(yscrollcommand=scrollbar.set)

setup_database()
load_expenses()

root.mainloop()
