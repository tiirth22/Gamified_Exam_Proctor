import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import User
from app.models.quiz import Quiz, Question
from app.models.attempt import QuizAttempt, AttemptAnswer
from app.models.violation import Violation

def init_db():
    """Initialize the database with sample data."""
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate them
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.password = 'admin123'
        db.session.add(admin)
        
        # Create sample student
        print("Creating sample student...")
        student = User(
            username='student1',
            email='student1@example.com',
            first_name='John',
            last_name='Doe',
            is_admin=False
        )
        student.password = 'student123'
        db.session.add(student)
        
        # Create sample quiz
        print("Creating sample quiz...")
        quiz = Quiz(
            title='Sample Quiz',
            description='This is a sample quiz to demonstrate the system.',
            time_limit=30,  # 30 minutes
            passing_score=70,  # 70%
            is_active=True
        )
        db.session.add(quiz)
        db.session.flush()  # Get the quiz ID
        
        # Add questions to the quiz
        questions = [
            {
                'question_text': 'What is the capital of France?',
                'option_a': 'London',
                'option_b': 'Paris',
                'option_c': 'Berlin',
                'option_d': 'Madrid',
                'correct_answer': 'b',
                'marks': 1,
                'explanation': 'Paris is the capital of France.'
            },
            {
                'question_text': 'Which of the following is not a programming language?',
                'option_a': 'Python',
                'option_b': 'Java',
                'option_c': 'HTML',
                'option_d': 'Ruby',
                'correct_answer': 'c',
                'marks': 1,
                'explanation': 'HTML is a markup language, not a programming language.'
            },
            {
                'question_text': 'What does SQL stand for?',
                'option_a': 'Structured Query Language',
                'option_b': 'Simple Query Language',
                'option_c': 'Standard Query Language',
                'option_d': 'Sequential Query Language',
                'correct_answer': 'a',
                'marks': 1,
                'explanation': 'SQL stands for Structured Query Language.'
            }
        ]
        
        for q in questions:
            question = Question(
                quiz_id=quiz.id,
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_answer=q['correct_answer'],
                marks=q['marks'],
                explanation=q['explanation']
            )
            db.session.add(question)
        
        # Create a sample quiz attempt
        print("Creating sample quiz attempt...")
        attempt = QuizAttempt(
            student_id=student.id,
            quiz_id=quiz.id,
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow() - timedelta(minutes=55),
            score=66.67,  # 2 out of 3 correct
            passed=False,
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        db.session.add(attempt)
        db.session.flush()
        
        # Add sample answers
        answers = [
            {'question_id': 1, 'selected_option': 'b', 'is_correct': True, 'time_taken': 15.5},
            {'question_id': 2, 'selected_option': 'a', 'is_correct': False, 'time_taken': 12.3},
            {'question_id': 3, 'selected_option': 'a', 'is_correct': True, 'time_taken': 18.7}
        ]
        
        for a in answers:
            answer = AttemptAnswer(
                attempt_id=attempt.id,
                question_id=a['question_id'],
                selected_option=a['selected_option'],
                is_correct=a['is_correct'],
                time_taken=a['time_taken']
            )
            db.session.add(answer)
        
        # Create sample violations
        print("Creating sample violations...")
        violations = [
            {
                'student_id': student.id,
                'attempt_id': attempt.id,
                'violation_type': 'face_not_visible',
                'severity': Violation.SEVERITY_MEDIUM,
                'description': 'Face was not visible for more than 10 seconds',
                'created_at': datetime.utcnow() - timedelta(minutes=50)
            },
            {
                'student_id': student.id,
                'attempt_id': attempt.id,
                'violation_type': 'tab_switch',
                'severity': Violation.SEVERITY_HIGH,
                'description': 'Tab was switched during the exam',
                'created_at': datetime.utcnow() - timedelta(minutes=45)
            }
        ]
        
        for v in violations:
            violation = Violation(**v)
            db.session.add(violation)
        
        # Commit all changes
        print("Committing changes to the database...")
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
