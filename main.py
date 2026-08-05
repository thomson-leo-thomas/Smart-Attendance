"""
Main entry point for the Smart Classroom Attendance System.
Features a dual interface:
1. A modern, dark-themed Tkinter GUI (default).
2. A text-based interactive Command-Line Interface (CLI) via `python main.py --cli`.
"""

import os
import sys
import cv2
import time
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime

# Local imports
import database
import utils
import register
import train_model
from recognizer import SmartRecognizer
import attendance

# Ensure DB and directories are ready
database.init_db()
utils.create_required_directories()


# =====================================================================
#                        PART 1: CLI INTERFACE
# =====================================================================

def run_cli_attendance():
    """
    Runs a live attendance session from the terminal.
    Opens OpenCV window and marks attendance in real-time.
    """
    print("\n" + "=" * 40)
    print("      LIVE ATTENDANCE SESSION (CLI)     ")
    print("=" * 40)
    
    subject = input("Enter Subject Name (e.g., Al_Lab): ").strip()
    if not subject:
        print("[ERROR] Subject name is required.")
        return

    print("\nLoading face recognition models...")
    recognizer = SmartRecognizer()
    if not recognizer.known_names:
        print("[ERROR] No face encodings found. Please register students and run training first.")
        return

    print("\nStarting webcam...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Could not open webcam.")
            return

    print("\nWebcam Active. Standing by to scan faces...")
    print("Press 'Q' to close the attendance session.")

    last_checked = {}  # Throttle marking frequency

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # Get recognition results
        faces = recognizer.recognize(frame)

        for face in faces:
            top, right, bottom, left = face["box"]
            name = face["name"]
            roll = face["roll"]
            conf = face["confidence"]
            is_live = face["liveness"]

            # Set color: Red for spoof/unknown, Green for recognized live face
            if name == "Unknown":
                color = (0, 0, 255)  # Red
                label = f"Unknown"
            elif not is_live:
                color = (0, 165, 255)  # Orange (Spoof Alert)
                label = f"SPOOF ALERT! {name}"
            else:
                color = (0, 255, 0)  # Green
                label = f"{name} ({roll}) {conf}%"

                # Throttle attendance mark to once every 5 seconds per student in frame
                now_ts = time.time()
                if roll not in last_checked or (now_ts - last_checked[roll]) > 5:
                    last_checked[roll] = now_ts
                    marked, msg = attendance.mark_student_present(roll, subject)
                    print(f"[ATTENDANCE] {msg}")

            # Draw box and label
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Draw Liveness flag
            liveness_text = "Liveness: Verified" if is_live else "Liveness: FAILED (Static Image)"
            cv2.putText(frame, liveness_text, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.imshow(f"Marking Attendance: {subject}", frame)

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Automatically trigger absent markings and parent notifications
    print(f"\nClosing attendance session for '{subject}'...")
    absent_count, absents = attendance.close_attendance_session(subject)
    print(f"[SESSION CLOSED] Marked {absent_count} students as Absent today.")
    if absent_count > 0:
        print("Absents List:")
        for stu in absents:
            print(f" - {stu['name']} ({stu['roll_number']})")
    print("Exporting report...")
    csv_path = utils.export_attendance_to_csv(datetime.now().strftime("%Y-%m-%d"))
    print(f"[SUCCESS] Todays attendance sheet exported to: {csv_path}")


def view_reports_cli():
    """
    Displays attendance records in the terminal.
    """
    print("\n" + "=" * 40)
    print("           ATTENDANCE LOGS (CLI)        ")
    print("=" * 40)
    records = database.get_all_attendance()
    if not records:
        print("No attendance records found.")
        return
        
    print(f"{'ID':<5} | {'Roll No':<10} | {'Name':<20} | {'Date':<12} | {'Time':<10} | {'Subject':<12} | {'Status':<8}")
    print("-" * 85)
    for r in records:
        print(f"{r['attendance_id']:<5} | {r['roll_number']:<10} | {r['student_name']:<20} | {r['date']:<12} | {r['time']:<10} | {r['subject']:<12} | {r['status']:<8}")


def run_cli_menu():
    """
    Main loop for interactive terminal mode.
    """
    while True:
        print("\n" + "=" * 50)
        print("   AI-BASED SMART CLASSROOM ATTENDANCE SYSTEM   ")
        print("=" * 50)
        print("1. Register New Student")
        print("2. Train AI Face Recognition Model")
        print("3. Start Live Attendance Session")
        print("4. View Attendance Logs")
        print("5. Export All Records to CSV")
        print("6. Exit")
        print("=" * 50)

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            register.register_student_cli()
        elif choice == "2":
            train_model.run_training()
        elif choice == "3":
            run_cli_attendance()
        elif choice == "4":
            view_reports_cli()
        elif choice == "5":
            csv_path = utils.export_attendance_to_csv()
            print(f"[SUCCESS] CSV Exported to: {csv_path}")
        elif choice == "6":
            print("\nExiting. Thank you for using Smart Classroom Attendance!")
            sys.exit(0)
        else:
            print("[ERROR] Invalid selection. Choose between 1 and 6.")


# =====================================================================
#                        PART 2: GUI INTERFACE
# =====================================================================

class SmartAttendanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Based Smart Classroom Attendance System")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 650)
        
        # Sleek dark theme styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Colors
        self.bg_color = "#1e1e1e"      # Charcoal Dark
        self.sidebar_color = "#121212" # Jet Black
        self.accent_color = "#00adb5"  # Teal Blue
        self.text_color = "#eeeeee"    # White Smoke
        self.card_color = "#2d2d2d"    # Lighter Gray
        
        self.root.configure(bg=self.bg_color)
        
        # Custom Widget Configurations
        self.style.configure(".", background=self.bg_color, foreground=self.text_color)
        self.style.configure("Sidebar.TFrame", background=self.sidebar_color)
        self.style.configure("Content.TFrame", background=self.bg_color)
        
        # Buttons
        self.style.configure("Menu.TButton", 
                             background=self.sidebar_color, 
                             foreground=self.text_color, 
                             borderwidth=0, 
                             font=("Segoe UI", 11, "bold"),
                             padding=15)
        self.style.map("Menu.TButton", 
                       background=[("active", self.accent_color), ("pressed", self.accent_color)])

        self.style.configure("Accent.TButton", 
                             background=self.accent_color, 
                             foreground=self.text_color, 
                             borderwidth=0, 
                             font=("Segoe UI", 11, "bold"),
                             padding=10)
        self.style.map("Accent.TButton", 
                       background=[("active", "#008a90"), ("pressed", "#006b70")])

        # Labels
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background=self.bg_color, foreground=self.text_color)
        self.style.configure("Sub.TLabel", font=("Segoe UI", 10), background=self.bg_color, foreground="#aaaaaa")
        
        # Treeview (Dark Theme)
        self.style.configure("Treeview", 
                             background=self.card_color, 
                             fieldbackground=self.card_color, 
                             foreground=self.text_color,
                             font=("Segoe UI", 10),
                             rowheight=25)
        self.style.configure("Treeview.Heading", 
                             background=self.sidebar_color, 
                             foreground=self.text_color,
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[("selected", self.accent_color)])

        # Variables
        self.cap = None
        self.recognizer = None
        self.camera_active = False
        self.selected_menu = None
        self.last_checked_gui = {}

        # Build UI layout
        self.create_layout()
        
        # Default view
        self.switch_frame("mark_attendance")

    def create_layout(self):
        """
        Creates Sidebar Navigation and Content Frame.
        """
        # Sidebar
        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y")

        # Sidebar Title
        title_lbl = ttk.Label(self.sidebar, text="SMART ATTENDANCE", font=("Segoe UI", 12, "bold"), foreground=self.accent_color, background=self.sidebar_color)
        title_lbl.pack(pady=20, padx=15)

        # Navigation Buttons
        btn_mark = ttk.Button(self.sidebar, text="Mark Attendance", style="Menu.TButton", command=lambda: self.switch_frame("mark_attendance"))
        btn_mark.pack(fill="x", pady=2)

        btn_reg = ttk.Button(self.sidebar, text="Register Student", style="Menu.TButton", command=lambda: self.switch_frame("register_student"))
        btn_reg.pack(fill="x", pady=2)

        btn_train = ttk.Button(self.sidebar, text="Train Encodings", style="Menu.TButton", command=lambda: self.switch_frame("train_model"))
        btn_train.pack(fill="x", pady=2)

        btn_view = ttk.Button(self.sidebar, text="View Logs / CSV", style="Menu.TButton", command=lambda: self.switch_frame("view_logs"))
        btn_view.pack(fill="x", pady=2)

        # Footer spacer
        lbl_spacer = ttk.Label(self.sidebar, text="", background=self.sidebar_color)
        lbl_spacer.pack(fill="both", expand=True)

        btn_exit = ttk.Button(self.sidebar, text="Exit", style="Menu.TButton", command=self.on_exit)
        btn_exit.pack(fill="x", side="bottom")

        # Main Content container
        self.content_frame = ttk.Frame(self.root, style="Content.TFrame")
        self.content_frame.pack(side="right", fill="both", expand=True)

    def switch_frame(self, target_frame):
        """
        Destroys the current content frame contents and builds the target page.
        """
        # Close camera if switching away from Mark Attendance
        if self.camera_active and target_frame != "mark_attendance":
            self.stop_camera()

        # Clear Content Frame
        for child in self.content_frame.winfo_children():
            child.destroy()

        self.selected_menu = target_frame

        if target_frame == "mark_attendance":
            self.build_mark_attendance_page()
        elif target_frame == "register_student":
            self.build_register_student_page()
        elif target_frame == "train_model":
            self.build_train_model_page()
        elif target_frame == "view_logs":
            self.build_view_logs_page()

    # -----------------------------------------------------------------
    # PAGE 1: MARK ATTENDANCE
    # -----------------------------------------------------------------
    def build_mark_attendance_page(self):
        # Header
        header = ttk.Label(self.content_frame, text="Mark Attendance Session", style="Header.TLabel")
        header.pack(anchor="w", padx=25, pady=(20, 5))
        
        sub = ttk.Label(self.content_frame, text="Select a subject and activate the webcam to track presence.", style="Sub.TLabel")
        sub.pack(anchor="w", padx=25, pady=(0, 20))

        # Controls Panel
        ctrl_panel = ttk.Frame(self.content_frame)
        ctrl_panel.pack(fill="x", padx=25, pady=5)

        ttk.Label(ctrl_panel, text="Subject / Class Code:", font=("Segoe UI", 11)).pack(side="left", padx=(0, 10))
        self.subject_entry = ttk.Entry(ctrl_panel, font=("Segoe UI", 11), width=18)
        self.subject_entry.pack(side="left", padx=(0, 15))
        self.subject_entry.insert(0, "AI_Lab")

        self.btn_camera = ttk.Button(ctrl_panel, text="Start Scanner", style="Accent.TButton", command=self.toggle_camera)
        self.btn_camera.pack(side="left", padx=5)

        self.btn_close_session = ttk.Button(ctrl_panel, text="Close Session & Notify", style="Accent.TButton", command=self.close_attendance_session_gui)
        self.btn_close_session.pack(side="left", padx=5)

        # Video Canvas
        self.canvas_w, self.canvas_h = 640, 480
        self.video_container = ttk.Frame(self.content_frame, borderwidth=1, relief="solid")
        self.video_container.pack(pady=20, padx=25)
        
        self.video_canvas = tk.Canvas(self.video_container, width=self.canvas_w, height=self.canvas_h, bg=self.sidebar_color, highlightthickness=0)
        self.video_canvas.pack()
        self.video_canvas.create_text(320, 240, text="Webcam Scanner Inactive", fill="#777777", font=("Segoe UI", 12, "bold"))

        # Status Bar
        self.status_lbl = ttk.Label(self.content_frame, text="Ready.", font=("Segoe UI", 11, "italic"), foreground=self.accent_color)
        self.status_lbl.pack(fill="x", padx=25, side="bottom", pady=15)

    def toggle_camera(self):
        if not self.camera_active:
            # Validate subject
            subject = self.subject_entry.get().strip()
            if not subject:
                messagebox.showerror("Error", "Please enter a Subject Name before starting.")
                return

            # Initialize recognizer
            self.recognizer = SmartRecognizer()
            if not self.recognizer.known_names:
                messagebox.showerror("Error", "No trained models found. Register students and run training first.")
                return

            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    messagebox.showerror("Error", "Could not access the webcam.")
                    return

            self.camera_active = True
            self.btn_camera.configure(text="Stop Scanner")
            self.subject_entry.configure(state="disabled")
            self.status_lbl.configure(text="Scanner Active. Scan face inside screen...")
            self.update_video_frame()
        else:
            self.stop_camera()

    def stop_camera(self):
        self.camera_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.btn_camera.configure(text="Start Scanner")
        self.subject_entry.configure(state="normal")
        self.video_canvas.delete("all")
        self.video_canvas.create_text(320, 240, text="Webcam Scanner Inactive", fill="#777777", font=("Segoe UI", 12, "bold"))
        self.status_lbl.configure(text="Scanner Stopped.")

    def close_attendance_session_gui(self):
        subject = self.subject_entry.get().strip()
        if not subject:
            messagebox.showerror("Error", "Subject name required.")
            return

        self.stop_camera()
        
        # Mark absents
        absents_count, absents = attendance.close_attendance_session(subject)
        
        # Export today's CSV
        today_str = datetime.now().strftime("%Y-%m-%d")
        csv_path = utils.export_attendance_to_csv(today_str)

        msg = (
            f"Attendance session for '{subject}' closed!\n\n"
            f"• Absent Students Logged: {absents_count}\n"
            f"• Parents Notified via simulated SMS/Email.\n"
            f"• Sheet exported to: {os.path.basename(csv_path)}"
        )
        messagebox.showinfo("Session Closed", msg)
        self.status_lbl.configure(text="Session closed and reported.")

    def update_video_frame(self):
        if not self.camera_active or not self.cap:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop_camera()
            return

        # Resize frame to canvas size
        frame = cv2.resize(frame, (self.canvas_w, self.canvas_h))
        faces = self.recognizer.recognize(frame)

        subject = self.subject_entry.get().strip()

        for face in faces:
            top, right, bottom, left = face["box"]
            name = face["name"]
            roll = face["roll"]
            conf = face["confidence"]
            is_live = face["liveness"]

            if name == "Unknown":
                color = (0, 0, 255)  # BGR Red
                label = "Unknown"
            elif not is_live:
                color = (0, 165, 255)  # Orange (Spoof)
                label = f"SPOOF: {name}"
                self.status_lbl.configure(text=f"WARNING: Static Photo Spoof Alert for {name}!", foreground="#ff5555")
            else:
                color = (0, 255, 0)  # Green
                label = f"{name} ({roll}) {conf}%"

                # Log present status
                now_ts = time.time()
                if roll not in self.last_checked_gui or (now_ts - self.last_checked_gui[roll]) > 5:
                    self.last_checked_gui[roll] = now_ts
                    marked, msg = attendance.mark_student_present(roll, subject)
                    self.status_lbl.configure(text=msg, foreground=self.accent_color)

            # Draw shapes on frame
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Liveness Tag
            liveness_tag = "Liveness: OK" if is_live else "Liveness: SPOOF"
            cv2.putText(frame, liveness_tag, (left, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # Convert frame to PhotoImage
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        self.imgtk = ImageTk.PhotoImage(image=img)
        
        self.video_canvas.create_image(0, 0, anchor="nw", image=self.imgtk)

        # Recursive loop call every 15 ms
        if self.camera_active:
            self.root.after(15, self.update_video_frame)

    # -----------------------------------------------------------------
    # PAGE 2: REGISTER STUDENT
    # -----------------------------------------------------------------
    def build_register_student_page(self):
        # Header
        header = ttk.Label(self.content_frame, text="Register New Student", style="Header.TLabel")
        header.pack(anchor="w", padx=25, pady=(20, 5))
        
        sub = ttk.Label(self.content_frame, text="Fill student details and capture 10 face snapshots using the camera.", style="Sub.TLabel")
        sub.pack(anchor="w", padx=25, pady=(0, 20))

        # Register Card Form
        form_frame = ttk.Frame(self.content_frame, borderwidth=1, relief="solid", padding=20)
        form_frame.pack(fill="x", padx=25, pady=10)

        # Roll Number
        ttk.Label(form_frame, text="Roll Number *", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=10, padx=10)
        self.reg_roll = ttk.Entry(form_frame, font=("Segoe UI", 11), width=35)
        self.reg_roll.grid(row=0, column=1, pady=10, padx=10)

        # Name
        ttk.Label(form_frame, text="Full Name *", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", pady=10, padx=10)
        self.reg_name = ttk.Entry(form_frame, font=("Segoe UI", 11), width=35)
        self.reg_name.grid(row=1, column=1, pady=10, padx=10)

        # Department
        ttk.Label(form_frame, text="Department *", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w", pady=10, padx=10)
        self.reg_dept = ttk.Entry(form_frame, font=("Segoe UI", 11), width=35)
        self.reg_dept.grid(row=2, column=1, pady=10, padx=10)
        self.reg_dept.insert(0, "Computer Science")

        # Semester
        ttk.Label(form_frame, text="Semester *", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, sticky="w", pady=10, padx=10)
        self.reg_sem = ttk.Entry(form_frame, font=("Segoe UI", 11), width=35)
        self.reg_sem.grid(row=3, column=1, pady=10, padx=10)
        self.reg_sem.insert(0, "VIII")

        # Capture Button
        btn_capture = ttk.Button(form_frame, text="Start Face Capture (10 Snaps)", style="Accent.TButton", command=self.register_student_action)
        btn_capture.grid(row=4, column=0, columnspan=2, pady=20)

    def register_student_action(self):
        roll = self.reg_roll.get().strip()
        name = self.reg_name.get().strip()
        dept = self.reg_dept.get().strip()
        sem = self.reg_sem.get().strip()

        # Validation
        valid, err = register.validate_input(roll, name, dept, sem)
        if not valid:
            messagebox.showerror("Error", err)
            return

        # Check duplication
        if database.get_student(roll):
            messagebox.showerror("Error", f"Student with Roll Number {roll} already exists.")
            return

        # Prompt webcam instruction
        confirm = messagebox.askyesno(
            "Camera Capture", 
            "The webcam will open. Face the lens clearly.\n"
            "Press 'SPACEBAR' to capture a snapshot (requires 10 captures).\n"
            "Press 'Q' inside the camera feed to abort.\n\nReady to start?"
        )
        if not confirm:
            return

        # Run Capture Loop
        success, msg = register.capture_student_faces(roll, name)

        if success:
            db_success = database.add_student(roll, name, dept, sem)
            if db_success:
                messagebox.showinfo("Success", f"Registration complete!\nStudent '{name}' added to database.")
                utils.sync_web_data()
                # Clear Form
                self.reg_roll.delete(0, "end")
                self.reg_name.delete(0, "end")
            else:
                messagebox.showerror("Database Error", "Failed to save student details to SQLite DB.")
        else:
            messagebox.showwarning("Cancelled", f"Registration cancelled: {msg}")

    # -----------------------------------------------------------------
    # PAGE 3: TRAIN MODEL
    # -----------------------------------------------------------------
    def build_train_model_page(self):
        header = ttk.Label(self.content_frame, text="Train Face Encodings", style="Header.TLabel")
        header.pack(anchor="w", padx=25, pady=(20, 5))
        
        sub = ttk.Label(self.content_frame, text="Compile captured student datasets into unified mathematical facial patterns.", style="Sub.TLabel")
        sub.pack(anchor="w", padx=25, pady=(0, 20))

        # Status Card
        status_card = ttk.Frame(self.content_frame, borderwidth=1, relief="solid", padding=20)
        status_card.pack(fill="x", padx=25, pady=10)

        dlib_status = "Available (dlib 128D encodings)" if train_model.HAS_FACE_RECOGNITION else "Not Installed (Using Grayscale Pixel Fallback Recognizer)"
        
        ttk.Label(status_card, text="AI Engine Profile Details", font=("Segoe UI", 12, "bold"), foreground=self.accent_color).pack(anchor="w", pady=(0,10))
        ttk.Label(status_card, text=f"• Recognition Engine: {dlib_status}", font=("Segoe UI", 11)).pack(anchor="w", pady=5)
        ttk.Label(status_card, text=f"• Dataset Source Folder: {utils.DATASET_DIR}", font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        ttk.Label(status_card, text=f"• Output Encoded Folder: {utils.ENCODINGS_DIR}", font=("Segoe UI", 10)).pack(anchor="w", pady=2)

        self.btn_train = ttk.Button(self.content_frame, text="Start Model Training", style="Accent.TButton", command=self.train_model_action)
        self.btn_train.pack(padx=25, pady=25, anchor="w")

        self.train_status_lbl = ttk.Label(self.content_frame, text="Awaiting command.", font=("Segoe UI", 11, "italic"))
        self.train_status_lbl.pack(padx=25, anchor="w")

    def train_model_action(self):
        self.train_status_lbl.configure(text="Training model. Please wait...")
        self.btn_train.configure(state="disabled")
        self.root.update()

        # Run training
        start_time = time.time()
        success = train_model.run_training()
        elapsed = round(time.time() - start_time, 2)

        self.btn_train.configure(state="normal")

        if success:
            msg = f"Training completed successfully in {elapsed} seconds!"
            self.train_status_lbl.configure(text=f"[SUCCESS] {msg}", foreground=self.accent_color)
            messagebox.showinfo("Success", msg)
        else:
            msg = "Training failed. Make sure you have registered students with image samples."
            self.train_status_lbl.configure(text=f"[FAILED] {msg}", foreground="#ff5555")
            messagebox.showerror("Error", msg)

    # -----------------------------------------------------------------
    # PAGE 4: VIEW LOGS / CSV
    # -----------------------------------------------------------------
    def build_view_logs_page(self):
        header = ttk.Label(self.content_frame, text="Attendance Records Logbook", style="Header.TLabel")
        header.pack(anchor="w", padx=25, pady=(20, 5))
        
        sub = ttk.Label(self.content_frame, text="Search attendance, filter logs, and export reports to CSV.", style="Sub.TLabel")
        sub.pack(anchor="w", padx=25, pady=(0, 20))

        # Filters Bar
        filter_bar = ttk.Frame(self.content_frame)
        filter_bar.pack(fill="x", padx=25, pady=5)

        ttk.Label(filter_bar, text="Search (Roll No / Name):").pack(side="left", padx=(0, 5))
        self.search_entry = ttk.Entry(filter_bar, width=20, font=("Segoe UI", 10))
        self.search_entry.pack(side="left", padx=(0, 15))
        
        # Bind key release to automatic filtering
        self.search_entry.bind("<KeyRelease>", self.filter_logs)

        btn_refresh = ttk.Button(filter_bar, text="Refresh", command=self.load_all_records_tree)
        btn_refresh.pack(side="left", padx=5)

        btn_csv = ttk.Button(filter_bar, text="Export CSV", style="Accent.TButton", command=self.export_csv_action)
        btn_csv.pack(side="right", padx=5)

        # Log Treeview
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=25, pady=15)

        # Scrollbar
        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side="right", fill="y")

        cols = ("ID", "Roll", "Name", "Date", "Time", "Subject", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", yscrollcommand=scroll.set)
        self.tree.pack(fill="both", expand=True)
        scroll.config(command=self.tree.yview)

        # Headings and widths
        widths = {"ID": 50, "Roll": 100, "Name": 180, "Date": 120, "Time": 100, "Subject": 120, "Status": 100}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c], anchor="center")

        # Initial Load
        self.load_all_records_tree()

    def load_all_records_tree(self):
        # Clear items
        for r in self.tree.get_children():
            self.tree.delete(r)

        records = database.get_all_attendance()
        for r in records:
            self.tree.insert("", "end", values=(
                r["attendance_id"],
                r["roll_number"],
                r["student_name"],
                r["date"],
                r["time"],
                r["subject"],
                r["status"]
            ))

    def filter_logs(self, event=None):
        q = self.search_entry.get().strip()
        if not q:
            self.load_all_records_tree()
            return

        # Clear items
        for r in self.tree.get_children():
            self.tree.delete(r)

        records = attendance.search_attendance(q)
        for r in records:
            self.tree.insert("", "end", values=(
                r["attendance_id"],
                r["roll_number"],
                r["student_name"],
                r["date"],
                r["time"],
                r["subject"],
                r["status"]
            ))

    def export_csv_action(self):
        try:
            csv_path = utils.export_attendance_to_csv()
            messagebox.showinfo("Export Successful", f"Full logbook exported to:\n{csv_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred:\n{e}")

    def on_exit(self):
        self.stop_camera()
        self.root.destroy()


# =====================================================================
#                        PART 3: APPLICATION INITS
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="Smart Classroom Attendance System CLI/GUI Launcher")
    parser.add_argument("--cli", action="store_true", help="Launch the program in interactive terminal mode")
    args = parser.parse_args()

    # Sync web data on startup to ensure dashboard is ready
    utils.sync_web_data()

    if args.cli:
        # Run Terminal Mode
        run_cli_menu()
    else:
        # Run GUI Mode (Default)
        root = tk.Tk()
        app = SmartAttendanceGUI(root)
        
        # Bind clean exit to close camera first
        root.protocol("WM_DELETE_WINDOW", app.on_exit)
        root.mainloop()


if __name__ == "__main__":
    main()
