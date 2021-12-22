import pygame
from game import Game, State


class View:

    def __init__(self, game, addInput=None, resolution=(640, 480)):
        pygame.init()

        self.res = resolution
        self.game = game
        self.game.subscribe(self.drawTile)
        self.addInput = self.game.addInput if addInput is None else addInput

        self.display = pygame.display.set_mode(self.res)
        self.display.fill((255, 255, 255))
        self.font = pygame.freetype.SysFont(name='Comic Sans', size=24)

        # tile dimensions
        self.rect_width = self.res[0] / self.game.WIDTH
        self.rect_height = self.res[1] / self.game.HEIGHT

        self.selection = []

    def start(self):
        self.drawAllTiles()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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
            self.selection.remove(pos)

        for p in self.possibleActions():
            self.drawTile(p, str(self.game.pieces[p]), (255, 165, 0))

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
        self.font.render_to(self.display, (self.rect_width*(x + 0.5), self.rect_height*(y + 0.5)), f'{piece_type} {hp}', text_color)


if __name__ == '__main__':
    import threading

    game = Game()
    g_thread = threading.Thread(target=game.play)
    g_thread.start()

    view = View(game)
    try:
        view.start()
    except KeyboardInterrupt:
        pass
