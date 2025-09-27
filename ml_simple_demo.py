#!/usr/bin/env python3
"""
Simple ML Demo for Online Exam Proctor
Shows computer vision capabilities step by step
"""

import cv2
import numpy as np
import mediapipe as mp
import time
import os
import sys

# Test imports
print("🔍 Testing ML imports...")
try:
    import cv2
    print("✅ OpenCV imported successfully")
except ImportError as e:
    print(f"❌ OpenCV import failed: {e}")

try:
    import numpy as np
    print("✅ NumPy imported successfully")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")

try:
    import mediapipe as mp
    print("✅ MediaPipe imported successfully")
except ImportError as e:
    print(f"❌ MediaPipe import failed: {e}")

try:
    from ultralytics import YOLO
    print("✅ YOLO imported successfully")
except ImportError as e:
    print(f"❌ YOLO import failed: {e}")

try:
    import utils
    print("✅ Utils module imported successfully")
    print("   - Face recognition fallback: MediaPipe")
    print("   - Object detection: YOLO")
    print("   - Voice detection: Available")
    print("   - Screen detection: Available")
except ImportError as e:
    print(f"❌ Utils import failed: {e}")

print("\n🚀 Starting ML Demo...")

class SimpleMLDemo:
    def __init__(self):
        print("📹 Initializing camera...")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Could not open camera")
            sys.exit(1)
        
        # Initialize MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.75)
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize YOLO
        try:
            self.model = YOLO("yolov8n.pt")
            print("✅ YOLO model loaded")
        except Exception as e:
            print(f"⚠️ YOLO model not available: {e}")
            self.model = None
        
        self.frame_count = 0
        self.start_time = time.time()
        
    def detect_faces(self, frame):
        """Face detection with MediaPipe"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        face_count = 0
        if results.detections:
            face_count = len(results.detections)
            for detection in results.detections:
                # Draw bounding box
                bbox = detection.location_data.relative_bounding_box
                ih, iw = frame.shape[:2]
                x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), int(bbox.width * iw), int(bbox.height * ih)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Face {face_count}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, face_count

    def detect_objects(self, frame):
        """Object detection with YOLO"""
        if self.model is None:
            cv2.putText(frame, "YOLO not available", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame, []
        
        try:
            results = self.model.predict(frame, conf=0.5, verbose=False)
            
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
            
            return frame, detected_devices
            
        except Exception as e:
            cv2.putText(frame, f"YOLO Error: {str(e)[:30]}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            return frame, []

    def run_demo(self):
        """Run the main demo loop"""
        print("\n🎮 Demo Controls:")
        print("  F - Face Detection Mode")
        print("  O - Object Detection Mode")
        print("  A - All Features Mode")
        print("  Q - Quit")
        print("\n📹 Starting camera feed...")
        
        mode = "all"
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                break
            
            # Process frame based on mode
            if mode == "face" or mode == "all":
                frame, face_count = self.detect_faces(frame)
                cv2.putText(frame, f"Faces: {face_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if mode == "object" or mode == "all":
                frame, devices = self.detect_objects(frame)
                device_text = f"Devices: {len(devices)}"
                cv2.putText(frame, device_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Add mode info
            cv2.putText(frame, f"Mode: {mode}", (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Calculate FPS
            self.frame_count += 1
            if self.frame_count % 30 == 0:
                fps = 30 / (time.time() - self.start_time)
                self.start_time = time.time()
                print(f"📊 FPS: {fps:.1f}")
            
            # Show frame
            cv2.imshow("ML Proctor Demo", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('f') or key == ord('F'):
                mode = "face"
                print(f"🔧 Mode: Face Detection")
            elif key == ord('o') or key == ord('O'):
                mode = "object"
                print(f"🔧 Mode: Object Detection")
            elif key == ord('a') or key == ord('A'):
                mode = "all"
                print(f"🔧 Mode: All Features")
        
        self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        self.cap.release()
        cv2.destroyAllWindows()
        print("✅ Demo completed!")

if __name__ == "__main__":
    demo = SimpleMLDemo()
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted")
        demo.cleanup()
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        demo.cleanup()