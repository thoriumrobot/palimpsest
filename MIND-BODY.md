# Exploring the mind↔body loop in Palimpsest

These programs are an intuition pump for one specific question: what are the
possible *outcomes* of a system in which the body produces a mind and the mind
simultaneously acts back on the body? Palimpsest is a good fit because that is a
loop of **reciprocal causation plus self-reference**, and self-reference is the
language's native subject.

## What this does and does not model

This models the **form** of the loop — the reciprocal causation and the
self-reference — as a small dynamical system, and lets you watch which *attractor*
different couplings fall into. It does **not** model experience. A fixed point
here is a self-consistent state, not a feeling; nothing in these programs touches
the "hard problem" of why there is something it is like to be a system, and
building a self-referential program that "models mind and body" neither explains
nor instantiates consciousness. Treat it as a labelled diagram you can run, not as
a claim about sentience. It is also discrete, deterministic, and symbolic, whereas
the real loop is continuous, noisy, and embodied; for quantitative dynamics,
coupled differential equations or an active-inference simulation are more
faithful. What Palimpsest adds is that the self-referential, self-modifying
*structure* becomes explicit and executable.

## The engine (`lib/mindbody.pal`)

A state can be a single `(being AROUSAL TAG)`, but the engine is shape-agnostic:
it renders and classifies any state via a `showstate` dispatcher, so an
environment can also use a predictive-processing agent `(pp BODY BELIEF PRIOR)` or
a two-being world `(world (being ...) (being ...))`. Each environment supplies one
`step` rule that senses the state and acts back on it. Numeric dynamics are built
from the primitives `min`/`max`/`abs`, a `clamp` helper, `rng` (a deterministic
splitmix64 hash, for reproducible pseudo-randomness), and `mix a b pct` (move `a`
a fraction `pct/100` of the way toward `b` — the fixed-point gradient step behind
perception, action, and attunement). The engine runs the loop for N ticks,
collects the trajectory, and classifies the attractor:

- **settled** — the last two states are equal: a fixed point the loop reproduces
  (a self-consistent "self"; as a self-rewriting program this is a quine).
- **limit cycle** — the last state recurs earlier: a stable oscillation with a
  measured period.
- **runaway** — arousal blows past a divergence bound: the loop escalates without
  bound.
- **bounded** — none of the above: it never settles *exactly*, but stays within a
  stable region — the verdict for noisy or orbiting systems, whose "self" is a
  stationary band rather than a single point.

The dynamics are built from the numeric primitives the language provides for this
kind of modelling: `min`/`max`/`abs` and a `clamp` helper for bounded variables,
and `rng` — a deterministic splitmix64 hash of a seed — for *reproducible*
pseudo-randomness. Because `rng` is pure, even the stochastic environments below
self-rewrite to byte-identical quines: the noise is the same every run.

Each environment is a self-rewriting program: `main` starts as `(trace initial N)`,
the self-rewrite runs the loop and writes the classified trajectory back into the
file (so the file *becomes* its own result), and the `display` command renders it
as a **text graph**. The rendering uses a small visualization library written in
Palimpsest, `lib/chart.pal`:

- `colplot` — a column chart, value on the vertical axis and time across, used for
  single-variable runs;
- `overlay` — two curves on one chart (`o` = first, `x` = second, `*` = both),
  used for the two-variable models so you watch the tracks converge or diverge;
- `histogram` — the value distribution (how often each level occurs), shown
  automatically for *bounded* runs, where it reveals bands and bimodality;
- `spark` — a compact one-line sparkline.

So running an environment prints a labelled 2D graph of its trajectory, then the
verdict. The chart tools are reusable on any `(series ...)` of integers.

For example, the limit-cycle environment renders as a column chart whose shape is
the oscillation itself, with a sparkline underneath:

```
   8 |   #     #
   6 |  ###   ###   #
   4 | ##### ##### ##
   2 |###############
     +----------------> time
  trend ▁▂▄▅▄▂▁▂▄▅▄▂▁▂▄
```

the two-variable models render as an overlay of two curves (here the dyad, `o`
rising to Alice's compromise and `x` falling to Bob's):

