# The Economy of *Hegemony* as a Term-Rewriting System

*A formal model of the 2-player game (Working Class vs. Capitalist Class, passive
State), its feedback loops, and eleven machine-checked results.*

Reproduce everything with:

```sh
cargo build --release
./verify-hegemony.sh                       # 9 checks, ~3 min
python3 crosscheck/hegemony_crosscheck.py  # 37 independent checks (part of the above)
```

| file | role |
|---|---|
| `lib/hegemony.pal` | the model: rule tables, ledger, phases, behaviour, IMF, elections, rendering |
| `lib/hegemony-loops.pal` | the causal-loop diagram as data, cycle enumeration, probes, exact election odds |
| `examples/hegemony-game.pal` | the game as a self-rewriting program (one round per run, quine at game end) |
| `examples/hegemony-loops.pal` | §4: the 17 feedback loops and the verification of all 30 edges |
| `examples/hegemony-regimes.pal` | §5: the reproduction map over all 243 policy profiles |
| `examples/hegemony-debt.pal` | §6: three theorems about forced borrowing |
| `examples/hegemony-politics.pal` | §7: election odds and the IMF |
| `examples/hegemony-policy.pal` | §8: nine counterfactual games |
| `crosscheck/hegemony_crosscheck.py` | an independent Python implementation of the same specification |

---

## 1. What is being modelled

The economy of a round of *Hegemony* is a map **F : X → X** on a finite but
large state space **X**. A state is one Palimpsest term, a record
(`h-setup` in `lib/hegemony.pal` builds the 2-player initial state) holding:

* the seven Policies `pol` ∈ {A,B,C}⁷ and the proposed Bills;
* the Working Class: money, Influence, Prosperity, VP, Loans, Workers, the
  unemployed pool by skill (`u`, `agri`, `lux`, `health`, `edu`, `media`), goods;
* the Capitalist Class: Revenue, Capital, VP, Loans, storage, prices, market;
* the State: Treasury, Loans, Public Services; the voting bag; the RNG seed;
* every Company (owner, output, wages L3/L2/L1, level, slots, crew, row);
* bookkeeping: the **flow matrix**, goods statistics, loan causes, event log, history.

One round, **F = Scoring ∘ Elections ∘ Production ∘ Action⁵ ∘ Preparation**, is
written as *equations* (`rule`): applied exhaustively by normal-order
rewriting, they compute the next state as the normal form of
`(play-round S)`. Playing the game is iterating F five times. In
`examples/hegemony-game.pal` that iteration is a **transition** (§2): each run
of the program rewrites the file's own `main` — the game state — by exactly one
round, and after round 5 the transition's guard fails, the rewrite is the
identity, and the file becomes a byte-identical quine. The fixed point is a
certificate that the game is over.

### Fidelity

**Exact from the rulebook (v1.2):** the population track (Pop = ⌊workers/3⌋,
max 10), the Income-Tax table, the Tax Multiplier formula, the Corporate-Tax
table, the Wealth table and its +3 VP bonus, wage floors by Labor Market,
welfare prices, tariffs and import prices, Public-Sector size and IMF loan
limits, immigration, storage capacities (8 Food, 12 others; Public Services =
production + 6), Loans (forced only, 50 each, 5 interest), the IMF profile
(1C 2C 3A 4B 5C 6B 7B), the election procedure (5 cubes drawn, 5 neutral Middle
Class cubes per refill in 2-player games, ties to the proposer, 3/1 VP),
Prosperity scoring, Demonstrations, and the end-game scoring. The 2-player setup
(policies 1C 2B 3A 4B 5C 6B 7B, 120 / 30 / 120 money, the four starting
Companies with their printed cards, Public Services 5/5/3) is reproduced.

**Card values read from the rulebook's pictures:** Supermarket, Shopping Mall,
Clinic, College (starting Companies) and Stadium, Institute of Technology,
Radio Station (the p. 18 market example).

