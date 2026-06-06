import pygame
import datetime
from services.weather_service import WeatherService
from config import LATITUDE, LONGITUDE, LOCATION_NAME

class HUD:
    """
    Draws the main ATLAS display
    This class controls all the information panels on the screen
    including the time, weather, and the small local grid panel

    PANELS:
        Time: current time and data
        Weather: live weather information
        Local Grid: Panel for the map

    ARGS:
        Width (int): Width of the window.
        Height (int): Height of the window.
    """

    def __init__(self, width, height):
        """
        Creates the fonts, colors, window size,
        and the weather service used by the weather panel
        """
        self.W = width
        self.H = height

        self.font_big = pygame.font.SysFont("Courier New", 28)
        self.font_med = pygame.font.SysFont("Courier New", 18)
        self.font_small = pygame.font.SysFont("Courier New", 14)

        self.panel_color = (0, 25, 35, 110)
        self.line_color = (0, 210, 255, 120)
        self.text_color = (150, 235, 255)
        self.dim_color = (0, 110, 150)
        self.weather_service = WeatherService(LATITUDE, LONGITUDE, LOCATION_NAME)
    def update(self, date_time, total_time):
        pass

    def draw(self, screen):
        """
        Draws all the HUD panels onto the screen

        ARGS:
            screen: Main pygame screen
        """
        self.draw_time_panel(screen)
        self.draw_weather_panel(screen)
        self.draw_map_panel(screen)

    def draw_panel(self, screen, x, y, w, h, title):

        """
        Draws a transparent panel

        This method keeps all of the HUD panels consistent
        by using the same background, border, title, and line

        ARGS:
            screen: Main pygame screen
            x (int): Left position of the panel
            y (int): Top position of the panel
            w (int): Width of the panel
            h (int): Height of the panel
            title (str): Text shown at the top of the panel
        """
        panel = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.panel_color, (0, 0, w, h), border_radius=12)
        pygame.draw.rect(panel, self.line_color, (0, 0, w, h), 1, border_radius=12)

        pygame.draw.line(panel, self.line_color, (15, 34), (w-15, 34), 1)

        title_surf = self.font_small.render(title.upper(), True, self.text_color)
        title_x = (w - title_surf.get_width()) // 2
        panel.blit(title_surf, (title_x, 10))
        screen.blit(panel, (x,y))

    def draw_time_panel(self, screen):
        """
        Draws the time panel

        Displays the current time and date in the top right section of the HUD
        """
        x = self.W - 330
        y = 45
        w = 280
        h = 110

        self.draw_panel(screen, x, y, w, h, "Chronos")
        t_now = datetime.datetime.now()

        #Get the current time
        time_text = t_now.strftime("%I:%M:%S %p")

        #Format the time and date into a readable form
        date_text = t_now.strftime("%A, %b %d")

        time_surf = self.font_big.render(time_text, True, self.text_color)
        date_surf = self.font_med.render(date_text, True, self.dim_color)
        screen.blit(time_surf, (x + 20, y +48))
        screen.blit(date_surf, (x + 22, y+ 80))

    def draw_weather_panel(self, screen):
        """
        Draws the weather panel

        pulls weather data from the weather service and displays
        temperature, precipitation, wind speed, and location
        """
        x = 50
        y = self.H - 170
        w = 390
        h = 150

        self.draw_panel(screen, x, y, w, h, "weather")

        #Get latest cached or live weather data
        weather = self.weather_service.get_weather()

        #Convert the weather values into readable form
        temp = f'{weather["temperature"]}°F'
        condition = f'Precipitation: {weather["precipitation"]}'
        wind = f'Wind: {weather["wind"]} mph'
        location = self.font_small.render(
            weather["location"],
            True,
            self.text_color
        )

        temp_surf = self.font_big.render(temp, True, self.text_color)
        condition_surf = self.font_med.render(condition, True, self.dim_color)
        wind_surf = self.font_small.render(wind, True, self.dim_color)

        screen.blit(temp_surf, (x + 22, y + 55))
        screen.blit(condition_surf, (x + 22, y + 95))
        screen.blit(wind_surf, (x + 22, y + 122))
        screen.blit(location, (x + 22, y + 20))

    def draw_map_panel(self, screen):
        """
        Draws the map panel

        Outlines where the map will be placed and gives ATLAS a
        position tracking element
        :param screen:
        :return:
        """
        x = 50
        y = 45
        w = 340
        h = 210

        self.draw_panel(screen, x, y, w, h, "local grid")

        #Draw vertical and horizontal lines
        for i in range(6):
            line_x = x + 25 + i * 48
            pygame.draw.line(screen, self.dim_color, (line_x, y + 50), (line_x, y + h - 20), 1)

        for j in range(4):
            line_y = y + 55 + j * 35
            pygame.draw.line(screen, self.dim_color, (x+ 20, line_y), (x + w - 20, line_y), 1)

        #Draws the current position mark
        pygame.draw.circle(screen, self.text_color, (x + w // 2, y + h // 2 + 15), 5)
        pygame.draw.circle(screen, self.line_color, (x + w // 2, y + h // 2 +15), 22, 1)
        label = self.font_small.render("CURRENT POSITION", True, self.text_color)
        screen.blit(label, (x + 95, y + h -38))

    def shutdown(self):
        pass
