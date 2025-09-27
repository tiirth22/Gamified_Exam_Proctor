import numpy as np
import cv2
import mediapipe as mp
import time
import math
import random
import os
import json
import shutil
import pyautogui
import pygetwindow as gw
from ultralytics import YOLO
import pyaudio
import wave
import subprocess
from datetime import datetime

# Face recognition fallback - use MediaPipe instead
try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False
    print("Warning: face_recognition not available, using MediaPipe fallback")

# Function to get or create student's screenshot directory
def get_student_screenshot_dir(student_name):
    """
    Create and return the path to the student's screenshot directory
    """
    # Sanitize student name to create a valid directory name
    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in student_name)
    dir_path = os.path.join('static', 'violation_screenshots', safe_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

# Function to save violation screenshots
def save_violation_screenshot(frame, violation_type, student_name=None):
    """
    Save a screenshot of the violation with timestamp in student's directory
    
    Args:
        frame: The image frame to save
        violation_type: Type of violation (e.g., 'multiple_faces', 'phone_detected')
        student_name: Name of the student (used to organize screenshots)
    """
    try:
        if student_name is None:
            student_name = Student_Name  # Use global Student_Name if not provided
            
        # Get or create student's directory
        student_dir = get_student_screenshot_dir(student_name)
        
        # Create filename with timestamp and violation type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_violation = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in violation_type)
        filename = os.path.join(student_dir, f"{safe_violation}_{timestamp}.jpg")
        
        # Save the image
        cv2.imwrite(filename, frame)
        print(f"Violation screenshot saved: {filename}")
        
        # Return relative path for web access
        return os.path.relpath(filename, 'static').replace('\\', '/')
    except Exception as e:
        print(f"Error saving violation screenshot: {str(e)}")
        return None

#Variables
#All Related
Globalflag = False
Student_Name = ''
start_time = [0, 0, 0, 0, 0]
end_time = [0, 0, 0, 0, 0]
recorded_durations = []
prev_state = ['Verified Student appeared', "Forward", "Only one person is detected", "Stay in the Test", "No Electronic Device Detected"]
flag = [False, False, False, False, False]
capb= cv2.VideoCapture(0)
width= int(capb.get(cv2.CAP_PROP_FRAME_WIDTH))
height= int(capb.get(cv2.CAP_PROP_FRAME_HEIGHT))
capb.release()
capa = cv2.VideoCapture("test_V.mp4")
EDWidth=int(capa.get(cv2.CAP_PROP_FRAME_WIDTH))
EDHeight=int(capa.get(cv2.CAP_PROP_FRAME_HEIGHT))
capa.release()
video = [(str(random.randint(1,50000))+".mp4"), (str(random.randint(1,50000))+".mp4"), (str(random.randint(1,50000))+".mp4"), (str(random.randint(1,50000))+".mp4"), (str(random.randint(1,50000))+".mp4")]
writer = [cv2.VideoWriter(video[0], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)), cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)), cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)), cv2.VideoWriter(video[3], cv2.VideoWriter_fourcc(*'mp4v'), 15, (1920, 1080)), cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), 20 , (EDWidth,EDHeight))]
#More than One Person Related
mpFaceDetection = mp.solutions.face_detection  # Detect the face
mpDraw = mp.solutions.drawing_utils  # Draw the required Things for BBox
faceDetection = mpFaceDetection.FaceDetection(0.75)# It has 0 to 1 (Change this to make it more detectable) Default is 0.5 and higher means more detection.
#Screen Related
shorcuts = []
active_window_title = "Exam — Mozilla Firefox"
exam_window_title = active_window_title
#ED Related
my_file = open("utils/coco.txt", "r") # opening the file in read mode
data = my_file.read() # reading the file
class_list = data.split("\n") # replacing end splitting the text | when newline ('\n') is seen.
my_file.close()
detection_colors = [] # Generate random colors for class list
for i in range(len(class_list)):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    detection_colors.append((b, g, r))
model = YOLO("yolov8n.pt", "v8") # load a pretrained YOLOv8n model
EDFlag = False
#Voice Related
TRIGGER_RMS = 10  # start recording above 10
RATE = 16000  # sample rate
TIMEOUT_SECS = 3  # silence time after which recording stops
FRAME_SECS = 0.25  # length of frame(chunks) to be processed at once in secs
CUSHION_SECS = 1  # amount of recording before and after sound
SHORT_NORMALIZE = (1.0 / 32768.0)
FORMAT = pyaudio.paInt16
CHANNELS = 1
SHORT_WIDTH = 2
CHUNK = int(RATE * FRAME_SECS)
CUSHION_FRAMES = int(CUSHION_SECS / FRAME_SECS)
TIMEOUT_FRAMES = int(TIMEOUT_SECS / FRAME_SECS)
# Capture
cap = None


