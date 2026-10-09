#!/usr/bin/env python3
"""Independent cross-check of the materialist-economy study (MATERIALIST-ECONOMY.md).

Pure Python 3, standard library only (fractions.Fraction for exact arithmetic).
Re-implements, from the written specification and not from the Palimpsest
code, every computation reported by the thirteen programs

    examples/me-value.pal  me-distribution.pal  me-games.pal  me-economy.pal
    examples/me-regimes.pal  me-loops.pal  me-dialectics.pal
    examples/me-classical.pal  me-selectorate.pal  me-extremes.pal  me-evidence.pal
    examples/me-finance.pal  me-financialized.pal

regenerates the text of their displayed tables with the same formatting, and
compares it with what Palimpsest prints. A table that agrees agrees digit for
digit (every number in it is an exact rational rounded only for display).

Usage:  python3 crosscheck/materialist_crosscheck.py [path/to/palimpsest]
        (with ME_OUTPUTS=DIR, reuses program outputs saved there as NAME.pal.out)
Exit status 0 iff everything agrees.
"""
import os, re, subprocess, sys
from fractions import Fraction as F
from itertools import product
from math import isqrt, factorial

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "target/release/palimpsest")
ENV = dict(os.environ, PALIMPSEST_LIB=os.path.join(ROOT, "lib"))
ok_all = True
n_checks = 0


def check(name, got, want):
    global ok_all, n_checks
    n_checks += 1
    ok = got == want
    ok_all &= ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        g, w = str(got).splitlines(), str(want).splitlines()
        for i in range(max(len(g), len(w))):
            a = g[i] if i < len(g) else "<missing>"
            b = w[i] if i < len(w) else "<missing>"
            if a != b:
                print(f"        line {i}:\n          python : {a}\n          model  : {b}")
                break


def run_pal(name):
    """run an example (or reuse its output saved by verify-materialist.sh in $ME_OUTPUTS)"""
    cache = os.environ.get("ME_OUTPUTS")
    if cache and os.path.exists(os.path.join(cache, name + ".out")):
        return open(os.path.join(cache, name + ".out")).read()
    path = os.path.join(ROOT, "examples", name)
    r = subprocess.run([BIN, path, "--dry-run"], capture_output=True, text=True, env=ENV)
    return r.stdout


def displays(out):
    """the bodies of all `display:` blocks, in order"""
    parts = out.split("display:\n")[1:]
    res = []
    for p in parts:
        lines = []
        for ln in p.split("\n"):
            if ln.startswith("display:") or ln.startswith("assert: ") or ln.startswith("fuel remaining") or ln.startswith("let: "):
                break
            lines.append(ln)
        while lines and lines[-1] == "":
            lines.pop()
        res.append("\n".join(lines))
    return res


def asserts_ok(out):
    m = re.search(r"asserts : (\d+) passed, (\d+) failed", out)
    return (int(m.group(1)), int(m.group(2))) if m else None


# ------------------------------------------------------------ formatting ----
def dec(x, d):
    """Palimpsest's (decimal X D): round half away from zero, D digits"""
    x = F(x)
    neg = x < 0
    ax = abs(x) * 10 ** d
    n = int(ax + F(1, 2))  # floor(ax + 1/2) for ax >= 0
    ip, fp = divmod(n, 10 ** d)
    s = ("-" if neg and n != 0 else "") + str(ip)
    if d > 0:
        s += "." + str(fp).rjust(d, "0")
    return s


def padl(s, w): return s.rjust(w)
def padr(s, w): return s.ljust(w)


def sh(t):
    """canonical Palimpsest printing of a Python stand-in for a term"""
    if isinstance(t, bool):
        return "true" if t else "false"
    if isinstance(t, int):
        return str(t)
    if isinstance(t, F):
        return str(t.numerator) if t.denominator == 1 else f"{t.numerator}/{t.denominator}"
    if isinstance(t, str):
        return t
    if isinstance(t, tuple):  # (head, args...)
        return "(" + " ".join(sh(x) for x in t) + ")"
    if isinstance(t, list):
        return "(list" + "".join(" " + sh(x) for x in t) + ")"
    raise TypeError(t)


def drow(xs, d, w): return "".join(padl(dec(x, d), w) for x in xs)
def srow(xs, w): return "".join(padl(sh(x), w) for x in xs)
def tf(b): return "true" if b else "false"
def rnd(x, k):
    """(round-to X K): floor(X K + 1/2) / K"""
    return F((F(x) * k + F(1, 2)).__floor__(), k)


# ------------------------------------------------------- linear algebra ----
def ident(n): return [[F(int(i == j)) for j in range(n)] for i in range(n)]
def msub(A, B): return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]
def mscale(c, A): return [[c * x for x in r] for r in A]
def vm(v, M): return [sum((v[i] * M[i][j] for i in range(len(v))), F(0)) for j in range(len(M[0]))]
def mv(M, v): return [sum((M[i][j] * v[j] for j in range(len(v))), F(0)) for i in range(len(M))]
def dot(a, b): return sum((F(x) * y for x, y in zip(a, b)), F(0))


def inv(M):
    n = len(M)
    a = [list(map(F, r)) + e for r, e in zip(M, ident(n))]
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j] != 0), None)
        if p is None:
            return None
        a[j], a[p] = a[p], a[j]
        pv = a[j][j]
        a[j] = [x / pv for x in a[j]]
        for i in range(n):
            if i != j and a[i][j] != 0:
                f = a[i][j]
                a[i] = [x - f * y for x, y in zip(a[i], a[j])]
    return [r[n:] for r in a]


def det(M):
    n = len(M)
    a = [list(map(F, r)) for r in M]
    d = F(1)
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j] != 0), None)
        if p is None:
            return F(0)
        if p != j:
            a[j], a[p] = a[p], a[j]
            d = -d
        d *= a[j][j]
        for i in range(j + 1, n):
            f = a[i][j] / a[j][j]
            a[i] = [x - f * y for x, y in zip(a[i], a[j])]
    return d


def hs(M):
    L = msub(ident(len(M)), M)
    return all(det([r[:k] for r in L[:k]]) > 0 for k in range(1, len(M) + 1))


def lvalues(A, l): return vm(l, inv(msub(ident(len(A)), A)))
def gross(A, d): return mv(inv(msub(ident(len(A)), A)), d)


def gross_iter(A, d, k):
    x = list(d)
    for _ in range(k):
        x = [a + b for a, b in zip(mv(A, x), d)]
    return x


def lv_iter(A, l, k):
    x = list(l)
    for _ in range(k):
        x = [a + b for a, b in zip(vm(x, A), l)]
    return x


# ============================================================================
# PART I -- examples/me-value.pal
# ============================================================================
def part1():
    print("PART I  value, the plan, the opposition of classes (me-value.pal)")
    out = run_pal("me-value.pal")
    D = displays(out)
    A = [[F(1, 5), F(1, 5), F(1, 10)], [F(1, 10), F(1, 5), F(0)], [F(0), F(0), F(0)]]
    l = [F(1), F(2), F(1)]
    b = [F(0), F(1, 4), F(0)]
    d3 = [F(0), F(10), F(2)]
    A4 = [[F(1, 20), F(1, 10), F(1, 50), F(0)], [F(2), F(1, 5), F(0), F(1, 2)], [F(0), F(0), F(0), F(5, 3)], [F(0)] * 4]
    l4 = [F(5), F(2), F(3), F(1)]
    d4 = [F(0), F(20000), F(0), F(1000)]
    lam = lvalues(A, l)
    # §3.1
    x4 = gross(A4, d4)

    def plan_loop(A, d, tol):
        x, k = list(d), 0
        while True:
            x2 = [a + b for a, b in zip(mv(A, x), d)]
            k += 1
            if max(abs(a - c) for a, c in zip(x2, x)) <= tol:
                return k, x2
            x = x2
    pk, px = plan_loop(A4, d4, 1)
    err = lambda k: max(abs(a - c) for a, c in zip(x4, gross_iter(A4, d4, k)))
    its = [gross_iter(A4, d4, j) for j in range(26)]
    mono = all(all(b2 >= a2 for a2, b2 in zip(its[i], its[i + 1])) for i in range(25))
    fmtv = lambda xs: " ".join(padl(dec(x, 4), 10) for x in xs)
    s1 = "\n".join([
        "§3.1 LABOUR VALUES AND THE PLAN",
        f"  E3 productive (Hawkins-Simon and (I-A)^-1 >= 0): {tf(hs(A) and all(v >= 0 for r in inv(msub(ident(3), A)) for v in r))}",
        f"  labour values lambda = l(I-A)^-1      : {sh(lam)}",
        f"  fixed point of lambda -> lambda A + l : {tf([a + c for a, c in zip(vm(lam, A), l)] == lam)}",
        f"  iterates lambda_0..lambda_4           : {fmtv(lv_iter(A, l, 4))}",
        f"  plan4 exact gross output              : {sh(x4)}",
        f"  ... rounded to the ton                : {sh([rnd(v, 1) for v in x4])}",
        f"  planner's loop to 1-ton agreement     : {sh(('plan', pk, [rnd(v, 1) for v in px]))}",
        f"  error after 17 / 18 / 25 passes       : {dec(err(17), 4)}  {dec(err(18), 4)}  {dec(err(25), 4)}",
        f"  iterates monotone (x_0 <= ... <= x_25): {tf(mono)}",
        f"  labour required by the plan, lambda.d : {sh(dot(lvalues(A4, l4), d4))} hours"])
    check("§3.1 labour values, the plan, its convergence (table text)", s1, D[0])
    # §3.2
    grid = [[x, y, z] for x in (F(0), F(1), F(7, 2)) for y in (F(0), F(1), F(7, 2)) for z in (F(0), F(1), F(7, 2))]
    cons = all(dot(lam, g) == dot(l, gross(A, g)) for g in grid)
    nv4 = dot(lvalues(A4, l4), d4)
    s2 = "\n".join(["§3.2 CONSERVATION: value of net product = living labour",
                    f"  E3, 27 final demands d in {{0, 1, 7/2}}^3 : {tf(cons)}",
                    f"  plan4                                   : {sh(nv4)} = {sh(dot(l4, gross(A4, d4)))}"])
    check("§3.2 conservation on 27 final demands and the plan", s2, D[1])
    # §3.3
    T = [[lam[i] / lam[j] for j in range(3)] for i in range(3)]
    T2 = [r[:] for r in T]
    T2[0][1] = F(11, 10) * T[0][1]
    T2[1][0] = 1 / T2[0][1]
    trip = [(i, j, k) for i in range(3) for j in range(3) for k in range(3)]
    refl = lambda t: all(t[i][i] == 1 for i in range(3))
    symm = lambda t: all(t[i][j] * t[j][i] == 1 for i, j, k in trip)
    trans = lambda t: all(t[i][j] * t[j][k] == t[i][k] for i, j, k in trip)
    best = lambda t: max(t[i][j] * t[j][k] * t[k][i] for i, j, k in trip)
    third = [T[i][0] for i in range(3)]
    s3 = "\n".join(["§3.3 EXCHANGE AS AN EQUIVALENCE RELATION",
                    f"  T = exchange at labour values: reflexive/symmetric/transitive : {tf(refl(T))} {tf(symm(T))} {tf(trans(T))}",
                    f"  the 'third thing' recovered from T (good mp = 1)               : {sh(third)}",
                    f"  ... represents T exactly                                       : {tf([[third[i] / third[j] for j in range(3)] for i in range(3)] == T)}",
                    f"  best 3-cycle of trades under T                                 : {sh(best(T))}",
                    f"  T' = T with one ratio raised 10%: reflexive/symmetric/transitive: {tf(refl(T2))} {tf(symm(T2))} {tf(trans(T2))}",
                    f"  best 3-cycle under T' (a pure-exchange M-C-M')                 : {sh(best(T2))}"])
    check("§3.3 exchange table, the 'third thing', arbitrage", s3, D[2])

    # §3.4
    def aug(A, b, l): return [[A[i][j] + b[i] * l[j] for j in range(len(l))] for i in range(len(l))]

    def bracket(M, k):
        lo, hi = F(-1, 2), F(8)
        for _ in range(k):
            mid = (lo + hi) / 2
            if hs(mscale(1 + mid, M)):
                lo = mid
            else:
                hi = mid
        return lo, hi
    vlp = dot(lam, b)
    comps = [dot(lam, [A[i][j] for i in range(3)]) / (vlp * l[j]) for j in range(3)]
    shbr = lambda br: f"[{dec(br[0], 8)}, {dec(br[1], 8)})"
    x3 = gross(A, d3)
    c = dot(vm(lam, A), x3); h = dot(l, x3); v = h * vlp
    betas = [F(k, 40) for k in range(1, 21)] + [F(31, 90)]
    fmt_ok = lambda bb: hs(aug(A, bb, l)) == (dot(lam, bb) < 1)

    def gmat(A, b, l):
        n = len(l)
        return [A[i] + [b[i]] for i in range(n)] + [l + [F(0)]]

    def kval(G, k):
        n = len(G)
        oth = [i for i in range(n) if i != k]
        sub = [[G[i][j] for j in oth] for i in oth]
        if not hs(sub):
            return None  # inf
        mu = vm([G[k][j] for j in oth], inv(msub(ident(len(oth)), sub)))
        return G[k][k] + dot(mu, [G[i][k] for i in oth])

    def gcet(bb):
        G = gmat(A, bb, l)
        ks = [kval(G, k) for k in (0, 1, 3)]
        if hs(aug(A, bb, l)):
            return all(x is not None and x < 1 for x in ks)
        return all(x is None or x >= 1 for x in ks)
    grid64 = [[x, y, z] for x in (F(0), F(1, 20), F(1, 10), F(1, 5)) for y in (F(0), F(1, 20), F(1, 10), F(1, 5)) for z in (F(0), F(1, 20), F(1, 10), F(1, 5))]
    G3 = gmat(A, b, l)
    s4 = "\n".join(["§3.4 EXPLOITATION, PRICES OF PRODUCTION, FMT, GCET",
                    f"  value of labour power lambda.b = {sh(vlp)}   rate of exploitation e = {sh((1 - vlp) / vlp)}",
                    f"  value compositions c/v by sector: {fmtv(comps)}",
                    f"  r* (uniform profit rate) in      : {shbr(bracket(aug(A, b, l), 30))}",
                    f"  R  (maximal, w = 0) in           : {shbr(bracket(A, 30))}",
                    f"  value rate of profit s/(c+v)     : {dec((h - v) / (c + v), 4)}",
                    f"  FMT on 21 wage bundles (0,beta,0), incl. the boundary beta = 31/90: {tf(all(fmt_ok([F(0), x, F(0)]) for x in betas))}",
                    f"    ... of which r* > 0: {sum(1 for x in betas if hs(aug(A, [F(0), x, F(0)], l)))}",
                    f"  FMT on 64 bundles b in {{0,1/20,1/10,1/5}}^3                          : {tf(all(fmt_ok(g) for g in grid64))}",
                    f"  GCET (mp, nec and labour all exploited iff r* > 0), same 21 bundles  : {tf(all(gcet([F(0), x, F(0)]) for x in betas))}",
                    f"  own k-values (mp, nec, labour) at b3: {fmtv([kval(G3, k) for k in (0, 1, 3)])}"])
    check("§3.4 exploitation, r* and R brackets, FMT (85 bundles), GCET", s4, D[3])

    # §3.5 / §3.6
    def fwage(A, l, d, r):
        u = vm(l, inv(msub(ident(len(A)), mscale(1 + r, A))))
        return dot(lvalues(A, l), d) / dot(u, d)

    def prices(A, l, d, r):
        w = fwage(A, l, d, r)
        u = vm(l, inv(msub(ident(len(A)), mscale(1 + r, A))))
        return [w * x for x in u]
    rs = [F(k, 10) for k in range(20)]
    ws = [fwage(A, l, d3, r) for r in rs]
    s5 = "\n".join(["§3.5 THE WAGE-PROFIT FRONTIER (numeraire: p.d = lambda.d)",
                    f"  r    : {fmtv(rs)}", f"  w(r) : {fmtv(ws)}",
                    f"  strictly decreasing on r = 0, 0.1, ..., 1.9 : {tf(all(ws[i + 1] < ws[i] for i in range(19)))}",
                    f"  w(0) = {sh(fwage(A, l, d3, F(0)))}   prices p(0) = lambda : {tf(prices(A, l, d3, F(0)) == lam)}"])
    check("§3.5 wage-profit frontier at 20 profit rates", s5, D[4])
    mawd = lambda A, l, d, r: dot([abs(p - q) for p, q in zip(prices(A, l, d, r), lvalues(A, l))], d) / dot(lvalues(A, l), d)
    m3 = [mawd(A, l, d3, F(k, 10)) for k in range(11)]
    Au, lu = [[F(1, 4), F(1, 4)], [F(1, 4), F(1, 4)]], [F(1), F(1)]
    s6 = "\n".join(["§3.6 PRICE-VALUE DEVIATIONS (MAWD over the net product)",
                    f"  r       : {fmtv([F(k, 10) for k in range(11)])}", f"  MAWD E3 : {fmtv(m3)}",
                    f"  MAWD(0) = 0 and strictly increasing on (0, 1]: {tf(all(m3[i + 1] > m3[i] for i in range(10)))}",
                    f"  uniform-composition economy (R = 1): MAWD = 0 at r = 0, ..., 0.9: {tf(all(mawd(Au, lu, [F(1), F(2)], F(k, 10)) == 0 for k in range(10)))}"])
    check("§3.6 price-value deviations (and the uniform-composition case)", s6, D[5])

    # §3.7 Okishio
    def pf(M, k):
        p = [F(1)] * len(M)
        for _ in range(k):
            p2 = vm(p, M)
            s = sum(p2)
            p = [rnd(x / s, 10 ** 12) for x in p2]
        return p
    rows = []
    M0 = aug(A, b, l)
    r0 = bracket(M0, 30)
    for j in (0, 1):
        for s in (F(1, 10), F(1, 5), F(3, 10)):
            for m in (F(1, 40), F(1, 20), F(1, 10)):
                A2 = [r[:] for r in A]; A2[0][j] += m
                l2 = l[:]; l2[j] = (1 - s) * l[j]
                M2 = aug(A2, b, l2)
                p = pf(M0, 60)
                dc = dot(p, [M2[i][j] for i in range(3)]) - dot(p, [M0[i][j] for i in range(3)])
                r1 = bracket(M2, 30)
                b2 = [x * (vlp / dot(lvalues(A2, l2), b)) for x in b]
                r2 = bracket(aug(A2, b2, l2), 30)
                rows.append((j, s, m, dc, r1, r2))
    lines = ["   j   cut  +mach   dCost@p  choice    r-old    r-new  r-new(e)"]
    ok_count = adopted = trpf = 0
    for j, s, m, dc, r1, r2 in rows:
        lines.append(padl(str(j), 4) + padl(dec(s, 2), 6) + padl(dec(m, 3), 7) + padl(dec(dc, 5), 10) + padl("adopt" if dc < 0 else "reject", 8)
                     + padl(dec(r0[0], 5), 9) + padl(dec(r1[0], 5), 9) + padl(dec(r2[0], 5), 10))
        ok_count += (r1[0] >= r0[1]) if dc < 0 else (r1[1] <= r0[0])
        adopted += dc < 0
        trpf += dc < 0 and r2[1] <= r0[0]
    lines.append(f"Okishio verdict holds in {ok_count} of {len(rows)} changes; adopted: {adopted}; of those, r falls under a constant rate of exploitation: {trpf}")
    check("§3.7 Okishio versus the falling rate of profit (18 changes)", "\n".join(["§3.7 TECHNICAL CHANGE: OKISHIO VERSUS THE FALLING RATE OF PROFIT"] + lines), D[6])
    # §3.8
    h = F(1)
    for _ in range(40):
        h = 1 + (F(10000) + 20000 * h) / 60000
    ht = (1 + F(10000, 60000)) / (1 - F(20000, 60000))
    s8 = "\n".join(["§3.8 SKILLED LABOUR",
                    f"  surgeon, 30,000 training h / 60,000 career h, training as simple labour : {sh(1 + F(30000, 60000))}",
                    f"  teacher fixed point (S=10,000, H=20,000, C=60,000)                       : {sh(ht)}",
                    f"  ... by iteration, 40 passes from 1                                        : {dec(h, 4)}",
                    f"  surgeon taught by such teachers (S=10,000, H=20,000)                      : {sh(1 + (10000 + 20000 * ht) / 60000)}"])
    check("§3.8 skilled labour", s8, D[7])
    check("me-value.pal: all assertions pass", asserts_ok(out), (17, 0))


