from piece import Piece, Pieces, Point, Action
from typing import List
from exceptions import ActionError

class Empty(Piece):

    def __init__(self, pos: Point, hp: int=0):
        super().__init__(0, hp, False, None, pos, False, False)

    def __str__(self):
        return '* * * *'

    def canAction(self, targets: List['Piece'], pieces: Pieces) -> bool:
        return False

    def applyAction(self, targets: List['Piece'], pieces: Pieces) -> None:
        raise ActionError('Empty can\'t perform an action')

    def listActions(self, pieces: Pieces) -> Action:
        return []
