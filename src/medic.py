from piece import Piece, Pieces, Point, Action
from typing import List
from colour import Colour
from exceptions import ActionError
from itertools import combinations

class Medic(Piece):

    def __init__(self, colour: Colour, pos: Point, hp: int=3):
        super().__init__(3, hp, False, colour, pos, False, True, 4)

    def __str__(self):
        return f'{self._colour} M {self._hp} {self._active}'

    def canAction(self, targets: List['Piece'], pieces: Pieces) -> bool:
        if not (1 <= len(targets) <= 4 and self._active):
            return False

        for t in targets:
            if self._colour != t._colour or t._hp <= 0 or t._hp == t._max_hp or self.distance(t) != 1:
                return False

        return True

    def applyAction(self, targets: List['Piece'], pieces: Pieces) -> None:
        if not self.canAction(targets, pieces):
            raise ActionError('can\'t apply action')
        
        for t in targets:
            t.heal()

    def listActions(self, pieces: Pieces) -> List[Action]:
        if not self._active:
            return []

        actions = []
        neighbours = [ pieces[i] for i in self.neighbourPositions() if self.canAction([pieces[i]], pieces) ]

        for k in [1, 2, 3, 4]:
            for subset in combinations(neighbours, k):
                actions.append({self:list(subset)})

        return actions
