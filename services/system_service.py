import psutil

class SystemService:
    """
    Gets system information for ATLAS

    This service sends real time values
    from the computer and returns
    them to be displayed

    STATS:
        1. CPU usage
        2. RAM usage
        3. Battery level
    """
    def get_stats(self):
        """
        Gets current system values

        Reads CPU, memory,
        and battery information

        RETURNS:
            dict
        """
        battery = psutil.sensors_battery()

        return {
            "cpu": int(psutil.cpu_percent(interval=None)),
            "ram": int(psutil.virtual_memory().percent),
            "battery": int(battery.percent)
        }