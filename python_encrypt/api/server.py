"""
This module contains Server-side functionality to work with file encryption\decryption
"""

import logging
import socket
import time
from datetime import datetime

from threading import Thread

from api.utils import PORT
from event import EncryptEvent, Event

logging.getLogger('EncryptionServer').setLevel(logging.DEBUG)


class EncryptionServer:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((socket.gethostbyname_ex(socket.gethostname())[2][-1], PORT))
        # self._socket.bind((socket.gethostbyname_ex(socket.gethostname())[2][-1], PORT))
        logging.info("Starting server")
        self._socket.listen(1)
        logging.info("Successfully started server and waiting for connection...")

        self._user_socket_connection = None
        self._user_address = None
        self.threads = []

    def listen(self, queue):
        while True:
            conn, addr = self._socket.accept()
            logging.info("Connected: {}, time: {}".format(addr, datetime.now().__str__()))
            self.perform_encryption_with_buffer(conn, queue)

    @staticmethod
    def perform_encryption_with_buffer(socket_connection, queue):
        try:
            user_data = socket_connection.recv(1024)
            file_name, file_size = user_data.decode().split("***")

            round_file_size = round(int(file_size) / (1024*1024), 2)
            logging.debug("Got file: {} with size: {} MB".format(file_name, round_file_size))
            queue.put(Event(EncryptEvent.RECEIVE_FILE.value, {'file_name': file_name,
                                                              'file_size': round_file_size,
                                                              'host': socket_connection.getpeername()[0]}))
            time.sleep(0.5)
            while True:
                event = queue.get()
                logging.debug(f'Server: Received event: {event.name}')
                if event.name == EncryptEvent.SAVE_FILE.value:
                    print("SAVE FILE")
                    print(EncryptEvent.SAVE_FILE.value.encode())
                    socket_connection.send(EncryptEvent.SAVE_FILE.value.encode())
                    break
                if event.name == EncryptEvent.CANCEL.value:
                    logging.debug('User canceled operation')
                    socket_connection.send(EncryptEvent.CANCEL.value.encode())
                    socket_connection.close()
                    return
                if event.name == EncryptEvent.RECEIVE_FILE.value:
                    queue.put(Event(EncryptEvent.RECEIVE_FILE.value, {'file_name': file_name,
                                                                      'file_size': round_file_size,
                                                                      'host': socket_connection.getpeername()[0]}))
                    continue

            received_data = bytes()
            total_received = 0
            queue.put(Event(EncryptEvent.DOWNLOAD_FILE.value, ''))
            socket_connection.settimeout(30)
            while True:
                data = socket_connection.recv(1024*1024)
                if data[-8:] == b"Finished":
                    received_data = received_data + data[:-8]
                    break
                total_received += len(data)
                progress_indicator = (total_received / float(file_size)) * 100
                queue.put(Event(EncryptEvent.DOWNLOAD_PROGRESS.value, {'progress': progress_indicator}))
                logging.debug("{0:.2f}".format(progress_indicator))
                received_data = received_data + data

            logging.debug("Successfully downloaded file")
            queue.put(Event(EncryptEvent.DONE_DOWNLOADING.value, ''))
            queue.put(Event(EncryptEvent.CREATE_FILE.value, (file_name.split('/')[-1], received_data)))
            socket_connection.close()
            return
        except (ValueError, OSError, socket.timeout, ConnectionResetError):
            queue.put(Event(EncryptEvent.ERROR.value, ''))
            socket_connection.close()
            return
