import re
from struct import pack, unpack, calcsize


CONNECTED_CMD = 'CONNECTED'
QUIT_CMD = 'QUIT'
SYNC_CMD = 'SYNC'
ERROR_CMD = 'ERROR'
SWAP_CMD = 'SWAP'
ACTION_CMD = 'ACTION'

SEPERATOR = '-'

STATUS_CODE_SUCCESS = '200'
STATUS_CODE_FAILURE = '400'

HEADER_FMT = '!I'
HEADER_SIZE = calcsize(HEADER_FMT)


def createHeader(payload_size):
    if not (0 <= payload_size <= 2**32 - 1):
        raise ValueError(f'payload_size must be in range [0, 2**32-1]')

    header = pack(HEADER_FMT, payload_size)
    return header

def decodeHeader(header):
    res = unpack(HEADER_FMT, header)
    return res[0]

def recv(socket):
    header = socket.recv(HEADER_SIZE)
    packet_size = decodeHeader(header)

    data = socket.recv(packet_size)
    res = data.decode()

    if not res:
        raise ValueError('Recieved an empty packet')

    status_code, cmd, msg = re.split(':|-', res)

    cmd = cmd.strip()
    msg = msg.strip()

    return status_code, cmd, msg

def send(socket, status_code, cmd, msg):
    data = f'{status_code}:{cmd} {SEPERATOR} {msg}'
    data = data.encode('utf-8')

    header = createHeader(len(data))

    if isinstance(socket, list):
        for s in socket:
            s.sendall(header)
            s.sendall(data)
    else:
        socket.sendall(header)
        socket.sendall(data)
