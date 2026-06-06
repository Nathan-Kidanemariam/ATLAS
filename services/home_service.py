import requests
import os

class HomeService:
    """
    Handles the smart home controls for ATLAS

    This service connects to Home Assistant and allows ATLAS
    to read and control thermostat settings

    FEATURES:
        1. Read home states
        2. Read temperature values
        3. Change Temperature
        4. Chang HVAC mode
        5. Generate status report
    """
    def __init__(self):
        """
        Load Home Assistant variables and prepares requests
        """

        #Load the environment variables to connect
        self.url = os.getenv("HOME_ASSISTANT_URL")
        self.token = os.getenv("HOME_ASSISTANT_TOKEN")
        self.thermostat = os.getenv("HOME_ASSISTANT_THERMOSTAT")

        #Creates the request headers for Authorization
        self.header ={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json",}

    def get_state(self):
        """
        Gets all the current home states

        RETURNS:
            dict: Home Assistant state data
        """
        response = requests.get(f"{self.url}/api/states", headers=self.header)
        return response.json()

    def get_thermostat_state(self):
        """
        Gets thermostat state
        RETURNS:
            dict: Thermostat state
        """
        response = requests.get(f"{self.url}/api/states/{self.thermostat}", headers=self.header)
        return response.json()

    def set_temperature(self, temp):
        """
         Changes thermostat temperature

         Sends the new temperature
         to Home Assistant

         ARGS:
             temp (int): New target temperature

         RETURNS:
             bool
         """

        #Create the request data
        d = {"entity_id": self.thermostat, "temperature": temp}
        response = requests.post(f"{self.url}/api/services/climate/set_temperature", headers=self.header, json=d)

        #return if the request worked
        if response.status_code == 200 or response.status_code == 201:
            return True

        return False

    def set_hvac_mode(self, mode):
        """
        Changes thermostat mode

        Examples:
            heat
            cool
            auto
            off

        ARGS:
            mode (str): HVAC mode

        RETURNS:
            bool
        """

        # Create the request data
        d = {"entity_id": self.thermostat, "hvac_mode": mode}
        response = requests.post(f"{self.url}/api/services/climate/set_hvac_mode", headers=self.header, json=d)

        # return if the request worked
        if response.status_code == 200 or response.status_code == 201:
            return True

        return False

    def increase_temperature(self, amount=1):
        """
        Raises thermostat temperature

        Reads the current value first
        before increasing it

        ARGS:
            amount (int): Degrees to increase

        RETURNS:
            int
        """

        state = self.get_thermostat_state()

        #Get the current temperature
        current = state["attributes"]["temperature"]

        #Increase the temperature
        new_temp = current + amount

        #send the new temperature
        self.set_temperature(new_temp)

        return new_temp

    def decrease_temperature(self, amount=1):
        """
        Lowers thermostat temperature

        Reads the current value first
        before decreasing it

        ARGS:
            amount (int): Degrees to lower

        RETURNS:
            int
        """
        state = self.get_thermostat_state()

        # Get the current temperature
        current = state["attributes"]["temperature"]

        # Increase the temperature
        new_temp = current - amount

        # send the new temperature
        self.set_temperature(new_temp)

        return new_temp

    def report(self):
        """
        Creates a thermostat report
        with the current temperature, humidity,
        the target temp, hvac mode, and the hvac state
        which will be sent to ATLAS for voice processing

        RETURNS:
            str
        """

        #Read temperature values
        state = self.get_thermostat_state()
        attributes = state["attributes"]
        current_temp = attributes.get("current_temperature")
        target_temp = attributes.get("temperature")
        humidity = attributes.get("current_humidity")
        hvac_mode = state.get("state")
        hvac_action = attributes.get("hvac_action")

        #Return the response
        return (
            f"The house is currently {current_temp} degrees "
            f"with humidity at {humidity} percent. "
            f"The thermostat is set to {target_temp} degrees. "
            f"Current mode is {hvac_mode} "
            f"and the system is currently {hvac_action}."
        )

