# This file is placed in the Public Domain.


"write your own commands"


import inspect


from .broker import Broker
from .method import Method


class Command:

    cmds = {}
    names = {}

    @staticmethod
    def add(*args):
        for func in args:
            name = func.__name__
            Command.cmds[name] = func
            Command.names[name] = func.__module__.split(".")[-1]

    @staticmethod
    def command(evt):
        Method.parse(evt, evt.text)
        func = Command.get(evt.cmd)
        if func:
           func(evt)
           Broker.display(evt)
        evt.ready()

    @staticmethod
    def get(cmd):
        return Command.cmds.get(cmd, None)

    @staticmethod
    def scan(module):
        for key, cmdz in inspect.getmembers(module, inspect.isfunction):
            if 'event' not in inspect.signature(cmdz).parameters:
                continue
            Command.add(cmdz)


def __dir__():
    return (
        'Command',
    )
