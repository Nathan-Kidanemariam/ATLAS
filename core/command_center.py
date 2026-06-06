import datetime
import os
import re
from services.weather_service import WeatherService
from services.ai_service import AIService
from config import LATITUDE, LONGITUDE, LOCATION_NAME
from services.desktop_service import DesktopService
from services.vision_service import VisionService
from services.memory_service import MemoryService
from services.workspace_service import WorkspaceService
from services.screen_shot_service import ScreenService
import screen_brightness_control as sbc
from services.editor_service import EditorService
from services.home_service import HomeService
from services.spotify_service import SpotifyService
from services.settings_service import SettingsService

class CommandCenter:
    """
    Handles ATLAS commands

    This class takes the user's voice input as text
    and then decides what service should handle it

    FEATURES:
        1. Weather and time commands
        2. Desktop commands
        3. Room scanning
        4. Memory commands
        5. Workspace commands
        6. Screen analysis
        7. Coding mode
        8. Focus mode

    ARGS:
        state: used to control ATLAS modes
    """
    def __init__(self, state):
        """
        Sets up the command center

        Creates all services that ATLAS can use
        when dealing with user commands
        """

        #Creates main services used my commands
        self.ai = AIService()
        self.weather = WeatherService(LATITUDE, LONGITUDE, LOCATION_NAME)
        self.desktop = DesktopService()
        self.vision = VisionService()
        self.state = state
        self.memory = MemoryService()
        self.workspace = WorkspaceService()
        self.screen = ScreenService()
        self.editor = EditorService()
        self.confirm_action = None
        self.home = HomeService()
        self.settings = SettingsService()

        #Loads the feature settings
        self.features = self.settings.get("features", {})

        #Only loads Spotify if it is enabled from settings
        if self.features.get("spotify_enabled", True):
            self.spotify = SpotifyService(state)
        else:
            self.spotify = None

    def has_words(self, command, words):
        """
        Checks if a command contains any listed words
        Uses word matching so ATLAS does not
        accidentally match parts of other words

        ARGS:
            command (str): User command text
            words (list): Words or phrases to search for

        RETURNS:
            bool
        """

        #Clean the command first
        command = command.lower().strip()

        #Check each word as a full word match
        for word in words:
            re_pat = r"\b" + re.escape(word.lower()) + r"\b"

            if re.search(re_pat, command):
                return True

        return False

    def handle(self, text):
        """
        Handles the main user command

        Takes the user's speech text and routes it
        to the correct ATLAS service

        ARGS:
            text (str): User speech converted into text

        RETURNS:
            str: Response for ATLAS to speak
        """

        #Clean the command text
        command = text.lower().strip()

        #Confirmation action for some risky actions
        if "confirm" in command and self.confirm_action:
            action = self.confirm_action
            self.confirm_action = None

            return action()

        #Thermostat commands
        if "set thermostat to" in command:

            numbers = [int(word) for word in command.split() if word.isdigit()]

            if numbers:
                temp = numbers[0]

                self.home.set_temperature(temp)

                return f"Setting thermostat to {temp} degrees."

        if "make it cold" in command:
            temp = self.home.decrease_temperature(2)

            return f"Lowering temperature to {temp} degrees."

        if "make it warm" in command:
            temp = self.home.increase_temperature(2)

            return f"Raising temperature to {temp} degrees."

        if "thermostat status" in command:
            return self.home.report()

        #Status report command
        if "status report" in command:
            report = self.state.window.create_status_report()

            return report

        # Weather and time commands
        if self.has_words(command, ["weather", "temperature", "forecast"]):
            return self.weather_response()
        if self.has_words(command, ["time", "current time"]):
            return self.time_response()

        # Open websites or applications
        if command.startswith("open "):
            target = command.replace("open ", "", 1)

            if target in ["youtube", "google", "github"]:
                return self.desktop.open_website(target)

            return self.desktop.open_app(target)

        # Search the web
        if command.startswith("search for "):
            query = command.replace("search for ", "", 1)
            return self.desktop.google_search(query)

        if command.startswith("google "):
            query = command.replace("google ", "", 1)
            return self.desktop.google_search(query)

        # Room scan command
        if self.has_words(command, ["scan room", "analyze room", "scan zone"]):
            self.state.set("SCANNING")
            frame = self.state.window.gesture.get_latest_frame()
            result = self.vision.scan(frame)

            self.state.set_scan_results(result["objects"])

            return result["text"]

        # Memory commands
        if command.startswith("remember that "):
            note = command.replace("remember that ", "", 1)
            self.memory.remember(note)
            return "Memory updated."

        if command.startswith("my name is "):
            name = command.replace("my name is ", "", 1).title()
            self.memory.set_name(name)
            return f"Understood. I will remember your name is {name}."

        if "what do you remember" in command:
            return self.memory.get_summary()

        # Coding commands
        if "open coding setup" in command:
            return self.workspace.launch("jarvis")

        if command.startswith("open my ") and "project" in command:
            proj_name = command.replace("open my ", "").replace("project", "").strip()
            return self.workspace.launch(proj_name)

        if command.startswith("launch ") and "workspace" in command:
            proj_name = command.replace("launch ", "").replace("workspace ", "").strip()
            return self.workspace.launch(proj_name)

        if command.startswith("remember this project as "):
            name = command.replace("remember this project as ", "", 1).strip()
            folder = os.getcwd()
            return self.workspace.add_workspace(name, folder)

        if command.startswith("list my projects"):
            return self.workspace.find_projs()

        if command.startswith("add note"):
            parts = command.replace("add note", "", 1).split(" to ")

            if len(parts) == 2:
                todo = parts[0].strip()
                name = parts[1].strip()
                return self.workspace.add_todo(name, todo)

        if command.startswith("what are my ") and " todos" in command:
            workspace_name = command.replace("what are my ", "", 1).replace(" todos", "").strip()
            return self.workspace.get_todos(workspace_name)

        if command.startswith("clear ") and " todos" in command:
            workspace_name = command.replace("clear ", "", 1).replace(" todos", "").strip()
            return self.workspace.clear_list(workspace_name)

        if command.startswith("continue "):
            name = command.replace("continue ", "", 1).strip()
            launcher = self.workspace.launch(name)
            todo_list = self.workspace.get_todos(name)

            return f"{launcher}{todo_list}"

        # Screen debugging/analyzing commands
        if self.has_words(command, ["explain my screen","summarize my screen","what am i looking at"]):
            result = self.screen.take_screen_shot()

            return self.ai.ask(f"""You are ATLAS, a screen-aware assistant. text from the user's screen: {result["text"]} Explain what the user is looking at in simple, useful terms. Keep it concise. """)

        if self.has_words(command, ["what am i coding", "explain this code", "continue from here"]):
            result = self.screen.take_screen_shot()

            return self.ai.ask(f"""You are ATLAS, a coding assistant. text from the user's screen:{result["text"]} Identify what code/project the user appears to be working on. Explain what is happening. Suggest the next useful step. Keep it practical and short. """)

        if self.has_words(command, ["debug my screen", "fix this error", "explain this error"]):
            result = self.screen.take_screen_shot()
            self.state.set_screen_boxes(result["boxes"])

            return self.ai.ask(f"""You are ATLAS, a debugging assistant. text from the user's screen: {result["text"]} Find the main error. Explain the cause simply. Give exact fix steps. If code is involved, provide the corrected snippet. Keep it concise. """)

        # Coding mode setup
        if self.has_words(command, ["start coding mode", "activate coding mode", "enter coding mode", "coding mode"]):
            self.state.set("CODING")
            if hasattr(self.state, "window"):
                self.state.window.active_theme = "CODING"

            coding_settings = self.state.settings.get("coding_mode", {})
            brightness_drop = coding_settings.get("brightness", 20)
            open_spotify = coding_settings.get("open_spotify", True)
            open_stackoverflow = coding_settings.get("open_stackoverflow", False)
            proj_name = ""
            if "for" in command:
                proj_name = command.split("for", 1)[1].strip()

            workspace_response = self.workspace.launch(proj_name)

            spotify_response = ""
            if open_spotify and self.spotify:
                spotify_response = self.spotify.play_random_playlist()

            try:
                current = sbc.get_brightness(display=0)[0]

                lowered = max(25, current - brightness_drop)

                sbc.set_brightness(lowered)

                brightness_response = "Brightness adjusted for development mode."

            except Exception as e:
                print("[Brightness Error]", e)
                brightness_response = ""

            self.memory.remember("User started coding mode.")

            return (
                "Coding mode activated. "
                f"{workspace_response}. "
                f"{spotify_response}. "
                f"{brightness_response} "
                "Development environment ready."
            )

        # Live commands
        if "what should we work on" in command or "next task" in command:
            return self.workspace.get_todos("jarvis")

        if command.startswith("add task"):
            task = command.replace("add task", "", 1)
            return self.workspace.add_todo("jarvis", task)

        if "start live vision" in command or "turn on live vision" in command:
            self.vision.start_live_detection()
            return "Live vision activated."

        if "stop live vision" in command or "turn off live vision" in command:
            self.vision.stop_live_detection()
            self.state.set_scan_results([])
            return "Live vision deactivated."

        # Code writing command
        if command.startswith("write code for ") or command.startswith("show me a code snippet"):
            prompt = command

            code = self.ai.ask(f"""Generate only a clean code snippet for this request:{prompt} Rules: Code only and No explanation""")
            self.editor.smart_insert(code)

            return "I have inserted the code into the editor"

        # Spotify commands
        if "pause spotify" in command:
            return self.spotify.pause()

        if "play coding playlist" in command:
            return self.spotify.play_random_playlist()

        # Focus mode commands
        if self.has_words(command, ["focus mode", "enter focus mode", "activate focus mode"]):
            self.state.enter_focus()

            if hasattr(self.state, "window"):
                self.state.window.current_mode = "FOCUS"

            return "Focus mode activated."

        if self.has_words(command, ["exit focus mode", "leave focus mode"]):
            self.state.set("STANDBY")

            if hasattr(self.state, "window"):
                self.state.window.current_mode = "MAP"

            return (
                "Returning to normal interface."
            )

        # General AI response
        return self.ai.ask(
            text,
            context=self.memory.get_summary()
        )


    def weather_response(self):
        """
        Creates the weather response
        Gets current weather data and turns it
        into a simple spoken sentence
        :return:
        """
        weather = self.weather.get_weather()
        return (
            f"It is currently {weather['temperature']} degrees in "
            f"{weather['location']}, with wind around {weather['wind']} miles per hour."
        )

    def time_response(self):
        """
        Creates the time response

        Gets the current system time and formats it
        for ATLAS to speak
        """
        t_now = datetime.datetime.now()
        return f"The time is {t_now.strftime('%I:%M %p')}."

