import sqlite3

# Connect to the correct database
conn = sqlite3.connect('gamified_exam_proctor.db')
cursor = conn.cursor()

# Check available tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Available tables:')
for table in tables:
    print(f'- {table[0]}')

# Check for demo quiz
if any('quiz' in str(table) for table in tables):
    cursor.execute('SELECT id, title, description FROM quiz ORDER BY id')
    quizzes = cursor.fetchall()
    print('\nAvailable quizzes:')
    for quiz in quizzes:
        print(f'ID: {quiz[0]}, Title: {quiz[1]}, Description: {quiz[2]}')

# Check for violations
if any('anti_cheat_log' in str(table) for table in tables):
    cursor.execute('SELECT * FROM anti_cheat_log ORDER BY created_at DESC LIMIT 5')
    violations = cursor.fetchall()
    print('\nRecent violations:')
    for v in violations:
        print(f'ID: {v[0]}, Student: {v[1]}, Type: {v[2]}, Severity: {v[3]}, Details: {v[4]}, Time: {v[5]}')

# Check for students
if any('student' in str(table) for table in tables):
    cursor.execute('SELECT id, name, email FROM student ORDER BY id')
    students = cursor.fetchall()
    print('\nAvailable students:')
    for student in students:
        print(f'ID: {student[0]}, Name: {student[1]}, Email: {student[2]}')

conn.close()