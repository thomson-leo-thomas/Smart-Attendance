# Academic Project Report
## AI-Based Smart Classroom Attendance System

**Course:** B.Tech Computer Science & Engineering (Final Year Project / AI Lab Submission)  
**Author:** Final Year B.Tech CSE Student  
**System Version:** v2.0 (Dual GUI/CLI with Vercel Analytics Dashboard)

---

## 1. Introduction
Traditional classroom attendance methods—such as calling out roll numbers or passing around sign-sheet logs—are highly inefficient, time-consuming, and vulnerable to manual errors and proxy attendance. In a standard 50-minute lecture, taking attendance manually consumes 10% to 15% of the class time.

Biometric solutions (fingerprint or iris scanners) require dedicated hardware, create long queues, and have sanitary concerns. 

This project implements an **AI-Based Smart Classroom Attendance System** that automatically logs student presence using facial recognition. The system leverages computer vision to scan faces in real-time via a local camera feed, matches them against registered templates, applies anti-spoofing filters, logs present markers in an SQLite database, sends absence alerts to parents, and syncs analytics to a web dashboard hosted on Vercel.

---

## 2. Problem Statement
Manual attendance processes suffer from:
1. **Time Loss**: Significant lecture time is wasted calling roll numbers.
2. **Proxy Attendance**: Students sign attendance sheets or answer roll calls for absent friends.
3. **Data Retrieval Overhead**: Manual calculation of attendance percentages for monthly reports is tedious and error-prone.
4. **Lack of Instant Communication**: Parents receive no real-time notification if a student skips a class.

**Proposed Solution**: Create a non-intrusive, automated, and tamper-proof computer vision agent that marks attendance within seconds of scanning a student's face, checks for spoofing (photo attacks), logs historical transactions in a database, and exposes data to a web dashboard.

---

## 3. Objectives
- Develop a Python desktop application (supporting GUI and CLI) for classroom registration and real-time attendance tracking.
- Implement robust facial recognition (using the advanced 128D dlib descriptor with a pure-OpenCV/grayscale template matching fallback for Windows compatibility).
- Prevent proxy attendance using liveness checks (Haar Cascade eye detection to verify human facial geometry and micro-movement checks).
- Provide automated attendance closure logic that flags absent students and logs simulated SMS/Email notifications to parents.
- Export records to structured CSV formats and sync databases with a static JSON payload for a Vercel-hosted analytics dashboard.

---

## 4. Literature Review
Facial recognition pipelines generally follow three stages:
1. **Face Detection**: Identifying bounding coordinates of a face in a frame. Common methods include Viola-Jones (Haar Cascades), Histograms of Oriented Gradients (HOG), and Convolutional Neural Networks (CNN/SSD).
2. **Feature Extraction**: Extracting facial landmark descriptors. The `dlib` library uses a deep residual network model to extract 128-dimensional vector descriptors where faces of the same person are mathematically close.
3. **Classification / Matching**: Comparing descriptors using distance metrics (Euclidean or Cosine distance) to determine identity.

To prevent paper-photo spoofing, researchers implement liveness cues (e.g., eye blink frequency, optical flow movements, and depth maps). This system applies eye-geometry validation within OpenCV frames to ensure face structures contain active pupil regions.

---

## 5. System Architecture
The system follows a modular architecture separating data processing, interface layers, visual recognition, and database operations.

```mermaid
graph TD
    A[Start] --> B[Open Webcam Frame]
    B --> C[Detect Face using Cascade / HOG]
    C --> D{Face Detected?}
    D -- NO --> B
    D -- YES --> E[Perform Anti-Spoofing Check]
    E --> F{Is Face Live?}
    F -- NO --> G[Display Spoof Warning / Reject]
    G --> B
    F -- YES --> H[Extract Facial Encodings / Pixel Vector]
    H --> I[Compare with Stored Encodings]
    I --> J{Confidence >= Threshold?}
    J -- NO --> K[Unknown Student / Display Frame]
    K --> B
    J -- YES --> L{Attendance Already Marked Today?}
    L -- YES --> M[Display Already Marked Alert]
    M --> B
    L -- NO --> N[Mark Present in Database]
    N --> O[Sync Web Dashboard JSON]
    O --> P[Display Success Frame]
    P --> B
    B --> Q[Quit Session]
    Q --> R[Close Session: Mark Unmarked as Absent]
    R --> S[Send simulated SMS/Email Parent Notifications]
    S --> T[Export CSV Sheet]
    T --> U[End]
```

