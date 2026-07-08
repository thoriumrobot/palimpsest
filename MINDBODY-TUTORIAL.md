# Tutorial: Simulating the Mind–Body Loop

This tutorial teaches you to read, run, and write the mind–body loop simulations
that ship with Palimpsest. It goes from the simplest possible loop to two-agent
models, one environment at a time. You will run real code from a shell as you go.

## What this models (and what it doesn't)

The "mind–body loop" is the idea that the body produces a mind and the mind
simultaneously acts back on the body — a circle of reciprocal causation that also
refers to itself. Palimpsest is a rewriting language whose native subject is
self-reference, so it is a natural place to make that loop *executable* and watch
what it does.

Be clear about the claim: these programs model the **form** of the loop —
reciprocal causation, feedback, self-modification, noise — as a small dynamical
system. They do **not** model experience. When a run "settles," that is a
self-consistent state, not a feeling; nothing here touches the question of why
there is something it is like to be a system. Treat the output as a labelled
diagram you can run, not as a claim about minds being conscious.

## The idea in one picture

Time advances in discrete ticks. At each tick the system is in a **state**. A
single rule, `step`, reads the state (the body "senses") and returns the next
state (the mind "acts"). Repeating `step` traces a **trajectory**, and the shape
of that trajectory is the interesting thing. A loop can:

- **settle** to a fixed point it reproduces forever (a stable "self");
- fall into a **limit cycle** and oscillate forever;
- **run away** and escalate without bound;
- stay **bounded** — never settle exactly, but never escape either (the verdict
  for noisy or orbiting systems).

The engine runs the loop, classifies which of these happened, and draws a text
graph of the trajectory. That is the whole game.

---

## 1. Running your first simulation

You need the interpreter built once. From the project root:

```sh
cargo build --release
```

That produces `./target/release/palimpsest`. Now run the simplest environment —
always from the project root, so the `import` lines resolve:

```sh
./target/release/palimpsest examples/mind-homeostasis.pal
```

You will see a header (program, mode, fuel, capabilities), then a `display:`
section with a graph, then the verdict:

```
mind-body loop
   9 |#
   6 |####
   4 |###########
   1 |###########
     +------------> time
  trend ▆▅▄▄▃▂▂▂▂▂▂
  => SETTLED to a self-consistent fixed point:
       ====  arousal 4   calm
```

Read the graph as a column chart: the vertical axis is arousal, time runs left to
right, and each column is filled up to that tick's value. Arousal starts at 9 and
falls to 4, where it stays — a settled loop. The `trend` line is the same series
as a compact sparkline.

**A quirk you should know about.** These example files *rewrite themselves*. The
first run prints `status : WROTE` — the program computed its trajectory and wrote
the result back into its own source (this is a self-rewriting quine; see §7). Run
the same file again and you will see `status : FIXED POINT … This is a quine`, and
the *same* graph. Re-running is harmless — you always get the graph — so you can
run any example as many times as you like. When you want to *experiment*, though,
don't edit the shipped examples; write your own file (§4), which will not rewrite
itself.

---

## 2. Reading the output

Every run prints a graph and then a verdict, so it is worth learning to read them
once. The rendering is a small library, `lib/chart.pal`, and across the tutorial
you will meet four kinds of graph:

- a **column chart** (`colplot`) for single-variable runs — value on the vertical
  axis, time running left to right, each column filled up to that tick's value, as
  in the homeostasis run above;
- a **sparkline** (`spark`) — the one-line `trend` printed under every column
  chart;
- an **overlay** (`overlay`) for the two-variable models, drawing two curves on one
  chart (`o` for the first, `x` for the second, `*` where they meet) so you can
  watch them converge or diverge;
- a **histogram** (`histogram`) of the value distribution, added automatically for
  `BOUNDED` runs, where *how often* the system sits at each level is the point.

The verdict line names the attractor — `SETTLED`, `LIMIT CYCLE`, `RUNAWAY`, or
`BOUNDED` — and, when it settles, shows the fixed-point state. That is the whole
vocabulary; the rest of the tutorial is worked examples.

---

## 3. The anatomy of an environment

Open `examples/mind-homeostasis.pal`. Ignoring the header directives, the body is:

