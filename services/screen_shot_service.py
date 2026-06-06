import pyautogui
import pytesseract

class ScreenService:
    """
    Handles screen debugging/analysis for ATLAS

    This service takes screenshots, reads text from screen,
    and finds any errors in code

    FEATURES:
        1. Screenshot
        2. Reads Text from screen
        3. Finds errors
        4. Generates boxes around the errors
    """
    def __init__(self):
        """
        Sets up the screen service

        Stores the tesseract path used for text recognition
        """
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def take_screen_shot(self):
        """
        Takes a screenshot, extracts text, and finds
        any erros

        RETURNS:
            dict
        """

        #Take screenshot of current screen
        screenshot = pyautogui.screenshot()

        #Extract text by converting the image into text
        text = pytesseract.image_to_string(screenshot)

        #find errors
        boxes = self.get_error_boxes(screenshot)

        #if nothing was found give default answer
        if not text.strip():
            return {
                "text": "I couldn't read any text from the screen",
                "raw" : "",
                "boxes": []
            }

        return {
            #Limit the length we can display
            "text": text[:4000],
            "raw": text,
            "boxes": boxes
        }

    def get_error_boxes(self, screenshot):
        """
        Finds any possible errors

        Looks through detected words and highlights
        words that match the detected words

        ARGS:
            screenshot: Captured screen image

        RETURNS:
            list
        """

        #Get data from the image
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

        #Words commonly founded in errors
        error_words = ["error", "exception", "traceback", "failed", "undefined", "invalid", "not", "missing", "denied", "cannot", "warning"]
        boxes = []

        #Check each detected word
        for i, word in enumerate(data["text"]):
            word2 = word.lower().strip()

            #Ignore empty results
            if not word2:
                continue

            #Match any possible error words
            if any(e in word2 for e in error_words):
                #store the word and the location
                boxes.append({"text": word, "x": data["left"][i],  "y": data["top"][i], "w": data["width"][i], "h": data["height"][i]})


        return boxes