import pygame
import threading
import sys
from game import Game
from view import View

class App:
    def __init__(self):
        pygame.init()
        
        self.res = (1920, 1080)
        self.display = pygame.display.set_mode(self.res)
        pygame.display.set_caption('Feud')

    def start(self):
        self.mainMenu()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()

                    for button, func in self.buttons:
                        if button.collidepoint(mouse):
                            func()
                            self.mainMenu()
                            break

            pygame.display.update()

    def mainMenu(self):
        self.display.fill((255, 255, 255))

        black = (0, 0, 0)
        grey = (128, 128, 128)
        width, height = self.res

        self.textWithBackground('Feud', (width/5, height/10, width*3/5, height/5), grey, black)
        new_game_bttn = self.textWithBackground('Play', (3*width/10, 4*height/10, width*4/10, height/10), grey, black)
        settings_bttn = self.textWithBackground('Settings', (3*width/10, 11*height/20, width*4/10, height/10), grey, black)
        quit_bttn = self.textWithBackground('Quit', (3*width/10, 14*height/20, width*4/10, height/10), grey, black)

        self.buttons = [(new_game_bttn, self.newGame), (settings_bttn, self.settingsMenu), (quit_bttn, self.quit)]

    def textWithBackground(self, text, bg_rect, bg_colour, text_colour=(0, 0, 0)):
        rect = pygame.draw.rect(
                surface=self.display,
                color=bg_colour,
                rect=bg_rect,
                width=0,
                border_radius=int(bg_rect[2]/32)
                )

        font = pygame.font.SysFont(name='Comic Sans', size=int(min(bg_rect[2], bg_rect[3])))
        title = font.render(text, 1, text_colour)
        title_rect = title.get_rect(center=rect.center)
        self.display.blit(title, title_rect)
        
        return rect

    def newGame(self):
        game = Game()
        g_thread = threading.Thread(target=game.play, daemon=True)
        g_thread.start()

        view = View(game, self.display, resolution=self.res)
        try:
            view.start()
        except KeyboardInterrupt:
            pass

    def settingsMenu(self):
        print('Settings')
        pass

    def quit(self):
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    import logging
    logging.basicConfig(format='%(levelname)s <%(asctime)s> %(message)s', level=logging.DEBUG)

    app = App()
    app.start()
