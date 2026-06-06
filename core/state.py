import time

class JarvisState:

    """
    Stores the current ATLAS state

    This class acts like the main memory system
    for ATLAS and keeps track of things like assistant mode,
    scan results, music, and screen debugging data

    STATES:
        1. IDLE: DEFAULT STATE
        2. LISTENING: WAITING FOR COMMANDS
        3. THINKING: PROCESSING COMMANDS
        4. SPEAKING: RESPONDING TO COMMANDS
        5. SCANNING: RUNNING SCAN MODE
        6. STANDBY: NO ACTIVITY MODE
        7. FOCUS: FOCUS MODE

    FEATURES:
        1. Tracks the state
        2. Saves the scan result
        3. Tracks the music
        4. Stores screen information
    """
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    SCANNING = "SCANNING"
    STANDBY = "STANDBY"
    FOCUS = "FOCUS"

    def __init__(self):
        """
        Sets up the ATLAS state

        creates default values used across the system
        """
        self.current = self.IDLE
        self.scan_results = []
        self.scan_time = 0

    def set(self, state):
        """
        Changes the state

        ARGS:
             state(str): New state
        """
        #Convert to uppercase to match the styles
        self.current = state.upper()

    def set_scan_results(self, results):
        """
        Stores the scan results
        saves the latest detected objects and records when they were found

        ARGS:
             results (list): Detected objects
        """
        self.scan_results = results
        self.scan_time = time.time()

    def scan_results_active(self, duration=6):
        """
        Checks if scanning results should still be on screen

        Results expire after a short amount of time

        ARGS:
            duration (int): maximum time item can be displayed

        RETURNS:
            bool
        """
        return self.scan_results and time.time() - self.scan_time < duration

    def get_scan_results(self):
        """
        Returns the latest scan results
        """
        return self.scan_results

    def get(self):
        return self.current

    def set_music(self, title="", source="", status="STOPPED"):
        """
        Stores the music information

        saves the track title, source, and playback

        ARGS:
            title (str): Track name
            source (str): Music source
            status (str): Playback state
        """
        self.music = {"title": title, "source": source, "status": status}

    def get_music(self):
        """
        Returns current music information
        Uses default values if nothing is currently playing
        """
        return getattr(self, "music", {"title": "No Track Selected", "source": "SPOTIFY", "STATUS": "IDLE"})

    def set_screen_boxes(self, boxes):
        """
        Saves the detected screen sections and keeps track of when they were updated
        ARGS:
             boxes (list): Screen sections
        """
        self.screen_boxes = boxes
        self.screen_box_time = time.time()

    def get_screen_boxes(self):
        """
        Returns the screen sections
        """
        return getattr(self, "screen_boxes", [])

    def enter_focus(self):
        """
        Switches ATLAS into focus mode
        :return:
        """
        self.current = self.FOCUS
