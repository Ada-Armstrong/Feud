import pygame
import time
from game import Game, State
from bot import RandomBot


class View:

    def __init__(self, game, display=None, addInput=None, resolution=(640, 480)):
        if not pygame.get_init():
            pygame.init()

        self.game = game
        self.game.subscribe(self.drawTile)
        self.game.subscribe(self.drawState, msg_type='turn')
        self.addInput = self.game.addInput if addInput is None else addInput

        self.res = resolution
        self.standalone = display == None
        self.display = display if display else pygame.display.set_mode(self.res)
        self.display.fill((255, 255, 255))
        self.font = pygame.freetype.SysFont(name='Comic Sans', size=24)

        # tile dimensions
        smaller_dim = min(self.res[0], self.res[1])
        self.rect_width = smaller_dim / self.game.WIDTH
        self.rect_height = smaller_dim / self.game.HEIGHT

        self.selection = []

        # temporary
        self.bot = RandomBot(game, game.turn)
        self.game.subscribe(self.bot.moveCallback, msg_type='turn')

    def start(self):
        self.drawAllTiles()
        self.drawState(str(self.game.turn), str(self.game.state))

        while True:
            if self.game.won:
                print('FINISHED')
                self.game.resetBoard()
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.standalone:
                        pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x_screen, y_screen = pygame.mouse.get_pos()
                    pos_game_space = (int(x_screen // self.rect_width), int(y_screen // self.rect_height))

                    self.drawAllTiles()

                    if self.game.state == State.SWAP:
                        self.handleSwap(pos_game_space)
                    else:
                        self.handleAction(pos_game_space)

                    for p in self.selection:
                        self.drawTile(p, str(self.game.pieces[p]), (0, 255, 0))

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if (self.game.state == State.SWAP and len(self.selection) == 2) or (self.game.state == State.ACTION):
                        self.drawAllTiles()
                        move_string = ' '.join([self.game._cord2str(p) for p in self.selection])
                        self.addInput(move_string)
                        self.selection.clear()
                        time.sleep(0.1)

                #self.drawState()

            pygame.display.update()

    def possibleSwaps(self):
        if not (n := len(self.selection)):
            possible_swaps = {p._pos for swap in self.game.listSwaps() for p in swap}
        elif n == 1:
            piece = self.game.pieces[self.selection[0]]
            possible_swaps = {p._pos for swap in self.game.listSwaps() for p in swap if piece in swap}
        else:
            possible_swaps = set()

        return possible_swaps

    def possibleActions(self):
        if not (n := len(self.selection)):
            possible_actions = {p._pos for action in self.game.listActions() for p in action}
        elif 1 <= n <= self.game.pieces[self.selection[0]]._max_trgts:
            piece = self.game.pieces[self.selection[0]]
            possible_actions = {p._pos for action in piece.listActions(self.game.pieces) for targets in action.values() for p in targets}
        else:
            possible_actions = set()

        return possible_actions

    def handleSwap(self, pos):
        if pos not in self.selection and pos in self.possibleSwaps():
            self.selection.append(pos)
        elif pos in self.selection:
            self.selection.remove(pos)

        for p in self.possibleSwaps():
            self.drawTile(p, str(self.game.pieces[p]), (255, 165, 0))

    def handleAction(self, pos):
        if pos not in self.selection and pos in self.possibleActions():
            self.selection.append(pos)
        elif pos in self.selection:
            i = self.selection.index(pos)
            if i != 0:
                self.selection.remove(pos)
            else:
                self.selection.clear()

        for p in self.possibleActions():
            self.drawTile(p, str(self.game.pieces[p]), (255, 165, 0))

    def drawState(self, turn_str, state_str):
        x_offset = self.rect_width*self.game.WIDTH
        text_y_offset = self.font.size

        whose_turn = 'Black' if turn_str == 'Colour.BLACK' else 'White'
        turn_type = 'Swap' if state_str == 'State.SWAP' else 'Action'
        black_passes, white_passes = self.game.passes.values()

        black = (0, 0, 0)

        pygame.draw.rect(
                surface=self.display,
                color=(128,128,128),
                rect=(x_offset, 0, self.res[0]-x_offset, self.res[1]),
                width=0
                )

        self.font.render_to(self.display, (x_offset, text_y_offset), f'{whose_turn}\'s {turn_type}', black)
        self.font.render_to(self.display, (x_offset, text_y_offset*2), f'Black Passes: {black_passes}', black)
        self.font.render_to(self.display, (x_offset, text_y_offset*3), f'White Passes: {white_passes}', black)

    def drawAllTiles(self):
        for col in range(self.game.WIDTH):
            for row in range(self.game.HEIGHT):
                pos = (col, row)
                self.drawTile(pos, str(self.game.pieces[pos]))

    def drawTile(self, position, tile_data, border_color=None):
        x, y = position
        color, piece_type, hp, active = tile_data.split()

        white = (255, 255, 255)
        black = (0, 0, 0)
        grey = (128, 128, 128)
        border_width = 10

        if color == 'Colour.BLACK':
            bg_color = black
        elif color == 'Colour.WHITE':
            bg_color = white
        else:
            bg_color = grey

        if border_color is None:
            border_color = (0, 0, 255) if active == 'True' else (255, 0, 0)

        text_color = white if bg_color == black else black

        pygame.draw.rect(
                surface=self.display,
                color=border_color,
                rect=(self.rect_width*x, self.rect_height*y, self.rect_width, self.rect_height),
                width=0
                )
        pygame.draw.rect(
                surface=self.display,
                color=bg_color,
                rect=(self.rect_width*x + border_width/2, self.rect_height*y + border_width / 2, self.rect_width - border_width, self.rect_height - border_width),
                width=0
                )
        if int(hp) > 0:
            self.font.render_to(self.display, (self.rect_width*(x + 0.5), self.rect_height*(y + 0.5)), f'{piece_type} {hp}', text_color)


if __name__ == '__main__':
    import threading
    import logging
    logging.basicConfig(format='%(levelname)s <%(asctime)s> %(message)s', level=logging.INFO)

    game = Game()
    g_thread = threading.Thread(target=game.play, daemon=True)

    view = View(game, resolution=(1920, 1080))
    g_thread.start()

    try:
        view.start()
    except KeyboardInterrupt:
        pass
