import PySimpleGUI as gui
from api.encryption import create_file
from gui.base import BaseWindow
from event import EncryptEvent, Event, GUIEvent
import os


class ReceiveCheckbox(BaseWindow):
    def __init__(self, queue):
        super().__init__(queue)

    def _initialize_window(self):
        self._window = gui.PopupYesNo(f'Would you like to download file:{self._event.data["file_name"]} '
                                      f'{self._event.data["file_size"]} MB from {self._event.data["host"]}?',
                                      title='Python Encrypt Receive File')

    def update(self, event):
        self._event = event
        if event.name == EncryptEvent.RECEIVE_FILE.value:
            self._initialize_window()
            self.process_event(self._window)
        if event.name == EncryptEvent.ERROR.value:
            if self._window:
                self._window.Close()
                self._window = None

    def process_event(self, event):
        if event == GUIEvent.YES.value:
            self._queue.put(Event(EncryptEvent.SAVE_FILE.value, ''))
        if event in (GUIEvent.CANCEL.value, GUIEvent.NO.value):
            self._queue.put(Event(EncryptEvent.CANCEL.value, ''))
        self._window = None


class SaveFileWindow(BaseWindow):
    def __init__(self, queue):
        super().__init__(queue)

    def _initialize_window(self):
        layout = [[gui.Text('Select folder to save file')],
                  [gui.Input(key='-FOLDER_PATH-'), gui.FolderBrowse()],
                  [gui.OK(), gui.Cancel()]]
        self._window = gui.Window('Python Encrypt').Layout(layout).Finalize()

    def update(self, event):
        self._event = event
        if event.name == EncryptEvent.CREATE_FILE.value:
            self._initialize_window()
            self.process_event(self._window)
        if event.name == EncryptEvent.ERROR.value:
            if self._window:
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
                create_file(os.path.join(value['-FOLDER_PATH-'] + '/' + self._event.data[0]),
                            self._event.data[1])
                gui.PopupOK('Successfully saved file', title='Python Encrypt')
                self._window.Close()
                break


