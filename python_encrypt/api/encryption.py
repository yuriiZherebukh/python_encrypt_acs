"""
This module contains encryption functionality
"""

from os import stat, remove

from pyAesCrypt import decryptStream, encryptStream

from api.utils import BUF_SIZE


def create_file(file_name, file_b):
    with open(file_name, "wb") as file:
        file.write(file_b)


def open_file(file_name):
    with open(file_name, "rb") as file:
        return file.read()


def encrypt_file(file_name, file_b, password):
    create_file(file_name, file_b)
    with open(file_name, "rb") as fIn:
        with open(file_name + ".aes", "wb") as fOut:
            encryptStream(fIn, fOut, password, BUF_SIZE)


def decrypt_file(file_name, password):

    enc_file_size = stat(file_name).st_size
    new_file_name = file_name[:-4]
    with open(file_name, "rb") as fIn:
        with open(new_file_name, "wb") as fOut:
            try:
                decryptStream(fIn, fOut, password, BUF_SIZE, enc_file_size)
            except ValueError:
                fIn.close()
                fOut.close()
                remove(new_file_name)
                raise ValueError
    remove(file_name)
