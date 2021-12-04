from piece import Piece, Pieces, Point, Action
from colour import Colour
from exceptions import SwapError, ActionError, BoardError, InputError
from typing import Type, Dict, List, Set, Tuple
from enum import Enum

from empty import Empty
from archer import Archer
from king import King
from medic import Medic
from shield import Shield
from knight import Knight
from wizard import Wizard


class State(Enum):
    SWAP = 0
    ACTION = 1

TeamPieces = Dict[Type[Colour], List[Type[Piece]]]

class Game:

    def __init__(self):
        self.WIDTH: int = 4
        self.HEIGHT: int = 4

        self.state: State = State.SWAP
        self.turn: Colour = Colour.BLACK
        self.passes: Dict[Type[Colour], int] = {Colour.BLACK:0, Colour.WHITE:0}

        self.pieces: Pieces = {
                (x, y):Empty((x,y))
                for x in range(self.WIDTH) for y in range(self.HEIGHT)}
        self.team_pieces: TeamPieces = {Colour.BLACK: [], Colour.WHITE: []}
        self.kings: Dict[Type[Colour], Piece] = {Colour.BLACK:None, Colour.WHITE:None}

        self.setBoard()
        self.findKings()
        self.addPiecesToTeams()

    def __str__(self):
        out = ''

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                out += str(self.pieces[(x, y)])
                if x != self.WIDTH - 1:
                    out += ' | '
            if y != self.HEIGHT - 1:
                out += '\n'

        return out

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))

        self.findKings()
        self.addPiecesToTeams()

        return result

    def _str2cord(self, string: str) -> Tuple[int, int]:
        if len(string) != 2:
            raise InputError('Too many characters provided as coordinate')

        try:
            col = ord(string[0].lower()) - ord('a')
            row = int(string[1]) - 1
        except TypeError as e:
            raise InputError('Coordinate must be in the format [A-D][1-4]')

        return (col, row)

    def play(self) -> None:
        while 1:
            print(self)

            if loser := (self.isolated() or self.kingDead()):
                print(f'{loser} lost')
                break

            if self.state == State.SWAP:
                print(f'{self.turn} to swap')

                while 1:
                    start, end = input().replace(' ', '').split(',')

                    try:
                        start_fmt = self._str2cord(start) 
                        end_fmt = self._str2cord(end)
                    except InputError as e:
                        print(e)
                        continue

                    try:
                        self.swap(start_fmt, end_fmt)
                        break
                    except SwapError as e:
                        print(e)

            else:
                print(f'{self.turn} to action')

                while 1:
                    str_cords = input().replace(' ', '').split(',')

                    try:
                        cords = [self._str2cord(s) for s in str_cords]
                    except InputError as e:
                        print(e)
                        continue

                    if len(cords) < 2:
                        print('Need at least 2 cordinates to preform an action')
                        continue

                    try:
                        self.action(cords[0], cords[1:])
                        break
                    except ActionError as e:
                        print(e)

    def isolated(self) -> Colour:
        black = sum([p._active for p in self.team_pieces[Colour.BLACK]]) == 0
        white = sum([p._active for p in self.team_pieces[Colour.WHITE]]) == 0

        if black and white:
            return Colour.BOTH
        elif black:
            return Colour.BLACK
        elif white:
            return Colour.WHITE

        return None

    def kingDead(self) -> Colour:
        black = self.kings[Colour.BLACK]._hp <= 0
        white = self.kings[Colour.WHITE]._hp <= 0

        if black and white:
            return Colour.BOTH
        elif black:
            return Colour.BLACK
        elif white:
            return Colour.WHITE

        return None

    def setBoard(self) -> None:
        # first row
        self.pieces[(0, 0)] = Archer(Colour.BLACK, (0, 0))
        self.pieces[(1, 0)] = King(Colour.BLACK, (1, 0))
        self.pieces[(2, 0)] = Medic(Colour.BLACK, (2, 0))
        self.pieces[(3, 0)] = Archer(Colour.BLACK, (3, 0))
        # second row
        self.pieces[(0, 1)] = Knight(Colour.BLACK, (0, 1))
        self.pieces[(1, 1)] = Shield(Colour.BLACK, (1, 1))
        self.pieces[(2, 1)] = Wizard(Colour.BLACK, (2, 1))
        self.pieces[(3, 1)] = Knight(Colour.BLACK, (3, 1))
        # third row
        self.pieces[(0, 2)] = Knight(Colour.WHITE, (0, 2))
        self.pieces[(1, 2)] = Shield(Colour.WHITE, (1, 2))
        self.pieces[(2, 2)] = Wizard(Colour.WHITE, (2, 2))
        self.pieces[(3, 2)] = Knight(Colour.WHITE, (3, 2))
        # forth row
        self.pieces[(0, 3)] = Archer(Colour.WHITE, (0, 3))
        self.pieces[(1, 3)] = King(Colour.WHITE, (1, 3))
        self.pieces[(2, 3)] = Medic(Colour.WHITE, (2, 3))
        self.pieces[(3, 3)] = Archer(Colour.WHITE, (3, 3))
        # activate pieces
        for p in self.pieces:
            self.pieces[p].updateActivity(self.pieces)

    def findKings(self) -> None:
        counts = {Colour.BLACK: 0, Colour.WHITE: 0}

        for p in self.pieces:
            piece = self.pieces[p]

            if type(piece) is King:
                self.kings[piece._colour] = piece
                counts[piece._colour] += 1

        for c in counts:
            if counts[c] != 1:
                raise BoardError(f'{counts[c]} {c} kings found') 


    def addPiecesToTeams(self) -> None:
        for i in self.pieces:
            if self.pieces[i]._colour is not None:
                self.team_pieces[self.pieces[i]._colour].append(self.pieces[i])

    def _inbound(self, pos: Point) -> bool:
        return 0 <= pos[0] <= self.WIDTH and 0 <= pos[1] <= self.HEIGHT

    def canSwap(self, pos1: Point, pos2: Point) -> bool:
        if (self.state != State.SWAP 
                or not self._inbound(pos1)
                or not self._inbound(pos2)):
            return False

        p1 = self.pieces[pos1]
        p2 = self.pieces[pos2]

        return ((p1._colour == self.turn and p1.canSwap(p2))
                or (p2._colour == self.turn and p2.canSwap(p1)))

    def swap(self, pos1: Point, pos2: Point) -> None:
        if not self.canSwap(pos1, pos2):
            raise SwapError(f'{pos1=} and {pos2=} cannot be swapped') 

        p1 = self.pieces[pos1]
        p2 = self.pieces[pos2]

        p1.applySwap(p2)

        self.pieces[pos1], self.pieces[pos2] = p2, p1

        # update activity of pieces and neighbours
        for i in p1.neighbourPositions():
            self.pieces[i].updateActivity(self.pieces)

        for i in p2.neighbourPositions():
            self.pieces[i].updateActivity(self.pieces)

        self.state = State.ACTION

    def canAction(self, pos: Point, targets: List[Point]) -> bool:
        if (self.state != State.ACTION
                or not self._inbound(pos)
                or sum([not self._inbound(p) for p in targets])):
            return False

        trgts = [self.pieces[p] for p in targets]

        return self.pieces[pos].canAction(trgts, self.pieces)

    def action(self, pos: Point, targets: List[Point]) -> None:
        if not self.canAction(pos, targets):
            raise ActionError(f'Can\'t perform action {pos}: {targets}')

        trgts = [self.pieces[p] for p in targets]

        self.pieces[pos].applyAction(trgts, self.pieces)

        for piece in trgts:
            for i in piece.neighbourPositions():
                self.pieces[i].updateActivity(self.pieces)

        self.state = State.SWAP
        self.turn = Colour.BLACK if self.turn == Colour.WHITE else Colour.WHITE

    def skipAction(self) -> None:
        self.passes[self.turn] += 1
        self.turn = Colour.BLACK if self.turn == Colour.WHITE else Colour.WHITE

    def listSwaps(self) -> Set[Tuple[Piece]]:
        out = set()
        team = self.team_pieces[self.turn]

        for p in team:
            out.update(p.listSwaps(self.pieces))

        return out

    def listActions(self) -> List[Action]:
        out = []
        team = self.team_pieces[self.turn]

        for p in team:
            out += p.listActions(self.pieces)

        return out
    

if __name__ == '__main__':
    from copy import deepcopy
    g = Game()
    g2 = deepcopy(g)
    #g.play()
    g.swap((0,0), (1, 0))
    print(g)
    print('-'*30)
    print(g2)