```
import "../lib/mindbody.pal"
rule step : (step (being ?a ?any)) => (being ?na (feel-of ?na)) where ?na <- (toward ?a 4)
rule feel-of  : (feel-of ?a) => calm  where (<= ?a 4)
rule feel-of2 : (feel-of ?a) => tense where (> ?a 4)
strategy solve = outermost(prim + rules)
main = (trace (being 9 tense) 10)
rewrite self with solve
display (loop-view main) with solve
```

Piece by piece:

- **The state.** A single body is written `(being AROUSAL TAG)`: an integer arousal
  and a "tag" term describing the mind (here a mood symbol like `calm`).
- **`step`.** The one rule that advances time. It reads `(step STATE)` and returns
  the next state. Here it moves arousal one unit `toward` the set-point 4 and reads
  off a mood. The `where ?na <- (toward ?a 4)` binding computes the new arousal
  once and reuses it.
- **`main = (trace INIT N)`.** `trace` runs the loop for `N` ticks from `INIT`,
  producing `N+1` states (the initial state plus `N` steps), and classifies the
  attractor.
- **`display (loop-view main)`.** `loop-view` turns the trajectory into the graph
  you saw.

The engine (`lib/mindbody.pal`) gives you a few helpers to write `step` with:

- `(toward a s)` — move `a` one unit toward `s` (proportional regulation);
- `(clamp x lo hi)` — keep `x` within `[lo, hi]`;
- `(mix a b pct)` — move `a` a fraction `pct/100` of the way toward `b`;

plus the ordinary primitives (`+ - * / mod`, comparisons, `abs`, `min`, `max`,
and `rng` for noise). You never write the classifier or the graphing code; you
only write `step` and choose `INIT` and `N`.

---

## 4. Writing and running your own loop

The cleanest way to experiment is your own file that does **not** rewrite itself,
so running it never changes it. Create `examples/myloop.pal`:

```
#lang palimpsest
#fuel 5000000
import "../lib/mindbody.pal"
rule step : (step (being ?a ?tag)) => (being (toward ?a 5) calm)
strategy solve = outermost(prim + rules)
main = (trace (being 10 tense) 12)
display (loop-view main) with solve
```

Run it from the project root:

```sh
./target/release/palimpsest examples/myloop.pal
```

```
mind-body loop
  10 |#
   6 |#####
   5 |#############
   1 |#############
     +--------------> time
  trend ▆▆▅▄▄▃▃▃▃▃▃▃▃
  => SETTLED to a self-consistent fixed point:
```

Putting the file in `examples/` matters only because of the import path
`"../lib/mindbody.pal"` — it is written relative to the file's own directory, so a
file in `examples/` finds the library in `lib/`. Keep that line and you can run
from the project root with no environment variables. From here, change the
set-point (the `5`), the starting arousal, or `N`, re-run, and watch the graph
change. Everything below is a variation on this one file.

The chart tools are not tied to the loop engine; you can call them on any
`(series ...)` of your own. For instance, a bare sparkline:

```sh
printf '#lang palimpsest\nimport "lib/chart.pal"\nstrategy s = outermost(prim+rules)\nmain = (x)\nshow (spark (series 1 4 9 4 1) 10) with s\n' > /tmp/spark.pal
./target/release/palimpsest /tmp/spark.pal
```

(`show` prints a term's reduced value; note that from a file outside `examples/`
the import path is `"lib/chart.pal"`.)

---

## 5. The environments, simple to complex

Each environment differs only in its `step` rule (and its state shape). Run any of
them the same way:

```sh
./target/release/palimpsest examples/<name>.pal
```

### 5.1 Homeostasis — a stable self (`mind-homeostasis.pal`)

The mind senses arousal and nudges the body one step toward a set-point. Gentle
negative feedback converges and holds — the canonical fixed point.

```
rule step : (step (being ?a ?any)) => (being ?na (feel-of ?na)) where ?na <- (toward ?a 4)
rule feel-of  : (feel-of ?a) => calm  where (<= ?a 4)
rule feel-of2 : (feel-of ?a) => tense where (> ?a 4)
main = (trace (being 9 tense) 10)
```

Verdict: `SETTLED` at arousal 4. This is your reference point; every other outcome
is a departure from it.

### 5.2 Limit cycle — perpetual oscillation (`mind-cycle.pal`)

Give the mind two modes with a switching delay (hysteresis): let arousal rise until
it feels too tense, then drive it down until it feels too flat, then flip again. It
never settles.

