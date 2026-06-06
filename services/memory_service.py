import json
import os

class MemoryService:
    """
    Handles the memory for ATLAS

    This service stores the user's information
    and loads it again when ATLAS starts

    FEATURES:
        1. Save user name
        2. Store notes
        3. Store preferences
        4. Save projects
    """
    def __init__(self, path="memory.json"):
        """
        Sets up the memory service

        Stores the file path and loads saved memory values
        :param path:
        """
        self.path = path

        #load the existing memory
        self.data = self.load()

    def load(self):
        """
        Loads the saved memory

        Creates default values if no memory file exists

        RETURNS:
            dict
        """
        if not os.path.exists(self.path):
            return {
                "name": None,
                "projects" : [],
                "preferences": {},
                "notes": []
            }
        with open(self.path, "r") as file:
            return json.load(file)

    def save(self):
        """
        Saves memory

        Writes current memory values into the JSON files
        """
        with open(self.path, "w") as file:
            #save memory with indentation to make the file easier to read
            json.dump(self.data, file, indent=4)

    def remember(self, note):
        """
        Stores a new note

        Adds the note and saves memory

        ARGS:
            note (str): Note to save
        """

        #Add note to memory
        self.data["notes"].append(note)
        self.save()

    def set_name(self, name):
        """
        Stores the user's name

        ARGS:
            name (str): Username
        """
        self.data["name"] = name
        self.save()

    def get_summary(self):
        """
        Returns memory as a string

        Converts memory into a string
        so ATLAS can speak

        RETURNS:
            str
        """
        return json.dumps(self.data, indent=2)
