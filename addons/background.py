import random
import pygame

class Background:
    """
    Draws the ATLAS background

    This class handles the grid, particles, scan lines,
    and the dark border behind the orb

    ARGS:
        width (int): Width of the window
        height (int): Height of the window
    """
    def __init__(self, width, height):
        self.W = width
        self.H = height

        self.spacing = 70
        self.offset = 0

        self.scan_y = 0

        self.particles = []
        for i in range(90):
            self.particles.append({
                "x": random.randint(0, self.W),
                "y": random.randint(0, self.H),
                "speed": random.uniform(8, 35),
                "size": random.randint(1,2),
            })

        self.grid_surface = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.make_grid()

    def make_grid(self):
        """
        Creates the background grid once so it does not
        need to be redrawn from scratch every frame
        """
        for x in range(0, self.W, self.spacing):
            pygame.draw.line(self.grid_surface, (0, 120, 170, 22), (x, 0), (x, self.H), 1)

        for y in range(0, self.H, self.spacing):
            pygame.draw.line(self.grid_surface, (0, 120, 170, 18), (0, y), (self.W, y), 1)

    def update(self, delta_time, total_time):
        """
        Updates the moving background objects

        Moves the scan line and particles over time

        ARGS:
            delta_time (float): Time since the last frame
            total_time (float): Total runtime passed into the loop
        """
        self.offset = (self.offset + delta_time * 18) % self.spacing
        self.scan_y = (self.scan_y + delta_time * 120) % self.H

        for p in self.particles:
            p["y"] += p["speed"] * delta_time
            if p["y"] > self.H:
                p["y"] = 0
                p["x"] = random.randint(0,self.W)

    def draw(self, screen):
        """
        Draws all the background layers onto the screen

        ARGS:
            screen: Main pygame screen
        """
        self.draw_particles(screen)
        self.draw_grid(screen)
        self.draw_scanlines(screen)
        self.draw_border(screen)

    def draw_grid(self, screen):
        screen.blit(self.grid_surface, (0, 0))

    def draw_scanlines(self, screen):
        scan_surface = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        for y in range(0, self.H, 6):
            pygame.draw.line(scan_surface, (0, 80, 110, 12), (0, y), (self.W, y), 1)
        pygame.draw.rect(scan_surface, (0, 210, 255, 35), (0, int(self.scan_y), self.W, 2))
        screen.blit(scan_surface, (0,0))

    def draw_particles(self, screen):
        """
        Draws small moving particles in the background
        """
        for p in self.particles:
            pygame.draw.circle(screen, (0, 100, 150), (int(p["x"]), int(p["y"])), p["size"])

    def draw_border(self, screen):
        """
        Draws the border around the screen
        to keep the center of the HUD focused.
        """
        border = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        for i in range(18):
            a = 8
            rect = pygame.Rect(i*25, i*25, self.W-i*50, self.H-i*50)
            pygame.draw.rect(border, (0, 0, 0, a), rect, 3)
        screen.blit(border, (0,0))

    def shutdown(self):
        pass