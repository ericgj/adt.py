from functools import partial, wraps, update_wrapper
from inspect import getargspec

"""
Derived from [fn.py](https://github.com/kachayev/fn.py) function 'curried'
Amended to fix wrapping error: cf. https://github.com/kachayev/fn.py/pull/75

Copyright 2013 Alexey Kachayev 
Under the Apache License, Version 2.0  
http://www.apache.org/licenses/LICENSE-2.0

"""
def curry(func):
  """A decorator that makes the function curried

  Usage example:

  >>> @curry
  ... def sum5(a, b, c, d, e):
  ...     return a + b + c + d + e
  ...
  >>> sum5(1)(2)(3)(4)(5)
  15
  >>> sum5(1, 2, 3)(4, 5)
  15
  """
  @wraps(func)
  def _curry(*args, **kwargs):
      f = func
      count = 0
      while isinstance(f, partial):
          if f.args:
              count += len(f.args)
          f = f.func

      spec = getargspec(f)

      if count == len(spec.args) - len(args):
          return func(*args, **kwargs)
          
      para_func = partial(func, *args, **kwargs)
      update_wrapper(para_func, f)
      return curry(para_func)
      
  return _curry


def curry_n(n):
  def _curry_n(func):
    @wraps(func)
    def _curry(*args, **kwargs):
      f = func
      
      count = 0
      while isinstance(f, partial) and count < n:
        if f.args:
          count += len(f.args)
        f = f.func

      if count >= n - len(args):
        return func(*args, **kwargs)
          
      para_func = partial(func, *args, **kwargs)
      update_wrapper(para_func, f)
      return _curry_n(para_func)
        
    return _curry
  
  return _curry_n
   

