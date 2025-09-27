from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import random
import time
from datetime import datetime, timedelta
import os
import threading

# Try to import heavy dependencies, fallback to mock functions if not available
try:
    import cv2
    import numpy as np
    from utils import faceDetectionRecording, Head_record_duration, voice_detection, screen_recorder
except ImportError:
    print("Warning: Heavy dependencies not available. Using fallback functions.")
    from utils_fallback import faceDetectionRecording, Head_record_duration, voice_detection, screen_recorder

app = Flask(__name__)
app.secret_key = 'gamified-learning-secret-key-2024'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamified_exam_proctor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Anti-cheat monitoring variables
anticheat_monitoring = {}
monitoring_threads = {}
violation_counts = {}
db = SQLAlchemy(app)

# Anti-cheat helper functions
def get_anticheat_score(student_id):
    """Calculate anti-cheat score based on recent violations"""
    try:
        cur = mysql.connection.cursor()
        cur.execute('''
            SELECT COUNT(*) as violation_count
            FROM anti_cheat_logs 
            WHERE student_id = %s AND created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
        ''', (student_id,))
        result = cur.fetchone()
        violation_count = result[0] if result else 0
        cur.close()
        return max(0, 100 - (violation_count * 10))
    except:
        return 100  # Default to 100 if any error

# Gamification settings
POINTS_PER_CORRECT_ANSWER = 10
BONUS_POINTS_PERFECT_SCORE = 50
BONUS_POINTS_SPEED_DEMON = 25
BONUS_POINTS_NO_VIOLATIONS = 30