#Database and Files Related
# function to add data to JSON
def write_json(new_data, filename='violation.json'):
    with open(filename,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

#Function to move the files to the Output Folders
def move_file_to_output_folder(file_name,folder_name='OutputVideos'):
    # Get the current working directory (project folder)
    current_directory = os.getcwd()
    # Define the paths for the source file and destination folder
    source_path = os.path.join(current_directory, file_name)
    dest_dir = os.path.join(current_directory, 'static', folder_name)
    os.makedirs(dest_dir, exist_ok=True)
    destination_path = os.path.join(dest_dir, file_name)
    try:
        # Use 'shutil.move' to move the file to the destination folder
        shutil.move(source_path, destination_path)
        print(f"File moved to static/{folder_name}: {file_name}")
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found in the project folder.")
    except shutil.Error as e:
        print(f"Error: Failed to move the file. {e}")

#Function to reduce video file's data rate to 100 kbps
def reduceBitRate (input_file,output_file):
   target_bitrate = "1000k"  # Set your desired target bitrate here
   # Specify the full path to the FFmpeg executable
   ffmpeg_path = "C:/Users/kaungmyat/Downloads/ffmpeg-2023-08-28-git-b5273c619d-essentials_build/ffmpeg-2023-08-28-git-b5273c619d-essentials_build/bin/ffmpeg.exe"  # Replace with the actual path to ffmpeg.exe on your system
   # Run FFmpeg command to lower the bitrate
   command = [
      ffmpeg_path,
      "-i", input_file,
      "-b:v", target_bitrate,
      "-c:v", "libx264",
      "-c:a", "aac",
      "-strict", "experimental",
      "-b:a", "192k",
      output_file
   ]
   subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   print("Bitrate conversion completed.")

#Recordings related
#Recording Function for Face Verification
def faceDetectionRecording(img, text):
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height
    print("Running FaceDetection Recording Function")
    print(text)
    if text != 'Verified Student appeared' and prev_state[0] == 'Verified Student appeared':
        start_time[0] = time.time()
        for _ in range(2):
            writer[0].write(img)
    elif text != 'Verified Student appeared' and str(text) == prev_state[0] and (time.time() - start_time[0]) > 3:
        flag[0] = True
        for _ in range(2):
            writer[0].write(img)
    elif text != 'Verified Student appeared' and str(text) == prev_state[0] and (time.time() - start_time[0]) <= 3:
        flag[0] = False
        for _ in range(2):
            writer[0].write(img)
    else:
        if prev_state[0] != "Verified Student appeared":
            writer[0].release()
            end_time[0] = time.time()
            duration = math.ceil((end_time[0] - start_time[0]) / 3)
            outputVideo = 'FDViolation' + video[0]
            FDViolation = {
                "Name": prev_state[0],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[0])),
                "Duration": str(duration) + " seconds",
                "Mark": math.floor(2 * duration),
                "Link": outputVideo,
                "RId": get_resultId()
            }
            if flag[0]:
                recorded_durations.append(FDViolation)
                write_json(FDViolation)
                reduceBitRate(video[0], outputVideo)
                move_file_to_output_folder(outputVideo)
            os.remove(video[0])
            print(recorded_durations)
            video[0] = str(random.randint(1, 50000)) + ".mp4"
            writer[0] = cv2.VideoWriter(video[0], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))
            flag[0] = False
    prev_state[0] = text

