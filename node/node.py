import socket
import json
import re
import os
from .terminal import Terminal, Command

BUFF_SIZE = 2 ** 12
MAX_CHUNK_SIZE = 60000


class Node:
    def __init__(self, addr, tracker_adr):
        commands = self.node_commands()
        self.terminal = Terminal(commands)
        self.addr = addr
        self.tracker_adr = tracker_adr

    def start(self):
        while True:
            command = self.terminal.get_input()
            self.run_command(command)

    def upload(self, file_name: str):
        data = {
            'type': 'add_peer',
            'peer_addr': self.addr,
            'file_name': file_name
        }
        self.send_receive_message_to_tracker(data, False)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(self.addr)
        while True:
            print(f'waiting for upload requests.')
            data, address = sock.recvfrom(BUFF_SIZE)
            data = data.decode('utf-8')
            print(f'got this request from {address}:\n'
                  f'{data}')
            data = json.loads(data)
            chunk = self.get_chunk(data)
            response = {
                'chunk_id': 'idk',
                'chunk': chunk
            }
            print(f'sending chunk {"idk"} to {address}')
            response = json.dumps(response).encode('utf-8')
            sock.sendto(response, address)

    def search(self, file_name: str):
        data = {
            'type': 'find_file',
            'file_name': file_name
        }
        response = self.send_receive_message_to_tracker(data, True)

    def send_receive_message_to_tracker(self, data: dict, has_response: bool) -> list:
        req = json.dumps(data).encode('utf-8')
        print(f'sending this data to tracker:\n'
              f'r{req}')
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        udp_socket.sendto(req, self.tracker_adr)
        response = None
        if has_response:
            response, address = udp_socket.recvfrom(BUFF_SIZE)
            response = json.loads(response.decode('utf-8'))
            print(f'got this response from the server:\n'
                  f'{response}')
        udp_socket.close()
        return response

    def run_command(self, command: str):
        command_parts = command.split()
        if 'upload' in command:
            file_name = command_parts[3].replace('"', '')
            self.upload(file_name)
        if 'search' in command:
            file_name = command_parts[2].replace('"', '')
            self.search(file_name)

    @staticmethod
    def get_chunk(req):
        return req

    @staticmethod
    def node_commands() -> Command:
        file_name_re = r'\w*(\.\w*)?'
        commands = list()
        commands.append(
            re.compile(fr'\Atorrent -setMode upload "{file_name_re}"$')
        )
        commands.append(
            re.compile(fr'\Atorrent -search "{file_name_re}"$')
        )
        return commands
