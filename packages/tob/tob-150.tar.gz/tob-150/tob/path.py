# This file is placed in the Public Domain.


"where objects are stored"


import os
import pathlib


from .object import Object


class Workdir:

    wdr = ""

    @staticmethod
    def cdir(path):
        pth = pathlib.Path(path)
        pth.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def path(obj):
        return Workdir.store(Object.ident(obj))

    @staticmethod
    def long(name: str):
        split = name.split(".")[-1].lower()
        res = name
        for names in Workdir.types():
           if split == names.split(".")[-1].lower():
               res = names
               break
        return res

    @staticmethod
    def moddir(modname: str = ""):
        return os.path.join(Workdir.wdr, modname or "mods")

    @staticmethod
    def pidfile(filename):
        if os.path.exists(filename):
            os.unlink(filename)
        path2 = pathlib.Path(filename)
        path2.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as fds:
            fds.write(str(os.getpid()))

    @staticmethod
    def pidname(name: str):
        return os.path.join(Workdir.wdr, f"{name}.pid")

    @staticmethod
    def skel():
        path = Workdir.store()
        if os.path.exists(path):
            return
        pth = pathlib.Path(path)
        pth.mkdir(parents=True, exist_ok=True)
        pth = pathlib.Path(Workdir.moddir())
        pth.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def store(fnm: str = ""):
        return os.path.join(Workdir.wdr, "store", fnm)

    @staticmethod
    def types():
        return os.listdir(Workdir.store())


def __dir__():
    return (
        'Workdir',
    )
