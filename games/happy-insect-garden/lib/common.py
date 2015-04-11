"""Common code shared between modules.

This module is intended to be imported with 'from ... import *' semantics and
provides an __all__ specification for this purpose.

"""

__all__ = ["cached", "propset", "propdel", "random_point_on_circle",
           "random_point_in_circle", "random_point_in_object", "ease_cubic", "pop_cubic"]


def cached(func):
    """Decorate a function as a caching property.

    Caching properties cache a computed value. The property is read only. The
    first time it is accessed it computes, caches and returns the result.
    Henceforth it returns the cached value.

    """

    cached_name = "_cached_%s" % func.func_name

    def fget(self):
        try:
            return getattr(self, cached_name)
        except AttributeError:
            value = func(self)
            setattr(self, cached_name, value)
            return value

    def fset(self, value):
        setattr(self, cached_name, value)

    def fdel(self):
        try:
            delattr(self, cached_name)
        except AttributeError:
            pass

    fget.func_name = "get_" + func.func_name
    fset.func_name = "set_" + func.func_name
    fdel.func_name = "del_" + func.func_name

    return property(fget, fset, fdel, doc=func.func_doc)


def propset(prop):
    """Decorate a function as a setter for a given property.

    :Parameters:
        `prop` : property
            The property to add the setter to.

    """
    def decorator(func):
        return property(prop.fget, func, prop.fdel, doc=prop.__doc__)
    return decorator


def propdel(prop):
    """Decorate a function as a deleter for a given property.

    :Parameters:
        `prop` : property
            The property to add the deleter to.

    """
    def decorator(func):
        return property(prop.fget, prop.fset, func, doc=prop.__doc__)
    return decorator


def random_point_on_circle(centre, radius):
    from vector import Vector as v
    import random
    return centre + v((radius, 0)).rotated(random.random() * 360)

def random_point_in_circle(centre, radius):
    import random
    return random_point_on_circle(centre, random.random() * radius)

def random_point_in_object(obj):
    return random_point_in_circle(obj.pos, obj.size/2)
    
def ease_cubic(t):
    return (3 - 2 * t) * (t ** 2)

def pop_cubic(t, poppiness=0.4):
    return (2 * t ** 3 - 3 * poppiness * t ** 2)/(2 -  3 * poppiness)