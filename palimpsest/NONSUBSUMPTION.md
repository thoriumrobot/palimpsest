# Two Kinds of "Contains"

### A non-subsumption theorem for the CTMU's topological and descriptive containment relations, proved with executable Palimpsest code

*Primary source verified against Christopher M. Langan, "The Cognitive-Theoretic
Model of the Universe: A New Kind of Reality Theory," Progress in Complexity,
Information, and Design 1.2–1.3 (2002) — the CTMU's original technical paper —
consulted directly, in full, for this revision. Citations below point to
specific passages; see the References section at the end.*

---

## Abstract

Christopher Langan's Cognitive-Theoretic Model of the Universe (CTMU) resolves
the set-of-all-sets paradox by splitting the word "contains" into two
relations — *topological* containment (a cupboard holding clothes: literal,
structural nesting) and *descriptive* containment (the clothes defining what
the cupboard *is*: a finite schema picking out possibly unboundedly many
instances) — and observing that a single object can sit on both sides of the
two relations at once without contradiction, because antisymmetry is a
property of a relation, not of an object. This paper gives both relations a
precise, decidable, executable meaning over a term algebra (Palimpsest, a
term-rewriting language), proves the two relations are incomparable, and
proves — constructively, not just abstractly — that they cannot be merged
into a single relation without that relation becoming either incomplete or
unsound. The proofs are backed by running code: every lemma and theorem below
cites a specific Palimpsest program, its exact output, and where in this
repository to find both. All source is in `lib/ctmu.pal` and
`examples/ctmu-*.pal`; `verify-ctmu.sh` reproduces every number in this paper
in one pass.

## In plain terms

Skip this section if you're comfortable with the technical material below;
it says the same thing without the notation.

Langan's starting observation is about the word "contains." Ordinary language
uses it for two different things and doesn't bother to distinguish them.
A cupboard "contains" your clothes — that's a physical fact about what's
sitting inside what. But a *description* of your wardrobe — "mostly blue,
size medium, going threadbare" — also, in a completely different sense,
"contains" your clothes: it's what tells you which clothes count as *part
of* that wardrobe in the first place. One is about physical location; the
other is about definition. Langan calls the first *topological* containment
and the second *descriptive* containment, and his resolution of a nasty
paradox about "the set of all things" hinges on these being genuinely
different relations rather than two flavors of the same one.

Why does that matter? Because if you try to build "the collection of
absolutely everything," classical set theory says you run into a
contradiction: the collection of everything's own power set (every possible
sub-collection of it) is, by a theorem of Cantor's, strictly *bigger* than
the collection you started with — but it's also, obviously, a collection of
*things*, so it ought to be a *sub*-collection of "everything" too. Bigger
than and smaller than, at once. Langan's fix is to say: those two "than"s are
talking about different relations. The collection of everything can
physically hold its power set (topological containment) while being defined
*by* that power set (descriptive containment) — and there's no contradiction,
because nothing requires those two relations to agree.

That's a clean move *if* the two relations really are different — different
enough that one genuinely can't do the other's job. This paper checks that.
Not by philosophical argument, but by building both relations as actual,
runnable code and testing them against each other head-on: we hand-build the
single most generous relation you could construct by combining the two
("something counts as contained if either notion of containment says so")
and then check whether it still behaves the way "container" is supposed to
behave — namely, that a container is at least as big as what's in it. It
isn't. The combined relation ends up claiming that a three-piece description
"contains" something forty-two pieces long, which is exactly the kind of
claim an ordinary container could never make. Try to build a single
relation that acts like both topological and descriptive containment, and
you get something that *works*, in the sense that it answers every question
correctly — but stops meaning "container" in any recognizable sense while
doing it. The two relations resist being merged not because we didn't try
hard enough, but because the properties that make each one what it is are
opposites: one is bounded by size, the other explicitly is not, and nothing
can be both at once for the same pair of things. That is the paper's whole
argument, run as a program instead of just asserted in prose.

## 1. Introduction

### 1.1 The claim being formalized, and its source

