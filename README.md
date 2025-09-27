# Gamified_Exam_Proctor
=

A secure online examination platform with AI-powered proctoring capabilities to ensure exam integrity and prevent cheating.

## 📸 Screenshots

### Webcam Feed with Face Detection
<!-- Add screenshot of the webcam feed with face detection overlay -->

![WhatsApp Image 2025-09-27 at 11 44 31 AM](https://github.com/user-attachments/assets/44201395-21b1-49a9-82c3-16941fa1decb)
![WhatsApp Image 2025-09-27 at 11 47 23 AM](https://github.com/user-attachments/assets/70090c24-6016-490a-988b-11876b0e2fc9)


### Exam Interface
<!-- Add screenshot of the exam interface with questions -->
![Exam Interface](./screenshots/exam_interface.png)

### Violation Alert
<!-- Add screenshot of a violation alert -->
![Violation Alert](./screenshots/violation_alert.png)

## 🚀 Features

- **Face Detection**: Ensures only the registered student is taking the exam
- **Real-time Monitoring**: Continuously monitors the exam session for suspicious activities
- **Question Management**: Supports multiple-choice questions with JSON-based question bank
- **Session Management**: Tracks exam sessions with timestamps and user responses
- **Violation Detection**: Flags potential violations like multiple faces or no face detected
- **Responsive UI**: Clean and intuitive interface for both students and administrators

## 🛠️ Tech Stack

- **Backend**: Python 3.8+
- **Web Framework**: Flask
- **Face Recognition**: face-recognition, OpenCV
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Handling**: JSON

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone [your-repository-url]
   cd QuizProctor
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🎯 Usage

1. **Starting an Exam**
   - The system will prompt for camera access
   - Face detection will verify your identity
   - The exam will begin once verification is complete

2. **During the Exam**
   - Answer questions using the provided interface
   - The system monitors for suspicious activities
   - Navigation between questions is logged

3. **Submitting the Exam**
   - Review your answers before submission
   - Click submit to complete the exam
   - Results are saved with timestamp and session details

## 🔒 Security Features

- Session-based authentication
- Face verification at regular intervals
- Activity logging
- Secure data handling

## 📂 Project Structure

### Directory for Screenshots
Create a `screenshots` directory in your project root and add the following screenshots:
- `face_detection.png`: Webcam feed showing face detection in action
- `exam_interface.png`: The main exam interface with questions
- `violation_alert.png`: Example of a violation notification

### ML Model Integration
The system uses the following ML components:
- Face detection and recognition pipeline
- Real-time activity monitoring
- Anomaly detection for suspicious behavior

```
ML Pipeline:
1. Face Detection → Face Recognition → Activity Monitoring → Violation Detection
```


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For any queries or support, please contact tirth2216@gmail.com.
Made by Tirth J Dalal, Hitanshu Varia, Kathan Purohit, Arham Shah
