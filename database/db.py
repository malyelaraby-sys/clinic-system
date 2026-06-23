import sqlite3

def connect_db():
    conn = sqlite3.connect("clinic.db")
    return conn