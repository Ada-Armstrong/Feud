import socket
import packet


class GameClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = None

    def __del__(self):
        self.socket.close()

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

            if not self.validCode(status_code):
                print(f'Recieved bad msg:\n{status_code}:{msg}')
                return
                
            if cmd == packet.QUIT_CMD:
                self.id = None
                print(f'Quiting')
                return
            elif cmd == packet.SYNC_CMD:
                request = input('Input turn: ')
                packet.send(
                        self.socket,
                        packet.STATUS_CODE_SUCCESS,
                        packet.SWAP_CMD,
                        request
                        )
            elif cmd == packet.SWAP_CMD:
                # update our local instance of the game
                pass
            else:
                print('Unknown command {cmd}')
                return

    def recv(self):
        return packet.recv(self.socket)

    def validCode(self, status_code):
        return status_code == packet.STATUS_CODE_SUCCESS 
        

if __name__ == '__main__':
    client = GameClient()
    client.connectToServer('localhost', 60555)
    client.play()
