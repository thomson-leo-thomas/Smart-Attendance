# 🎓 AI-Based Smart Classroom Attendance System

An intelligent classroom attendance system that uses **Artificial Intelligence**, **Computer Vision**, and **Facial Recognition** to automate attendance management. The system recognizes registered students in real time, prevents proxy attendance using liveness verification, stores attendance records in an SQLite database, and provides analytics through a web dashboard.

---

## 📖 Overview

Traditional attendance methods are time-consuming and prone to human errors and proxy attendance. This project replaces manual attendance with an AI-powered solution that automatically identifies students using facial recognition technology and records attendance digitally.

The system supports both a **Tkinter Desktop GUI** and an **interactive Command Line Interface (CLI)**. Attendance records are securely stored, exported as CSV files, and synchronized with a web-based analytics dashboard.

---

## ✨ Features

- 👤 Student Registration with webcam-based face capture
- 🤖 AI-powered Facial Recognition using OpenCV and `face_recognition`
- 🔄 Automatic fallback to OpenCV template matching when `dlib` is unavailable
- 🛡️ Passive Liveness Detection to reduce proxy attendance
- ✅ Automatic attendance marking
- 🚫 Duplicate attendance prevention
- 📊 Real-time Attendance Analytics Dashboard
- 📁 CSV Export of attendance reports
- 🗄️ SQLite database for student and attendance records
- 📧 Simulated parent notification system
- 🖥️ Supports both GUI and CLI modes

---

# 🏗️ System Architecture

```
                 Student Registration
                         │
                         ▼
                  Face Image Capture
                         │
                         ▼
               Face Encoding / Training
                         │
                         ▼
                  Live Webcam Stream
                         │
                         ▼
                   Face Detection
                         │
                         ▼
               Face Recognition Engine
                         │
               ┌─────────┴─────────┐
               │                   │
          Unknown Face        Recognized Face
               │                   │
               ▼                   ▼
        Reject Attendance     Duplicate Check
                                    │
                             ┌──────┴──────┐
                             │             │
                      Already Marked     New Record
                             │             │
                             ▼             ▼
                      Display Message   Store Attendance
                                            │
                                            ▼
                                   SQLite Database
                                            │
                                            ▼
                              Reports • Dashboard • CSV
```

---

# 🧠 AI Agent Design

The project is designed as an intelligent AI agent capable of perceiving the classroom environment through a webcam and autonomously recording student attendance.

### Performance Measure

- High face recognition accuracy
- Fast attendance marking
- Zero duplicate entries
- Reduced proxy attendance
- Accurate attendance reports

### Environment

- Classroom
- Students
- Faculty
- Webcam
- SQLite Database

### Actuators

- Display recognized student
- Record attendance
- Generate reports
- Export CSV
- Update dashboard

### Sensors

- Webcam
- Student database
- Face encodings
- System date & time
- User input

---

# 🌍 Environment Classification

| Property | Classification |
|-----------|---------------|
| Observability | Partially Observable |
| Determinism | Stochastic |
| Episode Type | Sequential |
| Dynamics | Dynamic |
| State Space | Discrete |
| Agents | Single Agent |

---

# 🧠 Rationality

The AI agent behaves rationally by

- Detecting student faces in real time.
- Comparing facial encodings with registered students.
- Applying a confidence threshold before marking attendance.
- Preventing duplicate attendance records.
- Performing passive liveness verification.
- Rejecting unknown or low-confidence faces.
- Handling errors such as unavailable webcams or missing datasets gracefully.

---

# 💡 Innovations

### 🔹 AI-Based Anti-Spoofing

Detects eye presence to reduce attendance fraud using photographs or mobile screens.

### 🔹 Real-Time Analytics Dashboard

Displays attendance statistics, participation trends, and absentee reports.

---

# 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| Language | Python 3.12 |
| Computer Vision | OpenCV |
| Face Recognition | face_recognition (dlib) |
| GUI | Tkinter |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Image Processing | Pillow |
| Dashboard | HTML, CSS, JavaScript |
| Charts | Chart.js |

---

# 📁 Project Structure

```
SmartAttendance/
│
├── main.py
├── register.py
├── recognizer.py
├── attendance.py
├── database.py
├── train_model.py
├── utils.py
├── requirements.txt
│
├── dataset/
├── encodings/
├── attendance/
├── database/
├── reports/
│   ├── AI_Report.pdf
│   └── project_report.md
│
└── web/
    ├── index.html
    ├── style.css
    ├── app.js
    └── vercel.json
```

---

# ⚙️ Installation

```bash
git clone https://github.com/<username>/SmartAttendance.git

cd SmartAttendance

pip install -r requirements.txt
```

---

# ▶️ Run the Project

### Desktop GUI

```bash
python main.py
```

### Command Line Interface

```bash
python main.py --cli
```

# 📄 Project Report

The complete project report is available here.

📘 **[AI-Based Smart Classroom Attendance System Report](report assignment.pdf)**

---

# 🚀 Future Enhancements

- Deep Learning based Anti-Spoofing
- Multi-camera classroom support
- Cloud Database Integration
- RFID + Face Recognition Hybrid System
- Mobile Application
- Email/SMS Integration
- Teacher Authentication
- Face Mask Recognition
- Attendance using Edge AI
- Cloud-based Analytics Dashboard

---

# 👨‍💻 Author

**Thomson Leo Thomas**

Group 2

Artificial Intelligence Lab Project

---

## ⭐ If you found this project useful, consider giving it a Star!
