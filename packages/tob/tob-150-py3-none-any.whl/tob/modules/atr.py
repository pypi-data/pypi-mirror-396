# This file is placed in the Public Domain.


"fields"


from tob import Locate, Workdir


def atr(event):
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in Workdir.types()])
        if res:
            event.reply(",".join(res))
        else:
            event.reply("no types")
        return
    items = Locate.attrs(event.args[0])
    if not items:
        event.reply("no fields")
    else:
        event.reply(",".join(items))