**Assumed (not printed legibly) — each collected in one rule so it can be
corrected:** the three 2-player Public Companies (2 Workers, cost 20, wages
30/20/10, output 4 Health / 4 Education / 3 Influence), the market-deck order,
the immigration deck, the four export cards (unit prices inside the bands
printed on the board), and a 25-cube supply per class.

**Abstracted:** Action cards are not modelled — every Main Action is a Basic
Action, which the rules always allow (any card may be discarded for one), so
the model is the game restricted to Basic + Free Actions, a *legal subgame*.
Strikes, Trade Unions, Business Deals, the Free Trade Zone, Machinery and
Immediate Votes are not used by the behavioural rules.

**Behaviour.** Each class follows a deterministic priority list of guarded
rules (§3.4), and election draws use the deterministic hash `rng` seeded in the
state. The whole game is therefore a function of its initial state; every
number in this document is reproducible bit for bit.

---

## 2. Extensions to Palimpsest

The model needed eight changes to the interpreter. All are additive or
semantics-preserving: the 37 Rust unit tests and all nine pre-existing
verification suites pass unchanged (including their exact fuel fingerprints).

| change | why |
|---|---|
| **Shared terms** (`Term::List(Rc<Vec<Term>>)`) | A game state is ~1,500 nodes and is bound, copied into right-hand sides and rebuilt along one path by `oncetd` at every step. With deep copies one round took minutes; with O(1) clones it takes 0.3 s. The heavy pre-existing suites also run ~10× faster (games 68 s → 6 s, logos 83 s → 7 s). |
| **True head index** | `rules` used to scan every rule with a head check; dispatch now merges the rules pinned to the subject's head with the wildcard rules, in source order, allocation-free. Behaviour and fuel are identical. |
| **Record primitives** `@ set@ add@ has@ put@ del@ keys@ sum@` | O(n) native field access on `(rec (k v) ...)`, with paths for nested records. **Closed world:** a missing key never fires, so a typo is a visibly stuck term, never a silently invented field. |
| **Record keys are labels** | Inside `(rec (k v) ...)` only values are evaluation positions. Before this, a field `(pop 3)` was rewritten by the rule `(pop ?s)` — a real bug the model hit. |
| **`transition`** items | Rules reachable only by name from a strategy, never via `rules`. This is rewriting logic's split between *equations* (accounting identities, applied to normal form) and *rules-as-transitions* (one game round, applied under control). Without it, a self-rewriting program cannot advance by exactly one round. |
| **`assert TERM with S`** | PASS iff the normal form is `true`; any FAIL makes the run exit non-zero. Every theorem below is an `assert`. |
| **`--stats`** | A rewrite profile (firings per rule) — a cheap derivation certificate. |
| **`#rebind main`** | Opt-in: after `rewrite self`, later commands see the rewritten subject, so the dashboard shows the round just played. |

The library also adds the strict helpers `eq?` and `shw-v`: `equal?` and `shw`
match *any* term on sight, so applied to an unevaluated call they compare or
print the call, not its value. The Python cross-check (§9) caught exactly this
in the model (the Capitalist's price check compared a value with a pending
`@`-call, so it "repriced" every turn and wasted its Free Action). That is the
most important practical lesson for writing large models in a normal-order
rewriting language: **every rule that pattern-matches "any term" must force its
argument (`!x`)**.

---

## 3. The model

### 3.1 The ledger (double entry)

Exactly three rules change a money balance — `credit`, `debit`, and `borrow` —
and they are called only from `pay` / `pay-c`:

```
rule pay : (pay ?from ?to ?amt ?cat ?s) => ?s3
  where ?s1 <- (debit ?from ?amt ?cat ?s), ?s2 <- (credit ?to ?amt ?s1),
        ?s3 <- (flow ?cat ?from ?to ?amt ?s2)
```

