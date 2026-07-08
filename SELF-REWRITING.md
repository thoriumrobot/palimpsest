# Self-Rewriting Coding in Palimpsest

Most programs read input and write output. A **self-rewriting** program does
something stranger: it edits *its own source file*. In Palimpsest this is the
whole point of the language. A program is a set of rewrite rules; running it
means normalizing a term; and when a program rewrites its own source to a form
that no longer changes, the file has reproduced itself — it is a **quine**.

That gives a single, surprising idea that this tutorial builds toward:

> A self-rewriting program *computes by editing itself*. Its source starts as a
> problem; each run rewrites it closer to the answer; and when the answer is
> reached there is nothing left to rewrite, so the program becomes a quine that
> holds its own solution. **Reaching the fixed point and finishing the
> computation are the same event.**

We start with a few small examples to learn the language, build the smallest
self-rewriting program, learn the `display` command for showing results
readably, and then walk through every complex self-rewriting program in the
distribution — Towers of Hanoi, the N-Queens solver (which prints a chess board),
a compiler, two string/term transforms, and finally a data-driven Turing machine —
each of which renders its own answer.

Everything below has been run against the interpreter and shows its real output.
The small examples of Part 1 are collected in `examples/rewriting-basics.pal`; the
complex programs are the files named in each section.

---

## Part 1 — The language in a few small examples

A Palimpsest program is made of **terms**, **rules**, and **strategies**.

**Terms** are S-expressions: atoms (`foo`, `42`, `"a string"`) and parenthesized
lists (`(pair a b)`, `(list 1 2 3)`). That's the entire data model — code and data
are both terms.

**Rules** rewrite one term into another. A rule has a name, a left-hand pattern,
and a right-hand replacement:

```
rule not-t : (not true) => false
rule not-f : (not false) => true
```

Patterns contain **variables**: `?x` matches one term, and `?xs...` matches a
whole *sequence* of terms. That is enough to write recursion over lists:

```
rule rev-0 : (reverse (list)) => (list)
rule rev-n : (reverse (list ?x ?xs...)) => (append (reverse (list ?xs...)) ?x)
rule append : (append (list ?ys...) ?z) => (list ?ys... ?z)
```

**Strategies** decide where and how often to apply rules. The everyday one is
"keep applying rules and built-in operations anywhere until nothing changes,"
which we'll call `solve`:

```
strategy solve = outermost(prim + rules)
```

Here `rules` means "any of my rules," `prim` means "any built-in operation" (`+`,
`*`, `<`, `cat`, and so on — see Part 3), `+` between them means "try the first,
else the second," and `outermost(...)` means "repeat to a fixed point, outermost
position first." The command `show TERM with STRATEGY` normalizes a term and
prints it:

```
show (not true)                     with solve   ==>  false
show (+ 21 21)                      with prim     ==>  42
show (reverse (list a b c d))       with solve   ==>  (list d c b a)
```

Rules can also carry a **guard** — a `where` condition that must hold for the rule
to fire. This "keep only the elements greater than 2" filter uses two guarded
rules that split on the comparison:

```
rule big-keep : (only-big (list ?x ?xs...)) => (cons ?x (only-big (list ?xs...))) where (> ?x 2)
rule big-drop : (only-big (list ?x ?xs...)) => (only-big (list ?xs...))            where (<= ?x 2)
rule big-0    : (only-big (list)) => (list)
```

```
show (only-big (list 1 5 2 8 3)) with solve   ==>  (list 5 8 3)
```

That is the whole language in miniature: pattern-match a term, rewrite it,
repeat. Everything that follows is built from exactly these parts.

---

## Part 2 — A program that rewrites itself

To make a program edit its own file we add three things:

- a `main = TERM` line — the one line the program is allowed to rewrite;
- the directive `#mode rewrite-then-run`;
- a capability grant `#caps { rewrite: [self] }` — permission to modify its own
  file, and nothing else;
- and a command `rewrite self with STRATEGY`, which normalizes `main` and writes
  the result back into this file.

Here is the smallest instructive one, `examples/counter-quine.pal`. It bumps a
counter until it reaches a target, then stops:

```
#lang palimpsest
#mode rewrite-then-run
#caps { rewrite: [self] }
rule tick : (count ?n) => (count (+ ?n 1)) where (< ?n 3)
strategy step = try(tick ; outermost(prim))
main = (count 0)
rewrite self with step
```

Run it several times on a scratch copy and watch its own source line climb, then
freeze:

