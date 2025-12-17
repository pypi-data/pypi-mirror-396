T O B
=====


**NAME**


|
| ``tob`` - bot in reverse !
|


**SYNOPSIS**

::

    >>> from tob.objects import Object
    >>> from tob.serials import Json
    >>> o = Object()
    >>> o.a = "b"
    >>> print(Json.loads(Json.dumps(o)))
    {'a': 'b'}


**DESCRIPTION**

``tob`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, etc.

``tob`` contains python3 code to program objects in a functional
way. it provides an “clean namespace” Object class that only has
dunder methods, so the namespace is not cluttered with method names.
This makes storing and reading to/from json possible.


**INSTALL**

installation is done with pipx

|
| ``$ pipx install tob``
|

**FILES**

|
| ``~/.tob``
| ``~/.local/bin/tob``
| ``~/.local/share/pipx/venvs/tob/*``
|


**AUTHOR**

|
| Bart Thate <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``tob`` is Public Domain.
|
