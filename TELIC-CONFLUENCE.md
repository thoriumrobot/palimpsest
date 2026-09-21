# Does Telic Recursion Converge?

### A confluence-theoretic test of the CTMU's account of local, independent self-configuration

*Citations below are to Christopher M. Langan, "The Cognitive-Theoretic Model of the Universe: A New Kind of Reality Theory" (2002), and to a separate published correspondence in which Langan answers a reader's question about decoherence, both consulted directly for this paper. See the References section for full attribution.*

## Abstract

The CTMU explains how reality configures itself locally, without a central coordinator, through what Langan calls telic recursion: many local operators ("telors"), each maximizing its own local utility function, independently resolve the regions where their domains overlap. Langan states plainly that this independence produces contingencies, and separately names the failure mode a system of this kind risks: decoherence into subrealities that no longer talk to each other. This paper asks whether that risk is merely hypothetical or is a property of the mechanism as described. It formalizes local, independent overlap-resolution as a term rewriting system and asks the question rewriting theory was built to answer: is the system confluent, meaning that resolving overlapping regions in a different order always reaches the same outcome? The answer, checked by computing the system's critical pairs rather than assumed, is no. Two independent, locally sensible resolution rules can disagree on their shared overlap, and the two outcomes are both stable and different: a real instance of the disconnected, mutually irrelevant split Langan names as pathological. The paper also shows what is missing: a single rule under shared, global information is confluent by construction. The gap between the two is not a technicality; it is the difference between independent local operators and an actual coordinator, and CTMU's own account, as far as this paper finds, supplies the first without the second.

## In plain terms

Skip this section if the abstract already made sense.

Picture two people rearranging the same shared bookshelf at the same time, each unaware of what the other is doing, each just trying to make their own end of the shelf look right. If they never touch the same books, no problem. But if they both reach for the same overlapping section at once, each acting on their own judgment about what looks best there, you would not be surprised if they ended up with two different, mutually incompatible arrangements of that middle section, one that made sense from the left person's plan and one that made sense from the right person's, neither one obviously wrong, and no way to tell in advance which one you will actually get.

The CTMU says something structurally similar is how reality configures itself moment to moment: not one global planner deciding everything at once, but many independent local processes, each locally optimizing its own patch, occasionally overlapping with a neighbor's patch and needing to settle what happens there. Langan calls these local processes telors and the moment-to-moment settling telic recursion. He says this independence is real and creates what he calls contingencies, and he separately names what can go wrong: the whole thing can fall apart into disconnected pieces that no longer make sense together.

This paper takes that setup at its word and builds the simplest honest version of it: two independent local resolvers, each with its own reasonable rule for what to do at an overlap, both rules literally taken from the shape Langan describes. Then it asks a question that has a real yes-or-no answer in mathematics, not just in argument: no matter which resolver gets there first, do you always end up in the same place? For this literal, minimal version of the mechanism, the answer, checked by exhaustively finding every way the two rules can conflict and testing whether the conflict resolves, is no. Which resolver acts first genuinely changes the outcome, and the two possible outcomes are the kind of disconnected, mutually irrelevant results Langan warns about, not a rare edge case but the generic behavior of this exact setup. The paper also builds the fix, a single shared rule instead of two competing local ones, and shows that it does resolve the issue immediately, which pins down precisely what a real fix would need: not more independence, but an actual mechanism for the two sides to agree, the one ingredient two independent, uncoordinated resolvers leave out by definition.

## 1. Introduction

### 1.1 The claim under test

The CTMU's account of how reality updates itself locally rests on a process Langan calls telic recursion. Local operators, which he calls telors, each maximize a local utility function over their own neighborhood, with no global process directing them: "local telors freely and independently maximize their local utility functions."[^1] New states arise, on Langan's account, where two such neighborhoods overlap: local operators mutually absorb and acquire each other's content at the point where their domains meet, and it is this local, pairwise event, not any global process, that settles what the new joint state becomes.[^2]

Independence of this kind has a cost, and Langan states so directly: telic recursion, precisely because it is carried out independently by many local subsystems, produces what he calls contingencies rather than a single determined outcome. He also states, in a separate piece answering a reader's question about what happens when a system of this kind fails to hold together, what that failure looks like: the system "pathologically decoheres into independent and mutually irrelevant subrealities."[^3]

Both statements are informal, and neither is accompanied by a demonstration of when the risk is realized and when it is not. This paper supplies one.

### 1.2 The question, made precise

