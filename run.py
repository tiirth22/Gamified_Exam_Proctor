import os
from app import create_app, db
from app.models.user import User
from app.models.quiz import Quiz, Question
from app.models.attempt import QuizAttempt, AttemptAnswer
from app.models.violation import Violation

# Create the Flask application
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Quiz': Quiz,
        'Question': Question,
        'QuizAttempt': QuizAttempt,
        'AttemptAnswer': AttemptAnswer,
        'Violation': Violation
    }

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
