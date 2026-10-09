# The Palimpsest Tutorial

Palimpsest is a small language where **everything is term rewriting**. You write
rules that turn one shape of term into another, you pick a strategy that decides
where and how often those rules fire, and running a program means rewriting a
term until it stops changing. The same machinery that computes `2 + 2` can
rewrite another program's source file — or its own, which is how a Palimpsest
program becomes a quine.

This tutorial takes you from a first program to writing your own libraries and
transforming files safely. Every snippet here has been run against the
interpreter; you can paste each into a `.pal` file and run it with
`./target/release/palimpsest yourfile.pal`.

## 1. Setup

```sh
cargo build --release
./target/release/palimpsest examples/stdlib_demo.pal   # sanity check
```

A program is a plain text file. Each line is one item: a directive (`#…`), an
`import`, a `rule`, a `strategy`, the `main` subject term, or a command (`run`,
`show`, `rewrite`). Lines starting with `//` are comments. **Every rule,
strategy, and command must fit on a single line** in this implementation.

## 2. Your first program

```
#lang palimpsest
rule greet : (greet ?who) => (hello ?who)
main = (greet world)
run rules
```

Output:

```
run: (greet world)  ==>  (hello world)
```

What happened: `main` is the term we start with. `run rules` normalizes it using
the strategy `rules` (which means "try every defined rule"). The one rule matches
`(greet world)`, binds the variable `?who` to `world`, and rewrites to
`(hello world)`.

## 3. Terms: the only data structure

Every value is a **term**, an S-expression:

- a symbol: `hello`, `+`, `fizzbuzz`
- an integer: `42`, `-7`
- a string: `"hi there"`
- a list: `(hello world)`, `(+ 1 2)`, `(list a b c)`

Lists nest arbitrarily. There is no separate notion of "code" vs "data" — a rule,
a number, and an abstract syntax tree are all just terms.

## 4. Rules

A rule has a name, a left-hand pattern, and a right-hand template:

```
rule NAME : LHS => RHS
```

Pattern variables carry a `?` sigil:

- `?x` is a **term variable** — it matches exactly one subterm.
- `?xs...` is a **sequence variable** — it matches zero or more subterms inside a
  list (think "the rest of the arguments").

Sequence variables make many operations a single rule:

```
#lang palimpsest
rule swap    : (pair ?a ?b) => (pair ?b ?a)
rule flatten : (wrap ?xs...) => (flat ?xs...)
main = (pair 1 2)
show (wrap a b c) with rules
run rules
```

```
show: (wrap a b c)  ==>  (flat a b c)
run: (pair 1 2)  ==>  (pair 2 1)
```

A variable used twice in a pattern must match equal terms (non-linear matching):
`(dup ?x ?x)` matches `(dup a a)` but not `(dup a b)`. This is how the standard
library's `dedup-label` rule collapses two identical labels in a row.

(There is a third, less common sigil, `!x` — a STRICT term variable, covered in
§7's "strictness tip" once there's a reason to want it.)

## 5. Strategies: controlling the rewriting

Rules say *what* may be rewritten. Strategies say *where* and *how often*. This
separation is the heart of the language. The building blocks:

| Strategy | Meaning |
|---|---|
| `id` | always succeed, change nothing |
| `fail` | always fail |
| a rule/strategy name | apply that rule (or named strategy) at the root |
| `rules` | try every defined rule at the root (left to right) |
| `prim` | evaluate a built-in primitive at the root |
| `s1 ; s2` | do `s1`, then `s2` on the result (fails if either fails) |
| `s1 + s2` | try `s1`; if it fails, do `s2` (deterministic choice) |
| `try(s)` | `s + id` — do `s` if you can, otherwise nothing |
| `repeat(s)` | apply `s` until it fails |
| `topdown(s)` / `bottomup(s)` | traverse the whole tree applying `s` |
| `oncetd(s)` / `oncebu(s)` | apply `s` **once**, at the first place it succeeds |
| `innermost(s)` | reduce to normal form, arguments first (call-by-value) |
| `outermost(s)` | `repeat(oncetd(s))` — reduce the outermost redex first |
| `fixpoint(s)` | apply `s` until the term stops changing |
| `all(s)` | apply `s` to every immediate child |

You combine these freely: `innermost(add-zero + add-suc)` means "using the choice
of those two rules, reduce fully, innermost-first."

