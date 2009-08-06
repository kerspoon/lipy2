
from parse import sexp_str
from trampoline import trampoline, thunk, identity

DEBUG = False  

def repl(context, parser):
    """reads a statement, evaluates it, applys (calls 
       as function) then prints it's result"""

    for sexp in parser:
        if DEBUG: print "#< ", sexp_str(sexp)
        result = trampoline(lipy_eval)(context, sexp, identity)
        if DEBUG: print "#> ", sexp_str(result)
        yield sexp_str(result)

# lipy_eval :: Context -> sexp -> (sexp -> None) -> None
def lipy_eval(context, code, continuation):
    if DEBUG: print "#e ", sexp_str(code), continuation
    if isinstance(code,str):
        # print "lookup", code, "=", context.lookup(code)
        return thunk(continuation)(context.lookup(code))
    elif isinstance(code,int):
        # print continuation, code 
        return thunk(continuation)(code)
    elif isinstance(code,list):
        if DEBUG: print "#a ", sexp_str(code)
        # inner_apply :: sexp -> None
        def inner_apply(func):
            # print "inner_apply", func
            return thunk(func)(context, code[1], continuation)
        return thunk(lipy_eval)(context, code[0], inner_apply)
    else:
        return "Error 1:", type(code), code 

# eval_list :: Context -> sexp -> (sexp -> None) -> None
def eval_list(context, args, continuation):
    """evaluate every item in the list and return the eval'ed list"""

    # print "eval_list", args, continuation

    if args == "nil": 
        return thunk(continuation)("nil")

    def inner2(first, rest):
        # print "inner2", first, rest
        return thunk(continuation)([first, rest])

    def eval_list_inner(first):
        # print "inner", first
        return thunk(eval_list)(context, args[1], lambda x: inner2(first,x))

    return thunk(lipy_eval)(context, args[0], eval_list_inner)


# -------------------------------------------------------------------------
# -------------------------------------------------------------------------

# lipy_quote :: Context -> sexp -> (sexp -> None) -> None
