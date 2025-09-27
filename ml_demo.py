#!/usr/bin/env python3
"""
ML Demo Script for Online Exam Proctor
Shows all computer vision and ML capabilities
"""

import cv2
import numpy as np
import mediapipe as mp
import time
import threading
from ultralytics import YOLO
import os
import sys

# Import our enhanced utils
from utils import (
    FaceRecognition, MTOP_Detection, electronicDevicesDetection, 
    screenDetection, voice_detection, face_locations, face_encodings,
    load_image_file, compare_faces, face_distance
)

class MLProctorDemo:
    def __init__(self):
        print("🚀 Initializing ML Proctor Demo...")
        
        # Initialize components
        self.face_recognizer = FaceRecognition()
        self.model = YOLO("yolov8n.pt", "v8")
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.75)
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Demo state
        self.running = False
        self.current_mode = "face_detection"
        self.detected_violations = []
        
        print("✅ ML Demo initialized successfully!")

    def test_face_detection(self, frame):
        """Test face detection with MediaPipe"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        face_count = 0
        if results.detections:
            face_count = len(results.detections)
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                ih, iw = frame.shape[:2]
                x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), int(bbox.width * iw), int(bbox.height * ih)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Face {face_count}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Faces Detected: {face_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame, face_count

    def test_head_movement(self, frame):
        """Test head movement detection"""
        rgb_frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.face_mesh.process(rgb_frame)
        rgb_frame.flags.writeable = True
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        head_position = "Forward"
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                face_3d = []
                face_2d = []
                
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in [33, 263, 1, 61, 291, 199]:
                        x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                        face_2d.append([x, y])
                        face_3d.append([x, y, lm.z])
                
                if len(face_2d) > 0 and len(face_3d) > 0:
                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)
                    
                    focal_length = 1 * frame.shape[1]
                    cam_matrix = np.array([[focal_length, 0, frame.shape[0] / 2],
                                         [0, focal_length, frame.shape[1] / 2],
                                         [0, 0, 1]])
                    dist_matrix = np.zeros((4, 1), dtype=np.float64)
                    
                    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
                    rmat, jac = cv2.Rodrigues(rot_vec)
                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
                    
                    x = angles[0] * 360
                    y = angles[1] * 360
                    
                    if y < -10:
                        head_position = "Looking Left"
                    elif y > 15:
                        head_position = "Looking Right"
                    elif x < -8:
                        head_position = "Looking Down"
                    elif x > 15:
                        head_position = "Looking Up"
                    
                    cv2.putText(frame, head_position, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        return frame, head_position

    def test_object_detection(self, frame):
        """Test YOLO object detection for electronic devices"""
        results = self.model.predict(frame, conf=0.5)
        
        electronic_devices = ['cell phone', 'laptop', 'tv', 'mouse', 'keyboard', 'remote', 'book']
        detected_devices = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = box.conf[0]
                
                if class_name.lower() in electronic_devices and confidence > 0.5:
                    detected_devices.append(class_name)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"{class_name} {confidence:.2f}", (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        device_text = f"Devices: {', '.join(detected_devices) if detected_devices else 'None'}"
        cv2.putText(frame, device_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame, detected_devices

    def test_screen_detection(self, frame):
        """Test screen/window detection"""
        try:
            import pygetwindow as gw
            active_window = gw.getActiveWindow()
            
            if active_window:
                window_title = active_window.title
                cv2.putText(frame, f"Active: {window_title[:30]}...", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
                # Simulate exam window detection
                exam_keywords = ["exam", "test", "quiz", "assessment"]
                is_exam_window = any(keyword in window_title.lower() for keyword in exam_keywords)
                
                status = "Exam Window" if is_exam_window else "Other Window"
                color = (0, 255, 0) if is_exam_window else (0, 255, 255)
                cv2.putText(frame, f"Window Status: {status}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                return frame, status
            else:
                cv2.putText(frame, "No Active Window", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                return frame, "No Window"
                
        except ImportError:
            cv2.putText(frame, "pygetwindow not available", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame, "Not Available"

    def run_demo(self):
        """Run the main demo loop"""
        print("🎮 Starting ML Demo...")
        print("Controls:")
        print("  1 - Face Detection Demo")
        print("  2 - Head Movement Demo") 
        print("  3 - Object Detection Demo")
        print("  4 - Screen Detection Demo")
        print("  5 - All Features Demo")
        print("  Q - Quit Demo")
        
        self.running = True
        demo_mode = "all"
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                break
            
            # Make a copy for different processing
            display_frame = frame.copy()
            
            # Run selected demo mode
            if demo_mode == "face_detection" or demo_mode == "all":
                display_frame, face_count = self.test_face_detection(display_frame)
            
            if demo_mode == "head_movement" or demo_mode == "all":
                display_frame, head_pos = self.test_head_movement(display_frame)
            
            if demo_mode == "object_detection" or demo_mode == "all":
                display_frame, devices = self.test_object_detection(display_frame)
            
            if demo_mode == "screen_detection" or demo_mode == "all":
                display_frame, window_status = self.test_screen_detection(display_frame)
            
            # Add demo info overlay
            cv2.putText(display_frame, f"ML Proctor Demo - Mode: {demo_mode}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow("ML Proctor Demo", display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                self.running = False
            elif key == ord('1'):
                demo_mode = "face_detection"
            elif key == ord('2'):
                demo_mode = "head_movement"
            elif key == ord('3'):
                demo_mode = "object_detection"
            elif key == ord('4'):
                demo_mode = "screen_detection"
            elif key == ord('5'):
                demo_mode = "all"
        
        self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✅ Demo completed!")

def test_face_recognition_fallback():
    """Test the face recognition fallback system"""
    print("🧪 Testing Face Recognition Fallback...")
    
    # Test with a simple image
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    
    if ret:
        # Test face locations with MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_locations(rgb_frame)
        print(f"✓ Face locations detected: {len(locations)}")
        
        # Test face encodings
        if locations:
            encodings = face_encodings(rgb_frame, locations)
            print(f"✓ Face encodings generated: {len(encodings)}")
            
            # Test comparison
            if encodings:
                matches = compare_faces(encodings, encodings[0])
                print(f"✓ Face comparison working: {matches[0]}")
        
        print("✅ Face recognition fallback system working!")
    
    cap.release()

def main():
    """Main function"""
    print("🎯 Online Exam Proctor - ML Demo")
    print("=" * 50)
    
    # Test face recognition fallback first
    test_face_recognition_fallback()
    
    # Run the main demo
    demo = MLProctorDemo()
    
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
        demo.cleanup()
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        demo.cleanup()

if __name__ == "__main__":
    main()