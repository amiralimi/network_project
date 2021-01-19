import getopt
import sys
import logging
from network_handler import *

unix_options = 't:s:u:d:p:p:'
gnu_options = ['torrent', 'setMode', 'upload', 'download', 'path=', 'port=']
logging.basicConfig(level=logging.DEBUG)


PSTATUS_UPLOAD_FILENAME = str()
PSTATUS_DOWNLOAD_FILENAME = str()
PSTATUS_LISTEN_PORT = 1111

def main(argv):
    try:
        arguments, values = getopt.getopt(argv, unix_options, gnu_options)
    except getopt.error as e:
        print(str(e))
        sys.exit(2)

    pstatus_mode_upload = False
    pstatus_mode_download = False
    pstatus_listen_port = 1111
    pstatus_download_filename = str()
    pstatus_upload_filename = str()

    for curr_arg, curr_val in arguments:
        if curr_arg == '--upload':
             pstatus_mode_upload = True
        if curr_arg == '--download':
             pstatus_mode_download = True
        if curr_arg == '--path':
            if(pstatus_mode_upload):
                pstatus_upload_filename = curr_val
            elif(pstatus_mode_download) :
                pstatus_download_filename = curr_val
        if curr_arg == '--port':
            pstatus_listen_port = int(curr_val)

    connect_to_tracker(pstatus_listen_port , pstatus_upload_filename)


if __name__ == '__main__':
    main(sys.argv[1:])
