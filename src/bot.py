from game import Game, State
from exceptions import TurnError
import logging
import time
import random

class Bot:

    def __init__(self, game_manager, team):
        self.manager = game_manager
        self.team = team

    def moveCallback(self, turn_str, state_str):
        if str(self.team) == turn_str:
            time.sleep(1)
            self.makeMove()

    def makeMove(self, time=None):
        if self.manager.turn() != self.team:
            raise TurnError("Not the bot's turn")
        elif self.manager.won() is not None:
            raise TurnError("The game is over")

        move = self.chooseMove(time)
        if self.manager.state() == State.SWAP:
            move = self.swap2str(move)
        else:
            move = self.action2str(move)
        self.manager.addInput(move)

    def chooseMove(self, time=None):
        raise NotImplementedError

    def swap2str(self, swap):
        out = f'{self.manager.cord2str(swap[0]._pos)} {self.manager.cord2str(swap[1]._pos)}'
        logging.info('Bot Swap: ' + out)
        return out

    def action2str(self, action):
        if not action:
            out = ''
        else:
            piece = list(action.keys())[0]
            out = f'{self.manager.cord2str(piece._pos)} '
            out += ' '.join([self.manager.cord2str(p._pos) for p in action[piece]])

        logging.info('Bot Action: ' + out)
        return out 

class RandomBot(Bot):

    def chooseMove(self, time=None):
        if self.manager.state() == State.SWAP:
            swaps = list(self.manager.listSwaps())
            return random.choice(swaps)
        else:
            actions = self.manager.listActions()
            return random.choice(actions)

