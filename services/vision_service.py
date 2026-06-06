import time
import threading
from ultralytics import YOLO


class VisionService:
    """
    Handles object detection for ATLAS

    This service uses YOLO to detect objects
    from camera frames and returns object names,
    confidence values, and screen boxes

    FEATURES:
        1. Load YOLO model
        2. Single frame scanning
        3. Live object detection
        4. Store latest detected objects
    """

    def __init__(self):
        """
        Sets up the vision service

        Loads the YOLO model and prepares
        values used for live detection
        """

        #Load the YOLO model
        self.model = YOLO("yolov8n.pt")

        #Tracks if live detection is running
        self.running = False

        #Stores latest objects from scan
        self.latest_objects = []

        self.latest_frame = None

        #Used to safely share the data between the vision thread and main program
        self.lock = threading.Lock()

        self.thread = None

    def live_loop(self):
        """
        Runs the live object detection

        Continuously gets camera frames,
        scans them with YOLO, and stores
        the latest detected objects
        """

        while self.running:

            #Get latest frame from camera
            frame = self.frame_provider()

            #Wait if no frame is available yet
            if frame is None:
                time.sleep(0.05)
                continue

            try:
                #Use Yolo on the frame
                results = self.model(frame, verbose=False)

                detected = []

                for result in results:
                    for box in result.boxes:

                        cls_id = int(box.cls[0])
                        name = self.model.names[cls_id]

                        conf = float(box.conf[0])

                        #ignore low confidence detections
                        if conf < 0.45:
                            continue

                        x1, y1, x2, y2 = box.xyxy[0]

                        #Store the detected objects
                        detected.append({"name": name, "confidence": round(conf, 2),"box": (int(x1), int(y1), int(x2), int(y2))})

                with self.lock:
                    self.latest_objects = detected

            except Exception as e:
                print("[Vision Error]", e)

            #Small delay to avoid overloading the CPU
            time.sleep(0.08)

    def get_live_objects(self):
        """
        Returns latest live objects

        RETURNS:
            list
        """
        with self.lock:
            return list(self.latest_objects)

    def scan(self, frame=None):
        """
        Scans one camera frame

        Used when ATLAS needs a quick
        object detection result

        ARGS:
            frame: Camera frame to scan

        RETURNS:
            dict
        """

        #Return default if no frame exists
        if frame is None:
            return {
                "text": "I do not have a camera frame yet.",
                "objects": []
            }

        #Run YOLO on the frame
        results = self.model(frame, verbose=False)

        #Gather all the detected objects
        detected = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                name = self.model.names[cls_id]
                conf = float(box.conf[0])

                #Ignore detections that are below 45%
                if conf < 0.45:
                    continue

                x1, y1, x2, y2 = box.xyxy[0]

                #Save the object name, confidence, and box
                detected.append({"name": name, "confidence": round(conf, 2), "box": (int(x1), int(y1), int(x2), int(y2))})

        #Return default if nothing was detected
        if not detected:
            return {
                "text": "I did not detect any objects.",
                "objects": []
            }

        #Gather all the object names
        names = []
        for obj in detected:
            if obj["name"] not in names:
                names.append(obj["name"])

        items = ", ".join(names[:5])

        #Speak only the first few objects
        return {
            "text": f"I have detected {items}.",
            "objects": detected[:8]
        }

    def start_live_detection(self, frame_provider=None):
        """
        Starts live object detection

        Uses a frame provider to get camera frames
        and starts detection in the background

        ARGS:
            frame_provider: Function that returns camera frames
        """

        #Do nothing if it's already running
        if self.running:
            return

        #Save the frame provider if there is none
        if frame_provider is not None:
            self.frame_provider = frame_provider

        #Stop if there is no camera frame source
        if self.frame_provider is None:
            return

        self.running = True

        #Start the live thread
        self.thread = threading.Thread(target=self.live_loop,daemon=True)
        self.thread.start()

    def stop_live_detection(self):
        """
        Stops live object detection

        Clears stored object results
        """
        self.running = False

        with self.lock:
            self.latest_objects = []

    def shutdown(self):
        """
        Shuts down the vision service
        """
        self.running = False
