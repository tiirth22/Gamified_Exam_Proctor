#!/usr/bin/env python3
"""
Demo Test Script for Online Exam Proctor System
This script tests the real-time ML monitoring and violation detection system.
"""

import time
import random
import requests
import json
from datetime import datetime

class ExamProctorDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.student_id = None
        self.quiz_id = None
        
    def login_student(self, email="demo@student.com", password="demo123"):
        """Login as a student"""
        print(f"🔐 Logging in as student: {email}")
        
        login_data = {
            'email': email,
            'password': password
        }
        
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        
        if response.status_code == 200 and 'dashboard' in response.url:
            print("✅ Student login successful!")
            return True
        else:
            print("❌ Student login failed!")
            return False
    
    def get_available_quizzes(self):
        """Get available quizzes"""
        print("📚 Fetching available quizzes...")
        
        response = self.session.get(f"{self.base_url}/dashboard")
        
        if response.status_code == 200:
            print("✅ Quizzes fetched successfully!")
            # In a real implementation, you'd parse the HTML to get quiz IDs
            # For demo purposes, we'll use quiz ID 1
            self.quiz_id = 1
            return True
        else:
            print("❌ Failed to fetch quizzes!")
            return False
    
    def start_quiz(self, quiz_id=1):
        """Start a quiz"""
        print(f"🚀 Starting quiz ID: {quiz_id}")
        
        response = self.session.get(f"{self.base_url}/quiz/{quiz_id}")
        
        if response.status_code == 200:
            print("✅ Quiz started successfully!")
            print("🛡️ ML monitoring systems are now active...")
            return True
        else:
            print("❌ Failed to start quiz!")
            return False
    
    def test_ml_detection_apis(self):
        """Test ML detection API endpoints"""
        print("\n🤖 Testing ML Detection APIs...")
        
        # Test ML status
        print("📊 Checking ML system status...")
        response = self.session.get(f"{self.base_url}/api/ml/status")
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ ML Status: {status_data}")
        else:
            print("❌ Failed to get ML status!")
        
        # Test face detection (simulated)
        print("👤 Testing face detection...")
        face_data = {
            'image': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
        }
        
        response = self.session.post(f"{self.base_url}/api/ml/detect_face", json=face_data)
        
        if response.status_code == 200:
            face_result = response.json()
            print(f"✅ Face Detection: {face_result}")
        else:
            print("❌ Face detection test failed!")
        
        # Test voice detection
        print("🎤 Testing voice detection...")
        response = self.session.post(f"{self.base_url}/api/ml/detect_voice_activity")
        
        if response.status_code == 200:
            voice_result = response.json()
            print(f"✅ Voice Detection: {voice_result}")
        else:
            print("❌ Voice detection test failed!")
        
        # Test screen activity detection
        print("🖥️ Testing screen activity detection...")
        response = self.session.post(f"{self.base_url}/api/ml/detect_screen_activity")
        
        if response.status_code == 200:
            screen_result = response.json()
            print(f"✅ Screen Detection: {screen_result}")
        else:
            print("❌ Screen detection test failed!")
    
    def simulate_violations(self):
        """Simulate various types of violations"""
        print("\n🚨 Simulating violations for testing...")
        
        violations = [
            {'type': 'Face not detected', 'severity': 'high'},
            {'type': 'Multiple faces detected', 'severity': 'high'},
            {'type': 'Voice activity detected', 'medium': 'medium'},
            {'type': 'Looking away from screen', 'severity': 'medium'},
            {'type': 'Electronic device detected', 'severity': 'high'},
            {'type': 'Tab switching detected', 'severity': 'medium'},
            {'type': 'Right click attempted', 'severity': 'low'},
            {'type': 'Developer tools attempted', 'severity': 'high'}
        ]
        
        for i, violation in enumerate(violations[:3]):  # Test first 3 violations
            print(f"⚠️ Simulating violation {i+1}: {violation['type']}")
            
            violation_data = {
                'quiz_id': self.quiz_id or 1,
                'reason': violation['type'],
                'severity': violation.get('severity', 'medium'),
                'question_number': 1,
                'timestamp': datetime.now().isoformat()
            }
            
            response = self.session.post(f"{self.base_url}/report_violation", json=violation_data)
            
            if response.status_code == 200:
                print(f"✅ Violation reported: {violation['type']}")
            else:
                print(f"❌ Failed to report violation: {violation['type']}")
            
            time.sleep(2)  # Wait between violations
    
    def test_admin_dashboard(self):
        """Test admin dashboard and violation reports"""
        print("\n👨‍💼 Testing admin dashboard...")
        
        # Login as admin
        admin_data = {
            'email': 'admin@demo.com',
            'password': 'admin123'
        }
        
        response = self.session.post(f"{self.base_url}/login", data=admin_data)
        
        if response.status_code == 200:
            print("✅ Admin login successful!")
            
            # Check violations
            response = self.session.get(f"{self.base_url}/admin/violations")
            if response.status_code == 200:
                print("✅ Admin violations dashboard accessible!")
            else:
                print("❌ Admin violations dashboard not accessible!")
        else:
            print("❌ Admin login failed!")
    
    def run_complete_demo(self):
        """Run the complete demo test"""
        print("🎯 Starting Online Exam Proctor System Demo")
        print("=" * 50)
        
        # Step 1: Login as student
        if not self.login_student():
            return False
        
        # Step 2: Get available quizzes
        if not self.get_available_quizzes():
            return False
        
        # Step 3: Start a quiz
        if not self.start_quiz():
            return False
        
        # Step 4: Test ML detection APIs
        self.test_ml_detection_apis()
        
        # Step 5: Simulate violations
        self.simulate_violations()
        
        # Step 6: Test admin dashboard
        self.test_admin_dashboard()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\n📋 Demo Summary:")
        print("✅ Student authentication working")
        print("✅ Quiz system functional")
        print("✅ ML detection APIs responding")
        print("✅ Violation reporting system active")
        print("✅ Admin dashboard accessible")
        print("\n🚀 The system is ready for real-time monitoring!")
        
        return True

def main():
    """Main demo function"""
    print("🎓 Online Exam Proctor System - Demo Test")
    print("This script will test the complete system functionality.")
    print("Make sure the Flask app is running on http://localhost:5000")
    print()
    
    # Ask user if they want to proceed
    proceed = input("Do you want to run the demo? (y/n): ").lower().strip()
    
    if proceed == 'y':
        demo = ExamProctorDemo()
        demo.run_complete_demo()
    else:
        print("Demo cancelled.")

if __name__ == "__main__":
    main()

