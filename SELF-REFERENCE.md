# Self-Referential Coding in Palimpsest

Most programs transform *other* things: input to output, one file to another. This
tutorial is about programs that transform *themselves* — terms that rewrite to
themselves, statements that describe themselves, functions that recurse through
copies of themselves, and, at the top, programs that rewrite their own source
file. Palimpsest is unusually good at this, because rewriting to a **fixed point**
is its native idea, and a program that rewrites its own file to a fixed point is,
by definition, a **quine**.

One mental model carries the whole tutorial:

> A fixed point is a thing that feeds its own output back in as its input, and
> comes out unchanged.

Everything here — quines, attractors, cycles, autograms, self-solvers — is that
one loop, seen at different scales. The background theorem is Kleene's second
recursion theorem: for any transformation you can define, a self-referential
program that survives it is guaranteed to exist. We won't prove it; we'll build
its instances.

Every example below has been run against the interpreter and shows its real
output. To watch the term-level ones all at once:

```sh
./target/release/palimpsest examples/self-reference-demo.pal
```

## 1. Fixed points: the atom of self-reference

A term `t` is a **fixed point** of a strategy `S` when `S(t) = t` — running `S`
leaves it exactly as it was. The most trivial case: the `id` strategy leaves
*everything* unchanged, so every term is a fixed point of `id`.

```
show (tree (leaf) (leaf)) with id      ==>  (tree (leaf) (leaf))
```

That's not interesting yet, because `id` does nothing. Self-reference gets
interesting when a rule that genuinely *does* something nevertheless leaves a
particular term alone. Take a rule that grows a seed:

```
rule grow : (seed) => (sprout)

show (seed)   with grow          ==>  (sprout)     ← changed: not a fixed point
show (sprout) with try(grow)     ==>  (sprout)     ← unchanged: a fixed point
```

`(sprout)` is a fixed point of `grow` because `grow` has nothing to do to it — it
is already a *normal form*. Fixed points are exactly the terms a rule can't touch.
The art of self-referential coding is engineering a term that a **non-trivial**
rule can't touch — because it already is what the rule would make it.

## 2. The term quine

Here is the smallest genuinely self-referential term. The rule copies a term's
"data" slot over its "code" slot:

```
rule q : (app ?code (quote ?data)) => (app ?data (quote ?data))
```

Now find a term this leaves unchanged. The trick is to make the code and the
quoted data *already agree*:

```
show (app quine (quote quine)) with fixpoint(q)    ==>  (app quine (quote quine))
```

Watch the mechanism: `q` matches with `?code = quine` and `?data = quine`, and
rebuilds `(app quine (quote quine))` — the same term. The quoted `quine` is the
program's *description of itself*; applying the rule *uses* that description to
rebuild the whole. Code that acts on a quoted copy of itself to reproduce itself
is precisely a quine. This is Kleene's theorem in one line: the program has access
to its own text (the `quote`) and uses it to reconstruct itself.

## 3. Attractors: falling into the fixed point

A fixed point is even more interesting if nearby terms *flow into* it. Start with
a term that is **not** the quine — its code slot is garbage — and apply the same
rule:

```
show (app anything (quote quine)) with fixpoint(q)   ==>  (app quine (quote quine))
```

One step copies `quine` over `anything`, and now we're at the fixed point forever.
The quine is an **attractor**: a whole neighbourhood of terms collapses onto it.
(This is why a quine is robust — corrupt the code slot and the next run repairs
it from the quoted description.)

## 4. Build your own self-reproducer

The self-reproducing *shape* is portable — it isn't about the words `app` or
`quote`. Rename everything and it still works, as long as one slot is overwritten
by a copy of another:

```
rule mirror : (self ?code (describes ?data)) => (self ?data (describes ?data))

show (self me (describes me)) with mirror     ==>  (self me (describes me))
```

If you can build this with your own constructors, you understand the pattern
rather than the example: **a fixed point of "copy my description over my body" is
any term whose body already matches its description.**

## 5. Cycles: self-reference that returns later

Not every self-returning term is a fixed point. Some come back to themselves only
after several steps. A swap is its own inverse, so it has period 2:

```
rule flip : (pair ?a ?b) => (pair ?b ?a)

show (pair x y) with flip            ==>  (pair y x)     ← one step: not home
show (pair x y) with (flip ; flip)   ==>  (pair x y)     ← two steps: home again
```

A three-way rotation returns after exactly three:

