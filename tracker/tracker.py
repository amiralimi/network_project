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
            print(f'got this request from {address}:\n'
                  f'{data}')
            data = json.loads(data)
            response = self.handle_request(data)
            if response:
                response = json.dumps(response).encode('utf-8')
                self.sock.sendto(response, address)
                print(f'sending this response to node:'
                      f'{response}')

    def handle_request(self, data):
        if data['type'] == 'add_peer':
            file_name = data['file_name']
            if file_name not in self.file_tracker:
                self.file_tracker[file_name] = list()
            self.file_tracker[file_name].append(data['peer_addr'])
            return None
        elif data['type'] == 'find_file':
            file_name = data['file_name']
            if file_name in self.file_tracker:
                response = self.file_tracker[file_name]
            else:
                response = []
            return response


if __name__ == '__main__':
    tracker = Tracker('localhost', 1111, 2 ** 16)
    tracker.run()
