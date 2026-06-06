import math
import pygame

class ScanOverlay:
    """
    Draws the scanning animation for ATLAS

    This only appears when scanning and adds scan lines, corners, and flash effects
    to make it seem more realistic

    EFFECTS:
        1. Moving scan line
        2. Corner markers
        3. Blue flash effect

    ARGS:
        width (int): Width of the window
        height (int): Height of the window
        state: used to get the current state
    """
    def __init__(self, width, height, state):
        self.W = width
        self.H = height
        self.state_manager = state

        self.scan_y = 0
        self.line_color = (0, 220, 255)
        self.dim_color = (0, 120, 170)


    def update(self, delta_time, total_time):
        """
        Updates the scan values

        Moves the scan line down over time

        ARGS:
            delta_time (float): Time since the last frame
            total_time (float): Total time
        """
        #Moves the scan line downward over time
        #Reset once it reaches the bottom of the window
        self.scan_y += delta_time * 420
        if self.scan_y > self.H:
            self.scan_y = 0

    def draw(self, screen):
        """
        Draws the full scan
        Only appears while ATLAS is scanning

        ARGS:
            screen: Main pygame screen
        """

        # Exit if ATLAS is not scanning
        if self.state_manager.get() != "SCANNING":
            return

        surface = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.draw_scanlines(surface)
        self.draw_corners(surface)
        self.draw_flash(surface)

        screen.blit(surface, (0, 0))

    def draw_scanlines(self, surface):
        """
        Draws the moving scan lines
        """
        for y in range(0, self.H, 8):
            pygame.draw.line(surface, (*self.dim_color, 18), (0, y), (self.W, y), 1)
        pygame.draw.rect(surface, (*self.line_color, 40), (0, int(self.scan_y), self.W, 4))

    def draw_corners(self, surface):

        """
        Creates a scanner frame around the screen
        """
        size = 70
        pad = 40
        t = 3

        #Create the four corners
        corners = [(pad, pad), (self.W-pad, pad), (pad, self.H-pad), (self.W-pad, self.H-pad)]
        for x,y in corners:
            #Draw different line directions depending on which corner is active
            if x < self.W // 2 and y < self.H // 2:
                pygame.draw.line(surface, self.line_color, (x,y), (x+size, y), t)
                pygame.draw.line(surface, self.line_color, (x,y), (x, y+size), t)
            elif x > self.W // 2 and y < self.H // 2:
                pygame.draw.line(surface, self.line_color, (x,y), (x-size,y), t)
                pygame.draw.line(surface, self.line_color, (x,y), (x,y+size), t)
            elif x < self.W // 2 and y > self.H // 2:
                pygame.draw.line(surface, self.line_color, (x,y), (x+size,y), t)
                pygame.draw.line(surface, self.line_color, (x,y), (x,y-size), t)
            else:
                pygame.draw.line(surface, self.line_color, (x, y), (x - size, y), t)
                pygame.draw.line(surface, self.line_color, (x, y), (x, y - size), t)

    def draw_flash(self, surface):
        """
        Draws the blue flash effect

        Slightly changes the brightness over time

        ARGS:
            surface: Surface used for calculation
        """
        t = pygame.time.get_ticks() / 1000.0
        a = 14 + math.sin(t*8) * 6
        flash = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        flash.fill((0, 180, 255, int(a)))

        surface.blit(flash, (0,0))

    def shutdown(self):
        pass

