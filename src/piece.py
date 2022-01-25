from abc import ABC, abstractmethod
from typing import Type, Optional, Tuple, Dict, List, Set
from exceptions import SwapError
from colour import Colour

Point = Tuple[int, int]
Pieces = Dict[Point, 'Piece']
Action = Dict['Piece', List['Piece']]

class Piece(ABC):
    '''
    An abstract base class for a Feud Piece. Implements swapping functionality.

    Attributes:
    _max_hp: The maximum number of hit points the piece can have.
    _hp: The current hit points the piece has.
    _active: A boolean that tracks whether the piece is active.
    _colour: The team which the piece belongs to.
    _pos: A tuple (x, y) representing the position of the piece on the board.
    _blocks: A boolean that tracks if the piece blocks projectiles.
    _swpable: A boolean that tracks if the piece is swapable by enemies.
    _max_trgts: The maximum number of pieces that can be targeted with an action.
    '''

    x_dir = [-1, 0, 1, 0]
    y_dir = [0, 1, 0, -1] 

    def __init__(
            self,
            max_hp: int,
            hp: int,
            active: bool,
            colour: Colour,
            pos: Point,
            blocks: bool,
            swapable: bool,
            max_trgts: int = 1
            ):
        self._max_hp: int = max_hp
        self._hp: int = min(hp, max_hp)
        self._active: bool = active
        self._colour: Optional[Colour] = colour
        self._pos: Point = pos
        self._blocks: bool = blocks
        self._swapable: bool = swapable
        self._max_trgts: int = max_trgts

    def neighbourPositions(self, boardWidth: int=4) -> List[Point]:
        return [ (x, y) for i in range(len(self.x_dir)) if 0 <= (x := self._pos[0]+self.x_dir[i]) < boardWidth and 0 <= (y := self._pos[1]+self.y_dir[i]) < boardWidth ]

    def distance(self, piece: 'Piece') -> int:
        return abs(self._pos[0]-piece._pos[0]) + abs(self._pos[1]-piece._pos[1])

    def index(self, boardWidth: int=4) -> int:
        return self._pos[0] + self._pos[1]*boardWidth

    def takeDmg(self) -> None:
        self._hp -= 1

        if self._hp <= 0:
            self._active = False
            self._swapable = False
            self._blocks = False
            self._colour = None

    def heal(self) -> None:
        self._hp = min(self._max_hp, self._hp + 1)

    def updateActivity(self, pieces: Pieces) -> None:
        if self._hp > 0:
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
        if not self._active:
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

