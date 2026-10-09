# A Materialist Economy as a Term-Rewriting System

*Marxian value theory, econophysics, class-analytic game theory, selectorate
theory and structural dialectics as one machine-checked model, with its
feedback loops written as rewrite rules and verified edge by edge, its
thresholds located exactly, and its outputs set beside published data.*

This is the technical companion to the study. The study is written up as an
academic paper in `MATERIALIST-ECONOMY-PAPER.md` (§15 below describes it).
Reproduce everything with:

```sh
cargo build --release
cargo test --release                            # 44 unit tests
./verify-materialist.sh                         # 13 checks, ~4 min; exit 0 iff all pass
python3 crosscheck/materialist_crosscheck.py    # 62 independent checks (part of the above)
```

| file | role | section |
|---|---|---|
| `lib/linalg.pal` | exact linear algebra over the rationals: Gauss–Jordan, determinants, Hawkins–Simon, the contractive iterations; strict list combinators | throughout |
| `lib/value.pal` | labour values and the plan, conservation, exchange as an equivalence relation, exploitation, the FMT and GCET, the wage–profit frontier, price–value deviations, Okishio, skilled labour | §3 |
| `lib/econophysics.pal` | exact multiplicities, the microcanonical marginal, random exchange, two classes and the asset cap, the Cantillon effect, labour vouchers | §4 |
| `lib/classgames.pal` | bargaining with outside options, the class-struggle game, Roemer's exploitation test, collusion in a divided government, quadratic voting, prospect theory, patronage | §5 |
| `lib/polecon.pal` | the integrated economy as an equation chain in three regimes, its causal-loop diagram, the probe machinery, regime transition | §6–§7 |
| `lib/cld.pal` | generic causal-loop diagrams: elementary cycles and polarity | §7 |
| `lib/dialectics.pal` | the five predicates of Structural Dialectics, Phase Inversion, the diagnostic taxonomy | §8 |
| `lib/longrun.pal` | the long-run profit attractor of *Classical Econophysics* §14.3 and its floor; CE Table 10.1 | §9–§10 |
| `lib/selectorate.pal` | the selectorate model of *The Logic of Political Survival*, ch. 3 | §9–§10 |
| `lib/report.pal` | strict text-report helpers, sparklines | displays |
| `examples/me-tour.pal` | one feedback loop, small enough to read with `--trace` (2 theorems) | §2 |
| `examples/me-value.pal` | Part I, 17 theorems (~7 s) | §3 |
| `examples/me-distribution.pal` | Part II, 18 theorems (~76 s) | §4 |
| `examples/me-games.pal` | Part III, 20 theorems (~8 s) | §5 |
| `examples/me-economy.pal` | the economy as a self-rewriting program (10 periods per run; a quine at period 60) | §6 |
| `examples/me-regimes.pal` | trajectories, stress scenario, 27-setting sensitivity grid, 13 theorems (~84 s) | §6 |
| `examples/me-loops.pal` | 14 feedback loops; every edge verified; what accountable planning removes, 5 theorems (~16 s) | §7 |
| `examples/me-dialectics.pal` | Part V: the post's worked examples recomputed; the predicates on the model, 13 theorems (~5 s) | §8 |
| `examples/me-classical.pal` | Part VI: checks against *Classical Econophysics* and *How the World Works*, 8 theorems (~7 s) | §9 |
| `examples/me-selectorate.pal` | Part VI: the selectorate model, 7 theorems (~9 s) | §9 |
| `examples/me-extremes.pal` | Part VII: limits, thresholds and inflection points, 6 theorems (~11 s) | §10 |
| `examples/me-evidence.pal` | Part VII: the model's figures beside cited empirical data, 3 theorems (~0.5 s) | §11 |
| `crosscheck/materialist_crosscheck.py` | an independent Python implementation that regenerates every displayed table | §13 |
| `verify-materialist.sh` | runs all of the above | §13 |
| `MATERIALIST-ECONOMY-PAPER.md` | the study as an academic paper, with code, data, sources and the reproduction protocol | §15 |

---

## 1. What is modelled, and why rewriting

The source material is seven documents: a case for *mechanical materialism*
(conservation laws, statistical mechanics, labour values predicting prices,
the two-class income structure, money creation as redistribution, the falling
rate of profit); the *accountable planning* proposal (quadratic voting, the
contractive planning computation, labour vouchers, a divided government, the
capitalist remainder and its expropriation triggers); *objections and
responses* (motivation, vouchers, skilled labour, counter-revolution, public
choice); a comparison of *philosophies of contradiction*; *Structural
Dialectics* (a formal framework of possibility, necessity, warrant,
realization and synthesis); and two short posts, on *fascism as an outgrowth
of capitalism* (falling living standards, radical coalitions, the Cold War)
and on *job creation* (right-wing patronage employment and institutional
capture).

The modelling choice follows the documents' own methodological argument. The
mechanical-materialism post asks for "regularities governing how systems
change states under specified conditions", and the contradictions post makes
the point against Buddhist impermanence that while objects change, "the law
that s transforms into Q in time t′ − t under certain conditions could be
essentially fixed". A rewrite rule `lhs => rhs where conditions` is exactly
such a law of transformation: the term (the state of the economy) is
impermanent, the rules are fixed. The same post records the Analytical
Marxists' proposal to rebuild Marx's explanatory apparatus with game theory;
here class analysis — a class is a relation to the means of production —
supplies the games' *inputs*: who the players are, what each can fall back on
if no agreement is reached, and what surplus there is to divide.

