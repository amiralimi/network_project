import socket
import json

BUFF_SIZE = 2 ** 13


class Tracker:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_adr = (self.ip, self.port)
        self.file_tracker = dict()

    def run(self):
        self.sock.bind(self.server_adr)
        while True:
            print(f'tracker is waiting for requests')
            data, address = self.sock.recvfrom(BUFF_SIZE)
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
            score = 0
            if 'chunks' in data:
                chunks = data['chunks']
                score = 100
                if file_name not in self.file_tracker:
                    return
            else:
                chunks = [-1]
            if file_name not in self.file_tracker:
                self.file_tracker[file_name] = {
                    'peers': list(),
                    'chunk_count': data['chunk_count']
                }
            self.file_tracker[file_name]['peers'].append({
                'peer_addr': data['peer_addr'],
                'score': score,
                'chunk_list': chunks
            })
            return None
        elif data['type'] == 'find_file':
            file_name = data['file_name']
            if file_name in self.file_tracker:
                response = self.file_tracker[file_name]
            else:
                response = {}
            return response


if __name__ == '__main__':
    tracker = Tracker('localhost', 1111)
    tracker.run()
