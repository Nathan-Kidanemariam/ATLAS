import pygame
from services.system_service import SystemService

class SystemPanel:
    """
    Draws the system panel for ATLAS

    This panel shows the live system information
    and updates automatically over time

    STATS:
        1. CPU usage
        2. RAM usage
        3. Battery level

    ARGS:
        width (int): Width of the window
        height (int): Height of the window
    """
    def __init__(self, width, height):

        """
        Sets up the system panel
        Creates fonts, colors, positions, and stores the values
        :param width:
        :param height:
        """
        self.W = width
        self.H = height

        #Store the position of the panel
        self.x = self.W - 320
        self.y = self.H - 170
        self.w = 280
        self.h = 120

        #Get the first system values
        self.service = SystemService()
        self.stats = self.service.get_stats()
        self.timer = 0

        self.font_title = pygame.font.SysFont("Courier New", 14)
        self.font_big = pygame.font.SysFont("Courier New", 22)
        self.text_color = (150, 235, 255)
        self.dim_color = (0, 110, 150)
        self.panel_color = (0, 25, 35, 110)
        self.line_color = (0, 210, 255, 120)

    def update(self, delta_time, total_time):

        """
        Updates the systems values
        Refreshes the stats every second

        ARGS:
            delta_time (float): Time since the last frame
            total_time (float): Total time
        """
        #Keep track of update time
        self.timer += delta_time

        #Only update once every second
        if self.timer >= 1.0:
            self.stats = self.service.get_stats()
            self.timer = 0

    def draw(self, screen):
        """
        Draws the system panel
        Displays the CPU, RAM, and Battery Information
        ARGS:
            screen: Main pygame screen
        """

        #Creates the transparent panel
        panel = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.panel_color, (0, 0, self.w, self.h), border_radius=12)
        pygame.draw.rect(panel, self.line_color, (0, 0, self.w, self.h), 1, border_radius=12)

        #Draw the title and line of separation
        title = self.font_title.render("SYSTEM", True, self.text_color)
        panel.blit(title, ((self.w - title.get_width())//2, 10))
        pygame.draw.line(panel, self.line_color, (15, 34), (self.w - 15, 34), 1)

        #Convert the values and turn it all into text
        cpu = self.font_big.render(f"CPU {self.stats['cpu']}%", True, self.text_color)
        ram = self.font_big.render(f"RAM {self.stats['ram']}%", True, self.text_color)
        bat = self.font_big.render(f"BAT {self.stats['battery']}%", True, self.text_color)

        #Draw the values onto the panel
        panel.blit(cpu, (25, 45))
        panel.blit(ram, (25, 70))
        panel.blit(bat, (25, 95))

        screen.blit(panel, (self.x, self.y))

    def shutdown(self):
        pass
