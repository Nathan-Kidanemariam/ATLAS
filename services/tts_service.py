import asyncio
import threading
import queue
import tempfile
import os

import pygame
import edge_tts
import pyttsx3


class TTSService:
    """
    Handles text to speech for ATLAS

    This service takes response text,
    places it into a speech queue,
    and plays it using Edge TTS

    If Edge TTS fails, it falls back
    to the offline pyttsx3 voice

    FEATURES:
        1. Speech queue
        2. Background speech thread
        3. Edge TTS voice
        4. Offline fallback voice
        5. ATLAS speaking state
    """
    def __init__(self, state):
        """
        Sets up the TTS service

        Creates the speech queue, starts the mixer,
        and runs the voice worker in the background
        """

        self.state = state

        #Queue stores text waiting to be spoken
        self.queue = queue.Queue()
        self.running = True

        #Tracks if ATLAS is currently speaking
        self.is_speaking = False

        #Voice used by Edge TTS
        self.voice = "en-GB-RyanNeural"

        #Start pygame mixer if it is not already running
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        #Start speech worker in the background
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def speak(self, text):
        """
         Adds text to the speech queue

         ARGS:
             text (str): Text for ATLAS to say
         """

        #Only add real text to the queue
        if text:
            self.queue.put(text)

    def worker(self):
        """
        Runs the speech loop

        Waits for text in the queue,
        speaks it, and then waits
        for the next message
        """

        while self.running:
            #Wait for text from the queue
            text = self.queue.get()

            #None is used to stop the worker
            if text is None:
                break

            self.is_speaking = True

            #Set ATLAS to speaking mode
            self.state.set("SPEAKING")

            try:
                #Try online Edge TTS first
                asyncio.run(self._speak_edge(text))

            except Exception as e:
                #Go offline if edge fails
                self.speak_fallback(text)

            self.is_speaking = False

            #Set ATLAS back to idle after it finishes speaking
            self.state.set("IDLE")

    async def _speak_edge(self, text):
        """
        Speaks text using Edge TTS

        Saves speech as a temporary mp3,
        plays it through pygame,
        then deletes the file

        ARGS:
            text (str): Text for ATLAS to say
        """

        #Create Edge TTS speech request
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate="-5%",
            pitch="-5Hz"
        )

        #Create a temporary mp3 file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_path = temp_audio.name

        #Save speech to the file
        await communicate.save(temp_path)

        #Play the audio file
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()

        #Wait until the audio finishes
        while pygame.mixer.music.get_busy():
            pygame.time.wait(50)

        #Unload the audio so the file can be deleted
        pygame.mixer.music.unload()

        #Delete the audio file
        try:
            os.remove(temp_path)
        except:
            pass

    def speak_fallback(self, text):
        """
        Speaks text using offline TTS

        Used when Edge TTS fails
        or internet speech is unavailable

        ARGS:
            text (str): Text for ATLAS to say
        """

        try:
            #Create offline engine
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")

            for voice in voices:
                name = voice.name.lower()
                voice_id = voice.id.lower()

                #Try to pick and english or british voice
                if "british" in name or "uk" in name or "english" in name or "gb" in voice_id:
                    engine.setProperty("voice", voice.id)
                    break

            #Set the speed and volume
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 1.0)

            #Speak
            engine.say(text)
            engine.runAndWait()
            engine.stop()

        except:
            pass

    def shutdown(self):
        """
        Shuts down the TTS service

        Stops the worker loop and sends
        None to unblock the speech queue
        """
        self.running = False
        self.queue.put(None)
