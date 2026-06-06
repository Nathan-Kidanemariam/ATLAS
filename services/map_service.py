import os
import math

import requests
from PIL import Image

class MapService:
    """
    Handles the map download for ATLAS

    This service takes the user location and puts into the map,
    downloads the nearby location information, and combines them into
    one map image

    FEATURES:
    1. Conversion of Latitude and Longitude
    2. Map location downloading
    3. Caching the map
    4. Map image creation
    """
    def __init__(self, lat, lon, zoom=14, cache="assets/map_cache"):
        """
        Sets up the map service

        Stores the location, zoom level, and folder used to save the map
        """
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
        self.cache = cache

        #Make cache folder if it doesn't exist
        os.makedirs(cache, exist_ok=True)

    def latlon_to_tile(self, lat, lon, zoom):
        """
         Converts latitude and longitude into map tile numbers

        Online maps are made of small square tiles.
        This math finds which tile contains the user's location

        ARGS:
            lat (float): Latitude value
            lon (float): Longitude value
            zoom (int): Map zoom level

        RETURNS:
            tuple: Tile x and y position
        """

        #Converts latitude to radians for the map formula
        lat_r = math.radians(lat)

        #Number of tiles depends on the zoom level
        n = 2 ** zoom

        #find tile position from longitude and latitude
        x = int((lon + 180.0)/360.0 * n)
        y = int((1.0-math.log(math.tan(lat_r) + 1/ math.cos(lat_r)) / math.pi)/2.0 * n)

        return x, y

    def download_local_map(self, size=3):
        """
        Downloads and builds the map

        Gets the center tile, downloads any tiles that are nearby,
        and brings them together into one image

        ARGS:
            size (int): Number of tiles per side

        RETURNS:
            str: Saved local map image path
        """

        #Finds the tile that contains the user's location
        center_x, center_y = self.latlon_to_tile(self.lat, self.lon, self.zoom)

        #Creates blank image for all the map tiles
        f1 = Image.new("RGB", (256 * size, 256 * size))

        #This offset keeps the user's location near the center
        start = -(size//2)

        #Loop through all the nearby tiles
        for d in range(start, start + size):
            for dy in range(start, start + size):
                x = center_x + d
                y = center_y + dy
                path = f"{self.cache}/{self.zoom}_{x}_{y}.png"

                #Download tile only if it is not already cached
                if not os.path.exists(path):
                    #open tile image
                    url = f"https://tile.openstreetmap.org/{self.zoom}/{x}/{y}.png"

                    headers = {
                        "User-Agent": "JarvisAIProject/1.0"
                    }
                    r = requests.get(url, headers=headers, timeout=10)
                    r.raise_for_status()

                    with open(path, "wb") as f:
                        f.write(r.content)

                #Place tile into the full map image
                tile = Image.open(path).convert("RGB")
                p1 = (d - start) * 256
                p2 = (dy - start) * 256
                f1.paste(tile, (p1, p2))

            output =  f"{self.cache}/local_map.png"

            #Save the completed map image
            f1.save(output)

            return output

