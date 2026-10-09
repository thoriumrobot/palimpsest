# Feedback Loops as Rewrite Rules: An Exact Model of Value, Class and Political Survival in Palimpsest

October 2026

## Abstract

Seven essays argue for a materialist political economy in three layers:

- **Physical.** Labour value is conserved in exchange. This conservation makes prices track values and gives money a two-class distribution.
- **Social.** Class relations drive capitalism's dynamics: a falling profit rate, a reserve army that disciplines labour, and a turn to radical politics when living standards fall.
- **Programmatic.** Democratic planning would remove these dynamics. Its instruments are a job guarantee, non-circulating labour vouchers, a divided government and an asset cap.

We state the essays' claims as eighteen propositions and write every mechanism as rewrite rules in the language Palimpsest, with exact rational arithmetic. Each proposition then faces three tests:

1. Does the model derive it?
2. Where does the model's behaviour change: at which limits, thresholds and tipping points?
3. Do published data show the pattern at a magnitude the model can match?

**Value and profit.** Conservation, the plan's fast convergence and the real opposition of wages and profits are derived exactly. Prices track values as the data show, but the model's price–value deviations (0.8–3.1%) are smaller than the 7–20% measured. The falling profit rate is determinate only given a wage rule (Okishio holds in 18 of 18 cases) or slowing demography. Its long-run attractor meets a floor at a computable rate of population decline.

**Money.** Conservation yields an exponential lower class with Gini 0.524, against 0.5 in US data. Capital income condenses far beyond the observed top-1% wealth share of 32.5%, unless an asset cap bounds it.

**The labour market.** The bargained wage has the measured elasticity of −0.1 at 5.5% unemployment. Below 1/12 unemployment capital flight is an equilibrium. A job guarantee raises private wages by 5%, as India's did, at 12.5% unemployment, and has no effect below 1/11.

**Politics.** Radical voting needs a deep loss. The threshold is set by the curvature of the value function, not by loss aversion. This matches the finding that far-right votes rise after financial crises but not ordinary recessions. A divided government defeats collusion once it has at least 1/P independent offices, where P is the audit probability and a whistle-blower's bounty equals the rent.

**The integrated economy.** Capitalism's labour share falls 19.9% in 60 periods, against 20.2% for the US from 1960 to 2026. Its unemployment, however, rises without limit, because mechanization outruns accumulation. A crisis becomes a lasting radical government above a sharp threshold in aspiration messaging, between 0.26 and 0.27. Planning removes every channel into the radical vote.

**Finance.** Credit at loan-to-value LTV prices a fixed stock at S/(1 − LTV) and hands the new money to incumbent holders, adding no output. Capital gains set against resets (heirs, bankruptcy, taxes) give a Pareto class with exponent log₂(q/p), which condenses below α = 1. Read on this lattice, the US top-1% wealth shares imply α = 1.46 in 1989, against direct estimates of 1.48–1.55, and 1.32 in 2026. Distress selling becomes a self-reinforcing spiral exactly when one sale lowers the price by more than the spacing of leverage. In a fourth, financialized regime, credit holds employment until the falling profit rate and interest bring a Minsky crisis. Each such crisis becomes a radical government through the household credit crunch, and none does without household debt. The regime elects radical governments in all 27 stress settings, against capitalism's 15. Inflation postpones the debt crisis; deflation brings it forward. Induced mechanization stops the unemployment trend, but it shows that the labour-share match rests on that trend.

Every displayed table is regenerated digit for digit by an independent implementation (80 checks).

## 1 Introduction

The seven essays studied here make an unusually testable argument for a Marxist political economy. They cover mechanical materialism, accountable planning, objections and responses, philosophies of contradiction, structural dialectics, fascism as an outgrowth of capitalism, and job creation. Their argument runs from physics to politics.

- **It starts from conservation.** Following Cockshott, value is a conserved quantity, abstract labour time. Its conservation in exchange is meant to generate statistical regularities, as the conservation of energy does in a gas: prices close to labour values, an exponential distribution of money, and a two-class income structure.
- **Class relations then drive the dynamics.** Who owns the means of production, and who can walk away from a bargain, determine a falling profit rate, a reserve army that holds wages down, money creation that favours asset holders, and radicalization when living standards fall.
- **A design is meant to remove those dynamics.** That design is accountable planning, which keeps democracy.

Each link in this chain is a claim about a mechanism, so each can be stated precisely and checked. We ask three questions of every link:

1. Do the essays' mechanisms, stated precisely, produce the outcomes the essays claim?
2. Where does their behaviour change qualitatively, at limits, thresholds and tipping points that a verbal argument cannot locate?
3. How well do the resulting patterns and magnitudes match the empirical record?

**The approach.** The mechanical-materialism essay defines a scientific law as "regularities governing how systems change states under specified conditions". A law of that form is a rewrite rule: a term of one shape becomes a term of another, under conditions. We therefore write the economy as rules in Palimpsest, a term-rewriting language with exact rational arithmetic.

In that language:

- one period of the economy is the normalization of a state term;
- a feedback loop is a chain of rules through which a quantity computed in one period re-enters the next;
- whether an edge of the causal diagram is real becomes a computation: perturb one variable, hold the others fixed, recompute, and read the sign.

**Class analysis as the input to games.** A class position fixes who the players are, what each can fall back on if bargaining fails, and what surplus is at stake. The reserve army is labour's outside option, and a job guarantee replaces it. That single substitution propagates through the wage bargain and the class-struggle game. Through prospect theory it reaches the share of voters willing to back a radical gamble.

### 1.1 Findings in brief

- **The accounting and the equilibria hold.** Conservation, the exponential limit, the Cantillon transfer, voucher non-circulation and the job guarantee's effect on employers are exact properties of the rules.
- **Every "always" becomes a threshold.** The falling profit rate, the radical coalition, the job guarantee's power and the patronage spiral each hold only on a definite part of parameter space, and the model computes its boundary.
- **Finance sharpens the political results.** A crisis turns into a radical government through the household credit crunch, which removes a reference point that credit had raised. Inflation postpones the second debt crisis but cannot prevent the first, and capital gains make a Pareto class whose size is set by policy.
- **The patterns match; some magnitudes do not.** Without any fitting, the wage curve, the labour share's decline, the lower-class Gini and the job guarantee's wage effect come out close to the data. Price–value deviations, wealth concentration and the long-run path of unemployment do not. In each of these failures the model's direction is right and a mechanism is missing.

### 1.2 How the paper is organized

Section 2 states the essays' claims as propositions T1–T14 and defines the three tests; §9 adds four financial propositions, T15–T18. Section 3 describes Palimpsest in enough detail to reproduce every run.

Sections 4–8 follow the essays' own chain from physics to politics:

- §4 value, prices and profit;
- §5 money and its distribution;
- §6 class conflict in the labour market;
- §7 politics;
- §8 the integrated economy, in which all these mechanisms run together in three regimes.

Each of these sections first builds the mechanism, then locates its thresholds, then sets it against the data, and ends with a verdict. Section 9 adds finance: credit money, capital gains, debt deflation, and a fourth, financialized regime of the integrated economy (T15–T18), with two further omitted mechanisms, induced mechanization and capital mobility.

Section 10 collects the verdicts, §11 gives the reproduction protocol, §12 the limitations, and §13 concludes.

## 2 The theories and how they are tested

### 2.1 Eighteen propositions

The essays draw on three reference works:

- **Classical Econophysics** (Cockshott, Cottrell, Michaelson, Wright and Yakovenko, 2009): the physics of value, money and profit.
- **How the World Works** (Cockshott, 2019): the historical materialism, including the demographic theory of the profit rate.
- **The Logic of Political Survival** (Bueno de Mesquita, Smith, Siverson and Morrow, 2003): selectorate theory, which we use to formalize the essays' claims about party-states, patronage and divided government.

The essays' claims reduce to fourteen propositions here, and §9 adds four about finance. The table numbers them in the order the essays raise them. Sections 4–8 group them by theme, and the last column gives where each is tested.

|  | proposition | essay (quoted) | tested in |
| --- | --- | --- | --- |
| T1 | Value is conserved in exchange; surplus value cannot arise from exchange | mechanical materialism: "in the exchange of commodities, abstract socially necessary labor time is conserved" | §4.1 |
| T2 | Labour values predict market prices | mechanical materialism: "labor values reliably predict prices" | §4.2 |
| T3 | Conservation yields an exponential distribution of money, and capital income a Pareto upper class | mechanical materialism: "the lower approximately 97% … follows an exponential law … the upper approximately 3% follows a Pareto power law" | §5.1–5.2 |
| T4 | Money creation redistributes real claims toward asset holders | mechanical materialism: it "does not create new value but redistributes existing claims on real output" | §5.3 |
| T5 | The rate of profit tends to fall | mechanical materialism: "the rate of profit tends to fall over the long run" | §4.3, §8.3 |
| T6 | Planning is a fast contractive computation | accountable planning: "By approximately the twentieth pass they converge" | §4.1 |
| T7 | Quadratic voting replaces the purchasing-power filter and protects intense minorities | accountable planning: it "directly replaces the purchasing-power filter with a democratic one" | §7.5 |
| T8 | A job guarantee breaks employers' power | accountable planning: capitalists "must offer conditions attractive enough to compete with the government sector" | §6.1–6.3 |
| T9 | A divided government cannot conspire | accountable planning: it "is divided within itself … so that it cannot conspire against the people" | §7.3–7.4 |
| T10 | Vouchers and an asset cap prevent accumulation and counter-revolution | accountable planning: vouchers "cannot be lent, invested, or accumulated" | §5.2–5.3 |
| T11 | Falling living standards and inflation drive voters to radical, authoritarian options | fascism: "The more radical side will always form the more powerful coalition"; accountable planning on inflation and terror management | §7.1, §8.4 |
| T12 | The Cold War forced capitalism to raise living standards universally | fascism: the wealthiest countries "forced their capitalists … to pursue policies that universally raised living standards" | §8.2 |
| T13 | Right-wing patronage employment produces a self-reinforcing spiral | job creation: "The right buys off every community leader … It's a downward spiral" | §7.2, §8.4–8.5 |
| T14 | Planning defuses authoritarian politics | accountable planning: "the existential anxiety that drives populations toward authoritarian leaders is defused" | §8.2, §8.4–8.6 |

Two essays supply method rather than propositions, and we implement both:

- **Philosophies of contradiction.** It argues, after Colletti, that class conflict is a *real opposition* rather than a logical contradiction, and it describes how an alternative can be "foreclosed". The real opposition appears as the wage–profit frontier (§4.2), and foreclosure as a computed state of the integrated model (§8.6).
- **Structural dialectics.** It defines formal predicates for transitions between social forms: viability, necessity, Phase Inversion, warrant and synthesis. They are evaluated on the model's own viability (§8.6).

The objections essay adds a computable rule for skilled labour (§4.1).

### 2.2 Three tests

Every proposition faces the same three tests, and every result comes from an `assert` or a `display` in a program listed in Appendix B.

**1. Derivation.** Does the model produce the claim? We use four verdicts:

- **Derived.** The proposition follows from the rules for all parameter values. Such a result is a theorem of the model, typically checked on certified exact brackets.
- **Reproduced.** It holds at the model's parameters, and we report the region where it holds.
- **Qualified.** It holds only under an extra condition that the model makes explicit.
- **Contradicted.** It fails.

**2. Extremes.** Where does the mechanism's behaviour change? We locate limits, thresholds, switch points and tipping points exactly. A verbal argument can say that a mechanism operates; only a model can say where it stops.

**3. Data.** Do published measurements show the pattern the model produces, at a magnitude the model can match?

The model is not fitted to any of the data. Its parameters come from its own steady-state algebra (§8.1) or from the essays. A match is therefore a check of the mechanism, not a calibration. Where a comparison is only qualitative, we say so. Each empirical figure used in a quantitative comparison is held, with its source, as a constant in `examples/me-evidence.pal`, beside the model's counterpart.

## 3 Method: feedback loops as rewrite rules in Palimpsest

Palimpsest is a term-rewriting language with a Rust interpreter. A program has four parts:

- a set of rewrite rules;
- strategies, which say where and in what order the rules apply;
- a distinguished subject term, `main`;
- a sequence of commands.

Programs may also rewrite their own source file, under explicit capabilities. This section describes the language as far as the model uses it, in enough detail to reproduce every result.

### 3.1 Terms, rules and strategy

Terms are symbols, strings, numbers and parenthesized lists. A rule has a name, a left-hand pattern, a right-hand side and optional `where` clauses:

```
rule NAME : LHS => RHS where CLAUSE, CLAUSE, ...
```

Pattern variables take three forms:

- `?x` matches one subterm.
- `?xs...` matches a sequence of list elements.
- `!x` is *strict*: the subject's argument is forced to normal form before matching.

A clause is either a guard, which must normalize to `true`, or a binding `?v <- EXPR`. Clauses are evaluated left to right with the full rule set, so a guard may call any library function.

The model uses a single strategy throughout:

```
strategy eval = outermost(prim + rules)
```

This is normal-order reduction. At each step it rewrites the leftmost-outermost redex, trying built-in primitives before rules and rules in source order. Every step consumes one unit of **fuel**, declared by `#fuel N`. Running out of fuel is an error, never a silent truncation. The fuel remaining is printed after each run and serves as a fingerprint of the derivation.

### 3.2 Numbers, records and commands

**Numbers.** They are exact. An integer of any size, or a rational written `n/d`, is a single term. A number whose value is an integer is always represented as an integer, so 6/3 *is* 2. Structural equality is therefore equality of values. The primitives are:

- the usual arithmetic and comparisons;
- `q/` (exact division);
- `num` and `den`;
- `floor` and `ceil`;
- `expt`;
- `isqrt`;
- `round-to x K` (nearest multiple of 1/K, half up);
- `decimal x d` (display only).

Rounding happens only where the source says so. The integrated model, for example, rounds its state to 10⁻⁶ once per period.

**Records.** The economy's state is a record `(rec (K 270) (kap 3) …)`, read with `@` and updated with `set@`, `put@` and `add@`. A function passed as data, `F`, is applied by writing `(app F x)`.

**Commands.** A program file begins with `#lang palimpsest` and directives (`#fuel`, `#memo`, `#caps`, `#rebind main`), followed by:

```
show TERM with S         // print the normal form
display TERM with S      // print a string normal form as text
assert TERM with S       // PASS iff the normal form is true; a FAIL exits non-zero
let $NAME = TERM with S  // normalize once, substitute $NAME in later commands
rewrite self with S      // rewrite main and write the program back to its file
```