## 6. Numbers, and why evaluation order matters

Palimpsest has built-in **primitives** on exact numbers, evaluated by the
`prim` strategy when the operands are literal values. Numbers are integers of
any size and exact rationals written `n/d`; a rational whose value is an integer
*is* that integer (`6/3` reads as `2`), so equality is structural:

```
+  -  *                  exact on any numbers: (+ 1/3 1/6) -> 1/2
/  mod                   integer division and remainder
q/                       exact division: (q/ 2 3) -> 2/3
<  <=  >  >=             any numbers -> bool   (the symbols true / false)
=  <>                    equality on numbers, strings, or symbols -> bool
cat                      (string, string) -> string
```

Section 16 covers the remaining numeric primitives (`round-to`, `decimal`,
`isqrt`, ...).

So `(+ (* 2 3) 4)` reduces to `10` under any strategy that includes `prim`:

```
#lang palimpsest
main = (+ (* 2 3) 4)
run innermost(prim)
```

Now the important lesson. Consider a recursive rule guarded by `if`:

```
rule count : (count ?n) => (if (<= ?n 0) done (count (- ?n 1)))
```

Under **innermost** (call-by-value) evaluation this **loops forever**: innermost
reduces arguments before the parent, so it keeps expanding the `(count (- ?n 1))`
branch before the `if` ever gets to collapse it. Under **outermost** (normal
order) it terminates, because the `if` fires at the top and discards the unused
branch before it can grow:

```
show (count 4) with outermost(prim + rules)   ==>  done
show (count 4) with innermost(prim + rules)   ==>  out of fuel!
```

**Rule of thumb:** use `outermost` (or the library's `normalize`) for anything
recursive; use `innermost` only for flat arithmetic where you want speed.

Every run is bounded by **fuel** (`#fuel N`, default 100000): each rule or
primitive application costs one unit. When fuel runs out the run aborts — and,
importantly, if it was a file rewrite, nothing is written. This is the universal
safety backstop against non-termination.

## 7. Using the standard library

Instead of defining arithmetic and lists yourself, import the prelude:

```
#lang palimpsest
import "../lib/prelude.pal"
main = (sum (range 1 100))
run normalize
```

```
run: (sum (range 1 100))  ==>  5050
```

`normalize` (a.k.a. `eval`) is the prelude's normal-order strategy —
`outermost(prim + rules)` — and it is what you almost always want. Importing the
prelude gives you the whole standard library:

- **lists** — `length append reverse map filter foldr foldl sum product member nth
  range take drop concat zip zipwith enumerate replicate last init snoc`,
  predicates `empty? all-of any-of count-if find index-of`, `minimum maximum`,
  and pairs `pair fst snd`
- **logic** — `if and or not xor`
- **arithmetic** — `inc dec square max min abs even odd between`
- **options** — `(some x)` / `none`, with `some? none? with-default map-option or-else`
- **math** — `gcd lcm pow factorial fib sign clamp divides? sum-to`
- **dictionaries** — association maps `(dict (entry k v) ...)` with
  `put get get-or has? keys values size remove`
- **sorting** — `insert sort sorted?`
- **text** — string assembly over `cat`: `join unwords commas surround parens
  brackets quote-str repeat-str`

Import resolution looks first next to your file, then in `$PALIMPSEST_LIB`. From
a file in `examples/`, `import "../lib/prelude.pal"` finds the library; or set
`PALIMPSEST_LIB=/path/to/lib` and write `import "prelude.pal"`.

### Higher-order functions

`map` and `filter` don't take Palimpsest lambdas (there aren't any). Instead they
call an **open application form** that your program fills in with rules:

- `map` and `filter` call `(app f x)`
- `foldr` calls `(app2 f a b)`

So you name a function with a symbol and give it meaning with a rule:

```
#lang palimpsest
#fuel 200000
import "../lib/prelude.pal"
rule app-double : (app double ?n) => (* ?n 2)
rule app-evenp  : (app evenp ?n)  => (even ?n)
main = (map double (filter evenp (range 1 10)))
run normalize
```

```
run: (map double (filter evenp (range 1 10)))  ==>  (list 4 8 12 16 20)
```

This "open recursion by symbol" is the idiomatic way to pass behavior around in a
term-rewriting language.

