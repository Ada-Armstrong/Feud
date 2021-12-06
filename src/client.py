import socket
import packet
from queue import Queue
from game import Game


class GameClient:

    def __init__(self, cli_mode=False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = None

        self.cli_mode = cli_mode

        self.game = Game()
        self.input_queue = Queue()

    def __del__(self):
        self.socket.close()

    def addInput(self, in_str):
        self.input_queue.put(in_str)

    def getInput(self):
        self.input_queue.get()

    def connectToServer(self, ip, port):
        self.socket.connect((ip, port))

        status_code, cmd, msg = self.recv()

        if not self.validCode(status_code):
            print(f'Recieved bad msg:\n{status_code}:{msg}')
            return

        self.id = int(msg[0])

    def play(self):
        if self.id is None:
            raise ValueError('Not connected to a server')

        while 1:
            print('Waiting to recv msg from server')

            status_code, cmd, msg = self.recv()
            print('*' * 30)
            print(f'{status_code=}\n{cmd=}\n{msg=}')
            print('*' * 30)
            print(self.game)

            if not self.validCode(status_code):
                print(f'Recieved bad msg:\n{status_code}:{msg}')
                continue
                
            if cmd == packet.QUIT_CMD:
                self.id = None
                print(f'Quiting')
                return
            elif cmd == packet.SYNC_CMD:
                if msg not in [packet.SWAP_CMD, packet.ACTION_CMD]:
                    print(f'Recieved bad msg:\n{status_code}:{msg}')
                    return

                request = input('> ') if self.cli_mode else self.getInput()

                self.send(packet.STATUS_CODE_SUCCESS, msg, request)
            elif cmd == packet.SWAP_CMD:
                args = msg.split()

                pos1 = self.game._str2cord(args[0])
                pos2 = self.game._str2cord(args[1])

                self.game.swap(pos1, pos2)
            elif cmd == packet.ACTION_CMD:
                args = msg.split()

                if len(args) == 0:
                    self.game.skipAction()
                else:
                    poses = [self.game._str2cord(p) for p in args]
                    self.game.action(poses[0], poses[1:])
            else:
                print('Unknown command {cmd}')
                return

    def send(self, status_code, cmd, msg):
        return packet.send(self.socket, status_code, cmd, msg)

    def recv(self):
        return packet.recv(self.socket)

    def validCode(self, status_code):
        return status_code == packet.STATUS_CODE_SUCCESS 
        

if __name__ == '__main__':
    client = GameClient(cli_mode=True)
    client.connectToServer('localhost', 60555)

    try:
        client.play()
    except KeyboardInterrupt:
        client.send(packet.STATUS_CODE_SUCCESS, packet.QUIT_CMD, 'Bye')

