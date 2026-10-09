# Palimpsest — a safe self-rewriting language (reference interpreter)

Palimpsest is a rewriting-based language: a program is a set of rewrite rules,
execution is normalization, and a program that rewrites its *own* source file to
a fixed point is, by construction, a **quine**. The interpreter is written in
**Rust** — the toolchain the design chose, because the language's defining hazard
is *irreversible file mutation*, which Rust's ownership model plus atomic
write-then-rename and a capability-checked write path contain best.

This tree contains the interpreter, a **standard library written in Palimpsest**
(including result renderers, a text-visualization library, a small
abstract-rewriting-systems toolkit for unification and confluence checking, and
a finite-games library), runnable examples — among them ten **mind↔body loop**
simulations that rewrite themselves into their own classified trajectory and
graph it — a graded puzzle book (`puzzles/PUZZLES.md`), and three groups of
documents.

*Guides:* a general walkthrough (`TUTORIAL.md`), a tour of self-rewriting
programs (`SELF-REWRITING.md`), a tour of self-referential coding
(`SELF-REFERENCE.md`), a reference on the mind↔body simulations
(`MIND-BODY.md`) and a step-by-step tutorial on them (`MINDBODY-TUTORIAL.md`).

*Studies of the CTMU* (Langan's Cognitive-Theoretic Model of the Universe), each
taking one mechanism of the theory, giving it a precise meaning in Palimpsest's
term language, and checking it by machine (see "CTMU studies" below):
the containment model (`CTMU.md`) and its non-subsumption proof
(`NONSUBSUMPTION.md`); a confluence test of telic recursion
(`TELIC-CONFLUENCE.md`); the semilattice characterization of convergent merges
(`SEMILATTICE-GRAMMAR.md`); a game-theoretic analysis of independent telors
and of the CTMU's global stage (`TELIC-GAMES.md`); and a comparison of SCSPL
with the internal processing of large language models (`LOGOS-SCSPL.md`).

*Studies in political economy* (see "Economics studies" below): the economy of
the board game *Hegemony* as a self-rewriting program (`HEGEMONY-ECONOMY.md`),
and an exact model of a materialist political economy — value, money, class
games, political survival and three regimes, with every feedback loop checked
edge by edge — set against published data (`MATERIALIST-ECONOMY.md`, written up
as the paper `MATERIALIST-ECONOMY-PAPER.md`).

## Build & run

```sh
cargo build --release
cargo test --release          # 44 unit tests
./run_demo.sh                 # full tour: core, quines, refactor, safety, stdlib,
                              #   the N-Queens chess board, and rendered outputs
./puzzles/check.sh            # 22 permutation & self-reference puzzles
./verify-self-reference.sh    # 19 examples from SELF-REFERENCE.md
./verify-self-rewriting.sh    # 6 complex self-rewriting programs (solve, render, quine)
./verify-mindbody.sh          # 10 mind<->body loop environments (attractors + quine)
./verify-ctmu.sh              # the CTMU containment model (3 self-rewriting proofs)
./verify-telic.sh             # confluence test of CTMU's telic recursion
./verify-semilattice.sh       # semilattice characterization of convergent merges
./verify-games.sh             # game theory of independent telors (~50 s)
python3 crosscheck/games_crosscheck.py  # independent Python re-derivation of TELIC-GAMES.md
./verify-logos.sh             # SCSPL versus language-model processing (~7 s)
python3 crosscheck/logos_crosscheck.py  # independent Python re-derivation of LOGOS-SCSPL.md
./verify-hegemony.sh          # the economy of the board game Hegemony (~3 min)
python3 crosscheck/hegemony_crosscheck.py  # independent Python re-derivation of HEGEMONY-ECONOMY.md
./verify-materialist.sh       # the materialist economy: value, distribution, class games,
                              #   political survival, three regimes, feedback loops, dialectics,
                              #   checks against the reference works and empirical data,
                              #   thresholds and inflection points (~4 min; includes
                              #   crosscheck/materialist_crosscheck.py)
```

Run a program:

```sh
./target/release/palimpsest examples/stdlib_demo.pal
./target/release/palimpsest examples/fizzbuzz.pal
./target/release/palimpsest examples/refactor.pal --dry-run
./target/release/palimpsest examples/quine.pal
./target/release/palimpsest examples/mind-homeostasis.pal   # a mind<->body loop, graphed
./target/release/palimpsest examples/telor-games-join.pal   # equilibria of telor overlap games
./target/release/palimpsest examples/me-tour.pal --trace 22 # one economic feedback loop, step by step
./target/release/palimpsest undo examples/refactor.pal      # roll back last write
```

Or run any of them in the browser: see "Run it in the browser" below.

## Run it in the browser

`index.html` at the repository root is a complete Palimpsest playground that
runs in the browser with [Pyodide](https://pyodide.org/): pick any example,
puzzle solution or library file, edit it, and run it with the same options as
the command line (`--dry-run`, `--memo`, `--stats`, `--trace N`, `--fuel N`).
Self-rewriting programs rewrite their file in a virtual file system, and
**Undo** restores the previous version from the ledger.

- **Publish it with GitHub Pages:** Settings → Pages → *Deploy from a branch*,
  branch `main` (or the branch holding this tree), folder `/ (root)`. The page
  is then at `https://<user>.github.io/<repo>/`. `.nojekyll` makes Pages serve
  every file unchanged.
- **Locally:** `python3 -m http.server` in the repository root, then open
  `http://localhost:8000/`. (Opened straight from disk, the page cannot fetch
  the `.pal` files.)
- **The engine** is `web/palimpsest.py`, a line-by-line Python port of the Rust
  interpreter (`src/*.rs`). It prints the same output as the native binary,
  fuel counts included; `python3 web/test_parity.py` checks this program by
  program (all 88 examples and puzzle solutions are identical). It is also a
  command-line interpreter in its own right:
  `python3 web/palimpsest.py examples/quine.pal --dry-run`.
- **Speed:** about 8× slower than the Rust binary under CPython and about 15×
  in the browser. Small programs run instantly; the large studies take minutes,
  and the page shows each program's native run time as a guide.
- **Rebuild** after changing the engine or adding programs:
  `python3 web/build.py` embeds `web/palimpsest.py` and a manifest of the
  programs into `web/index.template.html` and writes `index.html`.

## What's new since the bare interpreter

Three interpreter features were added specifically to make **libraries** and
practical programming possible:

1. **Imports** — `import "path.pal"` merges another file's rules and strategies.
   Imports are transitive and cycle-safe. Crucially, an imported library's
   directives, `main`, commands, and **capabilities are ignored** — only the
   root program can run commands or grant filesystem access, so a library can
   never widen a program's authority.
2. **Native primitives** — evaluated by the `prim` strategy: arithmetic and
   comparison on exact numbers — integers of any size and rationals, see
   "Exact numbers" below (`+ - * / mod   < <= > >=   = <>`), the numeric
   helpers `abs min max`, and `rng` (a pure, deterministic hash for reproducible
   pseudo-randomness); plus string and symbol handling — `cat str< str sym explode
   implode`, and `padl`/`padr` for aligning text output. (Peano numerals still work
   if you want them, but you no longer have to.)
3. **Normal-order evaluation** — `oncetd`/`oncebu` traversals and the derived
   `outermost(s) = repeat(oncetd(s))`. This is what lets recursive, `if`-guarded
   library functions terminate; innermost (call-by-value) would loop on them.

## Reflection, quotation, and strict evaluation

Three more interpreter features, added while building a formal model that needed
programs to inspect and construct their own descriptive vocabulary as data (see
`CTMU.md`), close gaps the first three features didn't cover. All three are
purely additive: no existing program's behavior changes.

1. **`matches?` / `match-witness`** — native primitives (fire under `prim`) that
   reify the interpreter's OWN pattern matcher — the mechanism that decides which
   subjects a `rule` governs — as object-level functions over ordinary term data.
   `(matches? PATTERN SUBJECT)` decides `exists sigma. sigma(PATTERN) = SUBJECT`;
   `(match-witness PATTERN SUBJECT)` exhibits the witnessing substitution as
   `(some (dict (entry name value) ...))`, or `none`. Nothing else in the
   language can do this: a `rule` left-hand side is fixed at parse time, so no
   rule can match a *runtime-computed* pattern against a subject. Like `equal?`,
   both fire on their arguments exactly as written — see "strict variables"
   below for how to force an argument to a value first when that matters.
2. **`verbatim`** — a right-hand-side (and `where`-binding) form:
   `(verbatim TERM)` substitutes to `TERM` exactly as written in the rule's own
   source, with no substitution inside it at all — not even for variables that
   rule's own left-hand side happens to bind. This is the one way a right-hand
   side can author brand-new pattern-shaped data (containing `?x` / `?xs...`
   symbols nothing on the left-hand side ever bound) instead of only ever
   passing through descriptive vocabulary it already received as an argument.
   Deliberately not named `quote`: that symbol is already an ordinary,
   uninterpreted tag used throughout this codebase's canonical quine idiom,
   `(app ?code (quote ?data)) => (app ?data (quote ?data))`, where `?data`
   inside it must substitute normally — reusing `quote` for this would have
   silently broken every quine example in the repository.
3. **Strict variables** — `!x` in a rule's left-hand side, in place of `?x`,
   at one of that pattern's TOP-LEVEL (direct-child) positions: before
   matching, the engine fully normalizes the subject at that position (the
   same evaluator a `where ?v <- EXPR` binding already uses), then matches as
   if the pattern had said `?x` all along. This exists because some rules are
   unavoidably shape-generic — `(size (?xs...))` matches ANY list, with no way
   to tell "this subject is already a value" from "this subject is an
   unevaluated call to some other rule that happens to also be list-shaped".
   Without forcing, `(size (some-rule-call 40))` would measure the two-element
   *call*, not whatever value it denotes — the exact hazard `equal?` already
   carries and only documents by convention ("reduce the arguments first").
   `!x` makes the fix enforceable: see `lib/ctmu.pal`'s `size`, `subterm?`, and
   `topcontains?` for the idiom (a forcing public entry point delegating to a
   lazy internal implementation), and `desccontains?` for the case where only
   ONE argument (the candidate instance, never the pattern) should be forced.
   Scope: only fixed-arity, top-level positions are supported — a pattern that
   also has a top-level sequence variable (`?xs...`) skips forcing entirely
   (the strict position isn't well-defined until matching decides how many
   elements the sequence variable spans), and the literal `!x`, unrecognized,
   simply fails to match anything: a clean "this rule doesn't apply", never a
   crash.

## Records, transitions, assertions, shared terms

Added to model the economy of the board game *Hegemony* (`HEGEMONY-ECONOMY.md`),
whose state is one ~1,500-node term rewritten for thousands of steps per round.
All are additive or semantics-preserving: every earlier suite passes with its
exact fuel fingerprints.

1. **Shared terms.** Lists are reference-counted (`Rc`), so cloning a term is
   O(1). Large-state programs became practical, and the existing heavy suites
   run about 10x faster.
2. **True head index.** `rules` dispatches only to rules pinned to the
   subject's head (plus wildcard-headed rules), merged in source order.
3. **Records** `(rec (k v) ...)` with native primitives `@` (get, with paths),
   `set@`, `add@` (integer increment), `has@`, `put@`, `del@`, `keys@`, `sum@`.
   Closed world: a missing key never fires. Inside a record, keys are labels,
   not calls: only values are evaluation positions.
4. **`transition NAME : LHS => RHS`** — a rule reachable only by name from a
   strategy, never through `rules` or `where` evaluation: rewriting logic's
   equations-versus-transitions split. `rewrite self with try(oncetd(crank))`
   advances a self-rewriting simulation by exactly one step per run.
5. **`assert TERM with S`** — PASS iff the normal form is `true`; any FAIL
   makes the run exit non-zero.
6. **`--stats`** — prints a rewrite profile (firings per rule).
7. **`#rebind main`** — after `rewrite self`, later commands see the rewritten
   subject.

### Exact numbers, `let`, the normal-form memo, and `--trace`

Added for the materialist-economy study (`MATERIALIST-ECONOMY.md` §2):

- **Exact numbers.** Integers of any size and exact rationals (`3/4`,
  `123456789012345678901234567890`). A value that fits an i64 integer is always
  stored as a plain integer, so equality stays structural and printing
  canonical. `+ - * < <= > >= = <> min max abs add@ sum@` accept any number;
  integer overflow gives the exact result instead of a stuck term. `/` and
  `mod` remain integer operations. New primitives: `q/` (exact division),
  `num`, `den`, `floor`, `ceil`, `round-to` (`(round-to X K)` rounds to the
  nearest 1/K, half up), `expt`, `isqrt`, `number?`, and `decimal`
  (`(decimal X D)` is a string with D decimal places).
- **`let $NAME = TERM with S`** normalizes TERM once and substitutes it for
  `$NAME` in every later `show`, `display` and `assert`. Names must begin
  with `$`.
- **`#memo` / `--memo`** remembers terms already proven normal, so the
  outermost redex search skips them. Normal forms and reduction order are
  unchanged (unit-tested); fuel counts drop, so it is opt-in. `--stats`
  reports memo hits.
- Under the memo, a **normalization cache** also remembers the normal form of
  each argument forced at a strict (`!x`) position, so trying the next rule
  of the same head does not force it again (me-regimes: 115 s -> 84 s).
- **`--trace N`** prints the first N rewrite steps as `rule: redex =>
  contractum`, indented by the depth of guard / `where` / strict-argument
  evaluation; observation only (`examples/me-tour.pal` is a good first trace).
- Internal hash maps (rule index, bindings) use a fast non-cryptographic
  hasher. All 76 earlier example programs print byte-identical output.

## Standard library (`lib/`)

Written entirely in Palimpsest. Import `lib/prelude.pal` to get everything plus
the evaluation strategies.

| Module | Provides |
|---|---|
| `logic.pal` | `if`, `not`, `and`, `or`, `xor`; booleans `true`/`false`; structural `equal?` on any two terms |
| `arith.pal` | `inc dec square max min abs between even odd` over native ints |
| `list.pal`  | `length append prepend reverse map filter foldr foldl sum product member nth range take drop concat`; `zip zipwith enumerate replicate last init snoc`; predicates `empty? all-of any-of count-if find index-of`; `minimum maximum`; pairs `pair fst snd` |
| `option.pal` | optional values `(some x)` / `none`: `some? none? with-default map-option or-else` |
| `math.pal` | `gcd lcm pow factorial fib sign clamp divides? sum-to` |
| `dict.pal` | association maps `(dict (entry k v) ...)`: `put get get-or has? keys values size remove` (`get` returns an option) |
| `sort.pal` | `insert sort sorted?` for integer lists |
| `text.pal` | string assembly over `cat`: `join unwords unlines commas surround parens brackets braces quote-str repeat-str`; `str-length str-reverse` over `explode`/`implode` |
| `prelude.pal` | imports all of the above and defines strategies `normalize`, `eval`, `eval-strict` |
| `refactor.pal` | reusable source-modernization rules + a `modernize` strategy |
| `render.pal` | result renderers (written in Palimpsest) for the `display` command: `shw` (generic term→string), `chess` (N-Queens board), `asm` (three-address code), `binview`, `moves-view`, `set-view`, `text-view` |
| `chart.pal` | text-visualization library: `colplot` (column chart of value vs time), `overlay` (two curves, `o`/`x`/`*`), `histogram` (value distribution), `spark` (one-line sparkline) — used to auto-display the mind↔body environments |
| `mindbody.pal` | the mind↔body loop engine (imports `render.pal` + `chart.pal`): `trace` runs a `step` loop, classifies the attractor (settled / cycle / runaway / bounded), and `loop-view` graphs it; helpers `toward clamp mix`. See `MIND-BODY.md` and `MINDBODY-TUTORIAL.md` |
| `ctmu.pal` | a formal model of the CTMU's dual containment relation: `subterm?`/`topcontains?`/`size` (topological, bounded), `desccontains?`/`desc-witness` (descriptive, unbounded — wraps `matches?`/`match-witness`), `dual-contains?` (the paradox-resolving combination), and a `ctrace`/`cverify` conspansion engine. See `CTMU.md` |
| `ars.pal` | abstract rewriting systems: `unify` (occurs-checked unification), `subterms`/`plug` (one-hole contexts), `critical-pairs`/`all-critical-pairs` (the Knuth-Bendix construction), `locally-confluent?`/`unjoinable-pairs` (the Critical Pair Lemma), `normalize` (rewriting under a ruleset given as data). See `TELIC-CONFLUENCE.md` |
| `games.pal` | finite normal-form games (imports `ars.pal`): `profiles`, `pure-nash`, `weakly-dominant?`/`dominance-witnesses`, `pareto-dominators`, `mixed-2x2` (exact fractions); better-response dynamics as a rewriting system — `improvements`, `improvement-rules` (feeds `ars.pal`'s critical-pair checker), `terminating?` (finite improvement property), `reachable-nash`/`schedule-dependent-starts` (confluence), `run-schedule` (explicit scheduler); potentials — `is-exact-potential?`, `ms-violations` (Monderer–Shapley 4-cycle test); join games `(join-game OP E UTIL SETS)`, `schedule-outcomes`, `all-weak-orders`, `count-cyclic-2`; Howard metagames — `meta21`, `swap`, `meta21-outcomes`/`meta12-outcomes`/`symmetric-meta-outcomes`. See `TELIC-GAMES.md` |
| `hegemony.pal` | the 2-player economy of *Hegemony* as a rewriting system: rulebook tables, a double-entry ledger (`pay`, flow matrix), goods and labor bookkeeping, the five phases, behavioural rules, elections, the IMF, `play-round`/`play-game`, invariants (`invariants?`), and renderers (`dashboard`, `ledger-view`, `goods-view`). See `HEGEMONY-ECONOMY.md` |
| `hegemony-loops.pal` | the causal-loop diagram of that economy as data; elementary-cycle enumeration and polarity; probes that verify every edge sign by finite differences of the model; exact election odds (`p-pass`) |
| `linalg.pal` | exact vectors and matrices over the rationals: `vdot mv vm mm mtrans mident leontief`, Gauss–Jordan `minv`/`mdet`/`msolve`, `hawkins-simon?`, contractive `iter-mv`/`iter-vm`; strict list combinators `smap sfilter scount sall sany sconcat srange` and strict folds `lmax`/`lmin` |
| `value.pal` | Marxian value theory: labour values, the contractive plan, conservation, exchange tables as equivalence relations, exploitation, the FMT and GCET, the profit rate by exact bisection, the wage–profit frontier, MAWD, Okishio tests, skilled-labour coefficients |
| `econophysics.pal` | exact multiplicities and the microcanonical marginal, random-exchange agents, two-class models with an asset cap, Gini/histograms, the Cantillon effect, labour vouchers |
| `classgames.pal` | games with class analysis as input: Nash bargaining against the reserve army or a job guarantee, the class-struggle game, Roemer's withdrawal test, collusion thresholds, quadratic voting, prospect theory, patronage dynamics |
| `polecon.pal` | the integrated political economy as an equation chain in three regimes (capitalism, Cold War, accountable planning), its causal-loop diagram, edge probes, regime conversion |
| `cld.pal` | generic causal-loop diagrams: elementary cycles, polarity, restriction |
| `dialectics.pal` | Structural Dialectics: viability, counterfactual, possibility, necessity, Phase Inversion, Bayesian warrant, synthesis, diagnoses |
| `report.pal` | strict text-report helpers (padded decimal rows, sparklines) |
| `longrun.pal` | the long-run profit rate as a demographic attractor R* = (n+g+dl)/lam (Cockshott et al.) and its floor -(1-w)(g+dl); the input-output iteration of *Classical Econophysics* Table 10.1 |
| `selectorate.pal` | the selectorate model of Bueno de Mesquita et al. (2003, ch. 3): closed forms, certified floor square roots, concave maximization, the Markov-perfect equilibrium, the book's limiting cases |
| `logos.pal` | a toy autoregressive language model and an SCSPL-style variant (imports `games.pal`): pooling algebra — `pool`, `pool-outcomes`, `positional-outcomes` (attention as an online-softmax monoid, max-pooling as a semilattice); the model — `generate`, `actualize` (`sample`/`greedy`), `step` in `frozen` or `telic` mode, `run-world`, `run-log`; measurements — `utility`, `syntax-changes`, `last-change`, `window-repeats`, `context-function?`, `replay-syntax`, `distinct-transitions`; `greedy-path`/`best-path`; `episode-update` for the self-configuring fixed point. See `LOGOS-SCSPL.md` |

`normalize` / `eval` are normal-order (`outermost(prim + rules)`) — the default
you want, terminating for recursive definitions. `eval-strict` is innermost
(call-by-value) — faster for flat arithmetic, but can loop on recursion.

Higher-order functions use an **open application form**: `map`/`filter` call
`(app f x)` and `foldr` calls `(app2 f a b)`, which your program extends with
rules, e.g. `rule app-double : (app double ?n) => (* ?n 2)`.

```
import "../lib/prelude.pal"
rule app-double : (app double ?n) => (* ?n 2)
main = (map double (filter evenp (range 1 10)))
run normalize
```

Beyond lists, the library includes options, integer math, association-map
dictionaries, sorting, and string assembly. For example, counting occurrences
with a dictionary (`examples/wordcount.pal`):

```
import "../lib/prelude.pal"
rule tally      : (tally ?xs) => (tally-into (dict) ?xs)
rule tally-done : (tally-into ?d (list)) => ?d
rule tally-step : (tally-into ?d (list ?x ?xs...)) => (tally-into (put ?x (+ 1 (get-or ?x 0 ?d)) ?d) (list ?xs...))
main = (get apple (tally (list apple banana apple cherry apple)))
run normalize        // ==> (some 3)
```

## Writing complex programs

Four features turn the core into something you can write real algorithms in.

Conditional rules (`where` guards): a rule may require a condition, itself
evaluated by rewriting. Two rules with the same left-hand side then dispatch on
their guards — that is exactly insertion sort's comparison (`examples/sort.pal`):

```
rule insert-le : (insert ?x (list ?y ?ys...)) => (list ?x ?y ?ys...) where (<= ?x ?y)
rule insert-gt : (insert ?x (list ?y ?ys...)) => (prepend ?y (insert ?x (list ?ys...))) where (> ?x ?y)
```

A guard also drives the matcher to *search*: if it rejects one way of splitting
the sequence variables, the matcher tries another. That makes the whole of bubble
sort a single rule — "swap any adjacent out-of-order pair" — repeated to a fixed
point (`run repeat(oncetd(prim + rules))`):

```
rule bubble : (list ?xs... ?a ?b ?ys...) => (list ?xs... ?b ?a ?ys...) where (> ?a ?b)
```

`where` bindings compute intermediate values with `?v <- EXPR`; the result is
normalized and made available to the right-hand side and later clauses:

```
rule classify : (classify ?n) => (result half ?h rem ?r) where ?h <- (/ ?n 2), ?r <- (mod ?n 2)
```

Parameterized and recursive strategies let you define your own combinators — the
strategy language is now programmable, not a fixed menu. Arguments may be
compound (`simplify(dbl + neg)`), and parameters are lexically scoped so
recursion resolves correctly (`examples/strategies.pal`):

```
strategy simplify(s) = innermost(s + prim)
strategy myrepeat(s) = try(s ; myrepeat(s))
show (dbl (dbl 5)) with simplify(dbl)          // ==> 20
```

Multi-line items: rules, strategies, and commands may span several lines. An item
continues while its parentheses are open, while it ends in a continuation token
(`=> = <- : + ; ,`), or while the next line starts with `where`/`+`/`;`/`,`. This
includes `main`: a self-rewriting program's `main = ...` may span multiple
physical lines (`rewrite self` finds and replaces exactly that logical span,
however many lines it occupies, and always writes the result back on one line)
— useful for anything larger than a one-liner, like `examples/ctmu-*.pal`.

Together these are enough to write a **small interpreter** for an expression
language with variables and lexically-scoped `let`, evaluated entirely by
rewriting over an association-list environment — see `examples/interp.pal`
(`let x = 5 in let y = 3 in x*y + 1  ==>  16`). Variable lookup is a non-linear
rule `(lookup ?x (bind ?x ?v ?rest)) => ?v` with a guarded miss case.

## A quine that solves a problem

The headline example is `examples/hanoi-quine.pal` — a self-rewriting program
whose act of reproducing itself *is* a computation: it solves the **Towers of
Hanoi** and becomes a quine at the moment the problem is solved.

Recall the language's definition of a quine: a program that rewrites its own
source file to a fixed point (byte-identical output). The trivial quine
(`examples/quine.pal`) reaches that fixed point immediately. This one reaches it
*by solving a problem first.*

Its `main` starts as an unsolved problem, and three rules encode the classic
recursive Hanoi decomposition — move `n-1` disks aside, move the big disk, move
the `n-1` back:

```
rule hanoi-0 : (hanoi 0 ?f ?t ?v) => (moves)
rule hanoi-n : (hanoi ?n ?f ?t ?v) => (seq (hanoi (- ?n 1) ?f ?v ?t) (move ?f ?t) (hanoi (- ?n 1) ?v ?t ?f)) where (> ?n 0)
rule seq-flatten : (seq (moves ?as...) ?m (moves ?bs...)) => (moves ?as... ?m ?bs...)
strategy solve = outermost(prim + rules)
main = (hanoi 3 a c b)
rewrite self with solve
```

What happens when you run it:

- **Run 1** normalizes `main` and writes the result back. `(hanoi 3 a c b)`
  expands to the full optimal move sequence, so the `main` line becomes
  `main = (moves (move a c) (move a b) (move c b) (move a c) (move b a) (move b c) (move a c))`
  — seven moves, the provably minimal 2³−1. The file has changed: status `WROTE`.
- **Run 2 (and every run after)** finds `main` already a flat `(moves ...)` list
  with nothing left to rewrite. It reproduces the file byte-for-byte: status
  `FIXED POINT … This is a quine.`

So the program is a quine **exactly when** the Hanoi problem is solved. The fixed
point is not incidental — it is a *certificate* that the computation finished.
This is the constructive content of Kleene's second recursion theorem: a program
can compute with its own text, and a self-reproducing fixed point is guaranteed
to exist. Here that fixed point carries a non-trivial answer.

Because the moves come out as terms, the new `str` primitive plus the `text`
library render them readably (`examples/hanoi-render.pal`):

```
"a->c  a->b  c->b  a->c  b->a  b->c  a->c"
```

To watch the whole arc, run it on a scratch copy so the seed stays unsolved:

```sh
cp examples/hanoi-quine.pal /tmp/hq.pal
palimpsest /tmp/hq.pal    # run 1: WROTE — solved Hanoi into its own source
palimpsest /tmp/hq.pal    # run 2: FIXED POINT — byte-identical quine
sha256sum /tmp/hq.pal     # stable from here on
```

## The capstone: a self-rewriting N-Queens solver

Hanoi expands in a single recursive sweep. The hardest thing a self-rewriting
program can do is a genuine *search* — try, fail, backtrack — and
`examples/queens-quine.pal` does exactly that: it solves the **N-Queens** problem
by depth-first search with backtracking, expressed entirely as term rewriting,
then rewrites the answer into its own source and becomes a quine.

The search is an abstract machine made of rewrite rules. A partial placement is
`(cols c_row … c_1)`; the driver tries each column in the current row, checks it
against every placed queen for column and diagonal conflicts, and recurses:

```
rule place-done : (place ?row ?placed ?n) => (found ?placed) where (> ?row ?n)
rule pick-yes   : (pick true ?row ?placed ?n ?c ?rest) => (after (place (+ ?row 1) (cols-add ?c ?placed) ?n) ?row ?placed ?n ?rest)
rule after-nope : (after nope ?row ?placed ?n ?rest) => (try ?row ?placed ?n ?rest)   // deeper search failed → backtrack
rule after-found: (after (found ?sol) ?row ?placed ?n ?rest) => (found ?sol)          // deeper search won → done
```

The backtracking lives in `after`: normal-order evaluation reduces the inner
`(place …)` first, and if it comes back `nope` the machine tries the next column;
if it comes back `(found …)` the answer propagates up. `main` starts as
`(nqueens 8)`; one self-rewrite runs the whole search and writes the solution
into the file (`WROTE`); the next run reproduces it byte-for-byte (`FIXED POINT`).

`examples/queens.pal` also draws and independently verifies the board:

```
Q.......    ....Q...    .......Q    .....Q..
..Q.....    ......Q.    .Q......    ...Q....
```

(shown here as two rows of four for space; the program prints the full 8×8 board,
columns 1 5 8 6 3 7 2 4 — the classic first solution — and checks that no two
queens attack).

Finding this among millions of placements is what the naive interpreter would
choke on, which is why the engine now **indexes rules by head symbol**: at each
node only rules whose left-hand side could match the subject's head are tried,
instead of the whole rule set. With the solver's ~25 rules that turns each step
from a linear scan into a couple of attempts, and the N=8 search finishes in well
under a second.

## Building complex self-rewriting programs

A self-rewriting program has to *compute* its next form, so the harder programs
lean on the parts of the language that manipulate values. A handful of primitives
make text, symbols, and generic data first-class, and each is exercised by a
complex self-rewriting program (each solves on the first run and reproduces itself
as a quine thereafter; verify them all with `verify-self-rewriting.sh`):

- **`explode` / `implode` / `str<`** bridge strings and lists and give a string
  order. `examples/self-sort-text.pal` holds a sentence, explodes it, insertion-
  sorts the characters by `str<`, and imploses the result back into its own
  source (`"the quick brown fox"` → `"   bcefhiknooqrtuwx"`).
- **`sym`** turns a computed string into a symbol, which is what fresh-name
  generation needs. `examples/self-compile.pal` is a compiler: it flattens an
  arithmetic expression into three-address code, inventing a fresh temporary
  `t0, t1, …` for each operation via `(sym (cat "t" (str k)))`, and writes the
  compiled program back into itself.
- **`equal?`** (structural equality on any two terms, expressed in the library
  with a non-linear rule) lets a program compare whole terms.
  `examples/self-dedup.pal` removes duplicate compound terms from a list by
  structural comparison.
- **The capstone, `examples/self-turing.pal`,** composes them: a Turing machine
  whose transition table is ordinary *data*, looked up by non-linear matching on
  `(state, symbol)`. It loads a string onto a tape with `explode`, runs the
  machine to `halt`, reads the tape back with `implode`, and rewrites the answer
  into its own source — `(increment "1011")` becomes `"1100"`, then a quine. A
  data-driven interpreter that edits itself is about as far as self-rewriting
  goes.

Each of these programs also **renders its result for a human**, using renderers
written in Palimpsest (`lib/render.pal`) and the `display` command, which prints a
string result with real line breaks. So running the N-Queens quine prints a text
chess board, the compiler prints an assembly listing, the Turing machine prints
`binary 1100  =  12 (decimal)`, and the deduplicator prints a bulleted set — all
produced by rewrite rules, not by the interpreter:

```
 8 . . . Q . . . .        t0 := a * b        set of 3:
 7 . Q . . . . . .        t1 := c * d          - (pt 1 2)
 6 . . . . . . Q .        t2 := t0 + t1        - (rgb 255 0 0)
 ...                      return t2            - (pt 3 4)
   1 2 3 4 5 6 7 8
```

The board renderer is a good example of the language rendering structured data:
`chess` walks a solution `(found (cols ...))` and builds the multi-line string
rank by rank, and the generic `shw` printer turns *any* term into its canonical
text (which is how `set-view` prints arbitrary elements).

## Language cheat-sheet

```
#lang palimpsest
#mode rewriting-as-running | rewrite-then-run
#fuel N
#caps { rewrite: [self, file "path"] }

import "path.pal"                 // merge a library's rules + strategies

rule NAME : LHS => RHS [where CLAUSE, ...]   // CLAUSE = guard EXPR | ?v <- EXPR
strategy NAME = STRATEGY                     // or NAME(p1, ...) = STRATEGY
main = TERM                                  // items may span multiple lines

run STRATEGY                     // normalize main, print
show TERM with STRATEGY          // normalize a literal term, print (canonical form)
display TERM with STRATEGY        // normalize, then print for a human: a string
                                 //   result is shown verbatim (real line breaks),
                                 //   so a rendered board/listing appears as itself.
                                 //   The symbol `main` in TERM is the subject term,
                                 //   so `display (chess main) with solve` renders it.
rewrite self with STRATEGY       // transactional self-modification (quine)
rewrite file "p" with STRATEGY   // transactional cross-file rewrite
assert TERM with STRATEGY        // PASS iff the result is `true` (else exit non-zero)
transition NAME : LHS => RHS     // a rule usable only by name from a strategy
#rebind main                     // later commands see the rewritten `main`
#memo                            // normal-form memo + strict-argument cache (opt-in; changes fuel only)
let $NAME = TERM with STRATEGY   // normalize once; later commands may use $NAME
```

Command-line flags: `--dry-run` (compute and diff, never write), `--fuel N`,
`--stats` (rewrite profile; memo and cache hits), `--memo` (as `#memo`),
`--trace N` (print the first N rewrite steps); subcommand `palimpsest undo FILE`.

Strategies: `id`, `fail`, `prim`, `rules`, a rule/strategy name, `NAME(args...)`
(call a user strategy), `s1 ; s2`, `s1 + s2`, `try(s)`, `repeat(s)`,
`topdown(s)`, `bottomup(s)`, `innermost(s)`, `oncetd(s)`, `oncebu(s)`,
`outermost(s)`, `fixpoint(s)`, `all(s)`.

Built-in primitives (fire under `prim` when operands are literals):
`+ - *` (exact, on integers of any size and rationals), `/ mod` (integer
division), `abs min max` and `< <= > >=` (any numbers), `= <>`
(number/str/sym→bool), `q/` (exact division), `num den floor ceil`,
`round-to` (`(round-to X K)`: nearest multiple of 1/K), `expt`, `isqrt`,
`number?`, `decimal` (`(decimal X D)`: display string with D places), the record
operations `@ set@ put@ add@ has@ del@ keys@ sum@`,
`cat` (str→str), `str<` (str,str→bool, lexicographic), `str` (sym/int/str→str,
e.g. `(str 42)` → `"42"`), `sym` (str→sym, the inverse of `str`, for computed
names), `explode` (str→list of one-char strings), `implode` (list of
strings→str), `rng` (int→int, a deterministic splitmix64 hash of a seed —
pure, so stochastic programs still self-rewrite to identical quines), and
`padl`/`padr` (str,int→str, pad a string to a width). `str<`,
`sym`, `explode`, and `implode` bridge symbols, strings, and lists (text
processing, fresh names, ordering); `abs`/`min`/`max`/`rng` support clamped and
noisy numeric dynamics; `padl`/`padr` align text output. `matches?`
(term,term→bool) and `match-witness` (term,term→option) reify the
interpreter's own pattern matcher as object-level functions — see
"Reflection, quotation, and strict evaluation" above.

Pattern variables: `?x` (term, matches any single subterm), `?xs...` (sequence,
matches zero or more elements, non-linear if repeated), and `!x` (STRICT term
variable — forces the subject at that top-level position to its normal form
before matching; see "Reflection, quotation, and strict evaluation" above). A
right-hand side may also use `(verbatim TERM)` to produce `TERM` completely
unsubstituted, for authoring fresh pattern-shaped data.

## Implementation map

| Concept | File |
|---|---|
| Terms, reader, canonical printer (round-trips) | `src/term.rs` |
| Exact numbers: canonical integer/rational representation, numeric primitives | `src/num.rs` |
| Fast non-cryptographic hasher for the rule index and bindings | `src/fxhash.rs` |
| Matching (`?x`, `?xs...`, non-linear), substitution, `verbatim` | `src/matcher.rs` |
| Strategy combinators, primitives (incl. `matches?`/`match-witness`, records), strict variables (`!x`), transitions, fuel, once/outermost, head-indexed dispatch, rewrite profile, normal-form memo and normalization cache, `--trace` | `src/strategy.rs` |
| Capabilities, atomic writes, snapshot ledger, dry-run, undo | `src/safety.rs` |
| Program loader with imports, `let`, `#memo` | `src/program.rs` |
| CLI driver, `display` rendering, `assert`, `--stats`, `--memo`, `--trace`, `#rebind main`, `undo` | `src/main.rs` |
| Python port of all of the above (Pyodide engine), parity test, page builder | `web/palimpsest.py`, `web/test_parity.py`, `web/build.py` |
| Browser playground (generated) | `index.html` |

## Safety properties (all demonstrated by `run_demo.sh`)

- **Termination** — fuel bounds every run; exhaustion aborts before any write.
- **Self-rewriting quine** — `examples/quine.pal` reproduces its own file
  byte-for-byte (verified by SHA-256), a genuine non-trivial fixed point. And
  `examples/hanoi-quine.pal` reaches that fixed point by *solving Towers of
  Hanoi* — the quine is the certificate that the computation finished.
- **Atomic writes** — temp file in the same dir, `fsync`, then `rename`.
- **Reversibility** — every write snapshots prior bytes; `undo` restores them.
- **Dry-run** — computes and diffs, persists nothing.
- **Least privilege** — `#caps` is enforced and cannot be widened by imports;
  `examples/escape.pal` computes a payload but is denied the write.

## Honest prototype caveats

- **Line-oriented parser.** Items may span multiple physical lines, but the
  parser is still heuristic (it tracks parentheses and continuation tokens)
  rather than a full grammar. Deeply unusual layouts may confuse it.
- **Filesystem sandbox** is enforced by path checks; production would use
  `cap-std` (structurally rejects `..`, absolute paths, symlink escapes) and run
  untrusted rule libraries under Wasmtime/WASI.
- **Content addressing** in the ledger uses FNV-1a; production would use SHA-256.
- **Confluence checking** (critical-pair analysis) is described in the design but
  not implemented; the engine offers ordered determinism plus fuel instead.
- **Partial functions** (e.g. `nth` past the end) reduce to a stuck term rather
  than raising a typed error. (`find`, dictionary `get`, and `index-of` instead
  return an option.)
- **Performance scales with data size, not rule count.** Rules are indexed by
  head symbol, so a large rule set (the whole standard library, a solver) costs
  little — only rules that could match are tried. The remaining cost is term
  size: this is a naive tree-rewriting interpreter where each `oncetd` pass
  rescans from the root and terms are cloned on each step, so operations over
  large *lists* are roughly cubic. Backtracking searches over small states (like
  the N-Queens capstone) are fast; bulk list processing over hundreds of elements
  is not. Accumulator-style helpers (`foldl`, `fib`) force their accumulators with
  `where` bindings to avoid an additional layer of blow-up.

## CTMU studies

Five studies use Palimpsest as a laboratory for single mechanisms of the CTMU. None evaluates the theory as a whole, and each states how far its formal reading of Langan's prose reaches. Each is reproduced by one script.

| document | question | result | check |
|---|---|---|---|
| `CTMU.md`, `NONSUBSUMPTION.md` | Can topological and descriptive containment be one relation? | No: one is bounded and one is unbounded; dual containment is consistent; conspansion is modelled as a verified period-6 cycle | `verify-ctmu.sh` |
| `TELIC-CONFLUENCE.md` | Is independent local overlap resolution confluent? | No: an unjoinable critical pair; a single shared rule restores confluence (revised Oct 2026: the CTMU does posit a global coordinating principle, though not as a rule) | `verify-telic.sh` |
| `SEMILATTICE-GRAMMAR.md` | Which merge rules make independent resolution order- and duplicate-insensitive? | Exactly the bounded semilattices (both directions proved) | `verify-semilattice.sh` |
| `TELIC-GAMES.md` | Can independent telors be analyzed with game theory, and does the CTMU's two-stage telic recursion hold up? | Yes. Overlaps are well-posed games only under a semilattice merge. Improvement always terminates iff contributions are totally ordered. Termination need not be confluent. The global stage works under sufficient conditions (aligned utilities, logit noise, potential = generalized utility) that the text names but does not specify; metagames help in the Prisoner's Dilemma only | `verify-games.sh`, `crosscheck/games_crosscheck.py` |
| `LOGOS-SCSPL.md` | Can SCSPL be structured like the internal processing of a large language model? | In part. Weight sharing, generation followed by sampling, and fixed versus context-dependent behavior correspond to SCSPL's distributed syntax, conspansion and two strata of syntax. LLM inference is standard recursion with fixed syntax, its products are strings, and attention is order-dependent and non-idempotent. A self-refining variant raises its utility from 16 to 29 of 30, and a fixed-point variant becomes a quine. Any computable self-refinement is still standard recursion on the joint state | `verify-logos.sh`, `crosscheck/logos_crosscheck.py` |

The studies build on one another's code: `TELIC-GAMES.md` hands game dynamics to the critical-pair checker written for `TELIC-CONFLUENCE.md` (`lib/ars.pal`), and computes merges with the `fold-op` used in `SEMILATTICE-GRAMMAR.md`; `LOGOS-SCSPL.md` builds on `lib/games.pal` and the logit rule of `TELIC-GAMES.md` §6.3. `TELIC-GAMES.md` §9 documents the execution model, a traced run, how to read the output, and the full reproduction protocol, with exact fuel fingerprints. Quotations of Langan in the telic studies were checked word for word against *The Portable Chris Langan*.

## Economics studies

Two further studies apply the same method to economics rather than the CTMU:

| document | question | result | check |
|---|---|---|---|
| `HEGEMONY-ECONOMY.md` | Can the economy of the board game *Hegemony* be modelled rigorously as term rewriting, with its feedback loops made explicit and checked? | Yes. One round is the normal form of a set of equations over a single state term; the game is a self-rewriting program that becomes a quine at game end. Four conservation laws hold at every round. The causal-loop diagram has 17 elementary cycles (8 reinforcing, 9 balancing), and all 30 edge signs are confirmed on the model by finite differences. Exact results: a Malthusian bound on the Working Class at every policy, labor-market dominance with an exact tax claw-back, a growth imperative, path-independent borrowing, a debt-spiral threshold, monotone election odds, and an idempotent IMF | `verify-hegemony.sh`, `crosscheck/hegemony_crosscheck.py` |
| `MATERIALIST-ECONOMY.md` | Can a mathematically rigorous model of the economy be built from Marxist class analysis, econophysics and game theory, with its feedback loops as term rewriting? | Yes, with exact rationals throughout. Values, the plan and conservation are exact; the FMT holds but so does it for every basic commodity (GCET); the falling rate of profit is determinate only given a wage rule (Okishio 18/18). Conservation yields the exponential distribution; capital income condenses unless capped. The class-struggle game has no rest point under capitalism (187/243 settings) and a stable concession under a job guarantee (243/243). Three regimes run as one self-rewriting program: capitalism's unemployment rises every period; radical governments appear in 15 of 27 sensitivity settings, never under planning. 14 feedback loops; 23 of 24 edge signs confirmed (unemployment raises labour's bargaining power near full employment, via capital flight). Structural Dialectics: a crisis opens a one-period Phase-Inversion window before foreclosure. Thresholds: capital flight below u = 1/12; a job guarantee bites only above u = 1/11; machinery pays at a wage 12.9% higher; the reserve army grows without limit when mechanization exceeds s_c·r − δ; the radical threshold is 11/2 − K in deep losses (curvature, not loss aversion); a crisis becomes a lock-in between aspiration 0.26 and 0.27; collusion fails at ⌈1/P⌉ offices. Against data (no fitting): wage-curve elasticity −0.1 at 5.5% unemployment, labour-share decline 19.9% vs 20.2% (US 1960–2026), lower-class Gini 0.524 vs 0.5, NREGA's +5% at 12.5% unemployment; misses: price–value deviations too small, capital condensation too extreme, unemployment trending | `verify-materialist.sh`, `crosscheck/materialist_crosscheck.py`; written up as a paper in `MATERIALIST-ECONOMY-PAPER.md` (with the selectorate model, checks against *Classical Econophysics* and *How the World Works*, a comparison with empirical data in `me-evidence.pal`, and the model's thresholds and inflection points in `me-extremes.pal`) |

The materialist study reuses the finite-games library (`lib/games.pal`) and the edge-probe method of the Hegemony study, and adds exact rationals, `let`, the normal-form memo and `--trace` to the interpreter. `MATERIALIST-ECONOMY.md` is its technical companion; `MATERIALIST-ECONOMY-PAPER.md` presents it as an academic paper organized by theme (value, money, the labour market, politics, the integrated economy), each section running mechanism, thresholds, evidence and verdict.

## Further reading

See `TUTORIAL.md` for a guided walkthrough, `SELF-REWRITING.md` for a tutorial on self-rewriting programs (from the basics through Hanoi and the N-Queens chess-board solver; verify with `verify-self-rewriting.sh`), `SELF-REFERENCE.md` for a tutorial on self-referential coding (quines, autograms, fixpoint combinators; verify with `verify-self-reference.sh`), `puzzles/PUZZLES.md` for graded puzzles to solve in the language (run `puzzles/check.sh` to verify solutions), `MIND-BODY.md` for a reference on the self-rewriting environments that explore the reciprocal mind↔body loop (`verify-mindbody.sh`), `MINDBODY-TUTORIAL.md` for a step-by-step tutorial on those environments, from the simplest fixed point to two-agent models, with runnable code, the CTMU studies listed above, and the economics studies (`HEGEMONY-ECONOMY.md`, `MATERIALIST-ECONOMY.md` and the paper `MATERIALIST-ECONOMY-PAPER.md`).

