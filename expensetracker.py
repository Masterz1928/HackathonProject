from PIL import Image
import customtkinter as ctk
import pytesseract
from tkinter import filedialog, ttk
from tkcalendar import Calendar
import re
import sqlite3
from datetime import datetime
import sys
import tkinter as tk 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Set the path to the Tesseract executable
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except FileNotFoundError:
    print("Tesseract executable not found. Please check the path.", file=sys.stderr)
    
# --- GLOBAL VARIABLES & FUNCTIONS ---
# Global variable to store OCR text for sharing between functions
global plot_canvas
plot_canvas = None 
global receipt_text
receipt_text = ""

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

def save_expense(amount, description="Receipt from OCR"):
    """
    Saves a new expense record and updates the daily total in the database.
    """
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    # Fixed the datetime call by removing the extra 'datetime'
    current_datetime_str = datetime.now().strftime("%Y-%m-%d")
    current_date_str = datetime.now().strftime("%Y-%m-%d")

    # 1. Insert the individual expense record
    cursor.execute("INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)",
                   (current_datetime_str, description, amount))
    
    # 2. Check if a total for the current date already exists
    cursor.execute("SELECT total FROM daily_totals WHERE date = ?", (current_date_str,))
    existing_total = cursor.fetchone()

    if existing_total:
        # If the date exists, update the total by adding the new amount
        new_total = existing_total[0] + amount
        cursor.execute("UPDATE daily_totals SET total = ? WHERE date = ?", (new_total, current_date_str))
    else:
        # If the date is new, insert a new record with the amount
        cursor.execute("INSERT INTO daily_totals (date, total) VALUES (?, ?)", (current_date_str, amount))
        
    conn.commit()
    conn.close()
    
def load_expenses(search_date=None):
    """
    Loads all expenses from the database and displays them in a flat list.
    """
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    # Get all individual records directly for a flat view
    if search_date:
        cursor.execute("SELECT * FROM expenses WHERE date LIKE ? ORDER BY date DESC", (search_date + '%',))
    else:
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    
    records = cursor.fetchall()
    conn.close()
    
    # Clear the old data from the treeview
    for record in table_view.get_children():
        table_view.delete(record)
    
    # Insert individual expenses directly into the Treeview
    for record in records:
        table_view.insert("", "end", values=(record[0], record[1], f"${record[2]:.2f}"))


def show_daily_totals_plot():
    """
    Fetches daily totals and displays them as a bar graph.
    """
    # NEW: Use the global variable to manage the canvas
    global plot_canvas
    
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM daily_totals ORDER BY date ASC")
    records = cursor.fetchall()
    conn.close()

    # NEW: Check for and explicitly close the old figure before destroying the canvas
    if plot_canvas:
        # Closes the Matplotlib figure, which should stop pending 'after' commands
        plt.close(plot_canvas.figure)
        # Destroys the Tkinter canvas widget
        plot_canvas.get_tk_widget().destroy()
        # Reset the global variable
        plot_canvas = None
    
    # Clear any "No data" label that might be present
    for widget in stats_frame.winfo_children():
        widget.destroy()

    if not records:
        no_data_label = ctk.CTkLabel(stats_frame, text="No daily totals found to display.", font=("Helvetica", 16))
        no_data_label.pack(pady=20)
        return

    dates = [row[0] for row in records]
    totals = [row[1] for row in records]
    
    # Configure Matplotlib to match the dark theme
    plt.style.use('dark_background')
    
    # Create the figure and axes for the plot
    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    fig.patch.set_facecolor('#2b2d2e')
    ax.set_facecolor('#2b2d2e')
    
    # Plot the bar chart
    ax.bar(dates, totals, color='#0078b6')
    ax.set_title("Daily Expense Totals", color='white')
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel("Total Amount ($)", color='white')
    
    # Adjust x-tick labels for readability based on the number of data points
    if len(dates) > 5:
        plt.xticks(rotation=45, ha='right', color='white')
    else:
        plt.xticks(rotation=0, color='white') # No rotation for a few points
    plt.yticks(color='white')
    plt.tight_layout()
    
    # Embed the plot in a standard tkinter canvas
    plot_canvas = FigureCanvasTkAgg(fig, master=stats_frame)
    plot_canvas.draw()
    plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
def on_tab_change(event):
    """
    Handles tab changes in the notebook to load the correct data.
    """
    selected_tab_text = notebook1.tab(notebook1.select(), "text")
    if selected_tab_text == "Records":
        load_expenses()
    elif selected_tab_text == "Statistics":
        show_daily_totals_plot()


def select_receipt():
    """
    Prompts the user to select an image file (receipt) and displays the OCR text.
    """
    global receipt_text
    filepath = filedialog.askopenfilename(
        initialdir="/",
        title="Select a file",
        filetypes=(("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*"))
        )
    if filepath:
        img = Image.open(filepath)
        receipt_text = pytesseract.image_to_string(img)
        output_textbox.delete("1.0", "end")
        output_textbox.insert("end", receipt_text)

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

def split_text_and_numbers(user_input):
    pattern = re.compile(r'(\d+\.?\d*|\D+)')
    return pattern.findall(user_input)