Independent local processes reliably agreeing and independent local processes producing mutually irrelevant, disconnected outcomes are not two ends of a spectrum to be balanced by appeal to hology or self-similarity; they are a yes-or-no question about a specific mechanism, and rewriting theory already has the right tool to ask it. A system of local rewrite rules is confluent if, whenever a state can be transformed two different ways, both ways can always be brought back to a common result. A system is locally confluent if that holds for every pair of rules that can fire on overlapping material in a single step. By the Critical Pair Lemma (Knuth and Bendix 1970; the general form is due to Huet 1980), local confluence can be decided outright, for a finite set of first-order rules, by checking a finite, computable list of "critical pairs": the outcomes of every way two rules' left-hand sides can be unified against each other. If every critical pair resolves to a common term, the system is locally confluent. If even one does not, it is not, and that pair is a concrete witness of the failure.

This gives a direct translation of Langan's own claim into a checkable question: model telic recursion's local, independent overlap-resolution as rewrite rules, compute its critical pairs, and see whether they all resolve.

### 1.3 What this paper contributes

1. A minimal, literal formalization of local, independent telic recursion as a term rewriting system, built directly from Langan's own description of telors, local utility maximization, and overlap.
2. A working implementation, in the Palimpsest term-rewriting language, of unification, critical pair computation, and local confluence checking for arbitrary first-order rewrite systems, validated first against textbook examples with known confluence status.
3. A computed result, not an assumption: the literal model of independent telic recursion is not locally confluent, and the specific pair of outcomes it produces on its simplest possible overlap is the disconnected, mutually irrelevant pair Langan's own vocabulary names as the failure state.
4. A constructive contrast: replacing the two independent rules with one rule under shared information restores confluence immediately, isolating what independent telic recursion, as described, does not supply.

### 1.4 Scope and epistemic status

This paper is about one mechanism inside the CTMU, not the theory as a whole, and it does not evaluate CTMU's claims about consciousness, teleology, or cosmology. It also does not claim that no elaboration of telic recursion could be made confluent; the constructive contrast in Section 5 shows a way to do that. What it claims is narrower and, unlike that broader question, checkable: the mechanism as Langan describes it, independent local operators each locally maximizing utility with no coordinating rule, is not confluent in its most direct formalization, and CTMU's account of hology (distributed replication of the same underlying grammar across every local operator) answers a different question than the one this failure raises. Hology, as stated, is about every operator sharing the same syntax to work with, not about a rule for what happens when two operators' independently-optimal outputs disagree. Those are different guarantees, and only the second one would block the failure this paper exhibits. CTMU sits outside the mathematical and scientific mainstream; this paper takes seriously only the specific technical claim examined here, not the theory's broader standing.

## 2. Background: rewriting, confluence, and critical pairs

A term rewriting system is a set of rules, each a pair of terms (a left side and a right side, the right possibly containing variables from the left), together with the convention that a term matching a rule's left side may be replaced by the corresponding instance of its right side. Two terms are joinable if some sequence of such replacements turns each into the same term. A system is confluent if every pair of terms reachable from a common ancestor is joinable, and locally confluent if that holds specifically for terms one step apart from a common ancestor.

Confluence is the formal content of "it doesn't matter what order you do things in, you get the same answer," and it is what would need to be true for many independent local processes to be guaranteed to settle on one coherent outcome regardless of which one acts first. Checking it directly, by comparing every possible pair of divergent computations, is not feasible in general; there are infinitely many. The Critical Pair Lemma reduces the check to something finite and computable: for finitely many first-order rules with no other divergences than those arising from two rules overlapping on the same material, local confluence holds exactly when every "critical pair" (the two outcomes of resolving one such overlap two different ways) is joinable. If a system is also terminating (has no infinite chain of rewrites), local confluence upgrades automatically to full confluence, by Newman's Lemma (Newman 1942).

## 3. A term-rewriting model of telic recursion

### 3.1 The overlap

Langan's own picture of where a new state comes from is spatial: local operators are pictured as circular domains ("inner expansive domains"), and a new state is settled precisely where two such circles intersect, through the local, pairwise exchange of content between the operators occupying that shared region.[^4] This paper takes that picture at face value: an overlap between two telors is represented as a single term holding both operators' locally-preferred values for the shared region,

```
(pending X Y)
```

where `X` is what the left-hand telor's local optimization would produce there and `Y` is what the right-hand telor's would produce, absent any coordination between them.

### 3.2 The two telors

Each telor resolves the overlap by its own rule, propagating its own locally-preferred value across the whole shared region (a stand-in for "this telor's locally maximal configuration now occupies this patch"):

```
rule telor-left  : (pending ?x ?y) => (resolved ?x ?x)
rule telor-right : (pending ?x ?y) => (resolved ?y ?y)
```

