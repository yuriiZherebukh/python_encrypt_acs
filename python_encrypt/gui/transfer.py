import PySimpleGUI as gui
from api.client import EncryptionClient
from gui.base import BaseWindow
from event import EncryptEvent, GUIEvent
import time


class SendFileWindow(BaseWindow):
    def __init__(self, queue):
        super().__init__(queue)
        self._host_path = None

    def _initialize_window(self):
        layout = [[gui.Text('Select file to send')],
                  [gui.Input(key='-FOLDER_PATH-'), gui.FileBrowse()],
                  [gui.OK(), gui.Cancel()]]
        self._window = gui.Window('Python Encrypt').Layout(layout).Finalize()

    def update(self, event):
        self._event = event
        if event.name == EncryptEvent.SEND_FILE.value:
            self._host_path = event.data
            self._initialize_window()
            self.process_event(self._window)

    def close(self):
        self._window.Close()
        self._window = None

    def process_event(self, event):
        while True:
            event, value = self._window.Read(timeout=100)
            if event in (GUIEvent.CANCEL.value, None):
                self._window.Close()
                break
            if event == GUIEvent.OK.value:
                if value['-FOLDER_PATH-'] == '':
                    gui.PopupOK('Please select folder path to save file', title='Info')
                    continue
                try:
                    client = EncryptionClient(value.get('-FOLDER_PATH-'), self._host_path, self._queue)
                except (ConnectionRefusedError, TimeoutError):
                    gui.PopupOK('Could not connect to the target machine')
                    self.close()
                    break
                client.send_file_info()
                self.close()
                client_response_window = gui.Window('Encrypt window').Layout([[gui.Text('Waiting for user to respond')]]).Finalize()
                while True:
                    try:
                        client_response_event, _ = client_response_window.Read(timeout=100)
                        if client_response_event in (GUIEvent.CANCEL.value, None):

                            client_response_window.Close()
                            return

                        try:
                            client.get_response()
                        except Exception:
                            pass

                    except ValueError:
                        gui.PopupOK('Could not send file info to user')
                        return
                    if self._queue.empty():
                        continue
                    client_event = self._queue.get()
                    if client_event.name == EncryptEvent.CANCEL:
                        client_response_window.Close()
                        gui.PopupOK('User cancelled operation')
                        return
                    elif client_event.name == EncryptEvent.SAVE_FILE:
                        client_response_window.Close()
                        client.send_file()
                    else:
                        gui.PopupOK('Something went wrong with client. Aborting')
                        client_response_window.Close()
                    return
