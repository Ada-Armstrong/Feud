from piece import Piece, Pieces, Point, Action
from typing import List
from colour import Colour
from exceptions import ActionError
from itertools import combinations

class Knight(Piece):

    def __init__(self, colour: Colour, pos: Point, hp: int=3):
        super().__init__(3, hp, False, colour, pos, False, True, 2)

    def __str__(self):
        return 'N ' + super().__str__()

    def canAction(self, targets: List['Piece'], pieces: Pieces) -> bool:
        if not (1 <= len(targets) <= 2 and self._active):
            return False

        for t in targets:
            if self._colour == t._colour or t._hp <= 0 or self.distance(t) != 1:
                return False

        return True

    def applyAction(self, targets: List['Piece'], pieces: Pieces) -> None:
        if not self.canAction(targets, pieces):
            raise ActionError('can\'t apply action')
        
        for t in targets:
            t.takeDmg()

    def listActions(self, pieces: Pieces) -> List[Action]:
        if not self._active:
            return []

        actions = []
        neighbours = [ pieces[i] for i in self.neighbourPositions() if self.canAction([pieces[i]], pieces) ]

        for k in [1, 2]:
            for subset in combinations(neighbours, k):
                actions.append({self:list(subset)})

        return actions
