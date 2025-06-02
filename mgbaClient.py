import socket
import struct
import time
from unit import Unit


def storeUnits(unitData):
    numUnits = int(len(unitData)/72)
    unitList = []
    startAddress = 0
    endAddress = 72
    for x in range(numUnits):
        unitList.append(Unit(unitData[startAddress:endAddress]))
        startAddress = endAddress
        endAddress += 72
    return unitList

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise ConnectionError("Socket closed before full message received")
        data += chunk
    return data

class MgbaClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print('Connected to mgba server')

    def send_command(self, command):
        
        try:
            self.sock.sendall((command + "\n").encode())
            if "press" not in command:
                raw_len = recv_all(self.sock,4)
                print("[Python] Raw header bytes:", raw_len.hex()) 
                msg_len = struct.unpack(">I", raw_len)[0]
                print(f"[Python] Expecting {msg_len} bytes from server")
                data = recv_all(self.sock, msg_len)
                return data
            return
        except Exception as e:
            print(f'Error during send: {e}')
            return None
        
        

    def close(self):
        self.sock.close()
        print('Closed connection to mgba server')