---

## 6. AI Agent Design

### PEAS Analysis
| Agent Type | Performance Measure | Environment | Actuators | Sensors |
| :--- | :--- | :--- | :--- | :--- |
| **Smart Classroom Attendance Agent** | • Recognition Accuracy %<br>• Speed of logging<br>• Spoofing detection rate<br>• Prevention of duplicate records | • Classroom/Lab room<br>• Lighting variations<br>• Webcam field-of-view<br>• Group of students | • GUI Window (Tkinter)<br>• SQLite DB Updates<br>• CSV / JSON File exporters<br>• Parent Notification Logs | • USB/Integrated Webcam<br>• Keyboard/Mouse inputs |

### Environment Classification
1. **Partially Observable**: The camera sensor only observes the field-of-view. It cannot observe who is in the classroom outside the camera frame.
2. **Stochastic**: Lighting conditions, student movements, head rotations, and camera noise are unpredictable.
3. **Sequential**: The state of marking attendance depends on previous actions (e.g., if a student has already been marked today, the next face check uses that historical database state to reject duplicates).
4. **Dynamic**: The environment changes constantly as students walk in, out, or block the camera view.
5. **Discrete**: Bounding box coordinates, database IDs, roll numbers, and attendance states ("Present", "Absent") are discrete values.
6. **Single-Agent**: The main scanning agent runs independently, marking status on a single database.

### Rationality
The AI agent behaves rationally by maximizing its performance measure. It:
1. Filters out static images (anti-spoofing) to ensure accuracy.
2. Implements a similarity distance threshold (60%) below which it flags "Unknown" to prevent false positives.
3. Checks database states before running insertions to eliminate duplicate records.
4. Automatically calculates absents and sends alerts upon session termination to close the attendance loop.

---

## 7. Innovation
1. **Dual Engine Recognizer**: Integrates advanced 128D dlib encodings, but seamlessly switches to a pure grayscale pixel feature template-matcher if dlib is not compile-ready. This maximizes cross-platform compatibility.
2. **Passive Eye-Presence Liveness Check**: Avoids expensive hardware. It monitors facial eye-coordinate reflections within the bounding box to distinguish a physical face from a paper/mobile screen photo.
3. **Parent Alert System & Vercel Dashboard Sync**: Automates notification dispatches to parents for absentees and exports statistics directly to a static JSON backend which feeds a sleek dashboard on Vercel.

---

## 8. Algorithms and Pseudocode

### Image Registration & Capture
1. Receive Roll Number, Name, Department, Semester.
2. Create folder `dataset/RollNumber_Name/`.
3. Open camera feed.
4. Capture frames, run Haar Cascade Face Detection.
5. Crop detected face area, save as `face_i.jpg` (capture 10 samples).
6. Save details to SQLite `students` table.

### Model Training
```text
FUNCTION TrainModel():
    INITIALIZE arrays: encodings, names, rolls
    FOR each folder in dataset/:
        EXTRACT roll, name from folder name
        FOR each image in folder:
            IF HAS_FACE_RECOGNITION_LIB:
                LOAD image, DETECT face locations
                EXTRACT 128D encoding
                APPEND to encodings, name to names, roll to rolls
            ELSE (Fallback):
                LOAD image, CONVERT to grayscale, DETECT face bounding box
                CROP face, RESIZE to 100x100 pixels, EQUALIZE histogram
                FLATTEN to 10000-D vector, NORMALIZE vector norm
                APPEND vector to encodings, name to names, roll to rolls
    SAVE encodings, names, rolls to Pickle file
```

