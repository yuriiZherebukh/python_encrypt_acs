import PySimpleGUI as gui
from api.encryption import decrypt_file, open_file
from gui.base import BaseWindow
from event import EncryptEvent, Event, GUIEvent
import os
from gui.constants import PythonEncryptKeyBinding


class DecryptFileWindow(BaseWindow):
    def __init__(self, queue):
        super().__init__(queue)
        self._file_path = None

    def _initialize_window(self):
        layout = [[gui.Text('Please enter password to decrypt file'), gui.Input(key=PythonEncryptKeyBinding.PASSWORD.value, password_char='*')],
                  [gui.OK(), gui.Cancel()]]
        self._window = gui.Window('Python Encrypt').Layout(layout).Finalize()

    def update(self, event):
        self._event = event
        if event.name == EncryptEvent.DECRYPT_FILE.value:
            self._file_path = event.data
            self._initialize_window()
            self.process_event(event)

    def process_event(self, event):
        while True:
            event, values = self._window.Read(timeout=100)
            if event in ('Cancel', None):
                self._window.Close()
                break
            if event == GUIEvent.OK.value:
                if values.get(PythonEncryptKeyBinding.PASSWORD.value) == '':
                    gui.PopupOK('Please type password')
                else:
                    try:
                        decrypt_file(self._file_path, values.get(PythonEncryptKeyBinding.PASSWORD.value))
                    except ValueError:
                        gui.PopupOK('Wrong password. Please enter once more')
                        self._window.Element(PythonEncryptKeyBinding.PASSWORD.value).Update('')
                        continue
                    gui.PopupOK('Successfully decrypted file')
                    self._window.Close()
                    break
