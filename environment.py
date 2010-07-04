
class MissingSym(Exception):
    pass

class AlreadyDefined(Exception):
    pass

# ------------------------------------------------------------------------------

class Environment:
    """Binds symbols to values. Seperate frame can mean bindings can 
    shadow others. You cannot re-bind something in the same frame though
    you can set it to something else."""

    def __init__(self, syms, vals, parent):
        # func init :: [Str] -> [LispBase] -> Optional Environment 'parent' -> Environment
        self.frame = {}
        self.parent = parent
        for sym, val in zip(syms, vals):
            assert(isinstance(sym, str))
            self.frame[sym] = val

    def add(self, sym, val):
        # func add :: Str 'sym' -> SchemeBase 'val' -> None
        assert(isinstance(sym, str))
        if sym in self.frame:
            raise AlreadyDefined("symbol already in environment: " + sym)
        self.frame[sym] = val

    def get(self, sym):
        # func get :: Str 'sym' -> SchemeBase
        assert(isinstance(sym, str))
        if sym in self.frame:
            return self.frame[sym]
        if self.parent is None:
            raise MissingSym("symbol not in environment: " + sym)
        return self.parent.get(sym)

    def set(self, sym, val):
        # func set :: Str 'sym' -> SchemeBase 'val' -> None
        assert(isinstance(sym, str))
        if sym in self.frame:
            self.frame[sym] = val
        elif self.parent is None:
            raise MissingSym("symbol not in environment: " + sym)
        else:
            return self.parent.set(sym, val)

    def __str__(self):
        # func __str__ :: None -> Str
        ret = "\n"
        for sym, val in self.frame.items():
            ret += sym + " = " + str(val) + "\n"
        ret += "---\n"
        if self.parent is not None:
            ret += str(self.parent)
        else:
            ret += "===\n"
        return ret

# ------------------------------------------------------------------------------

def test():
    topenv = Environment(["a","b","c"],[1, 2, 3], None)
    def test1():
        topenv = Environment(["a","b","c"], [1, 2, 3], None)
        assert(topenv.get("a") == 1)
        assert(topenv.get("b") == 2)
        assert(topenv.get("c") == 3)

    def test2():
        newenv = Environment([], [], topenv)
        assert(newenv.get("a") == 1)
        assert(newenv.get("b") == 2)
        assert(newenv.get("c") == 3)

    def test3():
        newenv = Environment(["x"],[7], topenv)
        assert(newenv.get("x") == 7)
        assert(newenv.get("a") == 1)
        assert(newenv.get("b") == 2)
        assert(newenv.get("c") == 3)

    def test4():
        newenv = Environment([], [], topenv)
        newenv.add("x", 7)
        assert(newenv.get("x") == 7)
        newenv.set("x", 99)
        assert(newenv.get("x") == 99)

    def test5():
        try:
            newenv = Environment([], [], topenv)
            newenv.add("x", 7)
            newenv.add("x", 7)
            raise Exception("an error should have been thrown")
        except AlreadyDefined:
            pass

    def test6():
        try:
            newenv = Environment([], [], topenv)
            newenv.get("notdefined")
            raise Exception("an error should have been thrown")
        except MissingSym:
            pass

    def test7():
        try:
            newenv = Environment([], [], topenv)
            newenv.set("x", 7)
            raise Exception("an error should have been thrown")
        except MissingSym:
            pass

    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()

# test()