### Options and dictionaries

Operations that might not return a value use the option type instead of getting
stuck. `find` and dictionary `get` both return `(some v)` or `none`, and
`with-default` unwraps them:

```
show (find evenp (list 1 3 4 7)) with normalize      // ==> (some 4)
show (with-default (get z (dict)) 0) with normalize  // ==> 0
```

Dictionaries are association maps. Here is word-frequency counting — fold a list
into a dictionary of counts (`examples/wordcount.pal`):

```
rule tally      : (tally ?xs) => (tally-into (dict) ?xs)
rule tally-done : (tally-into ?d (list)) => ?d
rule tally-step : (tally-into ?d (list ?x ?xs...)) => (tally-into (put ?x (+ 1 (get-or ?x 0 ?d)) ?d) (list ?xs...))
// (get apple (tally (list apple banana apple cherry apple)))  ==>  (some 3)
```

### A strictness tip: forcing accumulators

Under normal-order evaluation, an accumulator passed along unchanged is *not*
reduced until the very end — which for something like Fibonacci lets the
accumulator grow into a huge unreduced expression. The fix is to force it each
step with a `where` binding, which normalizes the value before the next call.
The library's `fib` does exactly this:

```
rule fib-next : (fib-step false ?n ?a ?b) => (fib-go ?m ?b ?s) where ?m <- (- ?n 1), ?s <- (+ ?a ?b)
```

Because `?s <- (+ ?a ?b)` is evaluated immediately, the running totals stay small
and `fib 40` returns instantly. Reach for `where` bindings whenever you write
accumulator-style recursion.

A related but different tool is the STRICT variable `!x` (in place of `?x`) in
a rule's own left-hand side: where a `where` binding forces a value used on the
*right*-hand side, `!x` forces the *subject* at that position before the rule
even decides whether to match. This matters for rules that dispatch on shape —
`(?xs...)` matches ANY list, with no way to tell "already a value" from "an
unevaluated call to some other rule that happens to also be list-shaped" — see
`README.md`, "Reflection, quotation, and strict evaluation", and `lib/ctmu.pal`
for worked examples (`size`, `subterm?`).

## 8. Writing your own library

A library is just a `.pal` file with rules and strategies — no `main`, no
commands. Here is a tiny string-path library:

```
// lib/paths.pal
#lang palimpsest
rule join2 : (join ?a ?b) => (cat ?a (cat "/" ?b))
rule ext   : (with-ext ?name ?e) => (cat ?name (cat "." ?e))
```

Use it:

```
#lang palimpsest
import "lib/paths.pal"
main = (with-ext (join "src" "main") "pal")
run outermost(prim + rules)
```

```
run: (with-ext (join "src" "main") "pal")  ==>  "src/main.pal"
```

Two things to know about imports:

1. They are **transitive and cycle-safe** — importing `prelude.pal`, which
   imports `list.pal`, which imports `logic.pal`, loads each once.
2. A library's `#caps`, `main`, and commands are **ignored**. Only the root
   program you actually run can execute commands or hold filesystem
   capabilities. A library can give you rules; it can never give itself (or you)
   authority you didn't ask for.

## 9. Rewriting other files, safely

Palimpsest's other half is transforming *source files*. A target file carries its
subject in a `main = …` line; a rewrite program transforms it. The reusable
modernization rules live in `lib/refactor.pal`; a program imports them and points
them at a file:

```
#lang palimpsest
#mode rewrite-then-run
#caps { rewrite: [file "examples/legacy.pal"] }
import "../lib/refactor.pal"
rewrite file "examples/legacy.pal" with modernize
```

Run it two ways:

```sh
palimpsest examples/refactor.pal --dry-run   # shows a diff, writes nothing
palimpsest examples/refactor.pal             # atomic write + snapshot
```

Everything about the write is safe by construction:

- **Capabilities.** The `#caps` header lists exactly which files may be written.
  A program granted only `[file "examples/legacy.pal"]` cannot touch anything
  else; a program granted only `[self]` can rewrite only its own file. Imports
  cannot widen this.
- **Atomic writes.** The new content goes to a temp file in the same directory,
  is flushed, then atomically renamed over the target — the file is never seen
  half-written.
- **The ledger.** Before every write, the previous bytes are snapshotted and the
  write is journaled under `.palimpsest/ledger/`. Nothing is ever lost.
