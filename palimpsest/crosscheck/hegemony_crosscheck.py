#!/usr/bin/env python3
"""Independent cross-check of the Hegemony economy study (HEGEMONY-ECONOMY.md).

Pure Python 3, standard library only. Re-implements, from the written
specification (not from the Palimpsest code), the 2-player Hegemony economy as
modelled in lib/hegemony.pal, then compares against Palimpsest's output:

  1. the full 5-round baseline game, round by round (all history rows), and
     the final money balances, flow matrix, goods statistics, VP and policies;
  2. the nine counterfactual games of examples/hegemony-policy.pal;
  3. the regime atlas of examples/hegemony-regimes.pal;
  4. the exact election odds of examples/hegemony-politics.pal;
  5. the debt theorems T5-T7 of examples/hegemony-debt.pal (re-derived);
  6. the 17 elementary cycles of the causal-loop diagram (re-enumerated).

Usage:  python3 crosscheck/hegemony_crosscheck.py [path/to/palimpsest]
Exit status 0 iff everything agrees.
"""
import copy, itertools, os, re, subprocess, sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "target/release/palimpsest")
ok_all = True
def check(name, got, want):
    global ok_all
    ok = got == want
    ok_all &= ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"\n        python: {got}\n        model : {want}"))

# ---------------------------------------------------------------- tables ----
SECS = "ABC"
def pop_of(w): return min(10, w // 3)
def ceil_half(n): return (n + 1) // 2
def ceil_div(a, b): return (a + b - 1) // b
def pos(x): return max(0, x)
INCOME = {("A","A"):7,("A","B"):6,("A","C"):5,("B","A"):4,("B","B"):4,("B","C"):4,("C","A"):1,("C","B"):2,("C","C"):3}
WMOD = {"A":2,"B":1,"C":0}
def tax_mult(t, h, e):
    if t == "A": return 3 + 2 * (WMOD[h] + WMOD[e])
    if t == "B": return 2 + WMOD[h] + WMOD[e]
    return 1
CTAB = {"A":[0,1,5,12,24,40,100,160],"B":[0,2,5,10,15,30,70,120],"C":[0,2,4,7,10,20,40,60]}
def count_le(r, xs):
    n = 0
    for x in xs:
        if r >= x: n += 1
        else: break
    return n
def corp_tax(t, r): return CTAB[t][count_le(r, [5,10,25,50,100,200,300])]
def wealth_idx(c): return count_le(c, [10,25,50,75,100,125,150,175,200,250,300,350,400,450,500])
MINLV = {"A":3,"B":2,"C":1}
def wage_at(w, lv): return w[3 - lv]
SPRICE = {"A":0,"B":5,"C":10}
TARIFF = {("food","A"):10,("food","B"):5,("food","C"):0,("lux","A"):6,("lux","B"):3,("lux","C"):0}
def tariff(r, tr): return TARIFF.get((r, tr), 0)
ROWS = {"A":3,"B":2,"C":1}
IMFLIM = {"A":2,"B":2,"C":1}
IMMIG = {"A":0,"B":1,"C":2}
def toward_a(s): return {"B":"A","C":"B"}[s]
def toward_c(s): return {"A":"B","B":"C"}[s]
def pol_bonus(k): return [0,1,4,8,12,18][k]
def price_opts(r): return [9,12,15] if r == "food" else [5,8,10]
def best_price(alt, opts):
    b = opts[0]
    for x in opts:
        if x <= alt: b = x
    return b
CARDS = {
  "supermarket": ("food",4,16,(25,20,15),["agri","u"]),
  "mall": ("lux",6,16,(25,20,15),["lux","u"]),
  "clinic": ("health",6,16,(30,20,10),["health","u"]),
  "college": ("edu",6,16,(30,20,10),["edu","u"]),
  "stadium": ("lux",8,20,(35,30,25),["lux","u","u"]),
  "institute": ("edu",8,20,(40,30,20),["edu","u","u"]),
  "radio": ("infl",2,8,(20,15,10),["u","u"]),
  "p-hospital": ("health",4,20,(30,20,10),["health","u"]),
  "p-univ": ("edu",4,20,(30,20,10),["edu","u"]),
  "p-media": ("infl",3,20,(30,20,10),["media","u"]),
}
MARKET_DECK = "clinic college mall supermarket stadium institute radio clinic college mall supermarket stadium institute radio clinic college".split()
IMMIG_DECK = "u agri u health u edu u lux u media".split()
EXPORT = [
  [("food",3,25),("lux",4,25),("lux",8,45),("health",3,20),("edu",3,20),("edu",5,35)],
  [("food",4,40),("food",2,18),("lux",5,35),("health",4,30),("health",2,12),("edu",4,24)],
  [("food",3,30),("lux",3,21),("lux",6,36),("health",5,40),("edu",6,42),("edu",2,10)],
  [("food",5,45),("food",3,24),("lux",4,32),("health",3,24),("edu",3,21)],
]
CATS = "wage-cc wage-pub sale-cc sale-st import tariff export tax-wc tax-emp tax-corp capex divest loan interest repay lobby shock".split()
POLS = "fiscal labor tax health edu trade immig".split()
IMF_PROFILE = [("fiscal","C"),("labor","C"),("tax","A"),("health","B"),("edu","C"),("trade","B"),("immig","B")]
CAUSE = {"wage-cc":"wage","wage-pub":"wage","sale-cc":"food","import":"food","tariff":"food","tax-wc":"tax","tax-emp":"tax","tax-corp":"tax","interest":"interest","capex":"capex"}

def rng(n):
    z = (n + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    z ^= z >> 31
    return z >> 1

def mk_co(name, own, row, lvl, crew):
    out, q, cost, w, slots = CARDS[name]
    return dict(name=name, own=own, out=out, qty=q, cost=cost, wages=w, lvl=lvl, slots=list(slots), crew=list(crew), row=row, committed=False)

def setup():
    S = dict(round=1, pol=dict(fiscal="C",labor="B",tax="A",health="B",edu="C",trade="B",immig="B"), bills=[],
      wc=dict(money=30,infl=1,prosp=0,vp=0,loans=0,workers=10,food=0,lux=0,health=0,edu=0,
              pool=dict(u=2,agri=0,lux=0,health=0,edu=0,media=0),demo=False,bills=3,cubes=17),
      cc=dict(rev=120,cap=0,vp=0,loans=0,infl=1,wmark=0,food=1,lux=2,health=0,edu=2,
              price=dict(food=12,lux=8,health=8,edu=8),market=["stadium","institute","radio","supermarket"],
              deck=list(MARKET_DECK),nextid=1,bills=3,cubes=17),
      st=dict(treasury=120,loans=0,writeoff=0,health=5,edu=5,infl=3), world=-270,
      bag=dict(wc=8,cc=8,mc=8), imm=1, seed=2026, events=[], taxlabor="B", hist=[],
      flows={c: dict(wc=0,cc=0,st=0,world=0) for c in CATS},
      cause=dict(wage=0,food=0,tax=0,interest=0,capex=0,other=0),
      gstat={g: dict(prod=0,imp=0,use=0,exp=0,lost=0) for g in ["food","lux","health","edu","infl"]})
    cos = {}
    cos["sm"] = mk_co("supermarket","cc",0,2,["agri","u"]); cos["mall"] = mk_co("mall","cc",0,2,["lux","u"])
    cos["college"] = mk_co("college","cc",0,2,[]); cos["clinic"] = mk_co("clinic","cc",0,2,[])
    for r in (1,2,3):
        cos[f"ph{r}"] = mk_co("p-hospital","st",r,2,["health","u"] if r == 1 else [])
        cos[f"pu{r}"] = mk_co("p-univ","st",r,2,["edu","u"] if r == 1 else [])
        cos[f"pm{r}"] = mk_co("p-media","st",r,2,[])
    S["cos"] = cos
    return S

# ---------------------------------------------------------------- ledger ----
def acct_add(S, who, a):
    if who == "wc": S["wc"]["money"] += a
    elif who == "cc": S["cc"]["rev"] += a
    elif who == "st": S["st"]["treasury"] += a
    else: S["world"] += a
def have(S, who):
    if who == "wc": return S["wc"]["money"]
    if who == "cc": return S["cc"]["rev"] + S["cc"]["cap"]
    if who == "st": return S["st"]["treasury"]
def flow(S, cat, frm, to, amt):
    S["flows"][cat][frm] -= amt; S["flows"][cat][to] += amt
def borrow(S, who, k, cat):
    amt = 50 * k
    if who == "cc": S["cc"]["cap"] += amt
    else: acct_add(S, who, amt)
    S["world"] -= amt
    flow(S, "loan", "world", who, amt)
    S[who]["loans"] += k
    S["cause"][CAUSE.get(cat, "other")] += k
def debit(S, who, a, cat, cap_first=False):
    if who == "world": S["world"] -= a; return
    h = have(S, who)
    if h < a: borrow(S, who, ceil_div(a - h, 50), cat)
    if who != "cc": acct_add(S, who, -a); return
    c = S["cc"]
    first, second = ("cap","rev") if cap_first else ("rev","cap")
    if c[first] >= a: c[first] -= a
    else: c[second] += c[first] - a; c[first] = 0
def pay(S, frm, to, a, cat, cap_first=False):
    debit(S, frm, a, cat, cap_first); acct_add(S, to, a); flow(S, cat, frm, to, a)
def money_total(S): return S["wc"]["money"] + S["cc"]["rev"] + S["cc"]["cap"] + S["st"]["treasury"] + S["world"]

# goods
def gmove(S, r, frm, to, q): S[frm][r] -= q; S[to][r] += q
def gprod(S, r, who, q, stored): S[who][r] += stored; S["gstat"][r]["prod"] += q; S["gstat"][r]["lost"] += q - stored
def guse(S, r, who, q): S[who][r] -= q; S["gstat"][r]["use"] += q
def gexp(S, r, who, q): S[who][r] -= q; S["gstat"][r]["exp"] += q
def gimp(S, r, who, q): S[who][r] += q; S["gstat"][r]["imp"] += q
def gdiscard(S, r, who, q): S[who][r] -= q; S["gstat"][r]["lost"] += q

# companies
def pop(S): return pop_of(S["wc"]["workers"])
def active(S, i):
    c = S["cos"][i]
    return True if c["own"] == "cc" else c["row"] <= ROWS[S["pol"]["fiscal"]]
def staffed(S, i): return len(S["cos"][i]["crew"]) > 0
def cur_wage(S, i): c = S["cos"][i]; return wage_at(c["wages"], c["lvl"])
def ids(S, pred): return [i for i in S["cos"] if pred(S, i)]
P_CC = lambda S, i: S["cos"][i]["own"] == "cc"
P_CC_OP = lambda S, i: P_CC(S, i) and staffed(S, i)
P_PUB_OP = lambda S, i: S["cos"][i]["own"] == "st" and active(S, i) and staffed(S, i)
P_PUB_ACTIVE = lambda S, i: S["cos"][i]["own"] == "st" and active(S, i)
P_VACANCY = lambda S, i: active(S, i) and not staffed(S, i)
def take_crew(slots, pool):
    p = dict(pool); crew = []
    for x in slots:
        if x != "u":
            if p[x] >= 1: p[x] -= 1; crew.append(x)
            else: return None
        else:
            t = next((t for t in ["u","agri","lux","health","edu","media"] if p[t] >= 1), None)
            if t is None: return None
            p[t] -= 1; crew.append(t)
    return crew, p
def can_staff(S, i): return take_crew(S["cos"][i]["slots"], S["wc"]["pool"]) is not None
P_STAFFABLE = lambda S, i: P_VACANCY(S, i) and can_staff(S, i)
def staff(S, i):
    crew, p = take_crew(S["cos"][i]["slots"], S["wc"]["pool"])
    S["wc"]["pool"] = p; S["cos"][i]["crew"] = crew; S["cos"][i]["committed"] = True
def unstaff(S, i):
    for t in S["cos"][i]["crew"]: S["wc"]["pool"][t] += 1
    S["cos"][i]["crew"] = []; S["cos"][i]["committed"] = False
def pool_size(S): return sum(S["wc"]["pool"].values())
def open_slots(S): return sum(len(S["cos"][i]["slots"]) for i in ids(S, P_VACANCY))
def wage_bill(S, pred): return sum(cur_wage(S, i) for i in ids(S, pred))
def expected_wages(S): return wage_bill(S, P_CC_OP) + wage_bill(S, P_PUB_OP)
def log(S, *e): S["events"].append(e)
def tm(S): p = S["pol"]; return tax_mult(p["tax"], p["health"], p["edu"])
def food_import_price(S): return 10 + tariff("food", S["pol"]["trade"])

# ---------------------------------------------------------------- phases ----
def prep(S):
    pay(S, "wc", "world", 5 * S["wc"]["loans"], "interest")
    pay(S, "cc", "world", 5 * S["cc"]["loans"], "interest", cap_first=True)
    pay(S, "st", "world", 5 * S["st"]["loans"], "interest")
    while S["st"]["loans"] > 0 and S["st"]["treasury"] > 50:
        pay(S, "st", "world", 50, "repay"); S["st"]["loans"] -= 1
    S["wc"]["prosp"] = pos(S["wc"]["prosp"] - 1)
    while len(S["cc"]["market"]) < 4 and S["cc"]["deck"]:
        S["cc"]["market"].append(S["cc"]["deck"].pop(0))
    S["wc"]["pool"]["u"] += 2; S["wc"]["workers"] += 2
    for _ in range(IMMIG[S["pol"]["immig"]]):
        t = IMMIG_DECK[S["imm"] % 10]
        S["wc"]["pool"][t] += 1; S["wc"]["workers"] += 1; S["imm"] += 1
    S["wc"]["bills"] = 3; S["cc"]["bills"] = 3

def use(S, r):
    p = pop(S); guse(S, r, "wc", p)
    np_ = min(10, S["wc"]["prosp"] + 1); S["wc"]["prosp"] = np_; S["wc"]["vp"] += np_
    if r == "health":
        S["wc"]["vp"] += 2; S["wc"]["workers"] += 1; S["wc"]["pool"]["u"] += 1
    elif r == "edu" and S["wc"]["pool"]["u"] >= 1:
        t = "health"
        for i in ids(S, P_VACANCY):
            k = S["cos"][i]["slots"][0]
            if k != "u" and S["wc"]["pool"][k] == 0: t = k; break
        S["wc"]["pool"]["u"] -= 1; S["wc"]["pool"][t] += 1

def best_vacancy(S):
    best, w = None, -1
    for i in ids(S, P_STAFFABLE):
        wx = cur_wage(S, i)
        if wx > w: best, w = i, wx
    return best
def demo_ok(S): return (not S["wc"]["demo"]) and pool_size(S) >= 2 + open_slots(S)
def wc_reserve(S):
    p = pop(S); pol = S["pol"]
    return pos(p * (food_import_price(S) + INCOME[(pol["labor"], pol["tax"])]) - expected_wages(S))
def wc_budget(S): return S["wc"]["money"] - wc_reserve(S)
def sources(S, r):
    pol = S["pol"]
    if r == "health": a, b = ("st", SPRICE[pol["health"]], S["st"]["health"]), ("cc", S["cc"]["price"]["health"], S["cc"]["health"])
    elif r == "edu": a, b = ("st", SPRICE[pol["edu"]], S["st"]["edu"]), ("cc", S["cc"]["price"]["edu"], S["cc"]["edu"])
    elif r == "lux": a, b = ("cc", S["cc"]["price"]["lux"], S["cc"]["lux"]), ("world", 6 + tariff("lux", pol["trade"]), 999)
    else: a, b = ("cc", S["cc"]["price"]["food"], S["cc"]["food"]), ("world", food_import_price(S), 999)
    return [b, a] if b[1] < a[1] else [a, b]
def plan_for(S, r):
    need = pop(S) - S["wc"][r]
    if need <= 0: return None
    cap = pop(S); cost = 0; lines = []
    for (w, p, a) in sources(S, r):
        if need == 0: break
        q = min(need, min(a, cap)); need -= q; cost += q * p
        if q > 0: lines.append((w, q, p))
    if need > 0: return None
    return (r, cost, lines)
def buy_choice(S):
    bud = wc_budget(S); best = None
    for r in ["health", "edu", "lux"]:
        pl = plan_for(S, r)
        if pl and pl[1] <= bud and (best is None or pl[1] < best[1]): best = pl
    return best
def exec_plan(S, pl):
    r = pl[0]
    for (w, q, p) in pl[2]:
        if w == "st": pay(S, "wc", "st", q * p, "sale-st"); gmove(S, r, "st", "wc", q)
        elif w == "cc": pay(S, "wc", "cc", q * p, "sale-cc"); gmove(S, r, "cc", "wc", q)
        else:
            t = tariff(r, S["pol"]["trade"])
            pay(S, "wc", "world", q * (p - t), "import"); pay(S, "wc", "st", q * t, "tariff"); gimp(S, r, "wc", q)
def bill_choice(S, who):
    if S[who]["bills"] <= 0: return None
    order, goal = (["labor","health","edu","fiscal"], "A") if who == "wc" else (["labor","tax","health","edu","fiscal"], "C")
    for p in order:
        sec = S["pol"][p]
        if sec != goal and not any(b[0] == p for b in S["bills"]):
            return (p, toward_a(sec) if goal == "A" else toward_c(sec))
    return None
def propose(S, b, who): S["bills"].append((b[0], b[1], who)); S[who]["bills"] -= 1
def pressure(S, who): S[who]["cubes"] -= 3; S["bag"][who] += 3

def wc_turn(S, k):
    R = S["round"]
    f = "free"
    for r in ["health", "edu", "lux"]:
        if S["wc"][r] >= pop(S): use(S, r); f = "used"; break
    v = best_vacancy(S)
    if v is not None:
        staff(S, v); log(S, R, k, "wc", "assign", v)
    elif demo_ok(S):
        log(S, R, k, "wc", "demonstrate", pool_size(S)); S["wc"]["demo"] = True
    else:
        b = buy_choice(S)
        if b is not None:
            exec_plan(S, b); log(S, R, k, "wc", "buy", b[0], b[1])
            if f == "free" and S["wc"][b[0]] >= pop(S): use(S, b[0]); f = "used"
        else:
            bl = bill_choice(S, "wc")
            if bl is not None: propose(S, bl, "wc"); log(S, R, k, "wc", "propose", bl)
            elif S["wc"]["cubes"] >= 3: pressure(S, "wc"); log(S, R, k, "wc", "pressure")
    if f == "free" and S["wc"]["loans"] > 0 and wc_budget(S) >= 50:
        pay(S, "wc", "world", 50, "repay"); S["wc"]["loans"] -= 1

def target_prices(S):
    pol = S["pol"]
    return dict(food=best_price(food_import_price(S), price_opts("food")),
                lux=best_price(6 + tariff("lux", pol["trade"]), price_opts("lux")),
                health=best_price(SPRICE[pol["health"]], price_opts("health")),
                edu=best_price(SPRICE[pol["edu"]], price_opts("edu")))
def cc_reserve(S): return wage_bill(S, P_CC_OP) + len(ids(S, P_CC_OP)) * tm(S)
def local_price(S, r): return 10 if r == "infl" else S["cc"]["price"][r]
def margin(S, n):
    out, q, cost, w, sl = CARDS[n]
    return q * local_price(S, out) - wage_at(w, MINLV[S["pol"]["labor"]])
def card_ok(S, n):
    out, q, cost, w, sl = CARDS[n]
    return (cost <= S["cc"]["rev"] + S["cc"]["cap"] - cc_reserve(S) and take_crew(sl, S["wc"]["pool"]) is not None
            and (S["wc"]["demo"] or margin(S, n) > 0))
def build_choice(S):
    if len(ids(S, P_CC)) >= 12: return None
    best, m = None, -999
    for n in S["cc"]["market"]:
        mc = margin(S, n)
        if card_ok(S, n) and mc > m: best, m = n, mc
    return best
def build(S, n):
    i = f"c{S['cc']['nextid']}"
    pay(S, "cc", "world", CARDS[n][2], "capex")
    S["cc"]["nextid"] += 1; S["cc"]["market"].remove(n)
    S["cos"][i] = mk_co(n, "cc", 0, MINLV[S["pol"]["labor"]], [])
    staff(S, i)
    if S["wc"]["demo"] and not (pool_size(S) >= 2 + open_slots(S)): S["wc"]["demo"] = False
def export_plan(S):
    p = pop(S)
    fo = sum(S["cos"][i]["qty"] for i in ids(S, P_CC_OP) if S["cos"][i]["out"] == "food")
    x = dict(food=pos(S["cc"]["food"] - pos(p - fo)), lux=pos(S["cc"]["lux"] - p), health=pos(S["cc"]["health"] - p), edu=pos(S["cc"]["edu"] - p))
    out = []
    for (r, q, m) in EXPORT[(S["round"] - 1) % 4]:
        if x[r] >= q: x[r] -= q; out.append((r, q, m))
    return out
def cc_turn(S, k):
    R = S["round"]; f = "free"
    t = target_prices(S)
    if t != S["cc"]["price"]: S["cc"]["price"] = t; f = "used"
    n = build_choice(S)
    if n is not None:
        build(S, n); log(S, R, k, "cc", "build", n)
    else:
        txs = export_plan(S)
        if txs:
            for (r, q, m) in txs: gexp(S, r, "cc", q); pay(S, "world", "cc", m, "export")
            log(S, R, k, "cc", "export", len(txs))
        else:
            bl = bill_choice(S, "cc")
            if bl is not None: propose(S, bl, "cc"); log(S, R, k, "cc", "propose", bl)
            elif S["cc"]["cubes"] >= 3: pressure(S, "cc"); log(S, R, k, "cc", "pressure")
    if f == "free" and S["cc"]["loans"] > 0 and S["cc"]["rev"] + S["cc"]["cap"] - cc_reserve(S) >= 50:
        pay(S, "cc", "world", 50, "repay", cap_first=True); S["cc"]["loans"] -= 1

def capacity(S, own, r):
    if own == "cc": return 8 if r == "food" else (99999 if r == "infl" else 12)
    return 6 + sum(S["cos"][i]["qty"] for i in ids(S, P_PUB_ACTIVE) if S["cos"][i]["out"] == r)
def produce(S, i):
    c = S["cos"][i]; own, out, q = c["own"], c["out"], c["qty"]
    pay(S, own, "wc", cur_wage(S, i), "wage-cc" if own == "cc" else "wage-pub")
    stored = min(q, pos(capacity(S, own, out) - S[own][out]))
    gprod(S, out, own, q, stored)

def set_policy(S, p, new):
    old = S["pol"][p]
    if old == new: return
    log(S, S["round"], 0, "policy", p, old, new)
    S["pol"][p] = new
    if p == "fiscal":
        a, b = ROWS[old], ROWS[new]
        while a < b:
            a += 1; pay(S, "st", "world", 60, "capex")
            for i in [i for i in S["cos"] if S["cos"][i]["own"] == "st" and S["cos"][i]["row"] == a]:
                if can_staff(S, i): staff(S, i)
        while a > b:
            for i in [i for i in S["cos"] if S["cos"][i]["own"] == "st" and S["cos"][i]["row"] == a]: unstaff(S, i)
            pay(S, "world", "st", 60, "divest"); a -= 1
            for r in ["health", "edu", "infl"]:
                gdiscard(S, r, "st", pos(S["st"][r] - capacity(S, "st", r)))
    elif p == "labor":
        m = MINLV[new]
        for i, c in S["cos"].items():
            if c["lvl"] < m or c["own"] == "st" or not c["committed"]: c["lvl"] = m
    S["cc"]["price"] = target_prices(S)

def imf(S):
    log(S, S["round"], 0, "imf", S["st"]["loans"])
    for (p, t, w) in S["bills"]: gimp(S, "infl", w, 1); S[w]["bills"] += 1
    S["bills"] = []
    for p, sec in IMF_PROFILE: set_policy(S, p, sec)
    while S["st"]["loans"] > 0 and S["st"]["treasury"] >= 55:
        pay(S, "st", "world", 55, "repay"); S["st"]["loans"] -= 1
    S["st"]["writeoff"] += S["st"]["loans"]; S["st"]["loans"] = 0

def production(S):
    S["taxlabor"] = S["pol"]["labor"]
    for i in ids(S, P_PUB_OP): produce(S, i)
    for i in ids(S, P_CC_OP): produce(S, i)
    for c in S["cos"].values(): c["committed"] = False
    if S["wc"]["demo"]:
        l = min(pool_size(S), 12 - len(ids(S, P_CC)))
        gimp(S, "infl", "wc", 1); S["cc"]["vp"] -= l; S["wc"]["demo"] = False
        log(S, S["round"], 0, "wc", "demo-penalty", l)
    n = pop(S)
    for (w, p, a) in sources(S, "food"):
        if n == 0: break
        q = min(n, a); n -= q
        if q == 0: continue
        if w == "cc": pay(S, "wc", "cc", q * p, "sale-cc"); gmove(S, "food", "cc", "wc", q); guse(S, "food", "wc", q)
        else:
            t = tariff("food", S["pol"]["trade"])
            pay(S, "wc", "world", q * (p - t), "import"); pay(S, "wc", "st", q * t, "tariff")
            gimp(S, "food", "wc", q); guse(S, "food", "wc", q)
    lim = IMFLIM[S["pol"]["fiscal"]]
    while S["st"]["loans"] >= lim and S["st"]["treasury"] >= 55:
        pay(S, "st", "world", 55, "repay"); S["st"]["loans"] -= 1
    if S["st"]["loans"] >= IMFLIM[S["pol"]["fiscal"]]: imf(S)
    pay(S, "wc", "st", pop(S) * INCOME[(S["taxlabor"], S["pol"]["tax"])], "tax-wc")
    pay(S, "cc", "st", len(ids(S, P_CC_OP)) * tm(S), "tax-emp")
    pay(S, "cc", "st", corp_tax(S["pol"]["tax"], S["cc"]["rev"]), "tax-corp")

def leftward(frm, to): return to < frm
def favors(who, frm, to): return leftward(frm, to) if who == "wc" else leftward(to, frm)
def commit(need, have_): return 0 if need <= 0 else (need if need <= have_ else 0)
def elections(S):
    if not S["bills"]: return
    for who, n in (("wc", ceil_half(pop(S))), ("cc", ceil_half(len(ids(S, P_CC_OP))))):
        k = min(n, S[who]["cubes"]); S[who]["cubes"] -= k; S["bag"][who] += k
    S["bag"]["mc"] += 5
    for p in POLS:
        b = next((b for b in S["bills"] if b[0] == p), None)
        if b is None: continue
        _, t, who = b
        opp = "cc" if who == "wc" else "wc"
        frm = S["pol"][p]; agree = favors(opp, frm, t)
        c = dict(wc=0, cc=0, mc=0)
        for _ in range(5):
            tot = sum(S["bag"].values())
            if tot == 0: break
            S["seed"] = rng(S["seed"]); i = S["seed"] % tot
            col = "wc" if i < S["bag"]["wc"] else ("cc" if i < S["bag"]["wc"] + S["bag"]["cc"] else "mc")
            c[col] += 1; S["bag"][col] -= 1
        if agree:
            S[who]["cubes"] += c[who]; S[opp]["cubes"] += c[opp]
            if c[opp] > 0: S[opp]["vp"] += 1
            log(S, S["round"], 0, "vote", p, t, who, "pass", c[who], c[opp], 0, 0)
            set_policy(S, p, t); S[who]["vp"] += 3
        else:
            pv, ov, ip, io = c[who], c[opp], S[who]["infl"], S[opp]["infl"]
            x = commit(ov + io - pv, ip); y = commit(pv + ip + 1 - ov, io)
            win = pv + x >= ov + y
            guse(S, "infl", who, x); guse(S, "infl", opp, y)
            if win: S[who]["cubes"] += pv; S["bag"][opp] += ov
            else: S[opp]["cubes"] += ov; S["bag"][who] += pv
            log(S, S["round"], 0, "vote", p, t, who, "pass" if win else "fail", pv, ov, x, y)
            if win: set_policy(S, p, t); S[who]["vp"] += 3
        S["bills"] = [bb for bb in S["bills"] if bb[0] != p]; S[who]["bills"] += 1

def scoring(S):
    c = S["cc"]; c["cap"] += c["rev"]; c["rev"] = 0
    i = wealth_idx(c["cap"]); w = c["wmark"]
    c["vp"] += i + 3 * pos(i - w); c["wmark"] = max(w, i); S["round"] += 1

def pol_word(S): return "".join(S["pol"][p] for p in POLS)
def snapshot(S):
    f = S["flows"]
    S["hist"].append(dict(round=S["round"] - 1, wc_vp=S["wc"]["vp"], cc_vp=S["cc"]["vp"], wc_money=S["wc"]["money"],
        cc_cap=S["cc"]["cap"], treasury=S["st"]["treasury"], workers=S["wc"]["workers"], pop=pop(S),
        unemployed=pool_size(S), prosp=S["wc"]["prosp"], cc_cos=len(ids(S, P_CC)),
        wages_cum=-(f["wage-cc"]["cc"] + f["wage-pub"]["st"]), wc_loans=S["wc"]["loans"],
        cc_loans=S["cc"]["loans"], st_loans=S["st"]["loans"], policy=pol_word(S)))

def game_end(S):
    S["cc"]["vp"] -= 5 * S["cc"]["loans"]
    due = 55 * S["wc"]["loans"]; paid = min(due, 5 * (S["wc"]["money"] // 5))
    pay(S, "wc", "world", paid, "repay"); S["wc"]["vp"] -= (due - paid) // 5; S["wc"]["loans"] = 0
    a = sum(1 for p in POLS[:5] if S["pol"][p] == "A"); cn = sum(1 for p in POLS[:5] if S["pol"][p] == "C")
    S["wc"]["vp"] += pol_bonus(a); S["cc"]["vp"] += pol_bonus(cn)
    S["wc"]["vp"] += min(15, S["wc"]["money"] // 10)
    c = S["cc"]; c["vp"] += c["food"] // 2 + c["lux"] // 3 + c["health"] // 3 + c["edu"] // 3
    log(S, 5, 0, "end")

def play_round(S):
    if S["round"] != 1: prep(S)
    for k in range(1, 6): wc_turn(S, k); cc_turn(S, k)
    production(S); elections(S); scoring(S); snapshot(S)
    if S["round"] > 5: game_end(S)
def play_game(S):
    for _ in range(5): play_round(S)
    return S

# --------------------------------------------- reading Palimpsest output ----
def run_pal(src_text, name):
    path = os.path.join(os.environ.get("TMPDIR", "/tmp"), name)
    with open(path, "w") as f: f.write(src_text)
    env = dict(os.environ, PALIMPSEST_LIB=os.path.join(ROOT, "lib"))
    out = subprocess.run([BIN, path], capture_output=True, text=True, env=env).stdout
    lines, res = out.splitlines(), []
    for i, l in enumerate(lines):
        if l.startswith("display: "): res.append(l[len("display: "):])
        elif l == "display:": res.append(lines[i + 1])
    return res
def parse(s):
    toks = re.findall(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()]+', s)
    def go(i):
        if toks[i] == "(":
            out = []; i += 1
            while toks[i] != ")":
                x, i = go(i); out.append(x)
            return out, i + 1
        t = toks[i]
        if re.fullmatch(r"-?\d+", t): return int(t), i + 1
        return t, i + 1
    return go(0)[0]
def rec(t): return {e[0]: e[1] for e in t[1:]}

# ================================================================== checks ==
print("1. Baseline game: every round, flows, goods, final state")
S = play_game(setup())
pal = run_pal('''#fuel 900000000
import "hegemony.pal"
rule out : (out !s) => (shw-v (list (@ ?s hist) (@ ?s flows) (@ ?s gstat) (@ ?s wc) (@ ?s cc vp) (@ ?s cc rev) (@ ?s cc cap) (@ ?s st) (@ ?s world) (@ ?s loan-cause) (length (@ ?s events))))
main = (h-setup)
display (out (play-game main)) with normalize
''', "hx_base.pal")
T = parse(pal[0].strip('"'))
hist = [rec(r) for r in T[1:][0][1:]]
for h_py, h_pal in zip(S["hist"], hist):
    want = {k.replace("-", "_"): v for k, v in h_pal.items()}
    check(f"round {h_py['round']} history row", h_py, want)
check("number of rounds", len(S["hist"]), len(hist))
flows = {k: rec(v) for k, v in rec(T[1:][1]).items()}
check("flow matrix (17 categories x 4 sectors)", S["flows"], flows)
check("goods statistics", S["gstat"], {k: rec(v) for k, v in rec(T[1:][2]).items()})
wc = rec(T[1:][3]); wc["pool"] = rec(wc["pool"]); wc["demo"] = wc["demo"] == "true"
check("final Working Class record", S["wc"], wc)
check("final CC vp / rev / cap", (S["cc"]["vp"], S["cc"]["rev"], S["cc"]["cap"]), tuple(T[1:][4:7]))
check("final State record", S["st"], rec(T[1:][7]))
check("world balance", S["world"], T[1:][8])
check("loan causes", S["cause"], rec(T[1:][9]))
check("number of logged events", len(S["events"]), T[1:][10])
check("money conserved (python)", money_total(S), 0)
check("flow rows sum to zero (python)", all(sum(r.values()) == 0 for r in S["flows"].values()), True)

print("2. Counterfactual games (Labor x Trade at the start)")
def start_at(l, tr):
    S = setup(); S["pol"]["trade"] = tr
    if l != S["pol"]["labor"]:
        S["pol"]["labor"] = l
        for c in S["cos"].values(): c["lvl"] = MINLV[l]
    S["cc"]["price"] = target_prices(S); return S
src = '#fuel 2000000000\nimport "hegemony.pal"\n' + \
  'rule start-at : (start-at ?l ?tr !s) => (reprice (relabor ?l (set@ ?s pol trade ?tr)))\n' + \
  'rule relabor : (relabor ?l ?s) => (if (= ?l (@ ?s pol labor)) ?s (each (relevel (min-level ?l)) (co-ids ?s) (set@ ?s pol labor ?l)))\n' + \
  'rule key : (key !g) => (shw-v (list (@ ?g wc vp) (@ ?g cc vp) (@ ?g wc money) (@ ?g cc cap) (@ ?g st treasury) (pol-word ?g) (@ ?g flows sale-cc wc)))\n' + \
  'main = (h-setup)\n' + "".join(f"display (key (play-game (start-at {l} {tr} main))) with normalize\n" for l in SECS for tr in SECS)
outs = run_pal(src, "hx_cf.pal")
for (l, tr), o in zip([(l, tr) for l in SECS for tr in SECS], outs):
    G = play_game(start_at(l, tr))
    got = [G["wc"]["vp"], G["cc"]["vp"], G["wc"]["money"], G["cc"]["cap"], G["st"]["treasury"], pol_word(G), G["flows"]["sale-cc"]["wc"]]
    want = parse(o.strip('"'))[1:]
    check(f"Labor {l} / Trade {tr}", got, want)

print("3. Regime atlas")
def wbill(l): return 2 * wage_at((25,20,15), MINLV[l]) + 2 * wage_at((30,20,10), MINLV[l])
def pf(tr): return best_price(10 + tariff("food", tr), [9,12,15])
def food(p, tr): return min(p,4) * pf(tr) + pos(p-4) * (10 + tariff("food", tr))
def s_wc(p, l, t, tr): return wbill(l) - food(p, tr) - p * INCOME[(l, t)]
def p_star(l, t, tr):
    for p in range(10, 2, -1):
        if s_wc(p, l, t, tr) >= 0: return p
    return 2
def lux_val(tr): return 6 * best_price(6 + tariff("lux", tr), [5,8,10])
def pre(p, l, t, h, e, tr): return min(p,4) * pf(tr) + lux_val(tr) - 2 * wage_at((25,20,15), MINLV[l]) - 2 * tax_mult(t, h, e)
def s_cc(p, l, t, h, e, tr): x = pre(p, l, t, h, e, tr); return x - corp_tax(t, pos(x))
def s_st(p, l, t, h, e, tr):
    x = pre(p, l, t, h, e, tr)
    return p * INCOME[(l, t)] + pos(p-4) * tariff("food", tr) + 2 * tax_mult(t, h, e) + corp_tax(t, pos(x)) - 2 * wage_at((30,20,10), MINLV[l])
profiles = list(itertools.product(SECS, repeat=5))
atlas = []
for p in range(3, 9):
    atlas.append([p, sum(s_wc(p,l,t,tr) < 0 for l,t,h,e,tr in profiles),
                  sum(s_wc(p,l,t,tr) - p * SPRICE[h] >= 0 for l,t,h,e,tr in profiles),
                  sum(s_cc(p,*x) < 0 for x in profiles), sum(s_st(p,*x) < 0 for x in profiles),
                  sum(s_wc(p,x[0],x[1],x[4]) >= 0 and s_cc(p,*x) >= 0 and s_st(p,*x) >= 0 for x in profiles)])
out = run_pal('#fuel 900000000\n' + open(os.path.join(ROOT, "examples/hegemony-regimes.pal")).read().split("main =")[0].replace('import "../lib/hegemony.pal"', 'import "hegemony.pal"') +
              'rule atl : (atl) => (shw-v (map atl-row (range 3 8)))\nrule app-atl-row : (app atl-row ?p) => (list ?p (count-if (wc-deficit ?p) ?ps) (count-if (prosper-ok ?p) ?ps) (count-if (cc-deficit ?p) ?ps) (count-if (st-deficit ?p) ?ps) (count-if (all-ok ?p) ?ps)) where ?ps <- (profiles5)\n'
              'rule core : (core) => (shw-v (map core-k (secs)))\nrule app-core-k : (app core-k ?l) => (list (p-star ?l A A) (p-star ?l B B) (p-star ?l C C) (p-star ?l A C) (s-wc 5 ?l B B))\n'
              'main = 0\ndisplay (atl) with normalize\ndisplay (core) with normalize\n', "hx_atlas.pal")
check("atlas counts (Pop 3..8)", atlas, [r[1:] for r in parse(out[0].strip('"'))[1:]])
core = [[p_star(l,"A","A"), p_star(l,"B","B"), p_star(l,"C","C"), p_star(l,"A","C"), s_wc(5,l,"B","B")] for l in SECS]
check("Malthusian bounds p* and S_wc(5)", core, [r[1:] for r in parse(out[1].strip('"'))[1:]])
check("T1 S_wc strictly decreasing in Pop", all(s_wc(p+1,l,t,tr) < s_wc(p,l,t,tr) for l,t,h,e,tr in profiles for p in range(3,10)), True)
check("T2 Labor dominance for Pop 3..9", all(l == "A" or s_wc(p,toward_a(l),t,tr) > s_wc(p,l,t,tr) for l,t,h,e,tr in profiles for p in range(3,10)), True)
check("T3 exact claw-back at Pop 10, Tax A", s_wc(10,"A","A","B") == s_wc(10,"B","A","B"), True)

print("4. Exact election odds")
def C(n, k): return 0 if k < 0 or k > n else __import__("math").comb(n, k)
def p_pass(w, c, m, iw, ic):
    n = w + c + m; d = min(5, n); num = 0
    for i in range(d + 1):
        for j in range(d - i + 1):
            x = commit(j + ic - i, iw); y = commit(i + iw + 1 - j, ic)
            if i + x >= j + y: num += C(w, i) * C(c, j) * C(m, d - i - j)
    return Fraction(num, C(n, d))
table = [[w, int(p_pass(w,9,13,0,0)*10000), int(p_pass(w,9,13,1,3)*10000), int(p_pass(w,9,13,3,1)*10000),
          int(p_pass(w+3,9,13,0,0)*10000) - int(p_pass(w,9,13,0,0)*10000)] for w in range(2, 15, 2)]
out = run_pal('import "hegemony-loops.pal"\nrule pp : (pp ?w ?c ?m ?iw ?ic) => (/ (* 10000 (pnum ?q)) (pden ?q)) where ?q <- (p-pass ?w ?c ?m ?iw ?ic)\n'
              'rule row : (row ?w) => (list ?w (pp ?w 9 13 0 0) (pp ?w 9 13 1 3) (pp ?w 9 13 3 1) (- (pp (+ ?w 3) 9 13 0 0) (pp ?w 9 13 0 0)))\n'
              'main = 0\ndisplay (shw-v (map rw (list 2 4 6 8 10 12 14)))  with normalize\nrule app-rw : (app rw ?w) => (row ?w)\n', "hx_odds.pal")
check("odds table x10000", table, [r[1:] for r in parse(out[0].strip('"'))[1:]])
G = [0,2,4,6,8,10,12]
mono = all(p_pass(w,c,m,iw,ic) <= p_pass(w+2,c,m,iw,ic) and p_pass(w,c+2,m,iw,ic) <= p_pass(w,c,m,iw,ic)
           and p_pass(w,c,m,iw,ic) <= p_pass(w,c,m,iw+1,ic) and p_pass(w,c,m,iw,ic+1) <= p_pass(w,c,m,iw,ic)
           for w in G for c in G for m in (5,13) for iw in (0,1,3) for ic in (0,1,3))
check("T8 monotonicity on the 882-point grid", mono, True)

print("5. Debt theorems (re-derived in Python)")
amts = [5,15,30,45,60,85]
def seq_loans(m, xs):
    L = 0
    for a in xs:
        if m < a: k = ceil_div(a - m, 50); L += k; m += 50 * k
        m -= a
    return L
seqs = [list(p) for p in itertools.product(amts, repeat=2)] + [list(p) for p in itertools.product(amts, repeat=3)]
check("T5 borrowing path-independence (5040 cases)", all(seq_loans(m, xs) == ceil_div(pos(sum(xs) - m), 50) for m in range(0, 100, 5) for xs in seqs), True)
check("T6 order matters with an inflow: (wage;food) vs (food;wage) loans", (seq_loans(0+40, [30]), seq_loans(0, [30])), (0, 1))
def orbit(s, L, m, n=30):
    out = []
    for _ in range(n):
        m -= 5 * L
        if m < 0: k = ceil_div(-m, 50); L += k; m += 50 * k
        if s >= 0: m += s
        else:
            if m < -s: k = ceil_div(-s - m, 50); L += k; m += 50 * k
            m -= -s
        if L > 0 and m >= 50: m -= 50; L -= 1
        out.append(L)
    return out
def kind(L0, ls):
    if ls[-1] == 0: return "repaid"
    if all(x == L0 for x in ls): return "fixed"
    return "runaway" if ls[-1] > L0 + 3 else "other"
def predicted(s, L0): return "repaid" if s > 5*L0 else (("repaid" if L0 == 0 else "fixed") if s == 5*L0 else "runaway")
check("T7 debt-spiral threshold (357 orbits)", all(kind(L0, orbit(s, L0, m)) == predicted(s, L0)
      for s in range(-20, 61, 5) for L0 in range(0, 7) for m in (0, 25, 45)), True)

print("6. Causal-loop diagram: elementary cycles")
nodes = "E W M R N H P F T G U Dm Vw Vc L D K Pub".split()
edges = [("E","W",1),("W","M",1),("M","R",1),("R","N",1),("N","E",1),("W","R",-1),("M","H",1),("H","P",1),("P","F",1),("F","M",-1),
         ("P","T",1),("T","M",-1),("T","G",1),("P","U",1),("E","U",-1),("U","Dm",1),("Dm","N",1),("P","Vw",1),("N","Vc",1),
         ("Vw","L",1),("Vc","L",-1),("L","W",1),("D","M",-1),("M","D",-1),("N","K",1),("K","R",-1),("K","G",1),("Pub","W",1),("Pub","G",-1),("G","Pub",1)]
sign = {(a, b): s for a, b, s in edges}; idx = {n: i for i, n in enumerate(nodes)}
cycles = []
def dfs(s, cur, path):
    for (a, b, _) in edges:
        if a != cur: continue
        if b == s: cycles.append(list(path))
        elif idx[b] > idx[s] and b not in path: dfs(s, b, path + [b])
for s in nodes: dfs(s, s, [s])
def pol_(c):
    p = 1
    for a, b in zip(c, c[1:] + c[:1]): p *= sign[(a, b)]
    return "R" if p > 0 else "B"
mine = sorted((pol_(c), " -> ".join(c + c[:1])) for c in cycles)
out = run_pal('#fuel 900000000\nimport "hegemony-loops.pal"\nmain = 0\ndisplay (loops-view (classify-loops)) with normalize\n', "hx_cld.pal")
txt = subprocess.run([BIN, os.path.join(os.environ.get("TMPDIR", "/tmp"), "hx_cld.pal")], capture_output=True, text=True,
                     env=dict(os.environ, PALIMPSEST_LIB=os.path.join(ROOT, "lib"))).stdout.split("display:\n", 1)[1]
theirs = sorted((l[0], l[5:].strip()) for l in txt.splitlines() if l[:1] in ("R", "B"))
check("17 cycles with identical polarity", mine, theirs)
check("8 reinforcing, 9 balancing", (sum(k == "R" for k, _ in mine), sum(k == "B" for k, _ in mine)), (8, 9))

print("\nALL AGREE" if ok_all else "\nDISAGREEMENT FOUND")
sys.exit(0 if ok_all else 1)
