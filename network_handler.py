import logging
import socket
import json
from main import *

BUFF_SIZE = 4096
WAIT_TIMEOUT = 5

peer_ip = 'localhost'
tracker_ip = 'localhost'
tracker_port = 8080


def connect_to_tracker(listen_port , filename):

    req = json.dumps({
        'type': 'add_peer',
        'peer_addr': {
                'ip': peer_ip,
                'port': listen_port
            },
        'filename': filename
        }
     ).encode('utf-8')

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,0)
    udp_socket.sendto(req, (tracker_ip, tracker_port))
    udp_socket.close()




