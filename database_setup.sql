-- Database setup for Online Exam Proctor with Gamified Learning System
CREATE DATABASE IF NOT EXISTS examproctordb;
USE examproctordb;

-- Existing students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'STUDENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gamified learning tables
CREATE TABLE IF NOT EXISTS achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(255),
    points INT DEFAULT 0,
    badge_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    achievement_id INT,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);

CREATE TABLE IF NOT EXISTS leaderboards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    total_points INT DEFAULT 0,
    exams_completed INT DEFAULT 0,
    average_score FLOAT DEFAULT 0,
    trust_score FLOAT DEFAULT 100,
    rank_position INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS quiz_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(20),
    icon VARCHAR(255),
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INT,
    difficulty_level VARCHAR(20),
    time_limit INT DEFAULT 30,
    total_questions INT DEFAULT 10,
    points_per_question INT DEFAULT 10,
    bonus_points INT DEFAULT 0,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES quiz_categories(id),
    FOREIGN KEY (created_by) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'multiple_choice',
    options JSON,
    correct_answer TEXT,
    explanation TEXT,
    points INT DEFAULT 10,
    time_limit INT DEFAULT 30,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);

CREATE TABLE IF NOT EXISTS student_quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    quiz_id INT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    total_score INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    wrong_answers INT DEFAULT 0,
    time_taken INT DEFAULT 0,
    trust_score FLOAT DEFAULT 100,
    violations_detected INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'in_progress',
    earned_points INT DEFAULT 0,
    bonus_points INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);

CREATE TABLE IF NOT EXISTS anti_cheat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attempt_id INT,
    violation_type VARCHAR(50),
    violation_description TEXT,
    severity_level INT DEFAULT 1,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    video_evidence VARCHAR(255),
    screenshot_evidence VARCHAR(255),
    FOREIGN KEY (attempt_id) REFERENCES student_quiz_attempts(id)
);

-- Insert sample data
INSERT INTO students (name, email, password, role) VALUES
('Admin User', 'admin@example.com', 'admin123', 'ADMIN'),
('John Doe', 'john@example.com', 'student123', 'STUDENT'),
('Jane Smith', 'jane@example.com', 'student123', 'STUDENT'),
('Mike Johnson', 'mike@example.com', 'student123', 'STUDENT');

INSERT INTO achievements (name, description, icon, points, badge_type) VALUES
('First Quiz', 'Complete your first quiz', '🎯', 50, 'bronze'),
('Perfect Score', 'Get 100% on a quiz', '💯', 100, 'gold'),
('Speed Demon', 'Complete a quiz in under 5 minutes', '⚡', 75, 'silver'),
('Trust Champion', 'Maintain 100% trust score', '🛡️', 150, 'gold'),
('Quiz Master', 'Complete 10 quizzes', '🏆', 200, 'platinum'),
('Anti-Cheat Hero', 'Complete quiz with no violations', '👮', 100, 'gold'),
('Consistent Learner', 'Complete 5 quizzes in a row', '🔥', 120, 'silver'),
('Night Owl', 'Complete a quiz after 10 PM', '🦉', 30, 'bronze');

INSERT INTO quiz_categories (name, description, difficulty_level, icon, color) VALUES
('Mathematics', 'Test your math skills', 'medium', '🔢', '#FF6B6B'),
('Science', 'Explore scientific concepts', 'hard', '🔬', '#4ECDC4'),
('History', 'Journey through time', 'easy', '📚', '#45B7D1'),
('Programming', 'Code your way to success', 'hard', '💻', '#96CEB4'),
('General Knowledge', 'Test your awareness', 'medium', '🌍', '#FFEAA7');

INSERT INTO quizzes (title, description, category_id, difficulty_level, time_limit, total_questions, points_per_question, bonus_points, created_by) VALUES
('Basic Math Challenge', 'Test your basic arithmetic skills', 1, 'easy', 15, 5, 20, 25, 1),
('Science Fundamentals', 'Basic science questions for beginners', 2, 'easy', 20, 8, 15, 20, 1),
('World History Quiz', 'Test your knowledge of world history', 3, 'medium', 25, 10, 10, 15, 1),
('Python Programming', 'Test your Python skills', 4, 'hard', 30, 12, 25, 50, 1),
('General Knowledge Test', 'Mixed questions from various topics', 5, 'medium', 20, 8, 15, 30, 1);

INSERT INTO questions (quiz_id, question_text, question_type, options, correct_answer, explanation, points, time_limit) VALUES
(1, 'What is 15 + 27?', 'multiple_choice', '["40", "42", "44", "46"]', '42', 'Basic addition: 15 + 27 = 42', 20, 30),
(1, 'What is 8 × 7?', 'multiple_choice', '["54", "56", "58", "60"]', '56', 'Multiplication: 8 × 7 = 56', 20, 30),
(1, 'What is 100 ÷ 4?', 'multiple_choice', '["20", "25", "30", "35"]', '25', 'Division: 100 ÷ 4 = 25', 20, 30),
(1, 'What is 12 - 8?', 'multiple_choice', '["2", "3", "4", "5"]', '4', 'Subtraction: 12 - 8 = 4', 20, 30),
(1, 'What is 9 × 9?', 'multiple_choice', '["79", "81", "83", "85"]', '81', 'Multiplication: 9 × 9 = 81', 20, 30);

-- Create indexes for better performance
CREATE INDEX idx_student_quiz_attempts_student_id ON student_quiz_attempts(student_id);
CREATE INDEX idx_student_quiz_attempts_quiz_id ON student_quiz_attempts(quiz_id);
CREATE INDEX idx_anti_cheat_logs_attempt_id ON anti_cheat_logs(attempt_id);
CREATE INDEX idx_leaderboards_total_points ON leaderboards(total_points DESC);
CREATE INDEX idx_student_achievements_student_id ON student_achievements(student_id);