import logging
import socket
import packet
from game import Game, State
from exceptions import SwapError, ActionError


class GameServer:
    '''
    Server to sync clients game instances.
    '''
    def __init__(self, ip='localhost', port=60555):
        self.NUM_PLAYERS = 2
        self.IP = ip
        self.PORT = port

        self.game = Game()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.IP, self.PORT))
        self.socket.listen()
        logging.info(f'Server started on {ip}:{port}')

    def shutdown(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def connectPlayers(self):
        self.players = []

        for i in range(self.NUM_PLAYERS):
            conn, addr = self.socket.accept()
            self.goodCommand(conn, packet.CONNECTED_CMD, f'{i}')

            logging.debug(f'Player connected from {addr}')
            self.players.append(conn)

    def play(self):
        if not self.players or len(self.players) != 2:
            return

        while 1:
            if loser := (self.game.isolated() or self.game.kingDead()):
                self.goodCommand(self.players, packet.QUIT_CMD, f'Player {loser} lost')

                for p in self.players:
                    p.close()
                return

            player = self.players[self.game.turn.value]

            request_to_player = packet.SWAP_CMD if self.game.state == State.SWAP else packet.ACTION_CMD
            # send sync message to player
            self.goodCommand(player, packet.SYNC_CMD, request_to_player)
            
            status_code, cmd, msg = self.recv(player)
            # used in case an error occurs
            player_input = cmd + f' {packet.SEPERATOR} ' + msg

            if cmd == packet.QUIT_CMD:
                self.quit_cmd()
                return
            elif cmd == packet.SWAP_CMD:
                if not self.swap_cmd(player, msg):
                    continue
            elif cmd == packet.ACTION_CMD:
                if not self.action_cmd(player, msg):
                    continue
            else:
                # unknown command
                self.badCommand(player, packet.ERROR_CMD, f'Unknown command')
                continue

            self.goodCommand(self.players, cmd, msg)
            # TODO: temporary
            logging.debug('*' * 50)
            logging.debug(self.game)

    def quit_cmd(self):
        self.goodCommand(self.players, packet.QUIT_CMD, f'Player {self.game.turn} quit')

        for p in self.players:
            p.close()

    def swap_cmd(self, player, msg):
        args = msg.split()

        try:
            if self.game.state != State.SWAP or len(args) != 2:
                raise RuntimeError('Wrong state')

            pos1 = self.game._str2cord(args[0])
            pos2 = self.game._str2cord(args[1])
        except:
            logging.warning(f'{packet.ERROR_CMD} {packet.SEPERATOR} Bad command "{player_input}"')
            self.badCommand(player, packet.ERROR_CMD, f'Bad command')
            return False

        try:
            self.game.swap(pos1, pos2)
        except SwapError as e:
            self.badCommand(player, packet.ERROR_CMD, str(e))
            return False

        return True

    def action_cmd(self, player, msg):
        args = msg.split()

        try:
            if self.game.state != State.ACTION:
                raise RuntimeError('Wrong state')

            if len(args) == 0:
                self.game.skipAction()
            else:
                poses = [self.game._str2cord(p) for p in args]
                try:
                    self.game.action(poses[0], poses[1:])
                except ActionError as e:
                    self.badCommand(player, packet.ERROR_CMD, str(e))
                    return False
        except Exception as e:
            logging.warning(f'{packet.ERROR_CMD} {packet.SEPERATOR} Bad command "{player_input}"')
            self.badCommand(player, packet.ERROR_CMD, f'Bad command')
            return False

        return True

    def recv(self, conn):
        return packet.recv(conn)

    def badCommand(self, targets, cmd, error_msg):
        packet.send(targets, packet.STATUS_CODE_FAILURE, cmd, error_msg)

    def goodCommand(self, targets, cmd, msg):
        packet.send(targets, packet.STATUS_CODE_SUCCESS, cmd, msg)

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s <%(asctime)s> %(message)s', level=logging.DEBUG)
    server = GameServer()

    try:
        server.connectPlayers()
        server.play()
    except Exception as e:
        logging.error(e)
    finally:
        server.shutdown()