Accounts are the Working Class (`wc`), the Capitalist (`cc`, Revenue then
Capital), the State (`st`), and `world` — the Supply, the Foreign Market and the
bank together: the money issuer, whose balance is minus the money in the
economy. `flow` posts −amt in the payer's column and +amt in the payee's column
of row `cat` of a 17×4 **transactions-flow matrix** (a Godley table). A
shortfall on a payment calls `cover-or-borrow`, which takes ⌈shortfall/50⌉
Loans from `world` (Loans are never taken voluntarily) and records their cause.

### 3.2 Goods and Workers

Likewise `gmove / gprod / guse / gexp / gimp / gdiscard` are the only rules
that change a stock, and `staff / unstaff` the only ones that move Workers
between the unemployed pool and a crew.

### 3.3 The phases

`prep-phase` (interest, State repayment, Prosperity −1, market refill, +2
Workers + immigration), `action-phase` (5 × Working Class turn, Capitalist turn),
`production-phase` (Public Companies, then Capitalist Companies pay Wages and
produce up to capacity; Demonstration penalty; Cover Needs; IMF check; taxes),
`election-phase` (refill bag; for each Bill in policy order: draw, commit
Influence, tally, apply), `scoring-phase` (Revenue → Capital, Wealth VP), and
`game-end`.

### 3.4 Behaviour (the decision rules)

*Working Class, each turn.* Free Action: use a held set of Health, Education or
Luxury if it holds Population tokens of one. Main Action, first applicable:
**assign** the unemployed to the staffable vacancy paying the highest Wage;
**demonstrate** if the unemployed exceed open slots by 2; **buy** the cheapest
affordable full set of Health / Education / Luxury (≤ 2 sources, ≤ Pop each),
where *affordable* means within money minus a reserve (Food at the import
price + Income Tax − expected Wages), then use it; **propose** a Bill toward A
(Labor, Health, Education, Fiscal); **apply pressure**. If the Free Action is
unused, repay a Loan when the budget allows.

*Capitalist, each turn.* Free Action: reset prices to the **best response** —
the highest printed price not above the competing source (import price incl.
tariff for Food/Luxury, public price for Health/Education). Main Action:
**build** the affordable market Company that the unemployed can staff at once
with the highest margin (output × local price − minimum Wage; must be positive
unless a Demonstration is on); **export** the stock above a domestic reserve
(Population units; for Food, net of own production); **propose** a Bill toward C
(Labor, Tax, Health, Education, Fiscal); **apply pressure**. Repay a Loan when
cash above the round's reserve allows.

*Elections.* Each side commits the least Influence that *guarantees* its result
against the opponent's entire Influence, or nothing if no amount does.

### 3.5 The baseline game

`examples/hegemony-game.pal`, run six times (5 × WROTE, then FIXED POINT):

```
     rnd   WC-VP   CC-VP    WC-$  CC-cap State-$     pop   unemp   prosp  CC-cos  policy
       1       6      15      53      63     146       3       1       1       5  CABBCBB
       2      12      28      58      94     160       5       5       1       5  CBCBBBB
       3      18      39      29     116     128       6       7       1       6  BBCBCBB
       4      21      51      31     128     201       7       8       0       6  CBCBBBB
       5      24      54      14     148     158       8      11       0       6  BBCCBBB
final (after end-game scoring): Working Class 25, Capitalist Class 61
```

and its transactions-flow matrix over the whole game:

```
category         WC       CC    State    World  row-sum
wage-cc         390     -390        0        0        0
wage-pub        220        0     -220        0        0
sale-cc        -435      435        0        0        0
sale-st         -65        0       65        0        0
export            0       99        0      -99        0
tax-wc         -126        0      126        0        0
tax-emp           0      -38       38        0        0
tax-corp          0      -89       89        0        0
capex             0      -24     -120      144        0
divest            0        0       60      -60        0
loan              0       50        0      -50        0
interest          0      -15        0       15        0
column          -16       28       38      -50        0
```

