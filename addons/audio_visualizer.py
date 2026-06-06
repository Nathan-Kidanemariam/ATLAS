import math
import random
import pygame

class AudioVisualizer:
    """
    Creates the circular outer ring around the ATLAS orb
    This AudioVisualizer reacts to the current state and generates
    wave bars that expand as well as contract to mimic audio waves

    STATES:
    SPEAKING - contains the strongest waves
    LISTENING - contains a medium strength wave
    THINKING - contains some small movement
    STANDBY - Stays Still

    ARGS:
         Width (int): Width of the window
         Height (int): Height of the window
         State: Global manager that is used to classify the current mode
         Orb: Reference to the main orb so this class can draw around it
    """
    def __init__(self, width, height, state, orb):
        """
        Initializes the settings and creates the bar values

        Stores the display information, values, colors,
        and starts each segment at zero energy.
        """
        self.W = width
        self.H = height
        self.state_manager = state
        self.orb = orb

        self.cx = self.W // 2
        self.cy = self.H // 2

        self.energy = 0.0
        self.fake_level = 0.0

        self.bar_count = 64
        self.values = []

        for i in range(self.bar_count):
            self.values.append(0.0)

        self.color = (0, 210, 255)
        self.dim = (0, 90, 130)

    def update(self, delta_time, total_time):
        """
        Updates the audio wave values

        Generates energy levels of the orb based on the current state
        and smoothly transitions the bar heights over time

        ARGS:
            delta_time (float): Time since the last frame

            total_time (float): Total runtime that has passed. Used for wave timing
        """
        state = self.state_manager.get()

        #Helps determine how active the sound waves should be
        #based on what ATLAS is doing
        if state == "SPEAKING":
            target = 0.75 + math.sin(total_time * 18) * 0.25 + random.uniform(-0.15, 0.15)
        elif state == "LISTENING":
            target = 0.35 + math.sin(total_time * 8) * 0.15
        else:
            target = 0.05 + math.sin(total_time * 2) * 0.03

        #Helps for smoother transitions instead of jumps
        target = max(0.0, min(1.0, target))
        self.energy += (target - self.energy) * 8 * delta_time

        #Updates each bar individually to create a ring wave effect
        for i in range(self.bar_count):
            wave = math.sin(total_time * 4 * i * 0.35) * 0.5 + 0.5
            self.values[i] += ((self.energy * wave) - self.values[i]) * 10 * delta_time

    def draw(self, screen):
        """
        Draws the AudioVisualizer only when ATLAS is active
        Only appears while speaking, listening, or thinking
        to reduce loss in fps and screen clutter

        ARGS:
             screen: Main pygame screen
        """
        state = self.state_manager.get()

        if state not in ["SPEAKING", "LISTENING", "THINKING"]:
            return

        self.draw_ring_wave(screen)

    def draw_ring_wave(self, screen):
        """
        Makes the circular wave around the orb

        Each line extends outward based on the current energy values
        to simulate ATLAS speaking

        ARGS:
             screen: Main pygame screen
        """

        #Creates a transparent layer so the waves can blend onto the main screen
        surface = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        rad = 185

        #converts the bar values into more circular positions
        #higher energy bars will extend farther from the orb
        for i, val, in enumerate(self.values):
            angle = (math.tau/self.bar_count) * i
            inner = rad
            outer = rad + val * 85

            cx = self.orb.x
            cy = self.orb.y

            x1 = cx + math.cos(angle) * inner
            y1 = cy + math.sin(angle) * inner

            x2 = cx + math.cos(angle) * outer
            y2 = cy + math.sin(angle) * outer

            #This alpha value will change depending on intensity
            #to make the movement feel more natural and alive
            al = int(40 + val * 180)
            pygame.draw.line(surface, (0, 210, 255, al), (x1, y1), (x2, y2), 2)

        screen.blit(surface, (0, 0))

    def shutdown(self):
        """
        Shuts down the visualizer
        """
        pass