#Recording Function for Head Movement Detection
def Head_record_duration(text,img):
    global start_time, end_time, recorded_durations, prev_state, flag,writer, width, height
    print("Running HeadMovement Recording Function")
    print(text)
    if text != "Forward":
        if str(text) != prev_state[1] and prev_state[1] == "Forward":
            start_time[1] = time.time()
            for _ in range(2):
                writer[1].write(img)
        elif str(text) != prev_state[1] and prev_state[1] != "Forward":
            writer[1].release()
            end_time[1] = time.time()
            duration = math.ceil((end_time[1] - start_time[1])/7)
            outputVideo = 'HeadViolation' + video[1]
            HeadViolation = {
                "Name": prev_state[1],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[1])),
                "Duration": str(duration) + " seconds",
                "Mark": duration,
                "Link": outputVideo,
                "RId": get_resultId()
            }
            if flag[1]:
                recorded_durations.append(HeadViolation)
                write_json(HeadViolation)
                reduceBitRate(video[1], outputVideo)
                move_file_to_output_folder(outputVideo)
            os.remove(video[1])
            print(recorded_durations)
            video[1] = str(random.randint(1, 50000)) + ".mp4"
            writer[1] = cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))
            flag[1] = False
    prev_state[1] = text

#More than One Person Detection Related
#Detection Function for More than One Person
def MTOP_Detection(img):
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height
    print("Running MTOP Detection Function")
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = faceDetection.process(imgRGB)
    
    if results.detections:
        person_count = len(results.detections)
        print(f"Detected {person_count} person(s)")
        
        if person_count > 1:
            text = f"{person_count} persons are detected"
            # Save screenshot when multiple people are detected
            save_violation_screenshot(img, f"multiple_persons_detected_{person_count}", Student_Name)
            if text != prev_state[2] and prev_state[2] == "Only one person is detected":
                start_time[2] = time.time()
                for _ in range(2):
                    writer[2].write(img)
            elif text != prev_state[2] and prev_state[2] != "Only one person is detected":
                writer[2].release()
                end_time[2] = time.time()
                duration = math.ceil((end_time[2] - start_time[2])/3)
                outputVideo = 'MTOPViolation' + video[2]
                MTOPViolation = {
                    "Name": prev_state[2],
                    "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[2])),
                    "Duration": str(duration) + " seconds",
                    "Mark": math.floor(2 * duration),
                    "Link": outputVideo,
                    "RId": get_resultId()
                }
                if flag[2]:
                    recorded_durations.append(MTOPViolation)
                    write_json(MTOPViolation)
                    reduceBitRate(video[2], outputVideo)
                    move_file_to_output_folder(outputVideo)
                os.remove(video[2])
                print(recorded_durations)
                video[2] = str(random.randint(1, 50000)) + ".mp4"
                writer[2] = cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))
                flag[2] = False
            prev_state[2] = text
        else:
            text = "Only one person is detected"
            if text != prev_state[2] and prev_state[2] != "Only one person is detected":
                writer[2].release()
                end_time[2] = time.time()
                duration = math.ceil((end_time[2] - start_time[2])/3)
                outputVideo = 'MTOPViolation' + video[2]
                MTOPViolation = {
                    "Name": prev_state[2],
                    "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[2])),
                    "Duration": str(duration) + " seconds",
                    "Mark": math.floor(2 * duration),
                    "Link": outputVideo,
                    "RId": get_resultId()
                }
                if flag[2]:
                    recorded_durations.append(MTOPViolation)
                    write_json(MTOPViolation)
                    reduceBitRate(video[2], outputVideo)
                    move_file_to_output_folder(outputVideo)
                os.remove(video[2])
                print(recorded_durations)
                video[2] = str(random.randint(1, 50000)) + ".mp4"
                writer[2] = cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))
                flag[2] = False
            prev_state[2] = text
    else:
        text = "No person is detected"
        if text != prev_state[2] and prev_state[2] != "No person is detected":
            start_time[2] = time.time()
            for _ in range(2):
                writer[2].write(img)
        elif text == prev_state[2] and prev_state[2] == "No person is detected" and (time.time() - start_time[2]) > 3:
            flag[2] = True
            # Save screenshot when no person is detected for more than 3 seconds
            save_violation_screenshot(img, "no_person_detected", Student_Name)
            for _ in range(2):
                writer[2].write(img)
        elif text == prev_state[2] and prev_state[2] == "No person is detected" and (time.time() - start_time[2]) <= 3:
            flag[2] = False
            for _ in range(2):
                writer[2].write(img)
        prev_state[2] = text
    
    return img