(rows with all zeros omitted). Two things are visible at once: the Working
Class spends **more than all its Capitalist wages** on Capitalist goods (435 vs
390) — the circuit of §4 closes with a leak toward the Capitalist — and every
Food token the Working Class ate in this game was bought from the Capitalist at
15 (tariff B makes the import cost 15 as well): the Food bill is the largest
single drain on the Working Class.

---

## 4. Feedback loops

### 4.1 The causal-loop diagram

`lib/hegemony-loops.pal` states a signed digraph over 18 variables:

| | | | |
|---|---|---|---|
| **E** staffed Companies | **W** Wages received | **M** WC money | **R** CC cash |
| **N** CC Companies | **H** Health used | **P** Workers | **F** Food bill |
| **T** Income Tax | **G** Treasury | **U** unemployed | **Dm** Demonstration |
| **Vw** WC cubes in bag | **Vc** CC cubes in bag | **L** Labor Market leftness | **D** WC Loans |
| **K** CC taxes | **Pub** operating Public Companies | | |

with 30 signed edges, each annotated with the rules that create it (e.g.
`P → F (+)`: *Food needs = Population* — `cover-needs`).

### 4.2 Loop enumeration (Theorem L1)

The program enumerates every **elementary cycle** of the digraph exactly once
(depth-first from each node, visiting only nodes after it, so each cycle is
found from its least node), and computes its polarity as the product of edge
signs. Result: **17 elementary cycles — 8 reinforcing, 9 balancing.**

| | len | loop | reading |
|---|---|---|---|
| **R1** | 5 | E → W → M → R → N → E | **the wage–demand circuit** (Kalecki): wages become demand, demand becomes profit, profit becomes companies, companies become jobs |
| **B1** | 4 | E → W → R → N → E | **profit squeeze**: the same wages are the Capitalist's cost |
| **B2** | 4 | M → H → P → F → M | **Malthusian loop**: Prosperity via Health adds Workers, who must be fed |
| **B3** | 4 | M → H → P → T → M | the same through Income Tax |
| **R2** | 6 | W → M → H → P → Vw → L → W | **demographic power**: a bigger Working Class puts more cubes in the bag and wins the wage floor |
| **R3** | 5 | W → R → N → Vc → L → W | **capture**: lower wages → profit → companies → CC cubes → lower wages (two negative edges: reinforcing) |
| **B4** | 6 | W → M → R → N → Vc → L → W | prosperity of the Capitalist erodes the wage floor that feeds its demand |
| **R4** | 2 | M → D → M | **debt spiral**: low money forces Loans, Loans cost interest |
| **B5** | 2 | G → Pub → G | **fiscal discipline**: public jobs drain the Treasury; a drained Treasury brings the IMF, which shuts public jobs |
| **R5** | 7 | W → M → H → P → T → G → Pub → W | **welfare circuit**: taxes on a growing population fund public wages |
| **R6** | 7 | W → M → R → N → K → G → Pub → W | corporate taxes fund public wages |
| **B6** | 3 | R → N → K → R | **tax drag**: every operational Company raises Employment Tax |
| **B7** | 4 | E → U → Dm → N → E | **Demonstration**: unemployment forces building, which absorbs it |
| B8 | 6 | W → R → N → K → G → Pub → W | |
| R7, R8, B9 | 8–10 | longer composites through H → P → U → Dm | |

### 4.3 Every edge is a property of the rules (Theorem L2)

A causal-loop diagram is only as good as its edge signs. Each edge X → Y
carries a **probe**: an intervention that raises X, the piece of the round in
which the effect happens, and a measurement of Y. The program computes the
finite difference **Δ = Y(T(I(S))) − Y(T(S))** — a derivative of the rewriting
system itself — at eight base states: the setup, the states at the start of
rounds 2–5 of the baseline game, a *stress* state (round 3 with an empty WC
purse and an indebted, empty Treasury), and two *excitation* states built so
that the conditional channels can fire. Interventions inject money through the
ledger (category `shock`) and Workers through the pool, so every probed state
still satisfies all conservation laws.

