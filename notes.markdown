

We have a working lexer, parser and printer. It can take the following BNF:
   
    sexp ==: sym | exp
    exp  ==: '(' sexp* ('.' sexp)? ')'
    sym  ==: [A-Za-z0-9]*

This is converted into a python **list** or a **str**. Which can be printed back out. 


WE do have some kind of eval. Not really sure what is working. 
