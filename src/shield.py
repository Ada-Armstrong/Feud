from piece import Piece, Pieces, Point, Action
from typing import List
from colour import Colour
from exceptions import ActionError

class Shield(Piece):

    def __init__(self, colour: Colour, pos: Point, hp: int=4):
        super().__init__(4, hp, False, colour, pos, True, False)

    def __str__(self):
        return f'{self._colour} S {self._hp} {self._active}'

    def canAction(self, targets: List['Piece'], pieces: Pieces) -> bool:
        return False

    def applyAction(self, targets: List['Piece'], pieces: Pieces) -> None:
        raise ActionError('Shield cannot perform an action')

    def listActions(self, pieces: Pieces) -> List[Action]:
        return []
