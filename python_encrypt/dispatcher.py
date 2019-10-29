import logging

logging.getLogger().setLevel(logging.DEBUG)


class EventDispatcher:
    def __init__(self, queue):
        self._queue = queue
        self._windows = list()

    def register(self, window):
        self._windows.append(window)

    def unregister(self, window):
        self._windows.remove(window)

    def notify(self, event):
        for window in self._windows:
            window.update(event)

    def dispatch(self):
        if self._queue.empty():
            pass
        else:
            event = self._queue.get()
            logging.debug(f'Dispatcher: Received event: {event.name}')
            self.notify(event)

