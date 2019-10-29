import PySimpleGUI as gui
from PySimpleGUIQt import SystemTray
import os
from abc import ABC, abstractmethod
from gui.constants import PythonEncryptKeyBinding
from event import EncryptEvent


class BaseWindow(ABC):
    def __init__(self, queue):
        self._queue = queue
        self._event = None
        self._window = None

    @abstractmethod
    def update(self, event):
        pass

    @abstractmethod
    def _initialize_window(self):
        pass

    @abstractmethod
    def process_event(self, event):
        pass


class PythonEncryptWindow:
    def __init__(self):
        self._window = None
        self._quit = False
        self.initialize_window()
        menu_layout = ['BLANK', ['&Open', '&Exit']]
        self._tray = SystemTray(menu=menu_layout, filename=''.join([os.getcwd(), '\src\icons\https-24px.svg']))

    def initialize_window(self):
        if self.window:
            return
        layout = [[gui.Text('Python Encrypt')],
                  [gui.Text('Please select mode to')],
                  [gui.Button('Encrypt', key=PythonEncryptKeyBinding.ENCRYPT.value)],
                  [gui.Input(key=PythonEncryptKeyBinding.FILE_PATH_ENCRYPT.value), gui.FileBrowse()],
                  [gui.Button('Decrypt', key=PythonEncryptKeyBinding.DECRYPT.value)],
                  [gui.Input(key=PythonEncryptKeyBinding.FILE_PATH_DECRYPT.value),
                                                             gui.FileBrowse(
                                                                 file_types=(('Encrypted Files', '*.aes'),))],
                  [gui.Text('Or')],
                  [gui.Text('Send file to:')], [gui.Input(key='-HOST_INPUT-'), gui.Button('Send', key='-SEND_FILE-')],
                  [gui.Text('Дипломна робота виконана студентом групи КНУС-12')],[gui.Text('Жеребух Юрій-Діонізій Ростиславович')],[gui.Text('2019 рік')],
                  [gui.Cancel()]]
        self._window = gui.Window('Python Encrypt').Layout(layout).Finalize()

    def close_base_window(self):
        self._window.Close()
        self._window = None

    def close_system_tray_icon(self):
        self._tray.Close()

    def clear_path(self):
        self._window.Element(PythonEncryptKeyBinding.FILE_PATH_ENCRYPT.value).Update('')
        self._window.Element(PythonEncryptKeyBinding.FILE_PATH_DECRYPT.value).Update('')

    @property
    def window(self):
        return self._window

    @property
    def tray_icon(self):
        return self._tray


class ProgressBar(BaseWindow):
    def __init__(self, queue, title):
        super().__init__(queue)
        self.title = title

    def _initialize_window(self):
        layout = [[gui.Text(self.title)],
          [gui.ProgressBar(100, orientation='h', size=(20, 20), key='-PROGRESS_ BAR-')]]
        self._window = gui.Window('Python Encrypt Download file', layout).Finalize()

    def update(self, event):
        raise NotImplementedError

    def process_event(self, event):
        self._window.Element('-PROGRESS_ BAR-').UpdateBar(event.data['progress'])


class DownloadProgressBar(ProgressBar):
    def __init__(self, queue, title=f'Downloading file'):
        super().__init__(queue, title)

    def update(self, event):
        self._event = event
        if event.name == EncryptEvent.DOWNLOAD_FILE.value:
            self._initialize_window()
        if event.name == EncryptEvent.DOWNLOAD_PROGRESS.value:
            self.process_event(event)
        if event.name == EncryptEvent.DONE_DOWNLOADING.value:
            self._window.Close()
            self._window = None


class TransferProgressBar(ProgressBar):
    def __init__(self, queue, title=f'Transfer file'):
        super().__init__(queue, title)

    def update(self, event):
        self._event = event
        if event.name == EncryptEvent.TRANSFER_FILE.value:
            self._initialize_window()
        if event.name == EncryptEvent.TRANSFER_PROGRESS.value:
            self.process_event(event)
        if event.name == EncryptEvent.DONE_TRANSFER.value:
            self._window.Close()
            self._window = None
            gui.PopupOK('Successfully sent file')
