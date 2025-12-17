# This file is placed in the Public Domain.


"callback engine"


import queue


from .thread  import Thread


class Engine:

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()

    def callback(self, event):
        func = self.cbs.get(event.kind, None)
        if not func:
            event.ready()
            return
        name = event.text and event.text.split()[0]
        event._thr = Thread.launch(func, event, name=name)

    def loop(self):
        while True:
            event = self.poll()
            if not event:
                break
            event.orig = repr(self)
            self.callback(event)

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put(event)

    def register(self, kind, callback):
        self.cbs[kind] = callback

    def start(self):
        Thread.launch(self.loop)

    def stop(self):
        self.queue.put(None)



def __dir__():
    return (
        'Engine',
    )
