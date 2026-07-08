# Palimpsest Permutation Puzzles

A graded series of twenty-two puzzles. The first fourteen train one specific
skill: **seeing how a row of symbols moves when you rewrite it.** The last eight
turn the language on itself — **fixed points, cycles, self-description, and
quines** — programs that transform into themselves. Every solution is a
Palimpsest program — a rule (or a few) plus a strategy that drives it. The point
is not the code; it is learning to *picture* the transformation before you write
it, then watch the language carry it out exactly.

Term rewriting is the ideal gym for this. A pattern like `(row ?a ?mid... ?z)`
literally draws a frame around a row of symbols: `?a` is the first, `?z` is the
last, and `?mid...` is "everything in between, held as one piece." When you write
the right-hand side, you are choosing where each piece lands. Learn to see the
frame and the pieces, and permutations stop being abstract.

## How to play

1. Read the puzzle and look at the **before → after** picture until you can see
   the motion in your head — which symbol goes where.
2. Write the rule(s) in a `.pal` file using the starter shown.
3. Run it: `./target/release/palimpsest yourfile.pal`.
4. Compare with the worked answer in `solutions/`, and check everything at once
   with `./puzzles/check.sh` (run from the project root).

A quick refresher on the two kinds of pattern variable, because the whole series
rests on them:

- `?x` — a **single** symbol (or subterm). One slot.
- `?xs...` — a **sequence** variable: a whole run of symbols, held as one piece.
  On the right-hand side it splices back in wherever you place it.

Two helper rules are *given* whenever a puzzle needs them — treat them as basic
moves you already own:

```
rule prepend : (prepend ?y (list ?ys...)) => (list ?y ?ys...)   // push one onto the front
rule append  : (append (list ?xs...) (list ?ys...)) => (list ?xs... ?ys...)   // join two rows
```

A note on **strategies**, since different puzzles need different drivers:

- Some transforms happen in a **single application** — you run the rule once
  (`run rulename`). Reversing a fixed triple is one move.
