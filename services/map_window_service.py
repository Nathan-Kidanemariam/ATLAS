import os
import webbrowser


class MapWindowService:
    """
    Handles opening the ATLAS map

    This service opens the HTML map inside the browser

    FEATURES:
        1. Opens local map
        2. Open browser
    """
    def start(self):
        """
        Opens the map

        Finds the saved HTML map
        and opens it with the browser
        """
        #Convert the maps path into a full path
        map_path = os.path.abspath("map/map.html")

        #opens the html file
        webbrowser.open(f"file:///{map_path}")


    def shutdown(self):
        pass