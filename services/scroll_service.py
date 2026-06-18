import pyautogui
import time

class ScrollService:

    def follow_tts(self, tts):

        while tts.is_speaking:

            # Small repeated wheel motions
            for _ in range(12):

                if not tts.is_speaking:
                    break

                pyautogui.scroll(-90)

                time.sleep(0.02)

            time.sleep(0.03)