def parsing_and_display():
    """
    This function gets the text from the global variable,
    parses it, saves it to the DB, and displays the result.
    """
    user_input = output_textbox.get("1.0", "end").strip()
    parsed_total = None

    components = split_text_and_numbers(user_input)
    
    for part in components:
        try:
            parsed_total = float(part)
            break # Stop after we find the first number
        except ValueError:
            continue # Skip to the next part if it's not a number

    if parsed_total is None:
        parsed_total = parse_receipt(user_input)

    output_textbox.delete("1.0", "end")
    if parsed_total is not None:
        output_textbox.insert("end", f"Saved: Amount ${parsed_total:.2f}")
        save_expense(parsed_total)
        load_expenses()
    else:
        output_textbox.insert("end", "[Error] Could not find a total amount.")


def filter_by_date():
    """
    This function gets the selected date from the calendar and calls
    load_expenses with that date to filter the records.
    """
    selected_date_str = calendar_widget.get_date()
    # The calendar provides MM/DD/YY, but the database stores YYYY-MM-DD
    date_object = datetime.strptime(selected_date_str)
    database_date = date_object.strftime('%Y-%m-%d')
    load_expenses(search_date=database_date)

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

# --- UI COMPONENTS ---
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Expense Tracker")
root.geometry("750x650")

#Adding in notepad view for organization
notebook1 = ttk.Notebook(root)
notebook1.pack(expand=True, fill="both")
notebook1.bind("<<NotebookTabChanged>>", on_tab_change)

frame1 = ctk.CTkFrame(notebook1)
frame1.pack(fill='both', expand=True)

frame2 = ctk.CTkFrame(notebook1)
frame2.pack(fill='both', expand=True)

frame3 = ctk.CTkFrame(notebook1)
frame3.pack(fill='both', expand=True)

statistics_scrollable_frame = ctk.CTkScrollableFrame(frame3)
statistics_scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
stats_frame = ctk.CTkFrame(statistics_scrollable_frame)
stats_frame.pack(fill="both", expand=True) 

stats_label = ctk.CTkLabel(statistics_scrollable_frame, text="Daily Totals", font=("Helvetica", 24, "bold"))
stats_label.pack(pady=(0, 20))

notebook1.add(frame1, text="Add in Expense")
notebook1.add(frame2, text="Records")
notebook1.add(frame3, text="Statistics")

# --- Frame 1: Add Expense ---
add_expense_scrollable_frame = ctk.CTkScrollableFrame(frame1)
add_expense_scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

label = ctk.CTkLabel(add_expense_scrollable_frame, text="Expense Tracker", font=("Helvetica", 24, "bold"))
label.pack(pady=(0, 20))

select_recipt_button = ctk.CTkButton(add_expense_scrollable_frame, text="Select a receipt", font=("Helvetica", 16), command=select_receipt)
select_recipt_button.pack(pady=(10, 5))

manual_entry_label = ctk.CTkLabel(add_expense_scrollable_frame, text="Or type in manually", font=("Helvetica", 16))
manual_entry_label.pack(pady=(10, 5))

output_textbox = ctk.CTkTextbox(add_expense_scrollable_frame, width=500, height=150)
output_textbox.pack(pady=10)

parse_and_save_button = ctk.CTkButton(add_expense_scrollable_frame, text="Save Expense", font=("Helvetica", 16), command=parsing_and_display)
parse_and_save_button.pack(pady=5)

# --- Frame 2: Records ---
records_scrollable_frame = ctk.CTkScrollableFrame(frame2)
records_scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Calendar and Search UI
calendar_label = ctk.CTkLabel(records_scrollable_frame, text="Filter by Date", font=("Helvetica", 20, "bold"))
calendar_label.pack(pady=(20, 5))

calendar_widget = Calendar(records_scrollable_frame, selectmode='day', font="Helvetica 12")
calendar_widget.pack(pady=5)

search_date_button = ctk.CTkButton(records_scrollable_frame, text="Search by Date", font=("Helvetica", 16), command=filter_by_date)
search_date_button.pack(pady=5)

show_all_button = ctk.CTkButton(records_scrollable_frame, text="Show All Expenses", font=("Helvetica", 16), command=lambda: load_expenses())
show_all_button.pack(pady=5)

# Treeview Table UI
table_label = ctk.CTkLabel(records_scrollable_frame, text="All Expenses", font=("Helvetica", 20, "bold"))
table_label.pack(pady=(20, 5))

# Style the Treeview to match the dark theme
style = ttk.Style()
style.theme_use("default") # Use a base theme to build upon
style.configure("Treeview",
                background="#2b2d2e",
                foreground="#fff",
                rowheight=25,
                fieldbackground="#2b2d2e",
                bordercolor="#333333",
                font=("Helvetica", 12))
style.map('Treeview',
          background=[('selected', '#0078b6')])
style.configure("Treeview.Heading",
                font=("Helvetica", 12, "bold"),
                background="#1f1f1f",
                foreground="#fff")

table_frame = ctk.CTkFrame(records_scrollable_frame)
table_frame.pack(pady=5, padx=20, fill="both", expand=True)

table_view = ttk.Treeview(table_frame, columns=("Date", "Description", "Amount"), show="headings", height=15)
table_view.pack(side="left", fill="both", expand=True)

table_view.bind("<MouseWheel>", on_treeview_scroll)

table_view.heading("Date", text="Date")
table_view.heading("Description", text="Description")
table_view.heading("Amount", text="Amount")

table_view.column("Date", width=150, anchor="center")
table_view.column("Description", width=250, anchor="w")
table_view.column("Amount", width=100, anchor="e")

scrollbar = ctk.CTkScrollbar(table_frame, command=table_view.yview)
scrollbar.pack(side="right", fill="y")
table_view.configure(yscrollcommand=scrollbar.set)

# Call the database setup and load expenses on app startup
setup_database()
load_expenses()

root.mainloop()