### Face Recognition & Attendance Marking
```text
FUNCTION ProcessFrame(frame, subject):
    FACES = DetectFaces(frame)
    FOR each face in FACES:
        is_live = DetectEyesInsideFaceBox(face)
        IF NOT is_live:
            DISPLAY "SPOOF ALERT"
            CONTINUE
        
        encoding = ExtractEncoding(face)
        best_match, confidence = MatchWithStoredEncodings(encoding)
        
        IF confidence >= THRESHOLD:
            student = FetchStudentFromDB(best_match.roll)
            IF AlreadyMarkedToday(student.roll, subject):
                DISPLAY "Already Marked"
            ELSE:
                MarkPresentInSQLite(student.roll, student.name, subject)
                SyncVercelJSON()
                DISPLAY "Attendance Marked"
        ELSE:
            DISPLAY "Unknown"
```

---

## 9. Database Design
The SQLite database contains two tables structured as follows:

```sql
-- Students Registry Table
CREATE TABLE IF NOT EXISTS students (
    roll_number TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    semester TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Attendance Transaction Logs Table
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT NOT NULL,
    student_name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    subject TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (roll_number) REFERENCES students(roll_number),
    UNIQUE(roll_number, date, subject) -- Prevents duplicate marks on the same day for a subject
);
```

---

## 10. Implementation Code File Summary
- `main.py`: Entry point for GUI and CLI. Controls canvas drawing and loop timers.
- `register.py`: Controls OpenCV capture window and saves image datasets.
- `train_model.py`: Computes dlib vector descriptors or builds grayscale templates.
- `recognizer.py`: Houses detection pipelines, liveness check, and similarity comparisons.
- `database.py`: Direct database SQLite connector and query helpers.
- `utils.py`: Manages directories, CSV/JSON exports, and parent notification dispatches.
- `seed_data.py`: Developer seed script to populate testing records.
- `web/`: Contains static HTML/CSS/JS frontend files deployed on Vercel.

---

## 11. Testing and Verification Plan

### Test Cases
| Test Case ID | Test Scenario | Input / Action | Expected Output | Actual Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Student Registration | Input fields & capture 10 faces | Directory created, pictures saved, DB record inserted | Same as expected | **PASS** |
| **TC-02** | Model Training | Click "Start Training" | Generates Pickle model file under `encodings/` | Same as expected | **PASS** |
| **TC-03** | Live Scanning (Normal) | Live registered student in frame | Frame displays green box, name, roll, confidence % | Same as expected | **PASS** |
| **TC-04** | Live Attendance Logging | Live scan of registered student | SQLite database receives record, exports updated Vercel JSON | Same as expected | **PASS** |
| **TC-05** | Duplicate Check | Registered student stands in frame again | Screen displays warning "Attendance already marked" | Same as expected | **PASS** |
| **TC-06** | Spoof Detection | Hold a printed smartphone picture of face | Frame box turns orange/red, displays "SPOOF: Name" | Same as expected | **PASS** |
| **TC-07** | Close Session Absent logs | Click "Close Session & Notify" | Unmarked students logged as "Absent" in DB, logs alert dispatch | Same as expected | **PASS** |
| **TC-08** | CSV Export | Click "Export CSV" | CSV created in `attendance/` with matching rows | Same as expected | **PASS** |
| **TC-09** | Vercel Sync | Check web dashboard after marking | Metrics and charts instantly refresh to match SQL records | Same as expected | **PASS** |

---

## 12. Advantages (10 Points)
1. **Automation**: Completely eliminates manual roll-calls.
2. **Speed**: Processes multiple face coordinates within milliseconds.
3. **Anti-Spoofing**: Prevents photo-flashing spoof attacks via eye-liveness validation.
4. **Duplicate Prevention**: SQLite constraints block double entries on the same day.
5. **No Cloud Dependencies**: Works entirely offline for local execution.
6. **Fallback Capability**: Runs on basic computers via grayscale pixel comparisons if `dlib` is absent.
7. **Dual Interface**: Supports rich desktop GUI and terminal CLI.
8. **Real-time Notifications**: Instantly drafts alerts when attendance session closes.
9. **Visual Analytics**: Interactive, stylish dashboard hosted on Vercel.
10. **Modular Codebase**: Adheres to PEP 8 standards, making it easy to extend and maintain.

---