An edge is **strict** if Δ has its sign at every base, **weak** if Δ never has
the wrong sign and is nonzero somewhere, and **FAIL** otherwise — including the
case where Δ is zero everywhere (unverified is not confirmed).

```
edge       sgn verdict  deltas at: setup    r2     r3     r4     r5 stress   ex1    ex2
E -> W     pos strict      20     30     20     20     20     20     30     20
W -> M     pos weak        10      0     15     20     30     15      0     10
M -> R     pos weak        16     32     40     48     30      0      0     16
R -> N     pos weak         0      0      1      0      0      0      0      1
N -> E     pos weak         1      0      1      0      0      1      1      1
W -> R     neg weak       -10      0    -15    -20    -30    -15      0    -10
M -> H     pos weak         0      0      0      0     14      0      0      0
H -> P     pos strict       1      1      1      1      1      1      1      1
P -> F     pos strict      15     15     15     15     15     15     15     15
F -> M     neg weak        -3      0      0      0      0      0      0     -3
P -> T     pos strict       4      6      4      4      4      4      7      4
T -> M     neg weak        -9     -3     -5     -6     -7     -7      0     -9
T -> G     pos weak         9      9      5      6      7      7      0      9
P -> U     pos strict       3      3      3      3      3      3      3      3
E -> U     neg weak        -2      0     -2     -2     -2     -2     -2     -2
U -> Dm    pos weak         1      0      1      0      0      1      0      1
Dm -> N    pos weak         0      0      0      0      0      0      1      0
P -> Vw    pos weak         0      0      0      1      0      0      0      0
N -> Vc    pos weak         1      0      0      1      0      0      1      1
Vw -> L    pos strict    1144    475    760    930    634    760   1144   1144
Vc -> L    neg strict   -1333   -219   -542   -802   -753   -542  -1333  -1333
L -> W     pos weak        10      0     15     20     30     15      0     10
D -> M     neg strict      -5     -5     -5     -5     -5     -5     -5     -5
M -> D     neg weak         0      0      0      0      0      0     -1      0
N -> K     pos strict       5      3      1      1      1      1      5      5
K -> R     neg weak        -4     -3      0      0      0      0     -4     -4
K -> G     pos weak         4      3      0      0      0      0      4      4
Pub -> W   pos strict      60     90     60     60     60     60     90     60
Pub -> G   neg strict    -120   -150   -120   -120   -120   -120   -150   -120
G -> Pub   pos weak         0      0      0      0      0      3      0      0
all edge signs confirmed by the model: true
```

(The `Vw → L` and `Vc → L` deltas are changes in the exact probability that a
Labor Market Bill toward A passes, in parts per 10,000 — see §7.) Hence every
loop polarity in §4.2 is a theorem about the model, not a drawing.

The probes did more than confirm: the first version of the table had six
FAILs, and each taught something. `T → M` and `K → R` looked *positive* because a
higher tax can force a Loan, which raises cash — the right variable is money
**net of Loan principal**. `Pub → G` looked positive at the stress state because
extra public spending triggered the IMF, which **writes off** the State's debt —
a moral-hazard nonlinearity; the edge's true content is the Treasury's
*outlay*. `E → U`, `Dm → N`, `M → D` and `G → Pub` were zero everywhere until bases
were built in which the channel can fire.

### 4.4 What the weak edges say about the game

*Weak* means *conditional*, and the conditions are the economics:

