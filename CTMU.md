# Modeling CTMU containment in Palimpsest

This models one specific idea from Christopher Langan's Cognitive-Theoretic
Model of the Universe (CTMU): that the word "contains" is ambiguous between
two different relations, and that keeping them separate is what lets a
single object be a container in one sense while being contained in the
other, with no contradiction.

- **Topological containment** — a cupboard containing clothes: literal,
  extensional, structural nesting.
- **Descriptive containment** — the clothes defining what the cupboard *is*:
  a finite schema picking out (possibly unboundedly many) instances.

The CTMU uses this split to resolve the set-of-all-sets paradox: the "set of
all sets" can't consistently contain its own powerset under one notion of
containment (Cantor's theorem says every powerset is strictly larger than
its set), but it can contain it topologically while being contained by it
descriptively, because those are two different relations and antisymmetry
is a property of a relation, not of an object.

This file has three parts: **the theorems** (topological containment is
bounded, descriptive containment is not, and a single object can sit on
both sides of the two relations at once without contradiction), **the
non-subsumption proof** (the two relations cannot be merged into one — built
and run, not just argued), and **conspansion** (dual containment as a
dynamical process, over a genuinely verified period-6 limit cycle). The
non-subsumption result also has a standalone, self-contained write-up —
`NONSUBSUMPTION.md`, "Two Kinds of Contains" — with full statements and
proofs of every lemma and theorem; this file's version is the model
reference, cross-linked to source, and lighter on formal proof.

## What this does and does not model

This gives both relations a precise, decidable, executable meaning over
Palimpsest's own term algebra, states four theorems about them, and
*checks* every one computationally rather than asserting it: topological
containment is the subterm relation on the term tree; descriptive
containment is the pattern-instance relation, `exists sigma. sigma(P) = T`,
exposed as a new primitive (see "Language changes" below). It does **not**
model CTMU as a whole, does not touch the parts of the theory concerned
with consciousness, teleology, or physical cosmology, and is not a
formalization Langan himself wrote down — the two-relation resolution of
the paradox is informally stated in his own work, so "modeling it" here
means building *a* mechanism with the right formal shape (bounded vs.
unbounded containment, two independent relations reconciling a
self-referential object), not proving that mechanism is the unique or
intended one. Treat it as a checked analogy, not a verification of CTMU
itself. CTMU is a fringe framework outside the mathematical and
philosophical mainstream; nothing here is a claim about its truth, only
about whether a specific piece of its internal logic can be made precise
and run.

## The theorems (`lib/ctmu.pal`, `examples/ctmu-containment.pal`)

**T1 — topological containment is bounded.** `(subterm? S T)` is the
reflexive-transitive closure of "is an immediate element of", decidable by
structural recursion (every Palimpsest term is a finite tree) and computed
generically for any term shape via the same decomposition idiom
`lib/render.pal`'s `shw` already uses. `(topcontains? CONTAINER PART)` is
the proper (irreflexive) version. `t1-holds?` checks, not asserts, that
every proper part is strictly smaller (`size`) than its container.

**T2 — descriptive containment is not bounded by size.** `(desccontains?
PATTERN TERM)` wraps a new primitive, `matches?` (see below): does
`sigma(PATTERN) = TERM` for some substitution sigma? `t2-holds?` confirms
that the *same fixed, finite* pattern `(family ?xs...)` contains instances
of size 0, 1, 5, and 40 alike — one compact description with genuinely
unbounded reach, which T1's relation structurally cannot have.

**T3 — dual containment**, the actual resolution: one object `U` on both
sides of the two relations at once. `U` literally contains (topologically)
a schema shaped like a real rule's left-hand side (`subterm-go-eq`, see
"Language changes"), alongside a sample expression that schema (read
descriptively) contains as an instance. `dual-contains?` independently
re-derives both directions rather than being told the answer.

**T3-HAZARD**, an honest negative result. If the mirrored schema had
instead reused the exact head symbol of a rule actually loaded and running
in the same program, it would *not* stay inert as data — the live rule set
normalizes every subterm of `main` with no notion of "this part is being
mentioned, not used", so the literal text `(subterm? ?s ?t)` dropped in as
"data" gets silently caught by `subterm?`'s own entry rule (whose strict
argument forcing an atom is a harmless no-op) and reduced to `false` by
`subterm-go-atom` before it can ever be read back out as the pattern it was
meant to represent. This is the sharpest evidence in the containment file
for why CTMU needs two different relations in the first place: the moment
"currently-quoted description" and "currently-running process" share a
name, mentioning and using collapse into each other — the exact kind of
conflation Russell's paradox exploits.

