"""
Student registration module for the Smart Classroom Attendance System.
Captures face images from the webcam and registers student details in the database.
"""

import os
import cv2
import time
from database import add_student, get_student
from utils import DATASET_DIR, sync_web_data


def validate_input(roll_number, name, department, semester):
    """
    Validates registration fields.
    Returns (True, None) if valid, or (False, "Error message").
    """
    if not roll_number or not roll_number.strip():
        return False, "Roll number cannot be empty."
    if not name or not name.strip():
        return False, "Name cannot be empty."
    if not department or not department.strip():
        return False, "Department cannot be empty."
    if not semester or not semester.strip():
        return False, "Semester cannot be empty."
    return True, None


def capture_student_faces(roll_number, name, max_samples=10, feedback_callback=None):
    """
    Opens the webcam and captures cropped face images of the student.
    Saves them in dataset/<roll_number>_<name>/
    If feedback_callback is provided, calls it with updates (e.g. status messages).
    Returns (True, message) or (False, error).
    """
    roll_number = roll_number.strip()
    name = name.strip()
    
    # Create directory for the student
    student_dir = os.path.join(DATASET_DIR, f"{roll_number}_{name}")
    os.makedirs(student_dir, exist_ok=True)

    # Initialize Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    # Start Webcam
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow on Windows for faster initialization
    if not cap.isOpened():
        # Try default if DSHOW fails
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, "Error: Could not access the webcam."

    count = 0
    message = "Press 'SPACE' to capture, or 'Q' to quit."
    if feedback_callback:
        feedback_callback(message)

    print(f"\n[INFO] Starting camera for: {name}. Look at the camera.")
    
    while count < max_samples:
        ret, frame = cap.read()
        if not ret:
            break

        # Create a display copy and convert frame to grayscale for cascade
        display_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            # Draw green rectangle around the detected face
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Show progress on screen
            cv2.putText(
                display_frame, 
                f"Face Detected! Press Space (Captured: {count}/{max_samples})", 
                (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                (0, 255, 0), 
                2
            )

        # Show control instructions
        cv2.putText(
            display_frame,
            f"Press 'SPACE' to capture face. 'Q' to Exit.",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        cv2.imshow("Registering Student Face - Webcam Feed", display_frame)

        key = cv2.waitKey(1) & 0xFF
        
        # Press Space to capture face
        if key == ord(" "):
            if len(faces) == 0:
                msg = "No face detected in frame. Adjust lighting and try again."
                print(f"[WARN] {msg}")
                if feedback_callback:
                    feedback_callback(msg)
                continue
                
            if len(faces) > 1:
                msg = "Multiple faces detected. Ensure only one person is in view."
                print(f"[WARN] {msg}")
                if feedback_callback:
                    feedback_callback(msg)
                continue

            # Save the single cropped face image
            x, y, w, h = faces[0]
            # Add small padding to crop
            offset = 15
            y_start = max(0, y - offset)
            y_end = min(frame.shape[0], y + h + offset)
            x_start = max(0, x - offset)
            x_end = min(frame.shape[1], x + w + offset)
            
            face_img = frame[y_start:y_end, x_start:x_end]
            
            # Save image
            img_filename = f"face_{count + 1}.jpg"
            img_path = os.path.join(student_dir, img_filename)
            cv2.imwrite(img_path, face_img)
            
            count += 1
            msg = f"Captured {count}/{max_samples} successfully!"
            print(f"[INFO] {msg}")
            if feedback_callback:
                feedback_callback(msg)
                
            # Quick green flash indicator
            flash_overlay = display_frame.copy()
            cv2.rectangle(flash_overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 255, 0), -1)
            cv2.addWeighted(flash_overlay, 0.3, display_frame, 0.7, 0, display_frame)
            cv2.imshow("Registering Student Face - Webcam Feed", display_frame)
            cv2.waitKey(200)

        # Press Q to quit
        elif key == ord("q"):
            print("[INFO] Capture cancelled by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if count >= max_samples:
        return True, f"Successfully captured {count} face samples."
    else:
        # Clean up directory if registration failed/cancelled and empty
        if len(os.listdir(student_dir)) == 0:
            try:
                os.rmdir(student_dir)
            except OSError:
                pass
        return False, f"Cancelled. Only captured {count} of {max_samples} samples."


def register_student_cli():
    """
    Terminal interface for registering a student.
    """
    print("\n" + "=" * 40)
    print("      STUDENT REGISTRATION MENU (CLI)     ")
    print("=" * 40)

    roll_number = input("Enter Roll Number: ").strip()
    if get_student(roll_number):
        print(f"[ERROR] Student with Roll Number {roll_number} already registered!")
        return

    name = input("Enter Full Name: ").strip()
    department = input("Enter Department: ").strip()
    semester = input("Enter Semester: ").strip()

    valid, error_msg = validate_input(roll_number, name, department, semester)
    if not valid:
        print(f"[ERROR] {error_msg}")
        return

    print("\nPreparing to capture face photos...")
    print("Webcam will open. Look directly into the lens.")
    print("Press SPACEBAR to capture an image. We need 10 samples.")
    time.sleep(2)

    success, msg = capture_student_faces(roll_number, name)
    if success:
        db_success = add_student(roll_number, name, department, semester)
        if db_success:
            print(f"\n[SUCCESS] Student {name} registered in DB.")
            print(msg)
            print("Note: Remember to run Model Training to compile new faces!")
            sync_web_data()
        else:
            print("\n[ERROR] Failed to save student details to Database.")
    else:
        print(f"\n[FAILED] Registration aborted: {msg}")


if __name__ == "__main__":
    register_student_cli()
