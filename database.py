import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "expense_tracker.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
  
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            payment_method TEXT
        )
    ''')
  
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            month_year TEXT NOT NULL,
            UNIQUE(category, month_year)
        )
    ''')
   
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            currency TEXT DEFAULT '₹'
        )
    ''')
   
    c.execute('SELECT COUNT(*) FROM settings')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO settings (id, currency) VALUES (1, '₹')")
    
    conn.commit()
    conn.close()

def add_transaction(tx_type, amount, category, description, date_str, payment_method):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (type, amount, category, description, date, payment_method)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tx_type, amount, category, description, date_str, payment_method))
    conn.commit()
    conn.close()

def get_transactions():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)
    conn.close()
    return df

def update_transaction(tx_id, tx_type, amount, category, description, date_str, payment_method):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE transactions
        SET type=?, amount=?, category=?, description=?, date=?, payment_method=?
        WHERE id=?
    ''', (tx_type, amount, category, description, date_str, payment_method, tx_id))
    conn.commit()
    conn.close()

def delete_transaction(tx_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id=?', (tx_id,))
    conn.commit()
    conn.close()

def get_budgets():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM budgets", conn)
    conn.close()
    return df

def set_budget(category, amount, month_year):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO budgets (category, amount, month_year)
        VALUES (?, ?, ?)
        ON CONFLICT(category, month_year) DO UPDATE SET amount=excluded.amount
    ''', (category, amount, month_year))
    conn.commit()
    conn.close()

def delete_budget(b_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM budgets WHERE id=?', (b_id,))
    conn.commit()
    conn.close()

def get_settings():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT currency FROM settings WHERE id=1')
    res = c.fetchone()
    conn.close()
    return res[0] if res else '₹'

def update_settings(currency):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE settings SET currency=? WHERE id=1', (currency,))
    conn.commit()
    conn.close()

def clear_all_data():
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM transactions')
    c.execute('DELETE FROM budgets')

    conn.commit()
    conn.close()
