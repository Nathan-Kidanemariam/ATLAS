import pyperclip
import pyautogui
import time

class EditorService:
    """
    Handles writing code into the editor

    This service inserts generated code
    either by typing or by pasting
    depending on the size

    FEATURES:
        1. Type code
        2. Paste code
        3. Chooses to type or paste
        """
    def type_code(self, code, delay=0.01):
        """
        Types code directly

        Simulates keyboard input
        for shorter lines of code

        ARGS:
            code (str): Code to insert
            delay (float): Delay between characters

    RETURNS:
        str: Status message
        """
        pyautogui.write(code, interval=delay)
        return "Typing complete"

    def paste_code(self, code):
        """
        Pastes code into the editor

        Copies code to the clipboard
        and pastes it automatically

        ARGS:
            code (str): Code to insert

        RETURNS:
            str: Status message
        """
        pyperclip.copy(code)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        return "Paste complete"

    def smart_insert(self, code):
        """
        Inserts code automatically

        Uses typing for shorter code
        and pasting for larger snippets

        ARGS:
            code (str): Code to insert

        RETURNS:
            str: Status message
        """
        if len(code) < 220:
            return self.type_code(code)

        return self.paste_code(code)