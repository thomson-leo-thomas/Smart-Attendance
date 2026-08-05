# AI-Based Smart Classroom Attendance System

An automated, biometric AI agent that marks student attendance using facial recognition while preventing proxy attendance. The system runs locally via a Tkinter GUI or a Terminal CLI, logs attendance transactions into an SQLite database, logs parent notification alerts, and compiles statistics for a sleek, Vercel-hostable analytics dashboard.

---

## 🚀 Features

1. **Student Registration**: Input student information and capture 10 face snapshots using a local camera.
2. **Dual Recognition Engines**: Utilizes advanced 128D `dlib` embeddings with a pure-OpenCV/grayscale template matching fallback (enabling execution on Windows systems without C++ compilation requirements).
3. **Anti-Spoofing Check**: Applies eye-reflectance and micro-movement analysis inside facial coordinates to block static paper-photo or mobile-screen flashing attacks.
4. **Attendance Management**: SQLite database logic prevents double-attendance marks today for a subject. Automatically marks unmarked students as `Absent` and triggers simulated parent alerts.
5. **Classroom Analytics Dashboard**: Pre-built dashboard showing metrics, daily trends, status distributions (Chart.js), registries, and search filters.
6. **Dual Mode Entry**: Run `python main.py` for a modern dark desktop GUI, or `python main.py --cli` for an interactive command-line interface.

---

## 📁 Directory Structure

```text
SmartAttendance/
├── main.py                # Launcher GUI (Tkinter) and terminal CLI Menu
├── register.py            # Image capture and student database registration
├── attendance.py          # Log transactions (Present/Absent) and alerts
├── recognizer.py          # Liveness validation and similarity matching
├── database.py            # SQLite initializer and raw query functions
├── train_model.py         # Extracts 128D encodings / grayscale templates
├── utils.py               # Path constants, CSV exports, SMS/Email simulator
├── requirements.txt       # Python dependencies list
├── .gitignore             # Git ignored cache files
│
├── dataset/               # Captured student snapshots (Ignored in Git)
├── encodings/             # Model weight pickles (Ignored in Git)
├── attendance/            # Exported CSV sheets (Ignored in Git)
├── database/              # SQLite DB location (Ignored in Git)
├── reports/               # Project report markdown and Viva Q&As
│   └── project_report.md  
└── web/                   # Vercel-hostable Frontend Dashboard
    ├── index.html         
    ├── style.css          
    ├── app.js             
    └── vercel.json        
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12+ installed.
- Integrated or USB Webcam.

### Step 1: Clone and install packages
Open your terminal inside the project directory and run:
```bash
pip install -r requirements.txt
```
*Note: If `face-recognition` installation fails due to C++ compilation or CMake requirements on Windows, simply delete `face-recognition>=1.3.0` from `requirements.txt` and install the remaining packages. The project features an automatic fallback to pure OpenCV/NumPy template matching.*

### Step 2: Seed the testing database (Optional)
To instantly pre-load the database and Vercel analytics dashboard with 10 dummy students and 90 records of attendance logs:
```bash
python seed_data.py
```

### Step 3: Run the application
- **GUI Mode (Default)**:
  ```bash
  python main.py
  ```
- **Terminal CLI Mode**:
  ```bash
  python main.py --cli
  ```

---

## 🌐 Web Dashboard Deployment (Vercel)

To host the analytics dashboard on Vercel:

1. Create a GitHub repository and push your project code.
2. Go to [Vercel](https://vercel.com) and import your repository.
3. **Important**: Set the **Root Directory** settings to `web`.
4. Deploy!
5. Whenever you run your local python scanner, it updates `web/attendance_data.json`. Commit and push this file to GitHub to update your live dashboard charts instantly.
