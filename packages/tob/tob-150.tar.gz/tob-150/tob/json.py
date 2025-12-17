# This file is placed in the Public Domain.


"realisation of serialisation"


import json as jsn
import types


class Encoder(jsn.JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, list):
            return iter(o)
        if isinstance(o, types.MappingProxyType):
            return dict(o)
        try:
            return jsn.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)


class Json:

    @staticmethod
    def dump(*args, **kw):
        kw["cls"] = Encoder
        return jsn.dump(*args, **kw)

    @staticmethod
    def dumps(*args, **kw):
        kw["cls"] = Encoder
        return jsn.dumps(*args, **kw)

    @staticmethod
    def load(s, *args, **kw):
        return jsn.load(s, *args, **kw)

    @staticmethod
    def loads(s, *args, **kw):
        return jsn.loads(s, *args, **kw)


def __dir__():
   return (
       'Json',
   )
