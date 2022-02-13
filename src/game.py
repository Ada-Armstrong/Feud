import logging
from typing import Type, Dict, List, Set, Tuple, Optional
from enum import Enum
from queue import Queue
from copy import deepcopy

from piece import Piece, Pieces, Point, Action
from colour import Colour
from exceptions import SwapError, ActionError, BoardError, InputError
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
    """
    Represents the board and game state for Feud.

    Attributes:
        WIDTH: The width of the board.
        HEIGHT: The HEIGHT of the board.
        max_passes: The maximum number of passes a player can do before forfeiting.
        won: The team Colour which has won.
        state: Whether the game is in SWAP or ACTION.
        turn: Whose turn it is to play.
        passes: A dict containing the number of passes for each player.
        pieces: A dict mapping each position on the board to a piece.
        team_pieces: A dict which contains a list for each player's pieces.
        kings: A dict that tracks the location of each team's king.
    """

    def __init__(self):
        self.WIDTH: int = 4
        self.HEIGHT: int = 4
        self.max_passes: int = 2

        self.resetBoard()

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

    def resetBoard(self) -> None:
        """
        Changes the board's state so that it is ready for a new game.

        Returns:
            None
        """
        self.won: Optional[Colour] = None
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

    def _str2cord(self, string: str) -> Tuple[int, int]:
        """
        Converts a string that represents a coordinate on the board to a tuple
        containing the (col, row) indices. The string must be in the following
        format: [a-d][1-4]

        Args:
            string: The coordinate string.

        Returns:
            A tuple, column by row, that the string coordinate represented on the board.

        Raises:
            InputError: If string is not in the correct format.
        """
        if len(string) != 2:
            raise InputError('Too many characters provided as coordinate')

        try:
            col = ord(string[0].lower()) - ord('a')
            row = int(string[1]) - 1
        except TypeError as e:
            raise InputError('Coordinate must be in the format [a-d][1-4]')

        return (col, row)

    def _cord2str(self, cord: Tuple[int, int]) -> str:
        """
        Inverse of _str2cord. Returns the string representation of the board
        coordinate.

        Args:
            cord: The coordinate on the board to convert (col, row).

        Returns:
            A string representation of the board coordinate. Will be in the
            following format: [a-d][1-4]
        """
        return chr(cord[0] + ord('a')) + str(cord[1] + 1)


    def _winnerFromBools(self, black: bool, white: bool) -> Colour:
        """
        Helper function that returns a colour according to the arguments. 

        Args:
            black: whether black satisfies the condition.
            white: whether white satisfies the condition.

        Returns:
            The colour which satisfies the condition.
        """
        if black and white:
            return Colour.BOTH
        elif black:
            return Colour.BLACK
        elif white:
            return Colour.WHITE
        else:
            return None

    def isolated(self) -> Colour:
        """
        Checks if either team is isolated.

        Returns:
            The colour which is isolated.
        """
        black = sum([p._active for p in self.team_pieces[Colour.BLACK]]) == 0
        white = sum([p._active for p in self.team_pieces[Colour.WHITE]]) == 0

        return self._winnerFromBools(black, white)


    def kingDead(self) -> Colour:
        """
        Checks if the kings are alive.

        Returns:
            The colour for which the king is dead.
        """
        black = self.kings[Colour.BLACK]._hp <= 0
        white = self.kings[Colour.WHITE]._hp <= 0

        return self._winnerFromBools(black, white)

    def tooManyPasses(self) -> Colour:
        """
        Checks if either team has exceed the allowed number of passes.

        Returns:
            The colour which has exceed the allowed number of passes.
        """
        black = self.passes[Colour.BLACK] > self.max_passes
        white = self.passes[Colour.WHITE] > self.max_passes

        return self._winnerFromBools(black, white)

    def setBoard(self) -> None:
        """
        Configures the pieces in their starting position and updates their
        activity flags.

        Returns:
            None
        """
        # first row
        self.pieces[(0, 0)] = Archer(Colour.BLACK, (0, 0))
        self.pieces[(1, 0)] = King(Colour.BLACK, (1, 0))
        self.pieces[(2, 0)] = Medic(Colour.BLACK, (2, 0))
        self.pieces[(3, 0)] = Archer(Colour.BLACK, (3, 0))
        # second row
        self.pieces[(0, 1)] = Knight(Colour.BLACK, (0, 1))
        self.pieces[(1, 1)] = Shield(Colour.BLACK, (1, 1), hp=3)
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
        """
        Sets the kings variable to track the location of the kings.

        Returns:
            None
        """

        for p in self.pieces:
            piece = self.pieces[p]

            if type(piece) is King and piece._colour:
                self.kings[piece._colour] = piece

    def addPiecesToTeams(self) -> None:
        """
        Sets the self.team_pieces dict.

        Returns:
            None
        """
        self.team_pieces[Colour.BLACK].clear()
        self.team_pieces[Colour.WHITE].clear()

        for i in self.pieces:
            if self.pieces[i]._colour is not None:
                self.team_pieces[self.pieces[i]._colour].append(self.pieces[i])

    def _inbound(self, pos: Point) -> bool:
        """
        Checks if pos is within the board.

        Args:
            pos: The point to check.

        Returns:
            True if pos is within the board dimensions, else False.
        """
        return 0 <= pos[0] <= self.WIDTH and 0 <= pos[1] <= self.HEIGHT

    def canSwap(self, pos1: Point, pos2: Point) -> bool:
        """
        Checks if swapping pos1 and pos2 is legal.

        Args:
            pos1: First position on the board.
            pos2: Second position on the board.

        Returns:
            True if the swap is legal, else False.
        """
        if (self.state != State.SWAP 
                or not self._inbound(pos1)
                or not self._inbound(pos2)):
            return False

        p1 = self.pieces[pos1]
        p2 = self.pieces[pos2]

        return ((p1._colour == self.turn and p1.canSwap(p2))
                or (p2._colour == self.turn and p2.canSwap(p1)))

    def swap(self, pos1: Point, pos2: Point, notify=None) -> None:
        """
        Performs the swap (pos1, pos2) if it is legal.

        Args:
            pos1: First position on the board.
            pos2: Second position on the board.

        Returns:
            None

        Raises:
            SwapError: If the swap is not legal.
        """
        if not self.canSwap(pos1, pos2):
            raise SwapError(f'{pos1=} and {pos2=} cannot be swapped') 

        p1 = self.pieces[pos1]
        p2 = self.pieces[pos2]

        p1.applySwap(p2)

        self.pieces[pos1], self.pieces[pos2] = p2, p1

        # update activity of pieces and neighbours
        for i in p1.neighbourPositions():
            self.pieces[i].updateActivity(self.pieces)
            if notify is not None:
                notify(i)

        for i in p2.neighbourPositions():
            self.pieces[i].updateActivity(self.pieces)
            if notify is not None:
                notify(i)

        self.state = State.ACTION

        loser = self.isolated()

        if loser == Colour.BLACK:
            self.won = Colour.WHITE
        elif loser == Colour.WHITE:
            self.won = Colour.BLACK
        elif loser == Colour.BOTH:
            self.won = Colour.BOTH

    def canAction(self, pos: Point, targets: List[Point]) -> bool:
        """
        Checks if the piece at pos can perform an action on targets.

        Args:
            pos: The position of the piece on the board to perform the action.
            targets: A list of positions to target with an action.

        Returns:
            True if the swap is legal, else False.
        """
        if (self.state != State.ACTION
                or not self._inbound(pos)
                or self.pieces[pos]._colour != self.turn
                or sum([not self._inbound(p) for p in targets])):
            return False

        trgts = [self.pieces[p] for p in targets]

        return self.pieces[pos].canAction(trgts, self.pieces)

    def action(self, pos: Point, targets: List[Point], notify=None) -> None:
        """
        Performs the action if it is legal.

        Args:
            pos: The position of the piece on the board to perform the action.
            targets: A list of positions to target with an action.

        Returns:
            None

        Raises:
            ActionError: If the action is not legal.
        """
        if not self.canAction(pos, targets):
            raise ActionError(f'Can\'t perform action {pos} {targets}')

        action_piece = self.pieces[pos]
        trgts = [self.pieces[p] for p in targets]

        action_piece.applyAction(trgts, self.pieces)
        action_piece.updateActivity(self.pieces)

        if notify is not None:
            notify(action_piece._pos)

        for piece in trgts:
            piece.updateActivity(self.pieces)

            if notify is not None:
                notify(piece._pos)

            for i in piece.neighbourPositions():
                self.pieces[i].updateActivity(self.pieces)
                if notify is not None:
                    notify(i)

        self.passes[self.turn] = 0
        self.state = State.SWAP
        self.turn = Colour.BLACK if self.turn == Colour.WHITE else Colour.WHITE

        loser = self.isolated() or self.kingDead()

        if loser == Colour.BLACK:
            self.won = Colour.WHITE
        elif loser == Colour.WHITE:
            self.won = Colour.BLACK
        elif loser == Colour.BOTH:
            self.won = Colour.BOTH

    def skipAction(self) -> None:
        """
        Skips the current player's turn action.

        Returns:
            None
        """
        self.passes[self.turn] += 1
        self.state = State.SWAP
        self.turn = Colour.BLACK if self.turn == Colour.WHITE else Colour.WHITE

        loser = self.tooManyPasses()

        if loser == Colour.BLACK:
            self.won = Colour.WHITE
        elif loser == Colour.WHITE:
            self.won = Colour.BLACK
        elif loser == Colour.BOTH:
            self.won = Colour.BOTH

    def listSwaps(self) -> Set[Tuple[Piece]]:
        """
        Returns the legal swaps.
        
        Returns:
            A set of tuples which present the legal swaps for the board. Each
            tuple contians two positions on the board.
        """
        out = set()
        
        if self.state == State.SWAP:
            team = self.team_pieces[self.turn]

            for p in team:
                out.update(p.listSwaps(self.pieces))

        return out

    def listActions(self) -> List[Action]:
        """
        Returns the legal actions. The empty dict represents the skip action.
        
        Returns:
            A list of actions. See piece.py for the definition of an Action.
        """
        out = [{}]

        if self.state == State.ACTION:
            team = self.team_pieces[self.turn]

            for p in team:
                out += p.listActions(self.pieces)

        return out


