import pygame.locals

class MessageBox: # the lower right area that contains all the messages the player gets.
    def __init__(self, screen):
        self.message_list = [] # holds all the messages currently on screen
        self.image = pygame.image.load('./img/message_box.png').convert_alpha()
        self.screen = screen

    def add(self, message):
        self.message_list.insert(len(self.message_list), message)
        if len(self.message_list) > 14:
            del self.message_list[-1:]

    def draw(self, screen):
        start_x, start_y = 480, 240
        # width, height = 360-5, 240-5
        font = pygame.font.SysFont('DejaVu Sans Mono', 14)
        message_height = 14
        next_y = 28
        self.screen.blit(self.image, (start_x, start_y))
        for message in self.message_list: # TODO: change this to FontManager
            textsurface = font.render(message, False, (0, 0, 0))
            self.screen.blit(textsurface, (start_x+5, start_y + next_y))
            next_y = next_y + message_height
