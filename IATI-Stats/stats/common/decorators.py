from collections import defaultdict
import datetime, dateutil.parser, dateutil.tz


# Memoize decorator caches the result of the wrapped function
def memoize(f):
    def wrapper(self):
        if not hasattr(self, 'cache'):
            self.cache = {}
        if not f.__name__ in self.cache:
            self.cache[f.__name__] = f(self)
        return self.cache[f.__name__]
    return wrapper


## Decorators that modify return when self.blank = True etc.
def returns_numberdictdictdict(f):
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper

def returns_numberdictdict(f):
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return defaultdict(lambda: defaultdict(int))
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper

def returns_numberdict(f):
    """ Dectorator for dictionaries of integers. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return defaultdict(int)
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper

def returns_dict(f):
    """ Dectorator for dictionaries. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return {}
        else:
            out = f(self, *args, **kwargs)
            if out is None: return {}
            else: return out
    return wrapper


def returns_number(f):
    """ Decorator for integers. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return 0
        else:
            out = f(self, *args, **kwargs)
            if out is None: return 0
            else: return out
    return wrapper

def no_aggregation(f):
    """ Decorator that perevents aggreagation. """
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return None
        else: return f(self, *args, **kwargs)
    return wrapper


def returns_date(f):
    class LargestDateAggregator(object):
        value = datetime.datetime(1900,1,1, tzinfo=dateutil.tz.tzutc())
        def __add__(self, x):
            if type(x) == datetime.datetime:
                pass
            elif type(x) == LargestDateAggregator:
                x = x.value
            else:
                x = dateutil.parser.parse(x)
            if x > self.value:
                self.value = x
            return self
    def __int__(self):
        return self.value
    def wrapper(self, *args, **kwargs):
        if self.blank:
            return LargestDateAggregator()
        else:
            return f(self, *args, **kwargs)
    return wrapper

