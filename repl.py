
from symbol import NIL
from parse import sexp_str

DEBUG = False

class suckmycont():
    def __str__(self):
        raise "poop"

def repl(context, parser):
    """reads a statement, evaluates it, applys (calls 
       as function) then prints it's result"""
    continuation = suckmycont()
    for sexp in parser:
        if DEBUG: print "#< ", sexp_str(sexp)
        continuation, result = lipy_eval(continuation, context, sexp)
        if DEBUG: print "#> ", sexp_str(result)
        return  sexp_str(result) # make a yield 
        # print sexp_str(result) # make a yield 

    # for sexp in parser:
    #     continuation = make_cont(sexp)
    #     while(continuation != None):
    #         continuation, code = continuation.pop()
    #         continuation, result = lipy_eval(continuation, context, code)

def lipy_eval(continuation, context, code):
    if DEBUG: print "#e ", sexp_str(code)
    if isinstance(code,str):
        return continuation, context.lookup(code)
    elif isinstance(code,int):
        return continuation, code
    elif isinstance(code,list):
        continuation, funct = lipy_eval(continuation, context, code[0])
        if DEBUG: print "#a ", code[0]
        return funct.apply(continuation, context, code[1])
    else:
        print type(code), code 
        raise Exception("don't know")

def eval_list(continuation, context, args):
    """evaluate every item in the list and return the eval'ed list"""
    if args == "nil": return continuation, "nil"
    continuation, first = lipy_eval(continuation, context, args[0])
    continuation, rest = eval_list(continuation, context, args[1])
    return continuation, [first, rest]


