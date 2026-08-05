"""
Attendance transactions and operations layer for the Smart Classroom Attendance System.
Handles marking present status, closing sessions to log absences,
triggering parent alerts, and exporting CSV sheets.
"""

from datetime import datetime
import database
import utils


def mark_student_present(roll_number, subject):
    """
    Marks a student as Present for a specific subject today.
    Validates if they are registered and checks duplicate markings.
    Returns (True, message) if marked successfully, or (False, reason).
    """
    # 1. Fetch student information
    student = database.get_student(roll_number)
    if not student:
        return False, f"Roll Number {roll_number} is not registered."

    student_name = student["name"]
    date_today = datetime.now().strftime("%Y-%m-%d")

    # 2. Check if already marked for this subject today
    if database.is_attendance_marked(roll_number, subject, date_today):
        return False, "Attendance already marked."

    # 3. Mark Present
    time_now = datetime.now().strftime("%H:%M:%S")
    success, msg = database.mark_attendance(
        roll_number=roll_number,
        student_name=student_name,
        subject=subject,
        date=date_today,
        time=time_now,
        status="Present"
    )

    if success:
        # Sync the updated data with Vercel web dashboard json
        utils.sync_web_data()
        return True, f"Present: {student_name} ({roll_number}) marked successfully."
    else:
        return False, msg


def close_attendance_session(subject):
    """
    Closes the attendance marking for a specific subject today.
    Identifies all students who did NOT attend (were not marked Present)
    and logs them as "Absent" in the database, triggering parent notifications.
    
    Returns (absent_count, list_of_absents)
    """
    date_today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")
    
    # 1. Retrieve all registered students
    all_students = database.get_all_students()
    
    # 2. Retrieve students marked present for this subject today
    present_records = database.get_attendance_by_date(date_today)
    present_rolls = {r["roll_number"] for r in present_records if r["subject"].lower() == subject.lower() and r["status"] == "Present"}

    absent_students = []
    
    for student in all_students:
        roll = student["roll_number"]
        name = student["name"]
        
        # If student not marked present, mark them absent (if not already logged as absent)
        if roll not in present_rolls:
            if not database.is_attendance_marked(roll, subject, date_today):
                success, _ = database.mark_attendance(
                    roll_number=roll,
                    student_name=name,
                    subject=subject,
                    date=date_today,
                    time=time_now,
                    status="Absent"
                )
                if success:
                    absent_students.append({"roll_number": roll, "name": name})
                    # Trigger alert (SMS / Email simulation)
                    utils.send_parent_notification(name, roll, subject, status="Absent")

    if absent_students:
        # Update Web JSON with absences
        utils.sync_web_data()

    return len(absent_students), absent_students


def search_attendance(query_str):
    """
    Searches attendance logs by student name or roll number.
    """
    return database.get_attendance_by_student(query_str)


def get_todays_attendance():
    """
    Retrieves all attendance records logged today.
    """
    date_today = datetime.now().strftime("%Y-%m-%d")
    return database.get_attendance_by_date(date_today)