* **R → N is almost never active**: cash is rarely what stops the Capitalist from
  building. The binding constraint is **staffing**: a Company can be built only
  if the unemployed include a Worker with the right skill, and new Workers
  arrive unskilled (2 per round + immigration). Unemployment in the baseline
  rises from 1 to 11 while the Capitalist sits on 148 Capital. The wage–demand
  circuit R1 is throttled by the **skills mismatch**, which only Education (the
  Working Class's choice) can relieve.
* **Dm → N fires only at the excitation base**: a Demonstration changes the
  Capitalist's behaviour only when the staffable Companies are unprofitable,
  because otherwise it would have built anyway. Its real bite is the VP
  penalty (the baseline Capitalist loses 6 VP to one in round 5).
* **M → H fires only once on the baseline path**: with Food at 15, the Working
  Class almost never has a full Health set within its budget. Prosperity is
  priced out — which is what §5 quantifies.

---

## 5. The reproduction map (`examples/hegemony-regimes.pal`)

Fix the setup board (the four staffed starting Companies at minimum Wage, the
Capitalist at its best-response prices, 4 Food per round from its Supermarket,
imports for the rest) and compute one round's accounts *with the model's own
functions* as a function of the policy profile and Population p:

* W(L) — Wages: 110 / 80 / 50 for Labor A / B / C;
* food(p) = min(p,4)·p_cc + max(0,p−4)·p_import;
* S_wc(p) = W − food(p) − p · rate(L,T) — the Working Class's surplus;
* **p\*** = the largest Population with S_wc ≥ 0.

```
 Labor   Tax Trade     W   CCf   imp  rate    S3    S5    S7    p*
     A     A     B   110    15    15     7    44     0   -44     5
     A     C     C   110     9    10     5    68    39     9     7
     B     A     B    80    15    15     4    23   -15   -53     4     <- the setup
     B     B     C    80     9    10     4    41    14   -14     6
     C     C     B    50    15    15     3    -4   -40   -76     2
   (27 rows in the program's output)
```

**Theorem R1 (Malthusian bound).** For all 243 profiles of Policies 2–6, S_wc
is strictly decreasing in Population (each extra Population costs at least 9 in
Food and 1 in tax), so the balancing loop B2 has a finite bound p\* at every
policy. *At the setup's policies p\* = 4*: the game starts at Population 3 and
the Working Class gains ≥ 3 Workers (≥ 1 Population) per round, so **after one
round it is in structural deficit unless employment grows** — exactly what the
baseline shows (WC money stalls; Prosperity decays to 0).

**Theorem R2 (Labor-Market dominance).** Moving Labor one step toward A raises
S_wc at every Population 3–9 under every Taxation and Trade setting.

**Theorem R3 (exact claw-back).** The raise from Labor B to A is 30 per round
on this board, and the Income-Tax table's step is 3 / 2 / 1 per Population
under Taxation A / B / C. At Population 10 under Taxation A the two cancel
**exactly**: S_wc(10, A, A) = S_wc(10, B, A). The Socialist wage floor is fully
taxed back from a large Working Class under a Socialist tax policy.

**Theorem R4 (the growth imperative).**

```
        Pop WC-deficit  WC+Health CC-deficit St-deficit     all>=0
          3         36        165         17        168         39
          4         54        108          3        129         60
          5        144         42          3         90         18
          6        189         18          3         53          7
          7        225          6          3         31          0
          8        243          0          3         24          0
```

From Population 7 on, **no policy profile** keeps the Working Class, the
Capitalist and the State all solvent on the setup board, and from Population 8
none even keeps the Working Class alone solvent. Policy can move the frontier
(Free Trade and a Socialist labor market push p\* to 7), but not abolish it:
the economy must grow — more staffed Companies — to reproduce itself, and
growth runs through the skill-constrained channel of §4.4.

---

## 6. Debt (`examples/hegemony-debt.pal`)

**Theorem D1 (borrowing is path-independent without inflows).** From money m,
paying mandatory amounts a₁…aₙ one after another forces exactly
⌈max(0, Σaᵢ − m)/50⌉ Loans, whatever their order and however the total is
split. *Proof sketch:* after each payment the purse holds m + 50Kₜ − Aₜ ≥ 0
with Kₜ minimal, and Aₜ is nondecreasing, so Kₙ is the minimal K for the whole
sum. *Check:* the model's own `pay` on all 20 × (36 + 216) = **5,040** cases
(m = 0…95 step 5, all ordered pairs and triples from {5,15,30,45,60,85}).

**Theorem D2 (phase order is load-bearing).** With an inflow in between, order
matters: from an empty purse, "receive a 40 Wage, then pay 30 for Food" ends
with (money 10, 0 Loans) while "pay 30, then receive 40" ends with (60, 1 Loan).
The two rewrite sequences reach **different normal forms** — a non-joinable
critical pair — so the rulebook's fixed order (*Produce* before *Cover Needs*)
is part of the economics: it guarantees that wages always arrive before the
Food bill. (Net worth is the same; the second path pays 5 interest every
following round.)

**Theorem D3 (the debt-spiral threshold).** Let s be the Working Class's
surplus per round before interest, L its Loans, and let it repay one Loan per
round whenever it holds 50. From any purse below 50:

* s > 5L ⇒ the debt is repaid to 0;
* s = 5L ⇒ L is a fixed point;
* s < 5L ⇒ L grows without bound — the reinforcing loop R4 dominates.

Checked on the model's ledger for 30 rounds on all **357** orbits (s from −20 to
60 step 5, L₀ = 0…6, m ∈ {0, 25, 45}). Sample orbits from 2 Loans:

