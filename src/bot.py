from game import Game, State
from exceptions import TurnError
import logging
import time
import random

class Bot:

    def __init__(self, game, team):
        self.game = game
        self.team = team

    def moveCallback(self, turn_str, state_str):
        if str(self.team) == turn_str:
            time.sleep(1)
            self.makeMove()

    def makeMove(self, time=None):
        if self.game.turn != self.team:
            raise TurnError("Not the bot's turn")
        elif self.game.won is not None:
            raise TurnError("The game is over")

        move = self.chooseMove(time)
        self.game.addInput(move)

    def chooseMove(self, time=None):
        raise NotImplementedError

    def swap2str(self, swap):
        out = f'{self.game._cord2str(swap[0]._pos)} {self.game._cord2str(swap[1]._pos)}'
        logging.info('Bot Swap: ' + out)
        return out

    def action2str(self, action):
        piece = list(action.keys())[0]
        out = f'{self.game._cord2str(piece._pos)} '
        out += ' '.join([self.game._cord2str(p._pos) for p in action[piece]])
        logging.info('Bot Action: ' + out)
        return out


class RandomBot(Bot):

    def chooseMove(self, time=None):
        if self.game.state == State.SWAP:
            swaps = list(self.game.listSwaps())
            swap = random.choice(swaps)

            return self.swap2str(swap)
        else:
            actions = self.game.listActions()
            action = random.choice(actions)

            return self.action2str(action)