```
rule step-rise-go   : (step (being ?a rise)) => (being (+ ?a 2) rise) where (< ?a 8)
rule step-rise-flip : (step (being ?a rise)) => (being (- ?a 2) fall) where (>= ?a 8)
rule step-fall-go   : (step (being ?a fall)) => (being (- ?a 2) fall) where (> ?a 2)
rule step-fall-flip : (step (being ?a fall)) => (being (+ ?a 2) rise) where (<= ?a 2)
main = (trace (being 2 rise) 14)
```

```
   8 |   #     #
   6 |  ###   ###   #
   4 | ##### ##### ##
   2 |###############
     +----------------> time
  trend ▁▂▄▅▄▂▁▂▄▅▄▂▁▂▄
  => LIMIT CYCLE: never settles; oscillates with period 6 steps
```

The engine measures the period by finding where the last state first recurs.

### 5.3 Runaway — a dysregulation spiral (`mind-runaway.pal`)

Flip the feedback sign: fear drives arousal up, and high arousal feeds fear. Each
reinforces the other and both escalate. The tag now carries a number (`(fear F)`),
which is how the mind's state accumulates.

```
rule step : (step (being ?a (fear ?f))) => (being (+ ?a ?f) (fear (nfear ?a ?f)))
rule nfear-up   : (nfear ?a ?f) => (+ ?f 1) where (>= ?a 4)
rule nfear-same : (nfear ?a ?f) => ?f       where (< ?a 4)
main = (trace (being 2 (fear 1)) 9)
```

```
  12 |      ####
   8 |     #####
   4 |  ########
   1 |##########
     +-----------> time
  trend ▁▂▂▃▄▆████
  => RUNAWAY: no fixed point; the loop escalates without bound
```

Arousal climbs off the top of the chart (values above the height clip to the top
row). The engine calls it `RUNAWAY` because arousal blows past a divergence bound.

### 5.4 The strange loop — the mind rewrites its own law (`mind-strange-loop.pal`)

Here the being carries its own regulation policy — its set-point — inside its state
as `(goal G)`. While arousal differs from the goal the mind regulates toward it;
but each time it *reaches* the goal, the mind lowers the goal, re-opening the gap.
The process edits the law that produces it, descending a staircase until it hits a
floor.

```
rule step-regulate : (step (being ?a (goal ?g))) => (being (toward ?a ?g) (goal ?g)) where (<> ?a ?g)
rule step-lower    : (step (being ?a (goal ?g))) => (being ?a (goal (- ?g 1)))         where (= ?a ?g), (> ?g 2)
rule step-floor    : (step (being ?a (goal ?g))) => (being ?a (goal ?g))               where (= ?a ?g), (<= ?g 2)
main = (trace (being 6 (goal 6)) 11)
```

```
   6 |##
   4 |######
   2 |############
     +-------------> time
  trend ▄▄▃▃▂▂▂▂▁▁▁▁
  => SETTLED to a self-consistent fixed point:
       ==  arousal 2   (goal 2)
```

The fuller version of this idea — the mind editing an entire rule *table* stored as
data — is exactly the pattern in `examples/self-turing.pal`.

### 5.5 Saturating control — the will overwhelmed (`mind-saturating.pal`)

The body has a constant upward load; the mind corrects toward a set-point but its
effort **saturates** at ±1 (a bounded will). This introduces `clamp` and `abs`. A
bounded controller cannot overcome a larger steady load, so arousal climbs one step
at a time and pins against the ceiling; `abs` reports the growing distress in the
tag.

```
rule step : (step (being ?a (ctl ?d))) => (being ?na (ctl ?nd))
  where ?eff <- (clamp (- 4 ?a) -1 1),
        ?na  <- (clamp (+ (+ ?a 2) ?eff) 0 12),
        ?nd  <- (abs (- 4 ?na))
main = (trace (being 0 (ctl 4)) 10)
```

```
  12 |        ###
   8 |    #######
   4 |  #########
   1 | ##########
     +------------> time
  trend ▁▂▄▄▅▆▆▇███
  => SETTLED to a self-consistent fixed point:
       ============  arousal 12   (ctl 8)
```

It settles — but at the ceiling, not the goal. A stable self that is not the self
the mind wanted.

### 5.6 Noisy homeostasis — a stable band (`mind-noisy.pal`)

Now add randomness. `rng` is a deterministic hash of a seed carried in the state:
pure, so the run is reproducible and still a quine, yet the sequence looks random.
Homeostasis plus a small ±2 perturbation never settles exactly but stays in a band
— the verdict is `BOUNDED`, and the engine adds a distribution histogram because
that is where "how often" matters.

