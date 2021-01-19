import socket
import json


class Tracker:
    def __init__(self, ip, port, BUFF_SIZE):
        self.ip = ip
        self.port = port
        self.BUFF_SIZE = BUFF_SIZE
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_adr = (self.ip, self.port)
        self.file_tracker = dict()

    def run(self):
        self.sock.bind(self.server_adr)
        while True:
            print(f'tracker is waiting for requests')
            data, address = self.sock.recvfrom(self.BUFF_SIZE)
            data = data.decode('utf-8')
            data = json.loads(data)
            self.handle_request(data, address)

    def handle_request(self, data, address):
        if data['type'] == 'add_peer':
            file_name = data['file_name']
            if file_name not in self.file_tracker:
                self.file_tracker[file_name] = list()
            self.file_tracker[file_name].append(address)  # or data['peer_addr']
        # TODO: other types of requests.


if __name__ == '__main__':
    tracker = Tracker('localhost', 1111, 2 ** 16)
    tracker.run()
