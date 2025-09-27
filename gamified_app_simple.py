from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import glob
import random
from datetime import datetime, timedelta
import threading
import time
import base64

# Try to import heavy dependencies, fallback to mock functions if not available
try:
    import cv2
    import numpy as np
    from utils import (
        faceDetectionRecording, Head_record_duration, voice_detection, screen_recorder,
        face_locations, face_encodings, electronicDevicesDetection, screenDetection
    )
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Heavy dependencies not available. Using fallback functions. Error: {e}")
    from utils_fallback import faceDetectionRecording, Head_record_duration, voice_detection, screen_recorder
    ML_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'gamified-learning-secret-key-2024'

# Context processor to make utility functions available in all templates
@app.context_processor
def utility_processor():
    def get_violation_count():
        return AntiCheatLog.query.count()
    
    return dict(
        get_violation_count=get_violation_count,
        datetime=datetime
    )

# Database configuration - using SQLite for simplicity
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamified_exam_proctor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Anti-cheat monitoring variables
anticheat_monitoring = {}
monitoring_threads = {}
violation_counts = {}

# Database Models
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    rank_position = db.Column(db.Integer, default=0)
    trust_score = db.Column(db.Float, default=100.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Admin flag for privileged access
    is_admin = db.Column(db.Boolean, default=False)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default='medium')
    time_limit = db.Column(db.Integer, default=30)
    points = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    points = db.Column(db.Integer, default=10)

class StudentQuizAttempt(db.Model):
    __tablename__ = 'student_quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer, default=0)
    anticheat_score = db.Column(db.Integer, default=100)
    anticheat_warnings = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AntiCheatLog(db.Model):
    __tablename__ = 'anti_cheat_logs'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    violation_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), default='low')
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='trophy')
    points = db.Column(db.Integer, default=10)
    badge_type = db.Column(db.String(20), default='bronze')

class StudentAchievement(db.Model):
    __tablename__ = 'student_achievements'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

# Anti-cheat helper functions
def start_anticheat_monitoring(student_id, quiz_id):
    """Start anti-cheat monitoring for a quiz session"""
    session_key = f"{student_id}_{quiz_id}"
    
    if session_key not in anticheat_monitoring:
        anticheat_monitoring[session_key] = {
            'monitoring': True,
            'start_time': time.time(),
            'violations': [],
            'score': 100
        }
        
        # Start monitoring threads
        monitoring_threads[session_key] = {
            'face': threading.Thread(target=monitor_face_detection, args=(student_id, quiz_id)),
            'screen': threading.Thread(target=monitor_screen_activity, args=(student_id, quiz_id)),
            'voice': threading.Thread(target=monitor_voice_activity, args=(student_id, quiz_id))
        }
        
        for thread in monitoring_threads[session_key].values():
            thread.daemon = True
            thread.start()

def monitor_face_detection(student_id, quiz_id):
    """Monitor face detection"""
    session_key = f"{student_id}_{quiz_id}"
    
    while anticheat_monitoring.get(session_key, {}).get('monitoring', False):
        # Simulate face detection monitoring
        if random.random() < 0.01:  # 1% chance of violation
            log_violation(student_id, quiz_id, "No face detected", "medium")
        time.sleep(1)

def monitor_screen_activity(student_id, quiz_id):
    """Monitor screen activity"""
    session_key = f"{student_id}_{quiz_id}"
    
    while anticheat_monitoring.get(session_key, {}).get('monitoring', False):
        # Simulate screen activity monitoring
        if random.random() < 0.005:  # 0.5% chance of violation
            log_violation(student_id, quiz_id, "Suspicious screen activity", "high")
        time.sleep(2)

def monitor_voice_activity(student_id, quiz_id):
    """Monitor voice activity"""
    session_key = f"{student_id}_{quiz_id}"
    
    while anticheat_monitoring.get(session_key, {}).get('monitoring', False):
        # Simulate voice detection monitoring
        if random.random() < 0.008:  # 0.8% chance of violation
            log_violation(student_id, quiz_id, "Voice/sound detected", "medium")
        time.sleep(3)

def log_violation(student_id, quiz_id, violation_type, severity="low", details=""):
    """Log a violation to the database"""
    try:
        violation = AntiCheatLog(
            student_id=student_id,
            quiz_id=quiz_id,
            violation_type=violation_type,
            severity=severity,
            details=details
        )
        db.session.add(violation)
        db.session.commit()
        
        # Update session monitoring
        session_key = f"{student_id}_{quiz_id}"
        if session_key in anticheat_monitoring:
            anticheat_monitoring[session_key]['violations'].append({
                'type': violation_type,
                'severity': severity,
                'timestamp': datetime.utcnow()
            })
            
            # Reduce anti-cheat score
            penalty = 5 if severity == "high" else (3 if severity == "medium" else 1)
            anticheat_monitoring[session_key]['score'] = max(0, 
                anticheat_monitoring[session_key]['score'] - penalty)
        
        print(f"Violation logged: {violation_type} - {severity}")
        
    except Exception as e:
        print(f"Error logging violation: {e}")

