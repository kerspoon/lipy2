
from lex import tokenize
from parse import parse
from environment import environment
from function import basic_funcs, function
from repl import repl

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

syms, vals = zip(*basic_funcs)
print repl(environment(syms, vals), parse(tokenize(["(display 'hello)"])))

# print repl(environment(),parse(tokenize(reader_raw())))
