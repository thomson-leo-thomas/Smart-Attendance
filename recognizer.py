"""
Facial recognition and detection core for the Smart Classroom Attendance System.
Detects faces in webcam streams, compares them to stored encodings,
performs anti-spoofing (eye-presence check), and outputs matches.
"""

import os
import cv2
import pickle
import numpy as np
from utils import CONFIDENCE_THRESHOLD, SCALE_FACTOR

# Import face_recognition if available
try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False

# File paths
ENCODINGS_FILE_DLIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "encodings", "face_encodings.pickle")
ENCODINGS_FILE_FALLBACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "encodings", "pixel_templates.pickle")


class SmartRecognizer:
    def __init__(self):
        """
        Initializes the face recognizer, loads Cascades and database files.
        """
        # Load OpenCV Haar Cascades for face and eyes (used in detection, fallback, & anti-spoofing)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        
        self.known_encodings = []
        self.known_names = []
        self.known_rolls = []
        self.mode = "dlib" if HAS_FACE_RECOGNITION else "fallback"
        
        # Load the models
        self.load_model()

    def load_model(self):
        """
        Loads stored encodings (pickle files) based on the running mode.
        """
        if self.mode == "dlib":
            if os.path.exists(ENCODINGS_FILE_DLIB):
                try:
                    with open(ENCODINGS_FILE_DLIB, "rb") as f:
                        data = pickle.load(f)
                    self.known_encodings = data.get("encodings", [])
                    self.known_names = data.get("names", [])
                    self.known_rolls = data.get("rolls", [])
                    print(f"[INFO] Loaded {len(self.known_names)} dlib facial encodings.")
                except Exception as e:
                    print(f"[ERROR] Failed to load dlib model: {e}. Switching to fallback mode.")
                    self.mode = "fallback"
            else:
                print("[WARN] dlib face_encodings.pickle not found. Will try fallback model.")
                self.mode = "fallback"

        if self.mode == "fallback":
            if os.path.exists(ENCODINGS_FILE_FALLBACK):
                try:
                    with open(ENCODINGS_FILE_FALLBACK, "rb") as f:
                        data = pickle.load(f)
                    self.known_encodings = data.get("templates", [])
                    self.known_names = data.get("names", [])
                    self.known_rolls = data.get("rolls", [])
                    print(f"[INFO] Loaded {len(self.known_names)} grayscale face templates (fallback mode).")
                except Exception as e:
                    print(f"[ERROR] Failed to load fallback model: {e}")
                    self.known_names = []
            else:
                print("[WARN] No trained face models found. Please register students and train.")
                self.known_names = []

    def verify_liveness(self, face_gray, face_color):
        """
        Simple Anti-Spoofing: checks for the presence of eyes inside the face region.
        A printed paper or screen photo often has reflections, lower depth, or the eye cascade 
        fails to detect distinct, active pupils compared to a live person.
        Also tracks if eyes are visible to ensure it's not a static image.
        Returns: True if eyes are detected (indicates high probability of a real face), False otherwise.
        """
        # Detect eyes in the grayscale face region
        eyes = self.eye_cascade.detectMultiScale(face_gray, scaleFactor=1.15, minNeighbors=4, minSize=(15, 15))
        
        # Real person must have eyes visible. A photo or display might fail this
        # or have too many reflections.
        if len(eyes) >= 1:
            return True
        return False

    def recognize(self, frame):
        """
        Processes a single BGR frame, detects faces, checks liveness, 
        and matches them against the database.
        
        Returns a list of dicts: [ { 'box': (top, right, bottom, left), 
                                    'name': name, 
                                    'roll': roll, 
                                    'confidence': confidence,
                                    'liveness': bool } ]
        """
        results = []
        if not self.known_names:
            return results

        # Scale down frame for speed
        small_frame = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)

        if self.mode == "dlib":
            # Convert BGR to RGB for face_recognition
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detect face locations and encodings
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale coordinates back up to original size
                top_up = int(top / SCALE_FACTOR)
                right_up = int(right / SCALE_FACTOR)
                bottom_up = int(bottom / SCALE_FACTOR)
                left_up = int(left / SCALE_FACTOR)

                # Crop face from original frame for liveness check
                face_crop_color = frame[top_up:bottom_up, left_up:right_up]
                if face_crop_color.size == 0:
                    continue
                face_crop_gray = cv2.cvtColor(face_crop_color, cv2.COLOR_BGR2GRAY)
                
                # Anti-spoofing
                is_live = self.verify_liveness(face_crop_gray, face_crop_color)

                # Compute face distances
                distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                best_idx = np.argmin(distances)
                distance = distances[best_idx]
                
                # Convert distance to confidence percentage
                confidence = (1.0 - distance) * 100.0
                confidence = max(0.0, min(100.0, confidence))

                name = "Unknown"
                roll = "Unknown"
                
                if confidence >= CONFIDENCE_THRESHOLD:
                    name = self.known_names[best_idx]
                    roll = self.known_rolls[best_idx]

                results.append({
                    "box": (top_up, right_up, bottom_up, left_up),
                    "name": name,
                    "roll": roll,
                    "confidence": round(confidence, 1),
                    "liveness": is_live
                })

        else:
            # Fallback mode using Custom Grayscale Pixel Template Matcher
            gray_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using Haar Cascade on small grayscale frame
            faces = self.face_cascade.detectMultiScale(gray_small, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                # Scale coordinates back up
                x_up = int(x / SCALE_FACTOR)
                y_up = int(y / SCALE_FACTOR)
                w_up = int(w / SCALE_FACTOR)
                h_up = int(h / SCALE_FACTOR)

                top_up = y_up
                left_up = x_up
                bottom_up = y_up + h_up
                right_up = x_up + w_up

                # Crop face
                face_crop_color = frame[top_up:bottom_up, left_up:right_up]
                if face_crop_color.size == 0:
                    continue
                face_crop_gray = cv2.cvtColor(face_crop_color, cv2.COLOR_BGR2GRAY)

                # Anti-spoofing check
                is_live = self.verify_liveness(face_crop_gray, face_crop_color)

                # Prepare cropped face for template matching
                resized = cv2.resize(face_crop_gray, (100, 100))
                normalized = cv2.equalizeHist(resized)
                flat_vector = normalized.flatten().astype(np.float32)
                
                norm = np.linalg.norm(flat_vector)
                if norm > 0:
                    flat_vector = flat_vector / norm

                # Calculate Cosine Similarities against all known templates
                # (since vectors are unit length, dot product is cosine similarity)
                similarities = [np.dot(flat_vector, temp) for temp in self.known_encodings]
                
                name = "Unknown"
                roll = "Unknown"
                confidence = 0.0

                if similarities:
                    best_idx = np.argmax(similarities)
                    similarity = similarities[best_idx]
                    
                    # Convert to percentage
                    confidence = similarity * 100.0
                    confidence = max(0.0, min(100.0, confidence))

                    if confidence >= CONFIDENCE_THRESHOLD:
                        name = self.known_names[best_idx]
                        roll = self.known_rolls[best_idx]

                results.append({
                    "box": (top_up, right_up, bottom_up, left_up),
                    "name": name,
                    "roll": roll,
                    "confidence": round(confidence, 1),
                    "liveness": is_live
                })

        return results