- Recursive transforms are run to a **normal form** with `run innermost(rules)`
  (reduce fully) or `run normalize` (the library's normal-order strategy).
- A transform that repeats a local edit until nothing more applies uses
  `run repeat(oncetd(prim + rules))` — "keep finding one spot to rewrite."

---

# Tier I — Fixed rearrangements

Small rows of a known length. Name every symbol; write them back in a new order.
This tier builds the core habit: *a variable is a place, and the right-hand side
is where that place's symbol goes.*

## Puzzle 1 — Swap

```
before:  (swap x y)
after:   (swap y x)
```

Two symbols trade places. See `?a` and `?b` cross over.

Starter:
```
rule swap : (swap ?a ?b) => ???
main = (swap x y)
run swap
```

<details><summary>Hint</summary>Put <code>?b</code> where <code>?a</code> was and
<code>?a</code> where <code>?b</code> was.</details>

Solution: `solutions/01-swap.pal`.

## Puzzle 2 — Reverse a triple

```
before:  (tri 1 2 3)
after:   (tri 3 2 1)
```

Name all three, then mirror them. The middle stays put; the ends swap.

```
rule tri : (tri ?a ?b ?c) => ???
main = (tri 1 2 3)
run tri
```

Solution: `solutions/02-reverse-triple.pal`.

## Puzzle 3 — Cycle four left

```
before:  (q a b c d)
after:   (q b c d a)
```

Everyone shifts one seat to the left; the person at the front walks to the back.
See the whole row slide.

```
rule cycle : (q ?a ?b ?c ?d) => ???
main = (q a b c d)
run cycle
```

Solution: `solutions/03-cycle-four.pal`.

---

# Tier II — Framing with sequence variables

Now the rows are *any* length. You can no longer name every symbol, so you name
the ones you care about and hold the rest as a single `?...` piece. Learn to see
the frame (the named ends) and the filling (the sequence).

## Puzzle 4 — Swap the ends

```
before:  (row a b c d e)
after:   (row e b c d a)
```

Only the two outermost symbols move; everything between them stays frozen. The
picture: grab the first and last, leave the middle block untouched.

```
rule ends : (row ?a ?mid... ?z) => ???
main = (row a b c d e)
run ends
```

<details><summary>Hint</summary>The pattern <code>(row ?a ?mid... ?z)</code> names
the first (<code>?a</code>), the last (<code>?z</code>), and the block between
(<code>?mid...</code>). Write them back with the ends swapped and
<code>?mid...</code> unchanged.</details>

Solution: `solutions/04-swap-ends.pal`.

## Puzzle 5 — Rotate left (any length)

```
before:  (rotl (list a b c d))
after:   (list b c d a)
```

The head of the line walks all the way to the back. One rule handles any length.

```
rule rotl : (rotl (list ?x ?xs...)) => ???
main = (rotl (list a b c d))
run rotl
```

<details><summary>Hint</summary><code>?x</code> is the head, <code>?xs...</code> is
the tail. Put the tail first, then splice <code>?x</code> on the end.</details>

Solution: `solutions/05-rotate-left.pal`.

## Puzzle 6 — Rotate right (any length)

```
before:  (rotr (list a b c d))
after:   (list d a b c)
```

The mirror image of Puzzle 5: the *last* symbol jumps to the front. The trick is
that a sequence variable can come *first* in the pattern, letting you name the
final element.

```
rule rotr : (rotr (list ?xs... ?x)) => ???
main = (rotr (list a b c d))
run rotr
```

Solution: `solutions/06-rotate-right.pal`.

## Puzzle 7 — Pluck a symbol to the front

```
before:  (pluck (list a b star c d))
after:   (list star a b c d)
```

Wherever `star` sits, lift it out and move it to the front; everything else keeps
its order. Two sequence variables surround the thing you are hunting for.

```
rule pluck : (pluck (list ?xs... star ?ys...)) => ???
main = (pluck (list a b star c d))
run pluck
```

<details><summary>Hint</summary><code>(list ?xs... star ?ys...)</code> means "some
stuff, then <code>star</code>, then more stuff." The matcher finds where
<code>star</code> is. Rebuild as <code>star</code> followed by both
blocks.</details>

Solution: `solutions/07-pluck-to-front.pal`.

---

# Tier III — Recursive transformations

These can't be done in a single sweep of one pattern; you peel off a piece, do
something, and recurse on the rest. Picture the row shrinking by a chunk each
step, and the answer being built back up.

## Puzzle 8 — Reverse a list

```
before:  (rev (list a b c d e))
after:   (list e d c b a)
```

Peel off the head, reverse what's left, and stick the head on the *end*. You are
given `append`.

```
rule rev-0 : (rev (list)) => ???
rule rev-n : (rev (list ?x ?xs...)) => ???
main = (rev (list a b c d e))
run innermost(rules)
```

<details><summary>Hint</summary>Empty reverses to empty. For a non-empty list,
<code>(append (rev tail) (list head))</code>.</details>

Solution: `solutions/08-reverse.pal`.

## Puzzle 9 — Riffle shuffle

```
before:  (riffle (list a b c) (list 1 2 3))
after:   (list a 1 b 2 c 3)
```

Interleave two rows, one symbol from each in turn — a perfect riffle. You are
given `prepend`. Handle the moment one pile runs out.

```
rule riffle-l : (riffle (list) ?ys) => ???
rule riffle-r : (riffle ?xs (list)) => ???
rule riffle-n : (riffle (list ?x ?xs...) (list ?y ?ys...)) => ???
main = (riffle (list a b c) (list 1 2 3))
run innermost(rules)
```

<details><summary>Hint</summary>Take the head of each list, emit them in order
(<code>prepend ?x (prepend ?y ...)</code>), and recurse on the two
tails.</details>

Solution: `solutions/09-riffle.pal`.

## Puzzle 10 — Unriffle (deal into two)

```
before:  (unriffle (list a 1 b 2 c 3))
after:   (pair (list a b c) (list 1 2 3))
```

The inverse of the riffle: deal a single row alternately into two piles. This one
is harder — you take *two* symbols at a time and must push each onto the correct
result pile, which the recursive call hands back.

```
rule unriffle-0 : (unriffle (list)) => (pair (list) (list))
rule unriffle-1 : (unriffle (list ?x)) => (pair (list ?x) (list))
rule unriffle-n : (unriffle (list ?x ?y ?rest...)) => (glue ?x ?y (unriffle (list ?rest...)))
rule glue : (glue ?x ?y (pair (list ?as...) (list ?bs...))) => ???
main = (unriffle (list a 1 b 2 c 3))
run innermost(rules)
```

<details><summary>Hint</summary><code>glue</code> receives the two piles from the
recursive call and must push <code>?x</code> onto the first and <code>?y</code>
onto the second.</details>

Solution: `solutions/10-unriffle.pal`.

## Puzzle 11 — Swap every adjacent pair

```
before:  (swapadj (list a b c d e f))
after:   (list b a d c f e)
```

Walk the row two at a time, swapping each neighboring pair. See the row as pairs:
`(a b)(c d)(e f)` → `(b a)(d c)(f e)`.

```
rule sa-0 : (swapadj (list)) => (list)
rule sa-1 : (swapadj (list ?x)) => (list ?x)
rule sa-n : (swapadj (list ?a ?b ?rest...)) => ???
main = (swapadj (list a b c d e f))
run innermost(rules)
```

Solution: `solutions/11-swap-adjacent.pal`.

---

# Tier IV — Comparison-driven & permutations

The capstones. Here the *data* decides the permutation.

## Puzzle 12 — Bubble sort in one rule ★

```
before:  (list 5 3 8 1 9 2 7 4 6)
after:   (list 1 2 3 4 5 6 7 8 9)
```

The whole of bubble sort is a single idea: *if two adjacent symbols are out of
order, swap them; repeat until none are.* Write exactly that — one rule with a
guard — and let a repeating strategy do the rest.

```
rule bubble : (list ?xs... ?a ?b ?ys...) => (list ?xs... ?b ?a ?ys...) where (> ?a ?b)
main = (list 5 3 8 1 9 2 7 4 6)
run repeat(oncetd(prim + rules))
```

The pattern `(list ?xs... ?a ?b ?ys...)` frames *any* adjacent pair `?a ?b`
anywhere in the row (with blocks on either side). The guard `where (> ?a ?b)`
keeps only the pairs that are out of order — and if the first pair the matcher
tries is already in order, it searches for another. `repeat(oncetd(...))` keeps
finding one such pair and swapping it until the row is sorted. Watch the biggest
numbers bubble rightward.

Solution: `solutions/12-bubble-sort.pal`.

## Puzzle 13 — Pancake flip

```
before:  (flip 3 (list a b c d e))
after:   (list c b a d e)
```

Reverse just the first *k* symbols, like flipping the top few pancakes with a
spatula; leave the rest. This is the atomic move of pancake sorting. (Import the
prelude for `take`, `drop`, `reverse`, `append`.)

```
import "../../lib/prelude.pal"
rule flip : (flip ?k ?xs) => ???
main = (flip 3 (list a b c d e))
run normalize
```

<details><summary>Hint</summary>Reverse the first <code>k</code> and append the
rest: <code>(append (reverse (take ?k ?xs)) (drop ?k ?xs))</code>. Try
<code>(flip 5 ...)</code> too — flipping the whole stack reverses it.</details>

Solution: `solutions/13-pancake-flip.pal`.

## Puzzle 14 — Apply a permutation

```
before:  (gather (idx 3 1 2) (vals x y z))
after:   (out z x y)
```

Here the permutation is *itself data*: a list of positions saying where to look.
`(idx 3 1 2)` means "take the 3rd value, then the 1st, then the 2nd." Gather the
value at each index, in order. This is the most abstract step — a permutation as a
first-class object you apply to a row. (Import the prelude for `nth`.)

```
import "../../lib/prelude.pal"
rule pick     : (pick ?i (vals ?xs...)) => (nth (- ?i 1) (list ?xs...))
rule gather-0 : (gather (idx) ?v) => (out)
rule gather-n : (gather (idx ?i ?is...) ?v) => (out-cons (pick ?i ?v) (gather (idx ?is...) ?v))
rule out-cons : (out-cons ?x (out ?xs...)) => ???
main = (gather (idx 3 1 2) (vals x y z))
run normalize
```

<details><summary>Hint</summary><code>pick</code> reads one value by 1-based index
(the library's <code>nth</code> is 0-based, hence <code>(- ?i 1)</code>).
<code>gather</code> walks the index list; <code>out-cons</code> pushes each picked
value onto the front of the growing result. Then try composing two permutations,
or inverting one.</details>

Solution: `solutions/14-apply-permutation.pal`.

---

# Tier V — Self-reference (hard)

The final tier turns the language on itself. A rewrite rule usually transforms a
term into a *different* term; here you build terms that transform into
*themselves*, programs that reason about their own structure, and — the
capstone — a program that rewrites its own source file. This is the deep end:
fixed points, cycles, self-description, and quines. Kleene's second recursion
theorem is the background music — a program can always be written that has access
to its own text.

A term is a **fixed point** of a rule when the rule rewrites it to itself. That is
the whole idea of a quine, shrunk to a single term. Learn to *see* the loop: where
does the output feed back into the input?

## Puzzle 15 — The fixed point (a term quine)

```
rule q : (app ?code (quote ?data)) => (app ?data (quote ?data))

before:  (app quine (quote quine))
after:   (app quine (quote quine))     ← unchanged!
```

The rule copies the `data` slot over the `code` slot. Find the one term it leaves
untouched. See why: if `code` already equals `data`, copying changes nothing.

```
rule q : (app ?code (quote ?data)) => (app ?data (quote ?data))
main = (app quine (quote quine))
run q
```

<details><summary>Hint</summary>The term is its own fixed point when the code and
the quoted data are the same symbol. That symbol, quoted, <em>is</em> the
program's description of itself.</details>

Start it instead from `(app anything (quote quine))`, and one step still lands on
`(app quine (quote quine))`: the quine is not merely a fixed point but an
**attractor** — a whole neighbourhood of terms collapses onto it.

Solution: `solutions/15-term-quine.pal`.

## Puzzle 16 — The reproducible random stream ★

```
main = (gen 1 6)   →   (stream 32 78 27 57 31 33)    ← looks random
run again          →   FIXED POINT (byte-identical)   ← yet it is a quine
```

A self-rewriting program that expands a seed into a fixed-length stream of
pseudo-random numbers, then holds still. The surprise: `rng` is a *pure*,
deterministic hash of its seed, so the "random" output is completely fixed. The
first run generates the stream and writes it back into `main`; the second run finds
nothing left to expand and reproduces the file byte-for-byte. Randomness you can
reproduce — and therefore a quine.

```
#mode rewrite-then-run
#caps { rewrite: [self] }
rule gen-0 : (gen ?seed 0) => (stream)
rule gen-n : (gen ?seed ?k) => (push (mod ?ns 100) (gen ?ns (- ?k 1))) where (> ?k 0), ?ns <- (rng ?seed)
rule push : (push ?x (stream ?xs...)) => (stream ?x ?xs...)
strategy solve = outermost(prim + rules)
main = (gen 1 6)
rewrite self with solve
```

<details><summary>Hint</summary>Each step emits <code>(mod ?ns 100)</code> and
advances the seed with the binding <code>?ns &lt;- (rng ?seed)</code>, so the whole
stream is a deterministic function of the starting seed. Once <code>(gen ...)</code>
has fully expanded there is nothing left to rewrite, so the resulting
<code>(stream ...)</code> is a fixed point.</details>

```sh
cp solutions/16-random-stream.pal /tmp/q.pal
palimpsest /tmp/q.pal      # run 1: WROTE — a deterministic "random" stream
palimpsest /tmp/q.pal      # run 2: FIXED POINT — a quine
```

Solution: `solutions/16-random-stream.pal`.

## Puzzle 17 — The self-tallying histogram ★★

```
main = (roll 7 18)   →   (series 2 3 6 1 3 3 2 2 5 4 3 1 1 2 2 6 6 2)   ← 18 dice
display              →   a bar chart of how often each face came up
run again            →   FIXED POINT (byte-identical)
```

Three new tools at once. Roll a fixed number of dice from a seed (deterministic,
via `rng`), rewrite the file so `main` holds the roll — a quine, because the roll
is reproducible — and *display* the distribution as a bar chart, using the
`histogram` tool from the visualization library `lib/chart.pal`. The program
computes a random-looking dataset, freezes it into itself, and draws its own
summary.

```
#mode rewrite-then-run
#caps { rewrite: [self] }
import "../../lib/chart.pal"
rule roll-0 : (roll ?seed 0) => (series)
rule roll-n : (roll ?seed ?k) => (rc (+ 1 (mod ?ns 6)) (roll ?ns (- ?k 1))) where (> ?k 0), ?ns <- (rng ?seed)
rule rc : (rc ?x (series ?xs...)) => (series ?x ?xs...)
strategy solve = outermost(prim + rules)
main = (roll 7 18)
rewrite self with solve
display (histogram main 6) with solve
```

The dice land in a `(series ...)` — exactly the shape `histogram` expects — so
`(histogram main 6)` tallies faces 0..6 and draws a bar per face. On the second run
`main` is already the series, so the file holds still while still drawing its chart.

<details><summary>Hint</summary>Each roll is <code>(+ 1 (mod ?ns 6))</code> with the
seed advanced by <code>?ns &lt;- (rng ?seed)</code>. Accumulate the faces into a
<code>(series ...)</code> with a small <code>rc</code> ("roll-cons") helper — the
same push-onto-the-front trick as Puzzle 16.</details>

```sh
# this solution imports ../../lib/chart.pal, so keep it beside the library:
cp solutions/17-dice-histogram.pal solutions/q17.pal
palimpsest solutions/q17.pal   # run 1: WROTE, and draws the histogram
palimpsest solutions/q17.pal   # run 2: FIXED POINT — a quine
rm solutions/q17.pal
```

Solution: `solutions/17-dice-histogram.pal`.

## Puzzle 18 — The oscillator (period 2)

```
run osc         :  (o x y) → (o y x)          (one step: swapped)
run (osc ; osc) :  (o x y) → (o x y)          (two steps: back home)
```

Not every self-returning term is a fixed point. Build one that comes back to
itself after *exactly two* rewrites — a 2-cycle, the smallest non-trivial orbit.
This is the seed of a quine *relay* (A becomes B becomes A).

```
rule osc : (o ?a ?b) => (o ?b ?a)
main = (o x y)
run (osc ; osc)
```

<details><summary>Hint</summary>A swap is its own inverse. Once returns the
halfway state; twice returns the start.</details>

Solution: `solutions/18-oscillator.pal`.

## Puzzle 19 — Idempotence

```
T(x)      = (list 1 2 3)
T(T(x))   = (list 1 2 3)     ← the same; a fixed point on the second pass
```

A transformation `T` is **idempotent** when `T(T(x)) = T(x)` — doing it twice is
the same as doing it once. Sorting is the classic example: the second sort finds
nothing to do. Show it by sorting, then sorting again, and landing on a fixed
point.

```
rule bubble : (list ?xs... ?a ?b ?ys...) => (list ?xs... ?b ?a ?ys...) where (> ?a ?b)
strategy sort = repeat(oncetd(prim + rules))
main = (list 3 1 2)
run (sort ; sort)
```

Solution: `solutions/19-idempotence.pal`.

## Puzzle 20 — The autogram ★

```
before:  (list counts 0 a b)
after:   (list counts 4 a b)     ← "this list has 4 elements" — and it does
```

A self-describing sentence: a list that truthfully states its own length. The
twist that makes it genuinely self-referential is that the *number is itself one
of the things it counts* — change the number and the count changes too. Write a
`recount` rule that replaces the number with the actual length, but only while the
claim is wrong, and let it settle at the self-consistent fixed point.

```
rule length-0 : (length (list)) => 0
rule length-n : (length (list ?x ?xs...)) => (+ 1 (length (list ?xs...)))
rule recount : (list counts ?n ?rest...) => (list counts ?len ?rest...) where ?len <- (length (list counts ?n ?rest...)), (<> ?n ?len)
strategy solve = outermost(prim + rules)
main = (list counts 0 a b)
run solve
```

<details><summary>Hint</summary>The guard <code>(&lt;&gt; ?n ?len)</code> stops the
rewrite once the stated number equals the real length — otherwise it would keep
"recounting" the same true statement forever. Count the whole term, including the
number slot: <code>(list counts 4 a b)</code> has four elements.</details>

Solution: `solutions/20-autogram.pal`.

## Puzzle 21 — Recursion from self-application ★

```
before:  (app (fix fac) 5)
after:   120
```

Compute factorial with a step function that **never mentions itself**. All the
recursion comes from one rule — the fixpoint combinator `fix f = f (fix f)` —
which hands the step function a copy of its own recursive self as `?self`. This is
the Y-combinator idea in rewriting form.

```
rule if-t : (if true ?t ?e) => ?t
rule if-f : (if false ?t ?e) => ?e
rule fix : (fix ?f) => (app ?f (fix ?f))
rule facstep  : (app fac ?self) => (facfun ?self)
rule facapply : (app (facfun ?self) ?n) => (if (<= ?n 0) 1 (* ?n (app ?self (- ?n 1))))
strategy solve = outermost(prim + rules)
main = (app (fix fac) 5)
run solve
```

<details><summary>Hint</summary><code>(fix fac)</code> unfolds to
<code>(app fac (fix fac))</code>, which becomes a function that, given <code>n</code>,
calls <code>?self</code> — another <code>(fix fac)</code> — on <code>n-1</code>.
Normal-order evaluation only unfolds <code>fix</code> as deep as the recursion
actually needs.</details>

Solution: `solutions/21-fixpoint-combinator.pal`.

## Puzzle 22 — The self-sorting quine ★★

```
run 1:  main = (list 5 3 8 1 9 2 7 4 6)   →   WROTE (file rewrites itself)
        main = (list 1 2 3 4 5 6 7 8 9)
run 2:  →   FIXED POINT — byte-identical. A quine.
```

The capstone unites the whole book. A program whose `main` is an unsorted list
and whose only rule is the one-rule bubble sort from Puzzle 12 — but this time it
rewrites *its own source file*. The first run sorts the list and writes it back;
from then on there is nothing left to swap, so the file reproduces itself exactly.
The program **sorts itself**, and the quine is the certificate that the sort is
finished. (Runs on its own file, so try it on a copy.)

```
#mode rewrite-then-run
#caps { rewrite: [self] }
rule bubble : (list ?xs... ?a ?b ?ys...) => (list ?xs... ?b ?a ?ys...) where (> ?a ?b)
strategy solve = repeat(oncetd(prim + rules))
main = (list 5 3 8 1 9 2 7 4 6)
rewrite self with solve
```

```sh
cp solutions/22-self-sorting-quine.pal /tmp/q.pal
palimpsest /tmp/q.pal      # run 1: WROTE — sorted its own source
palimpsest /tmp/q.pal      # run 2: FIXED POINT — a quine
```

Solution: `solutions/22-self-sorting-quine.pal`.

---

# Where to go next

Once these feel natural, invent your own from the same parts:

- **Rotate by k** — apply `rotl` k times (a counter and recursion).
- **Pancake sort** — repeatedly `flip` the largest unsorted pancake into place.
- **De-duplicate adjacent** — `(list ?xs... ?a ?a ?ys...) => (list ?xs... ?a ?ys...)`
  under `repeat` (a non-linear pattern plus search — the same backtracking that
  powers Puzzle 12).
- **Compose / invert permutations** — treat `(idx ...)` as an object and build an
  algebra on it.

And for the self-reference tier, some genuinely open challenges (no solutions
provided — you are on your own):

- **A quine relay.** Extend Puzzle 18: build terms A and B, each of which rewrites
  into the other, so the pair cycles with period two. Then make each carry a
  payload, so the relay also transports data.
- **A self-solving quine of your own.** Like Puzzle 22, but pick a different
  computation — reverse a list, compute a factorial, evaluate an expression — so
  the file rewrites itself into the answer and then holds still.
- **A richer autogram.** Make a sentence that counts occurrences of a specific
  symbol *within itself* (not just its length), so the numeral and the thing it
  counts genuinely interact.
- **A meta-circular twist.** Write a tiny evaluator (Puzzle-13 style), then feed it
  a representation of a program that uses the evaluator — an interpreter running
  code that is itself about interpreting.

The recurring insight across the whole series: **a pattern is a picture of a row,
sequence variables are the pieces you slide around, and a guard lets the matcher
*search* for the arrangement you mean.** The self-reference tier adds one more:
**a fixed point is a term that feeds its own output back as its input** — learn to
see that loop, and quines stop being magic.
