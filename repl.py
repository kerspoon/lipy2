
from symbol import NIL
from parse import sexp_str

def repl(context, parser):
    """reads a statement, evaluates it, applys (calls 
       as function) then prints it's result"""
    code = None
    continuation = None
    while(True):
        try:
            if code == None:
                code = parser.next()
                print "repl: code:", sexp_str(code)
                continuation = None # read_eval_continuation(context, reader)
            return lipy_eval(continuation, context, code)
        except StopIteration:
            return None, None

def lipy_eval(continuation, context, code):
    if isinstance(code,str):
        return context.lookup(code)
    elif isinstance(code,list):
        funct = lipy_eval(continuation, context, code[0])
        return funct.apply(continuation, context, code[1])
    else:
        print type(code), code 
        raise Exception("don't know")

def eval_list(continuation, context, args):
    """evaluate every item in the list and return the eval'ed list"""
    if args is NIL: return NIL
    return (lipy_eval(continuation, context, args[0]), 
            lipy_eval(continuation, context, args[1]))

