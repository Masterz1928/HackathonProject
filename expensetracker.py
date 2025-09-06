from PIL import Image
import customtkinter as ctk
import pytesseract

root = ctk.CTk()
root.title("Expense Tracker")
root.geometry("750x550")

label = ctk.CTkLabel(root, text="Expense Tracker", font=("Helvetica", 20))
label.pack()

root.mainloop()


img = Image.open("moni.jpg")  # put a small receipt image here
text = pytesseract.image_to_string(img)
print("---- OCR Output ----")
print(text)
