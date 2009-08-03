

class symbol:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return "symbol('"+self.value+"')"

    def __eq__(self, value):
        if isinstance(value, symbol):
            return self.value == value.value
        else:
            return False

# Predefined Symbols (can't be redefined)
NIL = symbol("nil")
QUOTE = symbol("quote")

# LAMBDA = symbol("lambda")
# IF = symbol("if")
# BEGIN = symbol("begin")
# SET = symbol("set!")
# DEFINE = symbol("define")
# LOAD = symbol("load")