- **Undo.** `palimpsest undo examples/refactor.pal` restores the target from its
  last snapshot.
- **Dry-run.** `--dry-run` computes the result and prints a diff but persists
  nothing at all.

## 10. The self-rewriting quine

Point a rewrite at `self` and the program transforms its own file. If the
transformation leaves the file unchanged, the file is a **fixed point** — and a
program that reproduces its own source is a quine.

`examples/quine.pal` does this non-trivially. Its subject is
`(app quine (quote quine))` and its rule is:

```
rule q : (app ?code (quote ?data)) => (app ?data (quote ?data))
```

Applying `q` rebinds `code := data := quine` and rebuilds the *same* term. The
rule genuinely fires (fuel is consumed), yet the normal form equals the original,
so `rewrite self with fixpoint(q)` writes back byte-for-byte identical content:

```
status : FIXED POINT — file reproduced byte-identically. This is a quine.
```

You can verify it with `sha256sum examples/quine.pal` before and after. This is
the fixed point that Kleene's second recursion theorem guarantees exists; the
companion `examples/quine-converge.pal` shows the same term is an *attractor* —
start from a different term and the rule drives it to the quine.

From here the idea scales up: a program can rewrite its own source into the
*solution* of a problem and only then become a quine. `SELF-REWRITING.md` is a
dedicated tutorial that builds from these basics through Towers of Hanoi, an
N-Queens solver that prints a chess board, a compiler, and a data-driven Turing
machine — each of which renders its answer with the `display` command (see §17) and
the renderers in `lib/render.pal`. `SELF-REFERENCE.md` goes deeper on the theory
(fixed points, attractors, cycles, autograms, fixpoint combinators), and
`puzzles/PUZZLES.md` turns both into graded exercises.

## 11. Conditional rules and local bindings

So far every rule fires whenever its pattern matches. Real algorithms need rules
that fire only under a condition. Add a `where` clause:

```
rule NAME : LHS => RHS where CLAUSE, CLAUSE, ...
```

A clause is either a **guard** (a term that must normalize to `true`) or a
**binding** `?v <- EXPR` (evaluate EXPR, bind the result to `?v` for use in the
right-hand side and later clauses). Guards are themselves evaluated by rewriting,
so they can use primitives and call library functions.

The classic use is two rules with the same left-hand side that dispatch on a
comparison — insertion sort:

```
#lang palimpsest
#fuel 500000
import "../lib/prelude.pal"
rule insert-empty : (insert ?x (list)) => (list ?x)
rule insert-le : (insert ?x (list ?y ?ys...)) => (list ?x ?y ?ys...) where (<= ?x ?y)
rule insert-gt : (insert ?x (list ?y ?ys...)) => (prepend ?y (insert ?x (list ?ys...))) where (> ?x ?y)
rule sort-empty : (sort (list)) => (list)
rule sort-cons  : (sort (list ?x ?ys...)) => (insert ?x (sort (list ?ys...)))
main = (sort (list 5 3 8 1 9 2 7))
run normalize
```

```
run: (sort (list 5 3 8 1 9 2 7))  ==>  (list 1 2 3 5 7 8 9)
```

Bindings let you name intermediate results instead of repeating subexpressions:

```
rule classify : (classify ?n) => (result half ?h rem ?r) where ?h <- (/ ?n 2), ?r <- (mod ?n 2)
// (classify 17) ==> (result half 8 rem 1)
```

Rules can also span multiple lines now — put the `where` clause on its own line if
it reads better. An item continues while its parentheses are open, while it ends
in `=> = <- : + ; ,`, or while the next line begins with `where` / `+` / `;` / `,`.

## 12. Programmable strategies

You can define your own strategy combinators, and they can take strategy
arguments and even recurse. This is what makes the strategy language a real
language rather than a fixed set of built-ins.

```
#lang palimpsest
import "../lib/prelude.pal"
rule dbl : (dbl ?n) => (* ?n 2)
rule neg : (neg ?n) => (- 0 ?n)
rule dec1 : (S ?n) => ?n

strategy simplify(s) = innermost(s + prim)     // parameter s is a strategy
strategy myrepeat(s) = try(s ; myrepeat(s))    // recursion is allowed

main = (nothing)
show (dbl (dbl (dbl 5))) with simplify(dbl)          // ==> 40
show (neg (dbl 21))      with simplify(dbl + neg)    // compound argument ==> -42
show (S (S (S 0)))       with myrepeat(dec1)         // ==> 0
```

