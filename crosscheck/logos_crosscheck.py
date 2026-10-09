#!/usr/bin/env python3
"""Independent cross-check of LOGOS-SCSPL.md, outside Palimpsest.

Pure Python 3 (standard library only); shares no code with lib/logos.pal.
Re-implements the toy model, the splitmix64 hash behind Palimpsest's `rng`
primitive, and the pooling algebra, and compares against the numbers the
paper reports. Exit status 0 iff all agree.

    python3 crosscheck/logos_crosscheck.py
"""
import itertools, sys
from fractions import Fraction

ok_all = True
def check(name, got, want):
    global ok_all
    ok = got == want
    ok_all &= ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {got}" + ("" if ok else f"   (expected {want})"))

M64 = (1 << 64) - 1
def rng(n):  # splitmix64, as in src/strategy.rs; result >> 1 (non-negative)
    z = (n + 0x9E3779B97F4A7C15) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    z ^= z >> 31
    return z >> 1

print("Section 3 (pooling algebra)")
items = [('a', 1, 2), ('b', 2, 5), ('c', 0, 9)]
def attn(seq, positional=False):
    w = wv = 0
    for j, (_, s, v) in enumerate(seq):
        k = 2 ** (s + (j if positional else 0)); w += k; wv += k * v
    return Fraction(wv, w)
check("attention over all orders", sorted({attn(p) for p in itertools.permutations(items)}), [Fraction(33, 7)])
check("attention [a,b] vs [a,b,a]", (attn(items[:2]), attn([items[0], items[1], items[0]])), (Fraction(4), Fraction(7, 2)))
check("positional attention: distinct outcomes over orders", len({attn(p, True) for p in itertools.permutations(items)}), 6)
check("max-pooling over orders and with a duplicate", ({max(v for _, _, v in p) for p in itertools.permutations(items)}, max([2, 5, 2])), ({9}, 5))

print("Section 4 (frozen versus telic)")
V = ['a', 'b', 'c']
CONS = {('a', 'b'), ('b', 'c'), ('c', 'a')}
CAP = 6
def run(mode, n=60, seed=1):
    W = {}; ctx = ['a']; recs = []; changes = []
    for _ in range(n):
        logits = [W.get((ctx[-1], t), 0) for t in V]
        # replay check: syntax rebuilt from initial weights and the context alone
        R = {}
        for i in range(1, len(ctx)):
            if mode == 'telic':
                d = 2 * ((ctx[i-1], ctx[i]) in CONS) - 1
                R[(ctx[i-1], ctx[i])] = min(CAP, max(0, R.get((ctx[i-1], ctx[i]), 0) + d))
        cf = logits == [R.get((ctx[-1], t), 0) for t in V]
        ws = [2 ** l for l in logits]; r = rng(seed) % sum(ws)
        for t, w in zip(V, ws):
            if r < w: break
            r -= w
        old = dict(W)
        if mode == 'telic':
            d = 2 * ((ctx[-1], t) in CONS) - 1
            W[(ctx[-1], t)] = min(CAP, max(0, W.get((ctx[-1], t), 0) + d))
        changed = {k: v for k, v in W.items() if v} != {k: v for k, v in old.items() if v}
        recs.append((tuple(ctx[-1:]), tuple(logits), cf, changed))
        ctx.append(t); seed += 1
    util = lambda c: sum((x, y) in CONS for x, y in zip(c, c[1:]))
    halves = [util(ctx[:31]), util(ctx[30:])]
    ch = [r[3] for r in recs]
    last = max([i + 1 for i, c in enumerate(ch) if c], default=0)
    repeats = sum(1 for i in range(len(recs)) for j in range(i + 1, len(recs))
                  if recs[i][0] == recs[j][0] and recs[i][1] != recs[j][1])
    distinct = len(set(zip(ctx, ctx[1:])))
    final = sorted((k, v) for k, v in W.items() if v)
    return dict(halves=halves, changes=sum(ch), last=last, repeats=repeats,
                ctxfn=all(r[2] for r in recs), distinct=distinct, tail=ctx[45:], syntax=final)
f = run('frozen'); t = run('telic')
check("frozen", (f['halves'], f['changes'], f['last'], f['repeats'], f['ctxfn'], f['distinct']), ([11, 13], 0, 0, 0, True, 9))
check("telic", (t['halves'], t['changes'], t['last'], t['repeats'], t['ctxfn'], t['distinct']), ([16, 29], 18, 34, 418, True, 8))
check("telic final syntax", t['syntax'], [(('a', 'b'), 6), (('b', 'c'), 6), (('c', 'a'), 6)])
check("telic tail", ''.join(t['tail']), 'abcabcabcbcabcab')

print("Section 5 (step-wise versus whole-path selection)")
P = {('a', 'a'): 0, ('a', 'b'): 3, ('a', 'c'): 1, ('b', 'a'): -4, ('b', 'b'): -4, ('b', 'c'): -4,
     ('c', 'a'): 2, ('c', 'b'): 0, ('c', 'c'): 3}
score = lambda p: sum(P[x] for x in zip(p, p[1:]))
g = ['a']
for _ in range(3):
    best = None
    for t2 in V:
        if best is None or P[(g[-1], t2)] > P[(g[-1], best)]: best = t2
    g.append(best)
paths = [('a',) + q for q in itertools.product(V, repeat=3)]
b = None
for p in paths:
    if b is None or score(p) > score(b): b = p
check("greedy path and score", (''.join(g), score(g)), ('abab', 2))
check("best path and score", (''.join(b), score(b)), ('accc', 7))

print("Section 6 (self-configuring fixed point)")
def episode(W, n=30, seed=1):
    W = dict(W); ctx = ['a']
    for _ in range(n):
        ws = [2 ** W.get((ctx[-1], t), 0) for t in V]; r = rng(seed) % sum(ws)
        for t, w in zip(V, ws):
            if r < w: break
            r -= w
        d = 2 * ((ctx[-1], t) in CONS) - 1
        W[(ctx[-1], t)] = min(CAP, max(0, W.get((ctx[-1], t), 0) + d))
        ctx.append(t); seed += 1
    return {k: v for k, v in W.items() if v}
W, k = {}, 0
while True:
    W2 = episode(W)
    if W2 == W: break
    W, k = W2, k + 1
check("refinements to the fixed point, and the fixed syntax", (k, sorted(W.items())), (2, [(('a', 'b'), 6), (('b', 'c'), 6), (('c', 'a'), 6)]))

def fixed_point(n, seed):
    W, k = {}, 0
    while k < 500:
        W2 = episode(W, n, seed)
        if W2 == W: return tuple(sorted(W.items()))
        W, k = W2, k + 1
    return None
fp30 = {fixed_point(30, sd) for sd in range(1, 41)}
check("30-step episodes, seeds 1-40: distinct fixed points", len(fp30), 1)
fp5 = [fixed_point(5, sd) for sd in range(1, 41)]
check("5-step episodes, seeds 1-40: seeds whose fixed point is the empty syntax", sum(f == () for f in fp5), 7)
check("5-step episodes: more than one fixed point occurs", len(set(fp5)) > 1, True)

print("all agree" if ok_all else "MISMATCH")
sys.exit(0 if ok_all else 1)
