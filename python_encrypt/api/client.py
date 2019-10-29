"""
This module contains Client-side functionality to work with file encryption\decryption
"""

import logging
import os
import socket
import datetime

import threading
from api.utils import PORT
from event import EncryptEvent, Event

logging.getLogger().setLevel(logging.DEBUG)


class EncryptionClient:
    def __init__(self, file, hostname, queue):
        self._file = file
        self._file_name = self._file.split("\\")[-1]
        self._file_size = os.stat(self._file).st_size
        self._queue = queue
        self._threads = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        now = datetime.datetime.now()
        after_5_min = now + datetime.timedelta(minutes=5)
        while not connected:
            try:
                self._socket.connect((hostname, PORT))
                connected = True
                now = datetime.datetime.now()
                if now >= after_5_min:
                    raise TimeoutError
            except socket.timeout:
                continue
        logging.info("Successfully established connection")

    def send_file_info(self):
        data_to_send = "{}***{}".format(self._file_name, self._file_size)
        logging.info("Sending data: filename - {}, file size - {}".format(self._file_name,
                                                                          self._file_size))
        self._socket.send(data_to_send.encode())
        logging.info("Successfully sent data to the server")

    def get_response(self):
        def _wait_for_user():
            try:
                response = self._socket.recv(1024).decode()
            except ConnectionResetError:
                self._socket.close()
                self._queue.put(Event(EncryptEvent.CANCEL, ''))
                return
            logging.info(f'User sent: {response}')
            self._queue.put(Event(EncryptEvent(response), ''))

        threads = threading.enumerate()
        if 'WaitForUser' in [thread.name for thread in threads]:
            return

        logging.info('Waiting for user to respond')
        t = threading.Thread(target=_wait_for_user, name='WaitForUser')
        self._threads.append(t)
        if len(self._threads) > 1:
            raise Exception
        t.start()

    def send_file(self):
        file = open(self._file, "rb")
        file_data = file.read(1024 * 1024)
        length_sent = len(file_data)
        self._queue.put(Event(EncryptEvent.TRANSFER_FILE.value, ''))
        while file_data:
            self._socket.send(file_data)
            file_data = file.read(1024 * 1024)
            length_sent = length_sent + len(file_data)
            progress_indicator = (length_sent / float(self._file_size)) * 100
            self._queue.put(Event(EncryptEvent.TRANSFER_PROGRESS.value, {'progress': progress_indicator}))

        self._socket.send(b"Finished")
        self._queue.put(Event(EncryptEvent.DONE_TRANSFER.value, ''))
        logging.info("Successfully sent file")
