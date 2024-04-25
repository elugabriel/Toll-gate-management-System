import sqlite3

DATABASE = 'toll.db'

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Admin Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Admin (
            adminID TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Staff Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Staff (
            staffID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            date_of_birth TEXT,
            state TEXT,
            address TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            transactionID INTEGER PRIMARY KEY AUTOINCREMENT,
            staffID INTEGER,
            userID INTEGER,
            date TEXT,
            time TEXT,
            amount REAL,
            vehicle_number TEXT,
            FOREIGN KEY(staffID) REFERENCES Staff(staffID),
            FOREIGN KEY(userID) REFERENCES User(userID)
        )
    ''')

    # User Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            userID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            date_of_birth TEXT,
            state TEXT,
            plate_number TEXT,
            address TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close() 

if __name__ == '__main__':
    create_tables()
