import json
import os

class SettingsService:
    """
    Handles ATLAS settings

    This service loads the saved settings and
    gives default values if no settings file exists

    FEATURES:
        1. Load settings
        2. Default settings
        3. Read from settings file
    """
    def __init__(self, path="settings.json"):
        """
        Sets up the settings service

        Stores the settings file
        and loads saved values
        """
        self.path = path

        #Load settings from file
        self.data = self.load()

    def load(self):
        """
        Loads settings

        Returns the saved settings if they exist,
        Otherwise it creates default values

        RETURNS:
            dict
        """
        #Return default settings when no file exists
        if not os.path.exists(self.path):
            return{
                "ai_name": "ATLAS",
                "wake_words": ["atlas", "hey atlas"],
                "boot_time": 23.0,
                "voice_style": "calm",
                "coding_mode": {
                    "brightness_drop": 20,
                    "open_spotify": True,
                    "open_stackoverflow": False
                },
                "default_mode": "MAP"
            }

        #Load settings from JSON file
        with open(self.path, "r") as file:
            return json.load(file)

    def get(self, key, answer=None):
        """
        Gets a setting value

        Returns the saved value

        ARGS:
            key (str): Setting name
            answer: Value to return if missing

        RETURNS:
            Any
        """
        return self.data.get(key, answer)