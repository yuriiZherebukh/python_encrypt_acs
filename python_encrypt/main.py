from python_encrypt.gui.base import base_window


while True:
    event, values = base_window.Read(timeout=1000)
    if event in ('Cancel', None):
        base_window.Close()
        break
