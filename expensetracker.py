from PIL import Image
import customtkinter as ctk
import pytesseract
from tkinter import filedialog
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

root = ctk.CTk()
root.title("Expense Tracker")
root.geometry("750x550")

label = ctk.CTkLabel(root, text="Expense Tracker", font=("Helvetica", 20))
label.pack()


def select_receipt():
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


root.mainloop()

