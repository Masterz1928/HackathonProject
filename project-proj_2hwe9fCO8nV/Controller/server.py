from database import get_db_connection
from flask import Flask, jsonify, request
from flask_cors import CORS # 1. Import the VIP list manager
import CRUD           # 2. Import your awesome new database functions!

app = Flask(__name__)
CORS(app) # 3. Tell Flask to allow requests from your React frontend

# --- READ ROUTE ---
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """React calls this to get all expenses."""
    data = CRUD.get_all_transactions()
    return jsonify(data)

# --- CREATE ROUTE ---
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """React calls this to add a new expense."""
    # request.get_json() automatically parses the incoming JSON data from React!
    incoming_data = request.get_json() 
    
    result = CRUD.create_transaction(incoming_data)
    
    # If our crud function returned an error dictionary, send a 500 Bad Request status
    if "Error" in result:
        return jsonify(result), 500
        
    # Otherwise, send back the newly created transaction with its new ID!
    return jsonify(result), 201

# --- DELETE ROUTE ---
# The <int:id> part tells Flask to expect a number here and grab it!
@app.route('/api/transactions/<int:id>', methods=['DELETE'])
def remove_transaction(id):
    """React calls this to delete an expense."""
    
    # We don't need request.get_json() because the ID is already in the URL!
    # We just pass the 'id' straight into your CRUD function
    result = CRUD.delete_transaction(id)
    
    # Check if your CRUD function sent back your ERRORTAG
    if "Error" in result:
        return jsonify(result), 500
        
    # Return success! (200 is the standard HTTP code for "OK")
    return jsonify(result), 200

#--UPDATE ROUTE---
@app.route('/api/transactions/<int:id>', methods=['PUT'])
def updating_transaction(id):
    """React calls this to update the transactions"""
    incoming_data = request.get_json()
    result = CRUD.updating_transaction(id, incoming_data)
    if "Error" in result:
        return jsonify(result), 500
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