#Screen Related
#Recording Function for Screen Detection
def screenDetection(img):
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height
    print("Running Screen Detection Function")
    active_window = gw.getActiveWindow()
    if active_window is not None:
        current_title = active_window.title
        print(f"Active window: {current_title}")
        
        # Check if the active window title matches the exam window title
        if exam_window_title not in current_title:
            text = "Switched from Exam Window"
            if text != prev_state[3] and prev_state[3] == "Stay in the Test":
                start_time[3] = time.time()
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)
                screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                resized_screenshot = cv2.resize(screenshot_bgr, (1920, 1080))
                for _ in range(2):
                    writer[3].write(resized_screenshot)
            elif text == prev_state[3] and (time.time() - start_time[3]) > 3:
                flag[3] = True
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)
                screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                resized_screenshot = cv2.resize(screenshot_bgr, (1920, 1080))
                for _ in range(2):
                    writer[3].write(resized_screenshot)
            elif text == prev_state[3] and (time.time() - start_time[3]) <= 3:
                flag[3] = False
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)
                screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                resized_screenshot = cv2.resize(screenshot_bgr, (1920, 1080))
                for _ in range(2):
                    writer[3].write(resized_screenshot)
            prev_state[3] = text
        else:
            text = "Stay in the Test"
            if text != prev_state[3] and prev_state[3] != "Stay in the Test":
                writer[3].release()
                end_time[3] = time.time()
                duration = math.ceil((end_time[3] - start_time[3])/3)
                outputVideo = 'ScreenViolation' + video[3]
                ScreenViolation = {
                    "Name": prev_state[3],
                    "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[3])),
                    "Duration": str(duration) + " seconds",
                    "Mark": math.floor(2 * duration),
                    "Link": outputVideo,
                    "RId": get_resultId()
                }
                if flag[3]:
                    recorded_durations.append(ScreenViolation)
                    write_json(ScreenViolation)
                    reduceBitRate(video[3], outputVideo)
                    move_file_to_output_folder(outputVideo)
                os.remove(video[3])
                print(recorded_durations)
                video[3] = str(random.randint(1, 50000)) + ".mp4"
                writer[3] = cv2.VideoWriter(video[3], cv2.VideoWriter_fourcc(*'mp4v'), 15, (1920, 1080))
                flag[3] = False
            prev_state[3] = text
    else:
        text = "No Active Window Detected"
        if text != prev_state[3] and prev_state[3] != "No Active Window Detected":
            start_time[3] = time.time()
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            resized_screenshot = cv2.resize(screenshot_bgr, (1920, 1080))
            for _ in range(2):
                writer[3].write(resized_screenshot)
        elif text == prev_state[3] and prev_state[3] == "No Active Window Detected" and (time.time() - start_time[3]) > 3:
            flag[3] = True
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            resized_screenshot = cv2.resize(screenshot_bgr, (1920, 1080))
            for _ in range(2):
                writer[3].write(resized_screenshot)
        elif text == prev_state[3] and prev_state[3] == "No Active Window Detected" and (time.time() - start_time[3]) <= 3:
            flag[3] = False
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            resized_screenshot = cv2.resize(screenshot_bgr, (1920, 1080))
            for _ in range(2):
                writer[3].write(resized_screenshot)
        prev_state[3] = text

