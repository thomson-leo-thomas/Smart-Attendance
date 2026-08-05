"""
Utility module for the Smart Classroom Attendance System.
Handles directory creations, path definitions, CSV exporting, 
and syncing data for the Vercel dashboard.
"""

import os
import csv
import json
import sqlite3
from datetime import datetime

# Define base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
ENCODINGS_DIR = os.path.join(BASE_DIR, "encodings")
ATTENDANCE_DIR = os.path.join(BASE_DIR, "attendance")
DB_DIR = os.path.join(BASE_DIR, "database")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
WEB_DIR = os.path.join(BASE_DIR, "web")

# Database Path
DB_PATH = os.path.join(DB_DIR, "attendance.db")
WEB_DATA_PATH = os.path.join(WEB_DIR, "attendance_data.json")

# Recognition configs
CONFIDENCE_THRESHOLD = 60.0  # Percentage threshold for face matching
SCALE_FACTOR = 0.25         # Image scaling factor for faster processing (1/4 size)


def create_required_directories():
    """
    Ensures all required project directories exist on start.
    """
    directories = [
        DATASET_DIR,
        ENCODINGS_DIR,
        ATTENDANCE_DIR,
        DB_DIR,
        REPORTS_DIR,
        WEB_DIR
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def export_attendance_to_csv(date_str=None):
    """
    Exports attendance data for a specific date (or all if None) to a CSV file.
    Saves to the attendance/ folder.
    Returns path of the generated CSV file.
    """
    from database import get_all_attendance, get_attendance_by_date

    create_required_directories()

    if date_str:
        records = get_attendance_by_date(date_str)
        filename = f"attendance_{date_str}.csv"
    else:
        records = get_all_attendance()
        filename = f"attendance_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    csv_path = os.path.join(ATTENDANCE_DIR, filename)

    headers = ["Attendance ID", "Roll Number", "Student Name", "Date", "Time", "Subject", "Status"]

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in records:
            writer.writerow([r["attendance_id"], r["roll_number"], r["student_name"], r["date"], r["time"], r["subject"], r["status"]])

    return csv_path


def sync_web_data():
    """
    Pulls all current student and attendance data from the SQLite database
    and updates the web/attendance_data.json file.
    This file is consumed by the Vercel-hostable web dashboard.
    """
    from database import get_db_connection

    create_required_directories()
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()

    # Get all students
    cursor.execute("SELECT roll_number, name, department, semester FROM students")
    students_rows = cursor.fetchall()
    students_list = [dict(row) for row in students_rows]

    # Get all attendance
    cursor.execute("SELECT attendance_id, roll_number, student_name, date, time, subject, status FROM attendance")
    attendance_rows = cursor.fetchall()
    attendance_list = [dict(row) for row in attendance_rows]

    conn.close()

    # Structure data for JSON consumption
    data = {
        "last_sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "students": students_list,
        "attendance": attendance_list
    }

    # Write to web/attendance_data.json
    with open(WEB_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return WEB_DATA_PATH


def send_parent_notification(student_name, roll_number, subject, status="Absent"):
    """
    Mock interface for sending parent alerts when a student is marked absent.
    In a real system, you would integrate Twilio (SMS), SendGrid (Email), or WhatsApp Business APIs.
    We print a simulated notification log and save it to a local alert log file.
    """
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    alert_log_file = os.path.join(log_dir, "parent_alerts.log")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_message = (
        f"[{timestamp}] ALERT: Student '{student_name}' (Roll No: {roll_number}) "
        f"is '{status}' for subject '{subject}' today. Parent notified via Email/SMS."
    )
    
    with open(alert_log_file, "a", encoding="utf-8") as f:
        f.write(alert_message + "\n")
        
    print(f"\n>>> [NOTIFICATION SENT] {alert_message}")


# Initialize system directories on import
create_required_directories()
