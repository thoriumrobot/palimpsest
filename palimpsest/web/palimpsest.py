#!/usr/bin/env python3
"""Palimpsest in Python: a faithful port of the Rust reference interpreter.

This module is the engine behind ``index.html``, which runs it in the browser
under Pyodide. It mirrors ``src/*.rs`` function by function -- reader and
printer (term.rs), exact numbers (num.rs), matching and substitution
(matcher.rs), strategies, primitives, strict variables, the normal-form memo
and the trace (strategy.rs), the program loader (program.rs), the
capability-checked transactional writer and ledger (safety.rs) and the command
driver (main.rs) -- so that a program prints the same output, fuel counts
included, under both interpreters. ``web/test_parity.py`` checks this against
the Rust binary on the repository's programs.

It also runs from the command line with the same flags as the Rust binary:

    python3 web/palimpsest.py examples/quine.pal --dry-run
    python3 web/palimpsest.py undo examples/refactor.pal

Term representation (chosen for speed in CPython/Pyodide):
    symbol            -> Python ``str``
    string literal    -> ``Str`` (a wrapper, so a string never equals a symbol)
    integer           -> Python ``int`` (any size)
    non-integer exact -> ``fractions.Fraction`` (never integer-valued)
    list              -> Python ``tuple`` (immutable; identity is used by the memo)
"""
import os
import sys
from fractions import Fraction

__all__ = ["main", "run_cli", "read_term", "render", "PalError"]


class PalError(Exception):
    """A hard error: the Rust interpreter's `Err(String)`."""


# ============================================================== terms ===

class Str:
    """A string literal. Distinct from a symbol (a plain Python str)."""
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v

    def __eq__(self, o):
        return type(o) is Str and o.v == self.v

    def __ne__(self, o):
        return not (type(o) is Str and o.v == self.v)

    def __hash__(self):
        return hash(("\x00str", self.v))

    def __repr__(self):
        return "Str(%r)" % self.v


TRUE = "true"
FALSE = "false"
I64_MIN = -(1 << 63)
I64_MAX = (1 << 63) - 1


def boolsym(b):
    return TRUE if b else FALSE


def is_num(t):
    tt = type(t)
    return tt is int or tt is Fraction


def from_rat(q):
    """Canonical numeric term: integer-valued rationals are ints."""
    if type(q) is Fraction and q.denominator == 1:
        return q.numerator
    return q


def fmt_num(t):
    if type(t) is int:
        return str(t)
    return "%d/%d" % (t.numerator, t.denominator)


def _render_str(s):
    out = ['"']
    for c in s:
        if c == '"':
            out.append('\\"')
        elif c == "\\":
            out.append("\\\\")
        elif c == "\n":
            out.append("\\n")
        else:
            out.append(c)
    out.append('"')
    return "".join(out)


def render(t):
    """Canonical printer (the inverse of read_term)."""
    tt = type(t)
    if tt is str:
        return t
    if tt is tuple:
        return "(" + " ".join([render(x) for x in t]) + ")"
    if tt is int:
        return str(t)
    if tt is Str:
        return _render_str(t.v)
    if tt is Fraction:
        return fmt_num(t)
    return str(t)


def _is_digits(s):
    return s != "" and all("0" <= c <= "9" for c in s)


def _is_int_lit(s):
    d = s[1:] if s.startswith("-") else s
    return _is_digits(d)


def parse_num(a):
    """An i64 (Rust accepts a leading '+'), a big integer, or n/d."""
    body = a[1:] if a[:1] in ("+", "-") else a
    if _is_digits(body):
        n = int(a)
        if I64_MIN <= n <= I64_MAX:
            return n
    if "/" in a:
        n, d = a.split("/", 1)
        if _is_int_lit(n) and _is_digits(d):
            dd = int(d)
            if dd == 0:
                return None
            return from_rat(Fraction(int(n), dd))
        return None
    if _is_int_lit(a):
        return int(a)
    return None


_OPEN, _CLOSE = 0, 1


def _lex(inp):
    toks = []
    i, n = 0, len(inp)
    while i < n:
        c = inp[i]
        if c == "(":
            toks.append((_OPEN, None))
            i += 1
        elif c == ")":
            toks.append((_CLOSE, None))
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            i += 1
            buf = []
            while True:
                if i >= n:
                    raise PalError("unterminated string literal")
                ch = inp[i]
                i += 1
                if ch == "\\":
                    if i >= n:
                        raise PalError("unterminated escape in string")
                    e = inp[i]
                    i += 1
                    buf.append("\n" if e == "n" else e)
                elif ch == '"':
                    break
                else:
                    buf.append(ch)
            toks.append((2, "".join(buf)))
        else:
            j = i
            while j < n:
                ch = inp[j]
                if ch.isspace() or ch == "(" or ch == ")" or ch == '"':
                    break
                j += 1
            toks.append((3, inp[i:j]))
            i = j
    return toks


def read_term(inp):
    """Read exactly one term from a string (must consume all of it)."""
    toks = _lex(inp)
    pos = 0
    stack = []
    result = None
    have = False
    while True:
        if pos >= len(toks):
            if stack:
                raise PalError("unterminated list")
            raise PalError("unexpected end of input while reading term")
        kind, val = toks[pos]
        pos += 1
        if kind == _OPEN:
            stack.append([])
            continue
        if kind == _CLOSE:
            if not stack:
                raise PalError("unexpected ')'")
            t = tuple(stack.pop())
        elif kind == 2:
            t = Str(val)
        else:
            t = parse_num(val)
            if t is None:
                t = val
        if stack:
            stack[-1].append(t)
        else:
            result = t
            have = True
            break
    if pos != len(toks):
        raise PalError("trailing tokens after term (read up to position %d/%d)" % (pos, len(toks)))
    assert have
    return result


def as_term_var(t):
    if type(t) is str and t.startswith("?") and not t.endswith("..."):
        return t[1:]
    return None


def as_seq_var(t):
    if type(t) is str and t.startswith("?") and t.endswith("...") and len(t) > 4:
        return t[1:-3]
    return None


def as_strict_var(t):
    if type(t) is str and t.startswith("!") and len(t) > 1 and not t.endswith("..."):
        return t[1:]
    return None


# ============================================================ numbers ===

def _q(t):
    return t if type(t) is Fraction else Fraction(t)


def num_add(a, b):
    ta, tb = type(a), type(b)
    if ta is int and tb is int:
        return a + b
    if (ta is int or ta is Fraction) and (tb is int or tb is Fraction):
        return from_rat(_q(a) + _q(b))
    return None


def num_sub(a, b):
    ta, tb = type(a), type(b)
    if ta is int and tb is int:
        return a - b
    if (ta is int or ta is Fraction) and (tb is int or tb is Fraction):
        return from_rat(_q(a) - _q(b))
    return None


def num_mul(a, b):
    ta, tb = type(a), type(b)
    if ta is int and tb is int:
        return a * b
    if (ta is int or ta is Fraction) and (tb is int or tb is Fraction):
        return from_rat(_q(a) * _q(b))
    return None


def num_cmp(a, b):
    """-1/0/1, or None if either is not a number."""
    if not (is_num(a) and is_num(b)):
        return None
    return (a > b) - (a < b)


def num_idiv(a, b):
    if type(a) is not int or type(b) is not int or b == 0:
        return None
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def num_imod(a, b):
    if type(a) is not int or type(b) is not int or b == 0:
        return None
    return a % abs(b)


def num_qdiv(a, b):
    if not (is_num(a) and is_num(b)) or b == 0:
        return None
    return from_rat(_q(a) / _q(b))


def num_abs(a):
    return abs(a) if is_num(a) else None


