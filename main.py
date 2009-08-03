

from lex import tokenize
from parse import parse
from environment import environment

def reader_raw():
    """a generator which returns one complete sexp as a string"""
    code = ""
    brackets = 0
    while True:
        if code == "":
            prompt = ">>>"
        else:
            prompt = "..."
        ln = raw_input(prompt)
        code+=ln+" "
        brackets+=ln.count("(") -  ln.count(")")
        if brackets == 0 and len(ln.strip())!=0:
            yield code
            code = ""

def repl(context, parser):
    """reads a statement, evaluates it, applys (calls 
       as function) then prints it's result"""
    
    code = None
    continuation = None
    while(True):
        try:
            if code == None:
                code = parser.next()
                continuation = None # read_eval_continuation(context, reader)
            return lipy_eval(continuation, context, code)
        except StopIteration:
            return None, None

def lipy_eval(continuation, context, code):
    if isinstance(code,str):
        return context.lookup(code)
    elif isinstance(code,list):
        function = lipy_eval(continuation, context, code[0])
        return function.apply(continuation, context, code[1])
    else:
        raise Exception("don't know")

def eval_list(continuation, context, args):
    """evaluate every item in the list and return the eval'ed list"""
    if args is NIL: return NIL
    return (lipy_eval(continuation, context, obj[0]), 
            lipy_eval(continuation, context, obj[1]))

print repl(environment(),parse(tokenize(["(display 'hello)"])))

# print repl(environment(),parse(tokenize(reader_raw())))