@app.route('/')
def index():
    return render_template('gamified_login.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student_id = session['student_id']
    
    # Get student info
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()
    
    # Get leaderboard position
    cur.execute("""
        SELECT s.name, l.total_points, l.rank_position, l.exams_completed, l.average_score
        FROM students s
        JOIN leaderboards l ON s.id = l.student_id
        ORDER BY l.total_points DESC
        LIMIT 10
    """)
    leaderboard = cur.fetchall()
    
    # Get student achievements
    cur.execute("""
        SELECT a.name, a.description, a.icon, a.points, sa.earned_at
        FROM achievements a
        JOIN student_achievements sa ON a.id = sa.achievement_id
        WHERE sa.student_id = %s
        ORDER BY sa.earned_at DESC
        LIMIT 5
    """, (student_id,))
    achievements = cur.fetchall()
    
    # Get available quizzes
    cur.execute("""
        SELECT q.*, c.name as category_name, c.icon as category_icon, c.color as category_color
        FROM quizzes q
        JOIN quiz_categories c ON q.category_id = c.id
        ORDER BY q.difficulty_level, q.title
    """)
    quizzes = cur.fetchall()
    
    cur.close()
    
    return render_template('gamified_dashboard.html', 
                           student=student, 
                           leaderboard=leaderboard,
                           achievements=achievements,
                           quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>')
def start_quiz(quiz_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student_id = session['student_id']
    
    # Create quiz attempt
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO student_quiz_attempts (student_id, quiz_id, start_time, status)
        VALUES (%s, %s, NOW(), 'in_progress')
    """, (student_id, quiz_id))
    attempt_id = cur.lastrowid
    mysql.connection.commit()
    
    # Get quiz info and questions
    cur.execute("SELECT * FROM quizzes WHERE id = %s", (quiz_id,))
    quiz = cur.fetchone()
    
    cur.execute("SELECT * FROM questions WHERE quiz_id = %s ORDER BY RAND()", (quiz_id,))
    questions = cur.fetchall()
    
    # Get student's anti-cheat score and warnings
    cur.execute('''
        SELECT COALESCE(SUM(CASE WHEN violation_type LIKE '%%No face detected%%' THEN 5
                                  WHEN violation_type LIKE '%%Suspicious screen activity%%' THEN 3
                                  WHEN violation_type LIKE '%%Voice/sound detected%%' THEN 2
                                  ELSE 1 END), 0) as anticheat_score,
               COUNT(*) as anticheat_warnings
        FROM anti_cheat_logs 
        WHERE student_id = %s 
        AND quiz_id = %s 
        AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    ''', (student_id, quiz_id))
    result = cur.fetchone()
    anticheat_score = result[0] if result else 0
    anticheat_warnings = result[1] if result else 0
    
    cur.close()
    
    session['current_attempt_id'] = attempt_id
    session['quiz_questions'] = [q[0] for q in questions]  # Store question IDs
    session['current_question_index'] = 0
    session['quiz_start_time'] = time.time()
    
    # Start anti-cheat monitoring
    start_anticheat_monitoring(student_id, quiz_id)
    
    return render_template('gamified_quiz.html', 
                         quiz=quiz, 
                         questions=questions,
                         anticheat_score=anticheat_score,
                         anticheat_warnings=anticheat_warnings)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'student_id' not in session or 'current_attempt_id' not in session:
        return jsonify({'error': 'No active quiz session'})
    
    data = request.json
    question_id = data.get('question_id')
    selected_answer = data.get('answer')
    time_taken = data.get('time_taken', 0)
    
    attempt_id = session['current_attempt_id']
    
    # Get question details
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
    question = cur.fetchone()
    
    if not question:
        return jsonify({'error': 'Question not found'})
    
    # Check if answer is correct
    is_correct = selected_answer == question[6]  # correct_answer column
    points_earned = question[7] if is_correct else 0  # points column
    
    # Record answer (you might want to create an answers table)
    # For now, we'll update the attempt summary
    
    # Move to next question
    session['current_question_index'] += 1
    
    # Check if quiz is complete
    if session['current_question_index'] >= len(session['quiz_questions']):
        # Calculate final score and bonuses
        quiz_time = time.time() - session['quiz_start_time']
        student_id = session['student_id']
        quiz_id = question[1]  # quiz_id from questions table
        
        # Get anti-cheat violations count
        cur.execute('''
            SELECT COUNT(*) as violation_count
            FROM anti_cheat_logs 
            WHERE student_id = %s AND quiz_id = %s 
            AND created_at > DATE_SUB(NOW(), INTERVAL 2 HOUR)
        ''', (student_id, quiz_id))
        violation_count = cur.fetchone()[0]
        
        # Adjust score for violations (-5 points per violation)
        adjusted_points = max(0, points_earned - (violation_count * 5))
        
        # Update attempt with final results
        cur.execute("""
            UPDATE student_quiz_attempts 
            SET end_time = NOW(), 
                status = 'completed',
                time_taken = %s,
                earned_points = %s
            WHERE id = %s
        """, (int(quiz_time), adjusted_points, attempt_id))
        
        # Stop anti-cheat monitoring
        stop_anticheat_monitoring(student_id, quiz_id)
        
        # Update leaderboard
        update_leaderboard(student_id, adjusted_points, is_correct)
        
        # Check for achievements
        check_achievements(session['student_id'], attempt_id)
        
        mysql.connection.commit()
        cur.close()
        
        # Clear session
        session.pop('current_attempt_id', None)
        session.pop('quiz_questions', None)
        session.pop('current_question_index', None)
        session.pop('quiz_start_time', None)
        
        return jsonify({
            'complete': True,
            'score': adjusted_points,
            'time_taken': int(quiz_time),
            'redirect': url_for('quiz_results', attempt_id=attempt_id)
        })
    
    cur.close()
    
    return jsonify({
        'complete': False,
        'correct': is_correct,
        'points': points_earned,
        'next_question_index': session['current_question_index']
    })

def update_leaderboard(student_id, points_earned, correct_answer):
    """Update student leaderboard stats"""
    cur = mysql.connection.cursor()
    
    # Get current stats
    cur.execute("SELECT * FROM leaderboards WHERE student_id = %s", (student_id,))
    current = cur.fetchone()
    
    if current:
        # Update existing record
        new_total_points = current[2] + points_earned
        new_exams_completed = current[3] + 1
        new_average_score = (current[4] * current[3] + (100 if correct_answer else 0)) / new_exams_completed
        
        cur.execute("""
            UPDATE leaderboards 
            SET total_points = %s, 
                exams_completed = %s, 
                average_score = %s,
                last_updated = NOW()
            WHERE student_id = %s
        """, (new_total_points, new_exams_completed, new_average_score, student_id))
    else:
        # Create new record
        cur.execute("""
            INSERT INTO leaderboards (student_id, total_points, exams_completed, average_score)
            VALUES (%s, %s, 1, %s)
        """, (student_id, points_earned, 100 if correct_answer else 0))
    
    # Update rankings
    cur.execute("""
        UPDATE leaderboards l
        JOIN (
            SELECT student_id, ROW_NUMBER() OVER (ORDER BY total_points DESC) as new_rank
            FROM leaderboards
        ) ranked ON l.student_id = ranked.student_id
        SET l.rank_position = ranked.new_rank
    """)
    
    mysql.connection.commit()
    cur.close()

def check_achievements(student_id, attempt_id):
    """Check and award achievements"""
    cur = mysql.connection.cursor()
    
    # Check for First Quiz achievement
    cur.execute("SELECT COUNT(*) FROM student_quiz_attempts WHERE student_id = %s AND status = 'completed'", (student_id,))
    total_quizzes = cur.fetchone()[0]
    
    if total_quizzes == 1:
        award_achievement(student_id, 'First Quiz')
    
    # Check for Perfect Score (simplified)
    cur.execute("SELECT total_score FROM student_quiz_attempts WHERE id = %s", (attempt_id,))
    score = cur.fetchone()
    if score and score[0] >= 90:  # Assuming 90+ is perfect
        award_achievement(student_id, 'Perfect Score')
    
    # Check for Speed Demon (completed in under 5 minutes)
    cur.execute("SELECT time_taken FROM student_quiz_attempts WHERE id = %s", (attempt_id,))
    time_taken = cur.fetchone()
    if time_taken and time_taken[0] < 300:  # 5 minutes in seconds
        award_achievement(student_id, 'Speed Demon')
    
    # Check for Quiz Master (10 quizzes)
    if total_quizzes >= 10:
        award_achievement(student_id, 'Quiz Master')
    
    mysql.connection.commit()
    cur.close()

# Anti-cheat monitoring functions
def start_anticheat_monitoring(student_id, quiz_id):
    """Start anti-cheat monitoring for a student taking a quiz"""
    monitoring_key = f"{student_id}_{quiz_id}"
    
    if monitoring_key not in monitoring_threads:
        # Start face detection monitoring
        face_thread = threading.Thread(target=monitor_face_detection, args=(student_id, quiz_id))
        face_thread.daemon = True
        face_thread.start()
        
        # Start screen monitoring
        screen_thread = threading.Thread(target=monitor_screen_activity, args=(student_id, quiz_id))
        screen_thread.daemon = True
        screen_thread.start()
        
        # Start voice detection
        voice_thread = threading.Thread(target=monitor_voice_activity, args=(student_id, quiz_id))
        voice_thread.daemon = True
        voice_thread.start()
        
        monitoring_threads[monitoring_key] = {
            'face': face_thread,
            'screen': screen_thread,
            'voice': voice_thread,
            'start_time': time.time()
        }

def monitor_face_detection(student_id, quiz_id):
    """Monitor face detection for violations"""
    try:
        # This would integrate with the existing face detection system
        # For now, we'll simulate monitoring
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # If no face detected for extended period, log violation
            if len(faces) == 0:
                log_violation(student_id, quiz_id, 'No face detected')
                
            time.sleep(5)  # Check every 5 seconds
            
            # Check if monitoring should stop
            monitoring_key = f"{student_id}_{quiz_id}"
            if monitoring_key not in monitoring_threads:
                break
                
        cap.release()
    except Exception as e:
        print(f"Face monitoring error: {e}")

def monitor_screen_activity(student_id, quiz_id):
    """Monitor screen for suspicious activity"""
    try:
        # This would integrate with screen recording functionality
        # For now, we'll simulate basic monitoring
        while True:
            # Check for suspicious activity (placeholder logic)
            time.sleep(10)
            
            # Simulate detection of suspicious activity
            if False:  # Replace with actual detection logic
                log_violation(student_id, quiz_id, 'Suspicious screen activity detected')
            
            # Check if monitoring should stop
            monitoring_key = f"{student_id}_{quiz_id}"
            if monitoring_key not in monitoring_threads:
                break
                
    except Exception as e:
        print(f"Screen monitoring error: {e}")

def monitor_voice_activity(student_id, quiz_id):
    """Monitor for voice/sound during quiz"""
    try:
        # This would integrate with voice detection system
        # For now, we'll simulate basic monitoring
        while True:
            time.sleep(15)
            
            # Simulate voice detection
            if False:  # Replace with actual voice detection logic
                log_violation(student_id, quiz_id, 'Voice/sound detected during quiz')
            
            # Check if monitoring should stop
            monitoring_key = f"{student_id}_{quiz_id}"
            if monitoring_key not in monitoring_threads:
                break
                
    except Exception as e:
        print(f"Voice monitoring error: {e}")

def log_violation(student_id, quiz_id, violation_type):
    """Log anti-cheat violation to database"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO anti_cheat_logs (student_id, quiz_id, violation_type, created_at)
            VALUES (%s, %s, %s, NOW())
        ''', (student_id, quiz_id, violation_type))
        mysql.connection.commit()
        cursor.close()
        print(f"Violation logged: {violation_type} for student {student_id}")
    except Exception as e:
        print(f"Error logging violation: {e}")

def stop_anticheat_monitoring(student_id, quiz_id):
    """Stop anti-cheat monitoring for a student"""
    monitoring_key = f"{student_id}_{quiz_id}"
    if monitoring_key in monitoring_threads:
        del monitoring_threads[monitoring_key]

@app.route('/report_violation', methods=['POST'])
def report_violation():
    """Report anti-cheat violation from frontend"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not authenticated'})
    
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    reason = data.get('reason')
    question_number = data.get('question_number')
    
    log_violation(session['student_id'], quiz_id, reason)
    
    return jsonify({'success': True, 'message': 'Violation reported'})

def award_achievement(student_id, achievement_name):
    """Award an achievement to a student"""
    cur = mysql.connection.cursor()
    
    # Get achievement ID
    cur.execute("SELECT id, points FROM achievements WHERE name = %s", (achievement_name,))
    achievement = cur.fetchone()
    
    if achievement:
        achievement_id, points = achievement
        
        # Check if already awarded
        cur.execute("SELECT id FROM student_achievements WHERE student_id = %s AND achievement_id = %s", 
                   (student_id, achievement_id))
        if not cur.fetchone():
            # Award achievement
            cur.execute("INSERT INTO student_achievements (student_id, achievement_id) VALUES (%s, %s)",
                       (student_id, achievement_id))
            
            # Add points to leaderboard
            cur.execute("UPDATE leaderboards SET total_points = total_points + %s WHERE student_id = %s",
                       (points, student_id))
    
    mysql.connection.commit()
    cur.close()

@app.route('/quiz_results/<int:attempt_id>')
def quiz_results(attempt_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    
    # Get quiz attempt details
    cursor.execute('''
        SELECT qa.*, q.title, q.quiz_id, s.name as student_name
        FROM student_quiz_attempts qa
        JOIN quizzes q ON qa.quiz_id = q.quiz_id
        JOIN students s ON qa.student_id = s.student_id
        WHERE qa.id = %s AND qa.student_id = %s
    ''', (attempt_id, session['student_id']))
    attempt = cursor.fetchone()
    
    if not attempt:
        cursor.close()
        return redirect(url_for('dashboard'))
    
    # Get quiz details
    quiz = {
        'quiz_id': attempt['quiz_id'],
        'title': attempt['title']
    }
    
    # Get student details
    student = {
        'name': attempt['student_name']
    }
    
    # Calculate original score based on points (reverse the penalty calculation)
    penalty_points = attempt['score'] * 0.1  # Approximate penalty
    original_score = min(100, attempt['score'] + (penalty_points * 10))
    final_score = attempt['score']
    
    # Get anti-cheat violations for this attempt
    cursor.execute('''
        SELECT * FROM anti_cheat_logs 
        WHERE student_id = %s AND quiz_id = %s 
        AND created_at > DATE_SUB(NOW(), INTERVAL 2 HOUR)
        ORDER BY created_at DESC
    ''', (session['student_id'], attempt['quiz_id']))
    violations = cursor.fetchall()
    
    # Process violations with severity and penalty
    processed_violations = []
    for violation in violations:
        violation_type = violation['violation_type']
        if 'No face detected' in violation_type:
            penalty = 5
            severity = 'error'
        elif 'Suspicious screen activity' in violation_type:
            penalty = 3
            severity = 'warning'
        elif 'Voice/sound detected' in violation_type:
            penalty = 2
            severity = 'warning'
        else:
            penalty = 1
            severity = 'info'
        
        processed_violations.append({
            'violation_type': violation_type,
            'created_at': violation['created_at'],
            'penalty': penalty,
            'severity': severity
        })
    
    # Get achievements earned for this quiz
    achievements = []
    if final_score >= 90 and len(violations) == 0:
        achievements.append('Honest Quiz Master')
    elif final_score >= 90:
        achievements.append('Quiz Master')
    elif final_score >= 80:
        achievements.append('High Achiever')
    
    if len(violations) == 0:
        achievements.append('Clean Record')
    
    # Get current leaderboard rank
    cursor.execute('''
        SELECT student_id, total_score, 
               RANK() OVER (ORDER BY total_score DESC) as rank
        FROM (
            SELECT student_id, SUM(score) as total_score
            FROM student_quiz_attempts
            GROUP BY student_id
        ) leaderboard
        WHERE student_id = %s
    ''', (session['student_id'],))
    rank_result = cursor.fetchone()
    current_rank = rank_result['rank'] if rank_result else 0
    
    # Get total points
    cursor.execute('''
        SELECT SUM(score) as total_points
        FROM student_quiz_attempts
        WHERE student_id = %s
    ''', (session['student_id'],))
    total_points_result = cursor.fetchone()
    total_points = total_points_result['total_points'] if total_points_result['total_points'] else 0
    
    cursor.close()
    
    # Determine score class for styling
    if final_score >= 90:
        score_class = 'excellent'
    elif final_score >= 80:
        score_class = 'good'
    elif final_score >= 70:
        score_class = 'average'
    else:
        score_class = 'poor'
    
    return render_template('quiz_results.html',
                         quiz=quiz,
                         student=student,
                         final_score=final_score,
                         original_score=original_score,
                         score_class=score_class,
                         correct_answers=int((final_score / 100) * 10),  # Approximate
                         total_questions=10,  # Approximate
                         time_taken=int(attempt['time_taken'] / 60),  # Convert to minutes
                         violations=processed_violations,
                         violation_count=len(violations),
                         penalty_points=sum(v['penalty'] for v in processed_violations),
                         achievements=achievements,
                         current_rank=current_rank,
                         total_points=total_points,
                         rank_improved=True)  # Placeholder
    
    # Get any achievements earned in this session
    # You might want to track this better
    
    cur.close()
    
    return render_template('quiz_results.html', result=result)

@app.route('/leaderboard')
def leaderboard():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.name, l.total_points, l.rank_position, l.exams_completed, 
               l.average_score, l.trust_score
        FROM students s
        JOIN leaderboards l ON s.id = l.student_id
        ORDER BY l.total_points DESC
        LIMIT 50
    """)
    leaderboard_data = cur.fetchall()
    cur.close()
    
    return render_template('leaderboard.html', leaderboard=leaderboard_data)

@app.route('/achievements')
def achievements():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student_id = session['student_id']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.name, a.description, a.icon, a.points, a.badge_type,
               CASE WHEN sa.student_id IS NOT NULL THEN 1 ELSE 0 END as earned
        FROM achievements a
        LEFT JOIN student_achievements sa ON a.id = sa.achievement_id AND sa.student_id = %s
        ORDER BY a.points DESC
    """, (student_id,))
    all_achievements = cur.fetchall()
    
    cur.close()
    
    return render_template('achievements.html', achievements=all_achievements)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE email = %s", (email,))
        student = cur.fetchone()
        cur.close()
        
        if student and student[4] == password:  # Simple password check
            session['student_id'] = student[0]
            session['student_name'] = student[1]
            session['student_email'] = student[2]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('gamified_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)