# ============================================================================
# PART II -- examples/me-distribution.pal
# ============================================================================
M64 = (1 << 64) - 1


def rng(n):
    """Palimpsest's `rng`: splitmix64 of the seed, shifted right by one"""
    z = (n + 0x9E3779B97F4A7C15) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    z ^= z >> 31
    return z >> 1


def gini(xs):
    ys = sorted(xs); n = len(ys); s = sum(ys)
    return F(0) if s == 0 else F(sum((2 * (i + 1) - n - 1) * y for i, y in enumerate(ys)), n * s)


def partitions(m, maxpart, maxcount):
    if m == 0:
        yield []
        return
    if maxcount == 0:
        return
    for p in range(min(m, maxpart), 0, -1):
        for rest in partitions(m - p, p, maxcount - 1):
            yield [p] + rest


def occ(part, N, M):
    n = [0] * (M + 1); n[0] = N - len(part)
    for p in part:
        n[p] += 1
    return n


def mult(n):
    w = factorial(sum(n))
    for k in n:
        w //= factorial(k)
    return w


def maxent(N, M):
    """the max-W macrostate, its W, and the number of ties; partitions are
    enumerated in Palimpsest's order (smallest first part first)"""
    parts = sorted(partitions(M, M, N))  # lexicographic = Palimpsest's sconcat over q = 1..M
    best = None; bw = 0; ties = 0; count = 0
    for part in parts:
        count += 1
        n = occ(sorted(part, reverse=True), N, M); w = mult(n)
        if w > bw:
            best, bw, ties = n, w, 1
        elif w == bw:
            ties += 1
    return best, bw, ties, count


def binom(n, k): return F(factorial(n), factorial(k) * factorial(n - k)) if 0 <= k <= n else F(0)
def micro_p(N, M, k): return binom(M - k + N - 2, N - 2) / binom(M + N - 1, N - 1)


def micro_seq(N, M, K):
    p = F(N - 1, M + N - 1); out = []
    for k in range(K + 1):
        out.append(p); p = p * F(M - k, M - k + N - 2)
    return out


def geo(T, k):
    q = F(T) / (1 + F(T)); return (1 - q) * q ** k


def tv_micro(N, M, K):
    T = F(M, N); ps = micro_seq(N, M, K); gs = [geo(T, k) for k in range(K + 1)]
    return (sum(abs(a - b) for a, b in zip(ps, gs)) + abs(sum(ps) - sum(gs))) / 2


def xrun(m, t, n, dm, k):
    m = m[:]
    for _ in range(k):
        i = rng(t) % n; j = rng(2 * t + 1000003) % n
        if i != j and m[i] >= dm:
            m[i] -= dm; m[j] += dm
        t += 1
    return m