```sh
cp examples/counter-quine.pal /tmp/cq.pal
palimpsest /tmp/cq.pal   # run 1: WROTE        main = (count 1)
palimpsest /tmp/cq.pal   # run 2: WROTE        main = (count 2)
palimpsest /tmp/cq.pal   # run 3: WROTE        main = (count 3)
palimpsest /tmp/cq.pal   # run 4: FIXED POINT — a quine   main = (count 3)
```

Each run prints one of two statuses. **`WROTE`** means the file changed — the
program modified itself. **`FIXED POINT`** means normalizing `main` produced
exactly what was already there, so the file reproduced itself byte-for-byte: it is
now a **quine**. The guard `(< ?n 3)` is what stops the climb; once it fails,
`tick` no longer fires, `main` stops changing, and *reaching that fixed point is
the same moment the file becomes a quine*.

This is safe to experiment with because self-modification is a transaction. The
`#caps` grant means a program can only touch files it was explicitly allowed to;
the new text is written to a temp file and atomically renamed over the original,
so the file is never seen half-written; and every write snapshots the previous
bytes first, so any self-rewrite can be undone:

```sh
palimpsest undo /tmp/cq.pal    # rolls the file back to its previous contents
```

Everything in the rest of this tutorial is this same machine — `main` starts as a
problem, `rewrite self` drives it to an answer, and the quine certifies the answer
is final. What changes is only how interesting the computation in the middle is.

---

## Part 3 — Showing the answer: the `display` command

The rewritten `main` is a term, and a term can be hard to read. Compare two ways
of printing the same computed result. `show` prints the **canonical term**, so a
multi-line string comes out escaped onto one line:

```
show (tally (votes (v alice 12) (v bob 7) (v carol 20))) with solve
  ==>  "results:\n  alice: 12\n  bob: 7\n  carol: 20\n"
```

`display` prints the result **for a human**: when the result is a string it is
shown verbatim, with real line breaks. It also lets the symbol `main` stand for
the program's subject term, so you can render whatever `main` currently is:

```
display (tally main) with solve
```
```
display:
results:
  alice: 12
  bob: 7
  carol: 20
```

(The `tally` renderer above is just a few ordinary rules that build a string with
`cat` and `str`; nothing built-in knows about votes.)

So the recipe for a readable self-rewriting program is: solve into `main` with
`rewrite self`, and render `main` with `display`. The renderings used below —
chess boards, assembly listings, move lists — are themselves written in
Palimpsest, in the library `lib/render.pal`. Two are worth knowing by name:

- `shw` turns *any* term into its canonical string (a pretty-printer written as
  rewrite rules), and
- `chess` turns an N-Queens solution into a board.

With that, we can look at the real programs. Each one both solves itself into a
quine and displays its answer.

---

## Part 4 — Towers of Hanoi: a self-solving quine

Hanoi is the gentlest "real" example because the solution is a single recursive
expansion — no search, no backtracking. The classic recurrence "move n-1 disks
aside, move the big disk, move the n-1 back" is two rewrite rules (`?f`, `?t`, `?v`
are the *from*, *to*, and *via* pegs):

```
rule hanoi-0 : (hanoi 0 ?f ?t ?v) => (moves)
rule hanoi-n : (hanoi ?n ?f ?t ?v) =>
                 (seq (hanoi (- ?n 1) ?f ?v ?t)
                      (move ?f ?t)
                      (hanoi (- ?n 1) ?v ?t ?f))
                 where (> ?n 0)
```

`seq` flattens the two sub-solutions and the middle move into one `(moves ...)`
list:

```
rule seq-flatten : (seq (moves ?as...) ?m (moves ?bs...)) => (moves ?as... ?m ?bs...)
```

With `main = (hanoi 3 a c b)`, the first run rewrites the problem into its
full solution and writes it back:

```
result  : (moves (move a c) (move a b) (move c b) (move a c) (move b a) (move b c) (move a c))
status  : WROTE (atomic rename), snapshot 5695062ff2c5fc2d -> 801fc16dc7b15c0b
```

The second run finds the solution already present and reproduces the file exactly
— `FIXED POINT`, a quine. And the program renders the moves for a human with
`display (moves-view main) with solve`, where `moves-view` numbers each step:

```
1. a -> c
2. a -> b
3. c -> b
4. a -> c
5. b -> a
6. b -> c
7. a -> c
```

Seven moves — the optimal `2³ − 1` — computed by a program rewriting its own
source. This is the template for everything that follows: `examples/hanoi-quine.pal`
is just `main`, the rules, `rewrite self with solve`, and `display (moves-view main)`.

---

## Part 5 — N-Queens: backtracking search, and a chess board