def stop_anticheat_monitoring(student_id, quiz_id):
    """Stop anti-cheat monitoring for a quiz session"""
    session_key = f"{student_id}_{quiz_id}"
    
    if session_key in anticheat_monitoring:
        anticheat_monitoring[session_key]['monitoring'] = False
        
        # Wait for threads to finish
        if session_key in monitoring_threads:
            for thread in monitoring_threads[session_key].values():
                thread.join(timeout=2)
            
            del monitoring_threads[session_key]
        
        return anticheat_monitoring[session_key]['score']
    
    return 100

def award_achievement(student_id, achievement_name):
    """Award an achievement to a student"""
    try:
        achievement = Achievement.query.filter_by(name=achievement_name).first()
        if not achievement:
            # Create achievement if it doesn't exist
            achievement = Achievement(
                name=achievement_name,
                description=f"Earned {achievement_name} achievement",
                points=50
            )
            db.session.add(achievement)
            db.session.commit()
        
        # Check if student already has this achievement
        existing = StudentAchievement.query.filter_by(
            student_id=student_id, 
            achievement_id=achievement.id
        ).first()
        
        if not existing:
            student_achievement = StudentAchievement(
                student_id=student_id,
                achievement_id=achievement.id
            )
            db.session.add(student_achievement)
            
            # Update student points
            student = Student.query.get(student_id)
            student.total_points += achievement.points
            
            db.session.commit()
            print(f"Achievement awarded: {achievement_name}")
            
    except Exception as e:
        print(f"Error awarding achievement: {e}")