## 13. Limitations (8 Points)
1. **Lighting Sensitivity**: Extremely dark or back-lit environments can degrade Haar Cascade face detection.
2. **Angles/Occlusions**: Face must look straight into the camera (side angles reduce matching confidence).
3. **Desktop Dependencies**: Standard Tkinter requires a local display server and hardware cameras.
4. **Eye-Check Fallibility**: If eyeglasses reflect heavy glare, the eye-cascade might fail, resulting in temporary liveness rejection.
5. **Local Database Storage**: Data is saved in a local SQLite file (requires manual deployment/push to synchronize with cloud servers).
6. **No Auto-Sync to Web**: Synchronization requires clicking "Export" or marking attendance locally to dump the JSON file (which must be committed to git to update Vercel).
7. **Scalability limits in Fallback Mode**: The grayscale pixel matching fallback is less accurate for classes larger than 50 students compared to the 128D dlib vector classifier.
8. **Camera Focus Constraints**: Standard USB webcams may fail to focus on students sitting in the back rows of a large classroom.

---

## 14. Future Scope (10 Points)
1. **Real-time SMS/WhatsApp APIs**: Integrate Twilio or WhatsApp Business API for instant parent alerts.
2. **IP Camera Integration**: Connect overhead classroom security cameras instead of a single instructor webcam.
3. **Liveness Blink Rates**: Track dynamic facial landmark movements over time to verify actual blinks.
4. **Multi-face Recognition**: Run batch face recognitions on groups rather than scanning individuals one by one.
5. **Cloud Database Integration**: Migrate SQLite to PostgreSQL or Firebase Firestore.
6. **Hybrid Face-Voice Verification**: Combine facial recognition with voice prints for multi-modal biometric check-ins.
7. **Vercel Dynamic REST API**: Build a FastAPI/Flask backend hosted on Vercel with web-based camera capture (WebRTC).
8. **Automatic Scheduler**: Auto-start attendance tracking according to class timetables.
9. **Student Portal**: Create logins for students to view their historical attendance charts.
10. **Mask/Glasses Robustness**: Use deep CNN models to recognize students wearing masks or accessories.

---

## 15. Conclusion
The AI-Based Smart Classroom Attendance System represents a modern biometric application of computer vision in education. By executing face-geometry checks locally, utilizing database integrity constraints, and compiling offline records for static web views, this project demonstrates a highly practical, reliable, and user-friendly system. The dual-engine implementation ensures compatibility on all student computers, making it an excellent blueprint for academia and biometric research.

---

