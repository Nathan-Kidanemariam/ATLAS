import random
import time

import pyautogui
import subprocess
from dotenv import load_dotenv

load_dotenv()
class SpotifyService:
    """
    Handles Spotify music for ATLAS

    This service opens Spotify links
    and controls playback

    FEATURES:
        1. Saved playlist links
        2. Random playlist selection
        3. Playlist opening
        4. Pause
    """
    def __init__(self, state=None):
        """
        Sets up the Spotify service

        Stores the ATLAS state and saved playlist links
        """
        self.state = state

        #Saved Spotify playlists and albums
        self.playlists = [
            "https://open.spotify.com/playlist/2bN6P9stLuQJHJg1A8dted?si=d302b04a1c2b447a",
            "https://open.spotify.com/album/5H93crLOLbd6qV4nAD6iop?si=74e345b146344638",
            "https://open.spotify.com/album/4EVEPI1V6dWOEw2wN1ghmJ?si=e6c40ffbe0a3418d"
        ]

    def play_random_playlist(self):
        """
        Opens a random Spotify playlist

        Used mostly for coding mode to start background music

        RETURNS:
            str
        """

        #Return if no playlists are saved
        if not self.playlists:
            return "No playlists have been added"

        #Pick a random playlist
        playlist = random.choice(self.playlists)

        #Update ATLAS music state
        if self.state:
            self.state.set_music(title="Coding playlist", source='SPOTIFY', status="PLAYING")

        #Open link
        subprocess.Popen(f"start {playlist}", shell=True)

        #Wait for Spotify to load
        time.sleep(5)

        #Press space to play
        pyautogui.hotkey("space")

        return "Opening random playlist"

    def play_playlist(self, index):
        """
        Opens a playlist by index

        Used when ATLAS needs to play
        a specific saved playlist

        ARGS:
            index (int): Playlist position in the list

        RETURNS:
            str
        """
        try:
            playlist = self.playlists[index]

            subprocess.Popen(f"start {playlist}", shell=True)

            time.sleep(5)

            pyautogui.hotkey("space")

            return "Opening playlist"
        except:
            return "Playlist not found"

    def pause(self):
        """
        Pauses or resumes Spotify

        Presses space through PowerShell

        RETURNS:
            str
        """
        subprocess.Popen(
            'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys(\' \')"',
            shell=True
        )
        return "Music Paused"