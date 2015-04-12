"""Common code shared between modules.

Functions here are usually just helper functions, nothing very game-specific.

"""

__all__ = ["propset", "propdel", "cached", "cachedgen"]

def propset(prop):
    """Decorate a function as a setter for a given property.

    Use the @property decorator first to make the getter, then decorate a
    setter function with the same name as the property using this.

    """
    def decorator(func):
        return property(prop.fget, func, prop.fdel, doc=prop.__doc__)
    return decorator

def propdel(prop):
    """Decorate a function as a deleter for a given property.

    Use the @property decorator first to make the getter, then decorate a
    deleter function with the same name as the property using this.

    """
    def decorator(func):
        return property(prop.fget, prop.fset, func, doc=prop.__doc__)
    return decorator

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

def cachedgen(func):
    """Decorate a generator as a caching property.

    Caching properties cache a computed value. In this case the computer value
    is an iterable with an internal cache. Each time it is iterated over it
    returns a iterator which references back to the parent iterables cache
    as it goes.

    Currently this implementation is not thread safe.

    """

    cached_name = "_cached_%s" % func.func_name

    class CachingIterator(object):
        """Iterator object which checks for cached values, see cachedgen.

        """
        def __init__(self, iterable):
            self.iterable = iterable
            self.idx = 0
        def __iter__(self):
            return self
        def next(self):
            try:
                value = self.iterable.cache[self.idx]
            except IndexError:
                value = self.iterable.generator.next()
                self.iterable.cache.append(value)
            self.idx += 1
            return value

    class CachingIterable(object):
        """Iterable object with cached values, see cachedgen.

        """
        def __init__(self, obj):
            self.cache = []
            self.generator = func(obj)
        def __iter__(self):
            return CachingIterator(self)

    def fget(self):
        try:
            return getattr(self, cached_name)
        except AttributeError:
            value = CachingIterable(self)
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