class GameManager:
    """
    Manages the board and game state for Feud.

    Attributes:
        game: The representation of the game.
        msg_types: A list of legal message types for subscribe and notify.
        subscribers: A dict containing the callback functions for each message type.
        input_queue: A queue that stores the moves to be played.
    """

    def __init__(self):
        self.game = Game()

        self.msg_types = ['board', 'turn', 'finished']
        self.subscribers = {msg_type:[] for msg_type in self.msg_types}
        self.input_queue = Queue()

    def dims(self):
        return (self.game.WIDTH, self.game.HEIGHT)

    def turn(self):
        return self.game.turn

    def state(self):
        return self.game.state

    def won(self):
        return self.game.won

    def pieces(self):
        return self.game.pieces

    def resetBoard(self):
        self.game.resetBoard()

    def passes(self):
        # TODO: temporary
        return self.game.passes.values()

    def subscribe(self, callback, msg_type='board') -> None:
        """
        Subscribes a callback function to a specific msg_type. For example
        msg_type=board calls the callback function whenever a piece is moved or
        mutated on the board.

        Args:
            callback: The callback function to run when notify is called for the
                        message type. For msg_type=board the callback must take
                        pos, string
            msg_type: A string representing the types of message to subscribe to.

        Returns:
            None

        Raises:
            TypeError: If msg_type is not valid.
        """
        if msg_type not in self.msg_types:
            raise TypeError(f'{msg_type} not a valid msg_type')
        self.subscribers[msg_type].append(callback)

    def notify(self, pos=None, msg_type: str='board') -> None:
        """
        Runs the callback functions for a specific msg_type.

        Args:
            msg_type: A string representing the types of message to run callback
                        functions for.

        Returns:
            None

        Raises:
            TypeError: If msg_type is not valid.
        """
        if msg_type not in self.msg_types:
            raise TypeError(f'{msg_type} not a valid msg_type')

        if msg_type == 'board':
            data = [pos, str(self.game.pieces[pos])]
        elif msg_type == 'turn':
            data = [str(self.turn()), str(self.state())]
        elif msg_type == 'finished':
            data = [str(self.won())]

        for callback in self.subscribers[msg_type]:
            callback(*data)

    def addInput(self, in_str: str) -> None:
        """
        Queues a move.

        Args:
            in_str: The move to queue in string format. See _str2cord for the
                        format that the string should be in.

        Returns:
            None
        """
        self.input_queue.put(in_str)

    def getInput(self) -> str:
        """
        Retrieves the first element in the input queue.

        Returns:
            A string representing a move.
        """
        return self.input_queue.get()

    def cord2str(self, p):
        return self.game._cord2str(p)

    def str2cord(self, s):
        return self.game._str2cord(s)

    def listSwaps(self):
        return self.game.listSwaps()

    def listActions(self):
        return self.game.listActions()

    def swap(self, pos1: Point, pos2: Point) -> None:
        self.game.swap(pos1, pos2, self.notify)

    def action(self, pos: Point, targets: List[Point]) -> None:
        self.game.action(pos, targets, self.notify)

    def play(self) -> None:
        """
        Starts the game loop.

        Returns:
            None
        """
        while 1:
            logging.debug(self.game)

            if loser := (self.game.isolated() or self.game.kingDead() or self.game.tooManyPasses()):
                if loser == Colour.BLACK:
                    self.game.won = Colour.WHITE
                elif loser == Colour.WHITE:
                    self.game.won = Colour.BLACK
                else:
                    self.game.won = Colour.BOTH

                logging.debug(f'{self.won} won')
                self.notify(msg_type='finished')
                break

            self.notify(msg_type='turn')

            if self.state() == State.SWAP:
                logging.debug(f'{self.game.turn} to swap')

                while 1:
                    start, end = self.getInput().split()
                    logging.debug(f'{start} {end}')

                    try:
                        start_fmt = self.game._str2cord(start) 
                        end_fmt = self.game._str2cord(end)
                    except InputError as e:
                        logging.warning(e)
                        continue

                    try:
                        self.swap(start_fmt, end_fmt)
                        break
                    except SwapError as e:
                        logging.warning(e)

            else:
                logging.debug(f'{self.game.turn} to action')

                while 1:
                    str_cords = self.getInput().split()
                    logging.debug(str_cords)

                    try:
                        cords = [self.game._str2cord(s) for s in str_cords]
                    except InputError as e:
                        logging.warning(e)
                        continue

                    if len(cords) == 0:
                        self.game.skipAction()
                        break

                    if len(cords) < 2:
                        logging.warning('Need at least 2 cordinates to preform an action')
                        continue

                    try:
                        self.action(cords[0], cords[1:])
                        break
                    except ActionError as e:
                        logging.warning(e)
    

if __name__ == '__main__':
    g = Game()
    g2 = deepcopy(g)
    g2.swap((0,0), (1,0))

    print(g)
    print('*'*50)
    print(g2)
