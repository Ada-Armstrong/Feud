import socket
from game import Game, State
import packet


class GameServer:
    def __init__(self, ip='localhost', port=60555):
        self.NUM_PLAYERS = 2
        self.IP = ip
        self.PORT = port

        self.game = Game()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.IP, self.PORT))
        self.socket.listen()
        print(f'Server started on {ip}:{port}')

    def __del__(self):
        self.socket.close()

    def connectPlayers(self):
        self.players = []

        for i in range(self.NUM_PLAYERS):
            conn, addr = self.socket.accept()
            self.goodCommand([conn], f'{packet.CONNECTED_CMD} {packet.SEPERATOR} {i}')

            print(f'Player connected from {addr}')
            self.players.append(conn)

    def play(self):
        if not self.players or len(self.players) != 2:
            return

        while 1:
            player = self.players[self.game.turn.value]

            # send sync message to player
            self.goodCommand(
                    [player],
                    f'{packet.SYNC_CMD} {packet.SEPERATOR} Your turn'
                    )
            
            status_code, cmd, msg = self.recv(player)
            # used in case an error occurs
            player_input = cmd + f' {packet.SEPERATOR} ' + msg

            if cmd == packet.QUIT_CMD:
                self.goodCommand(
                        self.players,
                        f'{packet.QUIT_CMD} {packet.SEPERATOR} Player {player} quit'
                        )
                for p in self.players:
                    p.close()
                return
            elif cmd == packet.SWAP_CMD:
                args = msg.split()

                try:
                    if self.game.state != State.SWAP or len(args) != 2:
                        raise
                    pos1 = self.game._str2cord(args[0])
                    pos2 = self.game._str2cord(args[1])
                except:
                    self.badCommand(
                            [player],
                            f'{packet.ERROR_CMD} {packet.SEPERATOR} Bad command "{player_input}"'
                            )
                    continue

                try:
                    self.game.swap(pos1, pos2)
                except SwapError as e:
                    self.badCommand(
                            [player],
                            '{packet.ERROR_CMD} {packet.SEPERATOR} ' + str(e)
                            )
                    continue
            elif cmd == packet.ACTION_CMD:
                args = msg.split()

                try:
                    if self.game.state != State.Action:
                        raise

                    num_args = len(args)

                    if num_args == 0:
                        self.game.skipAction()
                    else:
                        poses = [self._str2cords(p) for p in args]
                except:
                    self.badCommand(
                            [player],
                            f'{packet.ERROR_CMD} {packet.SEPERATOR} Bad command {player_input}'
                            )
                    continue

                try:
                    self.game.action(poses[0], poses[1:])
                except ActionError as e:
                    self.badCommand(
                            player,
                            '{packet.ERROR_CMD} {packet.SEPERATOR} ' + str(e)
                            )
                    continue
            else:
                # unknown command
                self.badCommand(
                        [player],
                        '{packet.ERROR_CMD} {packet.SEPERATOR} Unknown command'
                        )
                continue

            self.goodCommand(self.players, player_input)
            # TODO: temporary
            print(self.game)

    def recv(self, conn):
        return packet.recv(conn)

    def badCommand(self, targets, error_msg):
        data = f'{packet.STATUS_CODE_SUCCESS}:' + error_msg
        data = data.encode('utf-8')

        for conn in targets:
            conn.sendall(data)

    def goodCommand(self, targets, msg):
        data = '{packet.STATUS_CODE_FAILURE}:' + msg
        print(f'Sending {data}')
        data = data.encode('utf-8')

        for conn in targets:
            conn.sendall(data)

if __name__ == '__main__':
    server = GameServer()

    server.connectPlayers()
    server.play()
