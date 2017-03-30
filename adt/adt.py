from .f import curry_n
 

def construct_type_instance(tag, specs, args):
  return construct_type(tag, specs)(*args)

def construct_type(tag, specs):
  return Type(tag,specs)

def construct_record_instance(tag, specs, attrs):
  return construct_record(tag, specs)(**attrs)

def construct_record(tag, specs):
  return Record(tag,specs)


def Type(tag, specs):

  class _tagged_tuple(tuple):
    def __eq__(self,other):
      return (
        self.__class__.__name__ == other.__class__.__name__ and 
        super(_tagged_tuple,self).__eq__(other)
      )
     
    # Note: only eval()-able if constructors are in scope with same name as tags     
    def __repr__(self):
      return (
        self.__class__.__name__ + 
        "( " + ", ".join(repr(p) for p in self) + " )"
      )

    # For pickling
    def __reduce__(self):
      nospecs = [ anything for s in specs ]
      return ( construct_type_instance, (tag, nospecs, tuple(v for v in self)) )

  _tagged_tuple.__name__ = tag
  
  @curry_n(len(specs))
  def _bind(*vals):    
    nvals = len(vals)
    nspecs = len(specs)
    if nvals > nspecs:
      raise TypeError( "%s: Expected %d values, given %d" % (tag, nspecs, nvals))
    
    for (i,(s,v)) in enumerate(zip(specs,vals)):
      ok, err = validate(s,v)
      if not ok:
        msg = "%s: Invalid type in field %d: %s" % (tag,i,repr(v))
        if not (err is None):
          msg = "%s\n  %s" % (msg, err)
        raise TypeError(msg)
    
    return _tagged_tuple(vals)
    
  _bind.__name__ = "construct_%s" % tag
  _bind.__adt_class__ = _tagged_tuple
  return _bind


def Record(tag,specs):

  class _record(object):
    __slots__ = specs.keys()

    def __eq__(self,other):
      return (
        self.__class__.__name__ == other.__class__.__name__ and 
        all([ 
          getattr(self,k) == getattr(other,k) 
            for k in self.__class__.__slots__ 
        ]) 
      )
     
    def __repr__(self):
      return (
        self.__class__.__name__ + 
        "( " + 
        ", ".join([ 
          "%s=%s" % (k, repr(getattr(self,k))) 
            for k in self.__class__.__slots__ 
        ]) + 
        " )"
      )

    # For pickling
    def __reduce__(self):
      nospecs = dict([(k,anything) for k in specs.keys()])
      attrs = dict([(k,getattr(self,k)) for k in self.__class__.__slots__])
      return ( construct_record_instance, (tag, nospecs, attrs) )

    def __init__(self,**vals):
      for (k,v) in vals.items():
        if k not in ['__eq__', '__repr__', '__reduce__', '__init__']:
          setattr(self,k,v)

  _record.__name__ = tag

  def _bind(**vals):
    extras = [ ("'%s'" % k) for k in vals.keys() if not k in specs ]
    if len(extras) > 0:
      raise TypeError("%s: Unexpected values given: %s" % (tag, ", ".join(extras)))

    for (name,s) in specs.items():
      if not name in vals:
        raise TypeError("%s: Expected value for '%s', none given" % (tag, name))
      ok, err = validate(s,vals[name])
      if not ok:
        msg = "%s: Invalid type in field '%s': %s" % (tag,name,repr(vals[name]))
        if not (err is None):
          msg = "%s\n  %s" % (msg, err)
        raise TypeError(msg)

    return _record(**vals)

  _bind.__name__ = "construct_%s" % tag
  _bind.__adt_class__ = _record
  return _bind


def anything(x):
  return True

def typeof(adt):
  if not hasattr(adt, '__adt_class__'):
    raise TypeError("Not an ADT constructor")
  return adt.__adt_class__

@curry_n(2)
def seq_of(t,xs):
  return ( 
    hasattr(xs,'__iter__') and all( validate(t,x)[0] for x in xs )
  )

@curry_n(2)
def tuple_of(ts,xs):
  return (
    all( validate(t,x)[0] for (t,x) in zip(ts,xs) )
  )

@curry_n(2)
def one_of(ts,x):
  return any( validate(t,x)[0] for t in ts )

def validate(s,v):
  try:
    return ( isinstance(v,s), None )
  except TypeError:
    try:
      return (
        ( ( type(v) == s ) or
          ( hasattr(s,"__adt_class__") and isinstance(v,typeof(s)) ) or 
          ( callable(s) and s(v) == True ) or
          ( hasattr(s,'__iter__') and (
            any( hasattr(si,"__adt_class__") and isinstance(v,typeof(si)) 
                   for si in s ) 
            )
          )
        ), 
        None
      )
    except Exception as e:
      return (False, e)

 
@curry_n(3)  
def match(adts, cases, target):

  assert target.__class__ in [ typeof(adt) for adt in adts ],  \
    "%s is not in union" % target.__class__.__name__

  missing = [
    t.__adt_class__.__name__ for t in adts \
      if not (type(None) in cases) or (t in cases)
  ]
  assert len(missing) == 0, \
    "No case found for the following type(s): %s" % ", ".join(missing)
  
  fn = None
  wildcard = False
  try:
    fn = ( 
      next( 
        cases[constr] for constr in cases \
          if not constr == type(None) and isinstance(target,typeof(constr)) 
      )
    )

  except StopIteration:
    fn = cases.get(type(None),None)
    wildcard = not fn is None

  # note should never happen due to type assertions above
  if fn is None:
    raise TypeError("No cases match %s" % target.__class__.__name__)
  
  assert callable(fn), \
    "Matched case is not callable; check your cases"

  return fn() if wildcard else fn( *(slot for slot in target) )

