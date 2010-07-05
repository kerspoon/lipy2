LiPi
====

Lisp in Python

A smallish lisp/scheme implementation using python.  It has a small test suite but only test for success at the moment. Nothing of special interest, I have tried to keep the code clean-ish but I have been playing with more complex python so the results of my efforts might have resulted in overly complex sections. 

This is my 5th lisp implementation, the previous ones have been in C++, D, D again, and a previous version in Python. I really haven't tried to do anything new. 

We have a working lexer, parser and printer. It can take the following BNF:
   
    sexp   ==: symbol | int | string | list
    list   ==: '(' sexp* ('.' sexp)? ')'
    symbol ==: [A-Za-z0-9]*
    int    ==: ('+'|'-')?[0-9]*
    string ==: '"' ([A-Za-z0-9] | whitespace)* '"'

This is converted into a python **list** or a **str**. Which can be printed back out. We can 'eval' properly and the test list works apart from printing functions and procedures. 

ToDo
====

It mostly works, decided to get rid of CPS to make the code a bit neater. 

  - Add classes
  - Deal with errors better
  - Add more built in functions and macros
  - Think about modules and objects (import)
  - Libraries, libraries, libraries
  - csv file parser

Things to add
==============

^ / * eq equal <> not and or read assert


(define (length xs) 
  (xs,  inject
        0 
        (lambda(x y) + x 1)))

(define (reverse xs)
  (xs,  inject
        '()
        (flip cons)))

(define (map f xs)
  (xs,  foldr
        (lambda(x y) cons (f x) y)
        '()))
(define (filter f xs)
  (xs,  foldr
        (lambda(x y) if (f x) (cons x y) y)
        '()))

(define quick-sort (lambda(xs) 
  if  (xs, null)
      '()
      (concat (concat (((xs, cdr), filter (curry >= (xs, car))), quick-sort)
      (list (xs, car)))
              (((xs, cdr), filter (curry < (xs, car))), quick-sort))))


(define (max xs) (xs,  reduce (pick >)))
(define (min xs) (xs,  reduce (pick <)))
(define (sum xs)         (xs, reduce +  ))
(define (product xs)     (xs, reduce *  ))
(define (and xs)         (xs, reduce && ))
(define (or  xs)         (xs, reduce || ))