A `rewrite self` is transactional. It writes atomically, journals the old file, and writes nothing under `--dry-run`. A `transition` is a rule that only a named strategy can reach. A program whose `main` holds the economy's state therefore advances by exactly one period per run. When the transition's guard fails, the file is a byte-identical fixed point: a quine.

**Performance and observation.** Two interpreter options support this.

- `#memo` records the subterms already proven normal, and the normal form of each argument forced at a strict position. It changes fuel counts but never a normal form. On the program below it cuts the work of 400 periods from 29,505 steps to 10,568.
- `--trace N` prints the first N rewrite steps as `rule: redex => contractum`, indenting steps taken inside guards and strict arguments. It is observation only: a unit test confirms the normal form and fuel are unchanged.

### 3.3 A worked example: one feedback loop, traced

`examples/me-tour.pal` is the smallest complete instance of the method. It is a single loop K → E → u → w → profit → K:

- Capital *K* employs E = K/3 of N = 100 workers.
- Unemployment u = 1 − E/N sets the bargained wage share w(u) against the reserve army (§6.1).
- Profit (1 − w)E is saved at 3/5, and capital depreciates at 3%.

```
rule wage : (wage !u) => (q/ (+ 1/5 (* 4/5 (* ?u 2/5))) (+ 1/5 (* ?u 4/5)))
rule step : (step (st ?t ?k)) => (st ?t1 (round-to ?k2 1000))
  where ?t1 <- (+ ?t 1), ?e <- (min 100 (q/ ?k 3)), ?u <- (- 1 (q/ ?e 100)), ?w <- (wage ?u),
        ?k2 <- (+ (* 97/100 ?k) (* 3/5 (* (- 1 ?w) ?e)))
rule run-0 : (run !s !n) => ?s where (<= ?n 0)
rule run-n : (run !s !n) => (run (step ?s) (- ?n 1)) where (> ?n 0)
```

`palimpsest examples/me-tour.pal --trace 22` shows the first period (excerpt):

```
      2   min: (min 100 (q/ 270 3))  =>  (if (<= 100 (q/ 270 3)) 100 (q/ 270 3))
      3   <prim>: (q/ 270 3)  =>  90
      4   <prim>: (<= 100 90)  =>  false
      5   if-false: (if false 100 (q/ 270 3))  =>  (q/ 270 3)
      6   <prim>: (q/ 270 3)  =>  90
      9   wage: (wage 1/10)  =>  (q/ (+ 1/5 (* 4/5 (* 1/10 2/5))) (+ 1/5 (* 1/10 4/5)))
     15   <prim>: (q/ 29/125 7/25)  =>  29/35
     21 step: (step (st 0 270))  =>  (st 1 (round-to 18981/70 1000))
     22 <prim>: (round-to 18981/70 1000)  =>  271157/1000
```

The trace shows three things.

1. **The arithmetic is exact.** The wage share at u = 1/10 is the rational 29/35.
2. **The loop closes through the state.** Profit in period *t* becomes capital in period *t* + 1, so the feedback loop *is* the recursion of `run`.
3. **Laziness has a cost.** `min` copies its unevaluated argument, which is then computed twice (steps 3 and 6). A lazy variant of `run` with `?s ?n` in place of `!s !n` grows its counter into `(- (- … 1) 1)`, which every guard re-evaluates, so a linear loop costs quadratic work. This is why every library entry point is strict.

The loop has a rest point where saving replaces depreciation: w = 17/20, u = 1/12 and K\* = 275. The program asserts convergence to it within 1/1000.

## 4 Value, prices and profit (T1, T2, T5, T6)

The essays' argument starts from production. This section moves in three steps:

1. what is conserved;
2. how prices relate to what is conserved;
3. what happens to profitability over time.

The results are checked by `me-value.pal` (17 assertions) and `me-classical.pal` (8). The thresholds come from `me-extremes.pal` (§X3, §X5, §X10).

The reference economy E3 has three sectors: means of production, necessities (the wage good) and luxuries.

```latex
A=\begin{pmatrix}1/5&1/5&1/10\\1/10&1/5&0\\0&0&0\end{pmatrix},\quad l=(1,\;2,\;1),\quad b=(0,\;1/4,\;0).
```

### 4.1 Value, exchange and the plan (T1, T6)

**Values and the plan.** Labour values are computed by exact Gauss–Jordan inversion: λ = (50/31, 90/31, 36/31). The planner's loop x ← Ax + d is three rules.

The planning essay publishes a four-sector plan. On a table that reproduces it, the loop stops after **18 passes**, when two successive estimates agree to one ton; the essay says "approximately the twentieth pass". For every final demand, the value of the net product equals the living labour performed (λ·d = l·x).

**Exchange.** An exchange table that is reflexive, symmetric and transitive has the form Tᵢⱼ = vᵢ/vⱼ, so it determines a value vector, and every cycle of trades returns what it started with. Breaking transitivity by 10% creates a three-trade cycle that returns 11/10, a pure M–C–M′. Surplus value cannot arise in value-conserving exchange.

**Real data and skilled labour.** *Classical Econophysics* Table 10.1 is a four-industry input–output table. It yields labour values per dollar within 5.65% of their mean, and the value of final output equals the wage bill, 244, exactly.

The objections essay prices a surgeon's hour at 3/2 simple hours. If the teachers are themselves skilled, the coefficient is the fixed point of a contraction, which is 7/4 rather than 3/2.

**Verdict.** T1 and T6 are *derived*. Conservation holds by construction for any transitive exchange table and fails for any intransitive one. The plan's speed is set by the spectral radius of A.

### 4.2 Prices and the real opposition (T2)

If value is conserved, what makes prices deviate from it? In the classical account the answer is the profit rate.

**The profit rate, certified.** The uniform rate r\* solves p = (1 + r)p(A + b⊗l). We never compute an eigenvalue. Instead we bisect on *r*, deciding exactly at each step, by the Hawkins–Simon test on rational matrices, whether the spectral radius of (1 + r)M is below one. Each bracket is a certificate: two exact decisions bound r\*. After 30 halvings r\* ∈ \[0.22849294, 0.22849294).

Two theorems hold on every bundle tested:

- **The Fundamental Marxian Theorem** (r\* > 0 iff exploitation is positive) holds on 21 wage bundles and on all 64 bundles of a grid. These include the boundary where λ·b = 1 and r\* = 0 exactly.
- **The generalized commodity exploitation theorem** holds on the same 21 bundles: every basic commodity is "exploited" exactly when r\* > 0.

The theorems therefore do not single out labour, and the case for labour has to be empirical.

**The real opposition.** With the net product as numeraire, the wage w(r) falls strictly from 1 at r = 0 to 0.0174 at r = 1.9 (Figure 1). Whatever one class gains, the other loses. This exact opposition is the "real opposition" of the contradictions essay. Along the same frontier, the mean absolute weighted deviation (MAWD) of prices from values rises from 0 at r = 0 to 0.0349 at r = 1. It is zero at every *r* when the value composition is uniform.

[Chart: see the published version of this paper; its data are reproduced by the program named in the caption below.]

*Figure 1. The wage–profit frontier of E3 (`me-value.pal` §3.5; exact rationals shown to four decimals).*

**The data.** The empirical literature supports T2 strongly in direction and moderately in magnitude.

- **Correlations.** Cockshott and Cottrell (1997) report a correlation of 0.977 between sectoral prices and labour values for the UK. Zachariah (2006) studied eighteen OECD countries; the seven that Classical Econophysics reports (Table 10.3) have correlations of 0.942–0.986.
- **Deviations.** Shaikh (1998) measures a MAWD of 9.2% for the US, and *Classical Econophysics* reports 7.1–10.5% for 1947–72 (Table 10.2).
- **Breadth and stability.** Işıkara and Mokre (2022) examine more than 36,000 price vectors from 42 countries for 2000–17. They find deviations that are "small and stable"; the mechanical-materialism essay quotes them at 10–20%.

The model reproduces the structure of these findings: deviations vanish at r = 0 and grow with the profit rate. Its deviations are too *small*, however. E3 at its own profit rate gives 0.8%, and Table 10.1 gives 3.1%.

The reason is aggregation. Three or four sectors cannot carry the dispersion of capital composition found in 40-to-100-industry tables. Real data also include rents, taxes and market prices that deviate from prices of production.

**Verdict.** T2 is *derived* in structure and *supported* by the data. The model underestimates the magnitude of deviations by a factor of three to eleven against Shaikh's 9.2%.

### 4.3 The falling rate of profit (T5)

The frontier is static. The essays' strongest dynamic claim is that the profit rate tends to fall over time. The model gives three readings of it, at three timescales.

**Technique: Okishio.** Eighteen mechanizing changes were tested. Capitalists adopt a change iff it lowers unit cost at current prices.

- **With the real wage fixed**, Okishio's theorem holds in all 18: adopted changes raise r, and rejected ones would have lowered it.
- **With the rate of exploitation held constant**, r falls after 11 of the 14 adopted changes.

The tendency is therefore determinate only given a wage rule.

**When mechanization pays.** A rejected technique becomes cost-reducing if the wage rises far enough. For three rejected techniques the switch point is the same, β\* = 0.2822, a real-wage rise of 12.9%:

- in the means-of-production sector, a 0.10 labour cut with 0.05 more machinery;
- in the same sector, a 0.20 cut with 0.10;
- in necessities, a 10% labour cut with 0.10.

All three share one ratio of machinery added to labour saved, 1/2. A technique with ratio 1 never pays at any wage (asserted). The switch point depends only on that ratio, not on the size of the change. This is the Ricardo effect in exact form: higher wages call forth mechanization at a computable threshold. Section 8.3 shows the other half of the loop, in which mechanization swells the reserve army and lowers the wage.

**Demography: the long-run attractor.** `lib/longrun.pal` runs *Classical Econophysics*' accumulation model in exact discrete time. Capital grows at λR − (g + δ), where λ is the share of profit invested, and labour grows at *n*. They keep pace when

```latex
R^{*}=\frac{n+g+\delta}{\lambda},
```

independently of the wage share. Four economies with wage shares from 0.2 to 0.8 all converge to R\* = 2/15, monotonically in distance (Figure 2).

[Chart: see the published version of this paper; its data are reproduced by the program named in the caption below.]

*Figure 2. Every wage share converges to the same long-run profit rate (`me-classical.pal` §C1; every fourth period).*

**The floor.** Because L/K > 0, the profit rate is bounded below by −(1 − w)(g + δ), a floor the attractor formula omits. The attractor meets the floor at

```latex
n^{*}=-(g+\delta)\bigl(1+\lambda(1-w)\bigr)=-0.0248\quad(w=\lambda=3/5,\ g=0,\ \delta=0.02).
```

| n | R\* | floor | R after 599 periods |
| --- | --- | --- | --- |
| −0.0100 | 0.01667 | −0.00800 | 0.01667 |
| −0.0200 | 0 | −0.00800 | 0.00042 |
| −0.0248 | −0.00800 | −0.00800 | −0.00534 |
| −0.0300 | −0.01667 | −0.00800 | −0.00766 |
| −0.0500 | −0.05000 | −0.00800 | −0.00799 |

The attained limit is max(R\*, −(1 − w)(g + δ)). At the inflection n\* convergence slows dramatically: after 599 periods the rate is −0.00534, still 0.0027 short of its limit of −0.008, whereas at n = −0.05 it is within 0.00001. This is the critical slowing-down of a transcritical bifurcation, in which the interior attractor and the floor exchange stability.

*How the World Works* (§5.9) says that a shrinking population has a negative attractor. That is right in sign, but the model adds three things: the rate is bounded, it depends on the wage share, and near the threshold it is approached very slowly.

**The data.** Long-run estimates show a fall, but not a steady one.

- **Maito (2014)** estimates an average for six core countries (Germany, the US, the Netherlands, Japan, the UK and Sweden) of 40.6% in 1870–74. It falls to 15.9% in 1970–74, to 12.3% in 1975–79 and to a low of 10.8% in 1982. It recovers to 12.9% in 2000–04 and 14.6% in 2007.
- **Basu (2022)** finds a negative world trend for 1960–2019, driven by a falling output–capital ratio.

The three readings fit the data in different ways:

- **Okishio** rules out technique alone as the cause of a secular fall.
- **Constant exploitation** matches Basu's decomposition, in which the output–capital ratio is what falls.
- **The attractor** predicts a falling rate as population growth slows. Core-country population growth fell from about 1% a year in the late nineteenth century toward zero, and Japan's stationary population coincides with its low profitability.

The recovery of 1982–2007 is the counter-tendency that the integrated model makes explicit (§8.3): profitability is restored by a growing reserve army and a falling wage share.

**Verdict.** T5 is *qualified* by the model and *supported* by the data as a long-run tendency. It needs a wage rule or slowing demography, and the model cannot date the turning points.

## 5 Money and its distribution (T3, T4, T10)

The essays carry conservation from value to money. If money is conserved in exchange, its distribution is fixed by statistics before any question of merit arises. Capital income and money creation then distort that distribution, and the planning proposal is meant to undo the distortions.

The results are checked by `me-distribution.pal` (18 assertions). Randomness comes from a deterministic hash of an integer seed, so every sample is reproducible bit for bit.

### 5.1 Conservation and the exponential law (T3, lower class)

**The model.** If every division of M units among N agents is equally likely, one agent's holding has the exact law

```latex
P(m=k)=\binom{M-k+N-2}{N-2}\Big/\binom{M+N-1}{N-1}.
```

Its total-variation distance to the geometric law falls from 0.0339 to 0.0031 to 0.0003 for N = 10, 100 and 1000. The geometric law's Gini is 1/(1 + q) = 11/21 ≈ 0.524. Enumerating all macrostates for small N shows that the equal split is the *least* probable one.

The law also arises dynamically. Random one-unit trades among 100 agents raise the Gini from 0 to 0.46 after 20,000 events. The pooled histogram is geometric: 9.20% of agents hold nothing, against 9.09% predicted. No agent does anything but trade at random, so inequality of this degree is the generic outcome of conservation, not evidence of differential merit.

**The data.** Ludwig and Yakovenko (2022) fit US tax data for 1983–2018. The lower class, about 96% of tax units, is exponential with a Gini near 0.5. The model's 0.524 is the discrete counterpart of that value.

### 5.2 Capital income, condensation and the asset cap (T3, upper class; T10)

**The model.** Five owners and 95 workers trade under two kinds of event:

- **Wages** are additive: an owner pays a random worker one unit.
- **Sales** are multiplicative: the receiving owner is drawn in proportion to holdings.

The accountable-planning essay proposes a cap θ on private holdings, whose excess goes to a public fund that pays wages. It is one more rule.

