from game import Game, State
from bot import Bot
from math import sqrt, log
import random
import copy
import sys

#tmp
from colour import Colour


class Node:

    def __init__(self, state, parent, data=None):
        self.visits = 0
        self.wins = 0
        self.state = state
        self.parent = parent
        self.children = []
        self.data = copy.deepcopy(data)

    def __str__(self):
        return f'{self.visits=}, {self.wins=}, {self.data=}'

    def uct(self, n):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + 1.41 * sqrt(log(self.parent.visits)/n)

    def randomChild(self):
        return random.choice(self.children)

class MCTSBot(Bot):

    def chooseMove(self, time=None):
        self.sims = 0
        n_simulations = 1000
        root = Node(self.manager.game, None)

        for _ in range(n_simulations):
            if self.sims % 100 == 0:
                print(self.sims)
            self.sims += 1
            promising_node = self.selectPromisingNode(root)

            if promising_node.state.won == None:
                self.expandNode(promising_node)

            node_to_explore = promising_node if not promising_node.children else promising_node.randomChild()

            playout_res = self.simulatePlayout(node_to_explore)
            self.backprop(node_to_explore, playout_res)

        choice = max(root.children, key=lambda n : n.wins / n.visits)
        print(choice)

        return choice.data

    def selectPromisingNode(self, node):
        while node.children:
            node = max(node.children, key=lambda n : n.uct(self.sims))
        return node

    def expandNode(self, node):
        if node.state.state == State.SWAP:
            swaps = list(node.state.listSwaps())

            for swap in swaps:
                g = copy.deepcopy(node.state)
                g.swap(swap[0]._pos, swap[1]._pos)
                node.children.append(Node(g, node, swap))
        else:
            actions = node.state.listActions()

            for action in actions:
                g = copy.deepcopy(node.state)
                
                if action:
                    p = list(action.keys())[0]
                    g.action(p._pos, [x._pos for x in action[p]])
                else:
                    g.skipAction()
                node.children.append(Node(g, node, action))

    def simulatePlayout(self, node):
        tmp_state = copy.deepcopy(node.state)
        i = 0
        max_iters = 50

        while tmp_state.won == None and i < max_iters:
            i += 1
            if tmp_state.state == State.SWAP:
                swaps = list(tmp_state.listSwaps())
                try:
                    swap = random.choice(swaps)
                except Exception as e:
                    print(e)
                    print(tmp_state.state, tmp_state.turn)
                    print(tmp_state)
                    print(swaps)
                    sys.exit(1)
                tmp_state.swap(swap[0]._pos, swap[1]._pos)

            else:
                actions = tmp_state.listActions()
                try:
                    action = random.choice(actions)
                except:
                    print(tmp_state.state, tmp_state.turn)
                    print(tmp_state)
                    print(actions)
                    sys.exit(1)

                if action:
                    p = list(action.keys())[0]
                    tmp_state.action(p._pos, [x._pos for x in action[p]])
                else:
                    tmp_state.skipAction()

        return tmp_state.won

    def backprop(self, node, winner):
        while node:
            node.visits += 1
            if (node.state.state == State.SWAP and node.state.turn != winner) or (node.state.state == State.ACTION and node.state.turn == winner):
                node.wins += 1
            node = node.parent
