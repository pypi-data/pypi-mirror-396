# This file is placed in the Public Domain.


"in the beginning"


import time


from .cmnd   import Command
from .config import Main
from .pkg    import Mods
from .thread import Thread
from .utils  import Utils


class Kernel:

    @staticmethod
    def forever():
        while True:
            try:
                time.sleep(0.1)
            except (KeyboardInterrupt, EOFError):
                break

    @staticmethod
    def init(names, wait=False):
        mods = []
        thrs = []
        for name in Utils.spl(names):
            if name in Utils.spl(Main.ignore):
                continue
            mod = Mods.get(name)
            if "init" not in dir(mod):
                continue
            thrs.append(Thread.launch(mod.init))
            mods.append(name)
        if wait:
            for thr in thrs:
                thr.join()
        return mods

    @staticmethod
    def scanner(names):
        for mod in Mods.mods(names):
            Command.scan(mod)


def __dir__():
    return (
        'Kernel',
    )