```
rule rot3 : (cyc ?a ?b ?c) => (cyc ?b ?c ?a)

show (cyc 1 2 3) with (rot3 ; rot3 ; rot3)   ==>  (cyc 1 2 3)
```

A fixed point is just a cycle of period 1. Period-2 cycles are the seed of a
**quine relay** — two programs that print each other — and cycles in general are
how self-reference expresses *oscillation* instead of *stasis*.

## 6. Idempotence: fixed points of whole transformations

Scale up from terms to transformations. A transformation `T` is **idempotent**
when `T(T(x)) = T(x)`: doing it twice is the same as doing it once, because after
the first pass the result is already a fixed point. Sorting is the classic case —
the one-rule bubble sort from the puzzles, driven to completion:

```
rule bubble : (list ?xs... ?a ?b ?ys...) => (list ?xs... ?b ?a ?ys...) where (> ?a ?b)
strategy sort = repeat(oncetd(prim + rules))

show (list 3 1 2)       with sort            ==>  (list 1 2 3)
show (list 5 2 4 1 3)   with (sort ; sort)   ==>  (list 1 2 3 4 5)
```

`sort ; sort` gives the same answer as a single `sort`: the second pass finds a
fixed point immediately. Idempotence is self-reference at the level of *behaviour*
— the output is a fixed point of the very transformation that produced it.

## 7. Self-description: a term that talks about itself

Now the term refers not to its own *structure* but to its own *content*. We want a
list that truthfully states how many elements it has — and the twist that makes it
genuinely self-referential is that **the number is itself one of the elements it
counts.** Change the number and the count changes with it.

