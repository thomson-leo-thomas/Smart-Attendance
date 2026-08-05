"""
Database management module for the Smart Classroom Attendance System.
Handles SQLite operations, table creations, inserts, and query filters.
"""

import os
import sqlite3
from datetime import datetime

# Default database directory and path
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "attendance.db")


def get_db_connection(db_path=DB_PATH):
    """
    Establishes and returns a connection to the SQLite database.
    Creates the parent database directory if it does not exist.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db(db_path=DB_PATH):
    """
    Initializes the database by creating students and attendance tables.
    Also handles foreign key enabling.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Create students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            semester TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Create attendance table with a unique constraint on roll_number, date, and subject
    # to prevent duplicate attendance marks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT NOT NULL,
            student_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            subject TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (roll_number) REFERENCES students(roll_number),
            UNIQUE(roll_number, date, subject)
        )
    """)

    conn.commit()
    conn.close()


def add_student(roll_number, name, department, semester, db_path=DB_PATH):
    """
    Adds a new student to the database.
    Returns True if successful, False if roll number already exists.
    """
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO students (roll_number, name, department, semester, created_at) VALUES (?, ?, ?, ?, ?)",
            (roll_number.strip(), name.strip(), department.strip(), semester.strip(), created_at)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_student(roll_number, db_path=DB_PATH):
    """
    Retrieves student details by roll number.
    Returns sqlite3.Row object or None.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE roll_number = ?", (roll_number.strip(),))
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_students(db_path=DB_PATH):
    """
    Retrieves all students.
    Returns a list of sqlite3.Row objects.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def mark_attendance(roll_number, student_name, subject, date=None, time=None, status="Present", db_path=DB_PATH):
    """
    Logs attendance for a student.
    Returns (True, "Success Message") or (False, "Error Message").
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    if not time:
        time = datetime.now().strftime("%H:%M:%S")

    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attendance (roll_number, student_name, date, time, subject, status) VALUES (?, ?, ?, ?, ?, ?)",
            (roll_number.strip(), student_name.strip(), date, time, subject.strip(), status)
        )
        conn.commit()
        conn.close()
        return True, "Attendance marked successfully!"
    except sqlite3.IntegrityError:
        return False, "Attendance already marked for today."


def is_attendance_marked(roll_number, subject, date=None, db_path=DB_PATH):
    """
    Checks if a student already has attendance marked for a specific subject on a specific date.
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM attendance WHERE roll_number = ? AND date = ? AND subject = ?",
        (roll_number.strip(), date, subject.strip())
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None


def get_attendance_by_date(date, db_path=DB_PATH):
    """
    Retrieves all attendance records for a specific date (YYYY-MM-DD).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM attendance WHERE date = ? ORDER BY time DESC",
        (date,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_attendance_by_student(query_str, db_path=DB_PATH):
    """
    Searches attendance records by roll number or student name.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    search_term = f"%{query_str.strip()}%"
    cursor.execute(
        "SELECT * FROM attendance WHERE roll_number LIKE ? OR student_name LIKE ? ORDER BY date DESC, time DESC",
        (search_term, search_term)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_attendance(db_path=DB_PATH):
    """
    Retrieves all attendance records from the database.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Ensure database initializes when run directly
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
