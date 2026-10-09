#!/usr/bin/env python3
"""Independent cross-check of TELIC-GAMES.md, outside Palimpsest.

Pure Python 3 (standard library only). Re-implements the needed game theory
from scratch by brute force (no code is shared with lib/games.pal) and
compares against the numbers the paper reports. Exit status 0 iff all agree.

    python3 crosscheck/games_crosscheck.py
"""
import itertools, math, sys

ok_all = True
def check(name, got, want):
    global ok_all
    ok = got == want
    ok_all &= ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {got}" + ("" if ok else f"   (expected {want})"))

# ---- generic finite games -------------------------------------------------
def profiles(sets): return list(itertools.product(*sets))
def improvements(sets, u, p):
    out = []
    for i, Si in enumerate(sets):
        for s in Si:
            q = p[:i] + (s,) + p[i+1:]
            if u(i, q) > u(i, p): out.append(q)
    return out
def pure_nash(sets, u): return [p for p in profiles(sets) if not improvements(sets, u, p)]
def terminating(sets, u):
    E = {p: improvements(sets, u, p) for p in profiles(sets)}
    alive = set(E)
    while alive:
        sinks = {p for p in alive if not any(q in alive for q in E[p])}
        if not sinks: return False
        alive -= sinks
    return True
def reachable_nash(sets, u, p):
    seen, stack, out = set(), [p], set()
    while stack:
        x = stack.pop()
        if x in seen: continue
        seen.add(x)
        imps = improvements(sets, u, x)
        if not imps: out.add(x)
        stack += imps
    return out
def weakly_dominant(sets, u, i, s):
    return all(u(i, p[:i] + (s,) + p[i+1:]) >= u(i, p) for p in profiles(sets))

# ---- merges ----------------------------------------------------------------
def diamond(x, y):
    if x == y: return x
    if x == 'bot': return y
    if y == 'bot': return x
    return 'top'
RANK = {'bot': 0, 'lo': 1, 'mid': 2, 'hi': 3}
def chain(x, y): return x if RANK[x] >= RANK[y] else y
def join_game(merge, utils):
    def u(i, p):
        o = 'bot'
        for x in p: o = merge(o, x)
        return utils[i][o]
    return u

print("Section 4 (join games)")
rivals = [{'a': 3, 'b': 2, 'top': 1, 'bot': 0}, {'a': 2, 'b': 3, 'top': 1, 'bot': 0}]
full = [['bot', 'a', 'b', 'top']] * 2
check("diamond pure NE", pure_nash(full, join_game(diamond, rivals)),
      [('bot', 'b'), ('a', 'bot'), ('a', 'a'), ('b', 'b'), ('top', 'top')])
hd = [['a', 'bot'], ['b', 'bot']]
check("assert/yield pure NE", pure_nash(hd, join_game(diamond, rivals)), [('a', 'bot'), ('bot', 'b')])
# mixed: Pr[opponent asserts] making telor i indifferent (Prop 4.4 formula)
u0 = rivals[0]
sig = (u0['a'] - u0['bot']) / ((u0['a'] - u0['bot']) + (u0['b'] - u0['top']))
check("assert prob, collision prob", (sig, sig * sig), (0.75, 0.5625))
pp = [{'a': 1, 'b': 1, 'top': 0, 'bot': 0}, {'a': 0, 'b': 0, 'top': 1, 'bot': 0}]
check("parsimony/plenitude pure NE", pure_nash([['a', 'b']] * 2, join_game(diamond, pp)), [])
cu = [{'bot': 0, 'lo': 2, 'mid': 1, 'hi': 0}, {'bot': 0, 'lo': 1, 'mid': 2, 'hi': 1}]
cs = [['bot', 'lo', 'mid', 'hi']] * 2
check("chain peaks weakly dominant", (weakly_dominant(cs, join_game(chain, cu), 0, 'lo'),
                                      weakly_dominant(cs, join_game(chain, cu), 1, 'mid')), (True, True))
ku = [{'bot': 0, 'lo': 2, 'mid': 0, 'hi': 1}, cu[1]]
check("kinked peak weakly dominant", weakly_dominant(cs, join_game(chain, ku), 0, 'lo'), False)

print("Section 5 (dynamics)")
def weak_orders(dom):
    tabs = set()
    for v in itertools.product(range(len(dom)), repeat=len(dom)):
        r = sorted(set(v)); tabs.add(tuple(r.index(x) for x in v))
    return [dict(zip(dom, t)) for t in sorted(tabs)]
for name, merge, dom, want in [("chain lo<mid<hi", chain, ['lo', 'mid', 'hi'], 0),
                               ("{a,b,top}", diamond, ['a', 'b', 'top'], 18)]:
    W = weak_orders(dom)
    bad = sum(not terminating([dom, dom], join_game(merge, [t0, t1])) for t0 in W for t1 in W)
    check(f"games without FIP over {name} ({len(W)}x{len(W)})", bad, want)
