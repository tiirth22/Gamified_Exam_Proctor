import sqlite3
import os

def check_db(db_path, name):
    print(f"\n=== Checking {name} ===")
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check available tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f'Available tables in {name}:')
        for table in tables:
            print(f'  - {table[0]}')
        
        # Check for demo quiz
        if any('quiz' in str(table) for table in tables):
            cursor.execute('SELECT id, title, description FROM quiz ORDER BY id')
            quizzes = cursor.fetchall()
            print(f'\nAvailable quizzes in {name}:')
            for quiz in quizzes:
                print(f'  ID: {quiz[0]}, Title: {quiz[1]}, Description: {quiz[2]}')
        
        # Check for violations
        if any('anti_cheat_log' in str(table) for table in tables):
            cursor.execute('SELECT * FROM anti_cheat_log ORDER BY created_at DESC LIMIT 5')
            violations = cursor.fetchall()
            print(f'\nRecent violations in {name}:')
            for v in violations:
                print(f'  ID: {v[0]}, Student: {v[1]}, Type: {v[2]}, Severity: {v[3]}, Details: {v[4]}, Time: {v[5]}')
        
        conn.close()
    except Exception as e:
        print(f"Error checking {name}: {e}")

# Check both databases
check_db('gamified_exam_proctor.db', 'Main DB')
check_db('instance/gamified_exam_proctor.db', 'Instance DB')
check_db('proctoring_system.db', 'Proctoring DB')