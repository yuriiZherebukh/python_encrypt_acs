import multiprocessing
import re

import PySimpleGUI as gui

from api.server import EncryptionServer
from dispatcher import EventDispatcher
from event import GUIEvent, EncryptEvent, Event
from gui.base import PythonEncryptWindow, DownloadProgressBar, TransferProgressBar
from gui.decryption import DecryptFileWindow
from gui.encryption import EncryptFileWindow
from gui.receive import ReceiveCheckbox, SaveFileWindow
from gui.transfer import SendFileWindow


def run_main_thread(encrypt_queue):
    windows = [ReceiveCheckbox(encrypt_queue), DownloadProgressBar(encrypt_queue), TransferProgressBar(encrypt_queue),
               SaveFileWindow(encrypt_queue),
               EncryptFileWindow(encrypt_queue), DecryptFileWindow(encrypt_queue), SendFileWindow(encrypt_queue)]
    event_dispatcher = EventDispatcher(encrypt_queue)
    for window in windows:
        event_dispatcher.register(window)
    encrypt_window = PythonEncryptWindow()

    while True:
        if encrypt_window.window:
            event, values = encrypt_window.window.Read(timeout=10)
            if event in (GUIEvent.CANCEL.value, None):
                encrypt_window.close_base_window()
            if event == GUIEvent.ENCRYPT.value:
                if values.get('-FILE_PATH_ENCRYPT-') == '':
                    gui.PopupOK('You must select file to encrypt')
                else:
                    encrypt_window.clear_path()
                    encrypt_queue.put(Event(EncryptEvent.ENCRYPT_FILE.value, values.get('-FILE_PATH_ENCRYPT-')))
            if event == GUIEvent.DECRYPT.value:
                if values.get('-FILE_PATH_DECRYPT-') == '':
                    gui.PopupOK('You must select file to decrypt')
                else:
                    encrypt_window.clear_path()
                    encrypt_queue.put(Event(EncryptEvent.DECRYPT_FILE.value, values.get('-FILE_PATH_DECRYPT-')))
            if event == GUIEvent.SEND_FILE.value:
                if values.get('-HOST_INPUT-') == '':
                    gui.PopupOK('Please specify IP address of sender')
                else:
                    ip_address = values.get('-HOST_INPUT-')
                    ip_match = re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address)
                    if ip_match:
                        encrypt_queue.put(Event(EncryptEvent.SEND_FILE.value, ip_address))
                    else:
                        gui.PopupOK('Enter valid IP address')
        menu_item = encrypt_window.tray_icon.Read(timeout=10)
        if menu_item in (GUIEvent.OPEN.value, GUIEvent.ACTIVATED.value):
            if encrypt_window.window:
                continue
            encrypt_window.initialize_window()
        if menu_item == GUIEvent.EXIT.value:
            if encrypt_window.window:
                encrypt_window.close_base_window()
            encrypt_window.close_system_tray_icon()
            break
        event_dispatcher.dispatch()


if __name__ == '__main__':
    queue = multiprocessing.Queue()
    server = EncryptionServer()
    connection_service_process = multiprocessing.Process(target=server.listen, args=(queue,))
    connection_service_process.daemon = True
    connection_service_process.start()
    run_main_thread(queue)