Neither rule can fire again once either has: both produce a `resolved` term, and both rules' left sides match only `pending` terms. This is important and not a simplification made for convenience: it reflects that once an overlap is settled, it is settled, matching Langan's own description of new states as things that get acquired and then requantized, not reopened. (An earlier, more naive version of this model, without that property, does not terminate under either telor's own rule reapplied to its own output; the version above is the one actually analyzed throughout this paper.)

This is deliberately the simplest version of "two independent local optimizers, resolvable by unification, contending for one overlap" that can be built at all. It does not encode a specific numerical utility function, because Langan does not give telors' utility functions a general closed form either; it encodes only the one structural fact he does state unconditionally, that each telor resolves its neighborhood according to its own local process, with nothing in the rule for either telor referring to the other.

### 3.3 The confluence machinery

Unification, subterm enumeration, critical pair construction, and local confluence checking, for any ruleset given as data rather than hard-coded, are implemented in `lib/ars.pal` and used unmodified for the analysis below. The implementation was checked, before being pointed at the telor model, against three cases with known answers from rewriting theory: the classic non-confluent two-rule system `a -> b`, `a -> c` (correctly identified as not locally confluent, with the exact witnessing pair `(b, c)` returned); a single-rule system with only a trivial self-overlap (correctly identified as confluent); and a two-rule system with a genuine, non-trivial overlap that does resolve to a common term (correctly identified as confluent, with the shared resolution computed explicitly). All three checks are reproducible; see Appendix A.

## 4. Result: the two-telor overlap is not locally confluent

Computing every critical pair of the two-telor system (`lib/ars.pal`'s `all-critical-pairs`) finds exactly one non-trivial overlap: the two rules' left sides unify at the root (both match any `pending` term), producing the critical pair

```
( (resolved X X) , (resolved Y Y) )
```

for independent X and Y. Checking joinability (`locally-confluent?`) gives:

```
> (locally-confluent?
    (rules (rule (pending ?x ?y) (resolved ?x ?x))
           (rule (pending ?x ?y) (resolved ?y ?y))))
==> false
```

and the unjoinable witness pairs are exactly the two non-trivial orderings of that one conflict:

```
> (unjoinable-pairs ...)
==> (list (pair (resolved X X) (resolved Y Y))
          (pair (resolved Y Y) (resolved X X)))
```

Both sides of this pair are already normal forms: neither `telor-left` nor `telor-right` can rewrite a `resolved` term further, so there is no later step in the process that reconciles them. `(resolved X X)` and `(resolved Y Y)` are, for distinct X and Y, permanently different terms reachable from the same starting overlap `(pending X Y)`, differing only in which telor happened to settle it. Concretely, actually running the rewrite (`normalize`) on the two possible orderings of the identical overlap confirms the order-dependence directly:

```
> (normalize (pending p q) (rules telor-left telor-right)) ==> (resolved p p)
> (normalize (pending q p) (rules telor-left telor-right)) ==> (resolved q q)
```

Swapping which value is written first, with nothing else about the situation changed, changes the final state. This is not a bug in the model; it is what "independent" means when made precise: the mechanism does not, by itself, contain any information about which of two equally locally-valid resolutions should win, so there is nothing in it to make the two resolutions agree.

`(resolved p p)` and `(resolved q q)` are two disconnected, permanently stable results with nothing left in the system to connect them, one telor's outcome and the other's, neither one an error, both unreachable from the other. That is a literal instance of decohering into independent and mutually irrelevant outcomes, not a metaphor for it.

## 5. What would fix it, and what CTMU offers instead

The failure in Section 4 is not exotic; it has a well-understood fix in rewriting theory, and building it makes clear what ingredient was missing. Replace the two independent, competing rules with a single rule that both sides answer to:

```
rule telor-shared : (pending ?x ?y) => (resolved anchor anchor)
```

Here `anchor` stands for any single, globally shared piece of information both telors would defer to, rather than each acting on its own local preference. Checking confluence now:

```
> (locally-confluent? (rules telor-shared)) ==> true
> (normalize (pending p q) (rules telor-shared)) ==> (resolved anchor anchor)
> (normalize (pending q p) (rules telor-shared)) ==> (resolved anchor anchor)
```

Confluence returns immediately, and both orderings now agree, because there is only one rule to disagree with. This is a deliberately extreme fix (discarding `x` and `y` entirely rather than combining them more cleverly), chosen because it isolates the one property that matters here without needing extra machinery: what restored confluence was not adding detail to the local rules, but replacing two independently-acting rules with one rule that is not independent of anything, because there is only one of it.

This is precisely the gap CTMU's account of hology does not close. Hology, as Langan presents it, is a claim about every local operator working from the same underlying syntax: the same grammar is homogeneously present at every point of the medium, so that any local region reflects the structure of the whole.[^5] That is a claim about shared vocabulary: every telor has access to the same grammar. It is not a claim about shared decisions: nothing in that statement says two telors, independently applying that shared grammar to their own local utility functions, must reach the same conclusion about a region they both touch. The fix in this section needed a shared decision, a single rule standing in for one settled outcome both sides accept, not shared vocabulary. As far as this paper's reading of the source material finds, the CTMU supplies the first and, at the level of an explicit rewrite rule, not the second.

## 6. Discussion

**Is this a fair reading?** Sections 3.1 and 3.2 are built directly from language Langan uses unconditionally: telors act independently, each maximizes its own local utility, and new states settle at the intersection of two operators' domains. Nothing in the model adds a constraint or a coordinating mechanism Langan does not himself describe, and nothing in it removes one he does describe (the search for a coordinating mechanism in the source material, including the "hology" passage discussed in Section 5, came up empty; if one exists elsewhere in the CTMU corpus, the argument here is that it would need to look formally like the single shared rule of Section 5, not like a restatement that the syntax is everywhere the same). The model does not attempt to formalize telors' utility functions numerically, because doing so would require inventing content Langan does not supply. What it formalizes is the one property he states without qualification: independence.

**Might a real utility function make the rules agree in practice, even without an explicit coordinator?** Possibly, for specific utility functions and specific overlaps. But "possibly, for specific cases" is not the same claim as "coherence," and CTMU's own language does not hedge the way that concession would require: telic recursion is presented as the general account of how reality holds together, and the contingency Langan attributes to independent local action is presented as a real, general feature of the process, not a special case requiring justification. A mechanism whose coherence depends on the specific content of unspecified utility functions, in a way that is not guaranteed by the mechanism's structure, is a different and weaker claim than the one telic recursion is used to support.

**What does this not show?** It does not show that no version of telic recursion could be made confluent; Section 5 exhibits one that is. It does not show anything about whether reality is in fact coherent, only about whether the specific mechanism offered as an explanation for that coherence guarantees it by its own stated structure. And it is a property of one minimal, literal model, not a proof about every possible elaboration of the idea; a reader who thinks telors carry more coordinating structure than independence and shared grammar is invited to specify it as an explicit rule and rerun the same check, using the same code, against that version instead.

## 7. Conclusion

Local confluence is a precise, checkable stand-in for the claim that it does not matter which independent local process gets there first, and the CTMU's telic recursion, as described in Langan's own terms, is a mechanism whose coherence depends on that property. Built as literally as its own vocabulary allows and checked by computing its critical pairs rather than assuming an answer, the mechanism fails the check: two independent, equally locally valid resolutions of the same overlap produce two different, permanently unreconciled outcomes, a concrete rather than metaphorical instance of decoherence into independent, mutually irrelevant subrealities. A single shared rule fixes it immediately, which is itself the clearest evidence for what was missing: not more locality, but one genuine point of coordination, which independent local telors, so described, do not have.

---

## References

1. Christopher M. Langan, "The Cognitive-Theoretic Model of the Universe: A New Kind of Reality Theory" (2002) — the main technical source for Sections 1.1, 3.1, 3.2, and 5 (footnotes 1, 2, 4, 5).
2. Christopher M. Langan, published correspondence answering a reader's ("Mackenzie's") question on decoherence, consulted from the same collected-writings source as item 1 but a separate, distinct piece — source for footnote 3.
3. Donald E. Knuth and Peter B. Bendix, "Simple Word Problems in Universal Algebras" (1970) — the original critical pair / completion construction.
4. Gérard Huet, "Confluent Reductions: Abstract Properties and Applications to Term Rewriting Systems," *Journal of the ACM* 27.4 (1980) — the general Critical Pair Lemma used in Section 2 and implemented in `lib/ars.pal`.
5. M. H. A. Newman, "On Theories with a Combinatorial Definition of 'Equivalence'," *Annals of Mathematics* 43.2 (1942) — the termination-plus-local-confluence theorem referenced in Section 2.
6. This repository: `lib/ars.pal` (unification, critical pairs, confluence checking), `examples/telor-confluence.pal` (the full analysis in this paper, runnable end to end).

[^1]: Langan (2002), on telic recursion.
[^2]: Paraphrased from Langan (2002), on how new state-potentials arise through the mutual absorption of local syntactic operators via conspansion.
[^3]: Langan (2002), correspondence answering a reader's question on decoherence.
[^4]: Paraphrased from Langan (2002), on inner expansive domains and the local, pairwise events that occur where they intersect.
[^5]: Paraphrased from Langan (2002), on hology as a homogeneous, self-distributed syntactic medium.

## Appendix A: Reproducing these results

```sh
cargo build --release
./target/release/palimpsest examples/telor-confluence.pal
```

The same run reproduces every number in this paper in one pass: the full critical-pair list (Section 4), the confluence verdict and its witness pairs, the order-dependence check, and the single-rule fix (Section 5). The validation cases mentioned in Section 3.3 (the classic non-confluent `a -> b` / `a -> c` system, a trivially confluent single-rule system, and a genuinely overlapping but confluent system) can be checked directly against `lib/ars.pal`'s `locally-confluent?` with any first-order ruleset written in the `(rules (rule L R) ...)` form documented there.
