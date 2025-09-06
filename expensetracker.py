from PIL import Image
import customtkinter as ctk
import pytesseract
from tkinter import filedialog
import re
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
    Parses the OCR text from a receipt to find the total amount using a smarter regex.
    This function now finds ALL matches and returns the LAST one, which is more
    likely to be the final total.
    """
    # The regex pattern looks for keywords like "total", "grand total", etc.
    # and then captures the number that follows.
    pattern = r'(?:total|grand total|balance due|amount)\s*\D*(\d+\.?\d{2})'
    
    # Use re.findall to find all non-overlapping matches.
    # The list will contain only the captured group (the number).
    found_amounts = re.findall(pattern, text, re.IGNORECASE)
    
    if found_amounts:
        # Get the last item in the list, which is the most likely candidate for the final total.
        total_amount = found_amounts[-1]
        return float(total_amount)
    else:
        return None

def parsing_and_display():
    text = Output.get("1.0", "end")
    parsed_total = parse_receipt(text)

    Output.delete("1.0", "end")
    if parsed_total is not None:
        Output.insert("end", f"Total Amount Found: ${parsed_total:.2f}")
    else:
        Output.insert("end", "Could not find a total amount.")


parse_text = ctk.CTkButton(root, text="Parse", font=("Helventica", 20), command=parsing_and_display)
parse_text.pack()


root.mainloop()

