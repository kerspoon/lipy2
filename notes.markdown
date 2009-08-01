


    def expression_reader():
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

    def lex(reader):
        """a generator which tokenises the sexp"""
        ...

    def parse(tokens):
        """a generator which parses the tokens"""
        ...

    class environment:
          """the environment/context, a dict of name=value"""
          ...

    def repl(context, parser):
        """reads a statement, evaluates it, applys (calls as function)
           then prints it's result"""
        code = None
        continuation = None
        while(True):
            try:
                if code == None:
                    code = parser.next()
                    continuation = read_eval_continuation(context, reader)
                eval(continutation, context, code)
            except CONT as cc:
                print cc.value
                continutation = cc.continutation
                context = cc.context        
            except StopIteration:
                return None, value

    def somefunc(continutation, context):
        ... # do something 
        throw CONT(continutation, context, value)

    def repl(context, parser):
        
    def eval(continutation, context, code):
        if isinstance(code, list):
            return apply(continutation, context, code)
        elif isinstance(code, symbol):
            return (continuation, context.get(str(code)))
        else: 
            return (continuation, code)



