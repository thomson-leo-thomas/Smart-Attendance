"""
Training module for the Smart Classroom Attendance System.
Processes captured face images from the dataset directory and
generates face encodings/templates saved in the encodings folder.
"""

import os
import cv2
import pickle
import numpy as np
from utils import DATASET_DIR, ENCODINGS_DIR

# Flags and filenames
ENCODINGS_FILE_DLIB = os.path.join(ENCODINGS_DIR, "face_encodings.pickle")
ENCODINGS_FILE_FALLBACK = os.path.join(ENCODINGS_DIR, "pixel_templates.pickle")

# Try to import face_recognition
try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False


def train_dlib_model():
    """
    Computes 128D face encodings using face_recognition (dlib).
    Saves encodings and labels as a dictionary to face_encodings.pickle.
    """
    print("\n[INFO] Training with face_recognition (dlib 128D encodings)...")
    known_encodings = []
    known_names = []
    known_rolls = []

    if not os.path.exists(DATASET_DIR):
        print(f"[ERROR] Dataset directory '{DATASET_DIR}' not found. Register students first.")
        return False

    subdirs = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]
    
    if not subdirs:
        print("[ERROR] No student dataset folders found. Register students first.")
        return False

    total_images_processed = 0

    for subdir in subdirs:
        # Expected format: "rollNumber_studentName"
        parts = subdir.split("_")
        if len(parts) >= 2:
            roll = parts[0]
            name = "_".join(parts[1:])
        else:
            roll = "Unknown"
            name = subdir

        student_dir = os.path.join(DATASET_DIR, subdir)
        for img_name in os.listdir(student_dir):
            img_path = os.path.join(student_dir, img_name)
            
            if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            try:
                # Load image
                image = face_recognition.load_image_file(img_path)
                
                # Detect face location(s)
                face_locations = face_recognition.face_locations(image)
                
                if len(face_locations) == 0:
                    print(f"[WARN] No face found in: {subdir}/{img_name}. Skipping.")
                    continue
                
                # Compute 128D encoding
                encodings = face_recognition.face_encodings(image, face_locations)
                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(name)
                    known_rolls.append(roll)
                    total_images_processed += 1
            except Exception as e:
                print(f"[ERROR] Failed to process {img_path}: {e}")

    if total_images_processed == 0:
        print("[ERROR] No face encodings could be extracted. Check image quality.")
        return False

    # Save encodings
    data = {"encodings": known_encodings, "names": known_names, "rolls": known_rolls}
    with open(ENCODINGS_FILE_DLIB, "wb") as f:
        pickle.dump(data, f)

    print(f"[SUCCESS] Trained dlib model. Processed {total_images_processed} images.")
    print(f"Encodings saved to: {ENCODINGS_FILE_DLIB}")
    return True


def train_fallback_model():
    """
    Fallback training method: extracts flattened, normalized 100x100 grayscale face vectors.
    Saves templates and labels as a dictionary to pixel_templates.pickle.
    """
    print("\n[INFO] Fallback: Training custom Grayscale Pixel Template Matcher...")
    known_templates = []
    known_names = []
    known_rolls = []

    if not os.path.exists(DATASET_DIR):
        print(f"[ERROR] Dataset directory '{DATASET_DIR}' not found.")
        return False

    subdirs = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]
    
    if not subdirs:
        print("[ERROR] No student dataset folders found. Register students first.")
        return False

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    total_images_processed = 0

    for subdir in subdirs:
        parts = subdir.split("_")
        if len(parts) >= 2:
            roll = parts[0]
            name = "_".join(parts[1:])
        else:
            roll = "Unknown"
            name = subdir

        student_dir = os.path.join(DATASET_DIR, subdir)
        for img_name in os.listdir(student_dir):
            img_path = os.path.join(student_dir, img_name)
            
            if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            # Read image and convert to gray
            img = cv2.imread(img_path)
            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect face
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 50))
            
            cropped_face = None
            if len(faces) > 0:
                # Use the detected face bounding box
                x, y, w, h = faces[0]
                cropped_face = gray[y:y+h, x:x+w]
            else:
                # If cascade fails to detect inside already cropped sample, use the whole image
                cropped_face = gray

            # Resize to standardized template size
            resized_face = cv2.resize(cropped_face, (100, 100))
            
            # Normalize pixel intensities
            normalized_face = cv2.equalizeHist(resized_face)
            
            # Flatten to 10,000-dimensional vector
            flat_vector = normalized_face.flatten().astype(np.float32)
            
            # Normalize vector norm for cosine similarity calculations later
            norm = np.linalg.norm(flat_vector)
            if norm > 0:
                flat_vector = flat_vector / norm

            known_templates.append(flat_vector)
            known_names.append(name)
            known_rolls.append(roll)
            total_images_processed += 1

    if total_images_processed == 0:
        print("[ERROR] No face templates could be extracted.")
        return False

    # Save templates
    data = {"templates": known_templates, "names": known_names, "rolls": known_rolls}
    with open(ENCODINGS_FILE_FALLBACK, "wb") as f:
        pickle.dump(data, f)

    print(f"[SUCCESS] Trained fallback model. Processed {total_images_processed} images.")
    print(f"Templates saved to: {ENCODINGS_FILE_FALLBACK}")
    return True


def run_training():
    """
    Main training coordinator. Chooses dlib or fallback depending on system environment.
    """
    os.makedirs(ENCODINGS_DIR, exist_ok=True)
    if HAS_FACE_RECOGNITION:
        return train_dlib_model()
    else:
        return train_fallback_model()


if __name__ == "__main__":
    run_training()
