import getopt
import sys
from node.node import Node

unix_options = 't:s:u:d:p:p:'
gnu_options = ['ip=', 'port=', 'tracker_ip=', 'tracker_port=']


def parse_args(argv):
    try:
        arguments, values = getopt.getopt(argv, unix_options, gnu_options)
    except getopt.error as e:
        print(str(e))
        sys.exit(2)

    node_ip = 'localhost'
    node_port = 1112
    tracker_ip = 'localhost'
    tracker_port = 1111

    for curr_arg, curr_val in arguments:
        if curr_arg == '--ip':
            node_ip = curr_val
        if curr_arg == '--port':
            node_port = int(curr_val)
        if curr_arg == '--tracker_ip':
            tracker_ip = curr_val
        if curr_arg == '--tracker_port':
            tracker_port = int(curr_val)

    return (node_ip, node_port), (tracker_ip, tracker_port)


if __name__ == '__main__':
    node_addr, tracker_addr = parse_args(sys.argv[1:])
    print(node_addr)
    print(tracker_addr)
    node = Node(node_addr, tracker_addr)
    node.start()