def update_leaderboard(student_id):
    """Update student leaderboard position"""
    try:
        # Calculate total points and average score
        attempts = StudentQuizAttempt.query.filter_by(student_id=student_id).all()
        total_points = sum(attempt.score for attempt in attempts)
        exams_completed = len(attempts)
        average_score = total_points / exams_completed if exams_completed > 0 else 0
        
        # Update student record
        student = Student.query.get(student_id)
        student.total_points = total_points
        
        # Calculate rank based on total points
        all_students = Student.query.order_by(Student.total_points.desc()).all()
        for rank, s in enumerate(all_students, 1):
            if s.id == student_id:
                student.rank_position = rank
                break
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error updating leaderboard: {e}")

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/create_demo_quiz')
def create_demo_quiz():
    """Create a demo quiz for testing ML detection alerts"""
    try:
        # Check if demo quiz already exists
        demo_quiz = Quiz.query.filter_by(title='🚨 ML Detection Demo Quiz').first()
        if demo_quiz:
            return jsonify({'message': 'Demo quiz already exists', 'quiz_id': demo_quiz.id})
        
        # Create demo quiz
        quiz = Quiz(
            title='🚨 ML Detection Demo Quiz',
            description='Test quiz designed to trigger ML detection alerts for demo purposes',
            category='Demo',
            difficulty='easy',
            time_limit=10,  # 10 minutes
            points=50
        )
        db.session.add(quiz)
        db.session.flush()  # Get the quiz ID
        
        # Create demo questions designed to trigger alerts
        demo_questions = [
            {
                'question_text': 'During this quiz, try looking away from the screen or moving your head excessively to test eye detection alerts.',
                'option_a': 'I will look away to test the system',
                'option_b': 'I will keep looking at the screen',
                'option_c': 'I will move my head around',
                'option_d': 'I will test the detection system',
                'correct_answer': 'B',
                'points': 10
            },
            {
                'question_text': 'Try speaking or making sounds during this quiz to test voice detection alerts.',
                'option_a': 'I will speak to test voice detection',
                'option_b': 'I will stay quiet',
                'option_c': 'I will make some noise',
                'option_d': 'I will test the audio system',
                'correct_answer': 'B',
                'points': 10
            },
            {
                'question_text': 'You can test screen monitoring by switching tabs or opening other applications (this will trigger alerts).',
                'option_a': 'I will switch tabs to test',
                'option_b': 'I will stay on this tab',
                'option_c': 'I will open another app',
                'option_d': 'I will test tab switching',
                'correct_answer': 'B',
                'points': 10
            },
            {
                'question_text': 'Face detection can be tested by covering your camera or moving away from it.',
                'option_a': 'I will cover the camera',
                'option_b': 'I will stay visible',
                'option_c': 'I will move away',
                'option_d': 'I will test face detection',
                'correct_answer': 'B',
                'points': 10
            },
            {
                'question_text': 'This is the final question. The system should have recorded various violations during this demo quiz.',
                'option_a': 'I triggered several alerts',
                'option_b': 'I followed all rules',
                'option_c': 'I tested the ML system',
                'option_d': 'I completed the demo',
                'correct_answer': 'D',
                'points': 10
            }
        ]
        
        # Add questions to database
        for q_data in demo_questions:
            question = Question(quiz_id=quiz.id, **q_data)
            db.session.add(question)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Demo quiz created successfully!',
            'quiz_id': quiz.id,
            'title': quiz.title,
            'questions': len(demo_questions)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create demo quiz: {str(e)}'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        student = Student.query.filter_by(email=email).first()
        
        if student and check_password_hash(student.password, password):
            session['student_id'] = student.id
            session['student_name'] = student.name
            session['student_email'] = student.email
            is_admin = bool(getattr(student, 'is_admin', False))
            session['is_admin'] = is_admin
            
            # Redirect to admin dashboard if admin, otherwise to student dashboard
            if is_admin:
                return redirect(url_for('admin_dashboard'))
            # If ML utils are available, set the global Student_Name for screenshot foldering
            try:
                import utils as ml_utils
                ml_utils.Student_Name = student.name
            except Exception:
                pass
            return redirect(url_for('dashboard'))
        else:
            return render_template('gamified_login.html', error='Invalid credentials')
    
    return render_template('gamified_login.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.get(session['student_id'])
    
    # Get available quizzes
    available_quizzes = Quiz.query.limit(6).all()
    
    # Get recent attempts
    recent_attempts = StudentQuizAttempt.query.filter_by(
        student_id=session['student_id']
    ).order_by(StudentQuizAttempt.created_at.desc()).limit(5).all()
    
    # Get leaderboard (top 5)
    top_students = Student.query.order_by(Student.total_points.desc()).limit(5).all()
    
    # Get achievements
    achievements = db.session.query(Achievement).join(
        StudentAchievement, Achievement.id == StudentAchievement.achievement_id
    ).filter(StudentAchievement.student_id == session['student_id']).all()
    
    # Calculate anti-cheat score based on recent violations
    recent_violations = AntiCheatLog.query.filter(
        AntiCheatLog.student_id == session['student_id'],
        AntiCheatLog.created_at > datetime.utcnow() - timedelta(hours=24)
    ).all()
    
    anticheat_score = max(0, 100 - (len(recent_violations) * 5))
    
    # Add question counts to quizzes
    quizzes_with_counts = []
    for quiz in available_quizzes:
        question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        quiz.question_count = question_count
        quizzes_with_counts.append(quiz)
    
    return render_template('gamified_dashboard.html',
                         user_name=student.name,
                         total_points=student.total_points,
                         quizzes_taken=len(recent_attempts),
                         achievements_count=len(achievements),
                         recent_quizzes=quizzes_with_counts,
                         recent_attempts=recent_attempts,
                         top_players=top_students,
                         achievements=achievements,
                         anticheat_score=anticheat_score)

@app.route('/quizzes')
def list_quizzes():
    """List all available quizzes"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    # Get all available quizzes
    all_quizzes = Quiz.query.all()
    
    # Add question counts and difficulty badges
    quizzes_with_details = []
    for quiz in all_quizzes:
        question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        quiz.question_count = question_count
        
        # Add difficulty color
        difficulty_colors = {
            'easy': '#28a745',
            'medium': '#ffc107', 
            'hard': '#dc3545'
        }
        quiz.difficulty_color = difficulty_colors.get(quiz.difficulty, '#6c757d')
        
        quizzes_with_details.append(quiz)
    
    return render_template('quiz_list.html', quizzes=quizzes_with_details)

@app.route('/quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Get student's recent violations for anti-cheat warnings
    recent_violations = AntiCheatLog.query.filter(
        AntiCheatLog.student_id == session['student_id'],
        AntiCheatLog.created_at > datetime.utcnow() - timedelta(hours=1)
    ).all()
    
    anticheat_warnings = len(recent_violations)
    
    # Get current question number from request args
    current_question = request.args.get('question', 1, type=int)
    if current_question < 1 or current_question > len(questions):
        current_question = 1
    
    # Calculate anti-cheat score (start with 100, subtract penalties)
    anticheat_score = max(0, 100 - (anticheat_warnings * 5))
    
    # Get current question data
    current_question_data = questions[current_question - 1]
    
    # Parse options from the question data
    options = [
        current_question_data.option_a,
        current_question_data.option_b,
        current_question_data.option_c,
        current_question_data.option_d
    ]
    
    # Calculate progress
    progress_percent = int((current_question / len(questions)) * 100)
    
    # Time management (30 seconds per question)
    time_remaining = 30
    time_remaining_seconds = time_remaining * 60
    
    # Track answered questions (simplified - in real app this would be stored in session/database)
    answered_questions = []
    
    # Start anti-cheat monitoring
    start_anticheat_monitoring(session['student_id'], quiz_id)
    
    return render_template('take_quiz.html',
                         quiz=quiz,
                         questions=questions,
                         current_question=current_question,
                         current_question_data=current_question_data,
                         options=options,
                         total_questions=len(questions),
                         progress_percent=progress_percent,
                         time_remaining=time_remaining,
                         time_remaining_seconds=time_remaining_seconds,
                         answered_questions=answered_questions,
                         anticheat_warnings=anticheat_warnings,
                         anticheat_score=anticheat_score,
                         face_detection_active=True,
                         screen_monitoring_active=True,
                         voice_detection_active=True,
                         movement_detection_active=True)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', {})
    time_taken = data.get('time_taken', 0)
    
    # Stop anti-cheat monitoring and get final score
    anticheat_score = stop_anticheat_monitoring(session['student_id'], quiz_id)
    
    # Calculate score
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    correct_answers = 0
    total_questions = len(questions)
    
    for question in questions:
        if str(question.id) in answers and answers[str(question.id)] == question.correct_answer:
            correct_answers += 1
    
    # Calculate base score
    base_score = int((correct_answers / total_questions) * 100)
    
    # Apply anti-cheat penalty
    penalty = (100 - anticheat_score) // 10  # -1 point for every 10 anti-cheat points lost
    final_score = max(0, base_score - penalty)
    
    # Create quiz attempt record
    attempt = StudentQuizAttempt(
        student_id=session['student_id'],
        quiz_id=quiz_id,
        score=final_score,
        time_taken=time_taken,
        anticheat_score=anticheat_score,
        anticheat_warnings=AntiCheatLog.query.filter(
            AntiCheatLog.student_id == session['student_id'],
            AntiCheatLog.quiz_id == quiz_id,
            AntiCheatLog.created_at > datetime.utcnow() - timedelta(hours=1)
        ).count()
    )
    
    db.session.add(attempt)
    
    # Award achievements
    if final_score >= 90:
        award_achievement(session['student_id'], 'Quiz Master')
    elif final_score >= 80:
        award_achievement(session['student_id'], 'High Achiever')
    
    if anticheat_score >= 95:
        award_achievement(session['student_id'], 'Clean Record')
    
    db.session.commit()
    
    # Update leaderboard
    update_leaderboard(session['student_id'])
    
    return jsonify({
        'success': True,
        'attempt_id': attempt.id,
        'final_score': final_score,
        'base_score': base_score,
        'anticheat_score': anticheat_score,
        'penalty': penalty
    })

@app.route('/report_violation', methods=['POST'])
def report_violation():
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    violation_type = data.get('violation_type', 'Unknown violation')
    severity = data.get('severity', 'low')
    details = data.get('details', '')
    quiz_id = data.get('quiz_id', 0)
    
    log_violation(session['student_id'], quiz_id, violation_type, severity, details)
    
    return jsonify({'success': True})

@app.route('/quiz_results/<int:attempt_id>')
def quiz_results(attempt_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    attempt = StudentQuizAttempt.query.get_or_404(attempt_id)
    
    # Ensure this attempt belongs to the current student
    if attempt.student_id != session['student_id']:
        return redirect(url_for('dashboard'))
    
    quiz = Quiz.query.get(attempt.quiz_id)
    student = Student.query.get(session['student_id'])
    
    # Get violations for this attempt
    violations = AntiCheatLog.query.filter(
        AntiCheatLog.student_id == session['student_id'],
        AntiCheatLog.quiz_id == attempt.quiz_id,
        AntiCheatLog.created_at > attempt.created_at - timedelta(minutes=5),
        AntiCheatLog.created_at < attempt.created_at + timedelta(minutes=30)
    ).all()
    
    # Process violations
    processed_violations = []
    for violation in violations:
        if 'No face detected' in violation.violation_type:
            penalty = 5
            severity = 'error'
        elif 'Suspicious screen activity' in violation.violation_type:
            penalty = 3
            severity = 'warning'
        elif 'Voice/sound detected' in violation.violation_type:
            penalty = 2
            severity = 'warning'
        else:
            penalty = 1
            severity = 'info'
        
        processed_violations.append({
            'violation_type': violation.violation_type,
            'created_at': violation.created_at,
            'penalty': penalty,
            'severity': severity
        })
    
    # Calculate original score (reverse penalty calculation)
    penalty_points = sum(v['penalty'] for v in processed_violations)
    original_score = min(100, attempt.score + penalty_points)
    
    # Get achievements
    achievements = db.session.query(Achievement).join(
        StudentAchievement, Achievement.id == StudentAchievement.achievement_id
    ).filter(
        StudentAchievement.student_id == session['student_id'],
        StudentAchievement.earned_at > attempt.created_at - timedelta(minutes=1)
    ).all()
    
    # Score class for styling
    if attempt.score >= 90:
        score_class = 'excellent'
    elif attempt.score >= 80:
        score_class = 'good'
    elif attempt.score >= 70:
        score_class = 'average'
    else:
        score_class = 'poor'
    
    return render_template('quiz_results.html',
                         quiz=quiz,
                         student=student,
                         final_score=attempt.score,
                         original_score=original_score,
                         score_class=score_class,
                         correct_answers=int((attempt.score / 100) * 10),
                         total_questions=10,
                         time_taken=attempt.time_taken // 60,
                         violations=processed_violations,
                         violation_count=len(violations),
                         penalty_points=penalty_points,
                         achievements=achievements,
                         current_rank=student.rank_position,
                         total_points=student.total_points,
                         rank_improved=True)

@app.route('/leaderboard')
def leaderboard():
    # Get top students
    top_students = Student.query.order_by(Student.total_points.desc()).limit(50).all()
    
    return render_template('leaderboard.html', leaderboard=top_students)

# -----------------------------
# Admin-only routes (gamified)
# -----------------------------

def require_admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    return None

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with violation statistics"""
    guard = require_admin()
    if guard:
        return guard
    
    # Get violation statistics
    total_violations = AntiCheatLog.query.count()
    pending_violations = AntiCheatLog.query.count()
    
    # Get today's violations
    today = datetime.utcnow().date()
    todays_violations = AntiCheatLog.query.filter(
        func.date(AntiCheatLog.created_at) == today
    ).count()
    
    # Get recent violations
    recent_violations = AntiCheatLog.query.order_by(
        AntiCheatLog.created_at.desc()
    ).limit(5).all()
    
    # Get violation types distribution
    violation_types = db.session.query(
        AntiCheatLog.violation_type,
        func.count(AntiCheatLog.id).label('count')
    ).group_by(AntiCheatLog.violation_type).all()
    
    # Prepare stats dictionary
    stats = {
        'students_count': Student.query.count(),
        'quizzes_count': Quiz.query.count(),
        'violations_today': todays_violations,
        'pending_reviews': pending_violations
    }
    
    return render_template('admin_dashboard.html',
                         stats=stats,
                         recent_violations=recent_violations,
                         violation_types=violation_types)

@app.route('/admin')
def admin_home():
    guard = require_admin()
    if guard: return guard
    return redirect(url_for('admin_list_students_with_violations'))

@app.route('/admin/violations')
def admin_list_students_with_violations():
    guard = require_admin()
    if guard: return guard
    base_dir = os.path.join('static', 'violation_screenshots')
    students = []
    if os.path.exists(base_dir):
        students = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    return render_template('admin_students_with_violations_gamified.html', students=students)

@app.route('/admin/violations/<student_name>')
def admin_student_violations(student_name):
    guard = require_admin()
    if guard: return guard
    base_dir = os.path.join('static', 'violation_screenshots', student_name)
    images = []
    if os.path.exists(base_dir):
        for ext in ('*.jpg', '*.jpeg', '*.png', '*.webp'):
            images.extend(glob.glob(os.path.join(base_dir, ext)))
    # Convert to static-relative paths
    images_rel = [os.path.relpath(p, 'static').replace('\\', '/') for p in images]
    return render_template('admin_student_violations_gamified.html', student_name=student_name, images=images_rel)

@app.route('/admin/audio')
def admin_audio_list():
    guard = require_admin()
    if guard: return guard
    # Support both spellings just in case
    audio_dirs = [os.path.join('static', 'OutputAudios'), os.path.join('static', 'OuputAudios')]
    audio_files = []
    for a_dir in audio_dirs:
        if os.path.exists(a_dir):
            for ext in ('*.wav', '*.mp3', '*.m4a', '*.ogg'):
                audio_files.extend(glob.glob(os.path.join(a_dir, ext)))
    audio_rel = [os.path.relpath(p, 'static').replace('\\', '/') for p in audio_files]
    return render_template('admin_audio_list_gamified.html', audio_files=audio_rel)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/reset-db')
def reset_db():
    """Reset the database and create a fresh admin user (for development only)"""
    # Warning: This will delete all data in the database
    if not app.debug:
        return "This route is only available in debug mode.", 403
        
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    
    # Create a fresh admin user
    admin_student = Student(
        name="Admin User",
        email="admin@demo.com",
        password=generate_password_hash("admin123"),
        total_points=500,
        rank_position=1,
        trust_score=100.0,
        is_admin=True
    )
    db.session.add(admin_student)
    db.session.commit()
    
    return "Database reset successfully. Admin user created with email: admin@demo.com and password: admin123"

# Initialize database and create sample data
def init_db():
    with app.app_context():
        db.create_all()
        # Ensure is_admin column exists for existing SQLite DBs
        try:
            from sqlalchemy import text
            info = db.session.execute(text("PRAGMA table_info(students)")).fetchall()
            columns = [row[1] for row in info]
            if 'is_admin' not in columns:
                db.session.execute(text("ALTER TABLE students ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                db.session.commit()
                print("[DB] Added missing column students.is_admin")
        except Exception as e:
            print(f"[DB] Warning: could not verify/add is_admin column: {e}")
        
        # Create sample students if none exist
        if not Student.query.first():
            # Create admin student
            admin_student = Student(
                name="Admin User",
                email="admin@demo.com",
                password=generate_password_hash("admin123"),
                total_points=500,
                rank_position=1,
                trust_score=100.0,
                is_admin=True
            )
            db.session.add(admin_student)
            
            # Create demo student
            demo_student = Student(
                name="Demo Student",
                email="demo@student.com",
                password=generate_password_hash("demo123"),
                total_points=250,
                rank_position=2,
                trust_score=95.0
            )
            db.session.add(demo_student)
            
            # Create test student for violations
            test_student = Student(
                name="Test Student",
                email="test@student.com",
                password=generate_password_hash("test123"),
                total_points=100,
                rank_position=3,
                trust_score=75.0
            )
            db.session.add(test_student)
            
            # Create demo quizzes
            quizzes_data = [
                {
                    'title': 'Python Basics Quiz',
                    'description': 'Test your Python programming knowledge with ML monitoring',
                    'category': 'Programming',
                    'difficulty': 'medium',
                    'time_limit': 5,  # 5 minutes for demo
                    'points': 100,
                    'questions': [
                        {
                            'question_text': 'What is the correct way to create a list in Python?',
                            'option_a': 'list = []', 'option_b': 'list = ()', 
                            'option_c': 'list = {}', 'option_d': 'list = ""', 
                            'correct_answer': 'A'
                        },
                        {
                            'question_text': 'Which method is used to add an element to a list?',
                            'option_a': 'append()', 'option_b': 'add()', 
                            'option_c': 'insert()', 'option_d': 'extend()', 
                            'correct_answer': 'A'
                        },
                        {
                            'question_text': 'What does the len() function return?',
                            'option_a': 'Length of object', 'option_b': 'Type of object', 
                            'option_c': 'Value of object', 'option_d': 'None', 
                            'correct_answer': 'A'
                        },
                        {
                            'question_text': 'Which keyword is used to define a function in Python?',
                            'option_a': 'func', 'option_b': 'function', 
                            'option_c': 'def', 'option_d': 'define', 
                            'correct_answer': 'C'
                        },
                        {
                            'question_text': 'What is the output of print(type([]))?',
                            'option_a': "<class 'list'>", 'option_b': "<class 'array'>", 
                            'option_c': "<class 'tuple'>", 'option_d': "<class 'dict'>", 
                            'correct_answer': 'A'
                        }
                    ]
                },
                {
                    'title': 'JavaScript Fundamentals',
                    'description': 'Test your JavaScript knowledge with real-time proctoring',
                    'category': 'Web Development',
                    'difficulty': 'easy',
                    'time_limit': 3,  # 3 minutes for demo
                    'points': 80,
                    'questions': [
                        {
                            'question_text': 'Which keyword is used to declare a variable in JavaScript?',
                            'option_a': 'var', 'option_b': 'let', 
                            'option_c': 'const', 'option_d': 'All of the above', 
                            'correct_answer': 'D'
                        },
                        {
                            'question_text': 'What is the correct way to create an array in JavaScript?',
                            'option_a': 'var arr = []', 'option_b': 'var arr = {}', 
                            'option_c': 'var arr = ()', 'option_d': 'var arr = ""', 
                            'correct_answer': 'A'
                        },
                        {
                            'question_text': 'Which method adds one or more elements to the end of an array?',
                            'option_a': 'push()', 'option_b': 'pop()', 
                            'option_c': 'shift()', 'option_d': 'unshift()', 
                            'correct_answer': 'A'
                        }
                    ]
                },
                {
                    'title': 'Machine Learning Concepts',
                    'description': 'Advanced ML concepts with comprehensive monitoring',
                    'category': 'AI/ML',
                    'difficulty': 'hard',
                    'time_limit': 10,  # 10 minutes for demo
                    'points': 150,
                    'questions': [
                        {
                            'question_text': 'What is overfitting in machine learning?',
                            'option_a': 'Model performs well on training data but poorly on test data',
                            'option_b': 'Model performs poorly on training data',
                            'option_c': 'Model has too few parameters',
                            'option_d': 'Model takes too long to train',
                            'correct_answer': 'A'
                        },
                        {
                            'question_text': 'Which algorithm is used for classification problems?',
                            'option_a': 'Linear Regression', 'option_b': 'K-Means', 
                            'option_c': 'Random Forest', 'option_d': 'DBSCAN', 
                            'correct_answer': 'C'
                        },
                        {
                            'question_text': 'What is the purpose of cross-validation?',
                            'option_a': 'To increase model complexity',
                            'option_b': 'To reduce training time',
                            'option_c': 'To evaluate model performance on unseen data',
                            'option_d': 'To decrease model accuracy',
                            'correct_answer': 'C'
                        }
                    ]
                }
            ]
            
            # Create quizzes and questions
            for quiz_data in quizzes_data:
                quiz = Quiz(
                    title=quiz_data['title'],
                    description=quiz_data['description'],
                    category=quiz_data['category'],
                    difficulty=quiz_data['difficulty'],
                    time_limit=quiz_data['time_limit'],
                    points=quiz_data['points']
                )
                db.session.add(quiz)
                db.session.flush()
                
                # Create questions for this quiz
                for q_data in quiz_data['questions']:
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=q_data['question_text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_answer=q_data['correct_answer'],
                        points=quiz_data['points'] // len(quiz_data['questions'])
                    )
                    db.session.add(question)
            
            # Create sample achievements
            achievements = [
                Achievement(name="Quiz Master", description="Score 90% or higher on a quiz", icon="crown", points=50, badge_type="gold"),
                Achievement(name="High Achiever", description="Score 80% or higher on a quiz", icon="star", points=30, badge_type="silver"),
                Achievement(name="Clean Record", description="Complete a quiz with no violations", icon="shield", points=25, badge_type="bronze")
            ]
            
            for achievement in achievements:
                db.session.add(achievement)
            
            db.session.commit()
    print("✅ Database initialized with sample data")

# Real-time ML Detection API Endpoints
@app.route('/api/ml/detect_face', methods=['POST'])
def api_detect_face():
    """Real-time face detection API"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        image_data = data.get('image', '')  # Base64 encoded image
        
        if not image_data or not ML_AVAILABLE:
            return jsonify({'error': 'No image data or ML not available'}), 400
        
        # Decode base64 image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Convert to RGB for face detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations_list = face_locations(rgb_frame)
        face_count = len(face_locations_list)
        
        # Get face encodings if faces are detected
        face_encodings_list = []
        if face_count > 0:
            face_encodings_list = face_encodings(rgb_frame, face_locations_list)
        
        return jsonify({
            'success': True,
            'face_count': face_count,
            'face_locations': face_locations_list,
            'face_encodings_count': len(face_encodings_list),
            'message': f'Detected {face_count} face(s)'
        })
        
    except Exception as e:
        return jsonify({'error': f'Face detection failed: {str(e)}'}), 500

@app.route('/api/ml/detect_objects', methods=['POST'])
def api_detect_objects():
    """Real-time object detection API for electronic devices"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data or not ML_AVAILABLE:
            return jsonify({'error': 'No image data or ML not available'}), 400
        
        # Decode base64 image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Detect electronic devices (structured output)
        detected_devices = electronicDevicesDetection(frame, threshold=0.4)

        # Normalize class names and filter
        allowed = {'cell phone', 'laptop', 'tablet', 'keyboard', 'mouse', 'remote'}
        electronic_devices = [d for d in detected_devices if d.get('class') in allowed]

        # Server-side evidence capture if any devices detected
        if electronic_devices:
            try:
                from utils import save_violation_screenshot, Student_Name
                save_violation_screenshot(frame, "electronic_device_detected", getattr(Student_Name, 'value', None) if hasattr(Student_Name, 'value') else Student_Name)
            except Exception:
                pass

        return jsonify({
            'success': True,
            'device_count': len(electronic_devices),
            'devices': electronic_devices,
            'message': f'Detected {len(electronic_devices)} electronic device(s)'
        })
        
    except Exception as e:
        return jsonify({'error': f'Object detection failed: {str(e)}'}), 500

@app.route('/api/ml/detect_head_movement', methods=['POST'])
def api_detect_head_movement():
    """Real-time head movement detection API"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data or not ML_AVAILABLE:
            return jsonify({'error': 'No image data or ML not available'}), 400
        
        # Decode base64 image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Detect head movement
        head_position = headMovmentDetection(frame)
        
        # Determine if looking away (not forward)
        looking_away = head_position != "Forward"
        
        return jsonify({
            'success': True,
            'head_position': head_position,
            'looking_away': looking_away,
            'violation': looking_away,
            'message': f'Head position: {head_position}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Head movement detection failed: {str(e)}'}), 500

@app.route('/api/ml/detect_screen_activity', methods=['POST'])
def api_detect_screen_activity():
    """Real-time screen activity detection API"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        # Detect screen activity
        screen_info = screenDetection()
        
        # Check if exam window is active
        exam_window_active = screen_info.get('exam_window_active', False)
        suspicious_activity = screen_info.get('suspicious_activity', False)
        
        return jsonify({
            'success': True,
            'exam_window_active': exam_window_active,
            'suspicious_activity': suspicious_activity,
            'violation': suspicious_activity or not exam_window_active,
            'current_window': screen_info.get('current_window', 'Unknown'),
            'message': 'Screen activity detected' if suspicious_activity else 'Normal screen activity'
        })
        
    except Exception as e:
        return jsonify({'error': f'Screen detection failed: {str(e)}'}), 500

@app.route('/api/ml/detect_voice_activity', methods=['POST'])
def detect_voice_activity():
    """Real-time voice activity detection API"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        if not ML_AVAILABLE:
            # Fallback simulated voice detection
            voice_detected = random.random() < 0.05
            return jsonify({
                'success': True,
                'voice_detected': voice_detected,
                'volume_level': random.random() * 0.5 + 0.3 if voice_detected else 0,
                'duration': random.random() * 2 + 1 if voice_detected else 0,
                'confidence': random.random() * 0.3 + 0.7,
                'mode': 'simulated'
            })
        
        # Real voice detection using voice_detection function
        voice_result = voice_detection()
        
        return jsonify({
            'success': True,
            'voice_detected': voice_result['voice_detected'],
            'volume_level': voice_result.get('volume_level', 0),
            'duration': voice_result.get('duration', 0),
            'confidence': voice_result.get('confidence', 0.8),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Voice detection failed: {str(e)}'}), 500

@app.route('/api/ml/status', methods=['GET'])
def api_ml_status():
    """Get ML system status"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    return jsonify({
        'success': True,
        'ml_available': ML_AVAILABLE,
        'available_functions': [
            'face_detection',
            'object_detection', 
            'head_movement',
            'screen_detection'
        ] if ML_AVAILABLE else [],
        'message': 'ML systems operational' if ML_AVAILABLE else 'ML systems using fallback mode'
    })

def is_suspicious_app(window_title):
    """Check if a window title indicates suspicious activity"""
    suspicious_keywords = [
        'browser', 'chrome', 'firefox', 'edge', 'safari',
        'whatsapp', 'telegram', 'discord', 'skype',
        'youtube', 'netflix', 'facebook', 'instagram',
        'cheat', 'hack', 'solution', 'answer'
    ]
    
    window_lower = window_title.lower()
    return any(keyword in window_lower for keyword in suspicious_keywords)

@app.route('/admin/violations')
def admin_violations():
    """Admin dashboard to view all violations with evidence"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is admin (for demo, we'll check if student_id is 1)
    if session['student_id'] != 1:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get all violations with student and quiz info
    violations = db.session.query(AntiCheatLog, Student, Quiz).join(
        Student, AntiCheatLog.student_id == Student.id
    ).join(
        Quiz, AntiCheatLog.quiz_id == Quiz.id
    ).order_by(AntiCheatLog.created_at.desc()).all()
    
    return render_template('admin_violations.html', violations=violations)

@app.route('/admin/violation/<int:violation_id>')
def admin_violation_details(violation_id):
    """Detailed view of a specific violation with evidence"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is admin
    if session['student_id'] != 1:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get violation details
    violation = db.session.query(AntiCheatLog, Student, Quiz).join(
        Student, AntiCheatLog.student_id == Student.id
    ).join(
        Quiz, AntiCheatLog.quiz_id == Quiz.id
    ).filter(AntiCheatLog.id == violation_id).first()
    
    if not violation:
        return jsonify({'error': 'Violation not found'}), 404
    
    # Get related violations from the same session
    related_violations = AntiCheatLog.query.filter(
        AntiCheatLog.student_id == violation[0].student_id,
        AntiCheatLog.quiz_id == violation[0].quiz_id,
        AntiCheatLog.created_at >= violation[0].created_at - timedelta(minutes=30),
        AntiCheatLog.created_at <= violation[0].created_at + timedelta(minutes=30)
    ).order_by(AntiCheatLog.created_at.desc()).all()
    
    return render_template('admin_violation_details.html', 
                         violation=violation, 
                         related_violations=related_violations)

@app.route('/api/violations/<int:student_id>/<int:quiz_id>')
def get_violations_api(student_id, quiz_id):
    """API endpoint to get violations for a specific quiz attempt"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Allow students to see their own violations
    if session['student_id'] != student_id and session['student_id'] != 1:
        return jsonify({'error': 'Access denied'}), 403
    
    violations = AntiCheatLog.query.filter_by(
        student_id=student_id,
        quiz_id=quiz_id
    ).order_by(AntiCheatLog.created_at.desc()).all()
    
    return jsonify({
        'violations': [{
            'id': v.id,
            'violation_type': v.violation_type,
            'severity': v.severity,
            'details': v.details,
            'created_at': v.created_at.isoformat(),
            'evidence_url': f"/api/evidence/{v.id}" if v.details and 'evidence' in v.details else None
        } for v in violations]
    })

if __name__ == '__main__':
    # Enable debug mode
    app.debug = True
    
    # Initialize the database
    init_db()
    
    print("🚀 Starting Gamified Online Exam Proctor System...")
    print("📱 Access the application at: http://localhost:5000")
    print("🔧 Development tools:")
    print("   - Reset database: http://localhost:5000/reset-db")
    print("👤 Demo login: demo@student.com / demo123")
    print("🤖 ML API endpoints available at /api/ml/*")
    print("✅ Face Detection: /api/ml/detect_face")
    print("✅ Object Detection: /api/ml/detect_objects") 
    print("✅ Head Movement: /api/ml/detect_head_movement")
    print("✅ Screen Activity: /api/ml/detect_screen_activity")
    print("✅ Voice Detection: /api/ml/detect_voice_activity")
    print("✅ ML Status: /api/ml/status")
    print(f"🤖 ML Available: {ML_AVAILABLE}")
    app.run(debug=True, host='0.0.0.0', port=5000)