```
   8 | x
   7 |  xxxxxxx
   4 |  ooooooo
   2 | o
     +----------> time
```

and bounded runs add a distribution histogram (the bistable run is visibly
bimodal -- clusters low and around the middle):

```
   0 | #### 4
   2 | ### 3
   5 | ####### 7
```
the self-rewrite runs the loop and writes the classified trajectory back into the
file (so the file *becomes* its own result), and the `display` command renders it
as a text graph (see below).

## The environments

Run any of them (from the project root, so imports resolve):

```sh
./target/release/palimpsest examples/mind-homeostasis.pal
```

### 1. Homeostasis → a stable self (`examples/mind-homeostasis.pal`)

The mind regulates arousal one step toward a set-point. Negative feedback with
gentle gain converges: the loop reaches a self-consistent fixed point and holds.

```
  trend ▆▅▄▄▃▂▂▂▂▂▂        (arousal 9 -> 4)
  => SETTLED to a self-consistent fixed point:
       ====  arousal 4   calm
```

### 2. Limit cycle → perpetual oscillation (`examples/mind-cycle.pal`)

The mind switches modes with hysteresis: it lets arousal rise until it feels too
tense, drives it down until it feels too flat, then flips again. Regulation with a
switching delay never settles — it orbits forever (a mood/sleep-wake-like rhythm).

```
  trend ▁▂▄▅▄▂▁▂▄▅▄▂▁▂▄
  => LIMIT CYCLE: never settles; oscillates with period 6 steps
```

### 3. Runaway → a dysregulation spiral (`examples/mind-runaway.pal`)

Positive feedback: fear drives arousal up, and high arousal feeds fear. Each
reinforces the other, so both escalate without bound — the loop has no fixed point
and no cycle.

```
  trend ▁▂▂▃▄▆████        (arousal 2 -> 32, off the top of the chart)
  => RUNAWAY: no fixed point; the loop escalates without bound
```

### 4. The strange loop → the mind rewrites its own law (`examples/mind-strange-loop.pal`)

This is the case Palimpsest expresses most directly. The being carries its own
regulation policy — its set-point — as part of its state. While arousal differs
from the goal the mind regulates toward it; but each time it *reaches* the goal,
the mind rewrites the goal itself, re-opening the gap. The process edits the law
that produces it — a Hofstadter strange loop — descending a staircase of
ever-deeper calm until it hits a floor and reaches a *meta*-fixed-point.

```
  trend ▄▄▃▃▂▂▂▂▁▁▁▁        (a staircase: each time it reaches the goal, the goal drops)
  => SETTLED to a self-consistent fixed point:
       ==  arousal 2   (goal 2)
```

Here the set-point is a parameter of the generating rule, carried in the state and
rewritten by the mind. The fuller version of a strange loop — the mind editing its
entire transition *table*, stored as data — is exactly the data-driven-interpreter
pattern of `examples/self-turing.pal`, and could be built the same way.

The next three environments are more complex: they use bounded and *noisy*
dynamics, which is where the real loop lives.

### 5. Noisy homeostasis → a stable band (`examples/mind-noisy.pal`)

Homeostasis, but every tick a pseudo-random perturbation (from `rng`, seeded by a
value carried in the state) jitters the body. The loop never settles *exactly* —
the RNG stream keeps advancing — yet stays in a stable band around the set-point:
a **bounded** attractor, the stochastic analogue of a fixed point. Because `rng`
is pure, the run is fully reproducible and the file is still a quine.

```
  trend ▆▅▅▆▄▄▂▄▃▄▅▄▃▄▄
  distribution (how often at each arousal):  a band around 5-8
  => BOUNDED: never settles exactly, but stays in a stable region
```

### 6. Bistable + noise → metastable switching (`examples/mind-bistable.pal`)

The richest environment. Two stable moods — low arousal (~2) and high (~8) — are
separated by a barrier. The mind pulls toward the nearer attractor, but random
kicks occasionally shove arousal across the barrier, so the system dwells near one
mood and then *jumps* to the other. This noise-induced switching is a genuinely
new outcome: neither well alone produces it.