def num_numer(a):
    if not is_num(a):
        return None
    return a if type(a) is int else a.numerator


def num_denom(a):
    if not is_num(a):
        return None
    return 1 if type(a) is int else a.denominator


def num_floor(a):
    if not is_num(a):
        return None
    return a if type(a) is int else a.numerator // a.denominator


def num_ceil(a):
    if not is_num(a):
        return None
    return a if type(a) is int else -((-a.numerator) // a.denominator)


def num_round_to(a, k):
    if not is_num(a) or type(k) is not int or k <= 0:
        return None
    x = _q(a) * k + Fraction(1, 2)
    n = x.numerator // x.denominator
    return from_rat(Fraction(n, k))


def num_expt(a, k):
    if not is_num(a) or type(k) is not int:
        return None
    if k < I64_MIN or k > I64_MAX or abs(k) > 100000:
        return None
    if k < 0 and a == 0:
        return None
    return from_rat(_q(a) ** k)


def num_isqrt(a):
    if type(a) is not int or a < 0:
        return None
    import math
    return math.isqrt(a)


def num_dec(a, d):
    if not is_num(a) or type(d) is not int or d < 0 or d > 60:
        return None
    x = _q(a)
    scale = 10 ** d
    neg = x < 0
    ax = abs(x) * scale + Fraction(1, 2)
    n = ax.numerator // ax.denominator
    ip, fp = divmod(n, scale)
    s = "-" if (neg and n != 0) else ""
    s += str(ip)
    if d > 0:
        f = str(fp)
        s += "." + "0" * (d - len(f)) + f
    return Str(s)


# ===================================================== patterns/matcher ===

class PVar:
    __slots__ = ("name",)

    def __init__(self, name):
        self.name = name


class PSeq:
    __slots__ = ("name",)

    def __init__(self, name):
        self.name = name


class Verb:
    """`(verbatim X)` on a right-hand side: X, unsubstituted."""
    __slots__ = ("term",)

    def __init__(self, term):
        self.term = term


class SeqB:
    """A sequence-variable binding."""
    __slots__ = ("items",)

    def __init__(self, items):
        self.items = items


_MISSING = object()


def compile_pat(t, strict=False):
    """Pattern term -> compiled pattern (variables become PVar/PSeq)."""
    tt = type(t)
    if tt is str:
        if t.startswith("?"):
            if t.endswith("..."):
                if len(t) > 4:
                    return PSeq(t[1:-3])
                return t
            return PVar(t[1:])
        return t
    if tt is tuple:
        return tuple([compile_pat(x) for x in t])
    return t


def compile_rhs(t):
    """Right-hand side / where expression -> compiled template."""
    tt = type(t)
    if tt is str:
        if t.startswith("?"):
            if t.endswith("..."):
                if len(t) > 4:
                    return PSeq(t[1:-3])
                return t
            return PVar(t[1:])
        return t
    if tt is tuple:
        if len(t) == 2 and t[0] == "verbatim" and type(t[0]) is str:
            return Verb(t[1])
        return tuple([compile_rhs(x) for x in t])
    return t


def match_term(p, s, b):
    """First-order matching of a compiled pattern; mutates and returns b."""
    tp = type(p)
    if tp is PVar:
        prev = b.get(p.name, _MISSING)
        if prev is _MISSING:
            b[p.name] = s
            return b
        if type(prev) is SeqB:
            return None
        return b if prev == s else None
    if tp is tuple:
        if type(s) is not tuple:
            return None
        return _match_seq(p, 0, s, 0, b)
    if tp is PSeq:
        return None
    if tp is type(s) and p == s:
        return b
    return None


def _match_seq(ps, i, ss, j, b):
    np_, ns = len(ps), len(ss)
    while True:
        if i == np_:
            return b if j == ns else None
        h = ps[i]
        th = type(h)
        if th is PSeq:
            prev = b.get(h.name, _MISSING)
            if prev is not _MISSING:
                if type(prev) is not SeqB:
                    return None
                v = prev.items
                k = len(v)
                if ns - j >= k and ss[j:j + k] == v:
                    i += 1
                    j += k
                    continue
                return None
            name = h.name
            for k in range(j, ns + 1):
                b2 = dict(b)
                b2[name] = SeqB(ss[j:k])
                r = _match_seq(ps, i + 1, ss, k, b2)
                if r is not None:
                    return r
            return None
        if j == ns:
            return None
        if th is PVar:
            prev = b.get(h.name, _MISSING)
            if prev is _MISSING:
                b[h.name] = ss[j]
            elif type(prev) is SeqB or prev != ss[j]:
                return None
        elif th is tuple:
            s = ss[j]
            if type(s) is not tuple:
                return None
            b = _match_seq(h, 0, s, 0, b)
            if b is None:
                return None
        else:
            s = ss[j]
            if th is not type(s) or h != s:
                return None
        i += 1
        j += 1


def match_k(p, s, b, k):
    """Matching with a continuation (guards drive backtracking)."""
    tp = type(p)
    if tp is PVar:
        prev = b.get(p.name, _MISSING)
        if prev is _MISSING:
            b[p.name] = s
            return k(b)
        if type(prev) is SeqB:
            return None
        return k(b) if prev == s else None
    if tp is tuple:
        if type(s) is not tuple:
            return None
        return _match_seq_k(p, 0, s, 0, b, k)
    if tp is PSeq:
        return None
    if tp is type(s) and p == s:
        return k(b)
    return None


def _match_seq_k(ps, i, ss, j, b, k):
    np_, ns = len(ps), len(ss)
    if i == np_:
        return k(b) if j == ns else None
    h = ps[i]
    if type(h) is PSeq:
        prev = b.get(h.name, _MISSING)
        if prev is not _MISSING:
            if type(prev) is not SeqB:
                return None
            v = prev.items
            n = len(v)
            if ns - j >= n and ss[j:j + n] == v:
                return _match_seq_k(ps, i + 1, ss, j + n, b, k)
            return None
        name = h.name
        for split in range(j, ns + 1):
            b2 = dict(b)
            b2[name] = SeqB(ss[j:split])
            r = _match_seq_k(ps, i + 1, ss, split, b2, k)
            if r is not None:
                return r
        return None
    if j == ns:
        return None
    return match_k(h, ss[j], b, lambda b2: _match_seq_k(ps, i + 1, ss, j + 1, b2, k))


def subst(t, b):
    """Instantiate a compiled right-hand side under bindings b."""
    tt = type(t)
    if tt is tuple:
        out = []
        for el in t:
            te = type(el)
            if te is PSeq:
                v = b.get(el.name, _MISSING)
                if v is _MISSING:
                    raise PalError("unbound sequence variable ?%s..." % el.name)
                if type(v) is not SeqB:
                    raise PalError("?%s... bound to a single term, expected a sequence" % el.name)
                out.extend(v.items)
            elif te is PVar:
                v = b.get(el.name, _MISSING)
                if v is _MISSING:
                    raise PalError("unbound variable ?%s" % el.name)
                if type(v) is SeqB:
                    raise PalError("sequence variable ?%s... used in term position" % el.name)
                out.append(v)
            elif te is tuple or te is Verb:
                out.append(subst(el, b))
            else:
                out.append(el)
        return tuple(out)
    if tt is PVar:
        v = b.get(t.name, _MISSING)
        if v is _MISSING:
            raise PalError("unbound variable ?%s" % t.name)
        if type(v) is SeqB:
            raise PalError("sequence variable ?%s... used in term position" % t.name)
        return v
    if tt is Verb:
        return t.term
    if tt is PSeq:
        raise PalError("sequence variable ?%s... used outside a list" % t.name)
    return t


# ========================================================= strategies ===

ID, FAIL, ALLRULES, REF, CALL, PRIM, SEQ, CHOICE, TRY, REPEAT, TOPDOWN, \
    BOTTOMUP, INNERMOST, ONCETD, ONCEBU, FIXPOINT, ALL = range(17)

_S_ID = (ID,)
_S_FAIL = (FAIL,)
_S_ALLRULES = (ALLRULES,)
_S_PRIM = (PRIM,)
STD_INNER = (CHOICE, _S_PRIM, _S_ALLRULES)


def is_std_inner(s):
    return s[0] == CHOICE and s[1][0] == PRIM and s[2][0] == ALLRULES


_COMBINATORS = {"try": TRY, "repeat": REPEAT, "topdown": TOPDOWN, "bottomup": BOTTOMUP,
                "innermost": INNERMOST, "oncetd": ONCETD, "oncebu": ONCEBU,
                "outermost": "outermost", "fixpoint": FIXPOINT, "all": ALL}


def _lex_strat(inp):
    out = []
    i, n = 0, len(inp)
    while i < n:
        c = inp[i]
        if c in "();+,":
            out.append(c)
            i += 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < n and not inp[j].isspace() and inp[j] not in "();+,":
                j += 1
            out.append(("id", inp[i:j]))
            i = j
    return out


def _tokname(t):
    names = {"(": "LParen", ")": "RParen", ";": "Semi", "+": "Plus", ",": "Comma"}
    if type(t) is tuple:
        return 'Ident("%s")' % t[1]
    return names[t]


def parse_strategy(inp):
    toks = _lex_strat(inp)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def expect(t):
        if peek() == t:
            pos[0] += 1
        else:
            raise PalError("expected %s in strategy" % _tokname(t))

    def p_seq():
        left = p_choice()
        while peek() == ";":
            pos[0] += 1
            left = (SEQ, left, p_choice())
        return left

    def p_choice():
        left = p_atom()
        while peek() == "+":
            pos[0] += 1
            left = (CHOICE, left, p_atom())
        return left

    def p_atom():
        t = peek()
        if t is None:
            raise PalError("unexpected end of strategy")
        if t == "(":
            pos[0] += 1
            inner = p_seq()
            expect(")")
            return inner
        if type(t) is tuple:
            name = t[1]
            pos[0] += 1
            if peek() == "(":
                pos[0] += 1
                args = [p_seq()]
                while peek() == ",":
                    pos[0] += 1
                    args.append(p_seq())
                expect(")")
                if name in _COMBINATORS:
                    if len(args) != 1:
                        raise PalError("combinator '%s' takes exactly 1 argument" % name)
                    tag = _COMBINATORS[name]
                    if tag == "outermost":
                        return (REPEAT, (ONCETD, args[0]))
                    return (tag, args[0])
                return (CALL, name, tuple(args))
            if name == "id":
                return _S_ID
            if name == "fail":
                return _S_FAIL
            if name == "rules":
                return _S_ALLRULES
            if name == "prim":
                return _S_PRIM
            return (REF, name)
        raise PalError("unexpected token in strategy: %s" % _tokname(t))

    s = p_seq()
    if pos[0] != len(toks):
        raise PalError("trailing tokens in strategy near '%s'" % " ".join(_tokname(x) for x in toks[pos[0]:]))
    return s


class Rule:
    __slots__ = ("name", "lhs_term", "lhs", "lhs_forced", "strict", "arity", "rhs",
                 "conds", "head", "fixed_len")

    def __init__(self, name, lhs, rhs, conds):
        self.name = name
        self.lhs_term = lhs
        self.lhs = compile_pat(lhs)
        self.rhs = compile_rhs(rhs)
        # where clauses: (var or None, compiled expr)
        self.conds = [(v, compile_rhs(e)) for (v, e) in conds]
        self.strict = None
        self.lhs_forced = None
        self.arity = -1
        if type(lhs) is tuple:
            mask = [as_strict_var(p) is not None for p in lhs]
            has_seq = any(as_seq_var(p) is not None for p in lhs)
            if any(mask) and not has_seq:
                self.strict = tuple(mask)
                self.arity = len(lhs)
                self.lhs_forced = tuple(
                    PVar(lhs[i][1:]) if mask[i] else compile_pat(lhs[i]) for i in range(len(lhs)))
        self.head = head_key(lhs)
        # A list pattern without a top-level sequence variable only matches
        # (and only forces strict arguments of) subjects of the same length.
        self.fixed_len = -1
        if type(lhs) is tuple and not any(as_seq_var(p) is not None for p in lhs):
            self.fixed_len = len(lhs)


def head_key(t):
    if type(t) is str:
        return None if t.startswith("?") else t
    if type(t) is tuple and t and type(t[0]) is str and not t[0].startswith("?"):
        return t[0]
    return None


def _clip(s, n):
    return s if len(s) <= n else s[:n] + "..."


def is_record(t):
    if type(t) is not tuple or not t or t[0] != "rec" or type(t[0]) is not str:
        return False
    for e in t[1:]:
        if type(e) is not tuple or len(e) != 2 or type(e[0]) is not str:
            return False
    return True


MEMO_CAP = 1 << 21
NF_CAP = 1 << 14


class Engine:
    def __init__(self, out):
        self.out = out
        self.rules = []
        self.rule_index = {}
        self.strategies = {}
        self.by_head = {}
        self.wild = []
        self._cands = {}
        self.stats = None
        self.trace_limit = None
        self.trace_count = 0
        self.cond_level = 0
        self.memo = False
        self.known = {}
        self.nf = {}
        self.hits = 0
        self.nf_hits = 0
        self.fuel = 0
        self.std_eval = (REPEAT, (ONCETD, STD_INNER))

    # -- configuration --------------------------------------------------
    def enable_memo(self):
        self.memo = True
        self.known = {}
        self.nf = {}
        self.hits = 0
        self.nf_hits = 0

    def enable_stats(self):
        self.stats = {}

    def enable_trace(self, limit):
        self.trace_limit = limit
        self.trace_count = 0

    def add_rule(self, r):
        idx = len(self.rules)
        self.rule_index[r.name] = idx
        if r.head is not None:
            self.by_head.setdefault(r.head, []).append(idx)
        else:
            self.wild.append(idx)
        self.rules.append(r)
        self._cands = {}

    def add_transition(self, r):
        idx = len(self.rules)
        self.rule_index[r.name] = idx
        self.rules.append(r)

    def candidates(self, head):
        c = self._cands.get(head)
        if c is None:
            pinned = self.by_head.get(head, []) if head is not None else []
            c = tuple(self.rules[i] for i in sorted(set(pinned) | set(self.wild)))
            self._cands[head] = c
        return c

    # -- bookkeeping ----------------------------------------------------
    def _spend(self, name, before, after):
        if self.fuel == 0:
            raise PalError("out of fuel (rewrite step budget exhausted)")
        self.fuel -= 1
        if self.stats is not None:
            self.stats[name] = self.stats.get(name, 0) + 1
        if self.trace_limit is not None and self.trace_count < self.trace_limit:
            self.trace_count += 1
            ind = "  " * min(self.cond_level, 12)
            self.out("  %5d %s%s: %s  =>  %s\n" % (
                self.trace_count, ind, name, _clip(render(before), 150), _clip(render(after), 150)))

    def _memo_known(self, t):
        if type(t) is tuple and id(t) in self.known:
            self.hits += 1
            return True
        return False

    def _memo_insert(self, t):
        if len(self.known) >= MEMO_CAP:
            self.known.clear()
        self.known[id(t)] = t

    # -- rule application -----------------------------------------------
    def apply_rule(self, r, t):
        fl = r.fixed_len
        if fl >= 0 and (type(t) is not tuple or len(t) != fl):
            return None
        lhs = r.lhs
        subject = t
        if r.strict is not None and type(t) is tuple and len(t) == r.arity:
            lhs = r.lhs_forced
            mask = r.strict
            subject = tuple([self.force_strict(t[i]) if mask[i] else t[i] for i in range(r.arity)])
        if not r.conds:
            b = match_term(lhs, subject, {})
            if b is None:
                return None
            if self.fuel == 0:
                raise PalError("out of fuel (rewrite step budget exhausted)")
            out = subst(r.rhs, b)
            self._spend(r.name, subject, out)
            return out
        conds = r.conds
        b = match_k(lhs, subject, {}, lambda b: self.check_conds(conds, b))
        if b is None:
            return None
        if self.fuel == 0:
            raise PalError("out of fuel (rewrite step budget exhausted)")
        out = subst(r.rhs, b)
        self._spend(r.name, subject, out)
        return out

    def check_conds(self, conds, b):
        for v, expr in conds:
            e = subst(expr, b)
            nf = self.eval_cond(e)
            if v is not None:
                b[v] = nf
            elif nf != TRUE or type(nf) is not str:
                return None
        return b

    def eval_cond(self, t):
        if self.memo and self._memo_known(t):
            return t
        self.cond_level += 1
        try:
            r = self.normalize(t)
        finally:
            self.cond_level -= 1
        return r

    def force_strict(self, t):
        if self.memo and type(t) is tuple:
            hit = self.nf.get(id(t))
            if hit is not None:
                self.nf_hits += 1
                return hit[1]
        v = self.eval_cond(t)
        if self.memo and type(t) is tuple:
            if not (type(v) is tuple and v is t):
                if len(self.nf) >= NF_CAP:
                    self.nf.clear()
                self.nf[id(t)] = (t, v)
        return v

    # -- the standard evaluator: repeat(oncetd(prim + rules)) ------------
    def normalize(self, t):
        once = self.once_std
        while True:
            n = once(t)
            if n is None:
                return t
            t = n

    def root_std(self, t):
        """`prim + rules` at the root."""
        if type(t) is tuple:
            h = t[0] if t else None
            if type(h) is str:
                if h in PRIM_OPS:
                    v = eval_prim(t)
                    if v is not None:
                        self._spend("<prim>", t, v)
                        return v
                cands = self._cands.get(h)
                if cands is None:
                    cands = self.candidates(h)
            else:
                cands = self.candidates(None)
        elif type(t) is str:
            cands = self._cands.get(t)
            if cands is None:
                cands = self.candidates(t)
        else:
            cands = self.candidates(None)
        ar = self.apply_rule
        for r in cands:
            t2 = ar(r, t)
            if t2 is not None:
                return t2
        return None

    def _atom_inert(self, x):
        """True when no rule can fire on atom x (primitives never fire on atoms)."""
        if self.wild:
            return False
        return type(x) is not str or x not in self.by_head

    def once_std(self, t):
        """oncetd(prim + rules), with the normal-form memo when enabled."""
        if type(t) is not tuple:
            if self._atom_inert(t):
                return None
            return self.root_std(t)
        memo = self.memo
        if memo and id(t) in self.known:
            self.hits += 1
            return None
        r = self.root_std(t)
        if r is not None:
            return r
        once = self.once_std
        nowild = not self.wild
        by_head = self.by_head
        if t and t[0] == "rec" and type(t[0]) is str and is_record(t):
            for i in range(1, len(t)):
                kv = t[i]
                x = kv[1]
                if type(x) is not tuple and nowild and (type(x) is not str or x not in by_head):
                    continue
                v2 = once(x)
                if v2 is not None:
                    return t[:i] + ((kv[0], v2),) + t[i + 1:]
        else:
            i = 0
            for x in t:
                if type(x) is tuple or not nowild or (type(x) is str and x in by_head):
                    ci = once(x)
                    if ci is not None:
                        return t[:i] + (ci,) + t[i + 1:]
                i += 1
        if memo:
            self._memo_insert(t)
        return None

    # -- general strategies ----------------------------------------------
    def apply(self, s, t):
        return self.apply_d(s, t, None)

    def apply_d(self, s, t, env):
        tag = s[0]
        if tag == REPEAT:
            a = s[1]
            if a[0] == ONCETD and is_std_inner(a[1]):
                return self.normalize(t)
            cur = t
            while True:
                n = self.apply_d(a, cur, env)
                if n is None:
                    return cur
                cur = n
        if tag == CHOICE:
            if s[1][0] == PRIM and s[2][0] == ALLRULES:
                return self.root_std(t)
            r = self.apply_d(s[1], t, env)
            if r is not None:
                return r
            return self.apply_d(s[2], t, env)
        if tag == ONCETD:
            if is_std_inner(s[1]):
                return self.once_std(t)
            return self.once(s[1], t, True, env)
        if tag == ALLRULES:
            return self.root_rules(t)
        if tag == PRIM:
            v = eval_prim(t)
            if v is None:
                return None
            self._spend("<prim>", t, v)
            return v
        if tag == ID:
            return t
        if tag == FAIL:
            return None
        if tag == REF:
            name = s[1]
            e = env
            while e is not None:
                if e[0] == name:
                    body, cenv = e[1]
                    return self.apply_d(body, t, cenv)
                e = e[2]
            i = self.rule_index.get(name)
            if i is not None:
                return self.apply_rule(self.rules[i], t)
            d = self.strategies.get(name)
            if d is not None:
                params, body = d
                if params:
                    raise PalError("strategy '%s' expects %d argument(s)" % (name, len(params)))
                return self.apply_d(body, t, None)
            raise PalError("unknown rule or strategy '%s'" % name)
        if tag == CALL:
            name, args = s[1], s[2]
            d = self.strategies.get(name)
            if d is None:
                raise PalError("unknown strategy '%s'" % name)
            params, body = d
            if len(params) != len(args):
                raise PalError("strategy '%s' expects %d argument(s), got %d" % (name, len(params), len(args)))
            new_env = None
            for p, a in zip(params, args):
                new_env = (p, (a, env), new_env)
            return self.apply_d(body, t, new_env)
        if tag == SEQ:
            t1 = self.apply_d(s[1], t, env)
            if t1 is None:
                return None
            return self.apply_d(s[2], t1, env)
        if tag == TRY:
            r = self.apply_d(s[1], t, env)
            return t if r is None else r
        if tag == ALL:
            return self.all_apply(s[1], t, env)
        if tag == TOPDOWN:
            t1 = self.apply_d(s[1], t, env)
            if t1 is None:
                return None
            return self.all_apply(s, t1, env)
        if tag == BOTTOMUP:
            t1 = self.all_apply(s, t, env)
            if t1 is None:
                return None
            return self.apply_d(s[1], t1, env)
        if tag == INNERMOST:
            return self.innermost(s[1], t, env)
        if tag == ONCEBU:
            return self.once(s[1], t, False, env)
        if tag == FIXPOINT:
            cur = t
            while True:
                n = self.apply_d(s[1], cur, env)
                if n is None:
                    return cur
                if n == cur:
                    return cur
                cur = n
        raise PalError("bad strategy")

    def root_rules(self, t):
        tt = type(t)
        if tt is tuple:
            h = t[0] if t and type(t[0]) is str and not t[0].startswith("?") else None
        elif tt is str:
            h = None if t.startswith("?") else t
        else:
            h = None
        for r in self.candidates(h):
            t2 = self.apply_rule(r, t)
            if t2 is not None:
                return t2
        return None

    def all_apply(self, s, t, env):
        if type(t) is tuple:
            out = []
            for x in t:
                x2 = self.apply_d(s, x, env)
                if x2 is None:
                    return None
                out.append(x2)
            return tuple(out)
        return t

    def once(self, s, t, td, env):
        memo = td and self.memo and type(t) is tuple and is_std_inner(s)
        if memo and self._memo_known(t):
            return None
        if td:
            t2 = self.apply_d(s, t, env)
            if t2 is not None:
                return t2
        if is_record(t):
            for i in range(1, len(t)):
                kv = t[i]
                v2 = self.once(s, kv[1], td, env)
                if v2 is not None:
                    return t[:i] + ((kv[0], v2),) + t[i + 1:]
        elif type(t) is tuple:
            for i in range(len(t)):
                ci = self.once(s, t[i], td, env)
                if ci is not None:
                    return t[:i] + (ci,) + t[i + 1:]
        if not td:
            t2 = self.apply_d(s, t, env)
            if t2 is not None:
                return t2
        if memo:
            self._memo_insert(t)
        return None

    def innermost(self, s, t, env):
        while True:
            if type(t) is tuple:
                if is_record(t):
                    out = [t[0]]
                    for e in t[1:]:
                        out.append((e[0], self.innermost(s, e[1], env)))
                    t1 = tuple(out)
                else:
                    t1 = tuple([self.innermost(s, x, env) for x in t])
            else:
                t1 = t
            t2 = self.apply_d(s, t1, env)
            if t2 is None:
                return t1
            t = t2


# ========================================================= primitives ===

def _rng(n):
    m = (1 << 64) - 1
    z = ((n & m) + 0x9E3779B97F4A7C15) & m
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & m
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & m
    z ^= z >> 31
    return z >> 1


def _p_str(a):
    ta = type(a)
    if ta is str:
        return Str(a)
    if ta is int or ta is Fraction:
        return Str(fmt_num(a))
    if ta is Str:
        return Str(a.v)
    return None


def _p_explode(a):
    if type(a) is Str:
        return ("list",) + tuple(Str(c) for c in a.v)
    return None


def _p_implode(a):
    if type(a) is tuple and a and a[0] == "list" and type(a[0]) is str:
        parts = []
        for it in a[1:]:
            if type(it) is not Str:
                return None
            parts.append(it.v)
        return Str("".join(parts))
    return None


def _p_rng(a):
    if type(a) is int and I64_MIN <= a <= I64_MAX:
        return _rng(a)
    return None


_UNARY = {
    "str": _p_str,
    "sym": lambda a: a.v if type(a) is Str else None,
    "explode": _p_explode,
    "implode": _p_implode,
    "abs": num_abs,
    "num": num_numer,
    "den": num_denom,
    "floor": num_floor,
    "ceil": num_ceil,
    "isqrt": num_isqrt,
    "number?": lambda a: None if type(a) is tuple else boolsym(is_num(a)),
    "rng": _p_rng,
}


def _p_lt(a, b):
    c = num_cmp(a, b)
    return None if c is None else boolsym(c < 0)


def _p_le(a, b):
    c = num_cmp(a, b)
    return None if c is None else boolsym(c <= 0)


def _p_gt(a, b):
    c = num_cmp(a, b)
    return None if c is None else boolsym(c > 0)


def _p_ge(a, b):
    c = num_cmp(a, b)
    return None if c is None else boolsym(c >= 0)


def _both_prim(a, b):
    ta, tb = type(a), type(b)
    if (ta is Str and tb is Str) or (ta is str and tb is str):
        return True
    return is_num(a) and is_num(b)


def _p_eq(a, b):
    if not _both_prim(a, b):
        return None
    return boolsym(a == b)


def _p_ne(a, b):
    if not _both_prim(a, b):
        return None
    return boolsym(a != b)


def _p_cat(a, b):
    if type(a) is Str and type(b) is Str:
        return Str(a.v + b.v)
    return None


def _p_strlt(a, b):
    if type(a) is Str and type(b) is Str:
        return boolsym(a.v < b.v)
    return None


def _p_min(a, b):
    c = num_cmp(a, b)
    if c is None:
        return None
    return b if c > 0 else a


def _p_max(a, b):
    c = num_cmp(a, b)
    if c is None:
        return None
    return b if c < 0 else a


def _pad(left):
    def f(a, b):
        if type(a) is Str and type(b) is int and I64_MIN <= b <= I64_MAX:
            w = max(b, 0)
            s = a.v
            if len(s) >= w:
                return Str(s)
            pad = " " * (w - len(s))
            return Str(pad + s if left else s + pad)
        return None
    return f


def _p_matches(a, b):
    return boolsym(match_term(compile_pat(a), b, {}) is not None)


def _p_witness(a, b):
    bs = match_term(compile_pat(a), b, {})
    if bs is None:
        return "none"
    entries = ["dict"]
    for name in sorted(bs.keys()):
        v = bs[name]
        if type(v) is SeqB:
            v = ("list",) + tuple(v.items)
        entries.append(("entry", name, v))
    return ("some", tuple(entries))


_BINARY = {
    "+": num_add, "-": num_sub, "*": num_mul, "/": num_idiv, "mod": num_imod,
    "q/": num_qdiv, "round-to": num_round_to, "expt": num_expt, "decimal": num_dec,
    "<": _p_lt, "<=": _p_le, ">": _p_gt, ">=": _p_ge, "=": _p_eq, "<>": _p_ne,
    "cat": _p_cat, "matches?": _p_matches, "match-witness": _p_witness, "str<": _p_strlt,
    "min": _p_min, "max": _p_max, "padl": _pad(True), "padr": _pad(False),
}

_RECORD_OPS = frozenset(["@", "set@", "add@", "has@", "put@", "del@", "keys@", "sum@"])
PRIM_OPS = frozenset(_RECORD_OPS | set(_UNARY) | set(_BINARY))


def eval_prim(t):
    if type(t) is not tuple or not t:
        return None
    op = t[0]
    if type(op) is not str:
        return None
    n = len(t)
    if op in _RECORD_OPS:
        return eval_record_prim(op, t[1:])
    if n == 2:
        f = _UNARY.get(op)
        return f(t[1]) if f is not None else None
    if n == 3:
        f = _BINARY.get(op)
        return f(t[1], t[2]) if f is not None else None
    return None


def _rec_entries(r):
    if type(r) is tuple and r and type(r[0]) is str and r[0] == "rec":
        return r[1:]
    return None


def _rec_find(r, key):
    es = _rec_entries(r)
    if es is None or type(key) is not str:
        return None
    for i, e in enumerate(es):
        if type(e) is tuple and len(e) == 2 and type(e[0]) is str and e[0] == key:
            return i + 1
    return None


def _rec_get(r, path):
    cur = r
    for k in path:
        i = _rec_find(cur, k)
        if i is None:
            return None
        kv = cur[i]
        if type(kv) is not tuple:
            return None
        cur = kv[1]
    return cur


def _rec_update(r, path, f):
    if not path:
        return f(r)
    i = _rec_find(r, path[0])
    if i is None:
        return None
    kv = r[i]
    if type(kv) is not tuple:
        return None
    nv = _rec_update(kv[1], path[1:], f)
    if nv is None:
        return None
    return r[:i] + ((kv[0], nv),) + r[i + 1:]


def eval_record_prim(op, args):
    n = len(args)
    if op == "@":
        if n < 2:
            return None
        return _rec_get(args[0], args[1:])
    if op == "has@":
        if n != 2 or _rec_entries(args[0]) is None:
            return None
        return boolsym(_rec_find(args[0], args[1]) is not None)
    if op == "set@":
        if n < 3:
            return None
        v = args[-1]
        return _rec_update(args[0], args[1:-1], lambda _old: v)
    if op == "add@":
        if n < 3:
            return None
        d = args[-1]
        if not is_num(d):
            return None
        return _rec_update(args[0], args[1:-1], lambda old: num_add(old, d))
    if op == "put@":
        if n != 3 or type(args[1]) is not str or _rec_entries(args[0]) is None:
            return None
        entry = (args[1], args[2])
        i = _rec_find(args[0], args[1])
        r = args[0]
        if i is not None:
            return r[:i] + (entry,) + r[i + 1:]
        return r + (entry,)
    if op == "del@":
        if n != 2 or _rec_entries(args[0]) is None:
            return None
        i = _rec_find(args[0], args[1])
        r = args[0]
        if i is not None:
            return r[:i] + r[i + 1:]
        return tuple(r)
    if op == "keys@":
        if n != 1:
            return None
        es = _rec_entries(args[0])
        if es is None:
            return None
        out = ["list"]
        for e in es:
            if type(e) is tuple and len(e) == 2:
                out.append(e[0])
            else:
                return None
        return tuple(out)
    if op == "sum@":
        if n != 1:
            return None
        es = _rec_entries(args[0])
        if es is None:
            return None
        tot = 0
        for e in es:
            if type(e) is tuple and len(e) == 2 and is_num(e[1]):
                tot = num_add(tot, e[1])
            else:
                return None
        return tot
    return None


# ============================================================ program ===

def rust_lines(text):
    """str::lines(): split on \\n, drop one trailing empty line, strip \\r."""
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return [p[:-1] if p.endswith("\r") else p for p in parts]


def _starts_continuation(line):
    return (line.startswith("where") or line.startswith("+") or line.startswith(";")
            or line.startswith(",") or line.startswith("=>"))


def _paren_depth(s):
    depth = 0
    in_str = esc = False
    for c in s:
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
    return depth


def _is_complete(s):
    if _paren_depth(s) != 0:
        return False
    t = s.rstrip()
    for tok in ("=>", "<-", "+", ";", ",", ":", "("):
        if t.endswith(tok):
            return False
    if t.endswith("=") or t.endswith(" where"):
        return False
    return True


def logical_items(text):
    items = []
    acc = ""
    start = 0
    for idx, raw in enumerate(rust_lines(text)):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if acc and not _starts_continuation(line) and _is_complete(acc):
            items.append((start, acc))
            acc = ""
        if not acc:
            start = idx
            acc = line
        else:
            acc = acc + " " + line
    if acc:
        items.append((start, acc))
    return items


def split_top_level_str(s, sep):
    depth = 0
    in_str = esc = False
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0 and s.startswith(sep, i):
            return s[:i], s[i + len(sep):]
        i += 1
    return None


def split_top_level_commas(s):
    parts = []
    rest = s
    while True:
        r = split_top_level_str(rest, ",")
        if r is None:
            break
        parts.append(r[0])
        rest = r[1]
    parts.append(rest)
    return parts


def parse_rule(rest):
    r = split_top_level_str(rest, ":")
    if r is None:
        raise PalError("rule missing ':' -> %s" % rest)
    name, body = r
    r = split_top_level_str(body, "=>")
    if r is None:
        raise PalError("rule missing '=>' -> %s" % rest)
    lhs_src, rhs_rest = r
    w = split_top_level_str(rhs_rest, " where ")
    if w is not None:
        rhs_src, conds = w[0], parse_where(w[1])
    else:
        rhs_src, conds = rhs_rest, []
    return Rule(name.strip(), read_term(lhs_src.strip()), read_term(rhs_src.strip()), conds)


def parse_where(src):
    out = []
    for clause in split_top_level_commas(src):
        clause = clause.strip()
        if not clause:
            continue
        r = split_top_level_str(clause, "<-")
        if r is not None:
            v = r[0].strip()
            if not v.startswith("?"):
                raise PalError("where-binding target must be a ?variable: %s" % v)
            out.append((v[1:], read_term(r[1].strip())))
        else:
            out.append((None, read_term(clause)))
    return out


def parse_strategy_header(h):
    lp = h.find("(")
    if lp >= 0:
        name = h[:lp].strip()
        rp = h.rfind(")")
        if rp < 0:
            raise PalError("strategy header missing ')'")
        params = [p.strip() for p in h[lp + 1:rp].split(",") if p.strip()]
        return name, params
    return h.strip(), []


class Cap:
    __slots__ = ("kind", "path")

    def __init__(self, kind, path=None):
        self.kind = kind
        self.path = path

    def debug(self):
        if self.kind == "self":
            return "Selff"
        return 'File("%s")' % self.path.replace("\\", "\\\\").replace('"', '\\"')


def parse_caps(s):
    inside = s.strip().lstrip("{").rstrip("}").strip()
    caps = []
    pos = inside.find("rewrite:")
    if pos >= 0:
        after = inside[pos + len("rewrite:"):]
        lb = after.find("[")
        if lb < 0:
            raise PalError("caps: expected '[' after rewrite:")
        rb = after.find("]")
        if rb < 0:
            raise PalError("caps: expected ']'")
        for item in after[lb + 1:rb].split(","):
            item = item.strip()
            if not item:
                continue
            if item == "self":
                caps.append(Cap("self"))
            elif item.startswith("file "):
                caps.append(Cap("file", item[5:].strip().strip('"')))
            else:
                raise PalError("unknown capability entry: %s" % item)
    return caps


def _canon(p):
    return os.path.realpath(p) if os.path.exists(p) else p


def resolve_import(spec, importer):
    base = os.path.dirname(importer)
    local = os.path.join(base, spec)
    if os.path.exists(local):
        return local
    lib = os.environ.get("PALIMPSEST_LIB")
    if lib:
        c = os.path.join(lib, spec)
        if os.path.exists(c):
            return c
    if os.path.exists(spec):
        return spec
    raise PalError('cannot resolve import "%s" (looked relative to %s and $PALIMPSEST_LIB)' % (spec, base))


def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


class Program:
    def __init__(self, path, out):
        self.mode = "rewriting-as-running"
        self.rebind_main = False
        self.fuel = 100000
        self.caps = []
        self.engine = Engine(out)
        self.main = None
        self.commands = []
        self.path = path


def load_program(path, out):
    try:
        text = read_text(path)
    except OSError as e:
        raise PalError("cannot read %s: %s" % (path, e.strerror or e))
    prog = Program(path, out)
    _load_file(path, text, prog, set(), True)
    return prog


def _load_file(path, text, prog, visited, is_root):
    canon = _canon(path)
    if canon in visited:
        return
    visited.add(canon)
    eng = prog.engine
    for start_idx, item in logical_items(text):
        line = item.strip()
        if line.startswith("import "):
            spec = line[7:].strip().strip('"')
            resolved = resolve_import(spec, path)
            try:
                sub = read_text(resolved)
            except OSError as e:
                raise PalError("cannot read import %s: %s" % (resolved, e.strerror or e))
            _load_file(resolved, sub, prog, visited, False)
            continue
        if line.startswith("#"):
            if is_root:
                _parse_directive(line[1:], prog)
            continue
        if line.startswith("rule "):
            eng.add_rule(parse_rule(line[5:]))
        elif line.startswith("transition "):
            eng.add_transition(parse_rule(line[11:]))
        elif line.startswith("strategy "):
            r = split_top_level_str(line[9:], "=")
            if r is None:
                raise PalError("malformed strategy (no '='): %s" % line)
            name, params = parse_strategy_header(r[0].strip())
            eng.strategies[name] = (params, parse_strategy(r[1].strip()))
        elif line.startswith("main "):
            if is_root:
                body = line[5:].lstrip()
                if not body.startswith("="):
                    raise PalError("malformed main (no '='): %s" % line)
                prog.main = read_term(body[1:].strip())
        elif line.startswith("run "):
            if is_root:
                prog.commands.append(("run", parse_strategy(line[4:].strip())))
        elif line.startswith(("show ", "display ", "assert ")):
            if is_root:
                kw = line.split(" ", 1)[0]
                r = split_top_level_str(line[len(kw) + 1:], " with ")
                if r is None:
                    raise PalError("malformed %s (no 'with'): %s" % (kw, line))
                prog.commands.append((kw, read_term(r[0].strip()), parse_strategy(r[1].strip())))
        elif line.startswith("let "):
            if is_root:
                rest = line[4:]
                if "=" not in rest:
                    raise PalError("malformed let (no '='): %s" % line)
                lhs, rhs = rest.split("=", 1)
                name = lhs.strip()
                if (not name.startswith("$") or len(name) < 2
                        or any(c.isspace() or c in "()" for c in name)):
                    raise PalError("let: the name must be a symbol starting with '$': %s" % line)
                r = split_top_level_str(rhs, " with ")
                if r is None:
                    raise PalError("malformed let (no 'with'): %s" % line)
                prog.commands.append(("let", name, read_term(r[0].strip()), parse_strategy(r[1].strip())))
        elif line.startswith("rewrite "):
            if is_root:
                r = split_top_level_str(line[8:], " with ")
                if r is None:
                    raise PalError("malformed rewrite (no 'with'): %s" % line)
                tgt = r[0].strip()
                if tgt == "self":
                    target = ("self", None)
                elif tgt.startswith("file "):
                    target = ("file", tgt[5:].strip().strip('"'))
                else:
                    raise PalError("unknown target '%s'" % tgt)
                prog.commands.append(("rewrite", target, parse_strategy(r[1].strip()), r[1].strip()))
        else:
            raise PalError("unrecognized item in %s: %s" % (path, line))


def _parse_directive(rest, prog):
    rest = rest.strip()
    if rest.startswith("mode "):
        prog.mode = rest[5:].strip()
    elif rest.startswith("fuel "):
        f = rest[5:].strip()
        if not _is_digits(f) or int(f) >= 1 << 64:
            raise PalError("bad fuel value: %s" % rest[5:])
        prog.fuel = int(f)
    elif rest.startswith("caps "):
        prog.caps = parse_caps(rest[5:].strip())
    elif rest == "rebind main":
        prog.rebind_main = True
    elif rest == "memo":
        prog.engine.enable_memo()
    elif rest.startswith("lang"):
        pass
    else:
        raise PalError("unknown directive #%s" % rest)


def find_main(text):
    def is_main_item(acc):
        a = acc.lstrip()
        return a.startswith("main") and a[4:].lstrip().startswith("=")

    def parse_main(acc):
        body = acc.lstrip()[4:].lstrip()[1:]
        return read_term(body.strip())

    acc = ""
    start = 0
    last_idx = 0
    for idx, raw in enumerate(rust_lines(text)):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if acc and not _starts_continuation(line) and _is_complete(acc):
            if is_main_item(acc):
                return start, last_idx, parse_main(acc)
            acc = ""
        if not acc:
            start = idx
            acc = line
        else:
            acc = acc + " " + line
        last_idx = idx
    if acc and is_main_item(acc):
        return start, last_idx, parse_main(acc)
    raise PalError("target file has no 'main = ...' subject to rewrite")


def splice_main(text, start_idx, end_idx, new_term):
    lines = rust_lines(text)
    out = list(lines[:start_idx])
    out.append("main = %s" % render(new_term))
    if end_idx + 1 < len(lines):
        out.extend(lines[end_idx + 1:])
    s = "\n".join(out)
    if text.endswith("\n"):
        s += "\n"
    return s


# ============================================================= safety ===

def addr(data):
    h = 0xcbf29ce484222325
    m = (1 << 64) - 1
    for b in data:
        h ^= b
        h = (h * 0x00000100000001B3) & m
    return "%016x" % h


def _same_path(a, b):
    return _canon(a) == _canon(b)


def caps_allow(caps, target, self_path):
    for c in caps:
        if c.kind == "self":
            if _same_path(target, self_path):
                return True
        elif _same_path(target, c.path):
            return True
    return False


def _ledger_dir(anchor):
    base = os.path.dirname(anchor) or "."
    d = os.path.join(base, ".palimpsest", "ledger")
    os.makedirs(d, exist_ok=True)
    return d


def _write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def ledger_record(anchor, target, prev, new_content):
    d = _ledger_dir(anchor)
    if prev is not None:
        prev_addr = addr(prev.encode("utf-8"))
        sp = os.path.join(d, prev_addr + ".snap")
        if not os.path.exists(sp):
            _write_text(sp, prev)
    else:
        prev_addr = "----------------"
    new_addr = addr(new_content.encode("utf-8"))
    np_ = os.path.join(d, new_addr + ".snap")
    if not os.path.exists(np_):
        _write_text(np_, new_content)
    status = "unchanged" if new_content == prev else "rewrite"
    with open(os.path.join(d, "journal.log"), "a", encoding="utf-8", newline="") as j:
        j.write("%s\t%s\t%s\t%s\n" % (status, target, prev_addr, new_addr))
    return prev_addr, new_addr


def transactional_write(target, self_path, caps, new_content, dry_run):
    if not caps_allow(caps, target, self_path):
        raise PalError("capability denied: program is not permitted to rewrite %s" % target)
    try:
        prev = read_text(target)
    except OSError:
        prev = None
    changed = prev != new_content
    if dry_run:
        pa = addr(prev.encode("utf-8")) if prev is not None else "----------------"
        return changed, True, pa, addr(new_content.encode("utf-8"))
    prev_addr, new_addr = ledger_record(self_path, target, prev, new_content)
    d = os.path.dirname(target) or "."
    tmp = os.path.join(d, ".palimpsest.tmp.%d.%s" % (os.getpid(), new_addr))
    _write_text(tmp, new_content)
    os.replace(tmp, target)
    return changed, False, prev_addr, new_addr


def undo_last(anchor):
    d = _ledger_dir(anchor)
    try:
        text = read_text(os.path.join(d, "journal.log"))
    except OSError:
        text = ""
    lines = [l for l in rust_lines(text) if l.strip()]
    cols = lines[-1].split("\t") if lines else []
    if len(cols) != 4:
        raise PalError("nothing to undo: the ledger journal is empty")
    target, prev_addr = cols[1], cols[2]
    try:
        prev = read_text(os.path.join(d, prev_addr + ".snap"))
    except OSError:
        raise PalError("previous snapshot %s not found" % prev_addr)
    _write_text(target, prev)
    return target


def line_diff(old, new):
    if old == new:
        return "    (no change — already a fixed point)"
    o, n = rust_lines(old), rust_lines(new)
    out = []
    for i in range(max(len(o), len(n))):
        a = o[i] if i < len(o) else None
        b = n[i] if i < len(n) else None
        if a is not None and b is not None:
            if a != b:
                out.append("  - %s\n  + %s\n" % (a, b))
        elif a is not None:
            out.append("  - %s\n" % a)
        elif b is not None:
            out.append("  + %s\n" % b)
    return "".join(out)


# ============================================================= driver ===

def _subst_lets(t, lets):
    if not lets:
        return t
    tt = type(t)
    if tt is str and t.startswith("$"):
        for n, v in reversed(lets):
            if n == t:
                return v
        return t
    if tt is tuple:
        return tuple([_subst_lets(x, lets) for x in t])
    return t


def _subst_main(t, main):
    tt = type(t)
    if tt is str and t == "main":
        return main
    if tt is tuple:
        return tuple([_subst_main(x, main) for x in t])
    return t


def _indent(s):
    return "".join("  %s\n" % l for l in rust_lines(s))


def run_program(path, out, err, dry_run=False, fuel=None, stats=False, memo=False, trace=None):
    """Run a program file as the CLI does. Returns the exit status (0/1)."""
    try:
        _run(path, out, dry_run, fuel, stats, memo, trace)
        return 0
    except PalError as e:
        err("palimpsest: %s\n" % e)
        return 1
    except RecursionError:
        err("palimpsest: strategy recursion too deep\n")
        return 1


def _run(path, out, dry_run, fuel_override, stats, memo, trace):
    prog = load_program(path, out)
    eng = prog.engine
    if trace is not None:
        eng.enable_trace(trace)
    if memo:
        eng.enable_memo()
    if fuel_override is not None:
        prog.fuel = fuel_override
    if stats:
        eng.enable_stats()
    out("== palimpsest ==\n")
    out("program : %s\n" % path)
    out("mode    : %s\n" % prog.mode)
    out("fuel    : %d\n" % prog.fuel)
    out("caps    : rewrite [%s]\n" % ", ".join(c.debug() for c in prog.caps))
    if dry_run:
        out("DRY-RUN : no files will be modified\n")
    out("\n")
    eng.fuel = prog.fuel
    passed = failed = 0
    main_now = prog.main
    lets = []
    for cmd in prog.commands:
        kind = cmd[0]
        if kind == "run":
            if main_now is None:
                raise PalError("`run` requires a `main = ...` subject term")
            res = eng.apply(cmd[1], main_now)
            if res is None:
                raise PalError("strategy failed on the subject term")
            out("run: %s  ==>  %s\n" % (render(main_now), render(res)))
        elif kind == "show":
            t, s = cmd[1], cmd[2]
            res = eng.apply(s, _subst_lets(t, lets))
            if res is None:
                raise PalError("strategy failed")
            out("show: %s  ==>  %s\n" % (render(t), render(res)))
        elif kind == "display":
            t = _subst_lets(cmd[1], lets)
            if main_now is not None:
                t = _subst_main(t, main_now)
            res = eng.apply(cmd[2], t)
            if res is None:
                raise PalError("strategy failed")
            if type(res) is Str:
                out("display:\n%s\n" % res.v)
            else:
                out("display: %s\n" % render(res))
        elif kind == "let":
            name, t, s = cmd[1], cmd[2], cmd[3]
            t = _subst_lets(t, lets)
            if main_now is not None:
                t = _subst_main(t, main_now)
            v = eng.apply(s, t)
            if v is None:
                raise PalError("let: strategy failed")
            out("let: %s bound\n" % name)
            lets.append((name, v))
        elif kind == "assert":
            t, s = cmd[1], cmd[2]
            te = _subst_lets(t, lets)
            if main_now is not None:
                te = _subst_main(te, main_now)
            res = eng.apply(s, te)
            if res is None:
                raise PalError("strategy failed")
            if res == TRUE and type(res) is str:
                out("assert: PASS  %s\n" % render(t))
                passed += 1
            else:
                out("assert: FAIL  %s  ==>  %s\n" % (render(t), render(res)))
                failed += 1
        elif kind == "rewrite":
            target, strat, strat_src = cmd[1], cmd[2], cmd[3]
            new_main = _exec_rewrite(prog, target, strat, strat_src, dry_run, out)
            if prog.rebind_main and target[0] == "self":
                main_now = new_main
    out("\nfuel remaining: %d\n" % eng.fuel)
    if passed + failed > 0:
        out("asserts : %d passed, %d failed\n" % (passed, failed))
    if eng.trace_limit is not None:
        out("trace   : %d step(s) shown (limit %d)\n" % (eng.trace_count, eng.trace_limit))
    if eng.stats is not None:
        v = sorted(eng.stats.items(), key=lambda kv: (-kv[1], kv[0]))
        total = sum(n for _, n in v)
        out("\nrewrite profile (%d steps, %d distinct rules):\n" % (total, len(v)))
        if eng.memo:
            out("  memo: %d normal forms cached, %d hits; %d normalizations reused\n"
                % (len(eng.known), eng.hits, eng.nf_hits))
        for name, n in v:
            out("  %10d  %s\n" % (n, name))
    if failed > 0:
        raise PalError("%d assertion(s) failed" % failed)


def _exec_rewrite(prog, target, strat, strat_src, dry_run, out):
    target_path = prog.path if target[0] == "self" else target[1]
    try:
        target_text = read_text(target_path)
    except OSError as e:
        raise PalError("cannot read target %s: %s" % (target_path, e.strerror or e))
    start, end, main_term = find_main(target_text)
    new_term = prog.engine.apply(strat, main_term)
    if new_term is None:
        raise PalError("rewrite strategy failed on target subject")
    new_text = splice_main(target_text, start, end, new_term)
    label = "self" if target[0] == "self" else 'file "%s"' % target[1]
    out("rewrite %s with %s\n" % (label, strat_src))
    out("  subject : %s\n" % render(main_term))
    out("  result  : %s\n" % render(new_term))
    if dry_run:
        out("  diff    :\n")
        out(_indent(line_diff(target_text, new_text)))
    changed, was_dry, pa, na = transactional_write(target_path, prog.path, prog.caps, new_text, dry_run)
    if was_dry:
        out("  status  : DRY-RUN (%s), snapshot %s -> %s\n"
            % ("would change" if changed else "fixed point", pa, na))
    elif changed:
        out("  status  : WROTE (atomic rename), snapshot %s -> %s\n" % (pa, na))
    else:
        out("  status  : FIXED POINT — file reproduced byte-identically (%s). This is a quine.\n" % na)
    return new_term


def run_cli(args, out=None, err=None):
    """The `palimpsest` command line: args excludes the program name."""
    if out is None:
        out = sys.stdout.write
    if err is None:
        err = sys.stderr.write
    if not args:
        err("usage: palimpsest <program.pal> [--dry-run] [--fuel N] [--stats] [--memo] [--trace N]\n")
        err("       palimpsest undo <anchor.pal>   # roll back the last rewrite\n")
        return 2
    if args[0] == "undo":
        if len(args) < 2:
            err("usage: palimpsest undo <anchor.pal>\n")
            return 2
        try:
            t = undo_last(args[1])
            out("undo: restored %s from its previous snapshot\n" % t)
            return 0
        except PalError as e:
            err("palimpsest: %s\n" % e)
            return 1
    path = None
    dry_run = stats = memo = False
    fuel = trace = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--dry-run":
            dry_run = True
        elif a == "--stats":
            stats = True
        elif a == "--memo":
            memo = True
        elif a == "--trace":
            i += 1
            trace = int(args[i]) if i < len(args) and _is_digits(args[i]) else None
        elif a == "--fuel":
            i += 1
            fuel = int(args[i]) if i < len(args) and _is_digits(args[i]) else None
        else:
            path = a
        i += 1
    if path is None:
        err("error: no program file given\n")
        return 2
    return run_program(path, out, err, dry_run, fuel, stats, memo, trace)


def main():
    import threading
    sys.setrecursionlimit(1000000)
    for size in (512, 256, 64):
        try:
            threading.stack_size(size * 1024 * 1024)
            break
        except (ValueError, RuntimeError):
            continue
    result = []
    th = threading.Thread(target=lambda: result.append(run_cli(sys.argv[1:])))
    th.start()
    th.join()
    sys.stdout.flush()
    sys.exit(result[0] if result else 1)


if __name__ == "__main__":
    main()
