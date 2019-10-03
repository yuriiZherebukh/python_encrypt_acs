"""
This module contains Client-side functionality to work with file encryption\decryption
"""

import logging
import os
import socket
import time
from getpass import getpass
from sys import exit

from python_encrypt.api.utils import HOST, PORT

logging.getLogger().setLevel(logging.DEBUG)


class EncryptionClient:
    def __init__(self, file, pwd, encryption_mode):
        self._file = file
        self._file_name = self._file.split("\\")[-1]
        self._password = pwd
        self._encryption_mode = encryption_mode
        try:
            self._socket = socket.socket()
            self._socket.connect((HOST, PORT))
            logging.info("Successfully started the connection")
        except ConnectionRefusedError:
            logging.warning("Could not connect to server. Exiting the program")
            exit(1)

    def send_file_info(self):
        data_to_send = "{}/{}/{}/{}".format(self._file_name, os.stat(self._file).st_size, self._password,
                                            self._encryption_mode)
        logging.info("Sending data: filename - {}, file size - {}, "
                     "password length - {}, encryption mode - {}".format(self._file_name,
                                                                         os.stat(self._file).st_size,
                                                                         len(self._password),
                                                                         "encrypt" if self._encryption_mode == "e" else
                                                                         "decrypt"))
        self._socket.send(data_to_send.encode())
        logging.info("Successfully sent data to the server")

    def send_file(self):
        logging.info("Sending file")
        with open(self._file, "rb") as file:
            file_data = file.read()
            self._socket.sendall(file_data)
            self._socket.send(b"Finished")

        logging.info("Successfully sent file")

    def encrypt_decrypt_file(self):
        try:
            received_data = bytes()
            raw_data = self._socket.recv(1024)
            file_size, data = raw_data.split(b"***")

            logging.info("File size to receive: {}".format(file_size))
            logging.info("Receiving file...")
            time.sleep(0.5)
            if self._encryption_mode == "e":
                with open(self._file + ".aes", "wb") as file_to_encrypt:
                    total_received = len(data)
                    received_data = received_data + data
                    while data != bytes(''.encode()):
                        logging.info("{0:.2f}".format((total_received / float(file_size)) * 100) + "% Done")
                        data = self._socket.recv(1024)
                        total_received += len(data)
                        received_data = received_data + data

                    file_to_encrypt.write(received_data)

                logging.info("Successfully received file with name: {}".format(self._file + ".aes"))

            elif self._encryption_mode == "d":
                with open(self._file[:-4], "wb") as file_to_decrypt:
                    total_received = len(data)
                    received_data = received_data + data
                    while data != bytes(''.encode()):
                        logging.info("{0:.2f}".format((total_received / float(file_size)) * 100) + "% Done")
                        data = self._socket.recv(1024)
                        total_received += len(data)
                        received_data = received_data + data

                    file_to_decrypt.write(received_data)

                logging.info("Successfully received file with name: {}".format(self._file[:-4]))
            else:
                logging.warning("Incorrect mode: {}".format(self._encryption_mode))
                exit(1)

            self._socket.close()
        except Exception as err:
            logging.warning("Error when tried to send file for encryption\\decryption. Error: {}".format(err))
            exit(1)


if __name__ == '__main__':
    filename = input("Filename? -> ")
    password = getpass("Password ->")
    mode = input("Mode?(e/d (encrypt- decrypt)) -> ")
    encryption_client = EncryptionClient(filename, password, mode)
    encryption_client.send_file_info()
    encryption_client.send_file()
    encryption_client.encrypt_decrypt_file()
    exit(0)
