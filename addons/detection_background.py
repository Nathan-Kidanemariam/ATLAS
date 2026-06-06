import pygame

class DetectionOverlay:
    """
    Draws the scan results during object detection

    This displays the detected objects on the HUD panel
    and updates based on the current scan results

    ELEMENTS:
        1. Object title
        2. Transparent panel

    ARGS:
        Width (int): Width of the window
        Height (int): Height of the window.
        state: Used to get the current state of ATLAS

    """
    def __init__(self, width, height, state):
        """
        Sets up the fonts and colors and initializes width, height, and state variables
        """
        self.W = width
        self.H = height
        self.state = state

        self.font_title = pygame.font.SysFont("Courier New", 14)
        self.font_item = pygame.font.SysFont("Courier New", 20)

        self.text_color = (150, 235, 255)
        self.line_color = (0, 210, 255, 130)
        self.panel_color = (0, 25, 35, 120)

    def update(self, delta_time, total_time):
        pass

    def draw(self, screen):
        """
        Draws the detection panel and objects

        The panel is hidden when no scanning has taken place

        ARGS:
            screen: Main pygame screen
        """

        #Gets the current scan results from ATLAS
        objects = self.state.get_scan_results()

        #Exit early if nothing was found
        if not objects:
            return

        #creates the panel size
        #so any larger object list fit correctly
        x = self.W - 360
        y = 190
        w = 310
        h = 55 + len(objects) * 30

        #creates the background and border
        panel = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.panel_color, (0, 0, w, h), border_radius=12)
        pygame.draw.rect(panel, self.line_color, (0, 0, w, h), 1, border_radius=12)

        #draws the title section
        title = self.font_title.render("OBJECTS", True, self.text_color)
        panel.blit(title, (w-title.get_width() //2, 12))
        pygame.draw.line(panel, self.line_color, (18, 38), (w-18, 38), 1)

        #Write out each detected object onto the panel
        for i, o in enumerate(objects):
            label = self.font_item.render(f">{o.upper()}", True, self.text_color)
            panel.blit(label, (25, 52 + i *30))

        screen.blit(panel, (x,y))

    def shutdown(self):
        pass