## Non-subsumption (`examples/ctmu-nonsubsumption.pal`)

The theorems above establish that the two relations *differ*. This program
goes a step further and proves they cannot be *merged*: there is no single
relation that decides both topological and descriptive containment without
becoming either incomplete or unsound. Not argued abstractly — built, run,
and the violation it forces is computed, not asserted.

Two attempts, both against the same pair: the fixed pattern `(family
?xs...)` and a genuine 40-element instance of it (`t2-instance 40`, size
42) it must contain:

- **Attempt 1 — purely structural.** `topcontains?` by itself: exactly the
  well-founded relation of T1, with no existential/substitution machinery
  at all. Correct on a genuinely structural case (`(cupboard shirt pants)`
  contains `shirt`); **incomplete** on the descriptive one — blind to the
  40-element instance, because it is not literally nested inside the
  two-node pattern term.
- **Attempt 2 — the OR-merge.** `(contains-merge? x y) = topcontains?(x,y)
  OR desccontains?(x,y)` — the most generous possible single relation built
  from the two; if any unification is going to work, this is it. It *is*
  now correct on both cases. But: `(size pattern)` is 3, `(size instance)`
  is 42, and `(> (size instance) (size pattern))` computes to **true** — the
  "contained" instance is fourteen times larger than its "container". That
  is not a rounding error; it is the one property that makes topological
  containment a sound, trustworthy notion of physical/structural nesting in
  the first place — that a container is always at least as big as what it
  holds — and the OR-merge has none of it. Attempt 2 is **unsound as a size
  bound**.

There is no third attempt to try: completeness for descriptive containment
requires accepting instances of unbounded size (T2), and soundness as a
topological bound requires rejecting exactly those. A single relation
cannot do both for the same pair, because those two requirements are
direct logical negations of each other once you fix what "the same pair"
means. The program computes and prints the actual numbers (`size-of-pattern
3`, `size-of-instance 42`, `soundness-of-merge-as-a-bound true`) rather
than asserting the conclusion, and — like the other two — becomes a
self-rewriting quine once run.

## Conspansion (`lib/ctmu.pal`, "CONSPANSION" section; `examples/ctmu-conspansion.pal`)

CTMU calls the claim that reality's boundaries stay fixed while its content
perpetually requantizes within them *conspansion* — material contraction
during space expansion. `lib/ctmu.pal` turns dual containment from a static
pair of predicates into a dynamical system: a state `(scspl DESC (cells
?xs...) BOUND)` pairs a fixed, never-changing schema DESC = `(cells
?xs...)` with a bounded, evolving body that grows by one labelled cell per
tick and, on reaching BOUND, drops its oldest cell instead of growing.
Labels are drawn from a 3-symbol palette by tick number, independent of
body length, so the joint (length, contents) state space is finite —
meaning the trajectory *must* eventually re-enter an exact prior state, by
the pigeonhole principle, not merely as an empirically observed fact.

Running the actual 24-tick trajectory confirms this: it settles into a
genuine, verified **period-6 limit cycle** (`lcm(2, 3)`, from the
length-oscillation period and the label-palette period, exactly as the
pigeonhole argument predicts), and `cverify` checks — at *every one* of the
25 visited states, not just once — that the fixed schema is simultaneously
a literal topological part of the whole state term and a working
descriptive container for that tick's body.

## Language changes

Four changes were made to the interpreter itself, all additive and covered
by new Rust unit tests (`cargo test`, 32 total) plus a full pass of every
`verify-*.sh` suite (68 checks across `verify-mindbody.sh`,
`verify-self-rewriting.sh`, `verify-self-reference.sh`, and
`verify-ctmu.sh`), unaffected. See `README.md`, "Reflection, quotation, and
strict evaluation", for the same material aimed at a general reader rather
than this file's specific model.

