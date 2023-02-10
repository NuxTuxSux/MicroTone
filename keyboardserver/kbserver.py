from events import EventGenerator
# import select
import threading
import socket


SYNTH_PORT = 50000
PACKET_SIZE = 8

CODES = {
    0: 58,
    1: 59,
    2: 60,
    3: 61,
    4: 62,
    5: 63,
    6: 64,
    7: 65,
    8: 66,
    9: 67,
    10: 68,
    11: 69,
    12: 70,
    13: 71,
    14: 72,
    15: 73,
    16: 74,
    17: 75
}


class RemoteKeyboard(EventGenerator):

    def __init__(self):
        self.messages = []
        t = threading.Thread(target=self._startServer)
        self.running = True
        t.start()

    def close(self):
        self.running = False

    def _startServer(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(('0.0.0.0', SYNTH_PORT))
        serverSocket.listen()
        print(f"Keyboard server waiting for connection on port {SYNTH_PORT}")
        conn, address = serverSocket.accept()
        print("Connected to {}".format(address))
        while self.running:
            data = conn.recv(1024)
            if data != None:
                self.messages.append(data.decode())

    
    def _parseEvent(event):
        code, event = event.split(':')
        code = CODES[int(code[2:])]
        event = event.strip()
        if event == "on":
            return EventGenerator.keyDown(code)
        elif event == "off":
            return EventGenerator.keyUp(code)
        else:
            return None         # for clarity
        
    def close(self):
        self.running = False

    def get(self):
        mess = self.messages.copy()
        self.messages.clear()
        return list(map(RemoteKeyboard._parseEvent, mess))