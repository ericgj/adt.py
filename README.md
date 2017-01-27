# adt.py

Simple algebraic data types in Python

  - records (product types)
  - tagged unions (sum types)
  - simple tag-based pattern matching
  - immutable structures
  - records and tagged unions can be pickled/unpickled
  - python 2 and 3 compatible

Tip of the hat to [union-type](https://github.com/paldelpind/union-type), a
javascript library with similar aims and syntax.


## Tagged unions

    Point = Type("Point", [int, int])
    Rectangle = Type("Rectangle", [Point, Point])
    Circle = Type("Circle", [int, Point])
    
    # a union is defined as a sequence of types
    Shape = [ Rectangle, Circle ]
    
    # that then can be matched on
    area = match(Shape, {
      Rectangle: (lambda (t,l), (b,r): (b - t) * (r - l)),
      Circle: (lambda r, _: math.pi * (r**2))
    })
    
    rect = Rectangle( Point(0,0), Point(100,100) )
    area(rect)  # => 10000
    
    circ = Circle( 5, Point(0,0) )
    area(circ)  # => 78.539816...


Note that this is python 2 syntax. Python 3 sadly removed destructuring 
parameters in lambdas, so you have to do something like:

    area = match(Shape, {
      Rectangle: (lambda tl, br: (br[0] - tl[0]) * (br[1] - tl[1])),
      Circle: (lambda r, _: math.pi * (r**2))
    })



## Records

     Point = Record("Point", {'x': int, 'y': int})
     
     # types can be composed of records
     Rectangle = Type("Rectangle", [Point, Point])
     
     # and records composed of types
     Circle = Record("Circle", {'radius': int, 'center': Point} )

     Shape = [ Rectangle, Circle ]

     # including records composed of union types
     ScaledShape = Record("ScaledShape", {'shape': Shape, 'scale': int})
     
     p1 = Point(x=1,y=2)
     p2 = Point(x=4,y=6)
     rect = Rectangle( p1, p2 )
     srect = ScaledShape(shape=rect, scale=10) 


## To install

    pip install adt.py



## License

Copyright (c) 2017 Eric Gjertsen <ericgj72@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
