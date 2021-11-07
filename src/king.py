from piece import Piece, Pieces, Point, Action
from colour import Colour
from typing import List
from exceptions import ActionError

class King(Piece):

    def __init__(self, colour: Colour, pos: Point, hp: int=4):
        super().__init__(4, hp, False, colour, pos, False, True)

    def __str__(self):
        return f'{self._colour} K {self._hp} {self._active}'

    def canAction(self, targets: List['Piece'], pieces: Pieces) -> bool:
        return (len(targets) == 1
                and self._active
                and self._colour != targets[0]._colour
                and targets[0]._hp > 0
                and self.distance(targets[0]) == 1)

    def applyAction(self, targets: List['Piece'], pieces: Pieces) -> None:
        if not self.canAction(targets, pieces):
            raise ActionError('can\'t apply action')
        
        targets[0].takeDmg()

    def listActions(self, pieces: Pieces) -> List[Action]:
        if not self._active:
            return []

        indices = self.neighbourPositions()

        return [ {self:[pieces[i]]} for i in indices if self.canAction([pieces[i]], pieces) ]

