# This file is placed in the Public Domain.


"an object for a string"


class Broker:

    objects = {}

    @staticmethod
    def add(obj):
        Broker.objects[repr(obj)] = obj
        
    @staticmethod
    def all(attr):
       for obj in Broker.objects.values():
           if attr in dir(obj):
               yield obj

    @staticmethod
    def display(evt):
        bot = Broker.get(evt.orig)
        bot.display(evt)

    @staticmethod
    def get(origin):
        return Broker.objects.get(origin)

    @staticmethod
    def like(txt):
        for orig in Broker.objects:
            if orig.split()[0] in orig.split()[0]:
                yield orig


def __dir__():
    return (
        'Broker',
    )
