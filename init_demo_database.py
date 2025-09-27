#!/usr/bin/env python3
"""
Initialize database with complete demo data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gamified_app_simple import app, db, Quiz, Question, Student, Achievement
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_complete_demo_database():
    """Initialize database with complete demo data"""
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("🔄 Creating fresh database...")
        
        # Create demo students
        students = [
            Student(
                name="Admin User",
                email="admin@demo.com",
                password=generate_password_hash("admin123"),
                total_points=500,
                rank_position=1,
                trust_score=100.0
            ),
            Student(
                name="Demo Student",
                email="demo@student.com",
                password=generate_password_hash("demo123"),
                total_points=250,
                rank_position=2,
                trust_score=95.0
            ),
            Student(
                name="Test Student",
                email="test@student.com",
                password=generate_password_hash("test123"),
                total_points=100,
                rank_position=3,
                trust_score=75.0
            )
        ]
        
        for student in students:
            db.session.add(student)
        
        print("👥 Created demo students")
        
        # Create comprehensive demo quizzes
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
            },
            {
                'title': '🚨 ML Detection Demo Quiz',
                'description': 'Special quiz to test all ML monitoring features. Try switching tabs, covering camera, or speaking!',
                'category': 'Demo',
                'difficulty': 'easy',
                'time_limit': 10,
                'points': 50,
                'questions': [
                    {
                        'question_text': 'During this quiz, try looking away from the screen or covering your camera to test face detection.',
                        'option_a': 'I understand', 'option_b': 'Got it', 
                        'option_c': 'Will do', 'option_d': 'Testing now', 
                        'correct_answer': 'A'
                    },
                    {
                        'question_text': 'Try speaking or making sounds during this quiz to test voice detection.',
                        'option_a': 'Voice test', 'option_b': 'Audio check', 
                        'option_c': 'Speaking now', 'option_d': 'Sound test', 
                        'correct_answer': 'C'
                    },
                    {
                        'question_text': 'You can test screen monitoring by switching tabs or opening developer tools (F12).',
                        'option_a': 'Tab test', 'option_b': 'Screen test', 
                        'option_c': 'Dev tools', 'option_d': 'All above', 
                        'correct_answer': 'D'
                    },
                    {
                        'question_text': 'Face detection can be tested by covering your camera or having someone else in the frame.',
                        'option_a': 'Face test', 'option_b': 'Camera test', 
                        'option_c': 'Cover test', 'option_d': 'Multi-face', 
                        'correct_answer': 'B'
                    },
                    {
                        'question_text': 'This is the final question. The system should have captured any violations you triggered.',
                        'option_a': 'Complete', 'option_b': 'Finished', 
                        'option_c': 'Done', 'option_d': 'All done', 
                        'correct_answer': 'A'
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
        
        print("📚 Created demo quizzes with questions")
        
        # Create achievements
        achievements = [
            Achievement(name="Quiz Master", description="Score 90% or higher on a quiz", icon="crown", points=50, badge_type="gold"),
            Achievement(name="High Achiever", description="Score 80% or higher on a quiz", icon="star", points=30, badge_type="silver"),
            Achievement(name="Clean Record", description="Complete a quiz with no violations", icon="shield", points=25, badge_type="bronze"),
            Achievement(name="ML Tester", description="Complete the ML Detection Demo Quiz", icon="robot", points=40, badge_type="special"),
            Achievement(name="Speed Demon", description="Complete a quiz in under 2 minutes", icon="bolt", points=35, badge_type="bronze")
        ]
        
        for achievement in achievements:
            db.session.add(achievement)
        
        print("🏆 Created achievements")
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database initialization complete!")
        print("\n📊 Summary:")
        print(f"👥 Students: {len(students)}")
        print(f"📚 Quizzes: {len(quizzes_data)}")
        print(f"❓ Questions: {sum(len(q['questions']) for q in quizzes_data)}")
        print(f"🏆 Achievements: {len(achievements)}")
        
        print("\n🎯 Demo Accounts:")
        print("Admin: admin@demo.com / admin123")
        print("Student: demo@student.com / demo123")
        print("Test: test@student.com / test123")

if __name__ == "__main__":
    init_complete_demo_database()

