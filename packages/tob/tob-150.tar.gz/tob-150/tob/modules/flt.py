# This file is placed in the Public Domain.


from tob import Broker, Method, Thread


def flt(event):
    clts = Broker.all("announce")
    if event.args:
        index = int(event.args[0])
        if index < len(clts):
            event.reply(Method.fmt(list(clts)[index]), empty=True)
        else:
            event.reply(f"only {len(clts)} clients in fleet.")
        return
    event.reply(' | '.join([Thread.name(o) for o in clts]))
