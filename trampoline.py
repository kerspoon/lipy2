


thunk = lambda name: lambda *args: lambda: name(*args)

identity = lambda x: x

def _trampoline(bouncer):
    while callable(bouncer):
        bouncer = bouncer()
    return bouncer

trampoline = lambda f: lambda *args: _trampoline(f(*args))

