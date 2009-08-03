
from repl import eval_list

class function:
    def __init__(self,func,specialform=False):
        self.func = func
        self.specialform = specialform

    def __str__(self):
        return '#FUNC ' + str(self.func)
        
    def __eq__(self,other):
        if not isinstance(other, function): return False
        return self.func == other.func

    def apply(self, continutation, context, args):
        # we dont evaluate the arguments here with special funcs
        if not self.specialform:
            args = eval_list(continutation, context, args)
        return self.func(continutation, context, args)

#Convert a python function into a form
#suitable for the interpreter
# TODO this should be a deccorator
def predefined_function(function):
    def func(continuation, context, args):
        argList = []
        while args!=None:
            arg, args = args
            argList.append(arg)
        return continuation, function(*argList)
    return function(func)

def display(continutation, context, args):
    print "FUNC display"
    print args[0]

def display2(arg):
    print "mmmmmmm"
    print arg

def func_quote(continutation, context, args):
    print "FUNC QUOTE"
    return args[0]

basic_funcs = [ ("display", function(display)),
                ("nil", "nil"),
                ("quote", function(func_quote,True)),
                ("display2", predefined_function(display2))]


