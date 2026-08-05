"""
Helper seeding script for the Smart Classroom Attendance System.
Populates the SQLite database and syncs web JSON with sample students and attendance logs
to make testing immediate and easy.
"""

import os
from datetime import datetime, timedelta
import database
import utils


def seed():
    print("[INFO] Starting database seeding process...")
    # Initialize DB schema
    database.init_db()

    # Define mock students
    students = [
        ("CSE-001", "Aarav Sharma", "Computer Science", "VIII"),
        ("CSE-002", "Ananya Iyer", "Computer Science", "VIII"),
        ("CSE-003", "Rohan Varma", "Computer Science", "VIII"),
        ("CSE-004", "Ishaan Gupta", "Computer Science", "VIII"),
        ("CSE-005", "Priya Nair", "Computer Science", "VIII"),
        ("CSE-006", "Kabir Mehta", "Computer Science", "VIII"),
        ("ECE-012", "Vikram Sen", "Electronics & Comm", "VIII"),
        ("ECE-015", "Siddharth Rao", "Electronics & Comm", "VIII"),
        ("ME-045", "Neha Patil", "Mechanical Eng", "VIII"),
        ("EE-022", "Rahul Deshmukh", "Electrical Eng", "VIII")
    ]

    # Insert students
    added_count = 0
    for roll, name, dept, sem in students:
        if not database.get_student(roll):
            success = database.add_student(roll, name, dept, sem)
            if success:
                added_count += 1
    print(f"[SUCCESS] Registered {added_count} new students in SQLite database.")

    # Define subjects and statuses
    subjects = ["AI_Lab", "Computer_Vision", "Deep_Learning"]
    
    # Generate records for the past 3 days
    log_count = 0
    today = datetime.now()
    
    for i in range(3):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        
        for subject in subjects:
            for index, (roll, name, _, _) in enumerate(students):
                # Deterministic present/absent mix
                # e.g., student index % 5 == 0 is absent on odd days, etc.
                status = "Present"
                time_str = "09:05:00"
                
                if (index + i) % 7 == 0:
                    status = "Absent"
                    time_str = "10:15:00"  # logged late as absent

                # Check if already exists to prevent integrity errors
                if not database.is_attendance_marked(roll, subject, date_str):
                    success, _ = database.mark_attendance(
                        roll_number=roll,
                        student_name=name,
                        subject=subject,
                        date=date_str,
                        time=time_str,
                        status=status
                    )
                    if success:
                        log_count += 1

    print(f"[SUCCESS] Inserted {log_count} historical attendance records.")

    # Sync to web/attendance_data.json
    web_path = utils.sync_web_data()
    print(f"[SUCCESS] Updated web dashboard records at: {web_path}")
    print("[INFO] Seeding completed successfully. The application is ready to run!")


if __name__ == "__main__":
    seed()
