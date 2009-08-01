

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
                continuation = read_eval_continuation(context, reader)
            return lipy_eval(continutation, context, code)
        except StopIteration:
            return None, None

print repl(environment(),parse(tokenise(reader_raw())))