```
  s = -10 : 2 3 3 4 4 5 6 7 7 8 9 10 12
  s =   5 : 2 3 3 3 3 3 4 4 4 4 5 5 6
  s =  10 : 2 2 2 2 2 2 2 2 2 2 2 2 2        <- s = 5L: fixed point
  s =  15 : 2 2 2 2 2 2 2 2 2 2 1 1 1
  s =  30 : 2 2 2 1 1 0 0 0 0 0 0 0 0
```

Note the second row: a *positive* surplus of 5 still spirals once interest
exceeds it. Combined with §5, D3 explains the counterfactual games of §8 in
which the Working Class, starting under Labor C, ends with three Food-driven
Loans and a negative final score.

---

## 7. Politics and the IMF (`examples/hegemony-politics.pal`)

**Exact odds.** Drawing 5 cubes without replacement from w WC, c CC and m
neutral cubes, followed by the Influence-commitment rule, gives the probability
that a Working Class Bill opposed by the Capitalist passes as an exact rational
(`p-pass`, a hypergeometric sum). With 9 CC and 13 neutral cubes (×10,000):

```
           w     no-infl     WC1-CC3     WC3-CC1     +3cubes
           2        2192          67        7984        2107
           6        4865         867        9076        1350
          10        6569        2043        9524         845
          14        7637        3210        9732         540
```

The last column is the marginal value of *Apply Political Pressure*: it falls
from +21 to +5 percentage points as the bag fills — diminishing returns — while
an Influence edge of two tokens swings a Bill by 65–80 points. Influence, not
cubes, decides close elections.

**Theorem P1 (monotone odds).** P(pass) is nondecreasing in WC cubes and WC
Influence and nonincreasing in CC cubes and CC Influence, on the full grid
w, c ∈ {0,…,12} step 2, m ∈ {5,13}, Influence ∈ {0,1,3}: **882** exact
rational comparisons. This is what makes `Vw → L` and `Vc → L` signed edges.

**Theorem P2 (the IMF is a retraction).** For every one of the 243 settings of
Policies 1–5 applied to the round-3 state with an indebted State,
imf(imf(S)) = imf(S) up to the event log: the IMF is idempotent on the *whole
state*, not just on the Politics table. It projects every state onto its
profile 1C 2C 3A 4B 5C 6B 7B — which is the game's own starting profile with
the Labor Market moved from B to C.

