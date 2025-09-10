from flask import Flask, jsonify, request 
import re
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

@app.route("/")
def Test():
    return "Server is running"

def get_text_from_image_api(image_data):
    """
    Placeholder for a cloud-based OCR API call.
    In a real-world scenario, this would send image_data to an API like
    Google Cloud Vision API and return the extracted text.
    For demonstration purposes, it currently returns mock data.
    """
    print("Simulating cloud OCR API call...")
    
    # Returning a sample receipt text to test the parsing logic
    return """
    GROCERY STORE
    123 Main Street
    Anytown, USA
    --------------------
    Milk                 2.99
    Bread                3.50
    Eggs                 4.25
    Subtotal            10.74
    Tax                  0.86
    Total               11.60
    Credit Card
    --------------------
    """

@app.route("/api/parse_receipt", methods=["POST"])
def parse_receipt(text):

    print("--- Parsing Receipt ---")
    print(f"Original Text:\n{text}\n")

    # This regex is flexible, handling different keywords, currency symbols, and number formats.
    total_pattern = re.compile(
        r'(?:total|grand\s*total|balance\s*due|amount\s*paid|sum|price|charge|total\s*due)\s*[:\-]?\s*(?:\$|RM|MYR|SGD|€)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        re.IGNORECASE
    )
    matches = total_pattern.findall(text)
    if matches:
        # We take the last match as it is most likely the final total on the receipt.
        final_total_str = matches[-1].replace(',', '')
        print(f"Stage 1 (Keyword Match) found: {final_total_str}")
        try:
            return float(final_total_str)
        except ValueError:
            pass # Fall through to the next stage if conversion fails

    # Stage 2: Find the largest number on the receipt with two decimal places.
    # This is a strong heuristic as the total almost always has cents.
    all_decimal_numbers = re.findall(r'\b\d+\.\d{2}\b', text)
    if all_decimal_numbers:
        # Convert to floats and return the maximum value.
        decimal_floats = [float(n) for n in all_decimal_numbers]
        largest_decimal = max(decimal_floats)
        print(f"Stage 2 (Largest Decimal) found: {largest_decimal}")
        return largest_decimal
    
    # Stage 3: The final fallback. Find the largest number on the entire receipt.
    # This handles cases where the total is a round number (e.g., 50.00 is read as 50)
    all_numbers_pattern = re.compile(r'\b\d+\.?\d*\b')
    numbers = all_numbers_pattern.findall(text)
    if numbers:
        # Filter out small numbers that are likely item counts or dates
        cleaned_numbers = [float(n) for n in numbers if float(n) > 1.0]
        if cleaned_numbers:
            max_number = max(cleaned_numbers)
            print(f"Stage 3 (Largest Number Overall) found: {max_number}")
            return max_number

    print("No total amount could be found.")
    return None

def get_from_api():
    if "receipt" not in request.files:
        return jsonify({"Error: No receipt provided"}), 400 
    
    receipt_files = request.files["receipt"]
    image_data = receipt_files.read()
    receipt_text = get_text_from_image_api(image_data)
    total = parse_receipt(receipt_text)

    if total is not None: 
        print(total)
        return jsonify({f"Your total is : RM " : total})
    else: 
        print("No total found")
        return jsonify({f"Error : Cant find total"})

if __name__ == '__main__':
    app.run(debug=True)