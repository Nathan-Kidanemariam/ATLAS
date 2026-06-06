import pygame

class TargetOverlay:
    """
    Draws the Overlay for any objects that have been detected

    Creates scanner boxes around detected objects
    and displays what the objects are

    FEATURES:
        1. Target boxes
        2. Object labels
        3. Scales screen automatically

    ARGS:
        width (int): Width of the window
        height (int): Height of the window
        state: used to get scan results
    """
    def __init__(self, width, height, state):
        """
        Stores the values, fonts, and colors used by the scanner
        """
        self.W = width
        self.H = height
        self.state = state

        self.font = pygame.font.SysFont("Courier New", 18)

        self.color = (0, 220, 255)
        self.text_color = (180, 240, 255)

    def update(self, delta_time, total_time):
        pass

    def draw(self, screen):
        """
        Draws the boxes and lables for each object
        ARGS:
            screen: Main pygame screen
        """

        #Exit if scanning results is disabled
        if not self.state.scan_results_active():
            return

        #Get the detected objects
        objects = self.state.get_scan_results()

        if not objects:
            return

        #Convert object positions so they fit
        for obj in objects:
            name = obj["name"]
            x1, y1, x2, y2, = obj["box"]

            #current screen resolution
            scale_x = self.W/640
            scale_y = self.H/480

            x1 = int(x1 * scale_x)
            y1 = int(y1 * scale_y)

            x2 = int(x2 * scale_x)
            y2 = int(y2 * scale_y)

            #Draw the target box and object label
            self.draw_target_box(screen, x1, y1, x2, y2)
            label = self.font.render(name.upper(), True, self.text_color)
            screen.blit(label, (x1, y1-24))

    def draw_target_box(self, screen, x1, y1, x2, y2):
        """
        Draws the scanner target box
        uses corner lines rather than a full box
        ARGS:
            screen: Main pygame screen
            x1 (int): Left position
            y1 (int): Top position
            x2 (int): Right position
            y2 (int): Bottom position
        """
        size = 18
        t = 2
        
        # top-left
        pygame.draw.line(screen, self.color, (x1, y1), (x1 + size, y1), t)
        pygame.draw.line(screen, self.color, (x1, y1), (x1, y1 + size), t)

        # top-right
        pygame.draw.line(screen, self.color, (x2, y1), (x2 - size, y1), t)
        pygame.draw.line(screen, self.color, (x2, y1), (x2, y1 + size), t)

        # bottom-left
        pygame.draw.line(screen, self.color, (x1, y2), (x1 + size, y2), t)
        pygame.draw.line(screen, self.color, (x1, y2), (x1, y2 - size), t)

        # bottom-right
        pygame.draw.line(screen, self.color, (x2, y2), (x2 - size, y2), t)
        pygame.draw.line(screen, self.color, (x2, y2), (x2, y2 - size), t)

    def shutdown(self):
        pass
        

