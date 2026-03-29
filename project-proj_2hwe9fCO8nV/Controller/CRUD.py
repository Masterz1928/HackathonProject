from database import get_db_connection
ERRORTAG = "Error"
DB_CONNECTION_FAILED = "Database connection failed"

def create_transaction(data):
    """Inserts a new transaction and links any associated tags."""
    conn = get_db_connection()
    if not conn:
        return {ERRORTAG: DB_CONNECTION_FAILED}

    try:
        cursor = conn.cursor()
        
        # Step A: Insert the transaction
        cursor.execute(
            "INSERT INTO transactions (title, amount, type, date) VALUES (?, ?, ?, ?)",
            (data['title'], data['amount'], data['type'], data['date'])
        )
        
        # Get the ID of the new transaction (Python's equivalent to this.lastID)
        trans_id = cursor.lastrowid 

        # Step B: Link the tags (if any)
        # We check if 'tags' is in the dictionary and if it has items
        if 'tags' in data and data['tags']:
            for tag_name in data['tags']:
                link_tag(conn, trans_id, tag_name) # Calling the helper function!

        # Step C: Save everything!
        conn.commit() 
        
        # Return the data mixed with the new ID, just like your JS did
        return {"id": trans_id, **data}

    except Exception as e:
        # If ANYTHING fails (like a bad tag), undo the whole transaction so we don't get junk data
        conn.rollback() 
        return {"error": str(e)}
        
    finally:
        # This always runs, whether it succeeded or crashed, making sure the door is closed
        conn.close()

def delete_transaction(transaction_id):
    """Deletes a transaction from the database using its ID."""
    conn = get_db_connection()
    if not conn:
        return {ERRORTAG: DB_CONNECTION_FAILED}
        
    try: 
        cursor = conn.cursor()
        
        # The SQL Command
        cursor.execute(
            "DELETE FROM transactions WHERE id = ?", 
            (transaction_id,) # Don't forget the trailing comma for single-item tuples!
        )
        
        # Save the destruction!
        conn.commit()
        
        # Let the server know it worked
        return {"message": "Transaction deleted successfully"}

    except Exception as e: 
        return {ERRORTAG: str(e)}
        
    finally:
        # Always close the connection when you're done
        conn.close()

def updating_transaction(transaction_id, data):
    conn = get_db_connection()
    if not conn:
        return {ERRORTAG : DB_CONNECTION_FAILED}
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE transactions 
            SET title = ?, amount = ?, type = ?, date = ? 
            WHERE id = ?
            """,
            (data['title'], data['amount'], data['type'], data['date'], transaction_id)
        )
        cursor.execute("DELETE FROM transaction_tags WHERE transaction_id = ?", (transaction_id,))
        # Next, loop through the incoming tags and create fresh links!
        if 'tags' in data and data['tags']:
            for tag_name in data['tags']:
                link_tag(conn, transaction_id, tag_name) # Reusing your awesome helper function

            # Step 3: Save the changes!
        conn.commit()
        return {"message": "Transaction updated successfully", "id": transaction_id}

    except Exception as e:
        # If anything crashes, undo the changes so the database doesn't get corrupted
        conn.rollback() 
        return {ERRORTAG: str(e)}

    finally:
        conn.close()
    


def get_all_transactions():
    """Fetches all transactions and their grouped tags."""
    conn = get_db_connection()
    if not conn:
        return {ERRORTAG: DB_CONNECTION_FAILED}

    try:
        cursor = conn.cursor()
        
        # Notice we can just copy-paste your exact SQL query! SQL is universal.
        sql = """
            SELECT t.*, COALESCE(GROUP_CONCAT(tg.name, ', '), '') as category
            FROM transactions t
            LEFT JOIN transaction_tags tt ON t.id = tt.transaction_id
            LEFT JOIN tags tg ON tt.tag_id = tg.id
            GROUP BY t.id
            ORDER BY t.date DESC
        """
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        # Convert the SQLite Row objects into normal Python dictionaries
        return [dict(row) for row in rows]
        
    except Exception as e:
        return {"error": str(e)}
        
    finally:
        conn.close()

# --- PRIVATE HELPER FUNCTION ---
# We pass 'conn' (the connection) into this function so it shares the same transaction 
# as the create() or update() functions that call it.
def link_tag(conn, transaction_id, tag_name):
    cursor = conn.cursor()
    
    # 1. Create tag if it doesn't exist (INSERT OR IGNORE)
    # Note the comma in (tag_name,) - Python requires a tuple for single variables!
    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
    
    # 2. Get the tag's ID
    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    tag_row = cursor.fetchone() # Fetches exactly one row
    tag_id = tag_row['id']
    
    # 3. Link the transaction to the tag in the bridge table
    cursor.execute(
        "INSERT OR IGNORE INTO transaction_tags (transaction_id, tag_id) VALUES (?, ?)",
        (transaction_id, tag_id)
    )
    # We DO NOT close the cursor or commit here. We let the main function do that!