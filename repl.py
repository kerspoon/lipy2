
from symbol import NIL
from parse import sexp_str

class suckmycont():
    def __str__(self):
        raise "poop"

def repl(context, parser):
    """reads a statement, evaluates it, applys (calls 
       as function) then prints it's result"""
    continuation = suckmycont()
    for sexp in parser:
        print "#< ", sexp_str(sexp)
        continuation, result = lipy_eval(continuation, context, sexp)
        print "#> ", sexp_str(result)

    # for sexp in parser:
    #     continuation = make_cont(sexp)
    #     while(continuation != None):
    #         continuation, code = continuation.pop()
    #         continuation, result = lipy_eval(continuation, context, code)

def lipy_eval(continuation, context, code):
    # print "#e ", sexp_str(code)
    if isinstance(code,str):
        return continuation, context.lookup(code)
    elif isinstance(code,list):
        continuation, funct = lipy_eval(continuation, context, code[0])
        # print "#a ", code[0]
        return funct.apply(continuation, context, code[1])
    else:
        print type(code), code 
        raise Exception("don't know")

def eval_list(continuation, context, args):
    """evaluate every item in the list and return the eval'ed list"""
    if args is "nil": return continuation, "nil"
    continuation, first = lipy_eval(continuation, context, args[0])
    continuation, rest = eval_list(continuation, context, args[1])
    return continuation, [first, rest]
