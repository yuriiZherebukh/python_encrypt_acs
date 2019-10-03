"""
This module contains Server-side functionality to work with file encryption\decryption
"""

import logging
import socket
import threading
from datetime import datetime

from python_encrypt.api.encryption import encrypt_file, decrypt_file
from python_encrypt.api.utils import HOST, PORT, USERS_TO_LISTEN

logging.getLogger().setLevel(logging.DEBUG)


class EncryptionServer:
    def __init__(self):
        self._socket = socket.socket()
        self._socket.bind((HOST, PORT))
        logging.info("Starting server")
        self._socket.listen(USERS_TO_LISTEN)
        logging.info("Successfully started server and waiting for connection...")

        self._user_socket_connection = None
        self._user_address = None

    def listen(self):
        while True:
            conn, addr = self._socket.accept()
            logging.info("Connected: {}, time: {}".format(addr, datetime.now().__str__()))

            t = threading.Thread(target=self.perform_encryption_with_buffer, args=(conn,))
            t.start()

        s.close()

    @staticmethod
    def perform_encryption_with_buffer(socket_connection):
        try:
            user_data = socket_connection.recv(1024)
            file_name, file_size, password, mode = user_data.decode().split("/")
            logging.debug("Got file: {} with size: {}, mode: {}".format(file_name, file_size, mode))
            received_data = bytes()
            total_received = 0
            if mode == "e":
                while True:
                    data = socket_connection.recv(1024)
                    if data[-8:] == b"Finished":
                        received_data = received_data + data[:-8]
                        break
                    total_received += len(data)
                    logging.debug("{0:.2f}".format((total_received / float(file_size)) * 100) + "% Done")
                    received_data = received_data + data

                logging.debug("Successfully downloaded file")
                logging.debug("Encrypting file...")
                data = encrypt_file(file_name, received_data, password)
                logging.debug("Successfully encrypted file")
                logging.debug("Sending file...")

                while data:
                    if len(data) >= 1024:
                        socket_connection.send(data[:1024])
                        data = data[1024:]
                    else:
                        socket_connection.send(data)
                        break
            elif mode == "d":
                while True:
                    data = socket_connection.recv(1024)
                    if data[-8:] == b"Finished":
                        received_data = received_data + data[:-8]
                        break
                    total_received += len(data)
                    logging.debug("{0:.2f}".format((total_received / float(file_size)) * 100) + "% Done")
                    received_data = received_data + data

                logging.debug("Successfully downloaded file")
                logging.debug("Decrypting file...")
                data = decrypt_file(file_name, received_data, password)
                logging.debug("Successfully decrypted file")
                logging.debug("Sending file...")

                while data:
                    if len(data) >= 1024:
                        socket_connection.send(data[:1024])
                        data = data[1024:]
                    else:
                        socket_connection.send(data)
                        break
            else:
                logging.warning("Wrong mode. Cancelling operation")
                return
            logging.debug("Successfully sent file")
            socket_connection.close()
        except Exception as err:
            logging.warning("Error when tried to encrypt\\decrypt buffer. Error: {}".format(err))
            return


if __name__ == '__main__':
    encryption_server = EncryptionServer()
    encryption_server.listen()
