from piece import Piece, Pieces, Point, Action
from typing import List, Dict
from colour import Colour
from exceptions import ActionError

class Archer(Piece):

    def __init__(self, colour: Colour, pos: Point, hp: int=3):
        super().__init__(3, hp, False, colour, pos, False, True)

    def __str__(self):
        return f'{self._colour} A {self._hp} {self._active}'

    def _inSameCol(self, piece: Piece) -> bool:
        return self._pos[0] == piece._pos[0]

    def _inSameRow(self, piece: Piece) -> bool:
        return self._pos[1] == piece._pos[1]

    def _isBlocker(self, dir: Point, iters: int, pieces: Dict[Point, Piece]) -> bool:
        for i in range(1, iters):
            pos = (self._pos[0]+i*dir[0], self._pos[1]+i*dir[1])
            piece = pieces[pos]

            if self._colour != piece._colour and piece._blocks:
                return True

        return False

    def canAction(self, targets: List['Piece'], pieces: Pieces) -> bool:
        if not (len(targets) == 1
                and self._active
                and self._colour != targets[0]._colour
                and targets[0]._hp > 0
                and (self._inSameCol(targets[0]) or self._inSameRow(targets[0]))):
            return False

        target = targets[0]

        x_dir = target._pos[0] - self._pos[0]
        y_dir = target._pos[1] - self._pos[1]
        dir = (x_dir//abs(x_dir) if x_dir else 0, y_dir//abs(y_dir) if y_dir else 0)
        iters = abs(x_dir) + abs(y_dir)

        return not self._isBlocker(dir, iters, pieces)
        
    def applyAction(self, targets: List['Piece'], pieces: Pieces) -> None:
        if not self.canAction(targets, pieces):
            raise ActionError('can\'t apply action')
        
        targets[0].takeDmg()

    def listActions(self, pieces: Pieces) -> List[Action]:
        if not self._active:
            return []

        # not the most effiecent way
        return [ {self:[pieces[p]]} for p in pieces if self.canAction([pieces[p]], pieces) ]