Langan's own name for this split is **TD duality** — Topological-Descriptive
duality — and he gives it its own notation: topological inclusion as ⊃ₜ,
descriptive inclusion (which he also calls predicative inclusion — a
predicate's extension including whatever falls under it) as ⊃ᴅ.[^1] This
paper's ⊐ₜ / ⊐ᴅ is chosen to mirror that notation directly, subscript for
subscript. Langan's own illustration is a Venn diagram: the contents of a
circle are determined by, and reflect, the shape of its boundary — the
boundary is what does the describing, and its interior is a
self-distribution of that boundary constraint.[^2] That is a description of
descriptive containment; a moment later in the same passage, physical
nesting inside the boundary is the topological half of the same picture. The
cupboard/clothes framing used throughout this paper is one standard
illustration of the same distinction current in secondary CTMU literature,
chosen for accessibility over Langan's own more abstract Venn-diagram
presentation, but the underlying two-relation structure — one relation for
what's physically inside something, one for what its description picks out
— is his, not an invention for this paper.

The set-of-all-sets application is stated explicitly. Every set, even the
largest one, has a power set, and by Cantor's theorem that power set is
strictly larger — an apparent contradiction once you try to talk about the
set of everything. Langan's resolution is to extend set theory with two
senses of containment that can point opposite ways at once: the largest
possible set can hold its own power set in the topological sense while
being defined by that same power set in the descriptive sense, with neither
direction contradicting the other because they are different relations.[^3]
He states the general shape of this move as a broader principle (the
"Multiplex Unity Principle"): a whole can topologically contain exactly the
parts whose descriptions, in turn, characterize the whole[^4] — a reciprocal
relationship between one object and its contents, run through two different
relations at once, with the direction of "containment" flipping depending
on which relation is meant. That reciprocal, same-object-both-ways structure
is exactly what §7's Theorem 2 tests for breakage, and exactly what makes
"just merge the two relations" tempting to try in the first place: if the
same pair of objects is legitimately on both sides of two different
relations, why not one relation that's just as flexible?

This paper asks a narrower, checkable question: **can that split actually be
avoided?** Is there some single, well-defined relation that plays both roles,
making the two-relation move an expository convenience rather than a
necessity? We answer no, and we answer it by building the most natural
candidate for such a relation and running it.

[^1]: Langan (2002), "The Principle of Attributive (Topological-Descriptive,
    State-Syntax) Duality." Topological inclusion (⊃ₜ) is glossed there as a
    matter of position relative to a boundary — point-set topology's usual
    sense of a region containing a point. Descriptive inclusion (⊃ᴅ) is
    glossed as the Venn-diagram sense in which a predicate's extension
    determines what falls under it — logical substitution rather than
    spatial position. (Discussed further, with the original phrasing
    reproduced, in Mark C. Chu-Carroll, "Two for ONE: Crackpot Physics AND
    Crackpot Set Theory!", Good Math/Bad Math, Feb. 2008.)
[^2]: Paraphrased from Langan (2002), same chapter, on Venn diagrams: a
    circle's boundary is what determines and describes its contents, not
    the reverse.
[^3]: Paraphrased from Langan (2002), the containment-principles discussion
    preceding "Introduction to SCSPL."
[^4]: Paraphrased from Langan (2002), "Syntactic Coherence and Consistency:
    The Multiplex Unity Principle (MU)."

### 1.2 What this paper contributes

1. Precise, decidable definitions of topological containment (⊐ₜ) and
   descriptive containment (⊐ᴅ) over a concrete term algebra, each backed by
   an actual interpreter.
2. **Lemma A**: ⊐ₜ is bounded — a container is always strictly larger than
   what it contains. Proved by structural induction, and checked against a
   running instance.
3. **Lemma B**: ⊐ᴅ is not bounded — a single fixed, finite pattern contains
   instances of every size. Proved by exhibiting an explicit family of
   witnesses, one per size, and checked against four of them for real.
4. **Theorem 1**: ⊐ₜ and ⊐ᴅ are incomparable — neither is a subrelation of the
   other. Proved with an explicit witness pair in each direction.
5. **Theorem 2, the main result**: no single relation decides both
   topological and descriptive containment without becoming either
   incomplete or unsound. Proved constructively: we build the two natural
   attempts at unification, run them, and compute the exact violation each
   one forces.
6. A complementary, implementation-level demonstration that the same
   impossibility resurfaces as a silent-corruption hazard the moment quoted
   and live vocabulary are allowed to share a name — evidence that this is
   not a quirk of one particular formalization choice.

### 1.3 Scope and epistemic status

This paper does not defend the CTMU as a theory, does not touch the parts of
it concerned with consciousness, teleology, or cosmology, and is not a
formalization Langan himself wrote down in the form given here. Having now
read his primary paper directly rather than relying on secondary summaries,
that informality is confirmed rather than assumed: the two-relation move is
argued in prose, illustrated with Venn diagrams and the Multiplex Unity
Principle, and never given the kind of formal apparatus this paper builds —
no term algebra, no induction, no explicit unbounded witness family, no
attempted unification checked for failure. Langan's own defense of the move,
in at least one published exchange with a critic invoking Russell's type
theory, amounts to asserting that extending set theory with the dual
containment concept is sufficient to block the paradox, without further
formal argument.[^5] Whether that assertion holds up is exactly the kind of
question code can help answer and prose alone cannot — which is this
paper's actual reason for existing, not a criticism of the original.
"Formalizing it" here means constructing *a* mechanism with the right formal
shape (one relation bounded, one relation not, a single object legitimately
on both sides) and proving that shape is forced, not that this is the
unique or historically intended mechanism. The CTMU sits outside the
mathematical and philosophical mainstream, and its treatment of this exact
move has already drawn public technical criticism;[^6] nothing in this paper
is a claim about the CTMU's truth as a theory of the universe, only about
whether one specific piece of its internal logic — that there must be two
containments, not one — can be made precise and checked. Readers wanting the
CTMU's own presentation should consult Langan's writing directly; this
paper only formalizes and tests one isolated claim extracted from it.

[^5]: Christopher M. Langan, response to a reader (identified as "Ingvar")
    raising Russell's theory of types as an alternative resolution, in a
    Megaboard Q&A discussion reprinted in the Langan writings collection
    consulted for this paper.
[^6]: E.g. Mark C. Chu-Carroll, "Two for ONE: Crackpot Physics AND Crackpot
    Set Theory!", Good Math/Bad Math, Feb. 2008 — a working mathematician's
    critique of the same powerset argument discussed in §1.1, arguing the
    two-containment move does not by itself block the paradox rigorously.
    Included here for balance, not endorsed; this paper's own contribution
    (§4–§7) is independent of that critique's validity either way.

## 2. Preliminaries

### 2.1 The term algebra

Let **T** be the set of Palimpsest terms: symbols (atoms), integers, strings,
and finite lists of terms, generated by the grammar

```
t ::= sym | int | str | (t₁ t₂ ... tₙ)      n ≥ 0
```

This is not a stylized simplification for the paper — it is exactly
`enum Term { Sym(String), Int(i64), Str(String), List(Vec<Term>) }` in
`src/term.rs`, the interpreter's actual internal representation, and every
definition below compiles and runs as ordinary Palimpsest code against it.

### 2.2 Size

Define `size : T → ℕ₊` recursively: every atom costs 1, and every list costs
1 for itself plus the size of each element.

```palimpsest
rule size          : (size !t) => (size-go ?t)
rule size-go-list   : (size-go (?xs...)) => (size-sum (list ?xs...))
rule size-go-atom   : (size-go ?a) => 1
rule size-sum-0     : (size-sum (list)) => 1
rule size-sum-n     : (size-sum (list ?x ?xs...)) => (+ (size-go ?x) (size-sum (list ?xs...)))
```

(The `!t` is a *strict variable*: it forces its argument to a fully reduced
value before `size` inspects its shape. This is load-bearing and is explained
in §7.4 — skip it on a first read.)

### 2.3 Rewriting and matching, briefly

A Palimpsest program is a set of rewrite rules `LHS => RHS`. A pattern
variable `?x` matches any single subterm; a sequence variable `?xs...`
matches zero or more consecutive elements of a list; a variable repeated in
one pattern (non-linear matching) must bind to structurally equal subterms
each time. Matching a pattern `P` against a subject `S` either fails or
produces a substitution `σ` — a mapping from the pattern's variables to the
subterms they were bound to — such that `σ(P) = S`. This substitution
relation is the entire mathematical content of descriptive containment below;
nothing further needs to be assumed about the rewriting engine.

## 3. Two definitions of containment

### 3.1 Topological containment

`x ⊐ₜ y` ("x topologically contains y") holds iff `y` is a proper subterm of
`x` — `y` occurs, at any depth, among `x`'s elements, and `y ≠ x`.

```palimpsest
rule subterm?        : (subterm? ?s !t) => (subterm-go? ?s ?t)
rule subterm-go-eq   : (subterm-go? ?s ?t) => true where (equal? ?s ?t)
rule subterm-go-list : (subterm-go? ?s (?xs...)) => (any-of (subtermof ?s) (list ?xs...))
rule subterm-go-atom : (subterm-go? ?s ?t) => false
rule app-subtermof   : (app (subtermof ?s) ?x) => (subterm-go? ?s ?x)

rule topcontains? : (topcontains? !container !part) =>
  (and (subterm-go? ?part ?container) (not (equal? ?part ?container)))
```

`subterm?` is decidable by structural recursion, and terminates because every
term is a finite tree.

### 3.2 Descriptive containment

`x ⊐ᴅ y` ("x descriptively contains y") holds iff `x`, read as a pattern
(some of its symbols may be `?`-prefixed variables), has `y` as an instance:
`∃σ. σ(x) = y`.

```palimpsest
rule desccontains? : (desccontains? ?pattern !term) => (matches? ?pattern ?term)
```

`matches?` is a primitive added to the interpreter for this purpose
(`src/strategy.rs`): it reifies the interpreter's own pattern matcher — the
mechanism that ordinarily only runs, invisibly, when deciding whether a
`rule` fires — as an object-level boolean function over term data. Nothing
in the pre-existing language could express this: a `rule`'s left-hand side is
fixed at parse time, so no rule could previously match a *runtime-computed*
pattern against a subject. `desccontains?` is a thin wrapper making that
capability available under a name matching this paper's notation.

Both relations take a "container first" argument order — `topcontains?`
takes (container, part); `desccontains?` takes (pattern, instance), with the
pattern in the schema/container role — so that Theorem 2's merge in §7
compares like with like.

## 4. Lemma A — topological containment is bounded

> **Lemma A.** For all `x, y ∈ T`: `x ⊐ₜ y ⟹ size(y) < size(x)`.

**Proof.** By structural induction on `x`.

- If `x` is atomic, `size(x) = 1` and the only way `y ⊑ x` (the
  reflexive-transitive closure `subterm-go-eq`/`subterm-go-list` decide) is
  `y = x` — atoms have no elements to recurse into. Since `⊐ₜ` requires
  `y ≠ x`, the hypothesis `x ⊐ₜ y` is vacuously false for atomic `x`, and the
  implication holds trivially.
- If `x = (t₁ ... tₙ)`, `n ≥ 1`, then `x ⊐ₜ y` (via `subterm-go-list`, which
  dispatches to `any-of (subtermof ?s) (list ?xs...)`) means `y ⊑ tᵢ` for
  some `i`. Two cases:
  - `y = tᵢ`. Then `size(y) = size(tᵢ) < 1 + Σⱼ size(tⱼ) = size(x)`, since
    every summand is ≥ 1 and there are `n ≥ 1` of them, so the "+1" for `x`
    itself and the other summands already exceed `size(tᵢ)`.
  - `y ⊏ tᵢ` properly. By the induction hypothesis (applied to `tᵢ`, a proper
    subterm of `x`, so the induction is well-founded), `size(y) < size(tᵢ) ≤
    size(x) - 1 < size(x)`.

  Either way, `size(y) < size(x)`. ∎

This is not merely asserted — it is checked against a running instance.
`t1-holds?` computes both sides and conjoins them:

```palimpsest
rule t1-holds? : (t1-holds? ?container ?part) =>
  (and (topcontains? ?container ?part) (< (size ?part) (size ?container)))
```

Executed (`examples/ctmu-containment.pal`, and reproduced directly below):

```
> (topcontains? (cupboard shirt pants) shirt)                    ==> true
> (topcontains? (cupboard shirt pants) (cupboard shirt pants))   ==> false
> (size shirt)                                                   ==> 1
> (size (cupboard shirt pants))                                  ==> 4
> (t1-holds? (cupboard shirt pants) shirt)                       ==> true
```

What this shows: the first line is the everyday case the whole relation is
named for — a container really does hold what's inside it. The second line
is the check that nothing holds itself (irreflexivity — a cupboard is not
one of the things in the cupboard), which is what makes `⊐ₜ` a genuine order
rather than a reflexive one. The third and fourth lines are the actual
measurements Lemma A's proof turns on: `shirt` costs 1, the three-symbol
`cupboard` term costs 4 (1 for the list itself, plus 1 each for `cupboard`,
`shirt`, `pants`). The fifth line is `t1-holds?` computing both halves of
the lemma's conclusion — containment *and* the size inequality — and
finding them to agree, on a pair the proof above didn't special-case. None
of this is exotic; it is the mechanical content of "a cupboard can't be
smaller than what's in it," made checkable.

## 5. Lemma B — descriptive containment is not bounded by size

> **Lemma B.** There exists `p ∈ T` such that, for every `n ∈ ℕ`, there
> exists `y ∈ T` with `size(y) ≥ n` and `p ⊐ᴅ y`.

**Proof.** Take `p = (family ?xs...)` — a two-element list, `size(p) = 3`.
For each `n`, let `yₙ` be `family` followed by `n` copies of the atom `e`:

```palimpsest
rule t2-instance : (t2-instance ?n) => (cons-sym family (replicate ?n e))
rule cons-sym-0  : (cons-sym ?h (list)) => (?h)
rule cons-sym-n  : (cons-sym ?h (list ?x ?xs...)) => (?h ?x ?xs...)
```

The witnessing substitution is `σ = {xs ↦ [e, e, ..., e]}` (`n` copies):
`σ(p)` splices `σ(xs)` in for the sequence variable, giving exactly `yₙ`. This
substitution is always available, for every `n ≥ 0`: matching a pattern list
whose only elements are one literal head symbol followed by a single,
trailing sequence variable against a subject list of any length `≥ 1`
succeeds by binding the sequence variable to every remaining subject element
— there is nothing left in the pattern to also consume, so there is exactly
one way to split the subject, and it always exists.\* Hence `p ⊐ᴅ yₙ` for
every `n`, and `size(yₙ) = 1 + 1 + n = n + 2 ≥ n`. Since `n` is arbitrary,
`{size(y) : p ⊐ᴅ y}` is unbounded above. ∎

\* *This is a general property of Palimpsest's matcher, not special-cased for
this pattern: matching a sequence of pattern elements against a subject list
tries every split point for each sequence variable in turn, and a lone
trailing sequence variable with nothing following it in the pattern always
has exactly the split that consumes everything remaining — see
`match_seq` in `src/matcher.rs`.*

Checked directly, for four different sizes against the same fixed pattern
(`t2-holds?` normalizes `t2-instance ?n` before testing membership; see §7.4
for why that forcing is necessary):

```palimpsest
rule t2-holds? : (t2-holds? ?pattern ?n) => (desccontains? ?pattern (t2-instance ?n))
```

```
> (t2-holds? (family ?xs...) 0)     ==> true
> (t2-holds? (family ?xs...) 1)     ==> true
> (t2-holds? (family ?xs...) 5)     ==> true
> (t2-holds? (family ?xs...) 40)    ==> true
> (size (family ?xs...))            ==> 3
> (size (t2-instance 40))           ==> 42
```

What this shows: the first four lines are the same fixed pattern,
`(family ?xs...)`, tested against instances of four *different* sizes —
not one demonstration but a small sample of an argument that works for
every `n`, exactly as Lemma B's proof claims. It's the last two lines that
carry the weight: the pattern itself costs 3 nodes to write down, and one
particular instance it accepts costs 42. A single unchanging, three-node
description accepts something fourteen times its own size — with a proof
above showing that ceiling isn't 42, there isn't one. Compare this directly
to Lemma A's numbers (§4): there, `size(y) < size(x)` held every time,
because that inequality is what "topologically contains" *means*. Here it
fails outright, on purpose, because "descriptively contains" doesn't carry
that meaning at all. That contrast between the two number pairs — one
respecting a size bound, one blowing straight through it — is the entire
empirical content of this paper compressed into two lines.

The same fixed, three-node pattern contains a genuine 42-node instance. No
size-bounded relation could ever do this — which is exactly Theorem 2.

## 6. Theorem 1 — incomparability

> **Theorem 1.** `⊐ₜ ⊄ ⊐ᴅ` and `⊐ᴅ ⊄ ⊐ₜ`.

**Proof.**

**(a) `⊐ₜ ⊄ ⊐ᴅ`.** Let `C = (cupboard shirt pants)`, `S = shirt`. `C ⊐ₜ S`
(§4). But `C ⊐ᴅ S` fails: `C` is *ground* — it contains no pattern
variables — so as a pattern it admits only the identity substitution, and
`C ⊐ᴅ T` holds only for `T = C`. Since `S ≠ C`, `C ⊐ᴅ S` is false. So
`(C, S) ∈ ⊐ₜ \ ⊐ᴅ`.

**(b) `⊐ᴅ ⊄ ⊐ₜ`.** Let `p, y₄₀` be as in Lemma B (`size(p) = 3`,
`size(y₄₀) = 42`). `p ⊐ᴅ y₄₀` (Lemma B). But `p ⊐ₜ y₄₀` fails: by the
contrapositive of Lemma A, `size(y₄₀) ≥ size(p)` rules out `p ⊐ₜ y₄₀`. So
`(p, y₄₀) ∈ ⊐ᴅ \ ⊐ₜ`. ∎

Both witnesses, run:

```
> (desccontains? (cupboard shirt pants) shirt)                  ==> false
> (desccontains? (cupboard shirt pants) (cupboard shirt pants)) ==> true
> (topcontains? (family ?xs...) (t2-instance 40))               ==> false
> (desccontains? (family ?xs...) (t2-instance 40))              ==> true
```

What this shows: the first pair of lines is witness (a) — the cupboard term
descriptively contains only itself (line 2, `true`), never one of its own
parts like `shirt` (line 1, `false`), even though topologically it very much
does contain `shirt` (§4). A ground, variable-free term can't act as a
schema for anything but its own exact shape; "descriptive" containment has
nothing to grab onto without a variable in the pattern. The second pair is
witness (b), and it's the mirror image: the same pattern/instance pair from
Lemma B fails topological containment (line 3 — the 42-node instance simply
isn't written down anywhere inside the 3-node pattern) while it succeeds at
descriptive containment (line 4). Put the four lines side by side and the
two relations disagree on both pairs, in opposite directions — not a
coincidence of these particular examples, but the direct consequence of one
relation being bounded by size and the other not (Lemmas A and B). That
disagreement, made concrete, is what "incomparable" cashes out to: neither
relation is a special case of the other; each accepts pairs the other
flatly rejects.

## 7. Theorem 2 — non-subsumption (the main result)

> **Theorem 2.** There is no relation `R ⊆ T × T` such that `R` is *complete*
> for descriptive containment (`⊐ᴅ ⊆ R`) and `R` is *sound as a size bound*
> (`∀x,y. R(x,y) ⟹ size(y) < size(x)`) — the one property that makes
> topological containment a meaningful notion of physical/structural nesting,
> established for `⊐ₜ` itself by Lemma A.

**Abstract proof.** Suppose such an `R` exists. By completeness,
`R(p, y₄₀)` holds (Lemma B). By soundness, `R(p, y₄₀) ⟹ size(y₄₀) <
size(p)`, i.e. `42 < 3`. False. Contradiction. ∎

That proof is three lines once Lemma A and B are in hand — and it is worth
being honest that, stated abstractly, the theorem risks sounding almost
tautological ("of course something bounded can't equal something unbounded").
The substance is not in that final step; it is in (1) Lemma A and B
themselves, each a genuine structural fact about a real term algebra, checked
against running code rather than assumed, and (2) what follows: rather than
leaving the impossibility as an abstract non-existence claim, we build the
single most natural candidate for `R` and watch it fail, with the exact
violation computed.

### 7.1 Two attempts, not one

Any attempt to unify `⊐ₜ` and `⊐ᴅ` has to give up something. There are
exactly two things to give up — completeness or soundness — because those
are the only two properties Theorem 2's proof pits against each other. In
plain terms: either the merged relation refuses to agree with descriptive
containment on some pair (and is therefore not really doing descriptive
containment's job), or it agrees with descriptive containment everywhere
and inherits a case where the "contained" thing is bigger than its
"container" (and is therefore not really doing topological containment's
job). We build both attempts and run both, rather than picking whichever
makes the better story.

### 7.2 Attempt 1 — purely structural (incomplete)

The most conservative attempt: just use `topcontains?` (§3.1) and nothing
else — no existential/substitution machinery at all. It is sound as a size
bound by construction (it *is* `⊐ₜ`, Lemma A already proved this) but
incomplete for descriptive containment:

```
> (topcontains? (cupboard shirt pants) shirt)     ==> true    -- correct
> (topcontains? (family ?xs...) (t2-instance 40)) ==> false   -- WRONG: p ⊐ᴅ y₄₀, but this R says no
```

`examples/ctmu-nonsubsumption.pal` uses `topcontains?` directly for this
attempt rather than a hand-duplicated copy under a new name: `topcontains?`
already *is* the relation Attempt 1 tests, and re-implementing it under an
alias would prove nothing beyond what §3.1/§4 already established, while
inviting exactly the kind of drift between "what the paper describes" and
"what actually ran" this paper is trying to avoid.

### 7.3 Attempt 2 — the OR-merge (unsound)

The most generous attempt: something counts as contained if *either*
mechanism says so — the literal union of the two relations as sets of pairs.
If any single relation was going to work, it is this one, since it is by
construction a superset of both `⊐ₜ` and `⊐ᴅ`:

```palimpsest
rule contains-merge? : (contains-merge? ?x ?y) => (or ?s ?d)
  where
  ?s <- (topcontains? ?x ?y),
  ?d <- (desccontains? ?x ?y)
```

Run against the same two cases:

```
> (contains-merge? (cupboard shirt pants) shirt)     ==> true   -- correct
> (contains-merge? (family ?xs...) (t2-instance 40)) ==> true   -- correct!
```

Attempt 2 gets both cases right. It looks, for a moment, like the theorem
just failed. It has not — the failure shows up one level up, in what `R`
being true is supposed to *mean*:

```
> (size (family ?xs...))                                   ==> 3
> (size (t2-instance 40))                                   ==> 42
> (> (size (t2-instance 40)) (size (family ?xs...)))        ==> true
```

`contains-merge?` says the 42-node instance is contained by the 3-node
pattern — and the instance is, provably, fourteen times larger. This is not
a rounding error or an edge case: it is a direct, computed violation of
`R(x,y) ⟹ size(y) < size(x)`, the exact property Lemma A establishes for
`⊐ₜ` and the exact property that makes "container" a meaningful word for a
relation to model. Attempt 2 is complete and unsound, in exactly the sense
Theorem 2 predicts.

### 7.4 Why there is no third attempt

Sections 7.2 and 7.3 are not two examples chosen from a larger space of
possible fixes; they are the only two possible outcomes, by the abstract
proof in §7. Any relation agreeing with `⊐ᴅ` on `(p, y₄₀)` (required for
completeness) inherits the soundness violation of Attempt 2 for that exact
pair; any relation refusing to agree with `⊐ᴅ` there (to preserve soundness)
inherits the incompleteness of Attempt 1. There is no third position between
"accept the pair" and "reject the pair." A relation is, extensionally, just a
set of accepted pairs — there is no third truth value to assign `(p, y₄₀)`.

(One loose end: `size`, `topcontains?`, and `desccontains?` above are written
with `!` — *strict* — arguments at the positions that need a realized value,
not `?`. This is necessary for the numbers above to be trustworthy at all: a
rule dispatching on term *shape*, like `size-go-list`'s `(?xs...)`, matches
any list-shaped subject on sight, with no way to distinguish an
already-reduced value from an unevaluated call to some other rule that
happens to also be list-shaped. Without forcing, `(size (t2-instance 40))`
would silently measure the two-node *call* `(t2-instance 40)`, not the
42-node list it denotes, making every number in this section wrong in a way
that would not show up as an error — merely as a quietly incorrect count.
This was not a hypothetical risk: it is exactly what happened once, mid
development of this proof, for `(size (t2-instance 80))`, caught by hand
before it could make it into a citation, and fixed at the language level —
`!x` in `src/strategy.rs`/`src/term.rs` — precisely so it can't happen again
silently. Full account in `CTMU.md`, "Language changes".)

## 8. Corroborating evidence: the vocabulary-collision hazard

Theorem 2 shows the two *relations* cannot be merged. A related, weaker, but
independently interesting fact is that even attempting to merge the two
*vocabularies* — writing a piece of data meant to represent a descriptive
schema using the same head symbol as a live, loaded topological rule —
silently corrupts it, with no error raised. In plain terms: if you write
down a *sample* of what a rule looks like, using the rule's actual name, the
running program can't tell "this is just an example I'm showing you" from
"please execute this" — and it executes it, quietly overwriting the example
with whatever that rule happens to compute.

```palimpsest
main = ... (mirrored-as-data (subterm? ?s ?t)) ...
```

`(subterm? ?s ?t)` here is meant as inert data: a mention of the shape of the
rule `subterm-go-eq`, not an invocation of it. But the interpreter has no
notion of "mentioned, not used" — every subterm of a running program is a
candidate for reduction. `subterm?`'s own live rules catch it: the equality
guard fails (`?s` and `?t` are different literal symbols, not the same
term), the list case doesn't apply (the third position isn't a list), and it
falls through to the unconditional atom case, silently becoming `false`:

```
> (mirrored-as-data (subterm? ?s ?t))    ==> (mirrored-as-data false)
```

This happens at the level of *symbols*, independent of the abstract relation
theorem in §7 — the two are related but distinct failure modes, one semantic
(no relation can be both bounded and unbounded on the same pair) and one
syntactic (no namespace can, without discipline, let "quoted" and "live" text
coexist under one name). That the same underlying tension — content and
process refusing to stay separated once forced to share an identity — shows
up independently at both levels is, we think, modest additional evidence that
the two-relation split is not an arbitrary modeling choice. Full account,
including the `verbatim` mechanism this repository added specifically to
keep the two vocabularies separable on purpose, in `CTMU.md`, "T3-HAZARD".

## 9. Discussion

**Is this trivial?** The final step of Theorem 2's abstract proof (§7) is a
short and, once stated, unsurprising contradiction. What is not trivial —
and is the actual content of this paper — is (a) that `⊐ₜ` and `⊐ᴅ` are
*real*, checkable, independently-defined relations over an actual term
algebra rather than a hand-wavy metaphor, with Lemma A and B as genuine,
non-obvious-in-advance facts about them (a structural induction and an
explicit unbounded family of witnesses, respectively), and (b) that the most
generous, most natural attempt at unification — not a strawman, but literally
the union of the two relations — still fails, with a specific, computed,
checkable violation rather than an appeal to intuition.

**What this does and doesn't establish.** This paper establishes that *a*
formalization of the CTMU's topological/descriptive split, built to be
faithful to the informal description (bounded structural nesting vs.
unbounded schema-instance membership), cannot be collapsed into one
relation. It does not establish that this is the *only* possible
formalization, nor does it establish anything about the CTMU's other,
unrelated claims. A different formalization of "topological" or
"descriptive" containment might behave differently; we have tried to choose
the most natural and literal reading of each ("a cupboard is bigger than
what's in it"; "a schema can describe arbitrarily much"), and the fact that
those two natural readings turn out to be provably irreconcilable is the
paper's actual finding.

**A dynamical postscript.** `lib/ctmu.pal` and `examples/ctmu-conspansion.pal`
extend dual containment (not the non-subsumption result specifically) into a
small dynamical system modeling the CTMU's *conspansion* — material
contraction running alongside apparent spatial expansion, with a fixed
descriptive schema governing a bounded, perpetually "requantizing" body,
echoing Langan's own two-part description of the process.[^7] It settles
into a genuine, verified period-6 limit cycle, with dual containment checked
at all 25 visited states. It is a separate result from this paper's and is
documented in `CTMU.md` rather than argued here, but it shares the same
commitment: run it, don't just assert it.

[^7]: Langan (2002) describes conspansion as having two complementary
    phases, inner expansion and requantization, and states that the
    universe's contents shrink relative to a domain that does not itself
    expand in any absolute sense — the model in `lib/ctmu.pal` keeps only
    the coarse shape of this (a fixed boundary, a body that cycles within
    it) and none of the underlying physics (Planck-scale rescaling, the
    speed of light as conspansion's rate, or the rest of Langan's argument
    for accelerating cosmic expansion), which is well outside this paper's
    scope.

## 10. Conclusion

The CTMU's informal claim — that "contains" must split into a topological
and a descriptive relation to avoid the set-of-all-sets paradox — survives
formalization. Given the natural reading of each relation over a concrete
term algebra, topological containment is provably bounded (Lemma A) and
descriptive containment is provably not (Lemma B); the two are incomparable
(Theorem 1); and no single relation can decide both without becoming either
incomplete or unsound (Theorem 2), a fact demonstrated constructively by
building the most generous possible unification and computing the exact
violation it forces (42 > 3). Every claim in this paper corresponds to a
line of Palimpsest code and a line of verified output; `verify-ctmu.sh`
reproduces all of them in one pass.

---

## References

1. Christopher M. Langan, "The Cognitive-Theoretic Model of the Universe: A
   New Kind of Reality Theory," *Progress in Complexity, Information, and
   Design* 1.2–1.3 (2002) — the CTMU's original technical paper, and the
   primary source for §1.1, footnotes 1–4 and 7. Consulted directly and in
   full for this revision.
2. CTMU Community Wiki, "Topological-Descriptive Duality" and "Set of All
   Sets," ctmucommunity.org — secondary, community-maintained explication,
   consulted for cross-checking terminology and framing against source 1.
3. Mark C. Chu-Carroll, "Two for ONE: Crackpot Physics AND Crackpot Set
   Theory!", *Good Math/Bad Math*, Feb. 2008 — a critical, non-CTMU-aligned
   technical assessment of the same powerset argument this paper builds on;
   cited in §1.1 and §1.3 for terminology confirmation and for balance.
4. This repository: `lib/ctmu.pal`, `examples/ctmu-containment.pal`,
   `examples/ctmu-conspansion.pal`, `examples/ctmu-nonsubsumption.pal`,
   `src/strategy.rs`, `src/matcher.rs`, `src/term.rs`, `CTMU.md` — every
   definition, lemma, and theorem in this paper is executable and verified
   against these files; see Appendix A and B.

## Appendix A: Reproducing these results

```sh
git clone <this repository>
cd palimpsest
cargo build --release
./verify-ctmu.sh                                  # all results in this paper, in one pass
./target/release/palimpsest examples/ctmu-nonsubsumption.pal   # Theorem 2, standalone
./target/release/palimpsest examples/ctmu-containment.pal      # Lemmas A/B, Theorems 1, §8
```

Both example programs are self-rewriting: the first run computes every
result in this paper for real and writes it back into the program's own
`main`; the second run finds the file already in normal form and reports a
fixed point — a quine. That closure is itself a small illustration of the
paper's subject: a descriptive layer (the rules) generating exactly the
topological object (the file) that already contains it.

## Appendix B: Where each result lives

| Result | Definition | Executable check |
|---|---|---|
| §3.1 `⊐ₜ` | `lib/ctmu.pal`, `subterm?`/`topcontains?` | `examples/ctmu-containment.pal`, T1 |
| §3.2 `⊐ᴅ` | `lib/ctmu.pal`, `desccontains?`; `matches?` in `src/strategy.rs` | `examples/ctmu-containment.pal`, T2 |
| Lemma A | `lib/ctmu.pal`, `t1-holds?` | `examples/ctmu-containment.pal` |
| Lemma B | `lib/ctmu.pal`, `t2-instance`/`t2-holds?` | `examples/ctmu-containment.pal` |
| Theorem 1 | — | consolidated check in this paper's §6 |
| Theorem 2 | `examples/ctmu-nonsubsumption.pal`, `contains-merge?` | `examples/ctmu-nonsubsumption.pal` |
| §8 hazard | `examples/ctmu-containment.pal`, `T3-HAZARD` | `examples/ctmu-containment.pal` |
