# This file is placed in the Public Domain.


"configuration"


from .object import Default


class Main:

    debug = False
    ignore = ""
    init = ""
    level = "info"
    name = ""
    opts = ""
    sets = Default()
    version = 0


def __dir__():
    return (
        'Main',
    )
