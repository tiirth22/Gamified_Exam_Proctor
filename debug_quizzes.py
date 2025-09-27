#!/usr/bin/env python3
"""
Debug script to check database contents and quiz availability
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gamified_app_simple import app, db, Quiz, Question, Student

def debug_database():
    """Debug database contents"""
    with app.app_context():
        print("🔍 Debugging Database Contents")
        print("=" * 50)
        
        # Check students
        students = Student.query.all()
        print(f"📊 Students in database: {len(students)}")
        for student in students:
            print(f"  - {student.name} ({student.email})")
        
        print()
        
        # Check quizzes
        quizzes = Quiz.query.all()
        print(f"📚 Quizzes in database: {len(quizzes)}")
        for quiz in quizzes:
            questions = Question.query.filter_by(quiz_id=quiz.id).count()
            print(f"  - {quiz.title} (ID: {quiz.id}, Questions: {questions})")
            print(f"    Category: {quiz.category}, Difficulty: {quiz.difficulty}")
            print(f"    Time: {quiz.time_limit} min, Points: {quiz.points}")
        
        print()
        
        # Check questions
        questions = Question.query.all()
        print(f"❓ Questions in database: {len(questions)}")
        for question in questions:
            print(f"  - Quiz {question.quiz_id}: {question.question_text[:50]}...")
        
        print()
        print("✅ Database debug complete!")

if __name__ == "__main__":
    debug_database()

