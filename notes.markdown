

We have a working lexer, parser and printer. It can take the following BNF:
   
    sexp ==: sym | exp
    exp  ==: '(' sexp* ('.' sexp)? ')'
    sym  ==: [A-Za-z0-9]*

This is converted into a python **list** or a **str**. Which can be printed back out. We can 'eval' properly and the test list works apart from printing functions and procedures. 

To Do:
  > change apply to __call__ so that built-ins can be passed naked. 
  > allow functions and lambdas to be printed
  > read from file
  > call with current continuation
  > strings
  > tail call optimisation
  > macros
  > csv file parser

^ + - / * = eq equal < > <= >= <> not and or display newline read 