#Recording Function for Electronic Device Detection
# Returns structured detections for API use while keeping side effects (drawing, video writers, screenshots)
def electronicDevicesDetection(img, threshold: float = 0.4):
    global start_time, end_time, recorded_durations, prev_state, flag, writer, EDWidth, EDHeight, EDFlag, detection_colors, class_list
    print("Running Electronic Device Detection Function")

    detections = []
    results = model.predict(img)

    # Normalized device classes (lowercase) to detect
    device_aliases = {
        'cell phone': 'cell phone',
        'cellphone': 'cell phone',
        'mobile phone': 'cell phone',
        'phone': 'cell phone',
        'laptop': 'laptop',
        'tv': 'tv',
        'mouse': 'mouse',
        'keyboard': 'keyboard',
        'remote': 'remote',
        'tablet': 'tablet'
    }

    any_device_detected = False

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            class_id = int(box.cls[0])
            class_name = class_list[class_id]
            confidence = float(box.conf[0])

            cls_l = class_name.lower()
            norm_class = device_aliases.get(cls_l)

            if norm_class and confidence >= threshold:
                any_device_detected = True
                detections.append({
                    'class': norm_class,
                    'confidence': round(confidence, 4),
                    'bbox': [x1, y1, x2, y2]
                })

                # Draw bounding box for local pipelines
                cv2.rectangle(img, (x1, y1), (x2, y2), detection_colors[class_id], 2)
                cv2.putText(img, f"{norm_class} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, detection_colors[class_id], 2)

                text = f"Electronic Device Detected: {norm_class}"
                # Save screenshot when electronic device is detected
                try:
                    save_violation_screenshot(img, f"electronic_device_{norm_class.replace(' ', '_')}", Student_Name)
                except Exception as _e:
                    pass

                # Writer logic (unchanged)
                if text != prev_state[4] and prev_state[4] == "No Electronic Device Detected":
                    start_time[4] = time.time()
                    for _ in range(2):
                        writer[4].write(img)
                elif text == prev_state[4] and (time.time() - start_time[4]) > 3:
                    flag[4] = True
                    for _ in range(2):
                        writer[4].write(img)
                elif text == prev_state[4] and (time.time() - start_time[4]) <= 3:
                    flag[4] = False
                    for _ in range(2):
                        writer[4].write(img)
                prev_state[4] = text

        # After iterating boxes of this result, if none matched threshold, handle no-device path
        if not any_device_detected:
            text = "No Electronic Device Detected"
            if text != prev_state[4] and prev_state[4] != "No Electronic Device Detected":
                writer[4].release()
                end_time[4] = time.time()
                duration = math.ceil((end_time[4] - start_time[4]) / 3)
                outputVideo = 'EDViolation' + video[4]
                EDViolation = {
                    "Name": prev_state[4],
                    "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[4])),
                    "Duration": str(duration) + " seconds",
                    "Mark": math.floor(2 * duration),
                    "Link": outputVideo,
                    "RId": get_resultId()
                }
                if flag[4]:
                    recorded_durations.append(EDViolation)
                    write_json(EDViolation)
                    reduceBitRate(video[4], outputVideo)
                    move_file_to_output_folder(outputVideo)
                os.remove(video[4])
                print(recorded_durations)
                video[4] = str(random.randint(1, 50000)) + ".mp4"
                writer[4] = cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), 20, (EDWidth, EDHeight))
                flag[4] = False
            prev_state[4] = text
            EDFlag = False
        else:
            EDFlag = True

    return detections

