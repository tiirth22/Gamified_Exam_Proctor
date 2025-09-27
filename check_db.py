import sqlite3

# Connect to the database
conn = sqlite3.connect('proctoring_system.db')
cursor = conn.cursor()

# Check available tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Available tables:')
for table in tables:
    print(f'- {table[0]}')

# Check if anti_cheat_log exists
if any('anti_cheat_log' in str(table) for table in tables):
    print('\nRecent violations:')
    cursor.execute('SELECT * FROM anti_cheat_log ORDER BY created_at DESC LIMIT 5')
    violations = cursor.fetchall()
    for v in violations:
        print(f'ID: {v[0]}, Student: {v[1]}, Type: {v[2]}, Severity: {v[3]}, Details: {v[4]}, Time: {v[5]}')

# Check if quiz table exists and show demo quiz
if any('quiz' in str(table) for table in tables):
    print('\nAvailable quizzes:')
    cursor.execute('SELECT id, title, description FROM quiz ORDER BY id')
    quizzes = cursor.fetchall()
    for quiz in quizzes:
        print(f'ID: {quiz[0]}, Title: {quiz[1]}, Description: {quiz[2]}')

# Check if question table exists
if any('question' in str(table) for table in tables):
    print('\nQuestions in demo quiz:')
    cursor.execute('SELECT id, question_text FROM question WHERE quiz_id = 2 ORDER BY id')
    questions = cursor.fetchall()
    for q in questions:
        print(f'ID: {q[0]}, Question: {q[1][:50]}...')

conn.close()