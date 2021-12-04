from abc import ABC, abstractmethod
from typing import Type, Optional, Tuple, Dict, List, Set
from exceptions import SwapError
from colour import Colour

Point = Tuple[int, int]
Pieces = Dict[Point, 'Piece']
Action = Dict['Piece', List['Piece']]

class Piece(ABC):
    '''
    An abstract base class for a Feud Piece.
    Implements swapping functionality.
    '''
    def __init__(
            self,
            max_hp: int,
            hp: int,
            active: bool,
            colour: Colour,
            pos: Point,
            blocks: bool,
            swapable: bool
            ):
        self._max_hp: int = max_hp
        self._hp: int = hp
        self._active: bool = active
        self._colour: Optional[Colour] = colour
        self._pos: Point = pos
        self._blocks: bool = blocks
        self._swapable: bool = swapable

    def neighbourPositions(self, boardWidth: int=4) -> List[Point]:
        x_dir = [-1, 0, 1, 0]
        y_dir = [0, 1, 0, -1]
        return [ (x, y) for i in range(len(x_dir)) if 0 <= (x := self._pos[0]+x_dir[i]) < boardWidth and 0 <= (y := self._pos[1]+y_dir[i]) < boardWidth ]

    def distance(self, piece: 'Piece') -> int:
        return abs(self._pos[0]-piece._pos[0]) + abs(self._pos[1]-piece._pos[1])

    def index(self, boardWidth: int=4) -> int:
        return self._pos[0] + self._pos[1]*boardWidth

    def takeDmg(self) -> None:
        self._hp -= 1

        if self._hp <= 0:
            self._swapable = False
            self._blocks = False
            self.colour = None

    def heal(self) -> None:
        self._hp = max(self._max_hp, self._hp + 1)

    def updateActivity(self, pieces: Pieces) -> None:
        for i in self.neighbourPositions():
            if self._colour == pieces[i]._colour:
                self._active = True
                return

        self._active = False

    def canSwap(self, piece: 'Piece') -> bool: 
        return ((self._colour == piece._colour or piece._swapable)
                and self._active
                and self.distance(piece) == 1)

    def applySwap(self, piece: 'Piece') -> None:
        if not self.canSwap(piece):
            raise SwapError('{self} and {piece} are not swapable')

        self._pos, piece._pos = piece._pos, self._pos

    def listSwaps(self, pieces: Pieces) -> Set[Tuple['Piece', 'Piece']]:
        if not (self._active and self._swapable):
            return set()

        indices = self.neighbourPositions()
        out = set()

        for i in indices:
            if self.canSwap(pieces[i]):
                p1, p2 = self, pieces[i]
                if self.index() > pieces[i].index():
                    p1, p2 = pieces[i], self
                out.add((p1, p2))

        return out

    @abstractmethod
    def canAction(self, targets: List['Piece'], pieces: Pieces) -> bool:
        pass

    @abstractmethod
    def applyAction(self, targets: List['Piece'], pieces: Pieces) -> None:
        pass

    @abstractmethod
    def listActions(self, pieces: Pieces) -> List[Action]:
        pass
