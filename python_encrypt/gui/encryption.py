import PySimpleGUI as gui
from api.encryption import encrypt_file, open_file
from gui.base import BaseWindow
from event import EncryptEvent, Event, GUIEvent
import os
from gui.constants import PythonEncryptKeyBinding


class EncryptFileWindow(BaseWindow):
    def __init__(self, queue):
        super().__init__(queue)
        self._file_path = None
        self._password = None

    def _initialize_window(self):
        layout = [[gui.Text('Please enter password'), gui.Input(key=PythonEncryptKeyBinding.PASSWORD.value, password_char='*')],
                  [gui.Text('Repeat password'), gui.Input(key=PythonEncryptKeyBinding.REPEAT_PASSWORD.value, password_char='*')],
                  [gui.OK(), gui.Cancel()]]
        self._window = gui.Window('Python Encrypt').Layout(layout).Finalize()

    def update(self, event):
        self._event = event
        if event.name == EncryptEvent.ENCRYPT_FILE.value:
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
                elif values.get(PythonEncryptKeyBinding.REPEAT_PASSWORD.value) == '':
                    gui.PopupOK('Please repeat password')
                elif values.get(PythonEncryptKeyBinding.PASSWORD.value) != values.get(PythonEncryptKeyBinding.REPEAT_PASSWORD.value):
                    gui.PopupOK('Passwords don"t match')
                    self._window.Element(PythonEncryptKeyBinding.REPEAT_PASSWORD.value).Update('')
                    self._window.Element(PythonEncryptKeyBinding.PASSWORD.value).Update('')
                else:
                    self._password = values.get(PythonEncryptKeyBinding.PASSWORD.value)
                    encrypt_file(self._file_path, open_file(self._file_path), self._password)
                    gui.PopupOK('Successfully encrypted file')
                    self._window.Close()
                    break
