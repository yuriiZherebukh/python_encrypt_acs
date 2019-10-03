import PySimpleGUI as gui


base_window_layout = [[gui.Text('Python Encrypt')],
                      [gui.Text('Please select mode to')],
                      [gui.Text('Encrypt')], [gui.Input(), gui.FileBrowse()],
                      [gui.Cancel()]]

base_window = gui.Window('Python Encrypt', layout=base_window_layout)