## 16. References
- Viola, P., & Jones, M. (2001). Rapid object detection using a boosted cascade of simple features. CVPR.
- King, D. E. (2009). Dlib-ml: A Machine Learning Toolkit. Journal of Machine Learning Research.
- OpenCV Documentation (https://docs.opencv.org)
- face_recognition repository (https://github.com/ageitgey/face_recognition)
- Python SQLite3 documentation (https://docs.python.org/3/library/sqlite3.html)

---

## 17. Viva Questions and Answers (20 Q&As)

#### Q1: What is a Haar Cascade, and how does it detect faces?
**A:** A Haar Cascade is a machine learning object detection algorithm proposed by Viola and Jones. It uses Haar-like features (rectangular filters that compute pixel intensity differences between adjacent regions) to identify structures like eyes, nose, and cheeks. It runs frames through a cascade of classifiers to quickly reject non-face regions.

#### Q2: What is the purpose of resizing frames to 0.25 size in the recognizer code?
**A:** Resizing the frames down decreases the image resolution by 4 times, reducing the total pixel count by 16 times. This decreases CPU computation workload, allowing the face recognition algorithm to process frames in real-time (higher frames-per-second) on standard hardware.

#### Q3: Why does dlib extract a 128-dimensional vector for a face?
**A:** The 128D vector represents facial features (distances between eyes, nose width, jawline shape) mapped by a deep neural network. The network is trained such that vectors of the same individual are close (low Euclidean distance), while vectors of different individuals are far.

#### Q4: How is duplicate attendance prevented in your database schema?
**A:** The `attendance` table includes a SQL `UNIQUE(roll_number, date, subject)` constraint. If the system attempts to insert another row for the same student on the same day for that subject, SQLite throws an `IntegrityError`, which the code catches and handles gracefully.

#### Q5: Explain the custom fallback recognition algorithm.
**A:** If `dlib` is not available, the fallback algorithm detects faces using a Haar Cascade, crops and resizes them to 100x100 grayscale, equalizes contrast, flattens them into a 10,000-dimensional vector, and normalizes it. It compares vectors using Cosine Similarity (dot product) to find the closest template.

#### Q6: How does the liveness check work in your code?
**A:** It checks for the presence of eyes (using `haarcascade_eye.xml`) inside the cropped bounding box of the face. Printed paper or mobile screens often lack depth, reflection properties, or details required for the eye classifier to activate.

#### Q7: Why do we use direct show `cv2.CAP_DSHOW` when opening the VideoCapture on Windows?
**A:** `cv2.CAP_DSHOW` uses Windows DirectShow API, which initializes the web camera significantly faster compared to default APIs, avoiding GUI delays or freezing on startup.

#### Q8: What does histogram equalization do to face images?
**A:** Histogram equalization (`cv2.equalizeHist`) improves the contrast of grayscale images by stretching out the intensity range, reducing lighting variances so that matching algorithms perform more reliably.

#### Q9: What is the significance of the pickle file in the system?
**A:** The pickle file is used to serialize Python dictionaries containing the facial encodings (or templates) and their associated labels (names and roll numbers) to the disk. This allows the recognizer to load them directly into memory without retraining.

#### Q10: How are student absences recorded?
**A:** When the user clicks "Close Session" in the GUI or selects it in the CLI, the system retrieves all registered students, identifies who was *not* marked "Present" today, and logs them as "Absent" in SQLite.

#### Q11: Explain the PEAS analysis for this AI Agent.
**A:** **P (Performance)**: Accuracy, detection speed, proxy prevention. **E (Environment)**: Classroom, lighting, students. **A (Actuators)**: GUI canvas, database rows, notifications. **S (Sensors)**: Webcam, keyboard, mouse.

#### Q12: Why is the classroom environment classified as "Partially Observable"?
**A:** Because the camera sensor can only capture students standing directly within its limited field-of-view; it cannot observe students sitting elsewhere in the classroom or outside.

#### Q13: What happens when the face similarity confidence falls below 60%?
**A:** The recognizer classifies the face as "Unknown" and does not record attendance. This prevents false positive matchings of random objects or strangers.

#### Q14: How does the system update the Vercel dashboard?
**A:** Every time database insertions occur, the python script executes `utils.sync_web_data()`, which queries SQLite and writes it to `web/attendance_data.json`. When this file is committed and pushed to the Git repository, Vercel updates the analytics instantly.

#### Q15: Why is SQLite used instead of a normal text file?
**A:** SQLite is a relational database management system that supports structured SQL queries, indexes for fast lookups, data integrity constraints, and transaction rollbacks to prevent data corruption.

#### Q16: What is a dlib face distance?
**A:** It is the Euclidean distance between two 128D face vectors. A distance of 0 indicates an identical face. Typically, a distance below 0.6 is considered a positive match.

#### Q17: What are the main limitations of this system?
**A:** High sensitivity to extreme lighting variations, dependence on local desktop hardware/cam, and the static manual Git commit cycle required to sync records to Vercel.

#### Q18: How can this system be hosted completely on Vercel in the future?
**A:** By re-architecting the system with a web-frontend (HTML5/React) that streams webcam feeds via WebRTC to a Python backend API (FastAPI) hosted on a cloud server connected to a cloud database (like Supabase or MongoDB).

#### Q19: What is the PEP 8 standard?
**A:** PEP 8 is Python's style guide. It defines coding conventions such as using 4 spaces for indentation, writing descriptive snake_case names for functions/variables, and maintaining modular imports to ensure code readability.

#### Q20: How does the parent notification system work?
**A:** When a session is closed and absences are logged, the system logs dispatches to `logs/parent_alerts.log` containing student names and timestamps. This log serves as a gateway stub for API integration (like Twilio or SMTP servers).