```
rule step : (step (being ?a (mood ?lab ?s))) => (being ?na (mood (mood-of ?na) ?ns))
  where ?ns <- (rng ?s),
        ?noise <- (- (mod ?ns 5) 2),
        ?na <- (clamp (+ (toward ?a 5) ?noise) 0 10)
rule mood-of-lo : (mood-of ?a) => calm where (<= ?a 5)
rule mood-of-hi : (mood-of ?a) => edgy where (> ?a 5)
main = (trace (being 9 (mood edgy 12345)) 14)
```

```
   9 |#  #
   6 |###### # ### ##
   4 |###############
   1 |###############
     +----------------> time
  trend ▆▅▅▆▄▄▂▄▃▄▅▄▃▄▄
  distribution (how often at each arousal):
   5 | ## 2
   6 | ##### 5
   7 | ## 2
   8 | ### 3
  => BOUNDED: never settles exactly, but stays in a stable region (noisy / orbiting)
```

The seed is carried in the tag but hidden from the display; change the starting
seed (`12345`) and you get a different but equally reproducible run.

### 5.7 Bistable + noise — metastable switching (`mind-bistable.pal`)

Two stable moods — low (~2) and high (~8) — separated by a barrier at 5. The mind
pulls toward the nearer attractor, but random kicks occasionally shove arousal
across the barrier, so the system dwells near one mood and then jumps to the other.
This is the richest single-variable environment, and the histogram makes its
signature visible: two clusters.

```
rule step : (step (being ?a (mood ?lab ?s))) => (being ?na (mood (mood-of ?na) ?ns))
  where ?ns <- (rng ?s),
        ?kick <- (- (mod ?ns 7) 3),
        ?well <- (nearest-well ?a),
        ?pull <- (clamp (- ?well ?a) -2 2),
        ?na <- (clamp (+ (+ ?a ?pull) ?kick) 0 10)
rule nearest-well-lo : (nearest-well ?a) => 2 where (< ?a 5)
rule nearest-well-hi : (nearest-well ?a) => 8 where (>= ?a 5)
rule mood-of-lo : (mood-of ?a) => low  where (< ?a 5)
rule mood-of-hi : (mood-of ?a) => high where (>= ?a 5)
main = (trace (being 2 (mood low 4242)) 24)
```

```
  10 |     ##      #
   8 |    ####     #
   5 |  #############
   2 |################  ##  #
     +--------------------------> time
  trend ▁▁▃▃▅▆▆▆▄▃▃▃▃▆▃▂▁▁▂▂▁▁▁▁▁
  distribution (how often at each arousal):
   0 | #### 4
   2 | ### 3
   5 | ####### 7
  10 | ### 3
  => BOUNDED: never settles exactly, but stays in a stable region (noisy / orbiting)
```

The column chart shows the trajectory dwelling low, jumping to the high well, and
falling back; the histogram shows the bimodality directly. Neither well alone
produces switching — it is a product of the two wells *and* the noise.

### 5.8 Predictive processing — a self-model cohering (`mind-predictive.pal`)

Now two variables. The state `(pp BODY BELIEF PRIOR)` gives the mind a *belief*
about its own arousal. It minimizes prediction error two ways at once: perception
moves the belief toward the body, and action moves the body toward the belief;
the belief is also drawn toward a prior expectation. The display switches to an
**overlay** so you can watch the two tracks (`o` = body, `x` = belief) converge.

```
rule step : (step (pp ?body ?pred ?prior)) => (pp ?nbody ?npred ?prior)
  where ?nbody <- (clamp (toward (toward ?body 8) ?pred) 0 10),
        ?npred <- (clamp (toward (toward ?pred ?body) ?prior) 0 10)
main = (trace (pp 0 10 5) 8)
```

```
  o = body   x = belief
  10 |x
   8 | x
   6 |  xoooooo
   5 |   xxxxxx
   2 | o
     +----------> time
  => SETTLED to a self-consistent fixed point:
       body ====== 6   belief ===== 5   err 1
```

Belief (10) and body (0) close a prediction error of 10 down to a residual of 1:
the prior biases perception, so the mind's picture of itself settles just under the
body rather than exactly on it. This is the scientific model of the loop (active
inference) in miniature.