We need ordinary length, and a `recount` rule that fixes the stated number — but
only while it is *wrong* (the guard `(<> ?n ?len)` stops it once the statement is
true, so it doesn't "recount" a correct statement forever):

```
rule length-0 : (length (list)) => 0
rule length-n : (length (list ?x ?xs...)) => (+ 1 (length (list ?xs...)))
rule recount  : (list counts ?n ?rest...) => (list counts ?len ?rest...)
                  where ?len <- (length (list counts ?n ?rest...)), (<> ?n ?len)
strategy solve = outermost(prim + rules)

show (list counts 0 a b)         with solve   ==>  (list counts 4 a b)
show (list counts 9 a b c d e)   with solve   ==>  (list counts 7 a b c d e)
```

`(list counts 4 a b)` has exactly four elements — `counts`, `4`, `a`, `b` — and
says so. It is a tiny **autogram**: a self-descriptive statement that has made
itself true. The fixed point is the moment the sentence stops lying about itself.

## 8. Recursion from self-application

Here is self-reference doing real work. We'll compute factorial with a step
function that **never mentions its own name.** All the recursion comes from a
single combinator — the fixpoint combinator, `fix f = f (fix f)`:

```
rule if-t : (if true ?t ?e) => ?t
rule if-f : (if false ?t ?e) => ?e
rule fix  : (fix ?f) => (app ?f (fix ?f))

rule facstep  : (app fac ?self) => (facfun ?self)
rule facapply : (app (facfun ?self) ?n) => (if (<= ?n 0) 1 (* ?n (app ?self (- ?n 1))))
strategy solve = outermost(prim + rules)

show (app (fix fac) 5) with solve    ==>  120
```

The step function `fac` receives its own future self as `?self` and calls it for
the sub-problem `(n-1)`. `fix` supplies that self by unfolding `(fix fac)` into
`(app fac (fix fac))` on demand — normal-order evaluation only unfolds it as deep
as the recursion actually goes, so it terminates. The very same combinator runs
*any* recursion; here it is summing `1..n`:

```
rule sumstep  : (app summ ?self) => (sumfun ?self)
rule sumapply : (app (sumfun ?self) ?n) => (if (<= ?n 0) 0 (+ ?n (app ?self (- ?n 1))))

show (app (fix summ) 10) with solve   ==>  55
```

This is the Y-combinator idea: recursion is not a primitive, it is what you get
when a function is handed a copy of itself.

## 9. Programs that rewrite themselves

Everything so far lived inside a single run. Now the self-reference reaches the
*file*. The command `rewrite self with S` normalizes the program's `main` term
with `S` and writes the result back into this very file. If the new `main` equals
the old one, the file is unchanged — reproduced byte-for-byte. That is a quine.

The trivial quine (`examples/quine.pal`) is `main = (app quine (quote quine))`
plus the rule `q` from §2. Running it once:

```
  status  : FIXED POINT — file reproduced byte-identically (3bfb5f83e8f4dbd6). This is a quine.
```

To feel the difference between *self-modifying* and *quine*, here is a program
that changes itself a little each run and only becomes a quine once it settles.
It bumps a counter until it reaches a target, then stops
(`examples/counter-quine.pal`):

```
rule tick : (count ?n) => (count (+ ?n 1)) where (< ?n 3)
strategy step = try(tick ; outermost(prim))
main = (count 0)
rewrite self with step
```

Run it repeatedly on a scratch copy and watch its own source climb, then freeze:

```sh
cp examples/counter-quine.pal /tmp/cq.pal
palimpsest /tmp/cq.pal   # run 1: WROTE      main = (count 1)
palimpsest /tmp/cq.pal   # run 2: WROTE      main = (count 2)
palimpsest /tmp/cq.pal   # run 3: WROTE      main = (count 3)
palimpsest /tmp/cq.pal   # run 4: FIXED POINT — a quine   main = (count 3)
```

While it is counting, each run rewrites the file (`WROTE`) — self-modifying but
not a quine. When the guard `(< ?n 3)` finally fails, `main` stops changing and
the file reproduces itself. **Reaching the fixed point is the same event as
becoming a quine.**

## 10. Self-modifying computation: quines that solve problems

Combine the last two ideas and you get the most striking object in the language: a
program whose act of reproducing itself *is* a computation. Its `main` starts as an
unsolved problem; the self-rewrite drives it to the answer; and once the answer is
reached there is nothing left to rewrite, so the program becomes a quine holding
its own solution.

`examples/hanoi-quine.pal` solves the Towers of Hanoi this way. Run 1 expands the
problem `(hanoi 3 a c b)` into its full optimal move sequence and writes it back:

```
  result  : (moves (move a c) (move a b) (move c b) (move a c) (move b a) (move b c) (move a c))
  status  : WROTE (atomic rename), snapshot a1e682b5f788f67f -> a52666e121936727
```

Run 2 finds the solution already in place and reproduces the file exactly:

```
  status  : FIXED POINT — file reproduced byte-identically (a52666e121936727). This is a quine.
```

Puzzle 22 (`puzzles/solutions/22-self-sorting-quine.pal`) does the same with
sorting: a program whose `main` is an unsorted list rewrites itself into sorted
order and then holds still. In every case the pattern is identical and profound:

> The program is a quine **exactly when** the problem is solved. The fixed point
> is a *certificate* that the computation has finished.

Computation, here, is convergence to a self-reproducing fixed point.

## 11. Doing this safely

Self-modifying code sounds dangerous — a program editing its own source could
destroy it. Palimpsest makes it safe by construction, which is what lets you
experiment freely:

- **Capabilities.** A program can only rewrite files its `#caps` header lists.
  `#caps { rewrite: [self] }` permits self-modification and nothing else; without
  the grant, the write is refused.
- **Atomic writes.** The new text is written to a temp file and atomically renamed
  over the original — the file is never seen half-written.
- **Reversibility.** Every write snapshots the previous bytes first, so any
  self-modification can be undone:

```sh
cp examples/counter-quine.pal /tmp/uq.pal
palimpsest /tmp/uq.pal          # main = (count 0)  ->  (count 1)
palimpsest undo /tmp/uq.pal     # restored /tmp/uq.pal from its previous snapshot
                                # main = (count 1)  ->  (count 0)
```

So a self-rewrite is a *transaction*: gated, atomic, and reversible. You can point
a program at its own source with confidence.

## 12. The whole idea, in one loop

Every section was the same loop at a different scale:

- a **term** that rebuilds itself under a rule (§2–4),
- a **cycle** that returns to itself after k steps (§5),
- a **transformation** whose output is its own fixed point (§6),
- a **statement** that makes itself true (§7),
- a **function** that recurses through copies of itself (§8),
- a **file** that reproduces itself (§9), possibly after computing something (§10).

In each, output feeds back as input and comes out unchanged. Kleene's theorem
promises such fixed points always exist; Palimpsest's job is to let you write them
down and — because self-modification is transactional — run them without fear. Once
you can see the loop, self-reference stops being a paradox and becomes a tool.

To explore further, the `puzzles/PUZZLES.md` "Tier V — Self-reference" section
turns each of these into a challenge to solve yourself, and ends with open
problems: a quine relay, a self-solving quine of your own design, a richer
autogram, and a meta-circular interpreter. And for these ideas applied at
length — self-rewriting programs that settle into attractors, cycle, or run away,
and graph their own trajectories — see `MIND-BODY.md` and `MINDBODY-TUTORIAL.md`.