```
  trend ▁▁▃▃▅▆▆▆▄▃▃▃▃▆▃▂▁▁▂▂▁▁▁▁▁    (dwells low, jumps to the high well, drops back)
  distribution: bimodal -- clusters low and high
  => BOUNDED: never settles exactly, but stays in a stable region
```

### 7. Saturating control → the will overwhelmed (`examples/mind-saturating.pal`)

The body has a constant upward load; the mind corrects toward a set-point of 4 but
its effort **saturates** at ±1 (a bounded will, using `clamp`/`min`/`max`). A
bounded controller cannot overcome a larger steady load: arousal climbs, one step
at a time, until it pins against the ceiling — the will progressively overwhelmed.
`abs` reports the growing distress. The self is stable, but it is not the self the
mind was aiming for.

```
  trend ▁▂▄▄▅▆▆▇███        (climbs, one step at a time, until pinned at the ceiling)
  => SETTLED to a self-consistent fixed point:
       ============  arousal 12   (ctl 8)
```

The last three are the most complex: a hierarchical self-model, and two coupled
loops.

### 8. Predictive processing → a self-model cohering (`examples/mind-predictive.pal`)

The scientific model of the loop, in miniature (active inference). The state is
`(pp BODY BELIEF PRIOR)`. An external stressor pushes the body up; the mind holds
a *belief* about its own arousal and minimizes prediction error two ways at once —
**perception** moves the belief toward the body, and **action** moves the body
toward the belief — while the belief is also drawn toward a **prior** ("I expect
calm"). The renderer shows two tracks, and you watch them converge: the belief
(10) and body (0) close a prediction error of 10 down to a small residual. It
settles with `err 1` rather than 0, because the prior biases perception — the
mind's picture of itself settles just under the body rather than exactly on it.

```
  o = body   x = belief
  10 |x
   8 | x
   6 |  xoooooo
   5 |   xxxxxx        (belief and body converge; residual err 1)
   2 | o
     +----------> time
  => SETTLED to a self-consistent fixed point:
       body ====== 6   belief ===== 5   err 1
```

### 9. Co-regulation → two loops meeting (`examples/mind-dyad.pal`)

Now the "self" is a pair. Two mind-body loops share a world: Alice's baseline is
calm (3), Bob's anxious (8). Each regulates toward their own baseline *and* is
pulled toward the other's arousal (attunement / contagion). Starting far apart (0
and 10), they converge step by step to a shared compromise and settle — emotional
co-regulation — while each keeps some of their individual baseline, so the gap
narrows but never fully closes.

```
  o = A   x = B
  10 |x
   8 | x
   7 |  xxxxxxx        (Bob down from 10, Alice up from 0)
   4 |  ooooooo
   2 | o
     +----------> time
  => SETTLED to a self-consistent fixed point:
       A ==== 4   B ======= 7   gap 3
```

### 10. Escalation → two loops feeding each other (`examples/mind-dyad-escalation.pal`)

The same coupled structure with the coupling's sign flipped: each is agitated by
the other, more so when the other is more aroused, and neither self-regulates. A
quarrel that feeds on itself — both escalate without bound. The *only* difference
from co-regulation is the sign of the coupling, which is the whole point: whether
a shared loop soothes or inflames is a property of the coupling, not the parts.

```
  o = A   x = B
  10 |   **********   (both climb in lockstep and pin at the ceiling)
   8 |  *
   6 | *
   4 |x
   3 |o
     +--------------> time
  => RUNAWAY: no fixed point; the loop escalates without bound
```

## Exploring further

The outcome is set by the coupling, so the interesting move is to perturb it:
change the set-point or gain in homeostasis (too much gain plus a delay tips it
into the cycle), the thresholds in the oscillator (they set the period and
amplitude), or the feedback sign in the spiral. `verify-mindbody.sh` checks that
each environment still reaches its expected attractor and quines.

These outcomes echo real frameworks worth reading alongside the toy: Hofstadter's
**strange loops** and self-models; Maturana and Varela's **autopoiesis** (a system
that produces the components that produce it); and **predictive processing /
active inference**, where perception and action close exactly this loop through a
self-model. The toy makes the structural skeleton of all three runnable — which is
its only, and real, contribution.
