# This file is placed in the Public domain.


"utilities"


class Utils:

    @staticmethod
    def spl(txt):
        try:
            result = txt.split(",")
        except (TypeError, ValueError):
            result = []
        return result


def __dir__():
    return (
        'Utils',
    )
