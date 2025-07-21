import os
import sqlite3

db_name = "agent_memory.db"

def get_num_messages_by_id(context_id: str, num_messages: int) -> int:
    """Fetch the last n messages by context ID from the database."""
    try:
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message, role, created_at FROM messages
            WHERE context_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        ''', (context_id, num_messages))
        messages = cursor.fetchall()
        return messages  # List of tuples: (message, role, created_at)
    except sqlite3.Error as e:
        raise Exception(f"An SQLite error occurred: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while fetching messages: {e}")  
    finally:
        if conn:
            conn.close()

def add_message(context_id: str, message: str, role: str):
    """Add a new message to the database."""
    try:
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (context_id, message, role)
            VALUES (?, ?, ?)
        ''', (context_id, message, role))
        conn.commit()
    except sqlite3.Error as e:
        raise Exception(f"An SQLite error occurred: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while adding a message: {e}")
    finally:
        if conn:
            conn.close()

def get_all_messages():
    """Fetch all messages from the database."""
    try:
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages')
        messages = cursor.fetchall()
        return messages  # List of tuples: (id, context_id, message, role, created_at)
    except sqlite3.Error as e:
        raise Exception(f"An SQLite error occurred: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while fetching all messages: {e}")
    finally:
        if conn:
            conn.close()

def get_all_messsages_by_id(context_id: str):
    """Fetch all messages for a specific context ID."""
    try:
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM messages WHERE context_id = ?
        ''', (context_id,))
        messages = cursor.fetchall()
        return messages  # List of tuples: (id, context_id, message, role, created_at)
    except sqlite3.Error as e:
        raise Exception(f"An SQLite error occurred: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while fetching messages by context ID: {e}")
    finally:
        if conn:
            conn.close()
    
def clear_messages_by_id(context_id: str):
    """Clear all messages for a specific context ID."""
    try:
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM messages WHERE context_id = ?
        ''', (context_id,))
        conn.commit()
    except sqlite3.Error as e:
        raise Exception(f"An SQLite error occurred: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while clearing messages: {e}")
    finally:
        if conn:
            conn.close()

def clear_all_messages():
    """Clear all messages from the database."""
    try:
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages')
        conn.commit()
    except sqlite3.Error as e:
        raise Exception(f"An SQLite error occurred: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while clearing all messages: {e}")
    finally:
        if conn:
            conn.close()