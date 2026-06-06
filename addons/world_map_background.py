import math
import pygame

class WorldMapBackground:
    def __init__(self, width, height, state):
        self.W = width
        self.H = height
        self.state_manager = state

        self.rotation = 0

        self.cx = self.W // 2 + 440
        self.cy = self.H // 2 - 40

        self.radius = 240

        self.line_color = (0, 220, 255)
        self.dim_color = (0, 120, 170)
        self.cached_surface = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.frame_counter = 0

    def update(self, dt, t):
        self.rotation += dt * 0.35

    def draw(self, screen):
        self.frame_counter += 1

        if self.frame_counter % 3 == 0:
            self.cached_surface.fill((0, 0, 0, 0))

            self.draw_globe_glow(self.cached_surface)
            self.draw_globe(self.cached_surface)
            self.draw_scan(self.cached_surface)
            self.draw_location(self.cached_surface)

        screen.blit(self.cached_surface, (0, 0))

    def draw_globe_glow(self, surface):

        for i in range(8, 0, -1):
            glow_radius = self.radius + i * 18

            pygame.draw.circle(surface,(0, 140, 200, 8),(self.cx, self.cy), glow_radius)

    def draw_globe(self, surface):

        # outer sphere
        pygame.draw.circle(surface,(*self.line_color, 90),(self.cx, self.cy), self.radius,1)

        # latitude rings
        for lat in range(-60, 70, 30):

            lat_radians = math.radians(lat)

            ring_radius = math.cos(lat_radians) * self.radius
            y = self.cy + math.sin(lat_radians) * self.radius

            pygame.draw.ellipse(surface,(*self.dim_color, 85),(self.cx - ring_radius,y - ring_radius * 0.18, ring_radius * 2, ring_radius * 0.36),1)

        # longitude lines
        for lon in range(0, 360, 40):

            points = []

            lon_radians = math.radians(lon) + self.rotation

            for lat in range(-90, 91, 8):

                lat_radians = math.radians(lat)

                x = (self.cx + math.sin(lon_radians)* math.cos(lat_radians)* self.radius)

                y = (self.cy+ math.sin(lat_radians)* self.radius)

                depth = math.cos(lon_radians)

                if depth > -0.15:
                    points.append((x, y))

            if len(points) > 2:
                pygame.draw.lines(surface,(*self.dim_color, 70),False,points,1)

    def draw_scan(self, surface):
        t = pygame.time.get_ticks() / 1000.0

        angle = t * 0.8

        end_x = self.cx + math.cos(angle) * self.radius
        end_y = self.cy + math.sin(angle) * self.radius

        pygame.draw.line(surface,(*self.line_color, 55),(self.cx, self.cy),(end_x, end_y),2)

    def draw_location(self, surface):

        loc_x = self.cx + 70
        loc_y = self.cy - 40

        t = pygame.time.get_ticks() / 1000.0

        for i in range(3):
            pulse = 16 + i * 18 + math.sin(t * 2) * 3

            pygame.draw.circle(surface,(*self.line_color, 45),(int(loc_x), int(loc_y)),int(pulse),1)

        pygame.draw.circle(surface,(160, 240, 255),(int(loc_x), int(loc_y)),5)

    def shutdown(self):
        pass