def part2():
    print("PART II  the distribution of money (me-distribution.pal)")
    out = run_pal("me-distribution.pal")
    D = displays(out)
    a = maxent(8, 16); b = maxent(12, 24)
    eq_split = lambda N, M: mult([0] * (M // N) + [N] + [0] * (M - M // N))
    s1 = "\n".join(["§4.1 MACROSTATES: N agents, M units; W = N!/prod n_k! (exact integers)",
                    f"  N=8,  M=16: macrostates {a[3]}   max W {a[1]} (unique: {tf(a[2] == 1)})  at n_k = {sh(a[0][:8])}",
                    f"  N=12, M=24: macrostates {b[3]}  max W {b[1]} (unique: {tf(b[2] == 1)})  at n_k = {sh(b[0][:8])}",
                    f"  W of the equal split (everyone holds T): {eq_split(8, 16)} and {eq_split(12, 24)}"])
    check("§4.1 macrostates and the maximum-multiplicity occupation", s1, D[0])
    ok_rec = micro_seq(6, 10, 10) == [micro_p(6, 10, k) for k in range(11)] and micro_seq(10, 20, 20) == [micro_p(10, 20, k) for k in range(21)]
    ms = micro_seq(100, 1000, 60)
    tvs = [tv_micro(10, 100, 60), tv_micro(100, 1000, 60), tv_micro(1000, 10000, 60)]
    gg = 1 / (1 + F(10, 11))
    s2 = "\n".join(["§4.2 THE EXACT MICROCANONICAL MARGINAL  P(m=k) = C(M-k+N-2,N-2)/C(M+N-1,N-1)",
                    f"  recurrence = binomial formula, N=6 M=10 and N=10 M=20 (all k): {tf(ok_rec)}",
                    f"  N=100, M=1000: P(0..5) = {drow(ms[:6], 5, 9)}",
                    f"  geometric T=10:   g(0..5) = {drow([geo(10, k) for k in range(6)], 5, 9)}",
                    f"  strictly decreasing in k (N=100, M=1000, k = 0..60): {tf(all(ms[i + 1] < ms[i] for i in range(60)))}",
                    f"  total-variation distance to the geometric law, T = 10, N = 10 / 100 / 1000: {drow(tvs, 5, 9)}",
                    f"  Gini of the geometric law at T = 10: {sh(gg)} = {dec(gg, 4)}"])
    check("§4.2 microcanonical marginal, geometric limit, TV distances", s2, D[1])
    # §4.3 pooled exchange
    m = xrun([10] * 100, 0, 100, 1, 20000); t = 20000; hist = [0] * 121; okc = True
    for _ in range(40):
        m = xrun(m, t, 100, 1, 2000); t += 2000
        for x in m:
            hist[min(x, 120)] += 1
        okc &= sum(m) == 1000
    g3 = [gini(xrun([10] * 100, 0, 100, 1, k)) for k in (1000, 5000, 20000)]
    f30 = hist[:30] + [sum(hist[30:])]
    emp = [F(h, 4000) for h in f30]; gs = [geo(10, k) for k in range(30)]; gs.append(1 - sum(gs))
    tv = sum(abs(x - y) for x, y in zip(emp, gs)) / 2
    # Gini from the pooled histogram
    n = sum(hist); S = sum(k * c for k, c in enumerate(hist)); acc = F(0); pos = 0
    for k, c in enumerate(hist):
        sumi = c * pos + F(c * (c + 1), 2); acc += k * (2 * sumi - c * (n + 1)); pos += c
    gp = acc / (n * S)
    s3 = "\n".join(["§4.3 RANDOM CONSERVATIVE EXCHANGE (N = 100, T = 10, pooled 40 snapshots)",
                    f"  money conserved at every snapshot: {tf(okc)}",
                    f"  Gini after 1,000 / 5,000 / 20,000 events: {drow(g3, 4, 8)}",
                    f"  pooled histogram n_0..n_11: {srow(hist[:12], 5)}",
                    f"  expected (geometric x 4000): {drow([4000 * geo(10, k) for k in range(12)], 0, 5)}",
                    f"  share holding nothing: {dec(F(hist[0], 4000), 4)}   (geometric: 1/(T+1) = {dec(F(1, 11), 4)})",
                    f"  total-variation distance to the geometric law: {dec(tv, 4)}",
                    f"  pooled Gini: {dec(gp, 4)}   (geometric: {dec(gg, 4)})"])
    check("§4.3 random exchange: Gini path, pooled histogram, TV, Gini", s3, D[2])

    # §4.4 two classes
    def cstep(s, pub, t, n, c, theta):
        if rng(t) % 2 == 0:
            o = rng(t + 17) % c; w = c + rng(t + 29) % (n - c)
            if pub > 0:
                pub -= 1; s[w] += 1
            elif s[o] > 0:
                s[o] -= 1; s[w] += 1
        else:
            w = c + rng(t + 41) % (n - c); r = rng(t + 53)
            tot = sum(s[:c]) + c; x = r % tot; i = 0
            while True:
                wi = 1 + s[i]
                if i >= c - 1 or x < wi:
                    break
                x -= wi; i += 1
            if s[w] > 0:
                s[w] -= 1; s[i] += 1
        if theta is not None:
            for i in range(c):
                if s[i] > theta:
                    pub += s[i] - theta; s[i] = theta
        return s, pub
    lines = ["§4.4 TWO CLASSES: additive wages vs multiplicative capital income; the asset cap",
             "       events  owners%   wGini      owners (sorted)          pub total  cap-ok"]
    for theta in (None, 60, 30):
        s = [100] * 5 + [5] * 95; pub = 0
        lines.append("  cap " + ("none" if theta is None else str(theta)))
        for t in range(60000):
            s, pub = cstep(s, pub, t, 100, 5, theta)
            if (t + 1) % 20000 == 0:
                tot = sum(s) + pub
                capok = theta is None or all(x <= theta for x in s[:5])
                lines.append(padl(str(t + 1), 9) + padl(dec(F(sum(s[:5]), tot), 4), 9) + padl(dec(gini(s[5:]), 4), 9)
                             + padl(sh(sorted(s[:5])), 26) + padl(str(pub), 5) + padl(str(tot), 6) + padl(tf(capok), 7))
    check("§4.4 two classes under caps none / 60 / 30 (60,000 events each)", "\n".join(lines), D[3])
    # §4.5 Cantillon
    def cantillon(ms, q, d):
        mm = sum(ms); p0 = F(mm, q); b1 = min(F(q), F(ms[0] + d) / p0); left = q - b1
        rest = ms[1:]; withv = [b1] + [F(left) * x / sum(rest) for x in rest]
        return [w - F(q) * x / mm for w, x in zip(withv, ms)]
    def neutral(ms, q, d):
        mm = sum(ms); return [F(q, mm + d) * (x + F(d, mm) * x) - F(q) * x / mm for x in ms]
    c5 = cantillon([600, 300, 100], 1000, 100); n5 = neutral([600, 300, 100], 1000, 100)
    s5 = "\n".join(["§4.5 THE CANTILLON EFFECT (Q = 1000 goods, money 600/300/100, D = 100 new money)",
                    f"  injected at the asset holders, spent first at the old price: real gains {sh(c5)}",
                    f"  injected in proportion, spent after prices adjust:           real gains {sh(n5)}",
                    f"  real gains sum to zero in both (output is fixed): {tf(sum(c5) == 0 and sum(n5) == 0)}",
                    f"  first recipients' real gain = Q.D/M exactly: {tf(c5[0] == F(1000 * 100, 1000))}"])
    check("§4.5 the Cantillon effect, exactly", s5, D[4])

    # §4.6 vouchers
    def vrun(hours, T):
        v = [F(0)] * 20; iss = [F(0)] * 20; red = [F(0)] * 20
        for t in range(T):
            for i in range(20):
                v[i] += hours[i]; iss[i] += hours[i]
                c = v[i] * (1 + rng(1000 * t + i) % 4) / 4
                if c <= v[i]:
                    v[i] -= c; red[i] += c
        return v, iss, red
    hrs = [6 + i % 5 for i in range(20)]; hrs2 = [40] + hrs[1:]
    v1, i1, r1 = vrun(hrs, 30); v2, _, _ = vrun(hrs2, 30)
    xa = xrun([10] * 20, 0, 20, 1, 3000); xb = xrun([11] + [10] * 19, 0, 20, 1, 3000)
    ident_ok = all(v1[i] == i1[i] - r1[i] and 0 <= v1[i] <= i1[i] for i in range(20))
    s6 = "\n".join(["§4.6 LABOUR VOUCHERS (20 agents, 30 periods; issue on work, cancel on purchase, no transfers)",
                    f"  identity v = issued - redeemed, 0 <= v <= issued, every agent: {tf(ident_ok)}",
                    f"  agent 0 works 40 h instead of 6: other agents' holdings unchanged: {tf(v1[1:] == v2[1:])}",
                    f"  exchange economy: agent 0 starts with 1 more unit: others changed: {tf(xa[1:] != xb[1:])}",
                    f"  vouchers outstanding / issued in total: {dec(sum(v1), 2)} / {30 * sum(hrs)}"])
    check("§4.6 labour vouchers: identity, non-interference", s6, D[5])
    check("me-distribution.pal: all assertions pass", asserts_ok(out), (18, 0))

# ============================================================================
# PART III -- examples/me-games.pal
# ============================================================================
def w_cap(b, u, s): return (b + (1 - b) * u * s) / (b + u * (1 - b))
def w_ap(b, g): return g + b * (1 - g)


def cs_pay(reg, p, W, C):
    """class-struggle game payoffs (workers, capital)"""
    if C == "flt":
        return (p["s"], p["rext"]) if reg == "cap" else (p["g"], F(0))
    b = p["bl"] if W == "acc" else (p["bl"] if (reg == "cap" and C == "rep") else p["bh"])
    w = w_cap(b, p["u"], p["s"]) if reg == "cap" else w_ap(b, p["g"])
    pen = F(0) if C == "con" else (p["rho"] if reg == "cap" else p["pen"])
    return (w - (p["k"] if W == "org" else 0), 1 - w - pen)


class Game:
    def __init__(self, sets, pay):
        self.sets, self.pay = sets, pay
    def profiles(self): return list(product(*self.sets))
    def u(self, i, pr): return self.pay(pr)[i]
    def devs(self, i, pr): return [tuple(s if j == i else pr[j] for j in range(len(pr))) for s in self.sets[i]]
    def nash(self): return [pr for pr in self.profiles() if all(all(self.u(i, q) <= self.u(i, pr) for q in self.devs(i, pr)) for i in range(len(self.sets)))]
    def improvements(self, pr): return [q for i in range(len(self.sets)) for q in self.devs(i, pr) if self.u(i, q) > self.u(i, pr)]
    def terminating(self):
        nodes = {pr: self.improvements(pr) for pr in self.profiles()}
        live = set(nodes)
        while True:
            keep = {n for n in live if any(q in live for q in nodes[n])}
            if len(keep) == len(live):
                return len(keep) == 0
            live = keep
    def br_move(self, i, pr):
        best, bv = pr, self.u(i, pr)
        for q in self.devs(i, pr):
            if self.u(i, q) > bv:
                best, bv = q, self.u(i, q)
        return best
    def weakly_dominant(self, i, s):
        return all(self.u(i, tuple(s if j == i else pr[j] for j in range(len(pr)))) >= self.u(i, pr) for pr in self.profiles())


def cs_game(reg, p): return Game([["acc", "org"], ["con", "rep", "flt"]], lambda pr: cs_pay(reg, p, pr[0], pr[1]))


def mixed2(g, r0, r1, c0, c1):
    a = lambda x, y: g.u(0, (x, y)); b = lambda x, y: g.u(1, (x, y))
    q = (a(r1, c1) - a(r0, c1)) / ((a(r0, c0) - a(r1, c0)) - (a(r0, c1) - a(r1, c1)))
    pp = (b(r1, c1) - b(r1, c0)) / ((b(r0, c0) - b(r0, c1)) - (b(r1, c0) - b(r1, c1)))
    return pp, q


PAR3 = dict(s=F(2, 5), u=F(1, 5), bl=F(1, 5), bh=F(1, 2), k=F(1, 20), rho=F(1, 20), rext=F(1, 10), g=F(4, 5), pen=F(1, 10))


def cap_pred(p):
    wl = w_cap(p["bl"], p["u"], p["s"]); wh = w_cap(p["bh"], p["u"], p["s"]); gap = wh - wl
    return gap > p["k"] and p["rext"] < 1 - wl and (gap > p["rho"] or 1 - wh < p["rext"]) and p["rext"] < max(1 - wh, 1 - wl - p["rho"])


def prof(pr): return ("prof",) + tuple(pr)


def part3():
    print("PART III  games with class analysis as input (me-games.pal)")
    out = run_pal("me-games.pal")
    D = displays(out)
    us = [F(0), F(1, 10), F(1, 5), F(2, 5), F(3, 5), F(4, 5), F(1)]
    r15 = [w_cap(F(1, 5), u, F(2, 5)) for u in us]; r12 = [w_cap(F(1, 2), u, F(2, 5)) for u in us]
    pv = lambda y, g: y > g
    pp = lambda b, y, g: (1 - b) * (y - g) if y > g else F(0)
    s1 = "\n".join(["§5.1 WAGE BARGAINING WITH OUTSIDE OPTIONS (share of an hour's value going to the worker)",
                    f"  unemployment u               : {drow(us, 2, 8)}",
                    f"  w_cap, beta = 1/5 (reserve army): {drow(r15, 4, 8)}",
                    f"  w_cap, beta = 1/2              : {drow(r12, 4, 8)}",
                    f"  strictly decreasing in u (both rows): {tf(all(r15[i + 1] < r15[i] and r12[i + 1] < r12[i] for i in range(6)))}",
                    f"  w_ap = g + beta(1 - g), g = 4/5, beta = 1/5 / 1/2 : {sh(w_ap(F(1, 5), F(4, 5)))} / {sh(w_ap(F(1, 2), F(4, 5)))}",
                    f"  private firms viable at productivity 7/10 / 9/10 / 6/5 (g = 4/5): {tf(pv(F(7, 10), F(4, 5)))} {tf(pv(F(9, 10), F(4, 5)))} {tf(pv(F(6, 5), F(4, 5)))}",
                    f"  their profit per hour (beta = 1/2): {sh(pp(F(1, 2), F(7, 10), F(4, 5)))} {sh(pp(F(1, 2), F(9, 10), F(4, 5)))} {sh(pp(F(1, 2), F(6, 5), F(4, 5)))}"])
    check("§5.1 bargaining against the reserve army and the job guarantee", s1, D[0])
    gc, ga = cs_game("cap", PAR3), cs_game("ap", PAR3)
    table = lambda g: "\n".join("  " + padr(f"{a}/{c}", 9) + padl(dec(g.u(0, (a, c)), 4), 9) + padl(dec(g.u(1, (a, c)), 4), 9) for a, c in g.profiles())
    traj = [("acc", "con")]
    for i in (0, 1, 0, 1):
        traj.append(gc.br_move(i, traj[-1]))
    core = Game([["acc", "org"], ["con", "rep"]], lambda pr: cs_pay("cap", PAR3, pr[0], pr[1]))
    mp, mq = mixed2(core, "acc", "org", "con", "rep")
    s2 = "\n".join(["§5.2 THE CLASS-STRUGGLE GAME (payoffs: worker wage net of organizing cost; capital's share net of costs)",
                    "  CAPITALISM          W        C", table(gc),
                    f"  pure Nash equilibria: {sh([prof(x) for x in gc.nash()])}    better-response dynamics terminate: {tf(gc.terminating())}",
                    f"  best-response cycle from (acc,con), schedule W C W C: {sh([prof(x) for x in traj])}",
                    f"  mixed equilibrium of the {{acc,org}}x{{con,rep}} core: Pr[acc] = {sh(mp)}, Pr[con] = {sh(mq)}",
                    "  ACCOUNTABLE PLANNING W        C", table(ga),
                    f"  pure Nash equilibria: {sh([prof(x) for x in ga.nash()])}    better-response dynamics terminate: {tf(ga.terminating())}"])
    check("§5.2 class-struggle game: payoffs, equilibria, cycle, mixed equilibrium", s2, D[1])
    grid = [dict(PAR3, bl=bl, bh=bh, k=k, rho=rho, u=u) for bl in (F(1, 10), F(1, 5), F(3, 10)) for bh in (F(2, 5), F(1, 2), F(3, 5))
            for k in (F(1, 40), F(1, 20), F(1, 10)) for rho in (F(1, 40), F(1, 20), F(1, 10)) for u in (F(1, 10), F(1, 5), F(2, 5))]
    apu = sum(1 for p in grid if (lambda ne: ne and all(c == "con" for w, c in ne) and cs_game("ap", p).terminating())(cs_game("ap", p).nash()))
    ap2 = sum(1 for p in grid if len(cs_game("ap", p).nash()) == 2)
    cch = sum(1 for p in grid if (not cs_game("cap", p).nash()) == cap_pred(p))
    ccy = sum(1 for p in grid if not cs_game("cap", p).nash())
    s2r = "\n".join(["  robustness over 243 settings (bl, bh, k, rho, u):",
                     f"    accountable planning: a pure equilibrium exists, capital concedes in every one, dynamics terminate: {apu} of 243",
                     f"      (two equilibria, (acc,con) and (org,con), where organizing is worth exactly its cost: {ap2} settings)",
                     f"    capitalism: 'no pure equilibrium' agrees with the hand-derived condition: {cch} of 243",
                     f"    capitalism: settings with no pure equilibrium (perpetual struggle): {ccy}"])
    check("§5.2 robustness over 243 parameter settings", s2r, D[2])

    # §5.3 Roemer
    def roemer(ks, Y, S, kap):
        n = len(ks); K = sum(ks); r = (Y - S) / kap
        inc = [S + r * k for k in ks]
        def v(c):
            m = len(c); j = min(F(m), F(m * K, n * kap)); return j * Y + (m - j) * S
        coal = [c for bits in range(1, 2 ** n) for c in [[i for i in range(n) if bits >> (n - 1 - i) & 1]]]
        def status(x): return "exploited" if x > 0 else ("exploiter" if x < 0 else "neutral")
        st = [status(v(c) - sum(inc[i] for i in c)) for c in coal]
        ms = [status(F(K, n) - F(sum(ks[i] for i in c), len(c))) for c in coal]
        api = v([0])
        apx = sum(1 for c in coal if v(c) > len(c) * api)
        return st, ms, inc, api, apx
    Y, S, kap = F(1), F(2, 5), F(4)
    ks1, ks2 = [0, 0, 0, 1, 2, 9], [0, 1, 1, 2, 3, 5]
    a1 = roemer(ks1, Y, S, kap); a2 = roemer(ks2, Y, S, kap)
    cnt = lambda st, x: sum(1 for z in st if z == x)
    s3 = "\n".join(["§5.3 ROEMER: EXPLOITATION AS A PROPERTY RELATION (6 agents, job needs 4 units of capital, Y = 1, S = 2/5)",
                    f"  endowments {sh(ks1)}: exploited/exploiter/neutral coalitions = {cnt(a1[0], 'exploited')}/{cnt(a1[0], 'exploiter')}/{cnt(a1[0], 'neutral')}",
                    f"    withdrawal test = mean capital below/above the social mean, all 63 coalitions: {tf(a1[0] == a1[1])}",
                    f"  endowments {sh(ks2)}: exploited/exploiter/neutral coalitions = {cnt(a2[0], 'exploited')}/{cnt(a2[0], 'exploiter')}/{cnt(a2[0], 'neutral')}",
                    f"    withdrawal test = mean capital below/above the social mean, all 63 coalitions: {tf(a2[0] == a2[1])}",
                    f"  incomes {sh(a1[2])}  vs access to social means for all: {sh(a1[3])}",
                    f"  exploited coalitions when every worker has that access: {a1[4]}"])
    check("§5.3 Roemer's withdrawal test on all coalitions", s3, D[3])
    # §5.4 collusion
    ds = lambda k, p: (1 - F(1, k)) / (1 - p)
    kbar = lambda p: next(k for k in range(1, 1001) if not ds(k, p) < 1)
    s4 = "\n".join(["§5.4 COLLUSION IN A DIVIDED GOVERNMENT (rent R = 1 shared by K secretaries; whistleblower bounty B = 1)",
                    f"  K                    : {drow(range(1, 10), 0, 7)}",
                    f"  delta*(K), no audits : {drow([ds(k, F(0)) for k in range(1, 10)], 3, 7)}",
                    f"  delta*(K), audit 1/10: {drow([ds(k, F(1, 10)) for k in range(1, 10)], 3, 7)}",
                    f"  delta*(K), audit 1/5 : {drow([ds(k, F(1, 5)) for k in range(1, 10)], 3, 7)}",
                    f"  smallest K with no sustainable collusion: audit 1/10 -> {kbar(F(1, 10))}, audit 1/5 -> {kbar(F(1, 5))}",
                    "  a single ruling party (no bounty any member can claim): collusion sustainable at every delta"])
    check("§5.4 collusion thresholds delta*(K)", s4, D[4])

    # §5.5 QV
    def ballot(th, B):
        mx = isqrt(B); best = None; bu = None
        for v in product(range(mx + 1), repeat=len(th)):
            if sum(x * x for x in v) <= B:
                u = sum(a * b for a, b in zip(th, v))
                if best is None or u > bu:
                    best, bu = list(v), u
        return best
    pop = [(90, [2, 6, 1]), (5, [1, 1, 8]), (5, [9, 1, 1])]
    tally = [sum(n * ballot(th, 36)[c] for n, th in pop) for c in range(3)]
    plur = [0, 0, 0]
    for n, th in pop:
        plur[th.index(max(th))] += n
    def market(os):
        w = (1 - os) * 975 / 95; o = os * 975 / 5
        earners = [(90, w, [2, 6, 1]), (5, o, [1, 1, 8]), (5, w, [9, 1, 1])]
        return [sum(n * m * F(th[c], sum(th)) for n, m, th in earners) for c in range(3)]
    shares = lambda v: [F(x) / sum(v) for x in v]
    A = [[F(1, 5), F(1, 5), F(1, 10)], [F(1, 10), F(1, 5), F(0)], [F(0), F(0), F(0)]]; l = [F(1), F(2), F(1)]
    def jobs(direction):
        lam = lvalues(A, l); d = [F(1000) / dot(lam, direction) * x for x in direction]
        return [a * b for a, b in zip(l, gross(A, d))]
    mu, mc = market(F(973, 1000)), market(F(242, 1000))
    s5 = "\n".join(["§5.5 QUADRATIC VOTING AND DEMOCRATIC FINAL DEMAND (categories: investment, necessities, luxuries; B = 36 credits)",
                    f"  ballots: workers (2,6,1) -> {sh(ballot([2, 6, 1], 36))}   owners (1,1,8) -> {sh(ballot([1, 1, 8], 36))}   green minority (9,1,1) -> {sh(ballot([9, 1, 1], 36))}",
                    f"  QV tally (90/5/5 voters): {sh(tally)}   shares {drow(shares(tally), 3, 7)}",
                    f"  one person one vote (plurality per voter): {sh(plur)}",
                    f"  market demand shares, uncapped capitalism: {drow(shares(mu), 3, 7)}",
                    f"  market demand shares, asset cap 60       : {drow(shares(mc), 3, 7)}",
                    f"  jobs by sector for 1000 hours, QV demand        : {drow(jobs(tally), 1, 8)}",
                    f"  jobs by sector for 1000 hours, uncapped market  : {drow(jobs(mu), 1, 8)}",
                    f"  the green minority (5% of voters) gets a share of the votes: {dec(F(30, sum(tally)), 3)}"])
    check("§5.5 QV ballots, tallies, market demand, jobs by sector", s5, D[5])

    # §5.6 prospect theory
    KK, LAM = F(10), F(9, 4)
    v = lambda x: x - x * x / (2 * KK) if x >= 0 else LAM * (x + x * x / (2 * KK))
    U = lambda d, lot: sum(p * v(d + x) for p, x in lot)
    MODL = [(F(1), F(1))]; RADL = [(F(1, 4), F(6)), (F(3, 4), F(-2))]
    choice = lambda d: "radical" if U(d, RADL) > U(d, MODL) else "moderate"
    dsg = [F(k, 4) for k in range(-32, 13)]
    cs_ = [choice(d) for d in dsg]
    single = all(not (cs_[i] == "moderate" and cs_[i + 1] == "radical") for i in range(len(cs_) - 1))
    fm = next(d for d in dsg if choice(d) == "moderate")
    def rshare(strata): return F(sum(w for w, d in strata if choice(d) == "radical"), sum(w for w, d in strata))
    strata = lambda sh_: [(20, 1 + sh_), (30, -6 + sh_), (25, -3 + sh_), (20, 0 + sh_), (5, 2 + sh_)]
    cold = [(20, 2), (30, 1), (25, 1), (20, 1), (5, 2)]
    s6 = "\n".join(["§5.6 PROSPECT THEORY AND THE RADICAL COALITION (K = 10, loss aversion 9/4)",
                    f"  moderate: sure +1;  radical: +6 w.p. 1/4, -2 w.p. 3/4  (expected values {sh(F(1))} and {sh(F(0))})",
                    f"  choices from D = -8 to +3 in steps of 1/4 are single-crossing: {tf(single)}",
                    f"  on the quarter-unit grid the radical gamble is chosen exactly when D <= {sh(fm - F(1, 4))}  (first moderate at D = {sh(fm)}); exact threshold -5.3994, me-extremes X4",
                    f"  radical share, strata of the post (falling -6/-3, rising +1/+2):  {dec(rshare(strata(0)), 3)}",
                    f"  ... same strata measured against an aspiration 3 above:          {dec(rshare(strata(-3)), 3)}",
                    f"  ... Cold-War pattern (every stratum rising):                     {dec(rshare(cold), 3)}"])
    check("§5.6 prospect-theory threshold and radical shares", s6, D[6])

    # §5.7 patronage
    def pat_run(thr, thl, p):
        s_ = F(1, 2)
        for _ in range(p["t"]):
            rr = p["br"] + p["rho"] * s_; rl = p["bl"] + p["rho"] * (1 - s_)
            ar = rr * (p["a"] * thr + p["m"] * (1 - thr)); al = rl * (p["a"] * thl + p["m"] * (1 - thl))
            s_ = rnd(s_ + (ar / (ar + al) - s_) / 2, 1000)
        return s_
    pp1 = dict(br=F(2), bl=F(2), rho=F(4), a=F(3), m=F(1), t=12); pp2 = dict(pp1, br=F(3), bl=F(1))
    ths = [F(0), F(1, 4), F(1, 2), F(3, 4), F(1)]
    rows = [drow([pat_run(x, y, pp1) for y in ths], 3, 7) + "   " + drow([pat_run(x, y, pp2) for y in ths], 3, 7) for x in ths]
    pg = Game([ths, ths], lambda pr: (pat_run(pr[0], pr[1], pp2), 1 - pat_run(pr[0], pr[1], pp2)))
    s7 = "\n".join(["§5.7 PATRONAGE COMPETITION (R's membership share after 12 periods; rows R's job share, columns L's)",
                    "  equal base funding 2:2                   capital-funded R, 3:1"] + rows +
                   [f"  pure Nash equilibria (3:1): {sh([prof(x) for x in pg.nash()])}   'all jobs' weakly dominant for R / L: {tf(pg.weakly_dominant(0, F(1)))} / {tf(pg.weakly_dominant(1, F(1)))}",
                    f"  R's share if L creates no jobs while R does (3:1): {dec(pat_run(F(1), F(0), pp2), 3)}   if both do: {dec(pat_run(F(1), F(1), pp2), 3)}"])
    check("§5.7 patronage table, equilibrium, dominance", s7, D[7])
    check("me-games.pal: all assertions pass", asserts_ok(out), (20, 0))

# ============================================================================
# PART IV -- the integrated economy (me-economy, me-regimes, me-loops)
# ============================================================================
PE = dict(N=F(100), s=F(2, 5), bl=F(1, 5), bh=F(1, 2), k=F(1, 20), rho=F(1, 20), rext=F(1, 10), g=F(4, 5), pen=F(1, 10),
          rmin=F(1, 25), sc=F(3, 5), dep=F(3, 100), crash=F(1, 10), mu=F(1, 100), gam=F(1, 40), pistar=F(1, 50), shock1=40, shock2=41,
          shockpi=F(1, 10), coldend=30, repl=F(9, 10), phi=F(1, 5), psi=F(1, 20), asp=F(1, 5), scale=F(20), yp=F(6, 5), theta=F(60),
          dgrow=F(1, 50), L0=F(80), c0=F(4, 5), prho=F(4))
PT_K, PT_LAM = F(10), F(9, 4)
def pt_v(x): return x - x * x / (2 * PT_K) if x >= 0 else PT_LAM * (x + x * x / (2 * PT_K))
def pt_radical(d):
    rad = F(1, 4) * pt_v(d + 6) + F(3, 4) * pt_v(d - 2)
    return rad > pt_v(d + 1)
def clampv(x, lo, hi): return max(lo, min(hi, x))


def pe_init(reg):
    return dict(reg=reg, t=0, K=F(30) if reg == "ap" else F(270), kap=F(3), A=F(1), ce=F(4, 5), sR=F(1, 2), gov=0, cb=F(4, 5), t0=0)


def beta_and_flight(reg, gp):
    g = cs_game(reg, gp); ne = g.nash()
    if not ne:
        core = Game([["acc", "org"], ["con", "rep"]], lambda pr: cs_pay(reg, gp, pr[0], pr[1]))
        pp, q = mixed2(core, "acc", "org", "con", "rep")
        return gp["bl"] + (1 - pp) * q * (gp["bh"] - gp["bl"]), 0
    w, c = ne[0]
    if c == "flt":
        return gp["bl"], 1
    if w == "acc" or (reg == "cap" and c == "rep"):
        return gp["bl"], 0
    return gp["bh"], 0


def pat1(thr, thl, br, bl, rho, a, m, s_):
    rr = br + rho * s_; rl = bl + rho * (1 - s_)
    ar = rr * (a * thr + m * (1 - thr)); al = rl * (a * thl + m * (1 - thl))
    return rnd(s_ + (ar / (ar + al) - s_) / 2, 1000)


NODE_VARS = ["E", "U", "B", "W", "Inf", "Ce", "Pi", "Rr", "I", "K2", "Asp", "Rad", "Gov2", "SR2"]


def pe_chain(S, p, hook=None):
    """one period as an equation chain; hook = (x, d, base, frozen)"""
    V = dict(S)
    if hook and hook[0] in V:
        V[hook[0]] = V[hook[0]] + hook[1]
    mode = "cap" if (V["reg"] == "cold" and V["t"] >= p["coldend"]) else V["reg"]
    V["mode"] = mode
    def eq(name, val):
        V[name] = val
        if hook:
            x, d, base, frozen = hook
            if name == x:
                V[name] = V[name] + d
            elif name in frozen:
                V[name] = base[name]
    N = p["N"]
    if mode == "ap":
        eq("E", min(N, V["K"] / V["kap"]) if p["yp"] > p["g"] else F(0))
        eq("U", F(0))
    else:
        eq("E", min(N, V["K"] / V["kap"]))
        eq("U", 1 - V["E"] / N)
    gp = dict(p); gp["u"] = V["U"]
    if V["gov"] >= 1 and mode != "ap":
        gp["bl"] = p["bl"] / 2; gp["bh"] = p["bh"] / 2
    creg = "ap" if mode == "ap" else "cap"
    b, fl = beta_and_flight(creg, gp)
    eq("B", b)
    V["Fl"] = beta_and_flight(creg, gp)[1]
    if mode == "ap":
        eq("Inf", F(0))
        eq("W", w_ap(V["B"], p["g"]))
        bundle = V["cb"] * (1 + p["dgrow"]) ** (V["t"] - V["t0"])
        V["Lreq"] = (p["L0"] / p["c0"]) * bundle / V["A"]
        eq("Ce", bundle * min(F(1), (N - V["E"]) / V["Lreq"]))
        V["Cu"] = V["Ce"]
        eq("Pi", (1 - V["B"]) * (p["yp"] - p["g"]) * V["E"])
    else:
        eq("Inf", p["shockpi"] if p["shock1"] <= V["t"] <= p["shock2"] else p["pistar"])
        wc = w_cap(V["B"], V["U"], p["s"])
        if mode == "cold":
            eq("W", max(wc, V["ce"] * (1 + p["gam"] / 2) / V["A"])); V["Cu"] = p["repl"] * V["ce"]; eq("Ce", V["W"] * V["A"])
        else:
            eq("W", wc); V["Cu"] = p["s"]; eq("Ce", V["W"] * V["A"] / (1 + V["Inf"]))
        eq("Pi", (1 - V["W"]) * V["E"])
    eq("Rr", V["Pi"] / V["K"] if V["K"] > 0 else F(0))
    V["Cr"] = 0 if mode == "ap" else (1 if (V["Rr"] < p["rmin"] or V["Fl"] == 1) else 0)
    eq("I", F(0) if V["Cr"] == 1 else p["sc"] * V["Pi"])
    if mode == "ap":
        eq("K2", min(p["theta"], V["K"] * (1 - p["dep"]) + V["I"]))
    else:
        eq("K2", V["K"] * (1 - p["dep"]) + V["I"] - V["Cr"] * p["crash"] * V["K"])
    eq("Asp", V["ce"] * (1 + p["asp"] * V["sR"]))
    pos = lambda c: clampv(p["scale"] * (c - V["Asp"]) / V["Asp"], F(-8), F(8))
    if mode == "ap":
        eq("Rad", F(1) if pt_radical(pos(V["Ce"])) else F(0))
    else:
        eq("Rad", (1 - V["U"]) * (1 if pt_radical(pos(V["Ce"])) else 0) + V["U"] * (1 if pt_radical(pos(V["Cu"])) else 0))
    eq("Gov2", 1 if V["Rad"] > F(1, 2) else 0)
    thl = 0 if mode == "cap" else 1
    blf = p["psi"] * V["W"] * (N if mode == "ap" else V["E"])
    a = F(1) if mode == "ap" else 3 * (1 + V["U"])
    eq("SR2", pat1(1, thl, p["phi"] * V["Pi"], blf, p["prho"], a, F(1), V["sR"]))
    ec = clampv((N - V["E"] - V["Lreq"]) / V["Lreq"], F(-1), F(1)) if mode == "ap" else clampv((V["Rr"] - p["rmin"]) / p["rmin"], F(-1), F(1))
    po = 2 * (F(1, 2) - V["Rad"])
    V["econ"], V["pol"], V["Phi"] = ec, po, min(ec, po)
    return V


def pe_next(S, V, p):
    S2 = dict(S)
    S2.update(t=S["t"] + 1, K=rnd(V["K2"], 10 ** 6), kap=rnd(S["kap"] * (1 + p["mu"]), 10 ** 6), A=rnd(S["A"] * (1 + p["gam"]), 10 ** 6),
              ce=rnd(V["Ce"], 10 ** 6), sR=V["SR2"], gov=V["Gov2"])
    return S2


def pe_run(reg, p, n):
    S = pe_init(reg); rows = []
    for _ in range(n):
        V = pe_chain(S, p); rows.append(V); S = pe_next(S, V, p)
    return S, rows


def hist_view(rows, every):
    out = ["     t mode      u   beta      w      r cr     ce    rad     sR gov    Phi"]
    for V in rows:
        if V["t"] % every == 0:
            out.append(padl(str(V["t"]), 6) + padl(V["mode"], 5) + padl(dec(V["U"], 3), 7) + padl(dec(V["B"], 3), 7) + padl(dec(V["W"], 3), 7)
                       + padl(dec(V["Rr"], 3), 7) + padl(str(V["Cr"]), 3) + padl(dec(V["Ce"], 3), 7) + padl(dec(V["Rad"], 3), 7)
                       + padl(dec(V["sR"], 3), 7) + padl(str(V["gov"]), 4) + padl(dec(V["Phi"], 3), 7))
    return "\n".join(out)


def part4():
    print("PART IV  the integrated economy (me-economy, me-regimes, me-loops)")
    # --- the self-rewriting simulation ---
    import shutil, tempfile
    tmpd = tempfile.mkdtemp()
    tf_ = os.path.join(tmpd, "e.pal")
    shutil.copy(os.path.join(ROOT, "examples", "me-economy.pal"), tf_)
    with open(tf_) as fh:
        txt = fh.read().replace('import "../lib/', 'import "')
    with open(tf_, "w") as fh:
        fh.write(txt)
    seq = []
    for _ in range(7):
        o = subprocess.run([BIN, tf_], capture_output=True, text=True, env=ENV).stdout
        m = re.search(r"(WROTE|FIXED POINT)", o)
        seq.append(m.group(1) if m else "?")
        if "assert: PASS" not in o:
            seq.append("ASSERT-FAIL")
    check("me-economy.pal: 6 x WROTE, then FIXED POINT, invariants hold every run", seq, ["WROTE"] * 6 + ["FIXED POINT"])
    final = open(tf_).read()
    mm = re.search(r"^main = (.*)$", final, re.M).group(1)
    got = re.findall(r"\(h (\d+) (\w+) (\S+) (\S+) (\S+) (\S+) (\d+) (\d+)\)", mm)
    want = []
    for reg in ("cap", "cold", "ap"):
        _, rows = pe_run(reg, PE, 60)
        for V in rows:
            want.append((str(V["t"]), V["mode"], sh(rnd(V["U"], 10000)), sh(rnd(V["Rad"], 10000)), sh(rnd(V["Phi"], 10000)), sh(rnd(V["Ce"], 10000)), str(V["gov"]), str(V["Cr"])))
    check("me-economy.pal: the 180 history rows written into the quine", got, want)

    # --- me-regimes ---
    out = run_pal("me-regimes.pal"); D = displays(out)
    _, c = pe_run("cap", PE, 60); _, w = pe_run("cold", PE, 60); _, a = pe_run("ap", PE, 60)
    incr = lambda xs: all(xs[i + 1] > xs[i] for i in range(len(xs) - 1))
    decr = lambda xs: all(xs[i + 1] < xs[i] for i in range(len(xs) - 1))
    def plan_check(t):
        A0 = [[F(1, 5), F(1, 5), F(1, 10)], [F(1, 10), F(1, 5), F(0)], [F(0), F(0), F(0)]]
        At = (1 + PE["gam"]) ** t; lt = [x / At for x in [F(1), F(2), F(1)]]
        dirv = [F(300), F(450), F(120)]; lam0 = lvalues(A0, [F(1), F(2), F(1)])
        H = (PE["L0"] / PE["c0"]) * F(4, 5) * F(51, 50) ** t
        d = [H / dot(lam0, dirv) * x for x in dirv]
        x = gross(A0, d)
        err = max(abs(u - v) for u, v in zip(x, gross_iter(A0, d, 30)))
        return dot(lvalues(A0, lt), d) == dot(lt, x), err
    pcs = [plan_check(t) for t in range(60)]
    s1 = "\n".join(["§6.1 BASELINE (60 periods; every 5th shown)", "CAPITALISM", hist_view(c, 5),
                    "CAPITALISM UNDER THE COLD WAR (ends at period 30)", hist_view(w, 5), "ACCOUNTABLE PLANNING", hist_view(a, 5),
                    f"  capitalism: unemployment rises every period, {dec(c[0]['U'], 3)} -> {dec(c[59]['U'], 3)}; wage share falls every period: {tf(incr([V['U'] for V in c]) and decr([V['W'] for V in c]))}",
                    f"  capitalism: profit rate >= r_min (no crisis) in every period: {tf(all(V['Rr'] >= F(1, 25) for V in c))}",
                    f"  capitalism: the inflation shock cuts the living standard (t=40 < t=39): {tf(c[40]['Ce'] < c[39]['Ce'])}",
                    f"  Cold War: radical vote 0 while it lasts; equal to unemployment after: {tf(all(V['Rad'] == 0 for V in w[:30]))} {tf(all(V['Rad'] == V['U'] for V in w[31:]))}",
                    f"  planning: u = 0, radical vote 0, living standard rising every period: {tf(all(V['U'] == 0 and V['Rad'] == 0 for V in a) and incr([V['Ce'] for V in a]))}",
                    f"  planning: lambda.d = l.x exactly and residual < 1/1000 after 30 passes, every period: {tf(all(ok and e < F(1, 1000) for ok, e in pcs))}",
                    f"  ... largest residual: {dec(max(e for ok, e in pcs), 8)}"])
    check("§6.1 the three baseline trajectories (60 periods) and their properties", s1, D[0])
    ST = dict(PE, scale=F(30), asp=F(2, 5))
    _, sc = pe_run("cap", ST, 60); _, sw = pe_run("cold", ST, 60); _, sa = pe_run("ap", ST, 60)
    radp = lambda rows: sum(1 for V in rows if V["gov"] == 1)
    first = lambda rows: next((V["t"] for V in rows if V["gov"] == 1), "none")
    s2 = "\n".join(["§6.2 STRESS SCENARIO: loss sensitivity 30, aspiration messaging 2/5 (every 3rd period to 45)",
                    "CAPITALISM", hist_view(sc[:46], 3), "COLD WAR, ENDS AT 30", hist_view(sw[:46], 3), "ACCOUNTABLE PLANNING", hist_view(sa[:46], 3),
                    f"  radical government in power (periods of 60): capitalism {radp(sc)} from t={first(sc)};  Cold War {radp(sw)} from t={first(sw)};  planning {radp(sa)}"])
    check("§6.2 the stress scenario", s2, D[1])
    lines = ["§6.3 SENSITIVITY: 27 settings (loss scale x inflation shock x aspiration); per regime: radical-gov periods, first, min Phi",
             "  scale  shock   asp     cap: n  first   minPhi    cold: n first   minPhi      ap: n first   minPhi"]
    aprob = cnw = capr = cre = cinv = 0
    for scv in (20, 30, 40):
        for shv in (F(1, 20), F(1, 10), F(1, 5)):
            for aspv in (F(1, 10), F(1, 5), F(2, 5)):
                pp = dict(PE, scale=F(scv), shockpi=shv, asp=aspv)
                res = {}
                for reg in ("cap", "cold", "ap"):
                    _, rows = pe_run(reg, pp, 60)
                    res[reg] = (radp(rows), first(rows), min(V["Phi"] for V in rows), min(V["Phi"] for V in rows[1:]), max(V["Rad"] for V in rows[1:]), max(V["U"] for V in rows))
                cell = lambda r: padl(str(r[0]), 4) + padl(str(r[1]), 6) + padl(dec(r[2], 3), 8) + "  "
                lines.append(padl(str(scv), 5) + padl(sh(shv), 6) + padl(sh(aspv), 6) + "   " + cell(res["cap"]) + cell(res["cold"]) + cell(res["ap"]))
                ra = res["ap"]; aprob += ra[5] == 0 and ra[4] == 0 and ra[3] > 0
                cnw += res["cold"][0] <= res["cap"][0]; capr += res["cap"][0] > 0
                cre += res["cold"][1] != "none" and res["cold"][1] < 30; cinv += res["cap"][2] <= 0
    lines += [f"  planning in all 27: u = 0, radical vote 0 from period 1, Phi > 0 from period 1: {tf(aprob == 27)}",
              f"  Cold War never has more radical-government periods than capitalism: {tf(cnw == 27)}",
              f"  settings with a radical government: capitalism {capr} of 27;  Cold War before its end: {cre}",
              f"  settings in which capitalism reaches Phi <= 0 (phase inversion): {cinv}"]
    check("§6.3 the 27-setting sensitivity grid (81 runs of 60 periods)", "\n".join(lines), D[2])
    check("me-regimes.pal: all assertions pass", asserts_ok(out), (13, 0))

    # --- me-loops ---
    out = run_pal("me-loops.pal"); D = displays(out)
    nodes = "K Kap E U B W Inf Ce Pi Rr I Asp Rad Gov SR".split()
    edges = [("K", "E", 1), ("Kap", "E", -1), ("E", "U", -1), ("U", "B", -1), ("U", "W", -1), ("B", "W", 1), ("W", "Ce", 1), ("Inf", "Ce", -1),
             ("W", "Pi", -1), ("E", "Pi", 1), ("Pi", "Rr", 1), ("K", "Rr", -1), ("Rr", "I", 1), ("Pi", "I", 1), ("I", "K", 1), ("SR", "Asp", 1),
             ("Ce", "Rad", -1), ("U", "Rad", 1), ("Asp", "Rad", 1), ("Rad", "Gov", 1), ("Gov", "B", -1), ("Pi", "SR", 1), ("U", "SR", 1), ("W", "SR", -1)]
    def cycles(es):
        idx = {n: i for i, n in enumerate(nodes)}; outc = []
        def dfs(s_, cur, path):
            for a_, b_, _ in es:
                if a_ != cur:
                    continue
                if b_ == s_:
                    outc.append(list(path))
                elif idx[b_] > idx[s_] and b_ not in path:
                    dfs(s_, b_, path + [b_])
        for n in nodes:
            dfs(n, n, [n])
        sign = {(a_, b_): sg for a_, b_, sg in es}
        res = []
        for cyc in outc:
            pol = 1
            for a_, b_ in zip(cyc, cyc[1:] + cyc[:1]):
                pol *= sign[(a_, b_)]
            res.append(("R" if pol > 0 else "B", cyc))
        return res
    view = lambda cs: "\n".join(f"{k}{padl(str(len(cyc)), 3)}  " + " -> ".join(cyc + cyc[:1]) for k, cyc in cs)
    cs_ = cycles(edges)
    s1 = "\n".join(["§7.1 CAPITALISM'S CAUSAL-LOOP DIAGRAM: 15 variables, 24 signed edges (lib/polecon.pal)",
                    f"  elementary cycles: {len(cs_)}   reinforcing {sum(1 for k, _ in cs_ if k == 'R')}   balancing {sum(1 for k, _ in cs_ if k == 'B')}", view(cs_)])
    check("§7.1 the 14 elementary cycles and their polarities", s1, D[0])
    IV = {"K": ("K", "K2", F(10)), "Kap": ("kap", "kap", F(1, 10)), "E": ("E", "E", F(5)), "U": ("U", "U", F(1, 20)), "B": ("B", "B", F(1, 20)),
          "W": ("W", "W", F(1, 20)), "Inf": ("Inf", "Inf", F(1, 20)), "Ce": ("Ce", "Ce", F(1, 5)), "Pi": ("Pi", "Pi", F(5)), "Rr": ("Rr", "Rr", F(1, 50)),
          "I": ("I", "I", F(5)), "Asp": ("Asp", "Asp", F(1, 5)), "Rad": ("Rad", "Rad", F(3, 5)), "Gov": ("gov", "Gov2", F(1)), "SR": ("sR", "SR2", F(1, 5))}
    def probe(a_, b_, S, pp):
        x, _, d = IV[a_]; y = IV[b_][1]
        Vb = pe_chain(S, pp); frozen = [z for z in NODE_VARS if z != x and z != y]
        Vh = pe_chain(S, pp, (x, d, Vb, frozen))
        return Vh[y] - Vb[y]
    def at(reg, pp, t):
        S = pe_init(reg)
        for _ in range(t):
            S = pe_next(S, pe_chain(S, pp), pp)
        return S
    sq = pe_init("cap"); sq.update(kap=F(9, 2), K=F(396)); fu = pe_init("cap"); fu.update(K=F(285))
    cb = [(at("cap", PE, 0), PE), (at("cap", PE, 15), PE), (at("cap", PE, 30), PE), (at("cap", PE, 45), PE), (at("cold", PE, 10), PE),
          (at("cap", ST, 0), ST), (at("cap", ST, 1), ST), (at("cap", ST, 10), ST), (sq, PE), (fu, PE)]
    apc = at("ap", PE, 15); apc["K"] = F(60)
    ab = [(at("ap", PE, 0), PE), (at("ap", PE, 15), PE), (at("ap", PE, 30), PE), (at("ap", PE, 45), PE), (apc, PE)]
    lines = ["§7.2 EVERY EDGE CHECKED ON THE EQUATION CHAIN (partial finite differences)",
             "                       deltas at: cap0   cap15   cap30   cap45  cold10     st0     st1    st10 squeeze    full"]
    okn = 0; fails = []
    for a_, b_, sg in edges:
        ds = [probe(a_, b_, S, pp) for S, pp in cb]
        right = all((x > 0) if sg > 0 else (x < 0) for x in ds); zero = all(x == 0 for x in ds); nw = all((x >= 0) if sg > 0 else (x <= 0) for x in ds)
        v_ = "strict" if right else ("absent" if zero else ("weak" if nw else "FAIL"))
        okn += v_ in ("strict", "weak")
        if v_ == "FAIL":
            fails.append(f"{a_}->{b_}")
        lines.append(padl(a_, 4) + " -> " + padr(b_, 4) + padl("pos" if sg > 0 else "neg", 4) + padl(v_, 7) + drow(ds, 3, 8))
    lines.append(f"  confirmed (strict or weak): {okn} of {len(edges)};  failing: {sh(fails)}")
    check("§7.2 all 24 edge probes at 10 base states (exact finite differences)", "\n".join(lines), D[1])
    alive = [e for e in edges if any(probe(e[0], e[1], S, pp) != 0 for S, pp in ab)]
    removed = [e for e in edges if e not in alive]
    ca = cycles(alive)
    s3 = "\n".join(["§7.3 THE SAME PROBES AT FIVE ACCOUNTABLE-PLANNING STATES",
                    f"  edges still present: {sh([f'{a_}->{b_}' for a_, b_, _ in alive])}",
                    f"  edges removed by the regime: {sh([f'{a_}->{b_}' for a_, b_, _ in removed])}",
                    f"  elementary cycles left: {len(ca)}   reinforcing {sum(1 for k, _ in ca if k == 'R')}   balancing {sum(1 for k, _ in ca if k == 'B')}", view(ca)])
    check("§7.3 edges and loops left under accountable planning", s3, D[2])
    check("me-loops.pal: all assertions pass", asserts_ok(out), (5, 0))
    return ST


# ============================================================================
# PART V -- examples/me-dialectics.pal
# ============================================================================
def part5():
    print("PART V  structural dialectics (me-dialectics.pal)")
    out = run_pal("me-dialectics.pal"); D = displays(out)
    def post(pr, l1, l0): return (l1 * pr) / (l1 * pr + l0 * (1 - pr))
    def diag(phi, poss, d):
        viable = phi > 0; nec = poss and viable and phi - d <= 0
        return ("instability" if nec else "stasis") if viable else ("phase-inversion" if poss else "nonviable-incumbent")
    def example(pers, tt, succ):
        lines = ["  P     Phi     cf=Phi-d        diagnosis   post.  warr.   syn."]
        for t, phi, poss, d, pr, l1, l0, pc in pers:
            dg = diag(phi, poss, d); po = post(pr, l1, l0) if pr is not None else None
            warr = po is not None and dg in ("instability", "phase-inversion") and po >= pc
            syn = warr and t == tt and succ[0] > 0
            lines.append("  P" + padr(str(t), 3) + padl(dec(phi, 3), 8) + padl(dec(phi - d, 3), 8) + padl(dg, 21)
                         + padl(dec(po, 3) if po is not None else "-", 8) + padl(tf(warr), 7) + padl(tf(syn), 7))
        for i, x in enumerate(succ):
            lines.append("  P" + padr(str(tt + 1 + i), 3) + padl(dec(x, 3), 8) + "      successor (current state)")
        return lines
    ex1 = [(0, F(17, 20), False, 0, None, 0, 0, F(11, 20)), (1, F(3, 4), False, 0, None, 0, 0, F(11, 20)), (2, F(11, 20), False, 0, None, 0, 0, F(11, 20)),
           (3, F(7, 20), True, 0, None, 0, 0, F(11, 20)), (4, F(3, 20), True, F(1, 4), None, 0, 0, F(11, 20)), (5, F(-1, 20), True, F(2, 5), F(2, 5), F(3, 4), F(9, 50), F(11, 20))]
    ex2 = [(3, F(1, 10), False, 0, None, 0, 0, F(3, 5)), (4, F(-1, 20), True, F(1, 10), None, 0, 0, F(3, 5)), (5, F(-3, 20), True, F(1, 5), F(1, 2), F(71, 100), F(46, 100), F(3, 5))]
    ex3 = [(5, F(1, 20), True, F(1, 5), None, 0, 0, F(3, 5)), (6, F(-3, 20), True, F(7, 20), F(1, 2), F(81, 100), F(17, 100), F(3, 5))]
    s1 = "\n".join(["§8.1 THE POST'S THREE EXAMPLES, RECOMPUTED", "  hunting-and-gathering -> cultivation"] + example(ex1, 5, [F(1, 5), F(9, 50), F(4, 25)])
                   + ["  captive-supply-dependent coercion -> alternative labour institution"] + example(ex2, 5, [F(3, 20), F(13, 100), F(3, 25)])
                   + ["  serfdom (Domar constraint) -> capitalist tenancy"] + example(ex3, 6, [F(1, 4), F(23, 100)])
                   + ["  the post's verification list holds on all three runs: true"])
    check("§8.1 the post's three examples (diagnoses, posteriors, warrant, synthesis)", s1, D[0])
    ns = [F(3, 100), F(1, 40), F(1, 50), F(3, 200), F(1, 100), F(1, 200), 0, 0, 0]
    dk = [F(1, 50), F(1, 25), F(13, 200), F(19, 200), F(13, 100), F(381, 2000), F(47, 200), F(11, 40), F(31, 100)]
    pd = lambda g: [F(1, 2) * n + g - F(1, 100) - k + F(3, 20) for n, k in zip(ns, dk)]
    p02, p0 = pd(F(1, 5)), pd(F(0))
    s2 = "\n".join(["§8.2 CAPITALISM AND DEMOGRAPHY (incumbent viability only; no candidate)",
                    f"  P          : {drow(range(9), 0, 7)}", f"  Phi, g=0.20: {drow(p02, 3, 7)}", f"  Phi, g=0   : {drow(p0, 3, 7)}",
                    f"  g = 0.20 viable through P8: {tf(all(x > 0 for x in p02))};  g = 0 first non-viable at P{next(i for i, x in enumerate(p0) if x <= 0)}"])
    check("§8.2 capitalism and demography (the post's stated values)", s2, D[1])
    ST = dict(PE, scale=F(30), asp=F(2, 5)); MS = dict(PE, scale=F(30), shockpi=F(1, 10), asp=F(1, 5))
    def states(reg, pp, n):
        S = pe_init(reg); out_ = []
        for _ in range(n):
            out_.append(S); S = pe_next(S, pe_chain(S, pp), pp)
        return out_
    def per(S, pp):
        phi = pe_chain(S, pp)["Phi"]
        mode = "cap" if (S["reg"] == "cold" and S["t"] >= pp["coldend"]) else S["reg"]
        d = phi - pe_chain(dict(S, reg="cap"), pp)["Phi"] if mode == "cold" else F(0)
        return S["t"], phi, S["gov"] == 0, d
    def convert(S, pp):
        V = pe_chain(S, pp); avg = rnd((1 - V["U"]) * V["Ce"] + V["U"] * V["Cu"], 10 ** 6)
        return dict(reg="ap", t=S["t"], K=min(S["K"], pp["theta"]), kap=S["kap"], A=S["A"], ce=avg, sR=S["sR"], gov=0, cb=avg, t0=S["t"])
    letter = {"stasis": "s", "instability": "I", "phase-inversion": "P", "nonviable-incumbent": "n"}
    def scen(name, reg, pp, synth):
        sts = states(reg, pp, 60); pers = [per(S, pp) for S in sts]
        seq = "".join(letter[diag(phi, poss, d)] for t, phi, poss, d in pers)
        mind = min(d for t, phi, poss, d in pers)
        if not synth:
            sv = "no phase inversion: no transition is warranted"
        else:
            t1 = next(t for t, phi, poss, d in pers if phi <= 0 and poss)
            S1 = pe_next(sts[t1], pe_chain(sts[t1], pp), pp); A_ = convert(S1, pp); succ = []
            for _ in range(5):
                V = pe_chain(A_, pp); succ.append(V["Phi"]); A_ = pe_next(A_, V, pp)
            sv = f"phase inversion at t={t1}; successor Phi from t+1: {drow(succ, 3, 7)}   synthesis: {tf(succ[0] > 0)}"
        return ["  " + padr(name, 26) + seq, f"      min d = {dec(mind, 4)}   {sv}"]
    pc = F(11, 20); pth = pc * F(9, 50) / (pc * F(9, 50) + (1 - pc) * F(3, 4))
    s3 = "\n".join(["§8.3 THE PREDICATES ON THE INTEGRATED ECONOMY (one letter per period 0-59: s stasis, I instability, P phase inversion, n non-viable, candidate excluded)"]
                   + scen("baseline capitalism", "cap", PE, False) + scen("baseline Cold War", "cold", PE, False)
                   + scen("stress Cold War", "cold", ST, True) + scen("stress capitalism", "cap", ST, True) + scen("moderate inflation crisis", "cap", MS, True)
                   + [f"  prior needed for warrant (likelihoods 3/4, 9/50; threshold 11/20): {sh(pth)} = {dec(pth, 4)}"])
    check("§8.3 the predicates on five scenarios of the integrated economy", s3, D[2])
    check("me-dialectics.pal: all assertions pass", asserts_ok(out), (13, 0))


# ============================================================== PART VI ====
# (a) me-classical.pal: Cockshott's long-run profit-rate attractor, the
# accumulation identity of the integrated model, HWW's illustration, CE Table
# 10.1.  (b) me-selectorate.pal: the selectorate model of Bueno de Mesquita et
# al. (2003, ch. 3), from the closed forms stated in lib/selectorate.pal's
# header; square roots are exact floors to 1e-9 (math.isqrt) and every
# intermediate is rounded to 1e-9, as specified there.
K9 = 10 ** 9


def r9(x): return rnd(x, K9)


def lr_rates(w, lam, n, g, dl, L, K, T):
    out = []
    for _ in range(T):
        S = (1 - w) * (L - (g + dl) * K)
        out.append(r9(S / K))
        L, K = r9(L * (1 + n)), r9(K + lam * S - (g + dl) * K)
    return out


def part6a():
    print("PART VI(a)  classical econophysics checks (me-classical)")
    out = run_pal("me-classical.pal"); D = displays(out)
    n, g, dl, lam = F(1, 100), F(1, 50), F(1, 20), F(3, 5)
    rs = (n + g + dl) / lam
    ws = [F(1, 5), F(2, 5), F(3, 5), F(4, 5)]
    paths = {w: lr_rates(w, lam, n, g, dl, F(100), F(300), 200) for w in ws}
    lines = ["§C1 THE LONG-RUN RATE OF PROFIT IS A DEMOGRAPHIC ATTRACTOR (CE §14.3)",
             "  lam = 3/5, n = 0.01, g = 0.02, dl = 0.05;  R* = (n+g+dl)/lam = 2/15 = 0.13333 for every wage share",
             "  profit rate R_t at          t=0      t=10      t=50     t=100     t=199"]
    for w in ws:
        ps = paths[w]
        lines.append("  w = " + padl(dec(w, 1), 3) + "   " + drow([ps[0], ps[10], ps[50], ps[100], ps[199]], 5, 9))
    near = all(abs(paths[w][-1] - rs) < F(1, 1000) for w in ws)
    mono = all(all(abs(b - rs) <= abs(a - rs) for a, b in zip(paths[w], paths[w][1:])) for w in ws)
    lines.append("  |R_199 - R*| < 1/1000 for every w: " + tf(near) + ";  |R_t - R*| never increases: " + tf(mono))
    lines += ["", "  w = 3/5; limit = max(R*, -(1-w)(g+dl)): capital cannot shrink faster than it depreciates",
              "  scenario                                  n      g     dl   lam        R*     limit     R_299"]
    scen = [("fast population growth", F(1, 20), F(1, 50), F(1, 20), F(3, 5)), ("slow growth", F(1, 100), F(1, 50), F(1, 20), F(3, 5)),
            ("stationary population (Japan)", F(0), F(1, 50), F(1, 20), F(3, 5)), ("stationary, consume more profit", F(0), F(1, 50), F(1, 20), F(3, 10)),
            ("shrinking slowly", F(-1, 100), F(0), F(1, 50), F(3, 5)), ("shrinking fast, no productivity growth", F(-1, 20), F(0), F(1, 50), F(3, 5))]
    oks = []
    for nm, n_, g_, dl_, lam_ in scen:
        w = F(3, 5)
        star = (n_ + g_ + dl_) / lam_
        lim = max(star, -(1 - w) * (g_ + dl_))
        last = lr_rates(w, lam_, n_, g_, dl_, F(100), F(300), 300)[-1]
        oks.append(abs(last - lim) < F(1, 1000))
        lines.append("  " + padr(nm, 36) + padl(dec(n_, 3), 7) + padl(dec(g_, 3), 7) + padl(dec(dl_, 3), 7) + padl(dec(lam_, 2), 6)
                     + padl(dec(star, 5), 10) + padl(dec(lim, 5), 10) + padl(dec(last, 5), 10))
    lines.append("  R_299 within 1/1000 of the limit in every scenario: " + tf(all(oks)))
    check("§C1 the attractor R* = (n+g+dl)/lam, its floor, and convergence", "\n".join(lines), D[0])
    _, rows = pe_run("cap", PE, 60)
    E = [100 * (1 - V["U"]) for V in rows]
    gap = max(abs(F(3, 5) * rows[t]["Rr"] - (E[t + 1] / E[t] * F(101, 100) - F(97, 100))) for t in range(59))
    s2 = "\n".join(["§C2 THE INTEGRATED MODEL'S CAPITALISM OBEYS THE SAME ACCUMULATION IDENTITY",
                    "  sc r_t = (E_{t+1}/E_t)(1+mu) - (1-dl), t = 0..58:  largest gap ",
                    "    " + dec(gap, 9),
                    "  steady state with constant employment: r* = (mu + dl)/sc = 1/15 = " + dec(F(1, 15), 5),
                    "  r_t < 1/15 in every period (so employment must shrink, and unemployment rise): " + tf(all(V["Rr"] < F(1, 15) for V in rows)),
                    "  r_t at t = 0, 15, 30, 45, 59: " + drow([rows[t]["Rr"] for t in (0, 15, 30, 45, 59)], 5, 8)])
    check("§C2 the accumulation identity on the integrated model's capitalism", s2, D[1])
    s3 = "§C3 HWW §5.9: profit 50% of income, capital 200%, half of profit reinvested, income constant\n  r_t = 50/(200 + 25 t), t = 0..5: " + sh([F(50, 200 + 25 * t) for t in range(6)])
    check("§C3 HWW's falling-profit illustration", s3, D[2])
    A = [[F(0), F(100, 200), F(100, 300), F(10, 40)], [F(100, 310), F(0), F(0), F(0)], [F(0), F(20, 200), F(0), F(0)], [F(10, 310), F(0), F(20, 300), F(0)]]
    l = [F(100, 310), F(45, 200), F(85, 300), F(14, 40)]
    lam_v = lvalues(A, l)

    def iters(tol):
        v, k = l, 0
        while True:
            v2 = [a + b for a, b in zip(vm(v, A), l)]; k += 1
            if max(abs(a - b) for a, b in zip(v2, v)) < tol:
                return k
            v = v2
    m = sum(lam_v) / 4
    s4 = "\n".join(["§C4 CLASSICAL ECONOPHYSICS TABLE 10.1: LABOUR (WAGE $) PER DOLLAR OF OUTPUT",
                    "  exact, industries A B C D:   " + drow(lam_v, 5, 9),
                    "  iterations to agree within 1/1000: " + str(iters(F(1, 1000))) + ";  within 1/10^6: " + str(iters(F(1, 10 ** 6))),
                    "  largest relative deviation from the mean: " + dec(max(abs((x - m) / m) for x in lam_v), 4),
                    "  value of final output (hours) = total wages (244): " + tf(dot(lam_v, [100, 100, 280, 10]) == 244)])
    check("§C4 labour values per dollar for CE Table 10.1", s4, D[3])
    check("me-classical.pal: all assertions pass", asserts_ok(out), (8, 0))


def sqrtk(x): return F(isqrt((F(x) * 10 ** 18).__floor__()), K9)
def sel_h(r): return r + 1 - F(2) / (2 - r)


def tmax(f, lo, hi, n=45):
    lo, hi = F(lo), F(hi)
    for _ in range(n):
        m1, m2 = r9(lo + (hi - lo) / 3), r9(hi - (hi - lo) / 3)
        if f(m1) < f(m2):
            lo = m1
        else:
            hi = m2
    return r9((lo + hi) / 2)


def sel_challenger(N, W, p):
    kn = F(p + W, p * W) * N
    f = lambda r: sqrtk(kn * sel_h(r)) + sqrtk(2 - r)
    rc = tmax(f, 0, 1)
    return rc, r9(f(rc))


def sel_eq(N, S, W, p, d):
    k = F(p + W, p * W)
    rc, vc = sel_challenger(N, W, p)
    dc = d * (1 - F(W, S)) / (1 - d) * F(p, p + W)
    inc_r = lambda T: tmax(lambda r: N * sel_h(r) - max(T - sqrtk(2 - r), 0) ** 2 / k, 0, 1)
    H = lambda s_: s_ * (1 + dc) - vc + sqrtk(2 - inc_r(vc - dc * s_))
    lo, hi = F(0), vc / (1 + dc)
    for _ in range(40):
        m = r9((lo + hi) / 2)
        if H(m) < 0:
            lo = m
        else:
            hi = m
    sx = r9((lo + hi) / 2)
    rl = inc_r(vc - dc * sx)
    M = r9(sx * sx / k)
    x, g = r9(W * M / (p * (p + W))), r9(p * M / (W * (p + W)))
    wout = r9(sqrtk(x) + sqrtk(2 - rl))
    return dict(W=W, S=S, rc=rc, vc=vc, rl=rl, M=M, g=g, x=x, sur=r9(N * sel_h(rl) - M), priv=F(p, p + W),
                win=r9(wout + sqrtk(g)), wout=wout, resid=r9(H(sx)))


def part6b():
    print("PART VI(b)  the selectorate model (me-selectorate)")
    out = run_pal("me-selectorate.pal"); D = displays(out)
    N, P, DD = 100000, 10000, F(9, 10)
    revmax = tmax(sel_h, 0, 1)
    rc, vc = sel_challenger(N, N, P)
    Mu = N * sel_h(rc)
    ux, ug = r9(F(N) * Mu / (P * (P + N))), r9(F(P) * Mu / (N * (P + N)))
    s1 = "\n".join(["§S1 THE BOOK'S LIMITING CASES (N = 100,000, p = 10,000; appendix to ch. 3)",
                    "  revenue-maximizing tax 2 - sqrt 2 = 0.58579 (book):   " + dec(revmax, 5),
                    "  utilitarian (W = N): tax, x, g, welfare =   " + dec(rc, 6) + "   " + dec(ux, 5) + "   " + dec(ug, 5) + "   " + dec(vc, 5),
                    "  book:                                      0.508412   1.52327   0.01523   2.57893"])
    check("§S1 the book's limiting cases (revenue maximum, utilitarian optimum)", s1, D[0])
    ws = [1, 10, 100, 500, 1000, 5000, 10000, 50000]
    ea = [sel_eq(N, N, w, P, DD) for w in ws if w <= F(N + 1, 2)]
    eb = [sel_eq(N, 2000, w, P, DD) for w in ws if w <= F(2001, 2)]
    head = "      W     W/S     rC     rL         M         g       x   priv   surplus    Vin   Vout"
    line = lambda e: (padl(str(e["W"]), 7) + padl(dec(F(e["W"], e["S"]), 4), 8) + padl(dec(e["rc"], 4), 7) + padl(dec(e["rl"], 4), 7) + padl(dec(e["M"], 1), 10)
                      + padl(dec(e["g"], 4), 10) + padl(dec(e["x"], 4), 8) + padl(dec(e["priv"], 3), 7) + padl(dec(e["sur"], 1), 10) + padl(dec(e["win"], 3), 7) + padl(dec(e["wout"], 3), 7))
    s2 = "\n".join(["§S2 THE MARKOV-PERFECT EQUILIBRIUM (N = 100,000, p = 10,000, discount 9/10)", "  universal selectorate S = N", head] + [line(e) for e in ea]
                   + ["  narrow selectorate S = 2000", head] + [line(e) for e in eb]
                   + ["  largest residual of the steady-state condition: " + dec(max(abs(e["resid"]) for e in ea + eb), 9)])
    check("§S2 equilibria across W for S = N and S = 2000", s2, D[1])
    dec_ = lambda es, f: all(f(a) > f(b) for a, b in zip(es, es[1:]))
    inc_ = lambda es, f: all(f(a) < f(b) for a, b in zip(es, es[1:]))

    def stl(es):
        return ("challenger tax falls " + tf(dec_(es, lambda e: e["rc"])) + "; incumbent tax falls " + tf(dec_(es, lambda e: e["rl"])) + "; g falls " + tf(dec_(es, lambda e: e["g"]))
                + "; x rises " + tf(inc_(es, lambda e: e["x"])) + "; private share falls " + tf(dec_(es, lambda e: e["priv"])) + "; leader's surplus falls " + tf(dec_(es, lambda e: e["sur"]))
                + "; outsider welfare rises " + tf(inc_(es, lambda e: e["wout"])))
    loyal = all(sel_eq(N, N, w, P, DD)["sur"] > sel_eq(N, 2000, w, P, DD)["sur"] and sel_eq(N, N, w, P, DD)["M"] < sel_eq(N, 2000, w, P, DD)["M"] for w in (10, 100, 1000))
    s3 = "\n".join(["§S3 COMPARATIVE STATICS (book, ch. 3) ON THE COMPUTED EQUILIBRIA, as W rises:", "  S = N:    " + stl(ea), "  S = 2000: " + stl(eb),
                    "  loyalty norm, W in {10, 100, 1000}: S = N gives the leader more and spends less than S = 2000: " + tf(loyal),
                    "  S = 2000: private goods per member RISE from W = 500 to W = 1000 (W/S -> 1/2 weakens loyalty): " + tf(eb[4]["g"] > eb[3]["g"]),
                    "  private share of the budget = p/(p+W) exactly (closed form, see the library header)"])
    check("§S3 comparative statics and the loyalty norm", s3, D[2])
    pts = [("party-state, rigged elections (Djilas's new class)", 100000, 100), ("junta or court", 2000, 100),
           ("patronage capitalism: policy bought by a donor coalition", 100000, 1000), ("majoritarian democracy / accountable planning", 100000, 50000)]
    s4 = ["§S4 THE DOCUMENTS' POLITIES AS POINTS (W, S)", "  polity                                                     priv  kept    tax  Vout"]
    for nm, S_, W_ in pts:
        e = sel_eq(N, S_, W_, P, DD)
        s4.append("  " + padr(nm, 58) + padl(dec(e["priv"], 3), 7) + padl(dec(e["sur"] / (N * sel_h(e["rl"])), 3), 7) + padl(dec(e["rl"], 3), 7) + padl(dec(e["wout"], 3), 7))
    s4.append("  priv = patronage share of spending; kept = leader's surplus / revenue; Vout = an outsider's utility")
    check("§S4 the documents' polities as points (W, S)", "\n".join(s4), D[3])
    check("me-selectorate.pal: all assertions pass", asserts_ok(out), (7, 0))


# ============================================================== PART VI(c) ==
# examples/me-extremes.pal: limits, thresholds and inflection points
def part6c():
    print("PART VI(c)  extremes, thresholds and inflection points (me-extremes)")
    out = run_pal("me-extremes.pal"); D = displays(out)
    b, sv = F(1, 5), F(2, 5)
    el = lambda u: u * ((1 - b) * b * (sv - 1)) / ((b + u * (1 - b)) * (b + (1 - b) * u * sv))
    ustar = b / ((1 - b) * sqrtk(sv))
    lo, hi = F(0), ustar
    for _ in range(40):
        m = (lo + hi) / 2
        if el(m) > F(-1, 10): lo = m
        else: hi = m
    u10 = r9((lo + hi) / 2)
    s1 = ["§X1 THE WAGE CURVE w_cap(beta = 1/5, u, s = 2/5): LIMITS AND ELASTICITY", "       u        w   e(u)=dlnw/dlnu"]
    for u in (F(1, 100), F(1, 50), F(1, 20), F(1, 10), F(1, 5), F(2, 5), F(3, 5), F(1)):
        s1.append(padl(dec(u, 3), 8) + padl(dec(w_cap(b, u, sv), 4), 9) + padl(dec(el(u), 4), 9))
    s1 += ["  limits: w(0) = " + sh(w_cap(b, F(0), sv)) + ";  w(1) = beta + (1-beta)s = " + sh(w_cap(b, F(1), sv)),
           "  elasticity = -1/10 (Blanchflower-Oswald) at u = " + dec(u10, 4),
           "  |elasticity| is largest at u* = beta/((1-beta) sqrt s) = " + dec(ustar, 4) + ", where e = " + dec(el(ustar), 4)]
    check("§X1 the wage curve's limits and elasticity", "\n".join(s1), D[0])
    def gp(u):
        g = dict(PE); g["u"] = u; return g
    def nestr(ne): return "none (cycle; mixed)" if not ne else "".join(f"{w}/{c} " for w, c in ne)
    us = [F(0), F(1, 100), F(1, 50), F(3, 100), F(1, 25), F(1, 20), F(3, 50), F(1, 10), F(1, 5), F(3, 10), F(1, 2)]
    s2 = ["§X2 THE CLASS-STRUGGLE GAME ALONG UNEMPLOYMENT (capitalism, parameters of the integrated model)", "       u  #NE   pure equilibria         beta*"]
    for u in us:
        ne = cs_game("cap", gp(u)).nash()
        s2.append(padl(dec(u, 3), 8) + padl(str(len(ne)), 5) + "   " + padr(nestr(ne), 22) + padl(dec(beta_and_flight("cap", gp(u))[0], 4), 9))
    fl = lambda u: beta_and_flight("cap", gp(u))[1] == 1
    lo, hi = F(0), F(1, 10)
    for _ in range(30):
        m = (lo + hi) / 2
        if fl(m): lo = m
        else: hi = m
    s2.append("  capital flight is the equilibrium for u up to " + dec(r9((lo + hi) / 2), 5) + ";  beta* at u = 0, 1/20, 1/10: "
              + drow([beta_and_flight("cap", gp(u))[0] for u in (F(0), F(1, 20), F(1, 10))], 4, 8))
    check("§X2 the class game's regimes along unemployment", "\n".join(s2), D[1])
    A0 = [[F(1, 5), F(1, 5), F(1, 10)], [F(1, 10), F(1, 5), F(0)], [F(0), F(0), F(0)]]; l0 = [F(1), F(2), F(1)]
    def aug(A, l, bb): return [[A[i][j] + bb[i] * l[j] for j in range(3)] for i in range(3)]
    def pfp(M, k=60):
        p = [F(1)] * 3
        for _ in range(k):
            p2 = [sum((p[i] * M[i][j] for i in range(3)), F(0)) for j in range(3)]; t = sum(p2)
            p = [rnd(x / t, 10 ** 12) for x in p2]
        return p
    def dcat(beta, j, s_, m_):
        A2 = [r[:] for r in A0]; A2[0][j] += m_; l2 = l0[:]; l2[j] = (1 - s_) * l2[j]
        bb = [F(0), beta, F(0)]; M = aug(A0, l0, bb); M2 = aug(A2, l2, bb); p = pfp(M)
        return sum(p[i] * M2[i][j] for i in range(3)) - sum(p[i] * M[i][j] for i in range(3))
    def swb(j, s_, m_):
        if dcat(F(31, 90), j, s_, m_) > 0: return None
        lo, hi = F(1, 4), F(31, 90)
        for _ in range(24):
            mid = (lo + hi) / 2
            if dcat(mid, j, s_, m_) > 0: lo = mid
            else: hi = mid
        return rnd((lo + hi) / 2, 100000)
    s3 = ["§X3 SWITCH-POINT WAGES: THE RATE beta* AT WHICH A REJECTED TECHNIQUE BECOMES COST-REDUCING (current beta = 1/4)", "   j   cut  +mach     beta*  wage rise"]
    for j, s_, m_ in [(0, F(1, 10), F(1, 20)), (0, F(1, 10), F(1, 10)), (0, F(1, 5), F(1, 10)), (1, F(1, 10), F(1, 10))]:
        bs = swb(j, s_, m_)
        s3.append(padl(str(j), 4) + padl(dec(s_, 2), 7) + padl(dec(m_, 3), 8) + padl("never" if bs is None else dec(bs, 4), 12)
                  + padl("-" if bs is None else "+" + dec(100 * (4 * bs - 1), 1) + "%", 10))
    check("§X3 switch-point wages for rejected techniques", "\n".join(s3), D[2])
    def ptv(x, kk, lam): return x - x * x / (2 * kk) if x >= 0 else lam * (x + x * x / (2 * kk))
    def radical(d, kk, lam):
        return F(1, 4) * ptv(d + 6, kk, lam) + F(3, 4) * ptv(d - 2, kk, lam) > ptv(d + 1, kk, lam)
    def thr(lam, kk=F(10)):
        best, d = None, F(-8)
        while d <= 3:
            if radical(d, kk, lam): best = d
            d += F(1, 4)
        return best
    shn = lambda x: "none" if x is None else sh(x)
    def exact(lam, kk=F(10)):
        lo, hi = 2 - kk, F(0)
        for _ in range(30):
            m = (lo + hi) / 2
            if radical(m, kk, lam): lo = m
            else: hi = m
        return rnd((lo + hi) / 2, 100000)
    s4 = ["§X4 THE RADICAL THRESHOLD AS LOSS AVERSION VARIES (K = 10; sure +1 vs +6 w.p. 1/4, -2 w.p. 3/4)", "  lambda    D_max     exact  share of strata (-6,-3,+1,+2)"]
    for lam in (F(1), F(3, 2), F(2), F(9, 4), F(5, 2), F(3), F(4), F(10), F(100)):
        share = F(sum(1 for d in (-6, -3, 1, 2) if radical(F(d), F(10), lam)), 4)
        s4.append(padl(dec(lam, 2), 7) + padl(shn(thr(lam)), 10) + padl(dec(exact(lam), 4), 10) + padl(dec(share, 3), 10))
    s4.append("  curvature K (smaller = more curved): exact threshold at lambda 9/4, at lambda 1;  11/2 - K")
    for kk in (10, 20, 40, 80):
        s4.append(padl(str(kk), 7) + padl(dec(exact(F(9, 4), F(kk)), 4), 10) + padl(dec(exact(F(1), F(kk)), 4), 10) + padl(dec(F(11, 2) - kk, 4), 10))
    check("§X4 the radical threshold against loss aversion and curvature", "\n".join(s4), D[3])
    ns = -(F(0) + F(1, 50)) * (1 + F(3, 5) * (1 - F(3, 5)))
    s5 = ["§X5 THE FLOOR OF THE LONG-RUN PROFIT RATE (w = 3/5, lam = 3/5, g = 0, dl = 0.02)",
          "  R* reaches the floor -(1-w)(g+dl) at n* = -(g+dl)(1+lam(1-w)) = " + dec(ns, 4), "        n        R*     floor     R_599"]
    for n_ in (F(-1, 100), F(-1, 50), F(-31, 1250), F(-3, 100), F(-1, 20)):
        star = (n_ + F(1, 50)) / F(3, 5); floor_ = -(1 - F(3, 5)) * F(1, 50)
        last = lr_rates(F(3, 5), F(3, 5), n_, F(0), F(1, 50), F(100), F(300), 600)[-1]
        s5.append(padl(dec(n_, 4), 9) + padl(dec(star, 5), 10) + padl(dec(floor_, 5), 10) + padl(dec(last, 5), 10))
    check("§X5 the floor of the long-run profit rate", "\n".join(s5), D[4])
    s6 = ["§X6 MECHANIZATION AND THE RESERVE ARMY IN THE INTEGRATED CAPITALISM (60 periods)", "      mu     u_0    u_59    r_59    w_59 crises  mu at which E is constant"]
    for mu in (F(0), F(1, 200), F(1, 100), F(3, 200), F(1, 50)):
        pp = dict(PE); pp["mu"] = mu
        _, rows = pe_run("cap", pp, 60)
        r59 = rows[59]["Rr"]
        s6.append(padl(dec(mu, 4), 8) + padl(dec(rows[0]["U"], 3), 8) + padl(dec(rows[59]["U"], 3), 8) + padl(dec(r59, 4), 8) + padl(dec(rows[59]["W"], 3), 8)
                  + padl(str(sum(1 for V in rows if V["Cr"] == 1)), 6) + padl(dec(F(3, 5) * r59 - F(3, 100), 4), 9))
    check("§X6 mechanization and the reserve army", "\n".join(s6), D[5])
    s7 = ["§X7 FROM EPISODE TO LOCK-IN: ASPIRATION MESSAGING (loss sensitivity 30, shock 10% at t = 40-41)", "    asp  radgov  first   sR_59"]
    for a in (F(1, 10), F(3, 20), F(1, 5), F(1, 4), F(13, 50), F(27, 100), F(7, 25), F(29, 100), F(3, 10), F(7, 20), F(2, 5)):
        pp = dict(PE); pp["scale"] = F(30); pp["asp"] = a
        _, rows = pe_run("cap", pp, 60)
        firsts = [V["t"] for V in rows if V["gov"] == 1]
        s7.append(padl(dec(a, 3), 7) + padl(str(len(firsts)), 6) + padl(str(firsts[0]) if firsts else "none", 7) + padl(dec(rows[59]["sR"], 3), 8))
    check("§X7 the aspiration level at which a crisis becomes a lock-in", "\n".join(s7), D[6])
    s8 = ["§X8 THE SELECTORATE LEADER AND PATIENCE (N = S = 100,000, W = 1,000, p = 10,000)", "  delta     rL        M   surplus    Vin"]
    for d in (F(0), F(1, 2), F(9, 10), F(99, 100)):
        e = sel_eq(100000, 100000, 1000, 10000, d)
        s8.append(padl(dec(d, 2), 6) + padl(dec(e["rl"], 4), 8) + padl(dec(e["M"], 1), 9) + padl(dec(e["sur"], 1), 10) + padl(dec(e["win"], 3), 7))
    check("§X8 the selectorate leader's surplus against patience", "\n".join(s8), D[7])
    def kbar(P):
        k = 1
        while (1 - F(1, k)) / (1 - P) < 1: k += 1
        return k
    ps = (F(1, 20), F(1, 10), F(1, 5), F(1, 3), F(1, 2))
    s9 = ["§X9 COLLUSION: SMALLEST NUMBER OF SECRETARIES THAT CANNOT SUSTAIN COLLUSION (B = R)", "  audit  K-bar  ceil(1/P)"]
    for P in ps:
        s9.append(padl(dec(P, 3), 7) + padl(str(kbar(P)), 7) + padl(str(-((-P.denominator) // P.numerator)), 8))
    s9.append("  K-bar = ceil(1/P) for every audit rate tested: " + tf(all(kbar(P) == -((-P.denominator) // P.numerator) for P in ps)))
    check("§X9 the collusion threshold in closed form", "\n".join(s9), D[8])
    A = [[F(0), F(100, 200), F(100, 300), F(10, 40)], [F(100, 310), F(0), F(0), F(0)], [F(0), F(20, 200), F(0), F(0)], [F(10, 310), F(0), F(20, 300), F(0)]]
    lam_v = lvalues(A, [F(100, 310), F(45, 200), F(85, 300), F(14, 40)]); x = [F(310), F(200), F(300), F(40)]
    mm = sum(x) / sum(a * b_ for a, b_ in zip(lam_v, x))
    mawd = sum(abs(xi - mm * li * xi) for li, xi in zip(lam_v, x)) / sum(x)
    check("§X10 price-value deviation of CE Table 10.1", "§X10 CE TABLE 10.1: MEAN ABSOLUTE WEIGHTED DEVIATION OF PRICES FROM MELT-SCALED VALUES = " + dec(mawd, 4), D[9])
    check("me-extremes.pal: all assertions pass", asserts_ok(out), (6, 0))


# ============================================================== PART VI(d) ==
# examples/me-evidence.pal: the model's counterparts of the empirical figures
def part6d():
    print("PART VI(d)  the model against empirical data (me-evidence)")
    out = run_pal("me-evidence.pal"); D = displays(out)
    el = lambda b, sv, u: u * ((1 - b) * b * (sv - 1)) / ((b + u * (1 - b)) * (b + (1 - b) * u * sv))
    A = [[F(1, 5), F(1, 5), F(1, 10)], [F(1, 10), F(1, 5), F(0)], [F(0)] * 3]; l = [F(1), F(2), F(1)]
    M = [[A[i][j] + [F(0), F(1, 4), F(0)][i] * l[j] for j in range(3)] for i in range(3)]
    lo, hi = F(-1, 2), F(8)
    for _ in range(30):
        mid = (lo + hi) / 2
        if hs(mscale(1 + mid, M)): lo = mid
        else: hi = mid
    rlo = lo
    def prices(r):
        u = vm(l, inv(msub(ident(3), mscale(1 + r, A))))
        w = dot(lvalues(A, l), [0, 10, 2]) / dot(u, [0, 10, 2])
        return [w * x for x in u]
    lam = lvalues(A, l)
    mawd = dot([abs(a - b_) for a, b_ in zip(prices(rlo), lam)], [0, 10, 2]) / dot(lam, [0, 10, 2])
    At = [[F(0), F(100, 200), F(100, 300), F(10, 40)], [F(100, 310), F(0), F(0), F(0)], [F(0), F(20, 200), F(0), F(0)], [F(10, 310), F(0), F(20, 300), F(0)]]
    lt = lvalues(At, [F(100, 310), F(45, 200), F(85, 300), F(14, 40)]); x = [F(310), F(200), F(300), F(40)]
    mm = sum(x) / sum(a * b_ for a, b_ in zip(lt, x))
    ce = sum(abs(xi - mm * li * xi) for li, xi in zip(lt, x)) / sum(x)
    _, rows = pe_run("cap", PE, 60)
    w0, w59 = rows[0]["W"], rows[59]["W"]
    ls0, ls1 = F(331, 500), F(66, 125)
    wa = F(4, 5) + F(1, 5) * (1 - F(4, 5))
    jg = lambda u: wa / w_cap(F(1, 5), u, F(2, 5)) - 1
    uc = F(1, 5) * (1 - wa) / ((1 - F(1, 5)) * (wa - F(2, 5)))
    lo, hi = uc, F(1)
    for _ in range(40):
        m = (lo + hi) / 2
        if jg(m) < F(1, 20): lo = m
        else: hi = m
    ug = rnd((lo + hi) / 2, 100000)
    lo, hi = F(0), F(2, 5)
    for _ in range(40):
        m = (lo + hi) / 2
        if el(F(1, 5), F(2, 5), m) > F(-1, 10): lo = m
        else: hi = m
    ue = rnd((lo + hi) / 2, 100000)
    pct = lambda v: dec(100 * v, 1) + "%"
    gg = 1 / (1 + F(10, 11))
    s = ["§EV THE MODEL AGAINST EMPIRICAL DATA", "  quantity                                   data        model",
         "  wage-curve elasticity at u = 5% / 10%      " + dec(F(-1, 10), 2) + "        " + dec(el(F(1, 5), F(2, 5), F(1, 20)), 3) + " / " + dec(el(F(1, 5), F(2, 5), F(1, 10)), 3),
         "    ... unemployment at which the model gives -0.10: " + dec(ue, 4),
         "  labour share, relative change              " + pct((ls1 - ls0) / ls0) + "      " + pct((w59 - w0) / w0) + "  (60 periods)",
         "    ... levels: data " + pct(ls0) + " -> " + pct(ls1) + ";  model " + dec(w0, 3) + " -> " + dec(w59, 3),
         "  price-value MAWD                           " + pct(F(23, 250)) + "        E3 at r*: " + pct(mawd) + ";  CE Table 10.1: " + pct(ce),
         "  job-guarantee wage effect                  +" + pct(F(1, 20)) + "       +" + pct(jg(F(1, 10))) + " / +" + pct(jg(F(3, 20))) + " / +" + pct(jg(F(1, 5))) + "  at u = 10/15/20%",
         "    ... no effect below u_c = " + sh(uc) + ";  +5% at u = " + dec(ug, 4),
         "  Gini of the exponential (lower) class      " + dec(F(1, 2), 3) + "       " + dec(gg, 3) + "  (geometric law, T = 10)",
         "  loss aversion lambda                       " + dec(F(9, 4), 2) + "        2.25  (input; the threshold moves by 0.18 from lambda = 2 to 10, me-extremes §X4)"]
    check("§EV the comparison table: wage curve, labour share, MAWD, job guarantee, Gini", "\n".join(s), D[0])
    check("me-evidence.pal: all assertions pass", asserts_ok(out), (4, 0))


# ============================================================== PART VIII ===
# (a) examples/me-finance.pal: credit money and a fixed stock, the wealth
# lattice, Fisher's debt deflation, capital mobility (lib/finance.pal);
# (b) examples/me-financialized.pal: the financialized regime of
# lib/polecon-fin.pal, written again here from its header's specification.
def pct8(x, d): return dec(100 * x, d) + "%"
def ilist(xs): return "-" if not xs else " ".join(str(x) for x in xs)


def cantillon8(ms, q, d):
    m = sum(ms); ms2 = [ms[0] + d] + list(ms[1:])
    p0 = m / q; b1 = min(F(q), ms2[0] / p0); left = q - b1; rest = ms2[1:]
    withv = [b1] + ([x * left / sum(rest) for x in rest] if sum(rest) > 0 else rest)
    return [a - F(q) * b_ / m for a, b_ in zip(withv, ms)]


def lat_top(z, f):
    n = 0
    while not (z ** (n + 1) <= f): n += 1
    return (2 * z) ** (n + 1) + (f - z ** (n + 1)) * 2 ** n * (1 - 2 * z) / (1 - z)


def latf_top(z, L, f):
    mass = sum(z ** k for k in range(L + 1)); wealth = sum((2 * z) ** k for k in range(L + 1))
    target = f * mass; m = F(0); w = F(0)
    for k in range(L, -1, -1):
        mk = z ** k
        if m + mk >= target: return (w + (target - m) * 2 ** k) / wealth
        m += mk; w += mk * 2 ** k
    return w / wealth


def lat_alpha(z):
    big = (1 / z) ** 1000; lo, hi = 0, 8000
    for _ in range(14):
        m = (lo + hi) // 2
        if 2 ** m <= big: lo = m
        else: hi = m
    return F(lo, 1000)


def lat_z_for(f, share):
    lo, hi = F(1, 100), F(1, 2)
    for _ in range(30):
        m = (lo + hi) / 2
        if lat_top(m, f) < share: lo = m
        else: hi = m
    return rnd((lo + hi) / 2, 10 ** 6)


def part8a():
    print("PART VIII(a)  finance on its own (me-finance)")
    out = run_pal("me-finance.pal"); D = displays(out)
    # (1) the ledger and the asset market
    sc = [(F(100), F(0))]
    for ev, x in (("loan", 50), ("pay", 30), ("loan", 80), ("repay", 20), ("pay", 40), ("loan", 10), ("repay", 50), ("repay", 70)):
        m_, l_ = sc[-1]
        sc.append((m_ + x, l_ + x) if ev == "loan" else ((m_ - x, l_ - x) if ev == "repay" else (m_, l_)))
    s1 = ["§F1 CREDIT MONEY AND THE PRICE OF A FIXED STOCK",
          "  a ledger of loans (L), payments and repayments: deposits M and loans outstanding L after each event",
          "        M        L"] + [padl(dec(m_, 0), 9) + padl(dec(l_, 0), 9) for m_, l_ in sc]
    s1.append("  new deposits = loans outstanding after every event: " + tf(all(m_ - 100 == l_ for m_, l_ in sc)))
    s1 += ["  buyers with savings 1 bid for a fixed stock at loan-to-value LTV; 10 sales a period; output fixed at 1000",
           "   LTV    price  loan/sale new money  sellers' gain  others' loss  sum 0"]
    ltvs = [F(0), F(1, 2), F(3, 4), F(4, 5), F(9, 10), F(19, 20)]
    for ltv in ltvs:
        price = 1 / (1 - ltv); loan = ltv * price; g = cantillon8([F(600), F(300), F(100)], 1000, 10 * loan)
        s1.append(padl(dec(ltv, 2), 6) + padl(dec(price, 2), 9) + padl(dec(loan, 2), 9) + padl(dec(10 * loan, 1), 10)
                  + padl(dec(g[0], 2), 10) + padl(dec(g[1] + g[2], 2), 10) + padl(tf(sum(g) == 0), 7))
    s1.append("  price = savings / (1 - LTV) on the whole grid; no house and no unit of output added: " + tf(all((1 / (1 - x)) * (1 - x) == 1 for x in ltvs)))
    check("§F1 a credit ledger; the price of a fixed stock and its Cantillon transfer", "\n".join(s1), D[0])
    # (2) the lattice
    s2 = ["§F2 THE WEALTH LATTICE: doublings p, halvings q, z = p/q",
          "  the stationary law of the infinite lattice: a Pareto tail with alpha = log2(q/p)",
          "      z     q/p   alpha  top 1%  top 10%"]
    for z in (F(1, 4), F(1, 3), F(3, 8), F(2, 5), F(9, 20), F(19, 40)):
        s2.append(padl(sh(z), 7) + padl(dec(1 / z, 3), 8) + padl(dec(lat_alpha(z), 3), 8) + padl(pct8(lat_top(z, F(1, 100)), 1), 9) + padl(pct8(lat_top(z, F(1, 10)), 1), 9))
    pis = [F(1)] + [F(0)] * 30; p_, q_ = F(1, 10), F(1, 4); L = 30
    for _ in range(300):
        new = []
        for n in range(L + 1):
            fb = p_ * pis[n - 1] if n > 0 else F(0); fa = q_ * pis[n + 1] if n < L else F(0)
            stay = pis[n] * (1 - ((p_ if n < L else 0) + (q_ if n > 0 else 0)))
            new.append(rnd(fb + fa + stay, 10 ** 12))
        pis = new
    zz = F(2, 5); norm = sum(zz ** k for k in range(L + 1))
    tvd = sum(abs(a - zz ** n / norm) for n, a in enumerate(pis)) / 2
    s2.append("  from all fortunes at the floor, 300 periods of the chain (p = 1/10, q = 1/4, levels 0..30): TV distance to z^n = " + dec(tvd, 6))
    s2 += ["  a finite lattice of L + 1 levels (a cap at 2^L): share of the top 1% as the cap is raised",
           "      z    2z     L=10     L=20     L=40     L=80"]
    for z in (F(2, 5), F(1, 2), F(3, 5)):
        s2.append(padl(sh(z), 7) + padl(sh(2 * z), 6) + "".join(padl(pct8(latf_top(z, L_, F(1, 100)), 1), 9) for L_ in (10, 20, 40, 80)))
    z89, z26 = lat_z_for(F(1, 100), F(228, 1000)), lat_z_for(F(1, 100), F(325, 1000))
    s2 += ["  the US top-1% wealth shares (Distributional Financial Accounts) read on the lattice:",
           "    22.8% (1989 Q3): z = " + dec(z89, 4) + ", alpha = " + dec(lat_alpha(z89), 3) + ";   32.5% (2026 Q2): z = " + dec(z26, 4) + ", alpha = " + dec(lat_alpha(z26), 3),
           "    the change in the ratio of capital-gain doublings to resets, p/q: +" + pct8(z26 / z89 - 1, 1)]
    check("§F2 the wealth lattice: tail exponent, condensation, the cap, the DFA shares", "\n".join(s2), D[1])
    # (3) Fisher
    def fdebts(lo, hi): return [lo + j * (hi - lo) / 19 for j in range(20)]
    def frun(ds, sig, eta):
        m = 0
        while True:
            p = max(F(0), 1 - sig - eta * m); m2 = sum(1 for d in ds if d > p)
            if m2 == m: return m, p
            m = m2
    profs = [("spread [0.20, 0.80]", F(1, 5), F(4, 5)), ("high [0.50, 0.95]", F(1, 2), F(19, 20))]
    sigs = [F(1, 20), F(1, 10), F(3, 20), F(1, 5), F(1, 4), F(3, 10)]
    s3 = ["§F3 FISHER'S DEBT DEFLATION: 20 firms, distress sales lower the price by eta each",
          "    shock sales   price  nominal  dollar   amplification"]
    for eta in (F(1, 40), F(1, 50)):
        for name, lo, hi in profs:
            ds = fdebts(lo, hi)
            s3.append("  leverage " + name + ", spacing " + dec((hi - lo) / 19, 4) + ";  eta = " + dec(eta, 4))
            for sig in sigs:
                m, p = frun(ds, sig, eta)
                s3.append(padl(dec(sig, 2), 9) + padl(str(m), 6) + padl(dec(p, 3), 8) + padl(pct8(sum(d for d in ds if d <= p) / sum(ds) - 1, 1), 9)
                          + padl(("+" + pct8(1 / p - 1, 1)) if p > 0 else "-", 9) + padl(dec((1 - p) / sig, 2), 7))
    def closed(lo, hi, sig, eta):
        dd = (hi - lo) / 19
        if hi <= 1 - sig: return 0
        if eta >= dd: return 20
        x = (hi - (1 - sig)) / (dd - eta)
        return min(20, -((-x.numerator) // x.denominator))
    ok = all(frun(fdebts(lo, hi), sig, eta)[0] == closed(lo, hi, sig, eta) for _, lo, hi in profs for eta in (F(1, 50), F(1, 40), F(1, 30)) for sig in sigs)
    s3.append("  sales = the closed form (eta >= spacing: all 20 once one fails; else ceil((d_hi - 1 + shock)/(spacing - eta))), 2 profiles x 3 etas x 6 shocks: " + tf(ok))
    check("§F3 Fisher's debt deflation: the cascade and its closed form", "\n".join(s3), D[2])
    # (4) capital mobility
    def flight_any(u, r):
        gp = dict(PE); gp["u"] = u; gp["rext"] = r
        return any(c == "flt" for _, c in cs_game("cap", gp).nash())
    def edge(r):
        lo, hi = F(0), F(1)
        for _ in range(40):
            m = (lo + hi) / 2
            if flight_any(m, r): lo = m
            else: hi = m
        return rnd((lo + hi) / 2, 100000)
    cl = lambda r: F(1, 5) * (F(1, 20) + r) / (F(4, 5) * (1 - F(1, 20) - r - F(2, 5)))
    rs = [F(1, 20), F(1, 10), F(3, 20), F(1, 5), F(1, 4), F(3, 10), F(2, 5)]
    s4 = ["§F4 CAPITAL MOBILITY: THE UNEMPLOYMENT RATE BELOW WHICH CAPITAL FLIGHT IS AN EQUILIBRIUM",
          "  r_ext  game u_f  closed u_f  max w_l  flight at u = 1"]
    for r in rs:
        s4.append(padl(dec(r, 3), 7) + padl(dec(edge(r), 4), 9) + padl(dec(cl(r), 4), 9) + padl(dec(1 - F(1, 20) - r, 3), 9) + padl(tf(flight_any(F(1), r)), 8))
    s4.append("  game and closed form u_f = bl (rho + r) / ((1 - bl)(1 - rho - r - s)) agree on the grid: " + tf(all(abs(edge(r) - cl(r)) < F(1, 10000) for r in rs)))
    s4.append("  flight is an equilibrium at every unemployment rate once r_ext >= 1 - rho - (bl + (1 - bl) s) = 43/100: " + tf(flight_any(F(1), F(43, 100)) and not flight_any(F(1), F(21, 50))))
    check("§F4 capital mobility and the flight threshold", "\n".join(s4), D[3])
    check("me-finance.pal: all assertions pass", asserts_ok(out), (7, 0))


# --- the financialized regime ------------------------------------------------
PF = dict(PE); PF.update(ifr=F(1, 20), lev=F(1), chi=F(1, 2), dcap=F(1), arep=F(1, 5), imech=0, ws=F(153, 200), wm=F(108, 125))
FIN_NODE_VARS = ["E", "U", "B", "W", "Inf", "Ce", "Pi", "Rr", "I", "K2", "Asp", "Rad", "Gov2", "SR2", "Df2", "Dh2", "DS"]


def pf_init():
    S = pe_init("fin"); S["Df"] = F(0); S["dh"] = F(0); return S


def pf_mu(V, p):
    if p.get("imech", 0) == 1:
        return p["mu"] * max(F(0), V["W"] - p["ws"]) / (p["wm"] - p["ws"])
    return p["mu"]


def pf_chain(S, p, hook=None):
    """one period of the financialized regime (fin); other regimes go to pe_chain"""
    if S["reg"] != "fin":
        return pe_chain(S, p, hook)
    V = dict(S); V["mode"] = "fin"
    if hook and hook[0] in V:
        V[hook[0]] = V[hook[0]] + hook[1]
    def eq(name, val):
        V[name] = val
        if hook:
            x, d, base, frozen = hook
            if name == x: V[name] = V[name] + d
            elif name in frozen: V[name] = base[name]
    N = p["N"]
    eq("E", min(N, V["K"] / V["kap"])); eq("U", 1 - V["E"] / N)
    gp = dict(p); gp["u"] = V["U"]
    if V["gov"] >= 1:
        gp["bl"] = p["bl"] / 2; gp["bh"] = p["bh"] / 2
    b, fl = beta_and_flight("cap", gp)
    eq("B", b); eq("Fl", fl)
    eq("Inf", p["shockpi"] if p["shock1"] <= V["t"] <= p["shock2"] else p["pistar"])
    eq("W", w_cap(V["B"], V["U"], p["s"] - p["ifr"] * V["dh"] * (1 + V["Inf"]) / V["A"]))
    eq("Pi", (1 - V["W"]) * V["E"])
    pn = lambda: V["Pi"] - p["ifr"] * V["Df"]
    eq("Rr", pn() / V["K"] if V["K"] > 0 else F(0))
    eq("Cr", 1 if (V["Rr"] < p["rmin"] or V["Fl"] == 1) else 0)
    eq("Mu", pf_mu(V, p))
    eq("Bf", F(0) if V["Cr"] == 1 else p["lev"] * max(F(0), (V["Mu"] + p["dep"]) * V["K"] - p["sc"] * pn()))
    eq("I", F(0) if V["Cr"] == 1 else p["sc"] * pn() + V["Bf"])
    eq("Df2", ((1 - p["crash"]) * V["Df"] if V["Cr"] == 1 else V["Df"] + V["Bf"]) / (1 + V["Inf"]))
    eq("K2", V["K"] * (1 - p["dep"]) + V["I"] - V["Cr"] * p["crash"] * V["K"])
    eq("Asp", V["ce"] * (1 + p["asp"] * V["sR"]))
    eq("Inc", V["W"] * V["A"] / (1 + V["Inf"]))
    eq("Jh", p["ifr"] * V["dh"])
    eq("Bh", F(0) if V["Cr"] == 1 else min(p["chi"] * max(F(0), V["Asp"] - (V["Inc"] - V["Jh"])), max(F(0), p["dcap"] * V["Inc"] - V["dh"])))
    eq("Rh", p["arep"] * V["dh"] if V["Cr"] == 1 else F(0))
    eq("Ce", (V["Inc"] - V["Jh"]) + (V["Bh"] - V["Rh"]))
    eq("Cu", p["s"])
    eq("DS", (V["Jh"] + V["Rh"]) / V["Inc"])
    eq("Dh2", (V["dh"] + V["Bh"] - V["Rh"]) / (1 + V["Inf"]))
    pos = lambda c: clampv(p["scale"] * (c - V["Asp"]) / V["Asp"], F(-8), F(8))
    eq("Rad", (1 - V["U"]) * (1 if pt_radical(pos(V["Ce"])) else 0) + V["U"] * (1 if pt_radical(pos(V["Cu"])) else 0))
    eq("Gov2", 1 if V["Rad"] > F(1, 2) else 0)
    br = p["phi"] * (V["Pi"] + V["Jh"] * (1 + V["Inf"]) / V["A"] * V["E"])
    eq("SR2", pat1(1, 0, br, p["psi"] * V["W"] * V["E"], p["prho"], 3 * (1 + V["U"] + V["DS"]), F(1), V["sR"]))
    ec = clampv((V["Rr"] - p["rmin"]) / p["rmin"], F(-1), F(1)); po = 2 * (F(1, 2) - V["Rad"])
    V["econ"], V["pol"], V["Phi"] = ec, po, min(ec, po)
    return V


def pf_next(S, V, p):
    S2 = dict(S); r6 = lambda x: rnd(x, 10 ** 6)
    S2.update(t=S["t"] + 1, K=r6(V["K2"]), kap=r6(S["kap"] * (1 + pf_mu(V, p))), A=r6(S["A"] * (1 + p["gam"])), ce=r6(V["Ce"]), sR=V["SR2"], gov=V["Gov2"])
    if "Df" in S:
        S2.update(Df=r6(V["Df2"]), dh=r6(V["Dh2"]))
    return S2


def pf_rows(S, p, n=60):
    rows = []
    for _ in range(n):
        V = pf_chain(S, p)
        rows.append(dict(t=V["t"], U=V["U"], B=V["B"], W=V["W"], Rr=V["Rr"], Cr=V["Cr"], Ce=V["Ce"], Asp=V["Asp"],
                         dk=V.get("Df", F(0)) / V["K"], dh=(V["dh"] / V["Inc"]) if "Inc" in V else F(0), DS=V.get("DS", F(0)),
                         Rad=V["Rad"], sR=V["sR"], gov=V["gov"], Phi=V["Phi"]))
        S = pf_next(S, V, p)
    return rows


def pf_at(S, p, n):
    for _ in range(n):
        S = pf_next(S, pf_chain(S, p), p)
    return S


def part8b():
    print("PART VIII(b)  the financialized economy (me-financialized)")
    out = run_pal("me-financialized.pal"); D = displays(out)
    fp = lambda **kw: dict(PF, **kw)
    NOF = dict(lev=F(0), chi=F(0))
    frows = lambda p: pf_rows(pf_init(), p)
    crows = lambda p: pf_rows(pe_init("cap"), p)
    crises = lambda rs: [r["t"] for r in rs if r["Cr"] == 1]
    govs = lambda rs: [r["t"] for r in rs if r["gov"] == 1]
    wchg = lambda rs: rs[59]["W"] / rs[0]["W"] - 1
    def hist(rows, every):
        out_ = ["     t      u      w      r cr     ce    asp   Df/K dh/inc     DS    rad     sR gov"]
        for r in rows:
            if r["t"] % every == 0:
                out_.append(padl(str(r["t"]), 6) + padl(dec(r["U"], 3), 7) + padl(dec(r["W"], 3), 7) + padl(dec(r["Rr"], 4), 7) + padl(str(r["Cr"]), 3)
                            + padl(dec(r["Ce"], 3), 7) + padl(dec(r["Asp"], 3), 7) + padl(dec(r["dk"], 3), 7) + padl(dec(r["dh"], 3), 7) + padl(dec(r["DS"], 3), 7)
                            + padl(dec(r["Rad"], 3), 7) + padl(dec(r["sR"], 3), 7) + padl(str(r["gov"]), 4))
        return "\n".join(out_)
    f = frows(PF); c = crows(fp(**NOF)); fc = frows(fp(chi=F(0)))
    # nesting (asserted by the program; checked here too)
    _, cp = pe_run("cap", PE, 60); c0 = frows(fp(**NOF))
    keys = ["t", "U", "B", "W", "Rr", "Cr", "Ce", "Rad", "sR", "gov", "Phi"]
    nest = all(all(a[k] == b_[k] for k in keys) for a, b_ in zip(c0, cp)) and all(all(a[k] == b_[k] for k in keys) for a, b_ in zip(c, cp))
    check("financialized with both credit channels off = capitalism, row for row (60 periods)", nest, True)
    seg = f[9:52]
    s1 = ["§F5.1 FINANCIALIZED CAPITALISM (lev = 1, chi = 1/2, interest 5%; every 3rd period)", hist(f, 3),
          "  crises (net profit rate below r_min): " + ilist(crises(f)) + ";  radical government in periods " + ilist(govs(f)),
          "  capitalism (Part IV): crises " + ilist(crises(c)) + ";  radical government in " + str(len(govs(c))) + " periods",
          "  unemployment at t = 0 / 8 / 30 / 51 / 59: " + drow([f[t]["U"] for t in (0, 8, 30, 51, 59)], 3, 7),
          "    capitalism, the same periods:             " + drow([c[t]["U"] for t in (0, 8, 30, 51, 59)], 3, 7),
          "  between the crises (t = 9..51): wage share within " + dec(max(r["W"] for r in seg) - min(r["W"] for r in seg), 4)
          + ";  profit rate falls every period: " + tf(all(b_["Rr"] < a["Rr"] for a, b_ in zip(seg, seg[1:]))) + ", " + dec(f[9]["Rr"], 4) + " -> " + dec(f[51]["Rr"], 4),
          "  firm debt / capital at t = 9 / 24 / 39 / 51: " + drow([f[t]["dk"] for t in (9, 24, 39, 51)], 3, 7)
          + ";  household debt / income at its ceiling for t = 15..39: " + tf(all(r["dh"] > F(19, 20) for r in f[15:40])),
          "  labour share, relative change over 60 periods: financialized " + pct8(wchg(f), 1) + ";  capitalism " + pct8(wchg(c), 1)]
    check("§F5.1 the financialized trajectory against capitalism", "\n".join(s1), D[0])
    s2 = ["§F5.2 THE CHANNELS ONE AT A TIME", "  channels                   crises radgov  u_59  w change max Df/K max dh/inc"]
    for name, kw in (("none (= capitalism)", NOF), ("firm credit", dict(chi=F(0))), ("household credit", dict(lev=F(0))), ("both", {})):
        rs = frows(fp(**kw))
        s2.append(padr(name, 22) + padl(ilist(crises(rs)), 12) + padl(str(len(govs(rs))), 5) + padl(dec(rs[59]["U"], 3), 8) + padl(pct8(wchg(rs), 1), 9)
                  + padl(dec(max(r["dk"] for r in rs), 3), 9) + padl(dec(max(r["dh"] for r in rs), 3), 9))
    check("§F5.2 the financial channels one at a time", "\n".join(s2), D[1])
    lo, hi = F(-8), F(0)
    for _ in range(30):
        m = (lo + hi) / 2
        if pt_radical(m): lo = m
        else: hi = m
    dstar = (lo + hi) / 2
    pos20 = lambda cc, ref: clampv(20 * (cc - ref) / ref, F(-8), F(8))
    s3 = ["§F5.3 THE CREDIT CRUNCH: WHEN A CRISIS BECOMES A RADICAL GOVERNMENT",
          "  the employed vote radical iff standard / aspiration < 1 + D*/20 = " + dec(1 + dstar / 20, 4) + "   (D* = " + dec(dstar, 5) + ")",
          "  run              crisis  ce_t-1    ce_t   asp_t    drop  ce/asp  dh/inc radical"]
    crunch_ok = True
    for name, rs in (("financialized", f), ("firm credit only", fc)):
        for t in crises(rs):
            r0, r1 = rs[t - 1], rs[t]; rad = 1 if pt_radical(pos20(r1["Ce"], r1["Asp"])) else 0
            crunch_ok &= (rad == 1) == (r1["Ce"] / r1["Asp"] < 1 + dstar / 20)
            s3.append(padr(name, 18) + padl(str(t), 4) + padl(dec(r0["Ce"], 3), 8) + padl(dec(r1["Ce"], 3), 8) + padl(dec(r1["Asp"], 3), 8)
                      + padl(pct8(1 - r1["Ce"] / r0["Ce"], 1), 8) + padl(dec(r1["Ce"] / r1["Asp"], 4), 8) + padl(dec(r0["dh"], 3), 8) + padl(str(rad), 6))
    s3 += ["  household borrowing propensity chi (lev = 1):", "    chi    crises   radical gov  max dh/inc"]
    for chi in (F(0), F(1, 8), F(1, 4), F(3, 8), F(1, 2), F(3, 4), F(1)):
        rs = frows(fp(chi=chi))
        s3.append(padl(dec(chi, 3), 7) + padl(ilist(crises(rs)), 10) + padl(ilist(govs(rs)), 12) + padl(dec(max(r["dh"] for r in rs), 3), 9))
    check("§F5.3 the credit crunch, the radical threshold it crosses, and chi", "\n".join(s3), D[2])
    check("every crunch is radical exactly when standard/aspiration < 1 + D*/20", crunch_ok, True)
    s4 = ["§F5.4 HOW FAR THE BANKS ACCOMMODATE (share lev of the financing gap; chi = 1/2)", "    lev    crises radgov  u_59  max Df/K"]
    for lev in (F(0), F(1, 4), F(1, 2), F(5, 8), F(3, 4), F(7, 8), F(1)):
        rs = frows(fp(lev=lev))
        s4.append(padl(dec(lev, 3), 7) + padl(ilist(crises(rs)), 10) + padl(str(len(govs(rs))), 5) + padl(dec(rs[59]["U"], 3), 8) + padl(dec(max(r["dk"] for r in rs), 3), 9))
    lo, hi = F(3, 4), F(7, 8)
    for _ in range(8):
        m = (lo + hi) / 2
        if crises(frows(fp(lev=m))): hi = m
        else: lo = m
    s4.append("  a debt crisis within 60 periods appears between lev = " + dec(lo, 4) + " (none) and " + dec(hi, 4) + " (a crisis)")
    check("§F5.4 credit accommodation and the crisis threshold", "\n".join(s4), D[3])
    s5 = ["§F5.5 INFLATION, DEFLATION AND THE DEBT CRISIS", "  steady inflation (the shock of t = 40-41 kept at 10%):", "     pi    crises radgov Df/K_59 pay cut"]
    seconds = []
    for pi in (F(0), F(1, 50), F(1, 25), F(3, 50), F(2, 25), F(1, 10)):
        rs = frows(fp(pistar=pi)); cr = crises(rs); seconds.append(cr[1] if len(cr) > 1 else 1000)
        s5.append(padl(dec(pi, 3), 7) + padl(ilist(cr), 10) + padl(str(len(govs(rs))), 5) + padl(dec(rs[59]["dk"], 3), 8) + padl(pct8(pi / (1 + pi), 1), 9))
    s5 += ["  a 10% inflation shock against a 10% deflation shock at t = 40-41:", "  run                           crises         radical gov   ce_40 dh/inc_42"]
    for name, reg, shk in (("capitalism, inflation", "cap", F(1, 10)), ("capitalism, deflation", "cap", F(-1, 10)), ("financialized, inflation", "fin", F(1, 10)), ("financialized, deflation", "fin", F(-1, 10))):
        rs = frows(fp(shockpi=shk, **(NOF if reg == "cap" else {})))
        s5.append(padr(name, 26) + padl(ilist(crises(rs)), 10) + padl(ilist(govs(rs)), 22) + padl(dec(rs[40]["Ce"], 3), 8) + padl(dec(rs[42]["dh"], 3), 8))
    check("§F5.5 inflation, deflation and the date of the debt crisis", "\n".join(s5), D[4])
    check("the second debt crisis comes no earlier as steady inflation rises", all(b_ >= a for a, b_ in zip(seconds, seconds[1:])), True)
    s6 = ["§F5.6 THE STRESS GRID OF PART IV WITH AND WITHOUT FINANCE: radical-government periods of 60", "  scale shock   asp     cap     fin"]
    gr = []
    for sc_ in (20, 30, 40):
        for sh_ in (F(1, 20), F(1, 10), F(1, 5)):
            for asp in (F(1, 10), F(1, 5), F(2, 5)):
                cc = len(govs(frows(fp(scale=F(sc_), shockpi=sh_, asp=asp, **NOF)))); ff = len(govs(frows(fp(scale=F(sc_), shockpi=sh_, asp=asp))))
                gr.append((sc_, sh_, asp, cc, ff))
                s6.append(padl(str(sc_), 6) + padl(sh(sh_), 6) + padl(sh(asp), 6) + padl(str(cc), 8) + padl(str(ff), 8))
    fewer = [g for g in gr if g[4] < g[3]]
    s6 += ["  settings with a radical government: capitalism " + str(sum(1 for g in gr if g[3] > 0)) + " of 27;  financialized " + str(sum(1 for g in gr if g[4] > 0)) + " of 27",
           "  radical-government periods in all 27: capitalism " + str(sum(g[3] for g in gr)) + ";  financialized " + str(sum(g[4] for g in gr)),
           "  settings in which finance has fewer radical periods than capitalism: " + str(len(fewer)) + ";  all of them locked in under capitalism (aspiration 2/5, 56+ periods): "
           + tf(all(g[2] == F(2, 5) and g[3] >= 56 for g in fewer))]
    check("§F5.6 the 27-setting stress grid with and without finance (54 runs)", "\n".join(s6), D[5])
    s7 = ["§F5.7 INDUCED MECHANIZATION AGAINST CREDIT: TWO REMEDIES FOR THE UNEMPLOYMENT TREND",
          "  run                        u_0   u_15   u_30   u_45   u_59  w chg    r_59   crises"]
    ci = crows(fp(imech=1, **NOF)); fi = frows(fp(imech=1))
    for name, rs in (("capitalism", crows(fp(**NOF))), ("capitalism, induced", ci), ("financialized", f), ("financialized, induced", fi)):
        s7.append(padr(name, 24) + drow([rs[t]["U"] for t in (0, 15, 30, 45, 59)], 3, 7) + padl(pct8(wchg(rs), 1), 8) + padl(dec(rs[59]["Rr"], 4), 8) + padl(ilist(crises(rs)), 9))
    s7.append("  financialized, induced: unemployment the same in every period from t = 30: " + tf(all(rnd(r["U"], 1000) == rnd(fi[30]["U"], 1000) for r in fi[30:])))
    s7.append("  capitalism, induced: unemployment rises by less than 0.001 a period from t = 30: " + tf(all(F(0) <= b_["U"] - a["U"] < F(1, 1000) for a, b_ in zip(ci[30:], ci[31:]))))
    s7 += ["  the switch share ws at which mechanizing stops paying (capitalism, induced):", "     ws   u_15   u_30   u_45   u_59  w chg"]
    for ws in (F(7, 10), F(3, 4), F(153, 200), F(4, 5), F(21, 25)):
        rs = crows(fp(imech=1, ws=ws, **NOF))
        s7.append(padl(dec(ws, 3), 7) + drow([rs[t]["U"] for t in (15, 30, 45, 59)], 3, 7) + padl(pct8(wchg(rs), 1), 8))
    check("§F5.7 induced mechanization against credit", "\n".join(s7), D[6])
    # (8) edges and loops
    IVF = {"K": ("K", "K2", F(10)), "Kap": ("kap", "kap", F(1, 10)), "E": ("E", "E", F(5)), "U": ("U", "U", F(1, 20)), "B": ("B", "B", F(1, 20)),
           "W": ("W", "W", F(1, 20)), "Inf": ("Inf", "Inf", F(1, 20)), "Ce": ("Ce", "Ce", F(1, 5)), "Pi": ("Pi", "Pi", F(5)), "Rr": ("Rr", "Rr", F(1, 50)),
           "I": ("I", "I", F(5)), "Asp": ("Asp", "Asp", F(1, 5)), "Rad": ("Rad", "Rad", F(3, 5)), "Gov": ("gov", "Gov2", F(1)), "SR": ("sR", "SR2", F(1, 5)),
           "Df": ("Df", "Df2", F(5)), "Dh": ("dh", "Dh2", F(1, 10)), "DS": ("DS", "DS", F(1, 20))}
    def probe(a_, b_, S, pp):
        x, _, d = IVF[a_]; y = IVF[b_][1]
        Vb = pf_chain(S, pp); frozen = [z for z in FIN_NODE_VARS if z != x and z != y]
        return pf_chain(S, pp, (x, d, Vb, frozen))[y] - Vb[y]
    ST8 = fp(scale=F(30), asp=F(2, 5)); DF8 = fp(shockpi=F(-1, 10))
    bases = [(pf_at(pf_init(), PF, t), PF) for t in (0, 15, 30, 45, 7, 8, 52)] + [(pf_at(pf_init(), ST8, 10), ST8), (pf_at(pf_init(), PF, 40), PF), (pf_at(pf_init(), DF8, 41), DF8)]
    old = [("K", "E", 1), ("Kap", "E", -1), ("E", "U", -1), ("U", "B", -1), ("U", "W", -1), ("B", "W", 1), ("W", "Ce", 1), ("Inf", "Ce", -1),
           ("W", "Pi", -1), ("E", "Pi", 1), ("Pi", "Rr", 1), ("K", "Rr", -1), ("Rr", "I", 1), ("Pi", "I", 1), ("I", "K", 1), ("SR", "Asp", 1),
           ("Ce", "Rad", -1), ("U", "Rad", 1), ("Asp", "Rad", 1), ("Rad", "Gov", 1), ("Gov", "B", -1), ("Pi", "SR", 1), ("U", "SR", 1), ("W", "SR", -1)]
    new = [("K", "I", 1), ("K", "Df", 1), ("Pi", "Df", -1), ("Df", "Rr", -1), ("Inf", "Df", -1), ("Asp", "Dh", 1), ("Asp", "Ce", 1),
           ("Dh", "Ce", -1), ("Dh", "W", -1), ("Dh", "DS", 1), ("DS", "SR", 1), ("Inf", "Dh", -1)]
    def verdict(a_, b_, sg):
        ds = [probe(a_, b_, S, pp) for S, pp in bases]
        right = all((x > 0) if sg > 0 else (x < 0) for x in ds); zero = all(x == 0 for x in ds); nw = all((x >= 0) if sg > 0 else (x <= 0) for x in ds)
        return ("strict" if right else ("absent" if zero else ("weak" if nw else "FAIL"))), ds
    line = lambda a_, b_, sg, v_, ds: padl(a_, 4) + " -> " + padr(b_, 4) + padl("pos" if sg > 0 else "neg", 4) + padl(v_, 7) + drow(ds, 3, 8)
    nv = [(e, *verdict(*e)) for e in new]; ov = [(e, *verdict(*e)) for e in old]
    s8 = ["§F5.8 THE FINANCIAL EDGES, CHECKED ON THE EQUATION CHAIN (partial finite differences)",
          "                       deltas at:   f0     f15     f30     f45     cr7    gov8    cr52    st10   inf40   def41"]
    s8 += [line(*e, v_, ds) for e, v_, ds in nv]
    s8.append("  financial edges confirmed (strict or weak): " + str(sum(1 for _, v_, _ in nv if v_ in ("strict", "weak"))) + " of " + str(len(new)))
    s8.append("  capitalism's 24 edges at the financialized bases: those not strict")
    s8 += [line(*e, v_, ds) for e, v_, ds in ov if v_ != "strict"]
    alive = [e for e, v_, _ in ov if v_ != "absent"]
    edges = alive + new
    nodes = "K Kap E U B W Inf Ce Pi Rr I Asp Rad Gov SR Df Dh DS".split(); idx = {n: i for i, n in enumerate(nodes)}
    found = []
    def dfs(s_, cur, path):
        for a_, b_, _ in edges:
            if a_ != cur: continue
            if b_ == s_: found.append(list(path))
            elif idx[b_] > idx[s_] and b_ not in path: dfs(s_, b_, path + [b_])
    for n in nodes: dfs(n, n, [n])
    sign = {(a_, b_): sg for a_, b_, sg in edges}
    loops = []
    for cyc in found:
        pol = 1
        for a_, b_ in zip(cyc, cyc[1:] + cyc[:1]): pol *= sign[(a_, b_)]
        loops.append(("R" if pol > 0 else "B", cyc))
    fin_ = [l for l in loops if any(x in l[1] for x in ("Df", "Dh", "DS"))]
    s8.append("  financialized diagram: " + str(len(alive)) + " of capitalism's edges + " + str(len(new)) + " financial = " + str(len(alive) + len(new)) + " edges")
    s8.append("  elementary cycles: " + str(len(loops)) + "   reinforcing " + str(sum(1 for k, _ in loops if k == "R")) + "   balancing " + str(sum(1 for k, _ in loops if k == "B"))
              + ";  through a financial node: " + str(len(fin_)) + " (R " + str(sum(1 for k, _ in fin_ if k == "R")) + ", B " + str(sum(1 for k, _ in fin_ if k == "B")) + ")")
    s8.append("  the shortest loops through a financial node:")
    s8 += [f"{k}{padl(str(len(cyc)), 3)}  " + " -> ".join(cyc + cyc[:1]) for k, cyc in fin_ if len(cyc) <= 4]
    check("§F5.8 all 36 edge probes at 10 financialized states; the loops finance adds", "\n".join(s8), D[7])
    check("me-financialized.pal: all assertions pass", asserts_ok(out), (12, 0))
    return f, fc, ci


def part8_evidence(f, fc, ci):
    print("PART VIII(c)  finance against the data (me-evidence §EV2)")
    out = run_pal("me-evidence.pal"); D = displays(out)
    z89, z26 = lat_z_for(F(1, 100), F(228, 1000)), lat_z_for(F(1, 100), F(325, 1000))
    crad = lambda rs: sum(1 for r in rs if r["Cr"] == 1 and rs[r["t"] + 1]["gov"] == 1)
    ncr = lambda rs: sum(1 for r in rs if r["Cr"] == 1)
    drop = lambda rs, t: 1 - rs[t]["Ce"] / rs[t - 1]["Ce"]
    frel = lambda rs: (rs[59]["W"] - rs[0]["W"]) / rs[0]["W"]
    p1 = lambda x: dec(100 * x, 1) + "%"
    s = ["§EV2 FINANCE: THE MODEL AGAINST EMPIRICAL DATA", "  quantity                                   data        model",
         "  Pareto exponent of US wealth               " + dec(F(149, 100), 2) + "        " + dec(lat_alpha(z89), 3) + "  (the lattice reading of the 1989 top-1% share)",
         "    ... top-1% share " + p1(F(228, 1000)) + " -> " + p1(F(325, 1000)) + " (1989 -> 2026): alpha " + dec(lat_alpha(z89), 3) + " -> " + dec(lat_alpha(z26), 3) + "; condensation at 1",
         "  far-right vote after financial crises      +" + p1(F(3, 10)) + "      radical government after " + str(crad(f)) + " of " + str(ncr(f)) + " crunches with household debt, "
         + str(crad(fc)) + " of " + str(ncr(fc)) + " without",
         "    ... the employed standard in the crunch: " + p1(-drop(f, 7)) + " / " + p1(-drop(f, 52)) + " with household debt; +" + p1(-drop(fc, 5)) + " without",
         "  labour share, relative change              " + p1((F(66, 125) - F(331, 500)) / F(331, 500)) + "      financialized " + p1(frel(f)) + ";  induced mechanization " + p1(frel(ci)) + " (u_59 " + dec(ci[59]["U"], 3) + ")",
         "  capital-account opening, labour share      " + p1(F(-9, 200)) + "       wage-share ceiling 1 - rho - r_ext: " + p1((F(4, 5) - F(17, 20)) / F(17, 20)) + "  (r_ext 10% -> 15%)"]
    check("§EV2 finance against the data: wealth tail, crises and votes, labour share, capital account", "\n".join(s), D[1])


if __name__ == "__main__":
    part1()
    part2()
    part3()
    part4()
    part5()
    part6a()
    part6b()
    part6c()
    part6d()
    f8, fc8, ci8 = part8b()
    part8a()
    part8_evidence(f8, fc8, ci8)
    print("\nALL AGREE" if ok_all else "\nDISAGREEMENT FOUND", f"({n_checks} checks)")
    sys.exit(0 if ok_all else 1)
