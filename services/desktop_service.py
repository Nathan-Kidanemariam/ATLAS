import os
import webbrowser
import subprocess

class DesktopService:
    """
    Handles any desktop commands for ATLAS

    This service opens apps, websites, searches the internet,
    and opens coding terminals

    FEATURES:
        1. Opens apps
        2. Opens websites
        3. Google Search
        4. Opens Spotify
        5. Opens coding terminals
    """
    def open_app(self, app_name):
        """
        Opens Desktop apps

        Matches the users request and opens the correct app

        ARGS:
            app_name (str): Name of the app

        RETURNS:
        str: Status
        """

        #Clean up the app name
        app = app_name.lower().strip()

        #Opens up apps that match what the user wants
        #returns an error if failure
        try:
            if "chrome" in app:
                subprocess.Popen("start chrome", shell=True)
                return "Opening Chrome"

            if "edge" in app:
                subprocess.Popen("start msedge", shell=True)
                return "Opening Microsoft Edge."

            if "vs code" in app or "visual studio code" in app or "code" in app:
                subprocess.Popen("code", shell=True)
                return "Opening Visual Studio Code."

            if "file explorer" in app or "files" in app:
                subprocess.Popen("explorer", shell=True)
                return "Opening File Explorer."

            if "notepad" in app:
                subprocess.Popen("notepad", shell=True)
                return "Opening Notepad."

            return "I do not recognize that application yet."

        except Exception as e:
            return "I could not open that application."

    def open_website(self, site):
        """
        Opens websites

        supports common websites as well as direct input

        ARGS:
            site (str): Website name or link

        RETURNS:
            str: Status
        """
        site = site.lower().strip()

        #Opens the common websites
        if "youtube" in site:
            webbrowser.open("https://www.youtube.com")
            return "Opening Youtube"

        if "google" in site:
            webbrowser.open("https://www.google.com")
            return "Opening Google."

        if "github" in site:
            webbrowser.open("https://www.github.com")
            return "Opening GitHub."

        #Opens any custom links
        webbrowser.open(site)
        return "Opening the website."

    def google_search(self, query):
        """
         Searches Google

         Converts the search text
         into a browser search URL

        ARGS:
            query (str): Search text

        RETURNS:
            str: Status
         """

        #replaces spaces for the format of the URL
        url = "https://www.google.com/search?q=" + query.replace(" ", "+")
        webbrowser.open(url)
        return f"Searching Google for {query}."

    def open_spotify(self):
        """
        Opens Spotify

        Uses the desktop protocol
        to launch the application

        RETURNS:
            str: Status message
        """
        try:
            subprocess.Popen("start spotify: ", shell=True)
            return "Spotify Opened"
        except Exception as e:
            return "I could not open Spotify"

    def open_coding_tabs(self):
        """
        Opens coding websites
        RETURNS:
        str: Status message
        """
        webbrowser.open("https://stackoverflow.com")
        webbrowser.open("https://github.com")
        return "Coding Tabs Opened"
