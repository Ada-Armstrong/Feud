import re


CONNECTED_CMD = 'CONNECTED'
QUIT_CMD = 'QUIT'
SYNC_CMD = 'SYNC'
ERROR_CMD = 'ERROR'
SWAP_CMD = 'SWAP'
ACTION_CMD = 'ACTION'

SEPERATOR = '-'

STATUS_CODE_SUCCESS = '200'
STATUS_CODE_FAILURE = '400'

PACKET_SIZE = 1024


def recv(socket):
    data = socket.recv(PACKET_SIZE)
    res = data.decode()
    print(f'recv\'d {res}')

    if not res:
        raise ValueError('Recieved an empty packet')

    status_code, cmd, msg = re.split(':|-', res)

    cmd = cmd.strip()
    msg = msg.strip()

    return status_code, cmd, msg

def send(socket, status_code, cmd, msg):
    data = f'{status_code}:{cmd} {SEPERATOR} {msg}'
    data = data.encode('utf-8')

    socket.sendall(data)
