import time
import requests

class WeatherService:
    """
    Gets weather information for ATLAS

    This service requests weather data
    and stores the values to avoid
    unnecessary API requests

    FEATURES:
        1. Current weather
        2. Weather caching
        3. Location
        4. Offline mode
    """
    def __init__(self, latitude, longitude, location_name="Current Loc"):
        """
        Sets up the weather service

        Stores the location values
        and weather caching

        ARGS:
            latitude (float): Location latitude
            longitude (float): Location longitude
            location_name (str): Display location
        """
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name

        self.cached_weather = None
        self.last_update = 0

        #Only update weather every 10 minutes
        self.update_interval = 600

    def get_weather(self):
        """
        Gets current weather

        Returns cached weather if it was updated recently.
        Otherwise requests new weather data

        RETURNS:
            dict
        """

        #Get current time
        time_now = time.time()

        #Return saved weather if chace is still valid
        if self.cached_weather and time_now - self.last_update < self.update_interval:
            return self.cached_weather

        try:
            url = "https://api.open-meteo.com/v1/forecast"
            #Weather values that are requested from Open Meteo
            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "current": "temperature_2m,precipitation,wind_speed_10m",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto"
            }

            #Request weather data
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            #Get only the current weather section
            current = data["current"]

            #Save the weather to reduce how many requests are made
            self.cached_weather = {
                "location": self.location_name,
                "temperature": round(current["temperature_2m"]),
                "precipitation": current["precipitation"],
                "wind": round(current["wind_speed_10m"]),
                "updated": current["time"]
            }

            #Keep track of the last update
            self.last_update = time_now
            return self.cached_weather

        except Exception as e:
            print("ERROR: ", e)

            #Use saved weather if available so ATLAS still has data
            if self.cached_weather:
                return self.cached_weather

            #Return empty values otherwise
            return {
                "location": self.location_name,
                "temperature": "--",
                "precipitation": "--",
                "wind": "--",
                "updated": "Unavailable"
            }