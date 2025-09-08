from PIL import Image
import customtkinter as ctk
import pytesseract
from tkinter import filedialog, ttk
from tkcalendar import Calendar
import re
import sqlite3
from datetime import datetime, timedelta # ADDED: Import timedelta
import sys
import tkinter as tk 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from CRUD import setup_database, save_expense, load_expenses

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


def show_daily_totals_plot():
    """
    Fetches daily totals and displays them as a bar graph.
    """
    global plot_canvas
    
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    print("Executing query: SELECT * FROM daily_totals ORDER BY date ASC")
    cursor.execute("SELECT * FROM daily_totals ORDER BY date ASC")
    
    records = cursor.fetchall()
    conn.close()

    print("Records fetched from daily_totals:", records)

    if plot_canvas:
        plt.close(plot_canvas.figure)
        plot_canvas.get_tk_widget().destroy()
        plot_canvas = None
    
    for widget in stats_frame.winfo_children():
        widget.destroy()

    if not records:
        print("No records found, displaying 'No data' label.")
        no_data_label = ctk.CTkLabel(stats_frame, text="No daily totals found to display.", font=("Helvetica", 16))
        no_data_label.pack(pady=20)
        return

    dates = [row[0] for row in records]
    totals = [row[1] for row in records]
    
    print("Dates to plot:", dates)
    print("Totals to plot:", totals)
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    fig.patch.set_facecolor('#2b2d2e')
    ax.set_facecolor('#2b2d2e')
    
    ax.bar(dates, totals, color='#0078b6')
    ax.set_title("Daily Expense Totals", color='white')
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel("Total Amount ($)", color='white')
    
    if len(dates) > 5:
        plt.xticks(rotation=45, ha='right', color='white')
    else:
        plt.xticks(rotation=0, color='white')
    plt.yticks(color='white')
    plt.tight_layout()
    
    plot_canvas = FigureCanvasTkAgg(fig, master=stats_frame)
    plot_canvas.draw()
    plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    print("Plot canvas has been drawn and packed.")


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
    keyword_pattern = r'(?:total|grand total|balance due|amount)\s*\D*(\d+\.?\d{2})'
    found_amounts = re.findall(keyword_pattern, text, re.IGNORECASE)
    
    if found_amounts:
        return float(found_amounts[-1])
    else:
        currency_pattern = r'\b(?:RM|MYR|S\$|USD|SGD|€)\s*(\d+\.?\d{2})'
        all_currency_amounts = re.findall(currency_pattern, text, re.IGNORECASE)
        
        if all_currency_amounts:
            return max(float(n) for n in all_currency_amounts)
        else:
            return None

def split_text_and_numbers(user_input):
    pattern = re.compile(r'(\d+\.?\d*|\D+)')
    return pattern.findall(user_input)

# MODIFIED: Updated to get the date from the calendar
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
            break
        except ValueError:
            continue

    if parsed_total is None:
        parsed_total = parse_receipt(user_input)

    output_textbox.delete("1.0", "end")
    if parsed_total is not None:
        output_textbox.insert("end", f"Saved: Amount ${parsed_total:.2f}")
        
        # ADDED CODE: Get the selected date from the calendar
        selected_date_str = calendar_widget.get_date()
        date_object = datetime.strptime(selected_date_str, "%m/%d/%y")
        expense_date = date_object.strftime('%Y-%m-%d')
        
        # MODIFIED: Pass the new date to the save_expense function
        save_expense(parsed_total, expense_date=expense_date)
        
        load_expenses()
        show_daily_totals_plot()
        notebook1.select(2) # Switch to the Statistics tab
    else:
        output_textbox.insert("end", "[Error] Could not find a total amount.")


def filter_by_date():
    """
    This function gets the selected date from the calendar and calls
    load_expenses with that date to filter the records.
    """
    selected_date_str = calendar_widget.get_date()
    date_object = datetime.strptime(selected_date_str, "%m/%d/%y")
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
    return "break"

# --- UI COMPONENTS ---
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Expense Tracker")
root.geometry("750x650")

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

style = ttk.Style()
style.theme_use("default")
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


# Treeveiw for all expenses 
data = load_expenses()
for record in table_view.get_children():
    table_view.delete(record)

for record in data:
    table_view.insert("", "end", values=(record[0], record[1], f"${record[2]:.2f}"))

scrollbar = ctk.CTkScrollbar(table_frame, command=table_view.yview)
scrollbar.pack(side="right", fill="y")
table_view.configure(yscrollcommand=scrollbar.set)

# Call the database setup and load expenses on app startup
setup_database()
load_expenses()

root.mainloop()