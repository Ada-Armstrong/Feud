from game import Game, State
from bot import Bot
from colour import Colour
import copy


class Node:

    def __init__(self, state, parent, data=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.data = copy.deepcopy(data)
        self.value = 0

    def __str__(self):
        return f'{self.state}\n{self.visits=}, {self.wins=}, {self.data=}'

    def expand(self):
        if self.state.state == State.SWAP:
            swaps = list(self.state.listSwaps())

            for swap in swaps:
                g = copy.deepcopy(self.state)
                g.swap(swap[0]._pos, swap[1]._pos)
                self.children.append(Node(g, self, swap))
        else:
            actions = self.state.listActions()

            for action in actions:
                g = copy.deepcopy(self.state)
                if action:
                    p = list(action.keys())[0]
                    g.action(p._pos, [x._pos for x in action[p]])
                else:
                    g.skipAction()
                self.children.append(Node(g, self, action))


class AlphaBetaBot(Bot):

    def chooseMove(self, time=None):
        # set the depth dynamically based on the number of alive pieces
        depth = 12 - self.numberOfAlivePieces()//2
        root = Node(self.manager.game, None)
        self.visited = 0

        self.alphaBeta(root, depth, float('-inf'), float('inf'), self.manager.game.turn)

        choice = max(root.children, key=lambda n : n.value)
        print(f'Visited {self.visited} nodes')
        print(choice.data)

        return choice.data

    def numberOfAlivePieces(self):
        count = 0

        for p in self.manager.game.pieces:
            if self.manager.game.pieces[p]._hp > 0:
                count += 1

        return count

    def stateHeuristic(self, node, maximizing_player):
        if node.state.won == Colour.BOTH:
            value = 0.
        elif node.state.won == Colour.BLACK:
            value = float('inf')
        elif node.state.won == Colour.WHITE:
            value = float('-inf')
        else:
            # want alive and active pieces
            scores = {Colour.BLACK: 0., Colour.WHITE: 0.}
            for p in node.state.pieces:
                piece = node.state.pieces[p]
                if piece._hp <= 0:
                    continue
                scores[piece._colour] += 2 * piece._hp if piece._active else piece._hp

            value =  scores[Colour.BLACK] - scores[Colour.WHITE]

        return value if maximizing_player == Colour.BLACK else -value

    def alphaBeta(self, node, depth, a, b, maximizing_player):
        self.visited += 1
        if self.visited % 1000 == 0:
            print(self.visited)

        if depth <= 0 or node.state.won is not None:
            node.value = self.stateHeuristic(node, maximizing_player)
            return node.value

        node.expand()

        if maximizing_player == node.state.turn:
            value = float('-inf')
            for child in node.children:
                node.value = max(value, self.alphaBeta(child, depth-1, a, b, maximizing_player))
                value = node.value
                if value >= b:
                    break
                a = max(a, value)
        else:
            value = float('inf')
            for child in node.children:
                node.value = min(value, self.alphaBeta(child, depth-1, a, b, maximizing_player))
                value = node.value
                if value <= a:
                    break
                b = min(b, value)

        return value
