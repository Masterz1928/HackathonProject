import customtkinter as ctk
import pytesseract
from PIL import Image
from tkinter import filedialog, ttk
from tkcalendar import Calendar
import re
from datetime import datetime
import sys
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Import all database functions from the separate CRUD file
from CRUD import setup_database, save_expense, load_expenses, get_daily_totals

# Set the path to the Tesseract executable
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except FileNotFoundError:
    print("Tesseract executable not found. Please check the path.", file=sys.stderr)
    
# --- GLOBAL VARIABLES & FUNCTIONS ---
global plot_canvas
plot_canvas = None 
global receipt_text
receipt_text = ""


def show_daily_totals_plot():
    """
    Fetches daily totals from the database and displays them as a bar graph.
    """
    global plot_canvas
    
    # 1. Clear any existing plot and widgets in the stats frame
    if plot_canvas:
        plot_canvas.get_tk_widget().destroy()
        plt.close('all') # Close all existing matplotlib figures
        plot_canvas = None

    for widget in stats_frame.winfo_children():
        widget.destroy()

    # 2. Fetch data from the database using the new CRUD function
    records = get_daily_totals()

    if not records:
        no_data_label = ctk.CTkLabel(stats_frame, text="No daily totals found to display.", font=("Helvetica", 16))
        no_data_label.pack(pady=20)
        return

    dates = [row[0] for row in records]
    totals = [row[1] for row in records]
    
    # 3. Create the plot
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
    
    # 4. Embed the plot in the Tkinter window
    plot_canvas = FigureCanvasTkAgg(fig, master=stats_frame)
    plot_canvas.draw()
    plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


def on_tab_change(event):
    """
    Handles tab changes in the notebook to load the correct data.
    """
    selected_tab_text = notebook1.tab(notebook1.select(), "text")
    if selected_tab_text == "Records":
        update_records_treeview()
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


def parsing_and_display():
    """
    This function gets the text, parses it, saves it to the DB, and displays the result.
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
        # Get the selected date from the calendar on the "Add Expense" tab
        selected_date_str = add_expense_calendar.get_date()
        date_object = datetime.strptime(selected_date_str, "%m/%d/%y")
        expense_date = date_object.strftime('%Y-%m-%d')
        
        # Save expense to the database
        save_expense(parsed_total, expense_date=expense_date)
        
        output_textbox.insert("end", f"Successfully saved: Amount ${parsed_total:.2f} on {expense_date}")
        
        # Refresh the records and switch to the Statistics tab
        update_records_treeview()
        notebook1.select(2)
    else:
        output_textbox.insert("end", "[Error] Could not find a total amount.")


def update_records_treeview(search_date=None):
    """
    This function fetches expenses from the database and updates the Treeview.
    It can be called with an optional search_date to filter the records.
    """
    # Clear existing data in the Treeview
    for record in table_view.get_children():
        table_view.delete(record)
    
    # Load data from the database (filtered or all)
    data = load_expenses(search_date=search_date)

    # Insert new data into the Treeview
    for record in data:
        table_view.insert("", "end", values=(record[0], record[1], f"${record[2]:.2f}"))


def filter_by_date():
    """
    This function gets the selected date from the calendar and calls
    update_records_treeview with that date to filter the records.
    """
    selected_date_str = filter_calendar.get_date()
    date_object = datetime.strptime(selected_date_str, "%Y-%m-%d")
    database_date = date_object.strftime('%Y-%m-%d')
    
    update_records_treeview(search_date=database_date)

def on_treeview_scroll(event):
    """
    Handles mouse wheel events on the treeview.
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

# Frames for each tab
frame1 = ctk.CTkFrame(notebook1)
frame1.pack(fill='both', expand=True)
frame2 = ctk.CTkFrame(notebook1)
frame2.pack(fill='both', expand=True)
frame3 = ctk.CTkFrame(notebook1)
frame3.pack(fill='both', expand=True)

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

calendar_label = ctk.CTkLabel(add_expense_scrollable_frame, text="Select a Date", font=("Helvetica", 16))
calendar_label.pack(pady=(10, 5))

add_expense_calendar = Calendar(add_expense_scrollable_frame, selectmode='day', font="Helvetica 12")
add_expense_calendar.pack(pady=5)


# --- Frame 2: Records ---
records_scrollable_frame = ctk.CTkScrollableFrame(frame2)
records_scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Filter UI Frame
filter_frame = ctk.CTkFrame(records_scrollable_frame)
filter_frame.pack(pady=10, padx=10, fill="x")

calendar_label = ctk.CTkLabel(filter_frame, text="Filter by Date", font=("Helvetica", 16, "bold"))
calendar_label.pack(side="left", padx=(10,5))

filter_calendar = Calendar(filter_frame, selectmode='day', font="Helvetica 12", date_pattern='y-mm-dd')
filter_calendar.pack(side="left", padx=5)

search_date_button = ctk.CTkButton(filter_frame, text="Search", font=("Helvetica", 14), command=filter_by_date, width=100)
search_date_button.pack(side="left", padx=5)

show_all_button = ctk.CTkButton(filter_frame, text="Show All", font=("Helvetica", 14), command=lambda: update_records_treeview(), width=100)
show_all_button.pack(side="left", padx=5)

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

scrollbar = ctk.CTkScrollbar(table_frame, command=table_view.yview)
scrollbar.pack(side="right", fill="y")
table_view.configure(yscrollcommand=scrollbar.set)

# --- Frame 3: Statistics ---
statistics_scrollable_frame = ctk.CTkScrollableFrame(frame3)
statistics_scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

stats_label = ctk.CTkLabel(statistics_scrollable_frame, text="Daily Totals", font=("Helvetica", 24, "bold"))
stats_label.pack(pady=(0, 20))

stats_frame = ctk.CTkFrame(statistics_scrollable_frame)
stats_frame.pack(fill="both", expand=True)

# Initial setup: call the database setup and load expenses on app startup
setup_database()
update_records_treeview()

root.mainloop()