### 5.9 Co-regulation — two loops meeting (`mind-dyad.pal`)

The "self" becomes a pair. The state is a `world` of two beings. Alice's baseline
is calm (3), Bob's anxious (8); each regulates toward their own baseline *and* is
pulled toward the other (attunement). Starting far apart, they converge to a shared
compromise.

```
rule step : (step (world (being ?a alice) (being ?b bob))) => (world (being ?a2 alice) (being ?b2 bob))
  where ?a2 <- (clamp (toward (toward ?a 3) ?b) 0 10),
        ?b2 <- (clamp (toward (toward ?b 8) ?a) 0 10)
main = (trace (world (being 0 alice) (being 10 bob)) 8)
```

```
  o = A   x = B
  10 |x
   8 | x
   7 |  xxxxxxx
   4 |  ooooooo
   2 | o
     +----------> time
  => SETTLED to a self-consistent fixed point:
       A ==== 4   B ======= 7   gap 3
```

The gap narrows but never fully closes — each keeps some of their own baseline.

### 5.10 Escalation — two loops feeding each other (`mind-dyad-escalation.pal`)

The same two-agent structure with the coupling's sign flipped: each is agitated by
the other, more so when the other is more aroused, and neither self-regulates. A
quarrel that feeds on itself.

```
rule step : (step (world (being ?a alice) (being ?b bob))) => (world (being ?a2 alice) (being ?b2 bob))
  where ?a2 <- (min (+ ?a (spur ?a ?b)) 60),
        ?b2 <- (min (+ ?b (spur ?b ?a)) 60)
rule spur-more : (spur ?self ?other) => 3 where (> ?other ?self)
rule spur-less : (spur ?self ?other) => 2 where (<= ?other ?self)
main = (trace (world (being 3 alice) (being 4 bob)) 12)
```

```
  o = A   x = B
  10 |   **********
   8 |  *
   6 | *
   4 |x
   3 |o
     +--------------> time
  => RUNAWAY: no fixed point; the loop escalates without bound
```

`*` marks where both curves coincide; they climb in lockstep and pin at the top.
The only difference between this and co-regulation is the sign of the coupling —
which is the point: whether a shared loop soothes or inflames is a property of the
coupling, not of the individuals.

---

## 6. Experiments to try

Work in your own file (§4) so runs are non-destructive, and predict the verdict
before you run:

- In homeostasis, raise the step size so the mind *overshoots* the set-point. Does
  it still settle, or does it start to oscillate?
- In the limit cycle, change the thresholds `8` and `2`. What sets the period and
  the amplitude?
- In noisy homeostasis, widen the noise (`mod ?ns 5` → a larger modulus). How wide
  does the band get before it looks like runaway?
- In the dyad, make the two baselines equal. Do they meet exactly (gap 0)?
- Flip the dyad's coupling sign yourself to turn co-regulation into escalation, and
  confirm the verdict changes.

Because `rng` is deterministic, a given seed always gives the same run — change the
seed to get a different sample, not different physics.

---

## 7. The self-rewriting twist (optional)

The shipped examples add three lines the learner template omits:

```
#mode rewrite-then-run
#caps { rewrite: [self] }
...
rewrite self with solve
```

With these, running the file first *rewrites the file itself* — it replaces
`main = (trace …)` with `main = (report …)`, the fully computed and classified
trajectory — and then displays it. Run it a second time and nothing changes: the
file is already its own result, so it reproduces byte-for-byte. That is the
definition of a **quine**. It is a fitting flourish for this project — a program
about self-reference whose act of computing its trajectory turns it into a fixed
point of itself — but it is orthogonal to the modeling. Your own experiments do not
need it.

---

## 8. Honest caveats

This is a study of the loop's *form*, and a coarse one: the dynamics are integer,
deterministic (even the noise is a pure hash), and low-dimensional, whereas the
real loop is continuous, genuinely stochastic, and embodied. What the toy buys you
is that the self-referential, self-modifying *structure* is explicit and runnable,
so you can ask precise questions — when a loop has a stable self, when it must
oscillate, when it runs away, and how the answer changes with a coupling sign, a
gain, or a little noise. Read it alongside the real frameworks it gestures at
(Hofstadter's strange loops, autopoiesis, predictive processing), not as a
replacement for them, and never as a claim about experience.

For the concise reference version of this material, see `MIND-BODY.md`; for the
language itself, see `TUTORIAL.md` and `README.md`.
