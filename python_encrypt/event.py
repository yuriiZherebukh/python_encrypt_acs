from collections import namedtuple
from enum import Enum


class EncryptEvent(Enum):
    CANCEL = 'Cancel'
    RECEIVE_FILE = 'Receive_File'
    SAVE_FILE = 'Save_File'
    DOWNLOAD_FILE = 'Download_File'
    DOWNLOAD_PROGRESS = 'Download_Progress'
    DONE_DOWNLOADING = 'Done_Downloading'
    TRANSFER_FILE = 'Transfer_File'
    TRANSFER_PROGRESS = 'Transfer_Progress'
    DONE_TRANSFER = 'Done_Transfer'
    CREATE_FILE = 'Create_File'
    ENCRYPT_FILE = 'Encrypt_File'
    DECRYPT_FILE = 'Decrypt_File'
    SEND_FILE = 'Send_File'


class GUIEvent(Enum):
    CANCEL = 'Cancel'
    OK = 'OK'
    YES = 'Yes'
    EXIT = 'Exit'
    OPEN = 'Open'
    ACTIVATED = '__ACTIVATED__'
    SEND_FILE = '-SEND_FILE-'
    ENCRYPT = '-ENCRYPT-'
    DECRYPT = '-DECRYPT-'


Event = namedtuple("Event", ["name", "data"])
