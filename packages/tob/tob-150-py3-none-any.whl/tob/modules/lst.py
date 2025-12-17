# This file is been placed in the Public Domain.


from tob import Workdir


def lst(event):
    tps = Workdir.types()
    if tps:
        event.reply(",".join({x.split(".")[-1].lower() for x in tps}))
    else:
        event.reply("no data yet.")
