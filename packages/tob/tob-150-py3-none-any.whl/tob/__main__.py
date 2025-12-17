# This file is placed in the Public Domain.


import os
import sys
import threading
import time


from . import CLI, Command, Event, Kernel, Logging, Main, Mods, Method
from . import Static, Thread, Workdir
from . import modules as MODS


Main.ignore = "wsd,udp"
Main.level = "info"
Main.name = "tob" 
Main.version = 150


Mods.addpkg(MODS)


Workdir.wdr = os.path.expanduser(f"~/.{Main.name}")


class CLI(CLI):

    def raw(self, text):
        print(text.encode('utf-8', 'replace').decode("utf-8"))


class Console(CLI):

    def callback(self, event):
        if not event.text:
            return
        super().callback(event)
        event.wait()

    def poll(self):
        evt = Event()
        evt.text = input("> ")
        evt.kind = "command"
        return evt


class Runtime:

    @staticmethod
    def banner():
        tme = time.ctime(time.time()).replace("  ", " ")
        print("%s %s since %s (%s)" % (
                                       Main.name.upper(),
                                       Main.version,
                                       tme,
                                       Main.level.upper()
                                      ))
        sys.stdout.flush()

    @staticmethod
    def check(text):
        args = sys.argv[1:]
        for arg in args:
            if not arg.startswith("-"):
                continue
            for char in text:
                if char in arg:
                   return True

        return False

    @staticmethod
    def daemon(verbose=False, nochdir=False):
        pid = os.fork()
        if pid != 0:
            os._exit(0)
        os.setsid()
        pid2 = os.fork()
        if pid2 != 0:
            os._exit(0)
        if not verbose:
            with open('/dev/null', 'r', encoding="utf-8") as sis:
                os.dup2(sis.fileno(), sys.stdin.fileno())
            with open('/dev/null', 'a+', encoding="utf-8") as sos:
                os.dup2(sos.fileno(), sys.stdout.fileno())
            with open('/dev/null', 'a+', encoding="utf-8") as ses:
                os.dup2(ses.fileno(), sys.stderr.fileno())
        if not nochdir:
            os.umask(0)
            os.chdir("/")
        os.nice(10)

    @staticmethod
    def privileges():
        import getpass
        import pwd
        pwnam2 = pwd.getpwnam(getpass.getuser())
        os.setgid(pwnam2.pw_gid)
        os.setuid(pwnam2.pw_uid)

    @staticmethod
    def wrap(func):
        import termios
        old = None
        try:
            old = termios.tcgetattr(sys.stdin.fileno())
        except termios.error:
            pass
        try:
            Runtime.wrapped(func)
        finally:
            if old:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)

    @staticmethod
    def wrapped(func):
        try:
            func()
        except (KeyboardInterrupt, EOFError):
            pass


class Scripts:

    @staticmethod
    def background():
        Runtime.daemon(Runtime.check("v"), Runtime.check("m"))
        Runtime.privileges()
        Workdir.pidfile(Workdir.pidname(Main.name))
        Command.add(Cmds.cmd, Cmds.ver)
        Kernel.scanner(Mods.list() or "irc,rss")
        Kernel.init(Mods.list() or "irc,rss")
        Kernel.forever()

    @staticmethod
    def console():
        import readline
        readline.redisplay()
        Method.parse(Main, " ".join(sys.argv[1:]))
        Main.ignore = Main.sets.ignore or Main.ignore
        Logging.level(Main.sets.level or Main.level or "info")
        if "v" in Main.opts:
            Runtime.banner()
        if "a" in Main.opts:
            Main.init = Mods.list()
        else:
            Main.init = Main.sets.init or Main.init
        Kernel.scanner(Mods.list())
        Command.add(Cmds.cmd, Cmds.ver)
        Kernel.init(Main.init, "w" in Main.opts)
        csl = Console()
        csl.start()
        Kernel.forever()

    @staticmethod
    def control():
        if len(sys.argv) == 1:
            return
        Kernel.scanner(Mods.list())
        Command.add(Cmds.cmd, Cmds.srv, Cmds.ver)
        csl = CLI()
        csl.silent = False
        evt = Event()
        evt.orig = repr(csl)
        evt.text = " ".join(sys.argv[1:])
        evt.type = "command"
        Command.command(evt)
        evt.wait()

    @staticmethod
    def service():
        Runtime.privileges()
        Workdir.pidfile(Workdir.pidname(Main.name))
        Logging.level(Main.level)
        Kernel.scanner(Main.init or "irc,rss")
        Command.add(Cmds.cmd, Cmds.ver)
        Kernel.init(Main.init or "irc,rss")
        Kernel.forever()


class Cmds:

    @staticmethod
    def cmd(event):
        event.reply(",".join(sorted(Command.names or Command.cmds)))

    @staticmethod
    def srv(event):
        import getpass
        name = getpass.getuser()
        event.reply(Static.SYSTEMD % (Main.name.upper(), name, name, name, Main.name))

    @staticmethod
    def ver(event):
        event.reply(f"{Main.name.upper()} {Main.version}")


def main():
    Workdir.skel()
    check = Runtime.check
    if check("b"):
        threading.excepthook = Thread.threadhook
    if check('z'):
        Main.debug = True
    if check("c"):
        Runtime.wrap(Scripts.console)
    elif check("d"):
        Scripts.background()
    elif check("s"):
        Runtime.wrapped(Scripts.service)
    else:
        Runtime.wrapped(Scripts.control)


if __name__ == "__main__":
    main()
