import requests
import json

# Create a session to maintain cookies
session = requests.Session()

# Test login
login_data = {'email': 'demo@student.com', 'password': 'demo123'}
login_response = session.post('http://localhost:5000/login', data=login_data)
print(f'Login status: {login_response.status_code}')

# Submit multiple answers for a complete quiz
questions = [
    {'quiz_id': 1, 'question_id': 1, 'answer': 'A', 'time_taken': 25},
    {'quiz_id': 1, 'question_id': 2, 'answer': 'B', 'time_taken': 30},
    {'quiz_id': 1, 'question_id': 3, 'answer': 'C', 'time_taken': 20}
]

print('Submitting quiz answers...')
for i, answer_data in enumerate(questions):
    submit_response = session.post('http://localhost:5000/submit_answer', 
                                  json=answer_data,
                                  headers={'Content-Type': 'application/json'})
    print(f'Question {i+1} submission status: {submit_response.status_code}')
    
    if submit_response.status_code == 200:
        result_data = submit_response.json()
        print(f'  Score: {result_data.get("final_score", "N/A")}')
        print(f'  Anticheat: {result_data.get("anticheat_score", "N/A")}')

# Test accessing dashboard after quiz
dashboard_response = session.get('http://localhost:5000/dashboard')
print(f'Final dashboard status: {dashboard_response.status_code}')

# Test accessing leaderboard
leaderboard_response = session.get('http://localhost:5000/leaderboard')
print(f'Leaderboard status: {leaderboard_response.status_code}')

print('Complete flow test finished successfully!')