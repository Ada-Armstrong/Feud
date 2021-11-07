from piece import Piece, Pieces, Point, Action
from typing import List
from colour import Colour
from exceptions import ActionError

class Wizard(Piece):

    def __init__(self, colour: Colour, pos: Point, hp: int=3):
        super().__init__(3, hp, False, colour, pos, False, True)

    def __str__(self):
        return f'{self._colour} W {self._hp} {self._active}'

    def canAction(self, targets: List['Piece'], pieces: Pieces) -> bool:
        return (len(targets) == 1
                and self._active
                and self._colour == targets[0]._colour
                and targets[0]._hp > 0)

    def applyAction(self, targets: List['Piece'], pieces: Pieces) -> None:
        if not self.canAction(targets, pieces):
            raise ActionError('can\'t apply action')

        target = targets[0]

        pieces[self._pos], pieces[target._pos] = target, self
        self._pos, target._pos = target._pos, self._pos

    def listActions(self, pieces: Pieces) -> List[Action]:
        if not self._active:
            return []

        return [ {self:[pieces[p]]} for p in pieces if pieces[p] != self and self.canAction([pieces[p]], pieces) ]
