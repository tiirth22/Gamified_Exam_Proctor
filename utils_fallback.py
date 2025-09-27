# Fallback utilities for when heavy dependencies are not available
import json
import time
import random

def faceDetectionRecording(img=None, text="Verified Student appeared"):
    """Fallback face detection - just logs activity"""
    print(f"[FALLBACK] Face Detection: {text}")
    return text

def Head_record_duration(text="Forward", img=None):
    """Fallback head movement detection"""
    print(f"[FALLBACK] Head Movement: {text}")
    return text

def voice_detection():
    """Fallback voice detection - returns no violations"""
    print("[FALLBACK] Voice Detection: Monitoring...")
    return False

def screen_recorder():
    """Fallback screen recorder - returns empty data"""
    print("[FALLBACK] Screen Recording: Monitoring...")
    return []

def get_resultId():
    """Generate a random result ID"""
    return random.randint(1000, 9999)

# Mock violation logging
def log_violation(violation_type, severity="low", details=""):
    """Log violations to a simple file"""
    violation_data = {
        "type": violation_type,
        "severity": severity,
        "details": details,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "id": get_resultId()
    }
    
    try:
        with open('violation.json', 'r+') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
            data.append(violation_data)
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
    except FileNotFoundError:
        with open('violation.json', 'w') as file:
            json.dump([violation_data], file, indent=4)
    
    print(f"[FALLBACK] Violation logged: {violation_type} - {severity}")
    return violation_data