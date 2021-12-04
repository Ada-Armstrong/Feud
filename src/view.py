import pygame
import threading


class View:
    def __init__(self, game, resolution=(640, 480)):
        pygame.init()

        self.res = resolution
        self.game = game
        self.display = pygame.display.set_mode(self.res)

    def start(self):
        self.game_thread = threading.Thread(target=play_game, args=(self.game))



