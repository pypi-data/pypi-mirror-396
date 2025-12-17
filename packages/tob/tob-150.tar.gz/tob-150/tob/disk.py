# This file is placed in the Public Domain.


"disk persistence"


import json
import os
import threading
import time


from .json   import Json
from .method import Method
from .object import Object
from .path   import Workdir


class Cache:

    objects = {}

    @staticmethod
    def add(path, obj):
        Cache.objects[path] = obj

    @staticmethod
    def get(path):
        return Cache.objects.get(path, None)

    @staticmethod
    def sync(path, obj):
        try:
            Object.update(Cache.objects[path], obj)
        except KeyError:
            Cache.add(path, obj)


class Disk:

    lock = threading.RLock()

    @staticmethod
    def read(obj, path):
        with Disk.lock:
            with open(path, "r", encoding="utf-8") as fpt:
                try:
                    Object.update(obj, Json.load(fpt))
                except json.decoder.JSONDecodeError as ex:
                    ex.add_note(path)
                    raise ex

    @staticmethod
    def write(obj, path=""):
        with Disk.lock:
            if path == "":
                path = Workdir.path(obj)
            Workdir.cdir(path)
            with open(path, "w", encoding="utf-8") as fpt:
                Json.dump(obj, fpt, indent=4)
            Cache.sync(path, obj)
            return path


class Locate:

    @staticmethod
    def attrs(kind):
        objs = list(Locate.find(kind))
        if objs:
            return list(Object.keys(objs[0][1]))
        return []

    @staticmethod
    def find(kind, selector={}, removed=False, matching=False):
        fullname = Workdir.long(kind)
        for pth in Locate.fns(fullname):
            obj = Cache.get(pth)
            if not obj:
                obj = Object()
                Disk.read(obj, pth)
                Cache.add(pth, obj)
            if not removed and Method.deleted(obj):
                continue
            if selector and not Method.search(obj, selector, matching):
                continue
            yield pth, obj

    @staticmethod
    def fns(kind):
        path = Workdir.store(kind)
        for rootdir, dirs, _files in os.walk(path, topdown=True):
            for dname in dirs:
                if dname.count("-") != 2:
                    continue
                ddd = os.path.join(rootdir, dname)
                for fll in os.listdir(ddd):
                    yield os.path.join(ddd, fll)

    @staticmethod
    def fntime(daystr):
        datestr = " ".join(daystr.split(os.sep)[-2:])
        datestr = datestr.replace("_", " ")
        if "." in datestr:
            datestr, rest = datestr.rsplit(".", 1)
        else:
            rest = ""
        timed = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
        if rest:
            timed += float("." + rest)
        return float(timed)

    @staticmethod
    def last(obj, selector={}):
        result = sorted(
                        Locate.find(Object.fqn(obj), selector),
                        key=lambda x: Locate.fntime(x[0])
                       )
        res = ""
        if result:
            inp = result[-1]
            Object.update(obj, inp[-1])
            res = inp[0]
        return res


def __dir__():
    return (
        'Cache',
        'Disk',
        'Locate'
    )
