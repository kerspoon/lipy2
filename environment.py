
class MissingSym(Exception):
    pass

class AlreadyDefined(Exception):
    pass

class environment:
    """Binds symbols to values. Seperate frame can mean bindings can 
    shadow others. You cannot re-bind something in the same frame though
    you can set it to something else."""

    def __init__(self, syms=[], vals=[], parent = None):
        """create a frame with no parent and the binding given"""
        self.frame = {}
        for sym, val in zip(syms, vals):
            self.frame[sym] = val
        self.parent = parent

    def lookup(self, sym):
        """returns the value bound to the symbol in the environment"""
        if sym in self.frame:
            return self.frame[sym]
        if self.parent is None:
            raise MissingSym("symbol not in environment: " + sym)
        return self.parent.lookup(sym)

    def extend(self, syms, vals):
        """returns a new environment with a frame consisting of the new bindings"""
        return environment(syms, vals, self)

    def add(self, sym, val):
        """adds a new binding to the current frame of the environment"""
        if sym in self.frame:
            raise AlreadyDefined("symbol already in environment: " + sym)
        self.frame[sym] = val

    def set(self, sym, val):
        """changes an existing binding in the environment"""
        if sym in self.frame:
            self.frame[sym] = val
            return
        if self.parent is None:
            raise MissingSym("symbol not in environment: " + sym)
        self.parent.set(sym, val)


def test():
    topenv = environment(["a","b","c"],[1, 2, 3])
    def test1():
        topenv = environment(["a","b","c"],[1, 2, 3])
        assert(topenv.lookup("a") == 1)
        assert(topenv.lookup("b") == 2)
        assert(topenv.lookup("c") == 3)

    def test2():
        newenv = topenv.extend([],[])
        assert(newenv.lookup("a") == 1)
        assert(newenv.lookup("b") == 2)
        assert(newenv.lookup("c") == 3)

    def test3():
        newenv = topenv.extend(["x"],[7])
        assert(newenv.lookup("x") == 7)
        assert(newenv.lookup("a") == 1)
        assert(newenv.lookup("b") == 2)
        assert(newenv.lookup("c") == 3)

    def test4():
        newenv = topenv.extend([],[])
        newenv.add("x", 7)
        assert(newenv.lookup("x") == 7)
        newenv.set("x", 99)
        assert(newenv.lookup("x") == 99)

    def test5():
        try:
            newenv = topenv.extend([],[])
            newenv.add("x", 7)
            newenv.add("x", 7)
            raise Exception("an error should have been thrown")
        except AlreadyDefined:
            pass

    def test6():
        try:
            newenv = topenv.extend([],[])
            newenv.lookup("notdefined")
            raise Exception("an error should have been thrown")
        except MissingSym:
            pass

    def test7():
        try:
            newenv = topenv.extend([],[])
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

test()