- **`matches?` / `match-witness`** (`src/strategy.rs`) reify the
  interpreter's own pattern matcher — the mechanism that decides which
  subjects a `rule` governs — as object-level functions over ordinary term
  data. `matches?` decides `exists sigma. sigma(pattern) = term`;
  `match-witness` exhibits the witnessing substitution as `(some (dict
  (entry name value) ...))`, or `none`. Nothing in the pre-existing
  language could do this: a `rule` left-hand side is fixed at parse time,
  so no rule could previously match a *runtime-computed* pattern against a
  subject.
- **`verbatim`** (`src/matcher.rs`, in `subst`) lets a rule's right-hand
  side, or a `where ?v <- EXPR` binding, construct fresh pattern-shaped
  data containing `?x` / `?xs...` symbols that nothing on the left-hand
  side bound. Without it, `subst` treats every bare sequence-variable
  symbol on a right-hand side as something needing a binding from that
  same rule's own match, so a rule could otherwise only ever pass through
  descriptive vocabulary it already received, never mint new vocabulary of
  its own. Deliberately *not* named `quote`: that symbol is already an
  ordinary, uninterpreted tag used throughout this codebase's canonical
  quine idiom (`(app ?code (quote ?data)) => (app ?data (quote ?data))`,
  where `?data` inside it must substitute normally) — reusing it would have
  silently broken every quine example in the repository.
- **`find_main` / `splice_main`** (`src/program.rs`) were generalized from
  "`main = TERM` on exactly one physical line" to the same multi-line
  "logical item" grouping the rest of the parser already uses for
  everything else. This was a genuine pre-existing limitation, not a
  deliberate design choice: it silently broke any self-rewriting program
  whose `main` was written for readability across several lines (as all
  three files here are). Single-line `main` — every example in the
  repository predating this model — is unaffected.
- **Strict variables (`!x`)** (`src/strategy.rs`, `src/term.rs`) — writing
  `!x` for one of a rule's top-level left-hand-side arguments, in place of
  `?x`, forces that argument to its normal form before matching, using the
  same evaluator a `where ?v <- EXPR` binding already uses. This was needed
  because `size`, `subterm?`, `topcontains?`, and `desccontains?` are all,
  of necessity, shape-generic — `(size (?xs...))` matches ANY list-shaped
  subject, with no way to tell "this is already a value" from "this is an
  unevaluated call to some other rule that happens to also be
  list-shaped". While building `ctmu-nonsubsumption.pal`, exactly that
  hazard surfaced for real: `(size (t2-instance 80))`, called without
  forcing first, silently measured the two-node *call* `(t2-instance 80)`
  and returned `3`, not the 82-node list the call actually denotes — the
  same class of mistake `equal?` (`lib/logic.pal`) already carries and only
  documents by convention ("reduce the arguments first"). Strict variables
  make the fix enforceable rather than merely documented: `size`,
  `subterm?`, and `topcontains?` now force every argument that matters
  (`lib/ctmu.pal`, "TOPOLOGICAL CONTAINMENT"); `desccontains?` forces only
  its second argument, the candidate instance, and deliberately never the
  first, the pattern — forcing a pattern would defeat the entire point of
  `matches?`, which is to compare a schema against a subject exactly the
  way a real `rule` left-hand side would, and a rule's left-hand side is
  never pre-normalized either. All of this is a library-level fix
  (`lib/ctmu.pal`'s public predicates now have a forcing entry point
  delegating to a lazy internal implementation, e.g. `subterm?` to
  `subterm-go?`); no call site anywhere had to change, and every previously
  verified result — T1 through T3-HAZARD, both non-subsumption attempts,
  the period-6 cycle — was independently re-derived after the fix and
  matches exactly.

## Running it

```sh
./target/release/palimpsest examples/ctmu-containment.pal      # T1 / T2 / T3 / T3-HAZARD
./target/release/palimpsest examples/ctmu-conspansion.pal      # conspansion
./target/release/palimpsest examples/ctmu-nonsubsumption.pal   # the non-subsumption proof
```

Each is a self-rewriting program: the first run computes every check for
real and writes the result back into its own `main` line (`status: WROTE`);
the second run finds the file already in normal form (`status: FIXED
POINT`) — a genuine quine, and the concrete instance of SCSPL closure this
whole model is ultimately about: the descriptive layer (the rules) has
generated exactly the term that ends up as the file's own topological body.
`verify-ctmu.sh` checks all three, twice each, plus the invariant, cycle,
and non-subsumption verdicts, in one pass.
