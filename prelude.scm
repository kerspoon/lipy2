(define (not x) (if x false true))
(define (null obj) (if (eq obj '()) true false))
(define (id x) x)
(define (flip f) (lambda(x y) f y x))
(define (list x) (cons x '()))
(define (curry f x) (lambda(y) apply f (cons x y)))
(define (compose f g) (lambda(x) f (apply g x)))
(define (foldr f x xs)
  (if (null xs)
    x
    (f
      (car xs)
      (foldr f x (cdr xs)))))
(define (foldl f x xs)
  (if (null xs)
    x
    (foldl
      f
      (f x (car xs))
      (cdr xs))))
(define (unfold func init pred)
  (if (pred init)
      (cons init '())
      (cons init (unfold func (func init) pred))))
(define fold foldl)
(define (inject x f xs)  (foldl f x xs))
(define (reduce f xs)    (foldl f (car xs) (cdr xs)))
(define (pick f) (lambda(x y) if (f x y) x y))
(define zero              (curry = 0))
(define positive          (curry < 0))
(define negative          (curry > 0))
(define (odd num)         (= (mod num 2) 1))
(define (even num)        (= (mod num 2) 0))
(define assert
  (lambda(m x y) if (= x y) true (cons m (cons x y) ) ) )
(define concat
  (lambda(x y) foldr (lambda(a b) cons a b) y x) )
(assert 'concat (concat '(1 2 3) '(4 5 6)) '(1 2 3 4 5 6))