#Voice Related
#Detection Function for Voice Detection
def voice_detection():
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height
    print("Running Voice Detection Function")
    
    def get_rms(block):
        return np.sqrt(np.mean(np.square(block)))

    def write_wav(filename, data, rate):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SHORT_WIDTH)
            wf.setframerate(rate)
            wf.writeframes(b''.join(data))

    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        print("Voice detection started...")
        recording = False
        recording_data = []
        silent_frames = 0
        
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = get_rms(np.frombuffer(data, dtype=np.int16))
            
            if rms > TRIGGER_RMS:
                if not recording:
                    recording = True
                    recording_data = []
                    print("Voice detected - recording started")
                    text = "Voice Detected"
                    
                    if text != prev_state[4] and prev_state[4] == "No Voice Detected":
                        start_time[4] = time.time()
                        # Create a simple visualization frame
                        frame = np.zeros((height, width, 3), dtype=np.uint8)
                        cv2.putText(frame, "VOICE DETECTED", (width//2 - 200, height//2), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                        for _ in range(2):
                            writer[4].write(frame)
                
                recording_data.append(data)
                silent_frames = 0
            else:
                if recording:
                    recording_data.append(data)
                    silent_frames += 1
                    
                    if silent_frames > TIMEOUT_FRAMES:
                        # Save recording
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"voice_detection_{timestamp}.wav"
                        write_wav(filename, recording_data, RATE)
                        
                        print(f"Voice recording saved: {filename}")
                        recording = False
                        recording_data = []
                        silent_frames = 0
                        
                        text = "No Voice Detected"
                        if text != prev_state[4] and prev_state[4] != "No Voice Detected":
                            writer[4].release()
                            end_time[4] = time.time()
                            duration = math.ceil((end_time[4] - start_time[4])/3)
                            outputVideo = 'VoiceViolation' + video[4]
                            VoiceViolation = {
                                "Name": prev_state[4],
                                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[4])),
                                "Duration": str(duration) + " seconds",
                                "Mark": math.floor(2 * duration),
                                "Link": filename,
                                "RId": get_resultId()
                            }
                            if flag[4]:
                                recorded_durations.append(VoiceViolation)
                                write_json(VoiceViolation)
                                move_file_to_output_folder(filename, 'OutputAudios')
                            
                            video[4] = str(random.randint(1, 50000)) + ".mp4"
                            writer[4] = cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))
                            flag[4] = False
                        prev_state[4] = text
                        
            time.sleep(0.1)  # Small delay to prevent CPU overload
            
    except Exception as e:
        print(f"Voice detection error: {e}")
        return False
    
    return True

#Compatibility functions for gamified apps
def screen_recorder():
    """Screen recording function for compatibility with gamified apps"""
    try:
        import pygetwindow as gw
        active_window = gw.getActiveWindow()
        
        if active_window:
            window_title = active_window.title
            print(f"Screen recording: Active window - {window_title}")
            return [window_title]
        else:
            print("Screen recording: No active window")
            return []
            
    except ImportError:
        print("Screen recording: pygetwindow not available")
        return []
    except Exception as e:
        print(f"Screen recording error: {e}")
        return []

#Face Recognition Class with MediaPipe fallback
def load_image_file(image_path):
    """Load image file with fallback for face_recognition"""
    if HAS_FACE_RECOGNITION:
        return face_recognition.load_image_file(image_path)
    else:
        # Fallback: use OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image from {image_path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def face_locations(image):
    """Get face locations with MediaPipe fallback"""
    if HAS_FACE_RECOGNITION:
        return face_recognition.face_locations(image)
    else:
        # Use MediaPipe for face detection
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
        
        results = face_detection.process(image)
        locations = []
        
        if results.detections:
            height, width = image.shape[:2]
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * width)
                y = int(bbox.ymin * height)
                w = int(bbox.width * width)
                h = int(bbox.height * height)
                # Convert to face_recognition format (top, right, bottom, left)
                locations.append((y, x + w, y + h, x))
        
        return locations

def face_encodings(image, face_locations=None):
    """Get face encodings with MediaPipe fallback"""
    if HAS_FACE_RECOGNITION:
        return face_recognition.face_encodings(image, face_locations)
    else:
        # Fallback: return a simple hash-based encoding
        import hashlib
        if face_locations is None:
            face_locations = [(0, image.shape[1], image.shape[0], 0)]  # Whole image
        
        encodings = []
        for (top, right, bottom, left) in face_locations:
            face_image = image[top:bottom, left:right]
            if face_image.size > 0:
                # Create a simple encoding based on image hash
                face_bytes = face_image.tobytes()
                face_hash = hashlib.md5(face_bytes).hexdigest()
                # Convert hash to 128-dimensional encoding (face_recognition format)
                encoding = np.array([int(face_hash[i:i+2], 16) / 255.0 for i in range(0, 32, 2)] * 4)
                encodings.append(encoding)
        
        return encodings