**Scenario P3 (welfare overreach).** Start the Working Class with the full
Public Sector (Fiscal A, 8 Public Companies staffed) and Labor Market A. The
Treasury cannot carry 8 public Wages of 30 plus the 120 for opening two rows:
the State takes 5 Loans in round 1, the IMF intervenes in the first Production
Phase, and the policies are reset to Fiscal C / Labor C — the balancing loop B5
in one step.

---

## 8. Counterfactual games (`examples/hegemony-policy.pal`)

The whole game, replayed with the starting Labor Market and Foreign Trade
sections changed, everything else equal:

```
   Labor   Trade   WC-VP   CC-VP   prosp   unemp    WC-$  CC-cap State-$  CCwages  WCbuys
       A       A      47      68       2       5     190     128     149      525     465
       A       B      42      86       3       4      75     113     149      490     495
       A       C      43      71       3      11       2      86     118      310     331
       B       A      15      61       0      10       2     128     200      360     435
       B       B      25      61       0      11      14     148     158      390     435
       B       C      25      45       2      11      12      71     218      330     346
       C       A     -14      73       0      10       4     207     264      280     435
       C       B     -14      73       0      10       4     207     264      280     435
       C       C      38      63       2       6      58      66     293      380     286
```

* **The wage floor is the Working Class's master variable** (R2, §5): Labor A
  starts give it 42–47 VP; Labor C starts with protectionist trade end at −14,
  through the debt spiral of §6.
* **Labor A is not bad for the Capitalist**: under Labor A / Trade B it scores
  its best result (86 VP). Higher wages raise its sales (WCbuys 495) — the
  wage–demand circuit R1 beating the profit squeeze B1 — while its Wealth VP
  comes from Capital *levels*, not margins.
* **Free trade (C) cuts the Food price to 9** and is the only setting in which
  the Labor C Working Class escapes debt (38 VP), but it also cuts the
  Working Class's purchases from the Capitalist by a fifth to a third.

All nine games satisfy all four conservation laws.

---

## 9. Conservation laws and independent verification

**Theorems C1–C4**, asserted after every round of every game in this study:

* **C1 money:** wc + cc.rev + cc.cap + st + world = 0 — money is conserved;
* **C2 the Godley identities:** every row of the flow matrix sums to 0, and
  each sector's column is its net change in money;
* **C3 material balance**, per good: held = start + produced + imported − used
  − exported − lost;
* **C4 labor:** Workers = unemployed + Σ crews.

C1/C2 hold by construction for any rule that moves money only through `pay`;
the assertions are the check that no rule does otherwise.

**Independent re-derivation.** `crosscheck/hegemony_crosscheck.py` is a second
implementation of the same specification in plain Python (no shared code). It
reproduces, exactly, every history row of the baseline game, the full flow
matrix, goods statistics and final records, all nine counterfactual games, the
regime atlas and Theorems R1–R3, the odds table and P1, D1–D3, and the 17 loops
with their polarities — **37 checks**. It is not a formality: its first run
disagreed with the model on one counterfactual game, which exposed the lazy
`equal?` bug described in §2.

---

## 10. Limits

* **Behaviour is one strategy profile, not an equilibrium.** The loop structure
  (§4) and the static results (§5–7) do not depend on it; the trajectories
  (§3.5, §8) do.
* **Card values marked ASSUMED** (§1) affect magnitudes. In particular the
  Public Companies' output and wages set the State's budget in §5 and §7.
* **The subgame excludes Action cards**, Strikes, Trade Unions, Business Deals,
  Machinery and Immediate Votes. Strikes would add a wage-bargaining loop
  (Strike → L3 Wages) not present here.
* **Edge verification is local**: finite differences at eight states. It
  establishes that the signs hold where tested and that each is realised
  somewhere, not that they hold at every reachable state. Where a channel is
  regime-dependent (the IMF write-off) the probe measures the documented
  mechanism and the nonlinearity is reported separately.
