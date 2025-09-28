import io
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import sys
import requests
from datetime import datetime

# This is the corrected import statement.
from google.cloud import vision_v1 as vision
from google.protobuf.json_format import MessageToJson

# Create an instance of the Flask class
app = Flask(__name__)
# Enable CORS for the frontend to be able to communicate with this API
CORS(app)

def create_response(status, data, message, status_code):
    """
    A helper function to create a standardized JSON response.
    """
    response = jsonify({
        "status": status,
        "data": data,
        "message": message
    })
    response.status_code = status_code
    return response

def get_text_from_image_api(image_data):
    """
    Calls Google Cloud Vision API to extract text from an image.
    This function requires GOOGLE_APPLICATION_CREDENTIALS to be set.
    """
    print("Calling Google Cloud Vision API...")
    try:
        # A new line to check if the environment variable is set.
        print(f"Checking for credentials at: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
        # Instantiates a client. This will use the credentials from the environment.
        client = vision.ImageAnnotatorClient()
        
        # Creates a Vision API image object from the uploaded image data.
        image = vision.Image(content=image_data)
        
        # Performs text detection on the image.
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            # The first text annotation is the full text of the image.
            return texts[0].description
        else:
            return ""
    except Exception as e:
        print(f"Error calling Vision API: {e}")
        return ""

def parse_receipt(text):
    """
    Parses the OCR text from a receipt to find the total amount.
    It uses a multi-stage approach for better accuracy.
    """
    print("--- Parsing Receipt ---")
    print(f"Original Text:\n{text}\n")

    # Stage 1: The most reliable method. Look for a number directly following a total keyword.
    total_pattern = re.compile(
        r'(?:total|grand\s*total|balance\s*due|amount\s*paid|sum|price|charge|total\s*due)\s*[:\-]?\s*(?:\$|RM|MYR|SGD|€)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        re.IGNORECASE
    )
    matches = total_pattern.findall(text)
    if matches:
        final_total_str = matches[-1].replace(',', '')
        print(f"Stage 1 (Keyword Match) found: {final_total_str}")
        try:
            return float(final_total_str)
        except ValueError:
            pass 

    # Stage 2: Find the largest number on the receipt with two decimal places.
    all_decimal_numbers = re.findall(r'\b\d+\.\d{2}\b', text)
    if all_decimal_numbers:
        decimal_floats = [float(n) for n in all_decimal_numbers]
        largest_decimal = max(decimal_floats)
        print(f"Stage 2 (Largest Decimal) found: {largest_decimal}")
        return largest_decimal
    
    # Stage 3: The final fallback. Find the largest number on the entire receipt.
    all_numbers_pattern = re.compile(r'\b\d+\.?\d*\b')
    numbers = all_numbers_pattern.findall(text)
    if numbers:
        cleaned_numbers = [float(n) for n in numbers if float(n) > 1.0]
        if cleaned_numbers:
            max_number = max(cleaned_numbers)
            print(f"Stage 3 (Largest Number Overall) found: {max_number}")
            return max_number

    print("No total amount could be found.")
    return None

@app.route("/")
def test():
    now = datetime.now()
    return f"Server is running. Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

@app.route("/api/parse-receipt", methods=["POST"])
def parse_receipt_api():
    print("Received a new request to parse a receipt.")
    if "receipt" not in request.files:
        print("Error: No receipt file provided in the request.")
        return create_response("error", None, "No receipt file provided", 400) 
    
    receipt_file = request.files["receipt"]
    image_data = receipt_file.read()
    
    # We now call the real API function to get the text.
    receipt_text = get_text_from_image_api(image_data)
    
    total = parse_receipt(receipt_text)

    if total is not None: 
        print(f"Total found: {total}. Sending success response.")
        return create_response("success", {"total": total}, "Total found successfully", 200)
    else: 
        print("No total found. Sending error response.")
        return create_response("error", None, "Could not find a total amount.", 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
