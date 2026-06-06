import threading
import time
import speech_recognition as sr
from services.tts_service import TTSService
from core.command_center import CommandCenter
from services.settings_service import SettingsService

class VoiceController:
    """
    Handles the ATLAS voice system

    This class listens for wake words, activates command mode,
    sends commands to the command center, speaks responses back
    through the text to speech service

    TASK FLOW:
        1. Wait for the wake word
        2. Listen for the command
        3. Send command to command center for processing
        4. Speak the response given by the command center
        5. Return back to standby state

    ARGS:
        state: used to get the current mode
    """
    def __init__(self, state):

        """
        Sets up the voice controller
        Creates the microphone, recognizer, text to speech service,
        command center, settings, and background listening thread
        :param state:
        """
        self.state = state
        self.running = True
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.tts = TTSService(state)
        self.center = CommandCenter(state)
        self.settings = SettingsService()

        #Loads wake words from settings
        #Uses default wake words if none are saved
        self.wake_words = self.settings.get("wake_words", ["atlas", "hi", "hello", "hey atlas"])
        self.thread = threading.Thread(target=self.listen_loop, daemon=True)

        #start listening in a background thread
        self.thread.start()
        self.window = None

    def update(self, delta_time, total_time):
        pass

    def draw(self, screen):
        pass

    def listen_loop(self):
        """
        Main voice listening loop

        waits for a wake word, then listens for the next words as a command

        This loop runs in the background while ATLAS is active
        :return:
        """

        #Makes sure the mic filters out extra background noise
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)

        wake_words = self.wake_words
        activated = False

        #Start in standby mode
        self.state.set("STANDBY")

        while self.running:
            try:
                #skip listening while ATLAS is speaking
                if self.tts.is_speaking:
                    time.sleep(0.1)
                    continue

                #Listen through the microphone
                with self.mic as source:
                    audio = self.recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=18
                    )

                text = self.recognizer.recognize_google(audio).lower()

                # Wake word mode
                if not activated:
                    if any(word in text for word in wake_words):
                        activated = True
                        self.state.set("LISTENING")

                        self.tts.speak("Yes?")

                        while self.tts.is_speaking:
                            time.sleep(0.1)
                    else:
                        self.state.set("STANDBY")

                    continue

                # Command mode
                self.state.set("THINKING")

                #Handle gesture commands separately
                #because they control the main window
                if "turn on gesture" in text or "activate gesture" in text:
                    response = self.window.start_gesture_control()
                elif "turn off gesture" in text or "deactivate gesture" in text:
                    response = self.window.stop_gesture_control()
                #send any other command to the command center
                else:
                    response = self.center.handle(text)
                self.tts.speak(response)

                while not self.tts.is_speaking:
                    time.sleep(0.05)

                while self.tts.is_speaking:
                    time.sleep(0.1)

                activated = False
                self.state.set("STANDBY")

            except sr.WaitTimeoutError:
                if not self.tts.is_speaking:
                    self.state.set("STANDBY")

            except sr.UnknownValueError:
                if not self.tts.is_speaking:
                    self.state.set("STANDBY")

            except Exception as e:
                if not self.tts.is_speaking:
                    self.state.set("STANDBY")
                time.sleep(1)

    def shutdown(self):
        """
        Stops ATLAS from listening and shuts down TTS
        """
        self.running = False
        self.tts.shutdown()
