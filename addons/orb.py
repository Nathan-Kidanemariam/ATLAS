#This will house the orb of jarvis
import math
import random
import pygame

class Orb:
    """
      Draws the main ATLAS orb

      This orb moves around depending on the current state.
      It also draws the glow, rings, particles, and state text.

      STATES:
        1. LISTENING: orb is centered
        2. THINKING: orb moves a little upward
        3. SPEAKING: orb moves a little to the right
        4. SCANNING: orb moves to the lower right
        5. STANDBY: orb rests in the center of the right side

      ARGS:
        width (int): Width of the window
        height (int): Height of the window
        state: Used to get the current state from ATLAS
      """
    def __init__(self, width, height, state):
        self.W = width
        self.H = height
        self.state_manager = state

        self.x = self.W // 2
        self.y = self.H // 2

        self.home_x = self.x
        self.home_y = self.y

        self.target_x = self.x
        self.target_y = self.y

        self.radius = 95
        self.state = "IDLE"

        self.angle = 0
        self.estParticles = []

        #Creates particles around the orb
        #Each particle gets its own angle, distance,
        #speed, and size to make the movement feel more realistic
        for items in range(70):
            self.estParticles.append({"angle": random.uniform(0, math.tau), "distance": random.uniform(120, 230), "speed": random.uniform(0.15, 0.7), "size": random.randint(1,3),})
        self.cached_glow = None
        self.cached_glow_radius = 0

    def set_state(self, state):
        self.state = state.upper()

    def update(self, delta_time, total_time):
        """
         Updates the orb position and rotation
         Moves the orb based on the current state
         and smoothly moves it toward the target position

        ARGS:
         delta_time (float): Time since the last frame
         total_time (float): Total runtime
        """
        self.state = self.state_manager.get()
        speed = 0.9
        if self.state == "LISTENING":
            self.target_x = self.home_x
            self.target_y = self.home_y
        elif self.state == "THINKING":
            self.target_x = self.home_x
            self.target_y = self.home_y - 60
        elif self.state == "SPEAKING":
            self.target_x = self.W - 330
            self.target_y = self.H // 2
        elif self.state == "SCANNING":
            self.target_x = self.W - 330
            self.target_y = self.H - 260
        elif self.state == "STANDBY":
            self.target_x = self.home_x
            self.target_y = self.home_y + 25

        smoothness = 3.5
        self.x += (self.target_x - self.x) * smoothness * delta_time
        self.y += (self.target_y - self.y) * smoothness * delta_time
        self.angle += delta_time * speed

    def draw(self, screen):
        """
        Draws the full orb and handles the pulse size,
        particles, glow, core of the orb, rings, and the state text

        ARGS:
            screen: Main pygame screen
        """
        time = pygame.time.get_ticks()/1000.0
        pulse = math.sin(time * 2.5) * 8
        radius = self.radius + pulse

        if self.state == "LISTENING":
            radius += 10
        elif self.state == "THINKING":
            radius += math.sin(time * 8) * 6
        elif self.state == "SPEAKING":
            radius += math.sin(time * 14) * 12
        elif self.state == "SCANNING":
            radius += 4
        elif self.state == "STANDBY":
            radius -= 18


        self.draw_particles(screen, time)
        self.draw_glow(screen, radius)
        self.draw_orb_core(screen, radius)
        self.draw_rings(screen, radius)
        self.draw_state_text(screen)

    def draw_glow(self, screen, radius):
        """
        Draws the glow around the orb

        The glow is cached so pygame does not need to
        recreate the full glow every frame protecting fps

        ARGS:
            screen: Main pygame screen
            radius (float): orb radius
        """
        glow_radius = int(radius + 9 * 18)

        #Only rebuilds the glow if it doesn't exist
        #or if the size changes too much
        if self.cached_glow is None or abs(glow_radius - self.cached_glow_radius) > 8:
            self.cached_glow_radius = glow_radius
            self.cached_glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)

            #Creates multiple circles to create a more softer glow
            #Outer circles are darker while the inner circles are brighter
            for i in range(9, 0, -1):
                r = int(radius + i * 18)
                color = (0, 80 + i * 8, 120 + i * 12, 14)

                pygame.draw.circle(self.cached_glow, color,(glow_radius, glow_radius), r)

        screen.blit(self.cached_glow, (self.x - glow_radius, self.y - glow_radius))

    def draw_orb_core(self, screen, radius):
        """
        Draws the main orb circle

        This includes the dark center, outer blue ring, and inner ring
        """
        pygame.draw.circle(screen, (0, 35, 55), (self.x, self.y), int(radius))
        pygame.draw.circle(screen, (0, 180, 255), (self.x, self.y), int(radius), 2)
        pygame.draw.circle(screen, (160, 240, 255), (self.x, self.y), int(radius * 0.45), 1)

    def draw_rings(self, screen, radius):
        """
        Draws the rings around the orb

        The rings slightly shake and rotate to make ATLAS feel alive
        """
        for i in range(3):
            ring_rad = radius + 25 + i * 24
            point = []
            for j in range(0, 360, 8):
                angle = math.radians(j) + self.angle * (1 + i *0.35)
                shake = math.sin(angle * 3 + self.angle * 4) *5
                r = ring_rad + shake

                x = self.x + math.cos(angle) * r
                y = self.y + math.sin(angle) * r

                point.append((x, y))
            if len(point) > 2:
                pygame.draw.lines(screen, (0, 160, 220), True, point, 1)

    def draw_particles(self, screen, t):
        """
        Draws small particles around the orb
        The particles move around the center to give the orb more motion and energy
        """
        for p in self.estParticles:
            angle = p["angle"] + t * p["speed"]
            dist = p["distance"] + math.sin(t * 2 + p["angle"]) * 10
            x = self.x + math.cos(angle) * dist
            y = self.y + math.sin(angle) * dist
            pygame.draw.circle(screen, (0, 140, 200), (int(x), int(y)), p["size"])

    def draw_state_text(self, screen):
        """
        Draws the current state under the orb
        """
        font = pygame.font.SysFont("Courier New", 18)
        text = font.render(self.state, True, (0, 180, 255))
        screen.blit(text, (self.x - text.get_width() // 2, self.y + 180))

    def shutdown(self):
        pass