| cap θ | owners' share after 60,000 events | workers' Gini | owners' holdings |
| --- | --- | --- | --- |
| none | 0.9764 | 0.8439 | (0, 0, 0, 0, 952) |
| 60 | 0.2421 | 0.4905 | (0, 58, 59, 59, 60) |
| 30 | 0.1159 | 0.4859 | (4, 25, 26, 29, 29) |

Uncapped, capital income does more than produce a Pareto tail: it *condenses*, and one owner ends with 98% of all money. With a cap, the owners' share is bounded by Cθ/M at every checkpoint, and the workers' Gini returns to the exponential value.

**The data.** In Ludwig and Yakovenko's data the upper class is a Pareto tail holding 34% of income in 2018, and the total Gini is about 0.6. The top 1% income share rose from 9% to 21% over 1983–2018. The Federal Reserve's Distributional Financial Accounts put the top 1% wealth share at 32.5% in Q2 2026.

The model's direction is right: with capital income and no cap, concentration rises. Its magnitude is not. Real economies hold the tail at a power law through forces the minimal model omits: dispersion of returns, inheritance taxation, bankruptcy and the splitting of fortunes among heirs. Section 9.2 adds them. The asset cap itself has no empirical counterpart to test.

### 5.3 Money creation and labour vouchers (T4, T10)

**Money creation.** Take real output Q = 1,000 and money holdings of 600, 300 and 100 (asset holders, middle, poor). Credit 100 new units to the asset holders, who spend first at the old price. The real gains are (100, −75, −25). They sum to zero, and the first recipients gain exactly Q·D/M. The same injection made in proportion to holdings and spent after prices adjust redistributes nothing. Money creation transfers command over existing output; it creates none.

**The data.** Domanski, Scatigna and Zabai (2016, BIS) find that the equity-price channel of post-2008 monetary policy widened wealth inequality. A 10% rise in equity prices would need a rise of about 4¼% in house prices to be distributionally neutral. This is the Cantillon mechanism: new claims reach asset holders first. The model's exact zero-sum transfer is a stylized version of what the BIS measures.

**Vouchers.** Labour vouchers are issued for hours worked and cancelled on purchase. No rule moves a voucher between agents, so *non-interference* holds: one agent's extra work changes no one else's holdings, whereas in the money economy it does. The M–C–M′ circuit has no rule to run on. Within the model this is a syntactic property of the rule set, verified by execution.

**Verdict.**

- **T3** is *derived* and *supported* for the lower class. For the upper class it is *qualified*: the model's tail is too heavy.
- **T4** is *derived*, and the data *support* it qualitatively.
- **T10** is *derived*: non-interference holds and the owners' share is bounded. No data test it.

## 6 Class conflict in the labour market (T8)

Sections 4 and 5 treated the wage as given. This section derives it from class positions. The worker's outside option is fixed by the reserve army under capitalism and by the job guarantee under planning, and it sets the bargain. The bargain in turn sets the stakes of a game in which labour organizes and capital concedes, represses or flees.

The results are checked by `me-games.pal` (20 assertions), with thresholds from `me-extremes.pal` (§X1–X2) and the data comparison from `me-evidence.pal`.

### 6.1 The reserve army as an outside option

**The bargain.** A worker bargains with power β. If bargaining fails, she is re-employed with probability 1 − u and otherwise lives on a benefit *s*. Under a job guarantee paying *g*, the guarantee is the outside option instead. The Nash-bargaining wage shares are:

```latex
w_{\mathrm{cap}}(\beta,u,s)=\frac{\beta+(1-\beta)\,u\,s}{\beta+u\,(1-\beta)},\qquad w_{\mathrm{ap}}(\beta,g)=g+\beta\,(1-g).
```

The capitalist wage has two limits:

- **Full employment.** w(0) = 1: labour captures the whole product, because the threat of dismissal is empty.
- **Total unemployment.** w(1) = β + (1 − β)s = 13/25: labour's share falls to its bargaining power applied to the benefit.

**The steepest point.** The elasticity of the wage with respect to unemployment is

```latex
e(u)=\frac{d\ln w}{d\ln u}=\frac{u\,\beta(1-\beta)(s-1)}{\bigl(\beta+u(1-\beta)\bigr)\bigl(\beta+(1-\beta)us\bigr)},
```

which is zero at both ends. Its magnitude is largest at the inflection

```latex
u^{*}=\frac{\beta}{(1-\beta)\sqrt{s}}=0.3953,\qquad e(u^{*})=-0.2251.
```

In the model, the reserve army's power over wages is weakest near full employment and strongest at 40% unemployment.

**The data.** Blanchflower and Oswald (2005) estimate an elasticity of pay with respect to local unemployment of about −0.1, stable across countries. The model gives −0.093 at u = 5% and −0.148 at u = 10%, crossing −0.1 at u = 5.54% (Figure 3). That is a parameter-free match at realistic unemployment rates. The model also predicts a shape that could be tested: the wage curve should flatten at low unemployment.

[Chart: see the published version of this paper; its data are reproduced by the program named in the caption below.]

*Figure 3. The elasticity of the bargained wage against unemployment, with the measured elasticity (`me-extremes.pal` §X1).*

### 6.2 The class-struggle game and capital flight

**The game.** Workers accept or organize; capital concedes, represses or flees. The payoffs are built from the bargain:

- organizing raises bargaining power from b\_l to b\_h unless capital represses;
- organizing and repression cost k and ρ;
- flight earns capital r\_ext abroad and leaves workers with their outside option.

With b\_l = 1/5, b\_h = 1/2, k = ρ = 1/20, r\_ext = 1/10, s = 2/5 and g = 4/5 at u = 1/5:

| profile | capitalism: W | capitalism: C | planning: W | planning: C |
| --- | --- | --- | --- | --- |
| accept / concede | 0.7333 | 0.2667 | 0.8400 | 0.1600 |
| accept / repress | 0.7333 | 0.2167 | 0.8400 | 0.0600 |
| accept / flee | 0.4000 | 0.1000 | 0.8000 | 0.0000 |
| organize / concede | 0.8500 | 0.1000 | 0.8500 | 0.1000 |
| organize / repress | 0.6833 | 0.2167 | 0.8500 | 0.0000 |
| organize / flee | 0.4000 | 0.1000 | 0.8000 | 0.0000 |

- **Capitalism.** The game has *no pure Nash equilibrium*, and better responses cycle through four profiles. The mixed equilibrium has Pr\[accept\] = 7/10 and Pr\[concede\] = 3/10. Class struggle here is a game without a rest point.
- **Planning.** Repression fails and flight triggers expropriation, so the unique equilibrium is (organize, concede).
- **The grid.** Over 243 settings, planning always has a pure equilibrium in which capital concedes, while capitalism has none in 187. A closed-form condition for "no pure equilibrium" agrees with exhaustive computation in all 243.

**Along the unemployment axis.** The capitalist game changes character at a single point:

- **For u ≤ 1/12 (0.0833)**, capital flight is a pure equilibrium. Up to u = 1/20 there are two such equilibria, (accept, flee) and (organize, flee); above it only (organize, flee) remains.
- **For u > 1/12**, there is no pure equilibrium, and the outcome is mixed. Labour's expected bargaining power is 0.2549 at u = 0.1 and falls to 0.2188 at u = 0.5 as the reserve army grows.

Both thresholds have closed forms. Against organized labour, conceding leaves capital 1 − w\_h, which near full employment is below r\_ext, so flight is the best response once it also beats repression: r\_ext ≥ 1 − w\_l − ρ. With r\_ext = 1/10 and ρ = 1/20 this means w\_l ≥ 17/20, which the reserve-army wage reaches exactly at u = 1/12. Against accepting labour, flight must beat conceding: r\_ext ≥ 1 − w\_l, or w\_l ≥ 9/10, reached exactly at u = 1/20. Above 1/12 the grid's closed-form condition for "no pure equilibrium" holds at every u, because the gap w\_h − w\_l stays above k and ρ. Labour's bargaining power therefore jumps from 0.2000 in the flight region to 0.2549 at u = 0.1 before declining.

This is the model's formal version of Kalecki's (1943) "political aspects of full employment". Near full employment both wage levels approach the whole product, so the owner's best response to labour is to leave. The essays claim that, under planning, capitalists "must offer conditions attractive enough to compete". Under capitalism the claim has a converse: when conditions become attractive for labour, capital exits. Section 9.7 lets the return abroad vary. Section 8.5 shows that this converse is the one causal edge of the integrated model that fails its check.

### 6.3 The job guarantee

The guarantee raises the private wage only if the guarantee wage exceeds the reserve-army wage. Setting w\_cap = w\_ap gives

```latex
u_c=\frac{\beta\,(1-w_{ap})}{(1-\beta)(w_{ap}-s)}=\frac{1}{11}\quad(\beta=1/5,\ s=2/5,\ g=4/5).
```

Below 9.1% unemployment the guarantee is slack. Above it the private-wage gain rises steeply: +1.4% at u = 10%, +5% at u = 12.5%, +8.4% at 15% and +14.5% at 20%.

**The data.** The evidence is mixed in a way the model partly explains.

- **Imbert and Papp (2015).** India's NREGA raised rural private wages by about 5%, but public employment crowded out private employment one for one.
- **Muralidharan, Niehaus and Sukhtankar (2023).** In a randomized rollout, earnings rose 14% and poverty fell 26%. Of the earnings gains, 86% came from *non-programme* earnings, as private wages and employment both rose.

The model predicts exactly this channel: the guarantee raises the private wage by improving the outside option. The observed +5% corresponds to u = 12.5%, a slack rural labour market.

The job-guarantee essay presents the guarantee as decisive at all times. In the model it is decisive in slack markets and inert in tight ones, because the bargaining formula already gives workers more than *g* there. That inertness is partly an artefact of the formula, which lets the wage share approach 1 at full employment (§12.1).

**Verdict.** T8 is *reproduced* above u\_c = 1/11 and *supported* by the data in slack labour markets. It is untested at full employment.

### 6.4 Exploitation as a property relation

Roemer's test defines a coalition as capitalistically exploited if it would be better off withdrawing with its per-capita share of the means of production. Six agents hold capital (0, 0, 0, 1, 2, 9), and a job needs 4 units. On all 63 coalitions the test coincides with "mean capital below the social mean". When every worker has access to the social means of production, as the proposal's job and land assignment provides, no coalition is exploited. Roemer's counterfactual becomes an institution, and it is the same institution as the job guarantee of §6.3.

## 7 Politics (T7, T9, T11, T13)

The economy reaches politics through living standards. When they fall, voters weigh a radical gamble against a moderate sure thing. Networks that provide jobs shape what voters expect, and the structure of government decides whether those in power can collude against everyone else.

This section builds each political mechanism on its own. Section 8 then couples them to the economy.

The results are checked by `me-games.pal` and `me-selectorate.pal` (7 assertions), with thresholds from `me-extremes.pal` (§X4, §X8–X9).

### 7.1 Loss, curvature and the radical coalition (T11)

**The choice.** Voters choose between a moderate option, a sure +1, and a radical gamble: +6 with probability 1/4 and −2 with probability 3/4, an expected value of 0. Outcomes are valued from a reference position D, the voter's standard minus the reference point. The value function is concave over gains and convex and loss-averse over losses. It is piecewise quadratic, so everything stays exact:

```latex
v(x)=\begin{cases}x-x^{2}/(2K) & x\ge 0\\ \lambda\,\bigl(x+x^{2}/(2K)\bigr) & x<0\end{cases}\qquad K=10,\;\lambda=9/4.
```

Choices are single-crossing in D: the gamble is chosen exactly below a threshold, which at these parameters is D = −5.399. The fascism essay names four strata, falling by 6 and 3 or rising by 1 and 2. Weighted by their sizes, they give a radical share of 30%. Measured against an aspiration 3 units above their standard, they give 55%. When every stratum is rising, as in the Cold War pattern, they give 0%.

**What sets the threshold.** The essay attributes radicalization to loss aversion. The function is increasing only for outcomes x ≥ −K, so we search over D ≥ 2 − K, where every outcome lies in that range. The exact threshold at K = 10, by bisection to 10⁻⁵, is:

| λ | 1 | 1.5 | 2 | 2.25 | 2.5 | 3 | 4 | 10 | 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| threshold | −4.838 | −5.246 | −5.367 | −5.399 | −5.423 | −5.456 | −5.492 | −5.547 | −5.575 |

Raising loss aversion a hundredfold moves the threshold by 0.74. When every outcome is a loss (D < −6), λ multiplies both sides of the comparison and cancels, and the condition reduces to

```latex
-1+\frac{11-2D}{2K}>0\quad\Longleftrightarrow\quad D<\frac{11}{2}-K,
```

exact whenever 11/2 − K < −6, that is K > 23/2. Here −1 is the gamble's expected-value shortfall, and (11 − 2D)/(2K) is the premium that convexity over losses pays for the gamble's spread. The premium grows the deeper the voter has fallen.

| curvature K | 10 | 20 | 40 | 80 |
| --- | --- | --- | --- | --- |
| threshold at λ = 9/4 | −5.399 | −14.5 | −34.5 | −74.5 |
| threshold at λ = 1 | −4.838 | −14.5 | −34.5 | −74.5 |
| 11/2 − K | −4.5 | −14.5 | −34.5 | −74.5 |

As the value function approaches linearity (K → ∞), the threshold recedes without bound. A risk-neutral electorate never chooses the radical gamble, however badly off it is, because the gamble's expected value is below the sure option's. Both closed-form cases are asserted.

The radical coalition is therefore a product of *diminishing sensitivity*, the convexity over losses that makes a gamble attractive to those already behind. Loss aversion matters only where outcomes straddle the reference point, and even there its effect is bounded.

**The data.** Funke, Schularick and Trebesch (2016) examine 20 advanced economies over 1870–2014. Far-right vote shares rise by about 30% after financial crises, but not after ordinary recessions. This is the threshold the model computes: only a deep enough loss crosses it.

Lakner and Milanovic (2016) give the related distributional fact. In 1988–2008 the rich-world lower-middle class saw almost no income growth, while incomes near the global median rose by roughly three-quarters. This is the stratum the fascism essay identifies as falling.

Tversky and Kahneman (1992) estimate λ = 2.25, the value the model uses, and the result is insensitive to it. Their curvature estimate, a power exponent of α = 0.88, is close to linear over small stakes. That makes curvature, the operative property, the less well-estimated of the two parameters.

**Verdict.** T11 is *qualified* by the model and *supported and qualified* by the data. "The more radical side will always form the more powerful coalition" holds only in a deep enough loss domain, and the depth is set by curvature. Section 8.4 shows how the threshold behaves once aspirations are themselves shaped by politics.

### 7.2 Patronage (T13)