Parameters are lexically scoped: when `myrepeat(dec1)` recurses, the `s` inside
resolves to `dec1` at every depth. As always, fuel bounds recursion, so a runaway
strategy fails safely instead of hanging.

## 13. A worked example: a tiny interpreter

Conditional rules, non-linear patterns, and the standard library are enough to
write an interpreter for a small language — integers, arithmetic, variables, and
lexically-scoped `let` — evaluated purely by rewriting. Environments are
association lists `(bind x v (bind y w ... empty))`.

```
import "../lib/prelude.pal"
rule ev-num : (eval ?env (num ?n)) => ?n
rule ev-add : (eval ?env (add ?a ?b)) => (+ (eval ?env ?a) (eval ?env ?b))
rule ev-mul : (eval ?env (mul ?a ?b)) => (* (eval ?env ?a) (eval ?env ?b))
rule ev-var : (eval ?env (var ?x)) => (lookup ?x ?env)
rule ev-let : (eval ?env (let ?x ?e ?body)) => (eval (bind ?x (eval ?env ?e) ?env) ?body)
rule lookup-hit  : (lookup ?x (bind ?x ?v ?rest)) => ?v
rule lookup-miss : (lookup ?x (bind ?y ?v ?rest)) => (lookup ?x ?rest) where (<> ?x ?y)
main = (eval empty (let x (num 5) (let y (num 3) (add (mul (var x) (var y)) (num 1)))))
run normalize
```

```
run: ...  ==>  16
```

The key trick is `lookup-hit`: the variable `?x` appears twice in the pattern, so
it matches only when the bound name equals the name we're looking up (a non-linear
pattern). The miss case recurses, guarded by `(<> ?x ?y)`. The full program is
`examples/interp.pal`.

## 14. Common pitfalls

- **Innermost on recursion loops.** If a recursive program exhausts fuel, switch
  from `innermost`/`eval-strict` to `outermost`/`normalize`.
- **Primitives wait for literals.** `(+ x 3)` with a symbolic `x` stays as-is;
  `prim` only fires when operands are actual numbers. That's intentional — it
  lets you rewrite symbolically and evaluate later.
- **Partial functions get stuck.** `(nth 9 (list a b))` reduces to a leftover
  term rather than erroring. Guard your inputs, or read the stuck term as "no
  result."
- **`rules` tries rules in definition order.** When two rules could match, the
  first one defined wins. Order base cases before recursive ones.
