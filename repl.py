

# -----------------------------------------------------------------------------

def repl(env, parser, debug=False):
    """reads a statement, evaluates it, applys (calls 
       as function) then prints it's result"""

    for sexp in parser:
        if debug: print "#< ", str(sexp)
        result = sexp.scm_eval(env)
        if debug: print "#> ", str(result)
        yield str(result)


