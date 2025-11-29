import cv2
import mediapipe as mp
import pyautogui
import time
import threading
from utils import map_coordinates, calculate_distance, smooth_coordinates

# Global variables for thread communication
frame_lock = threading.Lock()
current_frame = None
running = True

def gesture_processing_thread():
    global current_frame, running
    
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    # Initialize Webcam
    cap = cv2.VideoCapture(0)
    
    # Screen dimensions
    screen_w, screen_h = pyautogui.size()
    
    # PyAutoGUI Optimization
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = False
    
    # Variables for smoothing
    prev_screen_x, prev_screen_y = 0, 0
    smoothing_factor = 0.2
    
    # Click state
    clicking = False
    
    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=1
    ) as hands:
        
        while running and cap.isOpened():
            success, image = cap.read()
            if not success:
                continue

            # Flip and convert
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)

            # Draw annotations
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get landmarks
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    
                    # Map coordinates
                    h, w, _ = image.shape
                    target_x, target_y = map_coordinates(
                        index_tip.x, index_tip.y, w, h, screen_w, screen_h
                    )
                    
                    # Smooth movement
                    curr_screen_x, curr_screen_y = smooth_coordinates(
                        target_x, target_y, prev_screen_x, prev_screen_y, smoothing_factor
                    )
                    
                    # Move mouse
                    pyautogui.moveTo(curr_screen_x, curr_screen_y)
                    prev_screen_x, prev_screen_y = curr_screen_x, curr_screen_y
                    
                    # Check for click
                    distance = calculate_distance(index_tip, thumb_tip)
                    click_start_threshold = 0.05 
                    click_stop_threshold = 0.06
                    
                    if distance < click_start_threshold:
                        if not clicking:
                            pyautogui.mouseDown()
                            clicking = True
                    elif distance > click_stop_threshold:
                        if clicking:
                            pyautogui.mouseUp()
                            clicking = False
                            
                    if clicking:
                        cv2.circle(image, (int(index_tip.x * w), int(index_tip.y * h)), 15, (0, 255, 0), cv2.FILLED)
            else:
                if clicking:
                    pyautogui.mouseUp()
                    clicking = False
            
            # Update global frame safely
            with frame_lock:
                current_frame = image.copy()
                
    # Cleanup
    if clicking:
        pyautogui.mouseUp()
    cap.release()

def main():
    global running
    print("Hand Gesture Controller Started. Press 'Esc' to exit.")
    
    # Start processing thread
    t = threading.Thread(target=gesture_processing_thread)
    t.daemon = True
    t.start()
    
    # Main GUI loop
    while True:
        with frame_lock:
            if current_frame is not None:
                cv2.imshow('Hand Gesture Controller', current_frame)
        
        # Wait for Esc key
        if cv2.waitKey(5) & 0xFF == 27:
            running = False
            break
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