Placing eight queens so none attacks another is a genuine search: you try a
column, and if the rest can't be completed you must *back up* and try another. The
whole search is an abstract machine made of rewrite rules
(`examples/queens.pal` / `examples/queens-quine.pal`).

A partial solution is `(cols c_row … c_1)`, the columns chosen so far, newest row
first. The driver tries each candidate column in the current row; the backtracking
lives in one pair of rules:

```
rule place-done : (place ?row ?placed ?n) => (found ?placed) where (> ?row ?n)
rule pick-yes   : (pick true ?row ?placed ?n ?c ?rest) =>
                    (after (place (+ ?row 1) (cols-add ?c ?placed) ?n) ?row ?placed ?n ?rest)
rule after-nope : (after nope ?row ?placed ?n ?rest)   => (try ?row ?placed ?n ?rest)   // deeper search failed → backtrack
rule after-found: (after (found ?sol) ?row ?placed ?n ?rest) => (found ?sol)            // deeper search won → done
```

The trick is `after`. Because the strategy reduces the inner `(place …)` first,
`after` waits to see how the deeper search turned out: if it comes back `nope`,
the machine tries the next column in this row (that *is* the backtrack); if it
comes back `(found …)`, the answer propagates all the way up. A safety check
(`safe?`) rejects a column that shares a file or diagonal with any placed queen.

With `main = (nqueens 8)`, one self-rewrite runs the entire search and writes the
solution into the file:

```
result  : (found (cols 4 2 7 3 6 8 5 1))
```

and the next run is a byte-identical quine. That column list is hard to read, so
the program renders it as a **text chess board** with `display (chess main) with
solve`:

```
 8 . . . Q . . . . 
 7 . Q . . . . . . 
 6 . . . . . . Q . 
 5 . . Q . . . . . 
 4 . . . . . Q . . 
 3 . . . . . . . Q 
 2 . . . . Q . . . 
 1 Q . . . . . . . 
   1 2 3 4 5 6 7 8 
```

Ranks run 8 (top) to 1 (bottom), files 1–8 below; `Q` is a queen, `.` an empty
square. This is the classic first solution, and `examples/queens.pal`
independently verifies it (no two queens attack) — it prints `true`.

The `chess` renderer is itself just rewrite rules: it walks the solution
`(found (cols ...))` rank by rank, and for each rank builds a row string of `. `
and `Q ` cells with `cat`, joining the rows with newlines. Nothing about chess is
built into the interpreter; the board is produced entirely in the language, and
the `display` command is what lets those embedded newlines print as an actual
grid instead of an escaped one-liner.

---

## Part 6 — A self-rewriting compiler

`examples/self-compile.pal` compiles an arithmetic expression into **three-address
code** — the flat "one operation per line, into a fresh temporary" form that real
compilers use. Flattening needs to invent fresh temporary names `t0, t1, …`, which
is what the `sym` primitive is for: `(sym (cat "t" (str k)))` turns the string
`"t0"` into the symbol `t0`.

The flattener threads a counter through the sub-expressions and emits one
instruction per operation:

```
rule flat-bin : (flat ?k (bin ?o ?a ?b)) => (seqA ?o ?b (flat ?k ?a))
rule emit : (emit ?o ?opa ?opb ?k ?code) =>
              (out (+ ?k 1)
                   (snoc ?code (:= (sym (cat "t" (str ?k))) (bin ?o ?opa ?opb)))
                   (var (sym (cat "t" (str ?k)))))
```

With `main = (compile (bin + (bin * (var a) (var b)) (bin * (var c) (var d))))` —
that is, `(a*b) + (c*d)` — the self-rewrite produces the compiled program and, via
`display (asm main) with solve`, prints it as a listing:

```
t0 := a * b
t1 := c * d
t2 := t0 + t1
return t2
```

The two multiplications become `t0` and `t1`, their sum becomes `t2`, and the
program returns `t2` — a correct linearization, written into the compiler's own
source and then held as a quine.

---

## Part 7 — Sorting text: strings become lists

The next programs work on strings and on arbitrary terms, which needs a few more
primitives — and it is cleaner to meet them one at a time before the program that
uses them all at once. `examples/self-sort-text.pal` introduces three: `explode`
turns a string into a list of one-character strings, `implode` turns such a list
back into a string, and `str<` compares strings lexicographically. Together they
let text be processed with ordinary list rules.

`main` holds a sentence; the self-rewrite explodes it into characters,
insertion-sorts them with `str<`, and imploses the result back into its own
source. Rendered with `display (text-view main) with solve`:

```
"   bcefhiknooqrtuwx"
```