- **Shape-generic rules (and `equal?`/`matches?`) compare exactly what's
  written, not what it evaluates to.** A rule whose pattern is `(?xs...)`
  matches ANY list-shaped subject immediately, including one that's really an
  unevaluated call to some other rule — `(size (some-call 40))` would measure
  the two-element *call*, not whatever 40-element list it actually denotes.
  Force it first with a `where ?v <- EXPR` binding (or, when writing the shape-
  generic rule itself, give it a STRICT `!x` argument instead of `?x` — see
  §7's "strictness tip" and `README.md`). This is not a bug to work around
  once; it's a standing property of comparing terms syntactically, and worth
  checking for whenever a result looks like unreduced source rather than a
  value.
- **A right-hand side can't invent new `?x` vocabulary out of nothing.** It can
  only splice a sequence variable (`?xs...`) that its OWN left-hand side bound.
  Writing `(family ?xs...)` fresh into a right-hand side, with nothing on the
  left-hand side ever binding `xs`, fails with "unbound sequence variable" —
  wrap it as `(verbatim (family ?xs...))` to produce it as literal, unsplit
  data instead (see `README.md`, "Reflection, quotation, and strict
  evaluation").
- **A label that is also a function name gets evaluated.** In a result term
  such as `(report (syntax-changes 18))`, `syntax-changes` is not inert if a
  rule defines it: the strategy rewrites the label as a call. Use label names
  that no rule mentions (`(changes 18)`).

## 15. Analyzing rule systems and games

Two libraries turn Palimpsest on its own subject matter: rule systems, and agents whose choices interact.

`lib/ars.pal` treats a rule set as *data*, `(rules (rule LHS RHS) ...)`, and asks the classic questions of rewriting theory about it: unification, critical pairs, local confluence. The textbook non-confluent system is two rules that rewrite the same term two ways:

```
show (locally-confluent? (rules (rule a b) (rule a c))) with solve    // ==> false
```

`lib/games.pal` (which imports `ars.pal`) does the same for finite games. A game is any symbol for which you supply two kinds of rules: the strategy lists and the payoffs. Here is the Prisoner's Dilemma:

```
#lang palimpsest
#mode run-only
#fuel 1000000
import "../lib/games.pal"
strategy solve = outermost(prim + rules)
rule sets : (strategy-sets pd) => (list (list c d) (list c d))
rule cc : (payoff pd ?i (prof c c)) => 3
rule dd : (payoff pd ?i (prof d d)) => 1
rule cd : (payoff pd ?i (prof c d)) => (if (= ?i 0) 0 5)
rule dc : (payoff pd ?i (prof d c)) => (if (= ?i 0) 5 0)
main = (nothing)
show (pure-nash pd) with solve                          // ==> (list (prof d d))
show (pareto-dominators pd (prof d d)) with solve       // ==> (list (prof c c))
show (improvement-rules pd) with solve
show (locally-confluent? (improvement-rules pd)) with solve   // ==> true
```

The third line prints the game's *better-response relation*, one rewrite rule per strict improvement a player can make:

```
(rules (rule (prof c c) (prof d c)) (rule (prof c c) (prof c d))
       (rule (prof c d) (prof d d)) (rule (prof d c) (prof d d)))
```

That relation is an ordinary rule set, so the confluence checker applies to it directly. Its normal forms are the pure Nash equilibria. It terminates exactly when independent improvement always stops. It is confluent when the equilibrium reached does not depend on who moves first. The Prisoner's Dilemma is confluent, because every path leads to mutual defection. Many games are not; `TELIC-GAMES.md` works through them.

Two habits from §7 and §14 matter here. Force a value with `where ?v <- EXPR` before a rule dispatches on its shape. And remember that one deterministic run returns one answer even when the rules allow several. To see the alternatives, ask for all of them: `reachable-nash` lists every equilibrium reachable under any order of moves, and `unjoinable-pairs` lists the conflicting critical pairs. `TELIC-GAMES.md` §9 documents the library function by function, with a traced execution.

## 16. Exact numbers, named results, and watching a run

**Exact numbers.** Because every number is exact, a computation that would be
approximate in floating point is a theorem here: `(= (+ 1/10 2/10) 3/10)` is
`true`. The numeric primitives are `+ - * q/` (exact), `/ mod` (integer),
`num den floor ceil expt isqrt number? abs min max`, and two for controlling
size and presentation:

- `(round-to X K)` rounds X to the nearest multiple of 1/K (half up). Long
  simulations use it once per step to keep denominators bounded; rounding
  happens only where you write it.
- `(decimal X D)` is a display string with D decimal places:
  `(decimal 2/3 4)` is `"0.6667"`.

**Naming a result.** `let $NAME = TERM with S` normalizes a term once and
substitutes the result for `$NAME` in every later `show`, `display` and
`assert`, so an expensive computation used by several commands runs once:

```
let $rows = (simulate 60) with eval
display (table $rows) with eval
assert (all-positive? $rows) with eval
```

**Watching a run.** `--trace N` prints the first N rewrite steps as
`rule: redex => contractum`; steps taken inside a guard, a `where` binding or a
strict argument are indented. `examples/me-tour.pal` is a single economic
feedback loop small enough to read this way:

```
./target/release/palimpsest examples/me-tour.pal --trace 22
```

The trace shows exact arithmetic (a wage share of `29/35`), the loop closing
through the state (profit in one period becomes capital in the next), and the
duplication hazard of normal order: `(min 100 (q/ 270 3))` rewrites to an `if`
that mentions `(q/ 270 3)` twice, and the trace shows it computed twice. That
is why the libraries' entry points use strict `!x` variables (see the strictness
tip in §7).

**Making long runs faster.** `#memo` (or `--memo`) remembers subterms already
proven normal, so the outermost redex search skips them, and remembers the
normal form of every argument forced at a strict position. Results and the
order of reduction are unchanged; only the fuel count drops, which is why it is
opt-in. `--stats` reports how often the memo was used.

## 17. Quick reference

Directives: `#lang`, `#mode {rewriting-as-running | rewrite-then-run}`, `#fuel N`,
`#caps { rewrite: [self, file "p"] }`, `#rebind main`, `#memo`.

Items (may span multiple lines): `import "p"`,
`rule N : L => R [where G, ?v <- E, ...]`, `strategy N = S`,
`strategy N(p, ...) = S`, `main = T`.

Commands: `run S`, `show T with S`, `display T with S` (prints for a human — a
string result is shown verbatim, and `main` in `T` is the subject term),
`rewrite {self | file "p"} with S`, `assert T with S` (PASS iff `true`; a FAIL
exits non-zero), `let $NAME = T with S`; `transition N : L => R` (a rule usable
only by name from a strategy). CLI: `undo` subcommand; flags `--dry-run`,
`--fuel N`, `--stats`, `--memo`, `--trace N`.

Strategies: `id fail prim rules NAME NAME(args...)  s;s  s+s  try repeat topdown
bottomup oncetd oncebu innermost outermost fixpoint all`.

Primitives: `+ - * / mod  q/  num  den  floor  ceil  round-to  expt  isqrt
number?  decimal  abs  min  max  < <= > >=  = <>  cat  str<  str  sym
explode  implode  rng  padl  padr  matches?  match-witness`, and the record
operations `@ set@ put@ add@ has@ del@ keys@ sum@`. (`sym` is the
inverse of `str`; `explode`/`implode` convert between a string and a list of
one-character strings; `str<` compares strings lexicographically; `rng` is a
deterministic splitmix64 hash of a seed, for reproducible pseudo-randomness;
`matches?`/`match-witness` decide/witness pattern-instance membership,
`exists sigma. sigma(pattern) = subject`, reifying the interpreter's own
matcher as data.)

Pattern variables: `?x` (term), `?xs...` (sequence, zero or more, non-linear if
repeated), `!x` (STRICT term — forces the subject at that top-level position to
its normal form before matching). Right-hand sides: `(verbatim T)` produces `T`
with no substitution at all, for authoring fresh `?x`-containing data.

Standard library (`import "../lib/prelude.pal"`): strategies `normalize eval
eval-strict`. Logic `if and or not xor` and structural `equal?`; arithmetic `inc
dec square max min abs between even odd`; lists `length append prepend reverse map
filter foldr foldl sum product member nth range take drop concat zip zipwith
enumerate replicate last init snoc empty? all-of any-of count-if find index-of
minimum maximum pair fst snd`; options `some? none? with-default map-option
or-else`; math `gcd lcm pow factorial fib sign clamp divides? sum-to`; dicts `put
get get-or has? keys values size remove`; sorting `insert sort sorted?`; text `join
unwords commas surround parens brackets quote-str repeat-str str-length
str-reverse`.

Renderers for the `display` command (`import "../lib/render.pal"`): `shw` (any
term → its canonical string), `chess` (an N-Queens solution → a board), `asm`
(three-address code), `binview`, `moves-view`, `set-view`, `text-view`.

Analysis libraries (§15): `ars.pal` — `unify`, `critical-pairs`,
`locally-confluent?`, `unjoinable-pairs`, `normalize` over a rule set given as
data, and finite-algebra checks (`is-semilattice?`, `fold-op`); `games.pal` —
`pure-nash`, `weakly-dominant?`, `pareto-dominators`, `mixed-2x2`,
`improvement-rules`, `terminating?`, `reachable-nash`, `run-schedule`,
`is-exact-potential?`, `ms-violations`, join games and metagames.

For self-referential and self-rewriting programs, see `SELF-REFERENCE.md` and
`SELF-REWRITING.md`; for a sustained application of the whole language —
self-rewriting dynamical-systems simulations that graph their own trajectories —
see `MIND-BODY.md` and the step-by-step `MINDBODY-TUTORIAL.md`. Graded exercises
live in `puzzles/PUZZLES.md`. For rule systems and games as objects of study,
see §15, and for the CTMU studies built on them, the "CTMU studies" section of
`README.md`. For a large application of exact numbers, games and verified
feedback loops, see `MATERIALIST-ECONOMY.md` and its paper
`MATERIALIST-ECONOMY-PAPER.md`.

Happy rewriting.