| document | where it enters the model |
|---|---|
| mechanical materialism | Part I (conservation, labour values, FMT, the frontier, TRPF/Okishio), Part II (Boltzmann–Gibbs money, two classes, Cantillon) |
| accountable planning | Part I (the contractive plan; the post's iron/coal/corn/bread example), Part II (vouchers, asset cap), Part III (QV, divided government, job guarantee), Part IV (the `ap` regime) |
| objections and responses | Part I (skilled-labour coefficients), Part III (collusion, counter-revolution via the asset cap, public choice via QV), Part IV |
| fascism as outgrowth of capitalism | Part III (prospect theory, the Cold War pattern), Part IV (the `cold` regime, radicalization, repression) |
| job creation | Part III (patronage competition), Part IV (right networks funded out of profits, terror-management insecurity) |
| philosophies of contradiction | §1 (laws of transformation), §8 (foreclosure), Part IV's equation chain |
| structural dialectics | Part V, applied to Part IV's own viability |
| the three reference works | Part VI (the long-run profit attractor, CE Table 10.1, *How the World Works* §5.9, the selectorate model) |
| published empirical data | Part VII (the model's figures beside cited measurements; thresholds and inflection points) |

Everything is exact. Numbers are Palimpsest integers of any size and exact
rationals; nothing is a float. Stochastic agent models use the interpreter's
deterministic hash `rng`, so every number in this document reproduces bit for
bit, and the Python cross-check (§13) re-derives every displayed table
independently and agrees digit for digit.

---

## 2. Interpreter features used by the study

| feature | why |
|---|---|
| **Exact numbers** (`src/num.rs`): arbitrary-precision integers and rationals as a term variant, literal syntax `n/d` | Labour values, prices of production, Leontief inverses, posteriors and probabilities are rationals; Hawkins–Simon brackets for the profit rate have 2³⁰ denominators; multiplicities are 13-digit integers. Invariant: a number whose value is an i64 integer is always `Int`, so equality stays structural and printing canonical (self-rewriting programs carrying rationals still become byte-identical quines). `+ - * < <= > >= = <> min max abs add@ sum@` work on all numbers; integer overflow yields the exact result instead of a stuck term. `/` and `mod` stay integer operations; further primitives: `q/` (exact division), `num`, `den`, `floor`, `ceil`, `round-to` (explicit rounding to 1/K, to bound denominators in long simulations), `expt`, `isqrt`, `number?`, `decimal` (display). Dependency: the `num-bigint`/`num-rational` crates. |
| **`let $NAME = TERM with S`** | Names a computed value: a sensitivity grid used by one display and four asserts is computed once. `let` normalizes once and substitutes `$NAME` into every later `show`, `display` and `assert`. Names start with `$`, so a binding can never capture a rule head. |
| **Normal-form memo** (`#memo`, `--memo`) | Rules are static and match context-free, so a term proven normal stays normal; the leftmost-outermost redex search skips it. Under the memo a **normalization cache** also keeps the normal form of every argument forced at a strict (`!x`) position, so when one rule's guard fails the next rule of the same head does not force the argument again (capped at 2¹⁴ entries; keys hold their terms alive). Normal forms and reduction order are exactly those of the plain evaluator (unit-tested); fuel counts drop, so it is opt-in and every program without `#memo` keeps its fuel fingerprint. On `me-tour.pal`, 400 periods take 10,568 steps instead of 29,505; `me-regimes.pal` runs in 84 s. `--stats` reports memo and cache hits. |
| **`--trace N`** | Prints the first N successful rewrite steps as `rule: redex => contractum`, indented by the nesting depth of guard, `where` and strict-argument evaluation. Observation only: a unit test checks that a traced run reaches the same normal form with the same fuel. `examples/me-tour.pal --trace 22` shows one period of a feedback loop. |
| **Fast internal hashing** (`src/fxhash.rs`) | The rule head index and variable bindings use a non-cryptographic hasher; nothing iterates these maps order-dependently. |

**Compatibility.** All 76 other example programs (54 examples and 22
puzzles) print byte-identical output, fuel counts included; all ten other
verification suites pass (83 checks); there are 44 unit tests.

**Two lessons about normal-order rewriting.**
(1) The Hegemony study warned that a rule matching "any term" sees an
*unevaluated call*. The cost side of the same fact: a rule that mentions an
unevaluated argument twice on its right-hand side evaluates it twice, and
recursion makes that exponential. The standard library's
`(max ?a ?b) => (if (>= ?a ?b) ?a ?b)` makes `maximum` exponential on long
folds; one exchange-table check took 9.5 million steps instead of 2,870. Every
public entry point of the study's libraries is strict (`!x`), and they use the
strict folds `lmax`/`lmin` (`arith.pal` is left unchanged to preserve existing
fuel fingerprints). Part I went from 194 s to 7 s. `me-tour.pal` shows the
hazard in miniature: `min` copies its unevaluated argument `(q/ 270 3)`, which
the trace shows being computed twice, and a lazy variant of its loop costs
quadratic work. (2) `list.pal`'s `map`/`filter` build a lazy chain that the
evaluator rescans from the root at every step; `linalg.pal` adds accumulator
versions (`smap sfilter scount sall sconcat srange`) that stay linear in steps.

---

## 3. Part I — value, the plan, and the opposition of classes (`me-value.pal`)

The reference economy E3 has three sectors — means of production (mp),
necessities (nec, the wage good) and luxuries (lux, non-basic):

```
A = [[1/5 1/5 1/10] [1/10 1/5 0] [0 0 0]]   (A[i][j]: units of i per unit of j)
l = (1 2 1) hours per unit,   wage bundle b = (0 1/4 0) per hour,   d = (0 10 2)
```

**V1 Labour values and the plan as a contractive loop.** λ = l(I−A)⁻¹ =
(50/31, 90/31, 36/31) exactly, and it is a fixed point of λ ↦ λA + l. The
planning post's worked example (iron, coal, corn, bread; final demand 20,000 t
coal and 1,000 t bread) quotes a converged plan but not its table; with our
reconstruction (`plan4`, chosen so the exact plan matches) the exact gross
output is (11125/3, 209375/6, 5000/3, 1000), which rounds to the published
**(3708, 34896, 1667, 1000)**. The planner's loop x ↦ Ax + d, stopped when two
successive estimates agree to a ton, stops after **18 passes** ("by
approximately the twentieth pass"); the error after 17/18/25 passes is
1.544/0.893/0.019 tons, and the iterates rise monotonically to the plan.

**V2 Conservation.** For every final demand, λ·d = l·x: the value of the net
product equals the living labour performed (checked on all 27 demands in
{0, 1, 7/2}³ and on the plan: 283000/3 hours both ways).

**V3 Exchange as an equivalence relation (Marx's "third thing").** An exchange
table that is reflexive, symmetric and transitive is exactly one of the form
T[i][j] = vᵢ/vⱼ: the value vector is recovered from it (1, 9/5, 18/25) and
represents it exactly, and every cycle of trades returns exactly what it
started with. Raise one ratio by 10% and the table stays reflexive and
symmetric but not transitive, and a three-trade cycle returns **11/10** — a
pure-exchange M–C–M′. Surplus value cannot come from value-conserving exchange.

**V4 Exploitation and the Fundamental Marxian Theorem.** The value of labour
power is λ·b = 45/62, the rate of exploitation 17/45. The uniform profit rate
r* (prices p = (1+r)p(A + bl)) lies in **[0.22849294, 0.22849294)**, bracketed by
30 exact Hawkins–Simon decisions; the maximal rate (wages zero) R ≈ 1.92893219.
FMT: r* > 0 ⟺ λ·b < 1, verified exactly on 21 wage bundles including the
boundary β = 31/90 (where λ·b = 1 and r* = 0 exactly) and on all 64 bundles
in {0, 1/20, 1/10, 1/5}³.

**V5 The generalized commodity exploitation theorem.** Treating labour as a
produced commodity, *every* basic commodity (mp, nec, labour) is "exploited"
(its own k-value is below 1: 0.4333, 0.7875, 0.7258) iff r* > 0, on all 21
bundles. The FMT therefore does not single out labour as the value base. The
argument for labour has to be the empirical one the mechanical-materialism
post makes (price–value correlations, the alternative-value-base tests), and
that is outside any model's reach.

**V6 The wage–profit frontier: the real opposition of the two classes.** With
the net product as numeraire (MELT = 1), w(0) = 1 (labour receives the whole
net product, and prices equal values) and w falls strictly through
0.9546, 0.9086, … to 0.0174 at r = 1.9. Whatever one class gains on the net
product the other loses. This is the exact, non-metaphorical content of
"contradiction" that the model uses throughout; it is a *real opposition* in
Colletti's sense, not a logical contradiction.

**V7 Price–value deviations.** MAWD(r) is 0 at r = 0 and rises strictly to
0.0349 at r = 1; in an economy with uniform value composition it is 0 at every
r. "Labour values predict prices" is here the theorem that prices of production
tend to labour values as the profit rate tends to zero relative to R. Against
measured deviations the model's are too small (§11).

**V8 Okishio versus the falling rate of profit.** Eighteen mechanizing
changes (labour cut 10–30%, extra machine input 0.025–0.1 per unit, in either
basic sector). Capitalists adopt a change iff it cuts unit cost at current
prices (prices from 60 exact power-iteration steps):

```
   j   cut  +mach   dCost@p  choice    r-old    r-new  r-new(e)
   0  0.10  0.025  -0.00552   adopt  0.22849  0.23315   0.22808
   0  0.20  0.100   0.00360  reject  0.22849  0.22515   0.22165
   1  0.30  0.025  -0.06972   adopt  0.22849  0.41699   0.21510
   ...                                          (18 rows in the program's output)
Okishio verdict holds in 18 of 18 changes; adopted: 14;
of those, r falls under a constant rate of exploitation: 11
```

With the real wage fixed, every adopted change raises the profit rate and
every rejected one would lower it (Okishio's theorem, on every row). If
instead the real wage rises enough to hold the rate of exploitation constant,
the profit rate falls after 11 of the 14 adopted changes. **The falling rate of
profit is determinate only given a wage rule**, which is Heinrich's
indeterminacy point. In this model the wage is not exogenous: Part III derives
it from the class-struggle game.

**V9 Skilled labour.** The surgeon of the objections post: 1 + 30,000/60,000
= **3/2**. If the teachers are themselves skilled (study 10,000 h, taught
20,000 h, career 60,000 h), their coefficient is the fixed point of a
contraction, 7/4 (reached by iteration), and a surgeon they teach counts 7/4,
not 3/2. The post's figure treats teaching hours as simple labour.

---

## 4. Part II — the distribution of money (`me-distribution.pal`)

**E1 Maximum entropy, decided by integers.** For N agents and M units, a
macrostate's multiplicity W = N!/∏nₖ! is an exact integer, so maximum entropy
is decided without logarithms. N = 8, M = 16: 186 macrostates, max W = 10,080
(unique) at occupation (2, 2, 1, 1, 1, 1, 0, …); N = 12, M = 24: 1,380
macrostates, max W = 4,989,600 (unique). The equal split has W = 1: **equality
is the least probable macrostate.**

**E2 The exact Boltzmann–Gibbs limit.** With all microstates equally likely,
P(m = k) = C(M−k+N−2, N−2)/C(M+N−1, N−1) (verified against the recurrence for
all k). It is strictly decreasing in k, and its total-variation distance to the
geometric law (1−q)qᵏ, q = T/(1+T), is 0.03387 / 0.00313 / 0.00031 for
N = 10 / 100 / 1000 at T = 10: the exponential distribution is the
large-N limit of a conservation law. Its Gini coefficient is 1/(1+q) = 11/21.

**E3 Random conservative exchange.** 100 agents, 10 units each, unit transfers
between random pairs. Money is conserved at every snapshot; the Gini
coefficient rises 0 → 0.2477 → 0.4026 → 0.4603 after 1,000/5,000/20,000
events; the histogram pooled over 40 snapshots is within total variation
0.0329 of the geometric law, 9.20% of agents hold nothing (theory 9.09%), and
the pooled Gini is 0.5182 (theory 0.5238). No agent does anything but trade
at random.

**E4 Two classes, and the asset cap.** Five owners (100 units each) and 95
workers (5 each). Wages are additive (an owner pays a random worker a unit);
sales are multiplicative (the seller is drawn in proportion to her holdings).
With caps none/60/30 (the planning post's second expropriation trigger:
holdings above θ go to a public fund that pays wages):

```
       events  owners%   wGini      owners (sorted)          pub total  cap-ok
  cap none
    60000   0.9764   0.8439        (list 0 0 0 0 952)    0   975   true
  cap 60
    60000   0.2421   0.4905      (list 0 58 59 59 60)    0   975   true
  cap 30
    60000   0.1159   0.4859      (list 4 25 26 29 29)    0   975   true
```

Uncapped, capital income condenses: one owner ends with 98% of all money, and
the workers' Gini is 0.84. This is the extreme limit of the Pareto tail, not a
fitted Pareto law. Capped, the owners' share is bounded by Cθ/M at every
checkpoint (asserted), and the workers return to the exponential's inequality
(Gini ≈ 0.49 against 0.5).

**E5 The Cantillon effect.** Real output 1,000; money 600/300/100 (asset
holders / middle / poor); 100 new units credited to the asset holders and
spent first at the old price. Real gains are **(100, −75, −25)**, summing to
exactly zero; the first recipients gain exactly Q·D/M. The same injection in
proportion to holdings, spent after prices adjust, redistributes nothing
(0, 0, 0). Money creation is symbolic appropriation that enables real
appropriation, not a creation of value.

**E6 Labour vouchers.** Issued for hours, cancelled on purchase, never
transferred. For 20 agents over 30 periods, v = issued − redeemed and
0 ≤ v ≤ issued for every agent. **Non-interference:** if agent 0 works 40
hours instead of 6, no other agent's holdings change. In the money economy,
giving agent 0 one extra unit at the start changes other agents' holdings.
There is no rule by which a voucher moves between people, so the M–C–M′
circuit has nothing to run on.

---

## 5. Part III — games with class analysis as input (`me-games.pal`)

**G1 The reserve army as an outside option.** Nash bargaining over an hour's
value, where a worker who walks away finds another job with probability 1−u
and otherwise lives on s = 2/5. The fixed point is
w_cap(β, u, s) = (β + (1−β)us)/(β + u(1−β)). It falls strictly with
unemployment (β = 1/5: 1.0000, 0.8286, 0.7333, 0.6308, … 0.5200 for u from 0
to 1). Under a job guarantee paying g = 4/5 the outside option is g itself:
w_ap = g + β(1−g) ≥ g. A private firm survives only if its productivity
exceeds g (at 7/10 it cannot; at 9/10 and 6/5 its profit per hour is 1/20 and
1/5). This is the post's claim that capitalists "must offer conditions
attractive enough to compete with the government sector", as an exact
inequality.

**G2 The class-struggle game.** Workers {accept, organize} × capital
{concede, repress, flee}. Payoffs are the wage net of organizing costs and
capital's share net of repression costs, with capital's return abroad as its
exit option:

```
  CAPITALISM          W        C        ACCOUNTABLE PLANNING W        C
  acc/con     0.7333   0.2667            acc/con     0.8400   0.1600
  acc/rep     0.7333   0.2167            acc/rep     0.8400   0.0600
  acc/flt     0.4000   0.1000            acc/flt     0.8000   0.0000
  org/con     0.8500   0.1000            org/con     0.8500   0.1000
  org/rep     0.6833   0.2167            org/rep     0.8500   0.0000
  org/flt     0.4000   0.1000            org/flt     0.8000   0.0000
```

Under capitalism there is **no pure equilibrium**, and better responses
cycle: (acc,con) → (org,con) → (org,rep) → (acc,rep) → (acc,con). The mixed
equilibrium of the core game has Pr[accept] = 7/10 and Pr[concede] = 3/10.
That is perpetual class struggle in the precise sense of a game without a
rest point. Under accountable planning repression is illegal (rights are
entrenched, so it fails and is penalized) and flight triggers expropriation
(workers move to public jobs). The unique equilibrium is (organize, concede),
and dynamics terminate. Over **243 parameter settings** (both bargaining
powers, both costs, three unemployment rates):

- *Accountable planning:* in all 243 a pure equilibrium exists, capital concedes in every one, and dynamics terminate. In 9 settings, where organizing is worth exactly its cost, there are two equilibria.
- *Capitalism:* 187 of the 243 settings have no pure equilibrium. A hand-derived condition for "no pure equilibrium" (gap > k, capital stays against acceptance, will neither concede nor flee against organization) agrees with the machine in all 243 settings. The first condition I wrote down was wrong (it agreed in 113), and the grid caught it.

**G3 Roemer: exploitation as a property relation.** Six agents with capital
(0,0,0,1,2,9); a job needs 4 units of capital; labour without capital yields
S = 2/5. A coalition is capitalistically exploited iff it would be better off
withdrawing with its per-capita share of the means of production. On all 63
coalitions this coincides with *mean capital below the social mean* (30
exploited, 30 exploiters, 3 neutral; also on a second endowment, 26/26/11).
When every worker has access to the social means of production, which is
what the proposal's land and job assignment provides, no coalition is
exploited. Roemer's counterfactual becomes an institution.

**G4 Collusion in a divided government.** K secretaries share a rent R if all
collude; any one can blow the whistle for a bounty B; an audit uncovers the
conspiracy with probability P each period. Grim-trigger collusion needs
δ ≥ δ*(K) = (1 − R/(KB))/(1 − P). With B = R, δ* is 0, 0.500, 0.667, … 0.889
for K = 1…9, and collusion becomes impossible at **K = 10** with 10% audits
and **K = 5** with 20%. A single ruling party (no bounty a member can claim)
sustains collusion at every δ. That is Djilas's "new class" as an equilibrium.
With B = R the smallest number of secretaries that cannot collude at any δ is
exactly K̄ = ⌈1/P⌉ (§10, X9).

**G5 Quadratic voting.** Integer ballots, 36 credits, three categories
(investment, necessities, luxuries), found by exhaustive search. Workers
(valuations 2,6,1) cast (3,5,1); owners (1,1,8) cast (0,0,6); a green
minority (9,1,1) casts (6,0,0). The tally for 90/5/5 voters is (300, 450, 120);
plurality would be (5, 90, 5). Demand weighted by purchasing power, with
Part II's uncapped distribution, puts **78.1% on luxuries**, and under the
asset cap 27.7%. For 1,000 hours of labour the plan employs 283.9/654.0/62.2
hours by sector under QV and 193.3/251.6/555.1 under the uncapped market.
Purchasing power, not need, decides what a market produces.

**G6 Prospect theory and the radical coalition.** A moderate option (a sure
+1) against a radical gamble (+6 with probability 1/4, −2 with 3/4, expected
value 0). The value function is concave over gains, convex and loss-averse
(9/4) over losses. Choices are single-crossing in the position D: on the
quarter-unit grid from −8 to +3 the gamble is chosen exactly when **D ≤ −11/2**,
and the exact threshold is **−5.3994** (§10, X4, which also shows that the
threshold is set by the curvature of the value function, not by loss aversion). With the fascism post's
strata (lower-middle falling −6, middle −3, poorest +1, top +2), 30% choose
the radical option. Measured against an aspiration 3 units above their
standard (the "promised land over the horizon"), 55% do. In the Cold-War
pattern, where every stratum is rising, none do.

**G7 Patronage.** Two ideological networks spend resources on jobs and
messages; members follow attraction, where a job binds three times as much as
a message (the job-creation post's premise). Resources follow membership. With
capital-funded R (base funding 3:1), the unique equilibrium has both networks
spend everything on jobs, which is weakly dominant for both. If L creates no
jobs while R does, R's share is 0.942; if both do, 0.743. Given its premise,
the post's conclusion follows.

---

## 6. Part IV — the integrated economy (`me-economy.pal`, `me-regimes.pal`)

**The equation chain.** One period is a chain of equations over a record (the
state plus every variable computed so far), each binding one variable:

```
capitalism:   E  U  B  Fl  Inf  W  Cu  Ce  Pi  Rr  Cr  I  K2  Asp  Rad  Gov2  SR2
planning:     E  U  B  Fl  Inf  W  Lreq PlanErr  Ce  Cu  Pi  Rr  Cr  I  K2  Asp  Rad  Gov2  SR2
```

Every equation is a mechanism from Parts I–III:

- **Employment** E = K/κ, where κ (capital per job) rises 1% a period. That is mechanization, the rising organic composition.
- **Bargaining power** B is *the equilibrium of the class-struggle game* at the current unemployment rate. It is the expected value under the mixed equilibrium when there is no pure one, and a radical government halves both levels.
- **The wage share** W is Nash bargaining against the reserve army (or against the job guarantee).
- **Profits** Π = (1−W)E and the profit rate drive **investment**. Below a minimum profit rate, or when the game's equilibrium is capital flight, capital goes on strike and a crisis destroys 10% of it.
- **The living standard** is eroded by inflation between pay settlements.
- **The radical vote** is prospect theory over the employed and unemployed strata. Their reference point is last period's standard, raised by the right network's promised-land messaging in proportion to its share.
- **The right network's share** follows the patronage dynamics. It is funded out of profits, and insecurity (terror management) raises the pull of institutions.

The regimes differ by equations, not by parameters:

| | capitalism `cap` | Cold War `cold` (until period 30) | accountable planning `ap` |
|---|---|---|---|
| labour market | reserve army | reserve army + insurance (9/10 of the employed standard) | job guarantee at g = 4/5 |
| wages | bargaining | bargaining, floor at half of productivity growth, cost-of-living adjustment | public g; private firms must beat it |
| money | 2% target, shock 10% in periods 40–41 | the same, compensated | vouchers: no inflation |
| left networks | create no jobs | create jobs | create jobs; patronage has no leverage (everyone has a job) |
| repression | a radical government halves bargaining power | the same | rights entrenched: fails |
| capital | accumulates out of profits | the same | the remainder is capped at θ = 60 |
| demand | purchasing power | purchasing power | QV direction (300, 450, 120), growing 2% a period; the plan by the contractive loop |
| viability's economic margin | profitability (r − r_min)/r_min | the same | plan feasibility (public labour − required)/required |

Viability Φ is the minimum of the economic margin and the political margin
2(1/2 − radical vote): the scalarization of "the regime reproduces itself and
keeps a democratic majority". Parameters were calibrated from the model's
own steady-state algebra (accumulation balances when s_c·r* = δ + μ), not by
fitting outcomes.

**The economy as a self-rewriting program.** `examples/me-economy.pal` holds
all three regimes in its `main`. Each run fires the transition `crank`, which
plays ten periods of each, writes them back, and re-checks invariants on the
history so far. After six runs, at period 60, the guard fails and the file
reproduces itself byte for byte:

```
THE SAME ECONOMY UNDER THREE REGIMES (one column per period)
capitalism            period 60
  unemployment  [0,1]   |   ...........................................::::::::::::::|
  radical vote  [0,1]   |   ...........................................::::::::::::::|
  viability Phi [-1,1]  |==++++++********************************++++++++++++++++++++|
  living std    [0,3]   |::::::::::::::::-------------==========+==++++++*******#####|
Cold War, ends at 30  period 60
  radical vote  [0,1]   |                              ................::::::::::::::|
accountable planning  period 60
  unemployment  [0,1]   |                                                            |
  radical vote  [0,1]   |                                                            |
  viability Phi [-1,1]  |====================++++++++++++++++++++++++++++++++********|
```

**Baseline results** (every one an `assert`):

- *Capitalism:* unemployment rises in every period, 0.100 → 0.299, and the wage share falls in every period. That is Marx's general law of accumulation: rising capital per job outpaces accumulation, and the reserve army is the counter-tendency that keeps the profit rate above the minimum in every period (no crisis). §9 (C2) gives the identity behind this and §10 (X6) the exact
boundary: employment is stationary only if μ ≤ s_c·r − δ. The inflation shock cuts the living standard at period 40, but no radical government results at baseline sensitivity.
- *Cold War:* the radical vote is exactly 0 while it lasts and equals unemployment afterwards. The unemployed lose their insurance and fall into the loss domain.
- *Accountable planning:* unemployment is 0, the radical vote is 0, the living standard rises in every period, and Φ > 0 throughout. In every period the plan's labour requirement λ·d equals living labour l·x exactly, and 30 contractive passes leave a residual below 1/1000 (largest 0.00000226).

**The stress scenario** (loss sensitivity 30, aspiration messaging 2/5):

```
CAPITALISM                       t    u   beta     w     r    ce   rad    sR gov   Phi
                                 0 0.100 0.255 0.864 0.045 0.847 0.100 0.500  0  0.131
                                 3 0.106 0.117 0.733 0.086 0.774 1.000 0.770  1 -1.000
                                15 0.082 0.120 0.774 0.065 1.099 1.000 0.854  1 -1.000
                                45 0.126 0.116 0.705 0.063 2.100 1.000 0.891  1 -1.000
radical government in power (periods of 60): capitalism 58 from t=2;
Cold War 29 from t=31;  planning 0
```

The radical government is not punished for failing to deliver.
Repression halves bargaining power, the wage share drops, and the profit rate
jumps from 0.045 to 0.086. Unemployment at first *falls* (0.106 → 0.079) and
living standards *rise* (0.85 → 2.10 by period 45), and yet the radical vote stays at 1. The hold rests on the
reference point: with the right network at 85–89% (periods 6–45), every stratum measures
itself against a standard 34–36% above its own, so it stays in the loss
domain whatever it gains. That is the job-creation post's "downward spiral"
in a precise form: institutions that set expectations lock in the vote.

**Sensitivity.** 27 settings (loss sensitivity 20/30/40 × inflation shock
5/10/20% × aspiration messaging 1/10, 1/5, 2/5), 81 runs of 60 periods:

- **Accountable planning:** in all 27, unemployment is 0, the radical vote is 0 from period 1 on, and Φ > 0 from period 1 on. In the three most extreme settings there is a radical vote in period 0, a transient from inheriting capitalism's reference point.
- **The Cold War** never has more radical-government periods than capitalism.
- **Capitalism** gets a radical government in **15 of 27** settings and reaches Φ ≤ 0 in the same 15. Those are two-period episodes when only the inflation shock pushes the employed into the loss domain, and 56–58-period lock-ins when aspiration messaging is high. The Cold War prevents a radical government before its end in all but 3 settings.

These are conditional results. The loss-sensitivity scale that converts a
change in living standards into prospect-theory units is not pinned down by
any of the documents. That is why the grid, not any single run, is the result.

---

## 7. Feedback loops (`me-loops.pal`)

**The diagram.** Capitalism's causal-loop diagram has 15 variables and 24
signed edges, each annotated with the equation that creates it. Enumerating
every elementary cycle once, from its least node, gives **14 loops: 5
reinforcing, 9 balancing.**

| | loop | reading |
|---|---|---|
| B | K → E → U → W → Pi → I → K | the profit squeeze (Goodwin): accumulation tightens the labour market, wages rise, profits fall |
| B | K → E → U → B → W → Pi → I → K | the same through the class game's bargaining power |
| B | K → Rr → I → K | more capital lowers the profit rate, which slows accumulation |
| R | K → E → Pi → I → K | accumulation: capital employs labour, labour yields profit, profit becomes capital |
| R | B → W → Ce → Rad → Gov → B | **radicalization**: falling wages → loss domain → radical government → repression → lower wages |
| R | B → W → Pi → SR → Asp → Rad → Gov → B | **patronage and repression**: lower wages → higher profits → right-wing patronage → promised land → radical government → repression |
| R | B → W → SR → Asp → Rad → Gov → B | lower wages → weaker union funding of the left network → … |
| B | K → E → U → Rad → Gov → B → W → Pi → I → K | **fascism restores profits**: unemployment → radical government → repression → profits → accumulation → employment |
| B | (four more variants through Rr, U → SR) | |

**Every edge is a property of the equations.** For each edge X → Y, a probe
adds Δ to X, freezes every other node variable at its base value, and
recomputes Y's equation: an exact partial finite difference of the rewriting
system. It does this at ten base states: the baseline at periods 0/15/30/45,
the Cold War at 10, the stress scenario at 0/1/10 (a radical government holds
power at 10), a profit squeeze (capital-intensive, r below the minimum, no
flight) and near-full employment (u = 5%).

```
edge          verdict  deltas at: cap0 cap15 cap30 cap45 cold10  st0   st1  st10 squeeze full
  U -> B   neg   FAIL   -0.020 -0.006 -0.004 -0.002 -0.007 -0.020 -0.016 -0.005 -0.013  0.055
  U -> W   neg strict   -0.047 -0.037 -0.032 -0.027 -0.007 -0.047 -0.046 -0.072 -0.044 -0.071
 Rr -> I   pos   weak    0      0      0      0      0      0      0      0     8.581   0
Gov -> B   neg   weak   -0.137 -0.117 -0.112 -0.108 -0.119 -0.137 -0.131  0     -0.128 -0.068
  ...                                         (24 rows in the program's output)
confirmed (strict or weak): 23 of 24;  failing: U->B
```

23 of 24 edges are confirmed. Weak edges are conditional, and the conditions
are economics:

- the crisis channel Rr → I fires only near the minimum profit rate;
- the radical vote responds to living standards only near the threshold;
- repression cannot lower bargaining power that is already repressed.

The one failure is a finding. **Unemployment lowers labour's equilibrium
bargaining power at every state on the trajectories, but raises it near full
employment.** At u = 5% both wage levels approach the whole product, so
organizing is barely worth its cost. Meanwhile the game's equilibria there
are *capital flight*: capital's best response to organized labour at full
employment is to leave. That is Kalecki's "political aspects of full
employment", which emerged from the game rather than being assumed. In closed
form (§10, X2): flight is capital's best response to organized labour once
r_ext ≥ 1 − w_l − ρ, i.e. for u ≤ 1/12, and to accepting labour once
r_ext ≥ 1 − w_l, i.e. for u ≤ 1/20; just above 1/12 equilibrium bargaining
power jumps from 0.200 to 0.255, which is the positive U → B probe.

**What accountable planning removes.** The same probes at five
planning states, including one with the remainder at its cap, show 12 edges
absent:

- the reserve army: E → U, U → B, U → W;
- the wage–profit opposition: W → Pi;
- the inflation channel: Inf → Ce;
- every channel into the radical vote: W → Ce, Ce → Rad, U → Rad, Asp → Rad;
- repression: Gov → B;
- insecurity's pull: U → SR;
- the crisis threshold: Rr → I.

**One elementary cycle is left**: the capitalist remainder's own accumulation,
K → E → Pi → I → K. At the cap the edge I → K vanishes (Δ = 0 at the `apcap`
base), so the asset cap bounds the only remaining reinforcing loop.

---

## 8. Part V — Structural Dialectics (`me-dialectics.pal`)

**The post's examples, recomputed exactly.** The library implements:

- possibility: admissibility;
- viability: Φ > 0;
- the counterfactual: Φ − d;
- necessity, Phase Inversion and the Bayesian posterior;
- warrant: (Nec ∨ Phase Inversion) ∧ posterior ≥ p_crit;
- realization and synthesis;
- the diagnostic taxonomy;
- the post's §8 verification list, as a predicate over a run.

All three worked examples come out as stated:

| example | diagnoses | posterior | synthesis |
|---|---|---|---|
| hunting-and-gathering → cultivation | P4 Instability (cf −0.100), P5 Phase Inversion (cf −0.450) | **0.735** ≥ 0.55 | on P5 → P6, successor 0.200, 0.180, 0.160 |
| captive-supply coercion → alternative labour | P4 Phase Inversion (no assessment), P5 Phase Inversion | **0.607** ≥ 0.600 | on P5 → P6, successor 0.150, 0.130, 0.120 |
| serfdom → capitalist tenancy | P5 Instability (cf −0.150), P6 Phase Inversion (cf −0.500) | **0.827** ≥ 0.600 | on P6 → P7, successor 0.250, 0.230 |

The post gives the prior and likelihoods only for 0.735. The pairs behind
0.607 and 0.827 are our choice, made to reproduce them to three decimals, and
are flagged as such. The capitalism-and-demography section is reproduced with
intermediate ΔK/L values of our choosing, again flagged. All the stated
values hold: Φ(P8) = 0.030 at g = 0.2, viable throughout; at g = 0 the first
non-viable period is P5, with −0.048, and −0.170 at P8.

**The predicates applied to the integrated economy.** For each model state:

- Φ is the model's own viability;
- the candidate (accountable planning) is admissible iff no radical government holds power;
- d is the viability contributed by candidate-associated mechanisms already active (under the Cold War: insurance, indexation, funded left jobs, removed by evaluating the same state as plain capitalism);
- the Bayesian component is *not* derived from the model: a stated prior 2/5 with the post's own likelihoods, and any prior ≥ 22/97 ≈ 0.227 would warrant.

Diagnoses by period, 0–59 (s stasis, I instability, P phase inversion, n
non-viable with the candidate excluded):

```
baseline capitalism        ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
baseline Cold War          ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
stress Cold War            sssssssssssssssssssssssssssssIPnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
stress capitalism          sPnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
moderate inflation crisis  ssssssssssssssssssssssssssssssssssssssssPnssssssssssssssssss
```

1. **At baseline, capitalism is in Structural Stasis throughout.** By the
   framework's own criteria no transition is warranted: there is neither
   necessity nor Phase Inversion.
2. **A crisis opens a window of exactly one period.** The Phase Inversion
   (incumbent non-viable, candidate admissible) lasts one period, because the
   radical government that takes power next period makes the democratic
   candidate inadmissible. The contradictions post calls this *foreclosure*:
   "socialism is radically excluded from the thinkable". Here it is a
   computed diagnosis: non-viable incumbent, no admissible alternative.
3. **Synthesis depends on the inherited reference point.** In a crisis with
   moderate aspiration messaging, the successor (the incumbent's state
   converted to planning) is viable from its first period (Φ = 0.886) and
   synthesis holds. In the high-messaging stress scenarios the successor is
   non-viable in its first period (Φ = −1: it inherits a reference point that
   puts everyone in the loss domain), recovers to 0.23–0.66 one period later,
   and synthesis fails by the framework's strict definition.
4. **The sign of d is empirical.** The framework assumes d ≥ 0. Under the
   Cold War the minimum d is −0.0597: insurance and indexation raise political
   viability but cost profitability, so removing them would *raise* Φ in some
   periods. The model computes the sign rather than assuming it.

---
## 9. Part VI — checks against the reference works (`me-classical.pal`, `me-selectorate.pal`)

**C1 The long-run profit rate is a demographic attractor** (*Classical
Econophysics* §14.3, *How the World Works* §5.9). The discrete recurrence
S = (1−w)(L − (g+δ)K), K′ = K + λS − (g+δ)K, L′ = (1+n)L, run exactly
(state rounded to 10⁻⁹), converges to R* = (n+g+δ)/λ = 2/15 from wage shares
0.2/0.4/0.6/0.8, with |R_t − R*| never increasing. **A floor the closed form
omits:** since L/K > 0, R > −(1−w)(g+δ); when the population shrinks fast
enough, R* is unreachable and R tends to the floor, which depends on w
(n = −5%: R* = −0.05, limit and R_299 = −0.008). Consuming more of the profit
*raises* the long-run rate (with a stationary population, R* = 0.117 at
λ = 0.6 and 0.233 at λ = 0.3), the books' paradox.

**C2 The integrated model obeys the same identity.** Without crisis and below
full employment, s_c r_t = (E_{t+1}/E_t)(1+μ) − (1−δ) on all 59 transitions
(largest gap 1.3 × 10⁻⁷, from rounding the state to 10⁻⁶). With constant
employment r* would be (μ+δ)/s_c = 1/15; the model's r stays below 1/15 in
every period, so employment must fall and unemployment rise in every period —
the mechanism behind §6's result.

**C3–C4** HWW's illustration r_t = 50/(200 + 25t); CE Table 10.1's labour
values per dollar (0.508, 0.528, 0.485, 0.477; within 5.65% of their mean),
8 iterations to 10⁻³ and 16 to 10⁻⁶, value of final output = total wages = 244.

**S1–S4 Political survival.** For the book's utility √x + √g + √y + √l the
equilibrium has closed forms (private share of spending = p/(p+W) exactly;
loyalty term D c s with D = δ(1 − W/S)/(1 − δ)), solved with certified floor
square roots (every root the exact floor to 10⁻⁹; largest stationarity
residual 8 × 10⁻⁹). Reproduced: revenue-maximizing tax 2 − √2; utilitarian
welfare 2.57893 (tax 0.508397 vs the book's 0.508412, a flat optimum).
Confirmed on computed equilibria: as W rises, both tax rates, the private share
and the leader's surplus fall, public goods and outsiders' utility rise; the
loyalty norm holds. **Not confirmed:** with S = 2000, private goods per member
rise from W = 500 to W = 1000 (W/S → 1/2 weakens loyalty; spending doubles).
Read as points (W, S), a party-state (S = 100,000, W = 100) spends 99.0% of
its budget on private goods, patronage capitalism (W = 1,000) 90.9%, and
majoritarian government (W = 50,000) 16.7%; the selectorate model cannot tell
accountable planning from any other majoritarian system.

---

## 10. Part VII — extremes, thresholds and inflection points (`me-extremes.pal`)

**X1 The wage curve.** w_cap(β = 1/5, u, s = 2/5) has limits w(0) = 1 and
w(1) = β + (1−β)s = 13/25. Its elasticity
e(u) = uβ(1−β)(s−1) / ((β + u(1−β))(β + (1−β)us)) is 0 at both ends and
steepest at u* = β/((1−β)√s) = 0.3953, where e = −0.2251. It equals the
empirical −0.1 at u = 0.0554.

**X2 The class-struggle game along unemployment** (integrated-model
parameters). (accept, flee) and (organize, flee) are both pure equilibria up to
u = 1/20, where w_l reaches 9/10 = 1 − r_ext; (organize, flee) alone up to
u = 1/12, where w_l reaches 17/20 = 1 − r_ext − ρ; above 1/12 there is no pure
equilibrium. Equilibrium bargaining power is 0.2000 in the flight region and
jumps to 0.2549 at u = 0.1, then declines (0.2188 at u = 0.5).

**X3 Switch-point wages.** Three techniques rejected at β = 1/4 (in the
means-of-production sector a 0.10 labour cut with 0.05 more machinery or a 0.20
cut with 0.10; in necessities a 10% cut with 0.10) become cost-reducing at the
same β* = 0.2822, a real-wage rise of 12.9%: all three add machinery worth half
the labour they save. A technique with ratio 1 never pays (asserted).

**X4 The radical threshold.** On the quarter-unit grid the threshold reads
−5, −21/4, −11/2 for λ = 1, 1.5, ≥ 2. The exact threshold (bisection over
D ≥ 2 − K, where the piecewise-quadratic value function is increasing) at
K = 10 is:

```
  lambda    1.00     1.50     2.00     2.25     2.50     3.00     4.00    10.00   100.00
  exact   -4.8377  -5.2464  -5.3668  -5.3994  -5.4233  -5.4560  -5.4923  -5.5471  -5.5749
```

A hundredfold rise in loss aversion moves it by 0.74. When every outcome is a
loss, λ cancels and the gamble wins iff −1 + (11 − 2D)/(2K) > 0, i.e.
**D < 11/2 − K** (exact for K > 23/2): −14.5, −34.5, −74.5 at K = 20, 40, 80,
for every λ (asserted). The radical coalition is a curvature effect; a
risk-neutral electorate never takes the gamble.

**X5 The floor of the long-run profit rate.** R* reaches −(1−w)(g+δ) at
n* = −(g+δ)(1 + λ(1−w)) = −0.0248 (w = λ = 3/5, g = 0, δ = 0.02). At n*
convergence slows sharply (R_599 = −0.00534 against the limit −0.008): the
critical slowing-down of a transcritical bifurcation.

**X6 Mechanization and the reserve army.** Over 60 periods of the integrated
capitalism:

```
      mu     u_0    u_59    r_59    w_59  crises  mu that holds E constant at r_59
  0.0000   0.100   0.110  0.0500   0.850     0   0.0000
  0.0050   0.100   0.179  0.0560   0.775     0   0.0036
  0.0100   0.100   0.299  0.0571   0.692     0   0.0042
  0.0150   0.100   0.461  0.0517   0.627     0   0.0010
  0.0200   0.100   0.596  0.0501   0.517     0   0.0001
```

Employment is stationary only if μ ≤ s_c·r − δ, and r never exceeds about
0.057, so any mechanization faster than about 0.4% a period makes the reserve
army grow without limit.

**X7 From episode to lock-in** (loss sensitivity 30, 10% shock at t = 40–41).
Radical-government periods against aspiration messaging: 0 below 0.20; a
two-period episode (from t = 41) for 0.20–0.26; **10 periods at 0.27**; then 19,
33, 39, 53 and 58 periods at 0.28, 0.29, 0.30, 0.35 and 0.40, starting at
t = 29, 11, 7, 3 and 2.

**X8 The selectorate leader and patience** (N = S = 100,000, W = 1,000,
p = 10,000). The leader's surplus is 0 at δ = 0 (all revenue must be spent),
12,394 at δ = 0.5, 16,949 at δ = 0.9 and 17,155 at δ = 0.99.

**X9 Collusion.** With B = R the smallest number of secretaries that cannot
sustain collusion at any δ is exactly K̄ = ⌈1/P⌉, since δ*(K) ≥ 1 iff
1 − 1/K ≥ 1 − P; verified at audit rates 5%, 10%, 20%, 1/3 and 1/2.

**X10** CE Table 10.1: mean absolute weighted deviation of prices from
MELT-scaled values 0.0306.

---

## 11. Part VII — the model against empirical data (`me-evidence.pal`)

Each empirical figure is a constant in the program, tagged with its source;
each model figure is computed from the libraries. The model is not fitted to
any of them.

```
§EV THE MODEL AGAINST EMPIRICAL DATA
  quantity                                   data        model
  wage-curve elasticity at u = 5% / 10%      -0.10        -0.093 / -0.148
    ... unemployment at which the model gives -0.10: 0.0554
  labour share, relative change              -20.2%      -19.9%  (60 periods)
    ... levels: data 66.2% -> 52.8%;  model 0.864 -> 0.692
  price-value MAWD                           9.2%        E3 at r*: 0.8%;  CE Table 10.1: 3.1%
  job-guarantee wage effect                  +5.0%       +1.4% / +8.4% / +14.5%  at u = 10/15/20%
    ... no effect below u_c = 1/11;  +5% at u = 0.1250
  Gini of the exponential (lower) class      0.500       0.524  (geometric law, T = 10)
  loss aversion lambda                       2.25        2.25  (input; the threshold moves by 0.18 from lambda = 2 to 10, me-extremes §X4)
```

Sources: Blanchflower and Oswald (2005), the wage curve; BLS (2026), the US
nonfarm labour share (66.2% in Q4 1960, 52.8% in Q2 2026); Shaikh (1998) via
*Classical Econophysics* Table 10.2; Imbert and Papp (2015), India's NREGA;
Ludwig and Yakovenko (2022), US income 1983–2018; Tversky and Kahneman (1992).
The job-guarantee threshold u_c = 1/11 solves w_cap = w_ap (asserted).

**What matches:** the wage-curve elasticity at realistic unemployment, the
proportional decline of the labour share, the lower-class Gini, and the
job-guarantee wage effect in a slack market. **What does not:** price–value
deviations are three to eleven times too small (three or four sectors cannot
carry real compositional dispersion); uncapped capital income condenses far
beyond the measured top-1% wealth share of 32.5% (Federal Reserve DFA,
Q2 2026); and the model's unemployment trends upward while measured
unemployment (FRED, 1948–2026) has no trend. The paper (§§4–8) discusses each
comparison with the qualitative evidence: price–value correlations, profit-rate
series (Maito 2014, Basu 2022), financial crises and the far right (Funke,
Schularick and Trebesch 2016), the Cold War and welfare states (Obinger and
Schmitt 2011), patronage (Thachil 2011), leniency programmes (Miller 2009),
selectorate evidence (Clarke and Stone 2008) and quadratic voting (Quarfoot
et al. 2017).

---

## 12. What the model supports, qualifies and contradicts

| claim in the documents | model | data |
|---|---|---|
| Value is conserved in exchange; surplus value cannot arise from exchange | **Supported** (V2, V3): exact conservation; pure exchange yields a profit only with intransitive ratios | not directly testable |
| The planning computation is a fast contractive iteration, ~20 passes | **Supported** (V1): 18 passes to a ton; monotone convergence | consistent with the post's example |
| Labour values predict prices | **Qualified** (V5, V7): prices tend to values as r → 0; the FMT holds for every basic commodity, so the case for labour is empirical | **supported** (correlations 0.94–0.99); model deviations 3–11× too small (§11) |
| The rate of profit tends to fall | **Qualified** (V8, C1, X5): false with a fixed real wage (Okishio, 18/18); true in 11 of 14 adoptions with constant exploitation; falls with demography, to a floor | **supported** as a long-run trend (Maito, Basu) |
| The exponential distribution follows from conservation | **Supported** (E1–E3) | **supported** (Gini 0.524 vs 0.5) |
| Multiplicative capital income produces a superthermal class | **Supported, more strongly** (E4): it condenses; an asset cap bounds it exactly | direction supported; real tail far milder |
| Money creation redistributes real command over resources | **Supported** (E5): exact transfer Q·D/M, zero-sum in real terms | **supported** qualitatively (BIS 2016) |
| Labour vouchers prevent accumulation | **Supported** (E6): non-interference holds as an exact property | no test available |
| A job guarantee breaks capitalist employers' power | **Supported above u_c = 1/11** (G1, G2, §11): capital concedes in all 243 settings; the guarantee is inert in tight labour markets | **supported** in slack markets (NREGA) |
| A divided government cannot conspire | **Supported, with a design rule** (G4, X9): collusion fails iff K ≥ ⌈1/P⌉ with B = R; a single party sustains it at every δ | plausible (leniency programmes) |
| QV protects intense minorities and replaces the purchasing-power filter | **Supported** (G5) | weakly supported |
| "The more radical side will always form the more powerful coalition" | **Contradicted as stated, supported conditionally** (G6, X4, §6): the radical coalition is the share in a deep enough loss domain (D < −5.4), a curvature effect | **supported and qualified**: crises, not ordinary recessions |
| The Cold War forced capitalism to raise living standards universally | **Supported** (§6): radical vote 0 while it lasts; never worse than capitalism | **supported** (Obinger and Schmitt) |
| Right-wing patronage employment drives a downward spiral | **Supported above a threshold** (G7, §6, §7, X7): jobs dominate; the lock-in starts between aspiration 0.26 and 0.27 | premise supported (Thachil) |
| Accountable planning defuses authoritarian politics | **Supported within the model** (§6–§8): no loss domain from period 1 in all 27 settings; the radicalization loops are structurally absent. Cautions: AP's viability depends on demand growth not outrunning productivity, and a transition from a high-aspiration society fails its first period | no test available |
| Unemployment always weakens labour | **Contradicted near full employment** (§7, X2): below u = 1/12 the class game's equilibrium is capital flight | — |
| Capitalism's reserve army keeps growing | **Model artefact** (C2, X6): only with μ > s_c·r − δ | **contradicted** (trendless unemployment) |

---

## 13. Independent verification

`crosscheck/materialist_crosscheck.py` is a second implementation in plain
Python: standard library only, exact `Fraction`s, no shared code. It
re-implements every computation from the specification (including the
interpreter's `rng`, `round-to` and `decimal` rounding, the floor square root,
the bisection brackets, the power iteration, the class game's equilibria, every
agent model, the equation chain with its probe hooks, the dialectics
predicates, the long-run recurrence, the selectorate equilibrium, every
threshold of §10 and every model figure of §11). It regenerates the **text** of
every displayed table with the same formatting and requires exact agreement:

| part | checks | covers |
|---|---|---|
| I value | 9 | §3 |
| II distribution | 7 | §4 |
| III games | 9 | §5 |
| IV economy and loops | 10 | §6–§7, including all 180 history rows the self-rewriting economy writes into its own source, the 27-setting grid and all 240 edge probes |
| V dialectics | 4 | §8 |
| VI(a) classical | 5 | §9 C1–C4 |
| VI(b) selectorate | 5 | §9 S1–S4 |
| VI(c) extremes | 11 | §10 |
| VI(d) evidence | 2 | §11 |

`verify-materialist.sh` runs the twelve programs (112 assertions), the
self-rewriting sequence (six rewrites, then a fixed point) and the cross-check:
13 checks, all passing. The two implementations share a specification, not
code, so they catch implementation errors but not specification errors; the
empirical comparison of §11 is the check on the specification.

---

## 14. Limits

- **The integrated model formalizes; it does not estimate.** Its equations come
  from Parts I–III, its parameters from the model's own steady-state algebra,
  and its conclusions are theorems about the model. Where a conclusion depends
  on an unpinned parameter (loss sensitivity, aspiration messaging, shock
  size), §6 reports the whole grid and §10 the threshold. The empirical
  comparisons of §11 are not fits.
- **The outside-option formula lets the wage share approach 1 at full
  employment.** It drives the capital-flight region below u = 1/12, the
  job guarantee's inertness below u_c = 1/11 and the zero elasticity at u = 0.
- **Mechanization is exogenous** in the integrated model (μ fixed); X3 computes
  when it pays, but firms do not choose it. **There is no demand side**, the
  likely reason for the trending unemployment.
- **The value function's curvature is a modelling choice**, valid only for
  losses smaller than K, and X4 shows that K decides the radical threshold.
- **Accountable planning's immunity to inflation is by construction.**
  Vouchers redeem at labour value, which is the proposal's design. The model
  shows its consequences; no economy has run it, so no data test it.
- **Edge verification is local**: exact finite differences at ten states. It
  establishes the sign where tested and that every channel fires somewhere,
  not that it holds everywhere (U → B shows it does not).
- **Behaviour is equilibrium play of stylized games**, not estimated
  behaviour.
- **The agent models are small** (20 to 100 agents) and seeded; their numbers
  are samples, reproducible bit for bit, and the exact results of E1–E2 are
  what they approximate.
- **Reconstructed inputs are flagged where they appear**: the plan4 table, the
  prior/likelihood pairs behind two of the post's posteriors, the intermediate
  demography values, the encoding of CE Table 10.1, and d = 0 before
  admissibility in the post's examples.
- **The data are mostly from the US and other rich democracies**; several
  empirical sources were consulted at second hand (Shaikh and Zachariah via
  *Classical Econophysics*; Cockshott and Cottrell and Işıkara and Mokre via
  the essays).
- **Not modelled:** international trade and unequal exchange, the party-state
  beyond its collusion and selectorate readings, Wright's social-architecture
  model of firm formation, the psychoanalytic models of the contradictions post
  (foreclosure appears only as the diagnosis of §8), and the
  Buddhism–dialectics comparison itself.

---

## 15. The paper

`MATERIALIST-ECONOMY-PAPER.md` presents the study as an academic paper. It is
organized by theme, and each of §§4–8 runs mechanism, thresholds, evidence and
verdict:

| paper section | content | here |
|---|---|---|
| §1–§2 | the essays' argument, the fourteen propositions T1–T14, and the three tests (derivation, extremes, data) | §1 |
| §3 | Palimpsest, with the traced `me-tour.pal` example | §2 |
| §4 | value, prices and profit (T1, T2, T5, T6) | §3, §9 C1, §10 X3/X5/X10 |
| §5 | money and its distribution (T3, T4, T10) | §4 |
| §6 | class conflict in the labour market (T8) | §5 G1–G3, §10 X1–X2, §11 |
| §7 | politics (T7, T9, T11, T13) | §5 G4–G7, §9 S1–S4, §10 X4/X8/X9 |
| §8 | the integrated economy (T11–T14) | §6–§8, §9 C2, §10 X6–X7 |
| §9 | the scorecard and the data at a glance | §11–§12 |
| §10–§12 | verification and reproduction, limitations, conclusion | §13–§14 |

It contains references and a list of the sources consulted online. A live
version with charts is published as a Claude document; the Markdown file marks
each chart's position and names the program that reproduces its data.