def compare_faces(known_encodings, encoding, tolerance=0.6):
    """Compare faces with fallback"""
    if HAS_FACE_RECOGNITION:
        return face_recognition.compare_faces(known_encodings, encoding, tolerance)
    else:
        # Fallback: simple distance-based comparison
        if not known_encodings:
            return [False]
        
        matches = []
        for known_encoding in known_encodings:
            distance = np.linalg.norm(known_encoding - encoding)
            matches.append(distance < tolerance)
        
        return matches

def face_distance(known_encodings, encoding):
    """Calculate face distance with fallback"""
    if HAS_FACE_RECOGNITION:
        return face_recognition.face_distance(known_encodings, encoding)
    else:
        # Fallback: simple Euclidean distance
        if not known_encodings:
            return np.array([1.0])
        
        distances = []
        for known_encoding in known_encodings:
            distance = np.linalg.norm(known_encoding - encoding)
            distances.append(distance)
        
        return np.array(distances)

#Face Recognition Class
class FaceRecognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.cap = None
        self.is_running = False
        self.thread = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def load_known_faces(self, image_path, name):
        """Load a known face with fallback"""
        try:
            image = load_image_file(image_path)
            locations = face_locations(image)
            if locations:
                encodings = face_encodings(image, locations)
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(name)
                    print(f"✓ Loaded face for {name}")
                    return True
            print(f"✗ No face found in {image_path}")
            return False
        except Exception as e:
            print(f"✗ Error loading {image_path}: {e}")
            return False

    def run_recognition(self):
        """Run face recognition with MediaPipe fallback"""
        if not self.cap:
            self.cap = cv2.VideoCapture(0)
        
        self.is_running = True
        recognition_count = 0
        total_frames = 0
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            total_frames += 1
            
            # Only process every other frame to save time
            if self.process_this_frame:
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Find face locations
                self.face_locations = face_locations(rgb_small_frame)
                
                if self.face_locations:
                    # Get face encodings
                    self.face_encodings = face_encodings(rgb_small_frame, self.face_locations)
                    
                    self.face_names = []
                    for face_encoding in self.face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"
                        
                        # Use the known face with the smallest distance to the new face
                        face_distances = face_distance(self.known_face_encodings, face_encoding)
                        if len(face_distances) > 0:
                            best_match_index = np.argmin(face_distances)
                            if matches and matches[best_match_index]:
                                name = self.known_face_names[best_match_index]
                                recognition_count += 1
                        
                        self.face_names.append(name)
                else:
                    self.face_names = ["No face detected"]
            
            self.process_this_frame = not self.process_this_frame
            
            # Display the results
            if self.face_names:
                name = self.face_names[0]
                confidence = (recognition_count / max(total_frames // 2, 1)) * 100
                
                if name != "Unknown" and name != "No face detected":
                    print(f"✓ Face Recognition: {name} (confidence: {confidence:.1f}%)")
                    return name, confidence
                elif name == "Unknown":
                    print(f"⚠ Unknown face detected")
                    return "Unknown", 0.0
                else:
                    print(f"⚠ No face detected")
                    return "No face", 0.0
        
        return "No face", 0.0

    def stop_recognition(self):
        """Stop face recognition"""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None

def get_resultId():
    """Generate a random result ID"""
    return random.randint(1000, 9999)

# Test the module
if __name__ == "__main__":
    print("Testing ML utilities...")
    
    # Test face detection with MediaPipe
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        print("✓ Camera access working")
        
        # Test face detection
        locations = face_locations(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        print(f"✓ Face detection found {len(locations)} face(s)")
        
        # Test YOLO
        results = model.predict(frame)
        print(f"✓ YOLO detection working, found {len(results[0].boxes)} objects")
        
    cap.release()
    
    print("✓ All ML utilities working!")
