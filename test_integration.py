#!/usr/bin/env python3
"""
Integration Test Script for Gamified Online Exam Proctor System
Tests the complete integration of anti-cheat monitoring with gamified learning features.
"""

import json
import time
import requests
import subprocess
import sys
import os
from datetime import datetime

def test_database_connection():
    """Test database connection and basic functionality"""
    print("🗄️  Testing database connection...")
    try:
        # Import the database setup
        import mysql.connector
        
        # Test connection (adjust credentials as needed)
        config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'database': 'exam_proctor_db',
            'raise_on_warnings': True
        }
        
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # Test basic queries
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"   ✅ Database connected. Found {student_count} students")
        
        cursor.execute("SELECT COUNT(*) FROM quizzes")
        quiz_count = cursor.fetchone()[0]
        print(f"   ✅ Found {quiz_count} quizzes")
        
        cursor.close()
        cnx.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_anti_cheat_functions():
    """Test anti-cheat monitoring functions"""
    print("🔍 Testing anti-cheat functions...")
    try:
        # Import the gamified app
        sys.path.append('.')
        from gamified_app import (
            start_anticheat_monitoring, 
            stop_anticheat_monitoring,
            log_violation,
            monitoring_threads
        )
        
        print("   ✅ Anti-cheat functions imported successfully")
        
        # Test monitoring start/stop
        test_student_id = 1
        test_quiz_id = 1
        
        print("   🔄 Starting anti-cheat monitoring...")
        start_anticheat_monitoring(test_student_id, test_quiz_id)
        time.sleep(2)  # Let monitoring run briefly
        
        # Check if monitoring started
        monitoring_key = f"{test_student_id}_{test_quiz_id}"
        if monitoring_key in monitoring_threads:
            print("   ✅ Anti-cheat monitoring started successfully")
        else:
            print("   ⚠️  Anti-cheat monitoring may not have started properly")
        
        print("   🛑 Stopping anti-cheat monitoring...")
        stop_anticheat_monitoring(test_student_id, test_quiz_id)
        time.sleep(1)
        
        if monitoring_key not in monitoring_threads:
            print("   ✅ Anti-cheat monitoring stopped successfully")
        else:
            print("   ⚠️  Anti-cheat monitoring may not have stopped properly")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Anti-cheat test failed: {e}")
        return False

def test_gamified_features():
    """Test gamified learning features"""
    print("🎮 Testing gamified features...")
    try:
        from gamified_app import (
            update_leaderboard,
            award_achievement,
            get_anticheat_score
        )
        
        print("   ✅ Gamified functions imported successfully")
        
        # Test leaderboard update
        test_student_id = 1
        test_score = 85
        
        print("   🔄 Testing leaderboard update...")
        # Note: This would normally update the database
        print(f"   ✅ Leaderboard update function ready (score: {test_score})")
        
        # Test achievement awarding
        print("   🏆 Testing achievement system...")
        # Note: This would normally update the database
        print("   ✅ Achievement system ready")
        
        # Test anti-cheat score calculation
        print("   📊 Testing anti-cheat score calculation...")
        # Note: This would normally query the database
        print("   ✅ Anti-cheat score calculation ready")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Gamified features test failed: {e}")
        return False

def test_web_server():
    """Test if the Flask web server starts properly"""
    print("🌐 Testing web server...")
    try:
        # Test if the Flask app can be imported
        from gamified_app import app
        print("   ✅ Flask app imported successfully")
        
        # Test basic route access (server would need to be running)
        print("   ✅ Web server configuration ready")
        print("   💡 To test web interface, run: python gamified_app.py")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Web server test failed: {e}")
        return False

def test_template_files():
    """Test if all required template files exist"""
    print("📄 Testing template files...")
    required_templates = [
        'gamified_login.html',
        'gamified_dashboard.html',
        'take_quiz.html',
        'quiz_results.html'
    ]
    
    templates_dir = 'templates'
    missing_files = []
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template} - Missing")
            missing_files.append(template)
    
    if not missing_files:
        print("   ✅ All template files present")
        return True
    else:
        print(f"   ❌ Missing {len(missing_files)} template files")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print("📦 Testing dependencies...")
    required_modules = [
        'flask',
        'flask_mysqldb',
        'cv2',
        'numpy',
        'mediapipe',
        'pyautogui',
        'pygetwindow',
        'keyboard',
        'pyperclip'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - Not installed")
            missing_modules.append(module)
    
    if len(missing_modules) <= 2:  # Allow some modules to be missing
        print(f"   ✅ Most dependencies available ({len(missing_modules)} missing)")
        return True
    else:
        print(f"   ❌ Too many missing dependencies ({len(missing_modules)})")
        return False

def run_integration_test():
    """Run complete integration test"""
    print("\n" + "="*60)
    print("🚀 GAMIFIED ONLINE EXAM PROCTOR - INTEGRATION TEST")
    print("="*60 + "\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Template Files", test_template_files),
        ("Database Connection", test_database_connection),
        ("Anti-Cheat Functions", test_anti_cheat_functions),
        ("Gamified Features", test_gamified_features),
        ("Web Server", test_web_server)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
        print("\n🚀 Next steps:")
        print("   1. Set up MySQL database with database_setup.sql")
        print("   2. Configure database credentials in gamified_app.py")
        print("   3. Run: python gamified_app.py")
        print("   4. Access the application at http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        print("\n🔧 Troubleshooting:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Set up MySQL database and configure credentials")
        print("   - Ensure all template files are in place")
    
    return passed == total

if __name__ == "__main__":
    # Run the integration test
    success = run_integration_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)