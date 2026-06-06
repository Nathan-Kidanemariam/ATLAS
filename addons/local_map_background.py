import math
import pygame
from services.map_service import MapService
from config import LATITUDE, LONGITUDE

class LocalMapBackground:
    """
    Draws the local map background for ATLAS

    this background loads in a local map and then
    uses different effects like movements, scan lines, zooming in and out,
    and a current position indicator

    EFFECTS:
        1. Slow moving map
        2. Grid like background
        3. Scan line
        4. Location pulse marker
        5. Darker color

    ARGS:
        Width (int): Width of the window.
        Height (int): Height of the window.
    """
    def __init__(self, width, height):
        """
        Sets up the map settings

        Downloads the local image, creates the layers,
        and stores values used to animate the map and positioning
        """
        self.W = width
        self.H = height
        #Load the map and scale the image
        service = MapService(LATITUDE, LONGITUDE, zoom=14)
        map_path = service.download_local_map(size=3)

        #Allows for a smoother fade in
        raw_map = pygame.image.load(map_path).convert()
        self.map_base = pygame.transform.smoothscale(
            raw_map,
            (self.W + 220, self.H + 140)
        )

        #Stores the center position used for the current location indicator
        self.alpha = 0
        self.target_alpha = 135
        self.location_x = self.W // 2
        self.location_y = self.H // 2
        self.font = pygame.font.SysFont("Courier New", 14)

    def update(self, dt, t):
        """
        Updates the background effect values
        Smoothly fades the map

        ARGS:
            dt (float): Time since the last frame
            t (float): Total time
        """
        self.alpha += (self.target_alpha - self.alpha) * 2.0 * dt

    def draw(self, screen):
        """
        Draws the complete animated map background
        Gives it zoom effects, scan line effects, and current location marker

        ARGS:
            screen: Main pygame screen
        """

        #Generate animation time
        t = pygame.time.get_ticks() / 1000.0

        layer = pygame.Surface((self.W, self.H), pygame.SRCALPHA)

        #Gives it slow movement to avoid a static background
        drift_x = math.sin(t * 0.08) * 28
        drift_y = math.cos(t * 0.07) * 18

        x = -110 + drift_x
        y = -70 + drift_y

        layer.blit(self.map_base, (int(x), int(y)))

        #Dark color keeps the elements readable
        dark = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 165))
        layer.blit(dark, (0, 0))

        #Gives it a futurstic blue tint
        tint = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        tint.fill((0, 190, 255, 38))
        layer.blit(tint, (0, 0))

        #Draws the layers
        self.draw_grid(layer)
        self.draw_scan(layer, t)
        self.draw_location(layer, t)

        layer.set_alpha(int(self.alpha))
        screen.blit(layer, (0, 0))

    def draw_grid(self, layer):
        """
        Draws the grid above the map

        Creates a scanning appearance
        """
        spacing = 64

        for x in range(0, self.W, spacing):
            pygame.draw.line(layer, (0, 200, 255, 24), (x, 0), (x, self.H), 1)

        for y in range(0, self.H, spacing):
            pygame.draw.line(layer, (0, 200, 255, 20), (0, y), (self.W, y), 1)

    def draw_scan(self, layer, t):
        """
        Draws the moving scan line effect
        ARGS:
            layer: Surface used for calculation
            t (float): current animation time
        """
        scan_y = int((t * 90) % self.H)

        pygame.draw.rect(
            layer,
            (0, 220, 255, 38),
            (0, scan_y, self.W, 3)
        )

    def draw_location(self, layer, t):
        """
        Draws the current location marker

        Creates a large, expanding, glowing circle around the user's location
        to show active tracking

        ARGS:
            layer: Surface used for calculation
            t (float): current animation time
        """
        cx = self.location_x
        cy = self.location_y

        #Give pulse effects to rings
        for i in range(3):
            radius = 15 + i * 20 + math.sin(t * 3) * 4
            pygame.draw.circle(layer,(0, 255, 170, 90),(cx, cy), int(radius),1)

        #Draws the marker
        pygame.draw.circle(layer, (120, 255, 210), (cx, cy), 5)

        #Draws the location label
        label = self.font.render("CURRENT LOCATION", True, (150, 255, 230))
        layer.blit(label, (cx + 16, cy - 8))

    def shutdown(self):
        pass