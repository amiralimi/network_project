import socket
import json
import re
import os.path
import random

from typing import List
from Crypto.PublicKey import RSA

from .terminal import Terminal, Command
from . import encryption

BUFF_SIZE = 2 ** 13
MAX_CHUNK_SIZE = 4000
UPLOAD_DIR = 'MEDIA/upload/'
DOWNLOAD_DIR = 'MEDIA/download/'


class Node:
    def __init__(self, addr, tracker_adr, input_json):
        commands = self.node_commands()
        self.terminal = Terminal(commands)
        self.addr = addr
        self.tracker_adr = tracker_adr
        self.chunks = dict()
        self.private_key, self.public_key = encryption.generate_keys()
        self.input_json = None
        if input_json:
            with open(input_json, 'r') as w:
                self.input_json = json.load(w)

    def start(self):
        while True:
            command = self.terminal.get_input()
            self.run_command(command)

    def upload(self, file_name: str):
        if not self.check_file_exist(file_name):
            print(f'file you are trying to upload doesn\'t exist')
            return
        self.chunks[file_name] = self.get_chunk(file_name)
        data = {
            'type': 'add_peer',
            'peer_addr': self.addr,
            'file_name': file_name,
            'chunk_count': len(self.chunks[file_name])
        }
        if self.input_json:
            data['chunks'] = self.input_json['chunks']
            # chunk_dict = dict()
            # for i, index in enumerate(input_json['chunks']):
            #     chunk_dict[index] = self.chunks['file_name'][i]
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
            chunks = self.chunks[file_name]
            chunk = chunks[data['chunk_id'] - max(min(self.input_json['chunks']), 0)]
            public_key = RSA.importKey(data['public_key'].encode('utf-8'))
            aes_key = encryption.generate_secret_key_for_AES_cipher()
            aes_res = encryption.encrypt_message_AES(chunk, aes_key, b'{')
            encrypted_aes_key = encryption.encrypt_message(aes_key, public_key)
            print(f'sending chunk {"idk"} to {address}')
            sock.sendto(encrypted_aes_key, address)
            sock.sendto(aes_res, address)

    def search(self, file_name: str):
        data = {
            'type': 'find_file',
            'file_name': file_name
        }
        response = self.send_receive_message_to_tracker(data, True)
        peers, chunk_counts = self.parse_tracker_response(response)
        if peers:
            self.download(file_name, peers, chunk_counts)

    def download(self, file_name: str, uploader_peer_adr_list: list, chunk_count: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(self.addr)
        file = list()
        sorted_peer_addr_list = sorted(uploader_peer_adr_list, key=lambda x: x['score'], reverse=True)
        for i in range(chunk_count):
            data = {
                'type': 'get_file',
                'file_name': file_name,
                'chunk_id': i,
                'public_key': self.public_key.exportKey('PEM').decode('utf-8')
            }
            req = json.dumps(data).encode('utf-8')
            uploader_peer_adr = self.choose_peer(sorted_peer_addr_list, i)
            sock.sendto(req, uploader_peer_adr)
            aes_key_encrypted, address = sock.recvfrom(BUFF_SIZE)
            chunk, address = sock.recvfrom(BUFF_SIZE)
            print(f'got response from server for chunk {i}')
            aes_key_decrypted = encryption.decrypt_message(aes_key_encrypted, self.private_key)
            decrypted_chunk = encryption.decrypt_message_AES(chunk, aes_key_decrypted, b'{')
            file.append(decrypted_chunk)
        file_path = DOWNLOAD_DIR + file_name
        file_byte = file[0]
        for i in range(1, len(file)):
            file_byte += file[i]
        f = open(file_path, "wb+")
        f.write(file_byte)
        f.close()
        sock.close()

    def send_receive_message_to_tracker(self, data: dict, has_response: bool) -> dict:
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
    def encode_decode(message, key, function) -> bytes:
        chunk = b''
        size = len(message) // 8
        for i in range(0, len(message), size):
            chunk += function(message[i:i + size], key)
        return chunk

    @staticmethod
    def parse_tracker_response(response: dict) -> tuple:
        peers = response['peers']
        chunk_count = response['chunk_count']
        return peers, chunk_count

    @staticmethod
    def choose_peer(peers, i):
        for peer in peers:
            if i in peer['chunk_list'] or -1 in peer['chunk_list']:
                return tuple(peer['peer_addr'])

    @staticmethod
    def check_file_exist(file_name: str) -> bool:
        file_path = UPLOAD_DIR + file_name
        if os.path.isfile(file_path):
            return True
        return False

    @staticmethod
    def get_chunk(file_name) -> List[bytes]:
        file_path = UPLOAD_DIR + file_name
        f = open(file_path, 'rb')
        data = f.read()
        f.close()
        chunks = [data[i:i + MAX_CHUNK_SIZE] for i in range(0, len(data), MAX_CHUNK_SIZE)]
        return chunks

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
