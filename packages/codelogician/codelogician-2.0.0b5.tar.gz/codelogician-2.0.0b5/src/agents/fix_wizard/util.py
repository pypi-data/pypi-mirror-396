# fmt: off
# ruff: noqa
from functools import partial as bind, reduce
import json
import itertools

# --- General purpose utils --------------------------

delay = bind(bind, bind)
def delay_decorator(d): return lambda f: lambda *args: d(bind(f, *args))

def splice(f): return lambda args: f(*args)
def unsplice(f): return lambda *args: f(args)
def identity(x): return x
def compose2(f, g): return lambda x: f(g(x))
def compose(*fs): return reduce(compose2, fs)
def const(x): return lambda _: x
def fst(xy): x, _ = xy; return x
def snd(xy): _, y = xy; return y
def ffst(f): return lambda xy: (f(xy[0]), xy[1])
def fsnd(f): return lambda xy: (xy[0], f(xy[1]))
def fboth(f): return lambda xy: (f(xy[0]), f(xy[1]))
def prod(f, g): return lambda xy: (f(xy[0]), g(xy[1]))
def forkl(f): return lambda x: (f(x), x)
def forkr(f): return lambda x: (x, f(x))
def swap(xy): x, y = xy; return y, x
def flip(f): return compose(f, swap)
def pair_with(x): return lambda y: (x,y)

def raise_(x): raise x
def foreach(f, xs):
    for x in xs: f(x)
def with_as(c,f):
    with c as x: return f(x)

class Context(object):
    def __init__(self, setup): self.setup = setup
    def __exit__(self, _1, exc, _3): self.cleanup()
    def __enter__(self):
        self.cleanup, x = self.setup()
        return x

def guard(p, x): return x if p(x) else None
def maybe_else(if_none, f, x): return if_none if x is None else f(x)
def maybe_lazy(if_none, f, x): return if_none() if x is None else f(x)

def translate(d, x): return d.get(x,x)
def filter_dict_vals(pred, d): return {k:v for k, v in d.items() if pred(v)}
def map_dict_vals(f, d): return {k:f(v) for k, v in d.items()}
def maybe_dict(**d): return filter_dict_vals(not_none, d)
def index_by(f,xs): return {f(x): x for x in xs}
def fkey(k,f): return lambda d: {**d, k:f(d[k])}
def skey(key, x): return lambda d: {**d, key: x}

def append(x): return lambda y: y + [x]
def not_empty(xs): return len(xs) > 0
def not_none(x): return x is not None
def map(f, xs): return [f(x) for x in xs]
def filter(f, xs): return [x for x in xs if f(x)]
def flat_map(f, xs): return [y for x in xs for y in f(x)]
def concat(ys): return [x for y in ys for x in y]
def find(p, xs): return next((x for x in xs if p(x)), None)
def batch(n, items): return map(list, itertools.batched(items, n))

def map_accum(f, xs, s):
    ys = []
    for x in xs:
        y, s = f(x, s)
        ys.append(y)
    return ys, s

def group_by_fn(f, items):
    return map(fsnd(list), itertools.groupby(sorted(items, key=f), key=f))

def group_snd_by_fst(pairs):
    return map(fsnd(bind(map, snd)), group_by_fn(fst, pairs))

@splice
def distr(x, ys): return [(x, y) for y in ys]

def uniq(xs):
    seen = set()
    return [x for x in xs if x not in seen or seen.add(x)]

def foldr(f, xs, s): return s if xs == [] else f(xs[0], foldr(f, xs[1:], s))

def file_opener(filename): return bind(open, filename, 'r')
def text_read(opener): return with_as(opener(), lambda f: f.read())
def text_write(filename, text): with_as(open(filename, 'w'), lambda f: f.write(text))
def json_write(filename, x): text_write(filename, json.dumps(x, sort_keys=True, indent=2))
json_read = compose(json.loads, text_read, file_opener)

def csv_read(csv_file):
    import csv
    return with_as(file_opener(csv_file)(), compose(list, csv.reader))

def lazy(f):
    cell = [None]
    def g():
        if cell[0] is None:
            cell[0] = f()
        return cell[0]
    return g

@delay
def broken(f, *args, **kwargs):
    breakpoint()
    return f(*args, **kwargs)