The characters of "the quick brown fox" in order — three spaces first, then the
letters. Because the result is a plain string it round-trips through the file, so
the next run is a quine.

---

## Part 8 — Deduplicating: comparing whole terms

`examples/self-dedup.pal` introduces the last primitive we need: structural
`equal?`, which compares two *entire* terms for equality (it is defined in the
library with a single non-linear rule — `(equal? ?x ?x) => true` matches only when
both arguments are the same term). `main` holds a list with duplicate compound
values; the self-rewrite removes every later copy of each element and, via
`display (set-view main) with solve`, prints the result as a bulleted set — using
the generic `shw` printer from Part 3 to render each element:

```
set of 3:
  - (pt 1 2)
  - (rgb 255 0 0)
  - (pt 3 4)
```

With `explode`/`implode` (Part 7) and `equal?` (here) in hand, we can build the
most ambitious program in the collection.

---

## Part 9 — A self-rewriting Turing machine (the capstone)

`examples/self-turing.pal` brings the pieces together: a Turing machine whose
transition table is ordinary **data**, not hard-coded rules. That makes it a tiny
*interpreter* that edits itself, and it uses exactly the primitives from the last
two parts — `explode`/`implode` to move between a string and a tape, and
structural `equal?` to compare machine states.

The transition table is a list of entries `(e state symbol write move next)`, and
the machine looks up the current `(state, symbol)` by **non-linear matching** — a
pattern in which the same variable appears twice matches only when the two
positions are equal:

```
rule look-hit  : (look ?st ?sy (table (e ?st ?sy ?w ?m ?ns) ?rest...)) => (act ?w ?m ?ns)
rule look-miss : (look ?st ?sy (table ?e ?rest...)) => (look ?st ?sy (table ?rest...))
```

`look-hit` fires only when the queried `?st`/`?sy` are identical to an entry's;
otherwise `look-miss` drops that entry and tries the next. The machine here adds 1
to a binary number: it `explode`s the input string onto a tape, runs to the
`halt` state, and `implode`s the tape back into a string. With
`main = (increment "1011")`, the self-rewrite computes `"1100"`, and
`display (binview main) with solve` shows it with its decimal value:

```
binary 1100  =  12 (decimal)
```

`1011` is 11, and 11 + 1 = 12 = `1100`. A data-driven interpreter that runs to a
halt and rewrites its own source into the result is about as far as self-rewriting
goes — and it is assembled entirely from the pieces built up in the earlier parts.

---

## Part 10 — The shape of every self-rewriting program

Look back and the same skeleton appears every time:

```
#mode rewrite-then-run
#caps { rewrite: [self] }
<rules that compute the answer>
strategy solve = outermost(prim + rules)
main = <a problem>
rewrite self with solve            # run 1 solves into main (WROTE); run 2+ is a quine
display (<render> main) with solve # print the answer for a human
```

- **`main` is a problem** — `(hanoi 3 a c b)`, `(nqueens 8)`, `(increment "1011")`.
- **`rewrite self` runs the computation** by normalizing `main` and writing the
  result back. The first run changes the file (`WROTE`); once the answer is in
  place there is nothing left to rewrite, so the file reproduces itself
  (`FIXED POINT`) — a quine.
- **The quine is the certificate** that the computation is finished: the program
  is a quine *exactly when* the problem is solved.
- **`display` renders the answer** through a renderer written in the language, so
  a raw solution term becomes a chess board, an assembly listing, or a set.

The tutorial walked these in increasing order of ambition — a recursive expansion
(Hanoi), a backtracking search (N-Queens), a compiler pass (`sym`), two
string/term transforms that each introduce a primitive (sort with
`explode`/`implode`/`str<`, dedup with `equal?`), and finally the data-driven
interpreter that combines them (the Turing machine) — but the outer machine never
changed. That outer machine is the language's defining idea: *computation as a
program editing itself toward a fixed point.*

To go deeper on the self-reference ideas themselves (fixed points, attractors,
cycles, autograms, fixpoint combinators), see `SELF-REFERENCE.md`; to practice,
`puzzles/PUZZLES.md` turns them into graded challenges. To watch all of these run
at once, `./run_demo.sh` ends with the Hanoi, N-Queens, and rendered-output
sections, and `verify-self-rewriting.sh` checks that each program solves, renders,
and quines. For a sustained application of self-rewriting — ten dynamical-systems
"mind↔body loop" programs that each rewrite into their classified trajectory and
graph it — see `MIND-BODY.md` and the step-by-step `MINDBODY-TUTORIAL.md`.