**The model.** Two ideological networks spend resources on jobs and messages. Members follow attraction, a job binding three times as strongly as a message (the job-creation essay's premise), and resources follow membership. With a capital-funded right network (base funding 3:1), the unique equilibrium has both networks spend everything on jobs, which is weakly dominant for both. If the left creates no jobs while the right does, the right's membership share reaches 0.942, against 0.743 if both do. Given its premise, the essay's conclusion follows.

**The data.** Thachil (2011) shows that the BJP's service-provision networks in India win the votes of poor beneficiaries who would otherwise oppose the party's elite programme. This is the essay's premise in a real case: material provision binds more strongly than messaging.

**Verdict.** T13's premise is *supported* and its static conclusion *reproduced*. Whether patronage produces a self-reinforcing *spiral* is a dynamic question, taken up in §8.4.

### 7.3 Collusion and the divided government (T9)

**The model.** K officials share a rent R if all collude. Any one of them can blow the whistle for a bounty B, and an audit detects the conspiracy with probability P each period. Grim-trigger collusion is sustainable when the discount factor is at least

```latex
\delta^{*}(K)=\frac{1-R/(KB)}{1-P}.
```

With a bounty equal to the rent (B = R), the smallest number of independent officials that cannot sustain collusion at any discount factor is exactly

```latex
\bar K=\lceil 1/P\rceil,
```

because δ\*(K) ≥ 1 iff 1 − 1/K ≥ 1 − P. The program verifies this at five audit rates, from 5% (K̄ = 20) to 50% (K̄ = 2).

The accountable-planning essay's "divided government" therefore has a design rule: the number of independently accountable offices must be at least the reciprocal of the audit probability, and fewer offices with more frequent audits are equivalent. A single ruling party, whose members cannot claim a bounty, sustains collusion at every δ. That is Djilas's new class as an equilibrium.

**The data.** The bounty mechanism has an empirical analogue in corporate leniency programmes, which reward the first conspirator to report. Miller (2009) finds that the US programme of 1993 raised cartel detection and deterred cartel formation.

### 7.4 Political survival (T9)

Collusion is one route to unaccountable power. Selectorate theory describes another: a leader who needs few supporters can buy them with private goods.

**The model.** For the book's utility √x + √g + √y + √l, the selectorate equilibrium reduces to closed forms. The share of spending on private goods is exactly

```latex
\frac{Wg}{M}=\frac{p}{p+W},
```

which the book calls "perhaps the key" result. The incumbent must deliver T = V\_c − Dcs, where D = δ(1 − W/S)/(1 − δ) is the loyalty term. Square roots are exact integer floors to 10⁻⁹, and the largest stationarity residual is 8 × 10⁻⁹.

The module reproduces the book's limiting cases. The revenue-maximizing tax is 2 − √2, matched to eight digits, and utilitarian welfare is 2.57893, matched to all reported digits. As the coalition W grows, taxes, the private share and the leader's surplus fall, and outsiders' utility rises, as the book predicts. One exception appears with a narrow selectorate (S = 2,000): private goods per member *rise* from W = 500 to 1,000, because the loyalty norm vanishes as W/S → 1/2.

**Patience.** The leader's surplus depends sharply on how much the coalition values the future. With N = S = 100,000, W = 1,000 and p = 10,000:

| δ | incumbent tax | spending M | leader's surplus | coalition member's utility |
| --- | --- | --- | --- | --- |
| 0 | 0.5619 | 17,117.7 | 0 | 5.538 |
| 0.5 | 0.5733 | 4,752.2 | 12,394.2 | 3.481 |
| 0.9 | 0.5832 | 207.6 | 16,949.3 | 1.668 |
| 0.99 | 0.5855 | 2.1 | 17,155.2 | 1.238 |

An impatient coalition (δ = 0) values future private goods at nothing. Loyalty is then worthless, and the leader must spend all revenue to survive: kleptocracy is zero. A patient coalition (δ → 1) is held by loyalty alone, and the leader keeps almost everything. Secure incumbency breeds extraction, which is the selectorate counterpart of Djilas's new class in §7.3.

**The documents' polities.** Read as points (W, S), the polities the documents discuss differ sharply:

- a party-state (S = 100,000, W = 100) spends 99.0% of its budget on private goods;
- patronage capitalism (W = 1,000) spends 90.9%;
- majoritarian government (W = 50,000) spends 16.7%.

The selectorate model cannot tell accountable planning from any other majoritarian system. Its distinctive features act on the economic base and on collusion.

**The data.** Selectorate theory is empirically contested. Clarke and Stone (2008) show that most of its cross-national findings lose significance once democracy is controlled for. The model sides with the critics in one respect: what distinguishes the proposal lies outside the selectorate model.

**Verdict.** T9 is *derived* for collusion, with the design rule K̄ = ⌈ 1/P ⌉, and *plausible* on the leniency evidence. Its selectorate reading is *reproduced* but empirically *contested*.

### 7.5 Quadratic voting and the direction of production (T7)

**The model.** Each voter has 36 credits over three categories: investment, necessities and luxuries. Workers with valuations (2, 6, 1) cast (3, 5, 1); owners with (1, 1, 8) cast (0, 0, 6); a green minority with (9, 1, 1) casts (6, 0, 0). For 90, 5 and 5 voters the tally is (300, 450, 120), so luxuries receive 13.8% of the votes. Demand weighted by purchasing power, using the uncapped distribution of §5.2, puts 78.1% of spending on luxuries. Purchasing power, not need, decides what a market produces.

**The data.** Quarfoot et al. (2017) find in a large national poll that QV elicits less polarized responses, more sensitive to intense preferences, than Likert scales. This is consistent with the model's tally, though it is far from a test of QV as a planning mechanism.

**Verdict.** T7 is *reproduced* and *weakly supported*.

## 8 The integrated economy (T11–T14)

Sections 4–7 tested each mechanism on its own. The essays' strongest claims, however, are about interaction. Unemployment weakens labour, falling wages push voters into the loss domain, a radical government represses unions, and patronage inflates aspirations. Planning is meant to cut every one of these links.

This section runs all the mechanisms together, in three regimes. The results are checked by:

- `me-regimes.pal` (13 assertions);
- the self-rewriting `me-economy.pal`;
- `me-loops.pal` (5);
- `me-dialectics.pal` (13);
- `me-classical.pal` (the accumulation identity);
- `me-extremes.pal` (§X6–X7).

### 8.1 One period as an equation chain

A period is a chain of equations over a record that holds the state and every variable computed so far. Each equation is a rule `(pe-eq NAME V P)`, and regimes differ by which rule's guard holds. The bridge to the games of §6 is one equation:

```
rule eq-B : (pe-eq B ?v ?p) => (pe-beta (pe-cs (@ ?v mode)) ?gp) where ?gp <- (pe-gpar ?v (put@ ?p u 0))
```

In each period, labour's bargaining power is *the equilibrium of the class-struggle game* at that period's unemployment rate. The chain then computes, in order:

- employment E = min(N, K/κ), with capital per job κ rising 1% a period;
- the wage share (§6.1), profit and the profit rate;
- investment, or a capital strike when profitability falls below r\_min or the game's equilibrium is flight;
- inflation and the living standard;
- the radical vote, from the prospect-theory choice of §7.1, against a reference point raised by the right network;
- the network's share, from the patronage dynamics of §7.2;
- viability Φ = min(economic margin, 2(1/2 − radical vote)).

The three regimes differ by equations, not by parameters:

|  | capitalism | Cold War (to t = 30) | accountable planning |
| --- | --- | --- | --- |
| outside option | reserve army | plus insurance at 9/10 of the employed standard | job guarantee, g = 4/5 |
| wages | bargaining | floored to half of productivity growth | public wage; private firms must beat it |
| money | 2% inflation, 10% shock at t = 40–41 | the same, indexed | labour vouchers |
| left network | no jobs | jobs | jobs |
| repression | radical government halves bargaining power | the same | rights entrenched |
| capital | accumulates | accumulates | capped at θ = 60 |

The parameters come from the model's steady-state algebra rather than from fitting. Accumulation balances when s\_c·r = δ + μ, so s\_c = 3/5, δ = 3% and μ = 1% put the profitability threshold at 1/15.

`me-economy.pal` holds all three regimes in its own `main`. Each run fires one transition, advances ten periods, writes the state back into the file and re-checks the invariants on the whole history. After six runs the guard fails and the file is a byte-identical quine. The file *is* the economy's state, and its version history is the economy's history.

### 8.2 Three regimes

Three baseline results follow (Figure 4):

- **Capitalism.** Unemployment rises in every period, from 0.100 to 0.299, and the wage share falls in every period.
- **The Cold War.** The radical vote is 0 while the Cold War lasts and equals the unemployment rate afterwards, when the unemployed lose their insurance.
- **Planning.** Unemployment and the radical vote are 0, living standards rise, Φ > 0 throughout, and the plan balances exactly in every period.

Under stress, the regimes separate further (right panel; §8.4). Capitalism elects a radical government that holds office for 58 of 60 periods. The Cold War does the same from the period after it ends, and planning never does.

[Chart: see the published version of this paper; its data are reproduced by the program named in the caption below.]

*Figure 4. Unemployment at baseline and the radical vote under stress, three regimes (`lib/polecon.pal`; every period).*

**The labour share.** The BLS (2026) reports the US nonfarm labour share at 52.8% in Q2 2026, the lowest on record, down from a peak of 66.2% in Q4 1960. That is a relative fall of 20.2%. The integrated capitalism's wage share falls by 19.9% over its 60 periods, from 0.864 to 0.692.

The levels differ, because measured labour share includes employer costs and treats depreciation differently from the model's value-added share. The match is in the proportional decline, which the model attributes to mechanization against a weakening bargaining position.

**The Cold War.** Obinger and Schmitt (2011) find that competition with the Soviet bloc had a positive, significant effect on Western welfare-state expansion, strongest in the 1970s. The model's Cold War regime prevents the radical vote while it lasts and loses that protection the period it ends. This is consistent with the rise in inequality since the 1980s that the BLS and Ludwig–Yakovenko series record, though the model cannot separate the Cold War's end from other causes.

**Verdict.** T12 is *reproduced* and *supported*.

### 8.3 Unemployment and mechanization

Why does capitalism's unemployment rise in every period? The answer is the same identity that governs the long-run profit rate of §4.3. Without crisis and below full employment, capital evolves as K′ = (1 − δ)K + s\_cΠ, and employment is E = K/κ with κ growing at rate μ. Hence, in every period,

```latex
s_c\, r_t \;=\; \frac{E_{t+1}}{E_t}\,(1+\mu) \;-\; (1-\delta).
```

This is the discrete form of R\* = (n + g + δ)/λ, with *n* read as the growth of employment, *g* as μ and λ as s\_c. The largest gap between the two sides over 60 periods is 1.33 × 10⁻⁷, from rounding the state to 10⁻⁶.

Employment is constant only if μ = s\_c·r − δ. Running the integrated capitalism at five rates of mechanization shows where that boundary lies:

| μ | u₀ | u₅₉ | r₅₉ | w₅₉ | μ that holds E constant at r₅₉ |
| --- | --- | --- | --- | --- | --- |
| 0 | 0.100 | 0.110 | 0.0500 | 0.850 | 0 |
| 0.005 | 0.100 | 0.179 | 0.0560 | 0.775 | 0.0036 |
| 0.010 | 0.100 | 0.299 | 0.0571 | 0.692 | 0.0042 |
| 0.015 | 0.100 | 0.461 | 0.0517 | 0.627 | 0.0010 |
| 0.020 | 0.100 | 0.596 | 0.0501 | 0.517 | 0.0001 |

Three results follow:

- **Without mechanization**, the profit rate converges to δ/s\_c = 0.05 and unemployment settles near 11%.
- **With mechanization**, the profit rate never exceeds about 0.057. The largest sustainable μ is therefore about 0.4% a period, and any faster rate makes the reserve army grow without limit.
- **The relation is not monotone.** Faster mechanization raises the profit rate at first, by weakening labour, and then lowers it, as fewer workers produce less profit. Marx's law and its counteracting tendency appear in a single table.

Together with the switch wage of §4.3, this closes a loop the essays describe in words. A rising wage induces mechanization, mechanization swells the reserve army, and the reserve army lowers the wage. The same counter-tendency is the model's reading of the profitability recovery of 1982–2007 (§4.3).

**The data.** Here the model fails clearly. US unemployment (FRED, 1948–2026) has no secular trend; it was 4.2% in September 2026. Barbosa-Filho and Taylor (2006) find Goodwin cycles in US data since 1929, together with a long-term profit squeeze.

The model contains the Goodwin loop (§8.5), but in its baseline the loop is overwhelmed, because mechanization of 1% a period outruns accumulation. Real economies with no unemployment trend must sit near the boundary μ ≈ s\_c·r − δ. Channels the model omits hold them there: demand management, the expansion of services and falling hours. Section 9.6 adds two candidates, credit and induced mechanization.

### 8.4 Stress, lock-in and the tipping point (T11, T13, T14)

In a stress scenario, loss sensitivity is raised to 30 and aspiration messaging to 2/5. Capitalism then elects a radical government in period 2.

The radical government is not punished for failing to deliver. Repression halves bargaining power, the wage share drops and the profit rate jumps from 0.045 to 0.086. Unemployment at first *falls*, from 0.106 to 0.079, and living standards *rise*, from 0.85 to 2.10 by period 45, yet the radical vote stays at 1.

The lock-in runs through the reference point. With the right network at 85–89% of membership from period 6 to period 45, every stratum measures itself against a standard 34–36% above its own, and it stays in the loss domain whatever it gains. This is the job-creation essay's "downward spiral" in exact form.

**How robust is this?** The scale that converts living standards into prospect-theory units is not fixed by any of the documents. The program therefore runs a grid of 27 settings, varying loss sensitivity, the inflation shock and aspiration messaging:

- **Planning** never has a radical vote after period 1.
- **The Cold War** never does worse than capitalism.
- **Capitalism** elects a radical government in 15 of the 27 settings.

**Where the spiral starts.** Figure 5 varies aspiration messaging, with loss sensitivity held at 30 and the inflation shock at 10%:

- **Below 0.20**, there is no radical government.
- **From 0.20 to 0.26**, the shock produces a two-period episode.
- **Between 0.26 and 0.27**, a radical government elected by the shock outlasts it, for 10 periods.
- **From 0.28 on**, the first radical period moves earlier, to 29, then 11, then 7. By 0.40 the radical government is elected in period 2 and holds 58 of 60 periods.

[Chart: see the published version of this paper; its data are reproduced by the program named in the caption below.]

*Figure 5. Periods of radical government against aspiration messaging (`me-extremes.pal` §X7).*

The tipping point is sharp because the lock-in is self-reinforcing. A radical government represses, profits rise, the right network grows on profits, and aspirations rise with the network's share. The "downward spiral" is a spiral with a threshold. Below it the same shock produces only a protest vote that reverses, which is the pattern Funke et al. (2016) find after ordinary recessions (§7.1).

**Verdict.**

- **T11 and T13** are *reproduced* as dynamics, above a computable threshold.
- **T14** is *reproduced* in all 27 settings. No economy has implemented the proposal, so it cannot be tested against data.

### 8.5 Feedback loops

The mechanisms of §§4–7 combine into a causal-loop diagram of 15 variables and 24 signed edges, held as a term. Enumeration finds **14 elementary loops: 5 reinforcing and 9 balancing**. They include:

- the Goodwin profit squeeze (balancing), the loop the data of §8.3 show;
- accumulation (reinforcing);
- radicalization (reinforcing): wages fall, voters enter the loss domain, a radical government represses;
- patronage (reinforcing): lower wages fund the right network, which inflates aspirations, the loop behind the lock-in of §8.4.

A diagram drawn by hand asserts its edges; this one *checks* them against the equations. The probe for an edge X → Y is an exact finite difference: raise X by Δ while it is computed, freeze every other node, and recompute Y. It runs at ten base states. **23 of 24 edges are confirmed.**

The failure is U → B, which turns positive near full employment. It is the capital-flight equilibrium of §6.2 seen from the integrated model: where capital's best response to organized labour is to leave, more unemployment *raises* labour's equilibrium bargaining power. A hand-drawn diagram would have recorded the edge as negative everywhere.

Under planning, 12 edges vanish:

- the reserve army;
- the wage–profit opposition;
- inflation;
- every channel into the radical vote;
- repression;
- the crisis threshold.

One loop remains, the capitalist remainder's accumulation, and the asset cap of §5.2 bounds it (Figure 6).

[Chart: see the published version of this paper; its data are reproduced by the program named in the caption below.]

*Figure 6. Capitalism's causal-loop diagram; dashed edges vanish under planning (`lib/polecon.pal`, `me-loops.pal` §7.3).*

### 8.6 Structural dialectics on the model

The structural-dialectics essay asks when a transition from one social form to another is warranted. Its predicates translate rule for rule, and its three worked transitions come out as stated.

We evaluate the predicates on the integrated model. Φ is the model's viability, and the candidate is planning, which is admissible while no radical government holds office. Diagnoses per period, for t = 0–59 (s stasis, I instability, P Phase Inversion, n non-viable with the candidate excluded):

```
baseline capitalism       ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
stress Cold War           sssssssssssssssssssssssssssssIPnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
stress capitalism         sPnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
moderate inflation crisis ssssssssssssssssssssssssssssssssssssssssPnssssssssssssssssss
```

Five readings follow:

1. **Stasis.** Baseline capitalism is in stasis throughout: rising unemployment alone warrants no transition.
2. **Instability.** The Cold War is diagnosed as Instability in its last period: its concessions held the regime up.
3. **Foreclosure.** A crisis opens a window of exactly one period, before a radical government makes the alternative inadmissible. This is the contradictions essay's *foreclosure*, computed.
4. **Synthesis.** Whether synthesis holds depends on the reference point the successor inherits.
5. **The sign of d.** The framework assumes that the candidate's contribution *d* is non-negative. The model computes it instead, and it is sometimes negative.

## 9 Finance (T15–T18)

In §§4–8 money appears only as a conserved quantity and as a one-off injection (§5.3). The essays say more about it, in four claims:

- **Credit money.** The mechanical-materialism essay says a bank "does not lend out pre-existing deposits" and that "New money bids up the price of housing and equities without a corresponding increase in the real output of the economy".
- **Capital gains.** The same essay traces the Pareto class to "compounding capital-gains income" and says the class structure is not something that "could be reformed away with the right policies".
- **Debt deflation.** The accountable-planning essay says that "nearly all production is financed by borrowing". Falling prices start a spiral ("Falling prices cause insolvency, insolvency causes distress selling, distress selling causes further price declines"), so "The system requires that the purchasing power of money be deliberately eroded as a condition of its own stability".
- **Debt and desperation.** The same essay treats economic insecurity as "an existential threat in the same register as mortality". The first version of this evaluation added that debt deepens the desperation, and with it the terror-management effects.

|  | proposition | essay (quoted) | tested in |
| --- | --- | --- | --- |
| T15 | Credit creates money and inflates asset prices, not output | mechanical materialism: "New money bids up the price of housing and equities without a corresponding increase in the real output of the economy" | §9.1 |
| T16 | Compounding capital gains produce the Pareto class, which reform cannot remove | mechanical materialism: "The Pareto (superthermal) class corresponds to compounding capital-gains income" | §9.2 |
| T17 | Nominal debt makes deflation a self-reinforcing spiral, so the system needs inflation, which cuts real pay | accountable planning: "The system requires that the purchasing power of money be deliberately eroded as a condition of its own stability" | §9.3–9.4 |
| T18 | Debt deepens economic desperation and the turn to authoritarian options | accountable planning: insecurity is "an existential threat in the same register as mortality" | §9.5 |

Two other omissions also bear on earlier claims. Induced mechanization, which the first version listed as a limitation, bears on the unemployment failure of §8.3 (§9.6). Capital mobility, which the first version held fixed in a single return abroad, bears on the flight threshold of §6.2 (§9.7).

The results are checked by `me-finance.pal` (7 assertions), `me-financialized.pal` (12) and `me-evidence.pal` §EV2 (1). The cross-check adds 18 checks (§11.2).

### 9.1 Credit money and the price of a fixed stock (T15)

**The model.** A loan credits the borrower with a deposit that did not exist before, and a repayment cancels one. Over a ledger of eight loans, payments and repayments, new deposits equal loans outstanding after every event.

Now let buyers with savings S bid for a fixed stock of houses, borrowing at loan-to-value ratio LTV. A buyer can pay at most S + LTV·P, so

```latex
P=\frac{S}{1-\mathrm{LTV}}.
```

Raising LTV from 0 to 0.8 multiplies the price by 5, and raising it to 0.95 multiplies it by 20. No house is built and no output is produced.

Each sale creates new money LTV·P and pays it to the incumbent holder first. With output fixed, the holder's real gain is exactly Q·D/M, the first-recipient transfer of §5.3, and everyone else loses as much. At LTV = 0.95, ten sales a period move 190 of 1,000 units of output to the sellers.

**The data.**
- **Favara and Imbs (2015)** use US bank-branching deregulation (1994–2005) as an exogenous expansion of mortgage credit. It raised house prices. Only where housing supply was elastic did the stock grow instead.
- **Jordà, Schularick and Taylor (2016)** find that across 17 advanced economies mortgages rose from about 30% of bank lending in 1900 to about 60% today. Nearly all of the financial sector's growth since 1913 is household mortgage lending, which "has little to do with the financing of the business sector".

**Verdict.** T15 is *derived*: the price formula and the transfer are accounting identities. It is *supported* by the data.

### 9.2 Capital gains, resets and the Pareto class (T16)

Section 5.2 found that capital income condenses and does not merely produce a Pareto tail. What it lacked are the forces that break fortunes up.

**The model.** The wealth lattice adds those forces in the simplest exact form:
- fortunes sit on levels 2ⁿ;
- each period a fortune doubles with probability p, a capital gain;
- it halves with probability q, a reset: division between two heirs, a bankruptcy or a tax;
- at the floor, n = 0, a fortune rejoins the exponential class and cannot halve.

The stationary law is geometric, π_n = (1 − z)zⁿ with z = p/q, so

```latex
P(W\ge 2^{n})=z^{n}=\bigl(2^{n}\bigr)^{-\alpha},\qquad \alpha=\log_2\frac{q}{p}.
```

Two regimes follow.

- **Resets frequent enough (z < 1/2, α > 1).** Mean wealth is finite and every top share converges. From every fortune at the floor, 31 levels reach the geometric law within 10⁻⁶ in 300 periods.
- **Resets too rare (z ≥ 1/2, α ≤ 1).** Mean wealth diverges, and a vanishing fraction ends with nearly everything. With the lattice capped at level L and z = 3/5, the top 1% hold 42.3%, 90.7%, 99.8% and 100.0% as L rises from 10 to 80. At z = 2/5 their share settles at 32.5%.

Section 5.2 is the case q = 0: no resets, so the wealth condenses. The asset cap is a finite lattice and bounds the share at every z.

The top-1% share moves steeply with α: 9.5% at α = 2, 17.9% at 1.58, 32.5% at 1.32 and 72.6% at 1.07 (Figure 7).

[Chart: see the published version of this paper; its data are reproduced by the program named in the caption below.]

*Figure 7. The top-1% wealth share on the lattice against the tail exponent, with the Federal Reserve's 1989 and 2026 shares read on it (`me-finance.pal` §F2).*

**The data.** Read on the lattice, the Federal Reserve's top-1% wealth shares imply:
- α = 1.460 in 1989, when the share was 22.8%;
- α = 1.322 in 2026, when it was 32.5%.

The 1989 value is close to direct estimates of the US wealth tail. Klass et al. (2006) find 1.49 from the Forbes 400 for 1988–2003, and Vermeulen (2018) finds 1.48–1.55 after correcting for non-response; both are reported by Benhabib and Bisin (2018).

The concentration since then corresponds to a 10.1% rise in the ratio of capital-gain doublings to resets. That rise has moved the tail about a third of the way to the condensation boundary α = 1. The lattice treats all fortunes as one Pareto population, so these numbers are a reading of the data, not a fit.

**Verdict.** The first half of T16 is *derived*: compounding gains set against resets give a Pareto class with exponent log₂(q/p).

The second half is *qualified*. The class's existence is structural, because any p > 0 and q > 0 produce a power law. Its weight is not. The resets are inheritance rules, bankruptcy law and taxes, and between α = 2 and α = 1.07 the top 1%'s share varies almost eightfold. Reform cannot remove the class, but it decides how large the class is. The condensation failure of §5.2 becomes a threshold, z = 1/2, and real economies sit below it.

### 9.3 Debt deflation (T17)

**The model.** Twenty firms each hold one unit of an asset and owe d_j, with debts evenly spaced (spacing Δ) between d_lo and d_hi.
- A shock σ lowers the price to 1 − σ.
- A firm whose debt exceeds the price is insolvent and sells.
- Each distress sale lowers the price by η.

The number of sales is the least fixed point of m ↦ #{j : d_j > 1 − σ − ηm}. The program computes it and checks a closed form on 36 cases:

- if η ≥ Δ, one insolvency brings down every firm;
- if η < Δ, the sales stop at

```latex
m^{*}=\left\lceil\frac{d_{\mathrm{hi}}-1+\sigma}{\Delta-\eta}\right\rceil .
```

The spiral is self-reinforcing exactly when one sale lowers the price by more than the gap to the next debtor. Financialization narrows that gap. With η = 0.025:
- firms whose debts are spread over [0.20, 0.80] (Δ = 0.032) absorb shocks up to 20% without a single sale, and amplify a 25% shock 1.8-fold;
- firms crowded into [0.50, 0.95] (Δ = 0.024) collapse completely after a 10% shock, a sixfold amplification.

**The data.** Fisher (1933) set out the chain from debt liquidation to distress selling, falling prices, falling net worth and bankruptcy, and stated its paradox: "Each dollar of debt still unpaid becomes a bigger dollar", so that "the very effort of individuals to lessen their burden of debts increases it" (p. 344, as quoted by Shiller). The model reproduces the mechanism and its threshold; it is not compared with Fisher's magnitudes.

**Verdict.** The spiral of T17 is *derived*, with a threshold: it is self-reinforcing only when distress sales move the price by more than the spacing of leverage. Section 9.4 tests the second half of T17, the need for inflation, in the integrated economy.

### 9.4 Financialized capitalism (T17, T5)

**The model.** `lib/polecon-fin.pal` adds a fourth regime to §8. It is capitalism with three financial channels, each one equation with one parameter.

1. **Credit-financed accumulation.**
   - Firms invest (μ + δ)K, which holds their workforce as capital per job rises. Banks lend the share lev of the gap that retained profit leaves.
   - Interest at 5% on firm debt is a deduction from profit, and the capital strike of §8.1 now reads the *net* profit rate. A debt crisis is therefore the existing crisis rule, reached through interest: Minsky's moment.
   - Debt is nominal, so inflation erodes it. A crisis writes off the share of the debt that the crash destroys and stops new lending.
2. **Household credit.**
   - The employed borrow half the gap between their aspiration (the reference point of §8.4) and their income net of interest.
   - Their debt is capped at one period's income.
   - In a crisis lending stops, and they repay a fifth of their debt.
3. **Debt and desperation.**
   - Debt service is owed whatever happens, so it is subtracted from the worker's fallback in the wage bargain.
   - The debt-service share of income, DS, joins unemployment in the insecurity that raises the pull of the right network's institutions: the terror-management term 3(1 + U) of §8.1 becomes 3(1 + U + DS).
   - Households' interest is income of capital and funds the right network with profits.

With both credit channels off, the regime reproduces capitalism row for row (asserted).

**The baseline** (lev = 1; Figure 8):

- **Crises.** There are two, at t = 7 and t = 52, and each is followed by one period of radical government. Capitalism at the same parameters has none.
- **Unemployment.** It no longer rises every period. It is flat between the crises, at 0.189–0.190 from t = 15 to t = 51, and jumps at each crisis. After 60 periods it is 0.298, against capitalism's 0.299. Credit changes the shape of the trend, not its size.
- **The profit rate.** Between the crises the wage share stays within 0.009, while the profit rate falls every period, from 0.073 to 0.040. Holding employment with credit holds the rate of exploitation constant, and as capital per job rises the profit rate falls. This is the reading of T5 that §4.3 found under constant exploitation, now produced by the economy instead of assumed. The crisis restores the profit rate.
- **Debt.** Firm debt rises from 6.2% of capital at t = 24 to 19.0% at t = 51 as profits fall. Household debt sits at its ceiling from t = 15 until the inflation shock of t = 40–41 cuts real income.

[Chart: see the published version of this paper; its data are reproduced by the program named in the caption below.]

*Figure 8. Unemployment in four runs, and firm debt relative to capital in the two financialized runs; dots mark crises (`me-financialized.pal` §F5.7, §F5.1).*

**The channels one at a time.**
- Firm credit alone produces crises at t = 5 and 50 and no radical government.
- Household credit alone produces no crisis.
- Both together produce crises at t = 7 and 52, each followed by a radical government.

**The thresholds.**

- **Accommodation.** How far the banks accommodate decides whether there is a crisis at all. For lev ≤ 3/4 there is none within 60 periods, and unemployment ends below capitalism's (0.240 at lev = 3/4). The boundary lies between lev = 0.7617 and 0.7622.
- **Inflation postpones the debt crisis but cannot prevent it.** The first crisis (t = 6–8) comes from the falling profit rate and happens at every inflation rate tested. The second comes later as inflation rises:

| steady inflation | 0 | 2% | 4% | 6% | 8% | 10% |
| --- | --- | --- | --- | --- | --- | --- |
| second crisis | t = 48 | 52 | 54 | 57 | 59 | none in 60 periods |
| real pay cut between settlements, π/(1 + π) | 0 | 2.0% | 3.8% | 5.7% | 7.4% | 9.1% |

- **Deflation does the opposite.** A 10% fall in prices at t = 40–41 raises the employed's living standard in debt-free capitalism, from 1.787 to 2.184. In the financialized economy the same fall:
  - lifts real household debt above its ceiling, to 1.235 of income at t = 42;
  - brings the second crisis forward from t = 52 to t = 49;
  - doubles the periods of radical government, from 2 to 4.

**The data.** US household debt rose to 99.1% of GDP in the first quarter of 2008 and has since fallen to 66.6% (Q1 2026; BIS data via FRED). This is the model's pattern of a ceiling followed by deleveraging, although the model's ceiling is a parameter, not an estimate.

**Verdict.** T17 is *reproduced* and *qualified*. The financialized economy needs inflation to postpone its debt crises, and the inflation that does so is a real pay cut, as the essay says. Inflation does not remove the crisis. It moves the second one later by about one period per percentage point.

T5 is *reproduced* under financialization: credit supplies the wage rule that §4.3 found the falling profit rate needs.

### 9.5 Debt, desperation and the radical vote (T18)

In §8.4 a shock became a radical government only under stress. In the financialized economy every crisis does so, even at baseline. The mechanism is the credit crunch.

**The crunch.** At a crisis, lending stops and households start repaying, so the employed's standard falls from a level that credit had inflated. That inflated standard also set their reference point. The employed vote radical iff their standard falls below 1 + D\*/20 = 0.730 of their aspiration, where D\* = −5.399 is the threshold of §7.1.

| run | crisis | standard before | standard at crisis | change | standard / aspiration | radical |
| --- | --- | --- | --- | --- | --- | --- |
| financialized | t = 7 | 1.095 | 0.851 | −22.3% | 0.670 | yes |
| financialized | t = 52 | 2.586 | 2.026 | −21.7% | 0.664 | yes |
| firm credit only | t = 5 | 0.935 | 0.959 | +2.5% | 0.889 | no |
| firm credit only | t = 50 | 2.491 | 2.553 | +2.5% | 0.871 | no |

Without household debt, the employed's standard *rises* at the same crisis. In both runs the program asserts that each crisis is radical exactly when the ratio falls below 0.730. A crisis becomes a radical government through the credit crunch, not through output: the crash destroys 10% of capital in both runs.

**How much households borrow.** At a borrowing propensity of 1/8 neither crisis radicalizes. At 1/4 and 3/8 only the second does, after debt has reached its ceiling. From 1/2 both do.

**Robustness.** Over the 27 stress settings of §8.4:
- capitalism elects a radical government in 15 settings, and the financialized economy in all 27;
- radical periods total 386 under capitalism and 509 under finance;
- in five settings finance *shortens* radical rule. All five are settings in which capitalism is locked in for 56 periods or more, and there credit lets households cushion the loss.

**The terror-management channel.** Three new edges hold with their stated sign at all ten base states probed:
- debt service → the right network (DS → SR);
- debt → debt service;
- debt → the wage, which is negative: the indebted worker bargains from a worse fallback.

The first is weak: a rise of 0.05 in DS raises the network's share by only 0.001–0.004. Through these edges financialization adds two reinforcing loops of four links:
- aspiration → household debt → debt service → right network → aspiration;
- wage → right network → aspiration → debt → wage.

Firm debt forms a balancing loop, capital → debt → profit rate → investment → capital: debt brings the crisis that writes it off. The financialized diagram has 36 edges and 37 elementary loops, of which 18 run through a financial variable (7 reinforcing, 11 balancing).

Two edges fail their checks.
- **U → B** fails as it did in §8.5.
- **Inflation → household debt** was expected to be negative, because inflation erodes debt. It is positive at the first base state, where households owe little: inflation cuts real pay, and households borrow to make it up. Which effect wins depends on the level of debt.

**The data.**
- **Funke, Schularick and Trebesch (2016).** Far-right vote shares rise by about 30% after financial crises, but not after normal recessions. This is the pattern the crunch reproduces.
- **Mian, Sufi and Trebbi (2014).** Countries become more polarized and fractionalized after financial crises.
- **Mian, Rao and Sufi (2013).** In the 2006–09 housing collapse, consumption responded most to wealth losses in ZIP codes with poorer and more levered households, whose marginal propensity to consume out of housing wealth was highest.
- **Jordà, Schularick and Taylor (2013).** Financial-crisis recessions cost more output. Three years after the peak, real GDP per capita is 2.5% below it after a financial crisis and 2.0% above it after a normal recession. The model does not reproduce this pattern: its crises destroy the same capital whether or not households are in debt.

**Verdict.** T18 is *reproduced*, and the data *support* its political pattern. In the model, desperation works mostly through the fall from a credit-inflated reference point, and only weakly through the level of debt service. This sharpens the finding of §7.1: financial crises cross the curvature threshold because credit has raised the reference point that the crunch then removes.

### 9.6 Two remedies for the unemployment trend

Section 8.3 found the model's clearest empirical failure: unemployment rises without limit, while US unemployment has no trend. Two omitted mechanisms could hold it down. Credit is one (§9.4).

The other is the loop that §4.3 closed only analytically: firms mechanize only when labour is dear. Under induced mechanization, capital per job rises at

```latex
\mu_t=\mu\,\frac{\max(0,\;w_t-w_s)}{w_m-w_s}.
```

The rate is the full 1% at the initial wage share w_m = 0.864. It is zero at w_s = 0.765, a wage share lower by the switch ratio 1.129 of §4.3.

| run | u₀ | u₁₅ | u₃₀ | u₄₅ | u₅₉ | wage share, 60 periods | r₅₉ | crises |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| capitalism | 0.100 | 0.168 | 0.205 | 0.249 | 0.299 | −19.9% | 0.0571 | none |
| capitalism, induced | 0.100 | 0.141 | 0.149 | 0.156 | 0.161 | −8.4% | 0.0538 | none |
| financialized | 0.100 | 0.190 | 0.189 | 0.189 | 0.298 | −21.7% | 0.0494 | t = 7, 52 |
| financialized, induced | 0.100 | 0.149 | 0.140 | 0.140 | 0.140 | −7.2% | 0.0477 | t = 7 |

**Induced mechanization removes the trend.** After t = 30 unemployment rises by less than 0.001 a period. With credit as well, it is constant at 0.140 from t = 30, after a single crisis. The switch share w_s sets the level: unemployment ends at 0.187 when w_s = 0.70 and at 0.117 when w_s = 0.84.

**The remedy costs the model its best quantitative match.** The labour share now falls only 8.4%, or 7.2% with credit, against 20.2% in the data. Across the switch shares, the less unemployment rises, the less the labour share falls: −11.2% at u₅₉ = 0.187, down to −2.7% at 0.117.

The reason is that in this model the wage share is a function of unemployment, and debt (§9.4) shifts it by only a point or two. The match of §8.2, 19.9% against 20.2%, is therefore the same fact as the unemployment failure. The US combination of a labour share down 20% and no unemployment trend needs a fall in labour's bargaining power at given unemployment, and neither remedy supplies one.

### 9.7 Capital mobility and Kalecki's threshold (T8)

Capital mobility is one candidate for that fall. In §6.2 the return abroad r_ext was fixed at 10%. Flight is an equilibrium of the class game when the reserve-army wage reaches 1 − ρ − r_ext. For returns from 5% to 40% that is

```latex
u\le u_f=\frac{\beta_l\,(\rho+r_{\mathrm{ext}})}{(1-\beta_l)(1-\rho-r_{\mathrm{ext}}-s)}.
```

The game and the closed form agree at all seven returns tested. (At a zero return the formula fails: flight is then an equilibrium only at full employment.)

| return abroad | 5% | 10% | 15% | 20% | 25% | 30% | 40% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flight up to unemployment u_f | 5.0% | 8.3% | 12.5% | 17.9% | 25.0% | 35.0% | 75.0% |

From r_ext = 43%, flight is an equilibrium at every unemployment rate. Financial openness therefore raises the unemployment rate below which capital leaves. It also lowers, one for one, the highest wage share consistent with domestic investment: from 0.85 to 0.80 as r_ext rises from 10% to 15%.

**The data.** Furceri, Loungani and Ostry (2019) find that episodes of capital-account liberalization lower the labour share by about 4.5% in the medium term, most in industries that depend on external finance.

The model's channel is cruder. Where the game has no pure equilibrium, the return abroad does not enter the mixed equilibrium, so openness moves the threshold but not the bargained wage. On its own it cannot produce the decoupling of §9.6.

Under planning, flight triggers expropriation, so capital mobility leaves the job guarantee of T8 unaffected. Under capitalism, Kalecki's political limit to full employment moves with financial openness.

### 9.8 Verdicts

- **T15** is *derived* and *supported*.
- **T16** is *derived* for the Pareto class, with exponent log₂(q/p). Its claim that reform cannot remove the class is *qualified*: the class persists, but its weight is set by resets that are matters of policy. The data *support* it, since the lattice reads the 1989 share as α = 1.46 against direct estimates of 1.48–1.55.
- **T17** is *derived* as a spiral above a threshold (η ≥ Δ). The need for inflation is *reproduced* as a postponement of the debt crisis. Fisher's account supports it.
- **T18** is *reproduced*, through the crunch, and *supported* by the political and consumption data. The output pattern of Jordà, Schularick and Taylor is not reproduced.
- **Earlier verdicts revised.**
  - T3's upper class: condensation becomes a threshold.
  - T5: reproduced under financialization.
  - §8.3's unemployment failure: either remedy removes it only by exposing that the labour-share match rests on it.
  - T8: Kalecki's threshold moves with the return abroad.

## 10 Assessment: what the model validates

### 10.1 The scorecard

The table collects the verdicts of §§4–8. Each proposition appears with what the model derives, what the data show, and the limit or condition the model finds.

|  | proposition | model | data | limit or condition | § |
| --- | --- | --- | --- | --- | --- |
| T1 | value conserved in exchange | **derived** | not directly testable | holds for any transitive exchange table, fails for any intransitive one | 4.1 |
| T2 | values predict prices | **derived**, deviation growing in r | **supported** (r ≈ 0.94–0.99) | deviations 3–11× too small in a 3–4-sector model | 4.2 |
| T3 | exponential lower class, Pareto upper class | lower class **derived**; upper class **qualified**, and **derived** once fortunes can be broken up (§9.2) | lower class **supported** (Gini 0.5); upper class matched by the lattice reading | condensation without resets (98% to one owner), a Pareto tail with them (z < 1/2) | 5.1–5.2, 9.2 |
| T4 | money creation redistributes | **derived** (zero-sum; first recipients gain Q·D/M) | **supported** (BIS) | a proportional injection spent after prices adjust redistributes nothing | 5.3 |
| T5 | falling profit rate | **qualified**: needs a wage rule or slowing demography; **reproduced** under financialization (§9.4) | **supported** as a long-run trend (Maito, Basu) | floor −(1 − w)(g + δ) below n\* = −0.0248, with slow convergence there | 4.3, 8.3 |
| T6 | planning converges fast | **derived** (18 passes) | consistent with the essay's worked example | speed set by the spectral radius of A | 4.1 |
| T7 | QV redirects production toward need | **reproduced** | **weakly supported** (survey QV) | none found | 7.5 |
| T8 | job guarantee breaks employer power | **reproduced** above u\_c = 1/11 | **supported** in slack markets (NREGA) | inert below 9.1% unemployment; capital flight up to u_f, which rises with the return abroad | 6.1–6.3, 9.7 |
| T9 | divided government cannot conspire | **derived**: K̄ = ⌈ 1/P ⌉ | **plausible** (leniency programmes); selectorate evidence contested | a single party sustains collusion at every δ | 7.3–7.4 |
| T10 | vouchers and caps prevent accumulation | **derived** (non-interference; bounded owners' share) | no test available | the cap bounds the last reinforcing loop | 5.2–5.3, 8.5 |
| T11 | losses and inflation drive radicalism | **qualified**: requires D < −5.4, a curvature effect | **supported and qualified** (crises, not ordinary recessions) | threshold 11/2 − K in deep losses; tipping point at aspiration 0.26–0.27 | 7.1, 8.4 |
| T12 | the Cold War raised living standards | **reproduced** | **supported** (Obinger and Schmitt) | the protection ends the period the Cold War ends | 8.2 |
| T13 | patronage spiral | **reproduced** | premise **supported** (Thachil) | a spiral only above a threshold; below it the protest vote reverses | 7.2, 8.4 |
| T14 | planning defuses authoritarianism | **reproduced** in all 27 stress settings | no test available | an inherited reference point can make the successor's first period non-viable | 8.4–8.6 |
| T15 | credit inflates asset prices, not output | **derived** (P = S/(1 − LTV); sellers gain Q·D/M) | **supported** (Favara and Imbs; mortgages 30% → 60% of bank lending) | none: accounting identities | 9.1 |
| T16 | capital gains make the Pareto class, which reform cannot remove | **derived** (α = log₂(q/p)); "cannot be reformed away" **qualified** | **supported** (lattice reading 1.46 in 1989 against direct estimates 1.48–1.55) | condensation iff 2p ≥ q; the exponent is set by resets, which are policy | 9.2 |
| T17 | debt deflation; the system needs inflation | spiral **derived** with a threshold; the need for inflation **reproduced** as postponement | **supported** (Fisher 1933) | complete spiral iff η ≥ Δ; second crisis at t = 48 → 59 for π = 0 → 8% | 9.3–9.4 |
| T18 | debt deepens desperation and radicalism | **reproduced** (2 of 2 crises radical with household credit, 0 of 2 without; 27 of 27 stress settings) | **supported** (Funke et al.; Mian, Sufi and Trebbi; Mian, Rao and Sufi) | standard/aspiration < 0.730 at the crunch; output depth not reproduced | 9.5 |

### 10.2 The data at a glance

`examples/me-evidence.pal` prints the quantitative comparisons of §§4–8 side by side:

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

§EV2 FINANCE: THE MODEL AGAINST EMPIRICAL DATA
  quantity                                   data        model
  Pareto exponent of US wealth               1.49        1.460  (the lattice reading of the 1989 top-1% share)
    ... top-1% share 22.8% -> 32.5% (1989 -> 2026): alpha 1.460 -> 1.322; condensation at 1
  far-right vote after financial crises      +30.0%      radical government after 2 of 2 crunches with household debt, 0 of 2 without
    ... the employed standard in the crunch: -22.3% / -21.7% with household debt; +2.5% without
  labour share, relative change              -20.2%      financialized -21.7%;  induced mechanization -8.4% (u_59 0.161)
  capital-account opening, labour share      -4.5%       wage-share ceiling 1 - rho - r_ext: -5.9%  (r_ext 10% -> 15%)
```

### 10.3 Five patterns

1. **The structural core holds.** Conservation, the real opposition of wages and profits, the reserve army's effect on wages and the exponential lower class are derived or reproduced exactly. They match the data in sign. For the wage curve and the labour share's decline they also match in magnitude.
2. **Every "always" becomes a threshold.** The essays state several claims without conditions: the more radical side *always* wins, the job guarantee breaks employer power, the profit rate falls. The model turns each into a statement with a computable boundary: D < −5.4, u > 1/11, and μ > s\_c·r − δ or n < n\*. Where data exist, they confirm the conditions: radicalization follows financial crises but not ordinary recessions, and job-guarantee wage effects come from slack labour markets.
3. **The model's failures are magnitudes, not signs.** Three magnitudes were wrong in the first version: price–value deviations are too small, capital concentration is too extreme, and unemployment rises without limit. In each case the model's direction agrees with the data, and each failure comes from a missing mechanism. Section 9 supplies two of the missing mechanisms.
   - Resets turn condensation into a Pareto tail; read from the 1989 top-1% share, its exponent (1.46) is close to the measured 1.48–1.55.
   - Induced mechanization stops the unemployment trend, but it reveals that the labour-share match rested on that trend.
4. **Finance runs the political mechanisms harder.** Every financial crisis in the model becomes a radical government, and does so through the household credit crunch, which removes the reference point that credit had raised. This is the pattern Funke et al. find: radicalization after financial crises, not after ordinary recessions.
5. **Some claims are beyond the data.** The model can show that vouchers, the asset cap and planning remove mechanisms. No economy has implemented the proposal, so whether it would work as modelled cannot be tested.

## 11 Verification and reproduction

Every result is checked twice:

1. by the assertions of the program that computes it;
2. by an independent second implementation that regenerates the text of every displayed table.

### 11.1 Reproduction protocol

The requirements are a Rust toolchain (`cargo`) and Python 3 (standard library only). From the root of the repository:

```
cargo build --release
cargo test --release                    # 44 unit tests, among them exact arithmetic, memo, trace
./verify-materialist.sh                 # 15 checks, about 6 minutes; exit status 0 iff all pass

# individual programs (--dry-run: never write files)
./target/release/palimpsest examples/me-tour.pal --trace 22
./target/release/palimpsest examples/me-value.pal --dry-run          #  7 s, 17 assertions
./target/release/palimpsest examples/me-classical.pal --dry-run      #  7 s,  8 assertions
./target/release/palimpsest examples/me-distribution.pal --dry-run   # 76 s, 18 assertions
./target/release/palimpsest examples/me-games.pal --dry-run          #  8 s, 20 assertions
./target/release/palimpsest examples/me-selectorate.pal --dry-run    #  9 s,  7 assertions
./target/release/palimpsest examples/me-regimes.pal --dry-run        # 84 s, 13 assertions
./target/release/palimpsest examples/me-loops.pal --dry-run          # 16 s,  5 assertions
./target/release/palimpsest examples/me-dialectics.pal --dry-run     #  5 s, 13 assertions
./target/release/palimpsest examples/me-extremes.pal --dry-run       # 11 s,  6 assertions
./target/release/palimpsest examples/me-evidence.pal --dry-run       #  2 s,  4 assertions
./target/release/palimpsest examples/me-finance.pal --dry-run        # 19 s,  7 assertions
./target/release/palimpsest examples/me-financialized.pal --dry-run  # 56 s, 12 assertions

# the self-rewriting economy: run on a copy; six runs rewrite it, the seventh is a fixed point
cp examples/me-economy.pal /tmp/e.pal && sed -i 's#import "../lib/#import "#' /tmp/e.pal
for i in 1 2 3 4 5 6 7; do PALIMPSEST_LIB=$PWD/lib ./target/release/palimpsest /tmp/e.pal | grep -E 'WROTE|FIXED POINT'; done

python3 crosscheck/materialist_crosscheck.py     # 80 independent checks
```

The times are wall-clock times on a two-core cloud container; each program runs on one core.

- **Pass and fail.** A program that prints `asserts : n passed, 0 failed` has verified all of its theorems. Any failed assertion makes it exit with a non-zero status.
- **Determinism.** All randomness comes from the deterministic `rng` hash, so every output, including the agent-based samples, is identical on every machine.

### 11.2 The independent cross-check

`crosscheck/materialist_crosscheck.py` is a second implementation written from the specification, using exact `Fraction` arithmetic. It reproduces:

- the interpreter's rounding rules, its `rng` hash and its floor square root;
- every model, including the bisection brackets, the financialized chain with its debts and hooks, the wealth lattice and the debt-deflation cascade, the class game's equilibria, the agent models, the equation chain with its probe hooks, the dialectics predicates, the selectorate equilibrium, every threshold and every model figure of §§4–8.

It formats each table exactly as Palimpsest does and requires the two texts to agree character for character.

| part | checks | covers |
| --- | --- | --- |
| I value | 9 | §4.1–4.3 |
| II distribution | 7 | §5 |
| III games | 9 | §6, §7.1–7.3, §7.5 |
| IV economy and loops | 10 | §8.1–8.5, including the 180 history rows the self-rewriting economy writes into its source, the 27-setting grid and all 240 edge probes |
| V dialectics | 4 | §8.6 |
| VI(a) classical | 5 | §4.1, §4.3, §8.3 (long run, input–output table, accumulation identity) |
| VI(b) selectorate | 5 | §7.4 |
| VI(c) extremes | 11 | the thresholds of §4.2–4.3, §6.1–6.2, §7.1, §7.3–7.4, §8.3–8.4 |
| VI(d) evidence | 2 | §6.3, §10.2 |
| VIII(a) finance | 5 | §9.1–9.3, §9.7 (credit ledger, asset price, lattice, cascade, capital mobility) |
| VIII(b) financialized | 12 | §9.4–9.6, including the nesting check (both credit channels off = capitalism, row for row), the 54-run stress grid and all 360 edge probes |
| VIII(c) evidence | 1 | §10.2 (§EV2) |

All 80 checks agree. The other 76 example programs of the Palimpsest distribution and its ten other verification suites also pass with the interpreter described here.

### 11.3 What the verification does and does not establish

The two implementations share a specification, not code. They therefore catch implementation errors, such as an off-by-one period, a wrong rounding, a mis-signed probe or a mis-copied payoff. They cannot catch a specification error.

The empirical comparisons of §§4–9 are the check on the specification. Its constants are cited in the program so that a reader can trace each one to its source.

## 12 Limitations

### 12.1 The model

- **It formalizes; it does not estimate.** Its parameters come from its own steady-state algebra or from the essays, and the empirical comparisons in §§4–8 are not fits. A parameter-free match, such as the wage-curve elasticity or the labour share's relative decline, is evidence for a mechanism. It is not evidence that the model is calibrated.
- **The outside-option formula lets the wage share approach 1 at full employment.** This drives three results: the capital-flight equilibrium below u = 1/12 (§6.2), the job guarantee's inertness below u\_c = 1/11 (§6.3), and the zero elasticity at u = 0. A formula with a productivity ceiling or an efficiency-wage floor would move all three thresholds.
- **Mechanization is exogenous in the three regimes of §8.** Capital per job rises at a fixed rate μ. Section 9.6 lets firms choose it, as an option. The trend then stops, at the cost of the labour-share match.
- **There is no demand side.** Credit (§9.4) finances investment and consumption, but output is still what the employed produce. Nothing models a realization crisis or fiscal policy.
- **The financial parameters are round values, not steady-state algebra.** They are the interest rate (5%), the banks' accommodation (lev = 1), the households' borrowing propensity (1/2), the debt ceiling (one period's income) and the crunch repayment (1/5). Section 9 reports a grid for each one that decides an outcome, together with the threshold where it changes.
- **The financial model is partial.**
  - Households default on nothing, and the unemployed carry no debt.
  - The interest rate responds to nothing.
  - Asset prices (§9.1) and the wealth lattice (§9.2) are not inside the integrated economy.
  - Crises destroy the same capital with or without debt, so the model cannot reproduce the deeper output losses of financial recessions.
- **The value function's curvature is a modelling choice.** The piecewise-quadratic form keeps everything exact, but it is valid only for losses smaller than K, and §7.1 shows that K decides the radical threshold. Results that depend on the threshold, notably the lock-in point of §8.4, inherit this dependence.
- **The wealth lattice is one population.** Reading the top-1% shares as tail exponents treats every fortune as part of one Pareto population. These numbers are a reading of the data, not an estimate.
- **The agent models are small.** They have 20 to 100 agents and are seeded. The exact results of §5.1 are what they approximate.
- **Some inputs are reconstructions.** These are the planning table, two prior and likelihood pairs in the dialectics examples, the intermediate demography values, and the encoding of *Classical Econophysics* Table 10.1.

### 12.2 The empirical comparison

- **The data are mostly from the United States.** The labour share, wage curve, distribution and unemployment series are US data, and the profit-rate and political evidence is drawn mainly from rich democracies. The essays' claims are general.
- **The measures do not map one to one.** Measured labour share includes employer contributions and treats depreciation and self-employment differently from the model's value-added share. Measured MAWD uses market prices from 40–100-industry tables, not prices of production from three sectors. Tax-unit income is not money holdings.
- **Correspondence is not identification.** That radical voting follows financial crises, as the model's threshold predicts, does not show that prospect-theoretic voters are the mechanism. Several of the cited studies are observational.
- **Some sources were consulted at second hand.** Shaikh (1998) and Zachariah (2006) are cited as reported in *Classical Econophysics*. Cockshott and Cottrell (1997) and Işıkara and Mokre (2022) are cited as reported in the essays and in the journal abstract.
- **Accountable planning cannot be tested.** No economy has run it, so §§8.1–8.6 describe the consequences of its rules, not evidence that it works. The Cold War regime has an empirical counterpart; the planning regime does not.

### 12.3 Not modelled

The model omits:

- international trade and unequal exchange (capital mobility enters only through the return abroad, §9.7);
- the party-state beyond its collusion and selectorate readings;
- Wright's social-architecture model of firm formation (*Classical Econophysics*, ch. 13);
- the psychoanalytic and Buddhist parts of the contradictions essay;
- the gender and racial divisions of the working class.

## 13 Conclusion

The essays argue from conservation through class relations to politics, and the model follows the same chain. Its first links hold as theorems:

- value is conserved in exchange, and conservation fixes the exponential distribution of money;
- wages and profits stand in exact opposition;
- the reserve army disciplines the wage, with the elasticity the data show.

The later links hold as well, but each holds only past a threshold, and the model computes every threshold exactly:

- the profit rate falls given a wage rule or slowing demography, toward a floor the closed form omits;
- the job guarantee bites above 1/11 unemployment;
- radical politics needs a loss deep enough to cross a curvature-set threshold;
- patronage locks in only above a sharp level of aspiration messaging.

Where the data speak, they generally confirm both the mechanisms and their thresholds. Radicalization follows financial crises and not ordinary recessions, and the job guarantee's wage effect appears in slack markets.

The model's failures are informative in the same way. Prices deviate from values more than three sectors allow. Wealth concentrates less than condensation predicts. Unemployment stays trendless where the model's grows. Each failure names a mechanism the essays leave implicit and a real economy supplies.

Finance follows the same pattern. Credit inflates asset prices without adding output. Capital gains make a Pareto class whose weight depends on how often fortunes are broken up. Distress selling is a spiral only above a threshold. Inflation postpones debt crises but cannot prevent the first one. And the essays' link from insecurity to authoritarianism runs most strongly through the credit crunch, which turns a financial crisis into a radical government by removing a reference point that credit had raised. The one remedy that fixes the unemployment trend also shows that the labour share's decline needs a cause the model does not contain.

The method made these results possible. Because every causal claim is a rewrite rule, every edge of the causal diagram can be checked against the equations that also run the simulation. Because the arithmetic is exact, observations near a tie become theorems, and thresholds become closed forms. Planning removes the mechanisms the essays blame, within the model. Whether it would do so in an economy is a question no data can yet answer.

## References

**Reference works**

- Bueno de Mesquita, B., Smith, A., Siverson, R. M., and Morrow, J. D. (2003). *The Logic of Political Survival*. Cambridge, MA: MIT Press. Ch. 3 and its appendix.
- Cockshott, W. P. (2019). *How the World Works: The Story of Human Labor from Prehistory to the Modern Day*. New York: Monthly Review Press. §5.4.8, §5.9.
- Cockshott, W. P., Cottrell, A. F., Michaelson, G. J., Wright, I. P., and Yakovenko, V. M. (2009). *Classical Econophysics*. London: Routledge. Ch. 8, §10.4 (Tables 10.1–10.3), ch. 13, §14.3.

**Essays** (cited by file name): `mechanical_materialism.html`, `accountable_planning.html`, `objections_and_responses.html`, `philosophies_of_contradiction.html`, `structural_dialectics.html`, `fascism_outgrowth_capitalism.html`, `job_creation.html`.

**Theory**

- Bouchaud, J.-P., and Mézard, M. (2000). Wealth condensation in a simple model of economy. *Physica A*, 282, 536–545.
- Colletti, L. (1975). Marxism and the dialectic. *New Left Review*, I/93, 3–29.
- Djilas, M. (1957). *The New Class*. New York: Praeger.
- Drăgulescu, A., and Yakovenko, V. M. (2000). Statistical mechanics of money. *European Physical Journal B*, 17, 723–729.
- Fisher, I. (1933). The debt-deflation theory of great depressions. *Econometrica*, 1(4), 337–357.
- Goodwin, R. M. (1967). A growth cycle. In C. H. Feinstein (ed.), *Socialism, Capitalism and Economic Growth*, 54–58. Cambridge University Press.
- Kahneman, D., and Tversky, A. (1979). Prospect theory. *Econometrica*, 47(2), 263–291.
- Kalecki, M. (1943). Political aspects of full employment. *Political Quarterly*, 14(4), 322–330.
- Lalley, S. P., and Weyl, E. G. (2018). Quadratic voting. *AEA Papers and Proceedings*, 108, 33–37.
- Minsky, H. P. (1986). *Stabilizing an Unstable Economy*. New Haven: Yale University Press.
- Morishima, M. (1973). *Marx's Economics*. Cambridge University Press.
- Nash, J. F. (1950). The bargaining problem. *Econometrica*, 18(2), 155–162.
- Okishio, N. (1961). Technical changes and the rate of profit. *Kobe University Economic Review*, 7, 85–99.
- Roemer, J. E. (1982). *A General Theory of Exploitation and Class*. Harvard University Press.

**Empirical sources**

- Barbosa-Filho, N. H., and Taylor, L. (2006). Distributive and demand cycles in the US economy: A structuralist Goodwin model. *Metroeconomica*, 57(3), 389–411.
- Basu, D. (2022). World profit rates, 1960–2019. UMass Amherst Economics Working Paper 318.
- Benhabib, J., and Bisin, A. (2018). Skewed wealth distributions: Theory and empirics. *Journal of Economic Literature*, 56(4), 1261–1291.
- Blanchflower, D. G., and Oswald, A. J. (2005). The wage curve reloaded. NBER Working Paper 11338 / IZA DP 1665.
- Bureau of Labor Statistics (2026). Labor share at its lowest level, 52.8 percent, in second quarter 2026. *The Economics Daily*, 15 September 2026.
- Clarke, K. A., and Stone, R. W. (2008). Democracy and the logic of political survival. *American Political Science Review*, 102(3), 387–392.
- Cockshott, W. P., and Cottrell, A. (1997). Labour-time versus alternative value bases: A research note. *Cambridge Journal of Economics*, 21(4), 545–549.
- Domanski, D., Scatigna, M., and Zabai, A. (2016). Wealth inequality and monetary policy. *BIS Quarterly Review*, March, 45–64.
- Favara, G., and Imbs, J. (2015). Credit supply and the price of housing. *American Economic Review*, 105(3), 958–992.
- Federal Reserve Board (2026). Distributional Financial Accounts: share of net worth held by the top 1%, Q2 2026 (FRED series WFRBST01134).
- Federal Reserve Bank of St. Louis (2026). Unemployment rate, UNRATE, 1948–2026.
- Federal Reserve Bank of St. Louis (2026). Household debt to GDP for the United States, HDTGPDUSQ163N (BIS data).
- Funke, M., Schularick, M., and Trebesch, C. (2016). Going to extremes: Politics after financial crises, 1870–2014. *European Economic Review*, 88, 227–260.
- Furceri, D., Loungani, P., and Ostry, J. D. (2019). The aggregate and distributional effects of financial globalization: Evidence from macro and sectoral data. CEPR Discussion Paper 14001.
- Imbert, C., and Papp, J. (2015). Labor market effects of social programs: Evidence from India's employment guarantee. *American Economic Journal: Applied Economics*, 7(2), 233–263.
- Işıkara, G., and Mokre, P. (2022). Price-value deviations and the labour theory of value: Evidence from 42 countries, 2000–2017. *Review of Political Economy*, 34(1), 165–180.
- Jordà, Ò., Schularick, M., and Taylor, A. M. (2013). When credit bites back. *Journal of Money, Credit and Banking*, 45(s2), 3–28.
- Jordà, Ò., Schularick, M., and Taylor, A. M. (2016). The great mortgaging: Housing finance, crises and business cycles. *Economic Policy*, 31(85), 107–152.
- Klass, O. S., Biham, O., Levy, M., Malcai, O., and Solomon, S. (2006). The Forbes 400 and the Pareto wealth distribution. *Economics Letters*, 90(2), 290–295. As reported in Benhabib and Bisin (2018).
- Lakner, C., and Milanovic, B. (2016). Global income distribution: From the fall of the Berlin Wall to the Great Recession. *World Bank Economic Review*, 30(2), 203–232.
- Ludwig, D., and Yakovenko, V. M. (2022). Physics-inspired analysis of the two-class income distribution in the USA in 1983–2018. *Philosophical Transactions of the Royal Society A*, 380, 20210162.
- Maito, E. E. (2014). The historical transience of capital: The downward trend in the rate of profit since XIX century. MPRA Paper 55894.
- Mian, A., Rao, K., and Sufi, A. (2013). Household balance sheets, consumption, and the economic slump. *Quarterly Journal of Economics*, 128(4), 1687–1726.
- Mian, A., Sufi, A., and Trebbi, F. (2014). Resolving debt overhang: Political constraints in the aftermath of financial crises. *American Economic Journal: Macroeconomics*, 6(2), 1–28.
- Miller, N. H. (2009). Strategic leniency and cartel enforcement. *American Economic Review*, 99(3), 750–768.
- Muralidharan, K., Niehaus, P., and Sukhtankar, S. (2023). General equilibrium effects of (improving) public employment programs: Experimental evidence from India. *Econometrica*, 91(4), 1261–1295.
- Obinger, H., and Schmitt, C. (2011). Guns and butter? Regime competition and the welfare state during the Cold War. *World Politics*, 63(2), 246–270.
- Quarfoot, D., von Kohorn, D., Slavin, K., Sutherland, R., Goldstein, D., and Konar, E. (2017). Quadratic voting in the wild: Real people, real votes. *Public Choice*, 172, 283–303.
- Shaikh, A. (1998). The empirical strength of the labour theory of value. In R. Bellofiore (ed.), *Marxian Economics: A Reappraisal*, vol. 2. Macmillan. As reported in *Classical Econophysics*, Table 10.2.
- Shiller, R. J. (2011). Irving Fisher, debt deflation and crises. Cowles Foundation Discussion Paper 1817.
- Thachil, T. (2011). Embedded mobilization: Nonstate service provision as electoral strategy in India. *World Politics*, 63(3), 434–469.
- Tversky, A., and Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323.
- Vermeulen, P. (2018). How fat is the top tail of the wealth distribution? *Review of Income and Wealth*, 64(2), 357–387. As reported in Benhabib and Bisin (2018).
- Zachariah, D. (2006). Labour value and equalisation of profit rates. *Indian Development Review*, 4(1), 1–21. As reported in *Classical Econophysics*, Table 10.3.

### Sources consulted online

- [Maito (2014), MPRA 55894](https://mpra.ub.uni-muenchen.de/55894/)
- [Basu (2022), UMass working paper 318](https://scholarworks.umass.edu/econ_workingpaper/318)
- [Işıkara and Mokre (2022), RePEc record](https://ideas.repec.org/a/taf/revpoe/v34y2022i1p165-180.html)
- [Ludwig and Yakovenko (2022), arXiv:2110.03140](https://arxiv.org/abs/2110.03140)
- [Fed DFA top 1% wealth share, FRED WFRBST01134](https://fred.stlouisfed.org/series/WFRBST01134)
- [Blanchflower and Oswald (2005), SSRN](https://papers.ssrn.com/abstract=723307)
- [BLS (2026), labour share at 52.8%](https://www.bls.gov/opub/ted/2026/labor-share-at-its-lowest-level-52-8-percent-in-second-quarter-2026.htm)
- [FRED UNRATE](https://fred.stlouisfed.org/series/UNRATE)
- [Barbosa-Filho and Taylor (2006), RePEc record](https://ideas.repec.org/a/bla/metroe/v57y2006i3p389-411.html)
- [Imbert and Papp (2015), VoxDev summary](https://www.voxdev.org/node/62777)
- [Muralidharan, Niehaus and Sukhtankar, NBER w23838](https://www.nber.org/papers/w23838)
- [Funke, Schularick and Trebesch (2016), Kiel Institute](https://www.kielinstitut.de/publications/going-to-extremes-politics-after-financial-crises-1870-2014-8783)
- [Obinger and Schmitt (2011)](https://www.socium.uni-bremen.de/f/a9c45e6d68.pdf)
- [Clarke and Stone (2008), RePEc record](https://ideas.repec.org/a/cup/apsrev/v102y2008i03p387-392_08.html)
- [Thachil (2011), World Politics](https://www.cambridge.org/core/journals/world-politics/article/abs/embedded-mobilization-nonstate-service-provision-as-electoral-strategy-in-india/386281259E8743E3C2D78B3D641ABA8B)
- [Domanski, Scatigna and Zabai (2016), BIS Quarterly Review](https://www.bis.org/publ/qtrpdf/r_qt1603f.htm)
- [Lakner and Milanovic (2016), CGD summary](https://www.cgdev.org/node/3126072)
- [Fed DFA top 1% wealth share, full series](https://fred.stlouisfed.org/data/WFRBST01134.txt)
- [Household debt to GDP, FRED HDTGPDUSQ163N](https://fred.stlouisfed.org/data/HDTGPDUSQ163N.txt)
- [Jordà, Schularick and Taylor (2013), NBER w17621](https://www.nber.org/papers/w17621.pdf)
- [Jordà, Schularick and Taylor, "The great mortgaging", VoxEU](https://cepr.org/voxeu/columns/great-mortgaging)
- [Favara and Imbs (2015), PSE record](https://www.parisschoolofeconomics.eu/en/publications-hal/credit-supply-and-the-price-of-housing)
- [Mian, Rao and Sufi (2013), RePEc record](https://ideas.repec.org/a/oup/qjecon/v128y2013i4p1687-1726.html)
- [Mian, Sufi and Trebbi (2014), Chicago Booth summary](https://www.chicagobooth.edu/research/rustandy/social-impact-research/research-papers/2014/resolving-debt-overhang-political-constraints-in-the-aftermath-of-financial-crises)
- [Benhabib and Bisin (2018), JEL survey](https://bpb-us-e1.wpmucdn.com/wp.nyu.edu/dist/c/16384/files/2019/11/5.-BB-JelPub.pdf)
- [Furceri, Loungani and Ostry, VoxEU summary](https://cepr.org/voxeu/columns/aggregate-and-distributional-effects-financial-globalisation)
- [Fisher (1933), debt deflation](https://en.wikipedia.org/wiki/Debt_deflation)
- [Shiller (2011), Irving Fisher, debt deflation and crises](https://cowles.yale.edu/sites/default/files/2022-08/d1817.pdf)

## Appendix A: Palimpsest at a glance

```
#lang palimpsest
#fuel N                            // step budget (default 100,000)
#mode rewriting-as-running | rewrite-then-run
#caps { rewrite: [self] }          // capability for self-modification
#rebind main                       // later commands see the rewritten main
#memo                              // normal-form memo and strict-argument cache

import "path.pal"                  // merge a library's rules and strategies (transitive, cycle-safe)

rule NAME : LHS => RHS where ?v <- EXPR, GUARD, ...
transition NAME : LHS => RHS       // usable only by name from a strategy
strategy NAME = STRATEGY           // id fail prim rules s1;s2 s1+s2 try repeat oncetd outermost innermost ...
main = TERM

run STRATEGY | show TERM with S | display TERM with S | assert TERM with S
let $NAME = TERM with S
rewrite self with S | rewrite file "p" with S
```

- **Pattern variables.** `?x` matches one term, `?xs...` a sequence, and `!x` is strict (normalize first).
- **Numbers.** Integers of any size and rationals `n/d`, with `q/ num den floor ceil round-to expt isqrt decimal`.
- **Records.** `(rec (k v) ...)` with `@ set@ put@ add@ has@ del@ keys@ sum@`.
- **Other primitives.** Strings: `cat str sym padl padr explode implode`. The deterministic hash: `rng`. Reflection: `matches? match-witness`.
- **Command-line flags.** `--dry-run` (never write), `--fuel N`, `--stats` (rewrite profile), `--memo` and `--trace N`. The subcommand `palimpsest undo FILE` restores the last self-rewrite.

## Appendix B: Files of the study

| file | role | section |
| --- | --- | --- |
| `lib/linalg.pal` | exact vectors and matrices, Hawkins–Simon, contractive iterations, strict combinators | throughout |
| `lib/value.pal` | values, plans, exploitation, certified profit rate, FMT, GCET, frontier, MAWD, Okishio, skilled labour | §4 |
| `lib/longrun.pal` | the long-run attractor and its floor; CE Table 10.1 | §4.1, §4.3 |
| `lib/econophysics.pal` | multiplicities, random exchange, two classes, asset cap, Cantillon, vouchers | §5 |
| `lib/classgames.pal` | bargaining, the class-struggle game, Roemer, collusion, QV, prospect theory, patronage | §6, §7 |
| `lib/selectorate.pal` | the selectorate equilibrium with certified square roots | §7.4 |
| `lib/polecon.pal` | the integrated economy, its causal-loop diagram and probes | §8.1–8.5 |
| `lib/finance.pal` | credit money and a fixed stock, the wealth lattice, the debt-deflation cascade | §9.1–9.3 |
| `lib/polecon-fin.pal` | the financialized regime and induced mechanization, on the chain of `polecon.pal` | §9.4–9.6 |
| `lib/cld.pal`, `lib/dialectics.pal`, `lib/report.pal` | loop enumeration, Structural Dialectics, text reports | §8.5–8.6 |
| `examples/me-tour.pal` | one feedback loop, traced (2 assertions) | §3.3 |
| `examples/me-value.pal` | value, planning, prices, profit (17) | §4 |
| `examples/me-classical.pal` | the long run, the accumulation identity, CE Table 10.1 (8) | §4.1, §4.3, §8.3 |
| `examples/me-distribution.pal` | the distribution of money (18) | §5 |
| `examples/me-games.pal` | bargaining, class struggle, Roemer, collusion, QV, prospect theory, patronage (20) | §6, §7 |
| `examples/me-selectorate.pal` | political survival (7) | §7.4 |
| `examples/me-economy.pal` | the self-rewriting economy (an invariant assertion every run) | §8.1 |
| `examples/me-regimes.pal` | trajectories, stress, the 27-setting grid (13) | §8.2–8.4 |
| `examples/me-loops.pal` | cycles, edge probes, what planning removes (5) | §8.5 |
| `examples/me-dialectics.pal` | Structural Dialectics (13) | §8.6 |
| `examples/me-extremes.pal` | limits, thresholds and inflection points (6) | §4.2–4.3, §6.1–6.2, §7.1, §7.3–7.4, §8.3–8.4 |
| `examples/me-evidence.pal` | the model against cited data (4) | §§4–9, §10.2 |
| `examples/me-finance.pal` | credit money, the wealth lattice, debt deflation, capital mobility (7) | §9.1–9.3, §9.7 |
| `examples/me-financialized.pal` | the financialized economy: channels, crunch, thresholds, stress grid, remedies, edges and loops (12) | §9.4–9.6 |
| `crosscheck/materialist_crosscheck.py` | independent Python implementation (80 checks) | §11 |
| `verify-materialist.sh` | runs all of the above (15 checks) | §11 |
