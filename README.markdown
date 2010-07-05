LiPi - Lisp in Python
====

A smallish lisp/scheme implementation using python. It has a small test suite but only test for success at the moment. Nothing of special interest, I have tried to keep the code clean-ish but I have been playing with more complex python so the results of my efforts might have resulted in overly complex sections. 

This is my 5th lisp implementation, the previous ones have been in C++, D, D again, and a previous version in Python. I really haven't tried to do anything new. 

We have a working lexer, parser and printer. It can take the following BNF:
   
    sexp   ==: symbol | int | string | list
    list   ==: '(' sexp* ('.' sexp)? ')'
    symbol ==: [A-Za-z0-9]*
    int    ==: ('+'|'-')?[0-9]*
    string ==: '"' ([A-Za-z0-9] | whitespace)* '"'

This is converted into a python **list** or a **str**. Which can be printed back out. We can 'eval' properly and the test list works apart from printing functions and procedures. 

I have just addded basic classes, these are unusual (for me) in that there is no difference between a class and an object. It's all crazy dynamic. 

It used to use CPS to help tail calls and give call/cc but I changed it all back to make the code neater.

Long Term Goal
=============

I would like a type-checked, objected-orientated lisp with a good module system and simple macros. If I was to ever used it for real coding I would need good error messages, a large library and integration with emacs at the least but as that will take forever I intend to focus on the interesting rather than the practicle. It is mearly a proof of concept. 

 + Objected Orientated 
 + Type Checked
 + Good Module System
 + Simple Macros

To Do
=====

  - Deal with errors better
  - Add more built in functions and macros
  - Think about modules and objects (import)

The syntax for classes is a bit messy. I still havent decided the best way to call their functions, access their elements and change their elements. 


Structure
====

 + *lex* - tokenise a string into a list of string tokens
 + *parse* - convert tokens into datatypes
 + *datatypes* - all the data in scheme is of one of these types
 + *environment* - anything defined in lipy get stored in an environment
 + *function* - all built in lipy function calls as well as the default env that includes these defaults
 + *main* - tests and misc
 + *prelude* - some default scheme functions taken from Haskell