chase = [{'a': 2, 'b': 2, 'top': 1, 'bot': 0}, {'a': 2, 'b': 2, 'top': 3, 'bot': 1}]
cg = [['a', 'b', 'bot', 'top']] * 2
check("chase: terminating, has NE", (terminating(cg, join_game(diamond, chase)),
                                     len(pure_nash(cg, join_game(diamond, chase))) > 0), (False, True))
check("assert/yield reachable from (a,b)", reachable_nash(hd, join_game(diamond, rivals), ('a', 'b')),
      {('bot', 'b'), ('a', 'bot')})
w = lambda x, y: 2 if x == y else 0
bias = lambda i, s: 1 if (i, s) in [(0, 'r'), (1, 'r'), (2, 'g')] else 0
def upath(i, p):
    x, y, z = p
    return [bias(0, x) + w(x, y), bias(1, y) + w(x, y) + w(y, z), bias(2, z) + w(y, z)][i]
phi = lambda p: bias(0, p[0]) + bias(1, p[1]) + bias(2, p[2]) + w(p[0], p[1]) + w(p[1], p[2])
P3 = [['r', 'g']] * 3
exact = all(upath(i, p[:i] + (s,) + p[i+1:]) - upath(i, p) == phi(p[:i] + (s,) + p[i+1:]) - phi(p)
            for p in profiles(P3) for i in range(3) for s in 'rg')
check("path: exact potential", exact, True)
check("path: NE and potentials", [(p, phi(p)) for p in pure_nash(P3, upath)],
      [(('r', 'r', 'r'), 6), (('g', 'g', 'g'), 5)])
check("path: schedule-dependent starts", sum(len(reachable_nash(P3, upath, p)) > 1 for p in profiles(P3)), 4)
mis = lambda x, y: 0 if x == y else 3
def uopp(i, p):
    x, y, z = p
    return [w(x, y), mis(x, y) + w(y, z), w(y, z)][i]
check("opposed path: NE, terminating", (pure_nash(P3, uopp), terminating(P3, uopp)), ([], False))

print("Section 6 (global stage)")
PD = {('c', 'c'): (3, 3), ('c', 'd'): (0, 5), ('d', 'c'): (5, 0), ('d', 'd'): (1, 1)}
upd = lambda i, p: PD[p][i]
def meta21(S0, S1, u):
    F = list(itertools.product(S0, repeat=len(S1)))          # f : S1 -> S0
    H = list(itertools.product(S1, repeat=len(F)))           # h : F  -> S1
    def play(f, h):
        b = h[F.index(f)]; return (f[S1.index(b)], b)
    out = set()
    for f in F:
        for h in H:
            o = play(f, h)
            if all(u(0, play(f2, h)) <= u(0, o) for f2 in F) and all(u(1, play(f, h2)) <= u(1, o) for h2 in H):
                out.add(o)
    return out
def meta12(S0, S1, u):
    return {(b, a) for (a, b) in meta21(S1, S0, lambda i, p: u(1 - i, (p[1], p[0])))}
uhd = join_game(diamond, rivals)
upp = join_game(diamond, pp)
for name, S0, S1, u, w21, w12 in [
        ("PD", ['c', 'd'], ['c', 'd'], upd, {('c', 'c'), ('d', 'd')}, {('c', 'c'), ('d', 'd')}),
        ("assert/yield", ['a', 'bot'], ['b', 'bot'], uhd, {('a', 'bot'), ('bot', 'b')}, {('a', 'bot'), ('bot', 'b')}),
        ("pennies", ['a', 'b'], ['a', 'b'], upp, {('a', 'a'), ('b', 'b')}, {('a', 'b'), ('b', 'a')})]:
    check(f"metagames {name}: 21G, 12G", (meta21(S0, S1, u), meta12(S0, S1, u)), (w21, w12))
def logit_stationary(sets, u, tau, iters=20000):
    P = profiles(sets); n = len(sets)
    pi = {p: 1 / len(P) for p in P}
    T = {}
    for p in P:
        row = {}
        for i in range(n):
            qs = [p[:i] + (s,) + p[i+1:] for s in sets[i]]
            z = sum(math.exp(u(i, q) / tau) for q in qs)
            for q in qs: row[q] = row.get(q, 0) + math.exp(u(i, q) / tau) / z / n
        T[p] = row
    for _ in range(iters):
        new = dict.fromkeys(P, 0.0)
        for p, m in pi.items():
            for q, x in T[p].items(): new[q] += m * x
        pi = new
    return pi
st = logit_stationary(P3, upath, 0.5)
check("logit path: pi(rrr)/pi(ggg) = e^{1/tau}", round(st[('r', 'r', 'r')] / st[('g', 'g', 'g')], 6), round(math.exp(2), 6))
st = logit_stationary([['c', 'd']] * 2, upd, 0.2)
check("logit PD (tau=0.2): mass on (d,d) > 0.98", st[('d', 'd')] > 0.98, True)

print("all agree" if ok_all else "MISMATCH")
sys.exit(0 if ok_all else 1)
