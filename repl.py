
from parse import sexp_str
from trampoline import trampoline, thunk, identity

DEBUG = True  

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
    if DEBUG: print "#e ", sexp_str(code)
    if isinstance(code,str):
        return thunk(continuation)(context.lookup(code))
    elif isinstance(code,int):
        return thunk(continuation)(code)
    elif isinstance(code,list):
        if DEBUG: print "#a ", sexp_str(code)
        # inner_apply :: sexp -> None
        inner_apply = lambda func: func(context, code[1], continuation)
        return thunk(lipy_eval)(context, code[0], inner_apply)
    else:
        return "Error 1"

# eval_list :: Context -> sexp -> (sexp -> None) -> None
def eval_list(context, args, continuation):
    """evaluate every item in the list and return the eval'ed list"""
    if args == "nil": 
        return thunk(continuation)("nil")

    inner2 = lambda first, rest: thunk(continuation)([first, rest])
    inner = lambda first: eval_list(context, args[1], lambda x: inner2(first,x))

    lipy_eval(context, args[0], inner)


# -------------------------------------------------------------------------
# -------------------------------------------------------------------------

# # lipy_quote :: Context -> sexp -> (sexp -> None) -> None
# def lipy_quote(context, args, continuation):
#     return thunk(continuation)(args[0])


# # lipy_if :: Context -> sexp -> (sexp -> None) -> None
# def lipy_if(context, args, continuation):
    
#     (condition, (true_thunk, (false_thunk, tmp_nil))) = args
#     assert tmp_nil == "nil"

#     # inner_if :: sexp -> None
#     def inner_if(evaluated_args):
#         if ( evaluated_args == 'true' ):
#             return thunk(lipy_eval)(context, true_thunk, continuation)
#         else:
#             return thunk(lipy_eval)(context, false_thunk, continuation)

#     return thunk(lipy_eval)(context, condition, inner_if)

# def testerere():
    
#     from lex import tokenize
#     from parse import parse
#     from environment import environment

#     basic_environment = [
#         ("nil", "nil"),
#         ("true", "true"),
#         ("false", "false"),
#         ("quote" , lipy_quote),
#         ("if" , lipy_if)]

#     inp = "(if false 'hello 'goodbye)"

#     syms, vals = zip(*basic_environment)
#     env = environment(syms, vals)
#     for result in repl(env.extend([],[]),parse(tokenize([inp]))):
#         print result

# testerere()
