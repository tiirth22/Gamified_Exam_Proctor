# 🎓 Online Exam Proctor System - Demo Guide

## 🚀 Quick Start Demo

This guide will help you test the complete Online Exam Proctor system with real-time ML monitoring, violation detection, and admin reporting.

### 📋 Prerequisites

1. **Python Dependencies**: Make sure all required packages are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Flask App Running**: Start the main application
   ```bash
   python gamified_app_simple.py
   ```

3. **Camera Access**: Ensure your camera is available for face detection tests

### 🎯 Demo Accounts

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| **Admin** | admin@demo.com | admin123 | View violation reports |
| **Student** | demo@student.com | demo123 | Take quizzes with monitoring |
| **Test User** | test@student.com | test123 | Generate violations for testing |

### 📚 Available Demo Quizzes

1. **Python Basics Quiz** (5 minutes, 5 questions)
   - Medium difficulty
   - Programming concepts
   - Perfect for testing ML monitoring

2. **JavaScript Fundamentals** (3 minutes, 3 questions)
   - Easy difficulty
   - Web development basics
   - Quick violation testing

3. **Machine Learning Concepts** (10 minutes, 3 questions)
   - Hard difficulty
   - Advanced AI/ML topics
   - Extended monitoring test

## 🔥 Real-Time Testing Features

### 🛡️ ML Monitoring Systems

The system automatically activates these monitoring systems when a quiz starts:

#### 👤 **Face Detection**
- **Real-time**: Detects single face, multiple faces, or no face
- **API**: `/api/ml/detect_face`
- **Violations**: "Face not detected", "Multiple faces detected"
- **Evidence**: Video recording of violations

#### 🎤 **Voice Detection**
- **Real-time**: Monitors audio for speaking/voice activity
- **API**: `/api/ml/detect_voice_activity`
- **Violations**: "Voice activity detected"
- **Evidence**: Audio recordings saved

#### 🖥️ **Screen Activity Detection**
- **Real-time**: Monitors active windows and applications
- **API**: `/api/ml/detect_screen_activity`
- **Violations**: "Tab switching detected", "Suspicious app detected"
- **Evidence**: Screenshots captured

#### 👁️ **Head Movement Detection**
- **Real-time**: Tracks eye movement and head orientation
- **API**: `/api/ml/detect_head_movement`
- **Violations**: "Looking away from screen", "Excessive head movement"
- **Evidence**: Movement pattern analysis

#### 📱 **Object Detection**
- **Real-time**: Detects electronic devices using YOLOv8
- **API**: `/api/ml/detect_objects`
- **Violations**: "Electronic device detected"
- **Evidence**: Object detection images

### 🚨 Real-Time Violation Alerts

When violations are detected, students receive:

1. **Immediate Visual Alerts**
   - Animated notification popups
   - Color-coded severity levels (High/Medium/Low)
   - Real-time timestamp
   - Auto-dismiss after 5 seconds

2. **Anti-Cheat Score Updates**
   - Score decreases with each violation
   - Color changes: Green → Yellow → Red
   - Auto-submit when score drops below 20%

3. **Critical Alerts**
   - Multiple violations trigger auto-submit
   - 3-second countdown warning
   - Force submission if needed

## 🧪 Testing Scenarios

### Scenario 1: Normal Quiz Taking
1. Login as `demo@student.com`
2. Start "Python Basics Quiz"
3. Answer questions normally
4. Observe live monitoring indicators
5. Complete quiz successfully

### Scenario 2: Violation Testing
1. Login as `test@student.com`
2. Start any quiz
3. **Test Face Detection**:
   - Cover your camera
   - Have someone else in frame
4. **Test Voice Detection**:
   - Speak during the quiz
5. **Test Screen Activity**:
   - Switch to another tab
   - Open developer tools (F12)
6. **Test Right-Click**:
   - Right-click on the page
7. **Test Tab Switching**:
   - Alt+Tab to another application

### Scenario 3: Admin Review
1. Login as `admin@demo.com`
2. Go to Admin Dashboard
3. View violation reports
4. Check evidence and timestamps
5. Review detailed violation logs

## 🎮 Interactive Demo Commands

### Run Automated Demo Test
```bash
python test_demo_system.py
```

This script will:
- ✅ Test student login
- ✅ Start a quiz
- ✅ Test all ML detection APIs
- ✅ Simulate violations
- ✅ Test admin dashboard
- ✅ Generate comprehensive report

### Manual Testing Steps

1. **Start the System**
   ```bash
   python gamified_app_simple.py
   ```

2. **Open Browser**
   - Navigate to `http://localhost:5000`
   - Login with demo credentials

3. **Start a Quiz**
   - Select any quiz from dashboard
   - Observe monitoring systems activate
   - Watch live indicators

4. **Generate Violations**
   - Try the violation scenarios above
   - Watch real-time alerts appear
   - Check anti-cheat score changes

5. **Admin Review**
   - Login as admin
   - Check violation reports
   - Review evidence and details

## 📊 Monitoring Dashboard

### Student View
- **Live Monitoring Status**: Real-time indicators for all systems
- **Anti-Cheat Score**: Current trust score with color coding
- **Violation Alerts**: Immediate notifications for violations
- **Timer**: Quiz countdown with urgency indicators

### Admin View
- **Violation Reports**: Complete list of all violations
- **Evidence Review**: Video, audio, and screenshot evidence
- **Student Analytics**: Performance and violation patterns
- **Export Features**: PDF reports and evidence download

## 🔧 System Configuration

### ML Detection Intervals
```javascript
const DETECTION_CONFIG = {
    FACE_CHECK_INTERVAL: 2000,      // 2 seconds
    VOICE_CHECK_INTERVAL: 3000,     // 3 seconds
    SCREEN_CHECK_INTERVAL: 4000,    // 4 seconds
    EYE_CHECK_INTERVAL: 1500,       // 1.5 seconds
    MIN_VIOLATION_GAP: 1000         // 1 second
};
```

### Violation Thresholds
- **Low Severity**: 1 point penalty
- **Medium Severity**: 3 points penalty
- **High Severity**: 5 points penalty
- **Auto-Submit**: When score drops below 20%

## 🎯 Demo Success Criteria

A successful demo should show:

1. ✅ **Seamless Integration**: Quiz starts → ML monitoring activates automatically
2. ✅ **Real-Time Detection**: Violations detected and reported within seconds
3. ✅ **Visual Feedback**: Students see immediate alerts and score changes
4. ✅ **Evidence Capture**: All violations recorded with proof
5. ✅ **Admin Access**: Complete violation reports with evidence available
6. ✅ **Auto-Enforcement**: Quiz auto-submits when violations exceed limits

## 🚀 Next Steps

After successful demo testing:

1. **Production Deployment**: Deploy to production environment
2. **User Training**: Train instructors on admin dashboard
3. **Student Orientation**: Brief students on monitoring systems
4. **Monitoring Setup**: Configure alerts and notifications
5. **Performance Tuning**: Optimize detection intervals and thresholds

## 📞 Support

If you encounter any issues during the demo:

1. Check Flask app is running on port 5000
2. Verify camera permissions are granted
3. Ensure all dependencies are installed
4. Check browser console for JavaScript errors
5. Review server logs for backend issues

---

**🎉 Enjoy testing your Online Exam Proctor System!**

The system provides comprehensive real-time monitoring with immediate violation detection, evidence capture, and automated enforcement - all working seamlessly together to ensure exam integrity.

