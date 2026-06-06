import cv2
import time
import threading
import mediapipe as mp
import copy


class HandTrackingService:
    """
    Handles hand tracking for ATLAS

    This service uses the webcam and MediaPipe
    to detect hand position, pinch gestures,
    open palm, fist, and pointing

    FEATURES:
        1. Webcam hand tracking
        2. Gesture detection
        3. Stores the latest frame
        4. Camera loop

    Gestures:
        PINCH:  thumb and index finger are close
        FIST:   all fingers are curled
        OPEN PALM: all fingers are raised
        POINT:   One finger pointing

    NOTES:
        Threshold values were tuned manually
        They might need some small changes depending on camera distance,
        lighting, hand size, and camera quality

    """
    def __init__(self):
        """
        Sets up hand tracking

        Starts the camera loop in the background thread
        and stores the latest hand data for the rest of ATLAS to use
        """
        self.running = True

        #Default hand data before anything is detected
        self.latest = {"hand_visible": False, "x": 0, "y": 0, "pinching": False, "gesture": "NONE"}

        #Starts the camera tracking in the background
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        self.latest_frame = None
        self.lock = threading.Lock()

    def run(self):
            self.run_camera()

    def run_camera(self):
        """
        Ruins the camera tracking

        Opens the camera, reads the frames, finds the hand landmarks,
        and updates the latest gesture
        """

        #Create the MediaPipe hand detector
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.65, min_tracking_confidence=0.65)

        # Open the camera
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return

        # Set camera size for consistent tracking
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Read camera frames while ATLAS is running
        while self.running:
            success, frame = cap.read()

            if not success:
                time.sleep(0.05)
                continue

            # Flip frame so movement feels natural like a mirror
            frame = cv2.flip(frame, 1)
            with self.lock:
                # Save latest frame for other services like vision scan
                self.latest_frame = frame.copy()

            # Convert image because MediaPipe uses RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process frame through MediaPipe
            result = hands.process(rgb)

            # If a hand is detected, read landmark points
            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                landmarks = hand.landmark
                point = []

                # Store landmark points for drawing/debugging
                for landm in landmarks:
                    point.append({"x": landm.x,"y": landm.y})

                # Use index finger as the main position
                index_tip = landmarks[8]
                thumb_tip = landmarks[4]

                x = index_tip.x
                y = index_tip.y

                # Measure distance between thumb and index finger for pinching
                # Use distance formula between thumb and index finger
                # This helps detect pinch gestures
                pinch_distance = ((index_tip.x - thumb_tip.x) ** 2 +(index_tip.y - thumb_tip.y) ** 2) ** 0.5

                # 0.055 means the thumb and index finger are close enough
                # to count as a pinch
                pinching = pinch_distance < 0.055
                fingers = self.fingers_up(landmarks)

                # Choose the strongest matching gesture
                if pinching:
                    gesture = "PINCH"
                elif self.is_fist(landmarks):
                    gesture = "FIST"
                elif all(fingers):
                    gesture = "OPEN_PALM"
                else:
                    gesture = "POINT"

                # Save latest hand data
                self.latest = {"hand_visible": True, "x": x, "y": y, "pinching": pinching, "gesture": gesture, "points": point}

            else:
                # If no hand is visible, reset hand data
                self.latest = {"hand_visible": False, "x": 0, "y": 0, "pinching": False, "gesture": "NONE", "points": []}
            time.sleep(0.02)

        cap.release()
        hands.close()

    def get_latest(self):
        return self.latest

    def shutdown(self):
        self.running = False

    def fingers_up(self, landmarks):
        """
        Checks which fingers are raised

        Compares each finger tip to the lower finger
        to see whether or not that finger is up

        ARGS:
            landmarks: MediaPipe hand landmarks

        RETURNS:
            list: True or False values for each finger
        """

        #Index, middle, right, and pinky finger tip points
        finger_tip = [8, 12, 16, 20]
        #Lower finger points for comparison
        p = [6, 10, 14, 18]

        fingers = []
        #if the fingertip is higher on the screen the finger is counted as raised
        for finger_tips, p2 in zip(finger_tip, p):
            fingers.append(landmarks[finger_tips].y < landmarks[p2].y)

        return fingers

    def reset_latest(self):
        self.latest = {"hand_visible": False, "x": 0, "y": 0, "pinching": False, "gesture": "NONE", "points": []}

    def get_latest_frame(self):
        with self.lock:
            if self.latest_frame is None:
                return None
            return self.latest_frame.copy()

    def is_fist(self, landmarks):
        """
        Checks if the hand is making a fist

        Counts how many fingers are curled.
        If all four fingers are curled,
        ATLAS treats the gesture as a fist

        ARGS:
            landmarks: MediaPipe hand landmarks

        RETURNS:
            bool
        """

        #Finger tips and lower finger points
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]

        #Does not count pinching as a fist
        pinch_distance = ((index_tip.x - thumb_tip.x) ** 2 +(index_tip.y - thumb_tip.y) ** 2) ** 0.5

        # 0.075 prevents a tight pinch from being mistaken as a fist
        if pinch_distance < 0.075:
            return False

        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]

        # Count how many fingers are curled
        curled_count = 0

        for tip, pip in zip(finger_tips, finger_pips):
            # 0.05 gives the finger room to bend before counting it as curled
            if landmarks[tip].y > landmarks[pip].y + 0.05:
                curled_count += 1

        # If all fingers are curled, return True
        return curled_count == 4