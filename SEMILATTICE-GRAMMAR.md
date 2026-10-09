# A Semilattice Characterization of Convergent Local Self-Configuration

> **Revision note (October 2026).** This version corrects the earlier text in five places.
> 1. The merge rule and the fold are now written in the orientation the code computes, $(w \sqcup v)$, accumulated value first (§3.2).
> 2. The worked example in §3.3 is recomputed; the earlier version contained a garbled chain of equalities.
> 3. The empty boundary $e$ is now required to be an identity (a *bounded* semilattice). This makes both directions of the characterization true as stated.
> 4. The necessity halves of Theorem 1 and of the idempotence result (now Theorem 2) are proved rather than called trivial.
> 5. The context of the "decoheres" quotation is described accurately (§3.1).
>
> Every computed value is unchanged. The game-theoretic sequel, `TELIC-GAMES.md`, also discusses the CTMU's Telic Principle, which this paper did not consider.

## Abstract

The Cognitive-Theoretic Model of the Universe (CTMU) accounts for the local self-configuration of reality through *telic recursion*, a process carried out by many local operators, or *telors*, each maximizing a local utility function independently of the others. Where two telors' domains overlap, the model requires that a single, well-defined outcome results, yet the source material states independence without stating a mechanism by which overlapping outcomes are reconciled. This paper answers the resulting grammatical question directly: what algebraic structure must a telor's local combination rule have for independently-computed outcomes to be guaranteed to agree wherever they overlap? We formalize overlap resolution as a term rewriting system parameterized by a binary combination operation and prove that the system is confluent, in the specific sense of being invariant to the order in which independent contributions are incorporated, if and only if that operation is a bounded semilattice: commutative, associative, idempotent, and with the empty boundary as identity. Both directions are proved. Sufficiency is proved by adjacent transpositions; necessity is proved by deriving each axiom from the convergence requirement on two- and three-element inputs, and is illustrated by a counterexample for each axiom. The characterization is verified computationally, over finite algebras represented as term-rewriting rule sets, using facilities written for this purpose. We further show that idempotence and the pair (commutativity, associativity) discharge logically distinct responsibilities: the former guarantees robustness to a contribution being incorporated more than once, the latter to the order contributions arrive in. We further show that a constant combination rule, while formally an admissible degenerate solution restricted to a one-element codomain, achieves convergence only by discarding all local information. The semilattice signature identified here coincides with the algebraic basis of Conflict-free Replicated Data Types in distributed computing, which solve the identical coordination problem under the identical constraints.

## 1. Introduction

### 1.1 Overview

Before the formal development, an informal statement of the result. Suppose reality is configured locally: many independent processes, each responsible for its own small patch, occasionally overlapping with a neighbor's patch and needing to agree on what happens there, without a central authority to consult. If each process simply does what it individually judges best, with no relationship to what its neighbor does, there is no reason for the two to agree when their patches meet, and in general they will not. The question this paper answers is what has to be true of each process's *rule* for agreement at the overlap to be guaranteed, not merely hoped for.

The answer is a specific and well-known algebraic condition. If every process resolves an overlap by combining the values it can see through an operation that does not care about the order of its arguments (commutativity), does not care how those arguments are grouped when there are more than two (associativity), and does not change its answer if given a value it has already incorporated (idempotence), then agreement is guaranteed, regardless of how many processes are involved, in what order they act, or whether any of them hears about the same update twice. This triple of properties defines a *semilattice*. It is a strong condition: most simple ways of resolving a conflict, such as "prefer my own answer," do not satisfy it. It is not, however, an unreasonably strong one, and the paper exhibits both the proof that it suffices and constructions violating each clause individually to show that none of the three properties is dispensable.

### 1.2 Contributions

1. A term-rewriting formalization of local overlap resolution, general enough to be parameterized by an arbitrary binary combination operation.
2. A theorem, proved directly rather than checked case by case, that the resulting system is order-invariant exactly when the combination operation is a semilattice, together with independent counterexamples showing each of the three semilattice axioms is individually necessary.
3. An executable verification of the theorem, including the specific and separable role of idempotence in tolerating duplicated contributions.
4. Identification of a degenerate but formally valid solution, a constant combination rule, and an account of why it is not a counterexample to the necessity of idempotence, only a boundary case of it.

## 2. Preliminaries

### 2.1 Terms and rewriting

Fix a set of function symbols and an infinite set of variables. A *term* is either a variable, a symbol applied to zero or more terms, or (as data) a symbol on its own. A *rewrite rule* is an ordered pair of terms $\ell \to r$; a set of rewrite rules is a *rewriting system*. A term $s$ *rewrites to* $t$ under a rule $\ell \to r$, written $s \to t$, if $s$ is an instance of $\ell$ under some substitution $\sigma$ and $t = \sigma(r)$. We are concerned in this paper only with *ground* rewriting over a fixed finite carrier set (Section 2.2), so no unification or non-linear matching is required for the results themselves; the underlying implementation (Section 5) is written generally enough to support it in any case.

A rewriting system is *confluent with respect to a given equivalence on initial conditions* if any two derivations starting from equivalent initial conditions reach a common term. The specific equivalence of interest in this paper is *reordering*: two sequences of incoming contributions are equivalent if one is a permutation of the other. This is a natural and, for the problem at hand, the correct notion of confluence to ask for: two telors do not disagree about *which* values are available at their shared boundary, only about *what order* those values became available in and *in what grouping* they were combined, since neither telor has access to a global scheduler.

### 2.2 Semilattices

**Definition 1.** Let $S$ be a set and $\sqcup : S \times S \to S$ a binary operation. $(S, \sqcup)$ is a *semilattice* if, for all $x, y, z \in S$:

- (commutativity) $x \sqcup y = y \sqcup x$;
- (associativity) $(x \sqcup y) \sqcup z = x \sqcup (y \sqcup z)$;
- (idempotence) $x \sqcup x = x$.

It is a *bounded* semilattice with identity $e \in S$ if, in addition, $x \sqcup e = e \sqcup x = x$ for all $x$. In the model below, $e$ is the empty boundary, "nothing contributed yet". Requiring it to be an identity says only that a single contribution $v$ arriving at an empty boundary produces $v$.

Semilattices are the algebraic structures underlying join operations in lattice theory, and, independently of that lineage, the structures used to define Conflict-free Replicated Data Types (CRDTs) in distributed systems, where $\sqcup$ is the *merge* function by which independent replicas reconcile divergent updates without coordination (Shapiro, Preguiça, Baquero, and Zawirski 2011). The coincidence is not superficial: a CRDT's convergence guarantee and the guarantee sought here for telors are the same theorem, applied to different subject matter.

## 3. Local Overlap Resolution

### 3.1 Telic recursion

The CTMU accounts for reality's local self-configuration through a process Langan calls *telic recursion*: local operators, called *telors*, each maximize a local utility function over their own neighborhood, with no global process directing the ensemble. In Langan's own words, "local telors freely and independently maximize their local utility functions" (Langan 2002). The model states this independence as a substantive commitment, not an approximation to be refined away: telic recursion is offered as the general account of how local configuration proceeds, and the independence of its constituent telors is offered without qualification.

Independence of this kind carries an evident risk, which Langan states directly rather than leaves implicit. In a separate piece, a reader suggested that one could accept the "philosophy of wholeness" without identifying it with God. Langan replied that the wave function of the universe "must be coherent in order for the universe to be self-consistent. Otherwise, it pathologically decoheres into independent and mutually irrelevant subrealities" (Langan, correspondence). That remark concerns the universe as a whole, not telor overlaps specifically. Langan also allows ordinary local decoherence: he calls local telic operators "mutually decoherent" and says "deviations from perfect complementarity are ubiquitous". What the model requires, then, is *global* coherence. The source assigns that job to a global principle, the Telic Principle, "a global (syntactic) invariant that works to minimize the total deviation". It does not supply an explicit rule by which disagreement is prevented at the level of two telors resolving a shared boundary. (`TELIC-GAMES.md` §6 examines what such a global principle would need to do.) That omission is the gap this paper closes: not by arguing whether decoherence occurs in the CTMU as a matter of general assertion, but by determining what a telor's local rule would need to satisfy for the specific failure mode Langan names to be structurally excluded.

### 3.2 A rewriting model of overlap resolution

Represent a shared boundary between two telors as a state accumulating contributions one at a time. Fix a finite set $D$ (the values telors may locally propose) and a distinguished initial value $e \notin D$ representing "nothing yet contributed." States are terms of the form $(\mathtt{state}\ v)$ for $v \in D \cup \{e\}$, and incoming contributions are incorporated by a single rule schema, instantiated once for every pair $(v, w) \in D \times (D \cup \{e\})$:

$$(\mathtt{merge}\ v\ (\mathtt{state}\ w)) \;\to\; (\mathtt{state}\ (w \sqcup v))$$

where $\sqcup$ is whatever combination operation the telors in question use, the accumulated value written first. A finite sequence of contributions $[v_1, \dots, v_n]$, applied in that order starting from $(\mathtt{state}\ e)$, realizes a derivation whose final state is $(\mathtt{state}\ ((\cdots((e \sqcup v_1) \sqcup v_2) \cdots) \sqcup v_n))$, the left fold of $\sqcup$ over the sequence with seed $e$:

$$\mathrm{fold}(\sqcup, e, []) = e, \qquad \mathrm{fold}(\sqcup, e, v :: L') = \mathrm{fold}(\sqcup, e \sqcup v, L').$$

This is exactly what `lib/ars.pal`'s `fold-op` computes (`(apply-op OP acc x)` at each step). For a commutative operation the orientation is immaterial; for the non-commutative examples of §3.3 it matters, so it is fixed here. Throughout, $e$ is assumed to be an identity, $e \sqcup v = v \sqcup e = v$, so that a single contribution to an empty boundary yields itself.

Two telors converging on the same boundary, having independently observed the same set of contributions in different orders (because they learned of them through different paths, or because nothing coordinates the order in which independent local events are noticed), correspond to two derivations realizing two different orderings of the same multiset. The system is confluent, in the sense of Section 2.1, exactly when $\mathrm{fold}(\sqcup, e, L)$ does not depend on the order of $L$, for every finite multiset of contributions the telors might see.

### 3.3 Arbitrary combination rules need not agree

Before stating the positive result, it is worth recording that the requirement is not automatically met. Let $D = \{p, q\}$ and consider two "combination rules," one for each of two independent telors, each simply repeating its own preferred value regardless of the other's:

$$\sqcup_{\mathrm{left}}(x, y) = x \qquad \qquad \sqcup_{\mathrm{right}}(x, y) = y$$

Both are perfectly well-defined local rules; each telor, using only information available at its own boundary, always knows what to propose. Extend both so that $e$ is an identity. Each rule is then order-dependent on its own:

- $\mathrm{fold}(\sqcup_{\mathrm{left}}, e, [p,q]) = p \sqcup_{\mathrm{left}} q = p$, but $\mathrm{fold}(\sqcup_{\mathrm{left}}, e, [q,p]) = q$;
- $\mathrm{fold}(\sqcup_{\mathrm{right}}, e, [p,q]) = q$, but $\mathrm{fold}(\sqcup_{\mathrm{right}}, e, [q,p]) = p$.

Neither is a fixed shared operation both telors apply identically ($\sqcup_{\mathrm{left}}$ and $\sqcup_{\mathrm{right}}$ are two different functions of the same two arguments). More directly, a telor using $\sqcup_{\mathrm{left}}$ and a telor using $\sqcup_{\mathrm{right}}$, presented with the same pair $(p, q)$, produce $p$ and $q$ respectively: two different, both locally well-justified, and permanently unreconciled outcomes from the identical situation. This is the concrete shape of local disagreement: not a single malfunctioning telor, but two telors that are each behaving exactly as independence permits. Whether such local disagreement amounts to the global decoherence Langan warns of depends on what the CTMU's global stage can do about it (`TELIC-GAMES.md` §6).

## 4. The Semilattice Theorem

### 4.1 Statement

**Theorem 1.** Let $D$ be a finite set, $e \notin D$, and $\sqcup: (D \cup \{e\}) \times (D \cup \{e\}) \to D \cup \{e\}$ a binary operation with identity $e$. Then $\mathrm{fold}(\sqcup, e, L)$ depends only on the multiset of elements of $L$, for every finite list $L$ over $D$, **if and only if** $\sqcup$ is commutative and associative on $D$.

Idempotence is not required for Theorem 1; its role is separate and is treated in Section 4.3.

### 4.2 Proof

We show that $\mathrm{fold}(\sqcup, e, L)$ is invariant under swapping two *adjacent* elements of $L$; since adjacent transpositions generate every permutation of a finite sequence, invariance under all reorderings follows immediately.

Let $L = [v_1, \dots, v_{i-1}, v_i, v_{i+1}, v_{i+2}, \dots, v_n]$ and let $L'$ be identical except with $v_i$ and $v_{i+1}$ exchanged. Let $a = \mathrm{fold}(\sqcup, e, [v_1,\dots,v_{i-1}])$ be the accumulated value common to both derivations immediately before position $i$; this value does not depend on which of $L, L'$ we are considering, since the two lists agree on their first $i - 1$ elements. The two derivations diverge only in how $v_i$ and $v_{i+1}$ are folded into $a$:

$$(a \sqcup v_i) \sqcup v_{i+1} \qquad \text{versus} \qquad (a \sqcup v_{i+1}) \sqcup v_i.$$

By associativity, $(a \sqcup v_i) \sqcup v_{i+1} = a \sqcup (v_i \sqcup v_{i+1})$. By commutativity, $v_i \sqcup v_{i+1} = v_{i+1} \sqcup v_i$, so $a \sqcup (v_i \sqcup v_{i+1}) = a \sqcup (v_{i+1} \sqcup v_i)$. By associativity again, $a \sqcup (v_{i+1} \sqcup v_i) = (a \sqcup v_{i+1}) \sqcup v_i$. Chaining these equalities gives $(a \sqcup v_i) \sqcup v_{i+1} = (a \sqcup v_{i+1}) \sqcup v_i$, so the two derivations agree at position $i + 1$ and, having the same remaining suffix $[v_{i+2}, \dots, v_n]$ to fold in from that common value, agree at every later position as well, including the final one. (Because $e$ is an identity, commutativity and associativity on $D$ extend to $D \cup \{e\}$, which covers the case $a = e$.)

*Necessity.* Commutativity: since $e$ is an identity, $\mathrm{fold}(\sqcup, e, [x, y]) = x \sqcup y$ and $\mathrm{fold}(\sqcup, e, [y, x]) = y \sqcup x$; these lists are permutations of each other, so $x \sqcup y = y \sqcup x$. Associativity: $[x, y, z]$ and $[z, y, x]$ are permutations, so $(x \sqcup y) \sqcup z = (z \sqcup y) \sqcup x$. Applying commutativity twice to the right-hand side gives $x \sqcup (y \sqcup z)$. Note that associativity is derived *using* commutativity; the two are not independently "trivial" consequences. $\blacksquare$

### 4.3 The separate role of idempotence

Theorem 1 addresses only the order in which a *fixed* multiset of contributions is incorporated. A distinct and equally realistic failure mode for independently-acting telors is that the same contribution reaches a telor more than once, through redundant paths or repeated observation, without the telor having any way to detect the repetition from local information alone. This is a distinct hazard from misordering, and is guarded against by idempotence rather than by commutativity or associativity:

**Theorem 2.** Let $\sqcup$ be commutative and associative with identity $e$. Then $\mathrm{fold}(\sqcup, e, L_1) = \mathrm{fold}(\sqcup, e, L_2)$ whenever $L_1$ and $L_2$ contain the same *set* of distinct elements, **if and only if** $\sqcup$ is idempotent on $D$.

*Proof.* Sufficiency: by Theorem 1, an extra copy of $v$ can be moved next to an existing one, where idempotence collapses the pair, $v \sqcup v = v$; induct on the number of extra copies. Necessity: if $x \sqcup x \neq x$ for some $x$, then $\mathrm{fold}(\sqcup, e, [x]) = x$ but $\mathrm{fold}(\sqcup, e, [x, x]) = x \sqcup x$, although both lists have the set $\{x\}$. $\blacksquare$

Together, Theorems 1 and 2 say that convergence under arbitrary reordering *and* duplication holds exactly when $(D \cup \{e\}, \sqcup, e)$ is a bounded semilattice.

Commutativity and associativity alone do not give this guarantee. Ordinary addition on the integers is commutative and associative but not idempotent ($1 + 1 = 2 \neq 1$), and folding a duplicated contribution through it changes the total, as Section 5.3 demonstrates directly rather than merely by this remark.

## 5. Computational Verification

The formal argument of Section 4 does not depend on execution to be correct; it is a proof. What follows checks that the definitions used above correspond to a real, running rewriting system, and confirms Theorems 1 and 2 against concrete instances rather than leaving them as claims about an abstraction.

### 5.1 Representing finite algebras

A binary operation over a finite carrier set is represented as a rewriting system whose rules enumerate the operation's Cayley table directly: one ground rule $(\mathtt{op}\ A\ B) \to C$ for every pair $(A, B)$ in the domain. This is a faithful, complete specification of a finite operation, in the same sense that a truth table is a complete specification of a finite boolean function, and it is executable exactly as written: applying the operation to two elements is a single rewrite step.

```
rules (rule (op a a) a) (rule (op a b) b) (rule (op a c) c)
      (rule (op b a) b) (rule (op b b) b) (rule (op b c) c)
      (rule (op c a) c) (rule (op c b) c) (rule (op c c) c)
```

is the complete Cayley table for $\sqcup = \max$ over $D = \{a, b, c\}$ under the order $a < b < c$. Whether a given table satisfies each semilattice axiom is then a finite, brute-force, mechanically decidable question: commutativity and idempotence are checked over every pair drawn from the domain, associativity over every triple. Checking the table above against all three axioms, and against a second table deliberately constructed to satisfy commutativity and idempotence while violating associativity ($(a \sqcup b) \sqcup c = b \sqcup c = c$ against $a \sqcup (b \sqcup c) = a \sqcup c = a$), gives:

```
> (is-commutative? max-table (list a b c))  ==> true
> (is-associative? max-table (list a b c))  ==> true
> (is-idempotent?  max-table (list a b c))  ==> true
> (is-semilattice? max-table (list a b c))  ==> true

> (is-commutative? broken-table (list a b c))  ==> true
> (is-idempotent?  broken-table (list a b c))  ==> true
> (is-associative? broken-table (list a b c))  ==> false
> (is-semilattice? broken-table (list a b c))  ==> false
```

The second table shows the three axioms are being checked independently rather than conflated: satisfying two of them does not satisfy the third, and the implementation correctly reports which one fails, since it is the specific counterexample this table was built to contain.

### 5.2 Order-independence

Theorem 1 predicts that folding any ordering of the same contributions through a genuine semilattice operation yields the same value, and folding through an operation failing associativity need not. Folding $[a, b, c]$ in three different orders through the max-table above, and through the broken table, gives:

```
> (fold-op max-table    bottom (list a b c))  ==> c
> (fold-op max-table    bottom (list c b a))  ==> c
> (fold-op max-table    bottom (list b c a))  ==> c

> (fold-op broken-table bottom (list a b c))  ==> c
> (fold-op broken-table bottom (list c b a))  ==> a
> (fold-op broken-table bottom (list b c a))  ==> a
```

The three orderings agree under the semilattice operation, as Theorem 1 requires, and disagree under the operation the theorem's hypothesis excludes. This is not a coincidence of the particular orderings chosen; it is Theorem 1's proof, restated as an executed computation on a specific triple rather than an equation over a universally quantified one, and the disagreement in the second block is the direct, minimal failure mode the proof's associativity step is required to prevent.

### 5.3 Idempotence and duplicate delivery

The distinct claim of Section 4.3, that idempotence rather than commutativity or associativity is what protects against a repeated contribution, is checked by folding a list containing a duplicate through an idempotent operation and through a non-idempotent one. For the max-table, folding $[a,b,c]$ against $[a,b,a,c,b]$ (the same three contributions, in a different order and with two of them repeated):

```
> (fold-op max-table bottom (list a b c))       ==> c
> (fold-op max-table bottom (list a b a c b))   ==> c
```

the duplicated and reordered delivery reaches the same value as the clean one. For ordinary addition, represented the same way as a finite Cayley table over a small enough range to remain closed under the additions performed, folding $[1,2]$ against $[1,2,1]$:

```
> (fold-op add-table 0 (list 1 2))    ==> 3
> (fold-op add-table 0 (list 1 2 1))  ==> 4
```

the duplicate strictly changes the outcome, since addition is commutative and associative but $1 + 1 = 2 \neq 1$ violates idempotence. The two experiments isolate the two hazards independent telors face, misordering and duplication, and confirm that each is governed by a distinct clause of Definition 1, not by the semilattice condition as an undifferentiated whole.

## 6. The Degenerate Case

One admissible way to satisfy Theorem 1's hypothesis deserves separate mention, since it is easy to construct and easy to mistake for a genuine solution. Let $\sqcup$ be the constant operation $x \sqcup y = k$ for some fixed $k$, for all $x, y$. This operation is commutative and associative on any domain, trivially: both sides of each axiom evaluate to $k$ regardless of $x$, $y$, or $z$. It is idempotent only in the degenerate sense that $k \sqcup k = k$; it is not idempotent as a general property of the domain unless the domain is the single point $\{k\}$, since idempotence requires $x \sqcup x = x$ for every $x$ in the domain the operation is defined over, and here $x \sqcup x = k$ regardless of $x$.

Restricted formally to the one-element carrier $\{k\}$, this constant operation is a legitimate, if trivial, semilattice, and Theorem 1 applies to it without qualification. What it buys operationally is convergence purchased by discarding every local contribution: whatever the telors have locally observed, the outcome is $k$ regardless. This is not a counterexample to anything proved above (the theorem does not promise that a semilattice operation preserves information, only that it converges), but it marks the boundary of what the characterization guarantees. A grammar that resolves every overlap to a fixed constant is convergent and uninformative in equal measure; the content of Theorem 1 is that convergence is available *without* that sacrifice, for any operation satisfying the three axioms on a codomain larger than one point, of which $\max$ over an ordered set and set union are two ordinary examples that retain the contributed information rather than discarding it.

## 7. Discussion

### 7.1 Relation to distributed convergence

The characterization in Theorem 1 is not particular to the setting of telors. It is the same theorem, under the same hypotheses, that justifies the convergence property of Conflict-free Replicated Data Types: independent replicas in an asynchronous system, receiving updates in different orders and sometimes more than once, are guaranteed to converge on identical state exactly when their merge operation is a semilattice (Shapiro, Preguiça, Baquero, and Zawirski 2011). The correspondence is not an analogy imposed from outside; it is the identical mathematical statement, with "replica" read as "telor" and "update" read as "locally observed contribution." A grammar for SCSPL satisfying the independence Langan states and the coherence Langan requires is, in the relevant formal sense, obligated to have this structure, whatever vocabulary is used to describe it.

### 7.2 Fit with the source material's own vocabulary

CTMU's account of hology, every local operator working from a homogeneous, self-distributed syntax such that any local region reflects the grammar of the whole, is a claim about every telor sharing the same descriptive resources. It is not, as stated, a claim that those shared resources determine a shared combination rule of the specific algebraic shape identified here; two telors can share an identical grammar and still combine locally observed values by two different, non-semilattice operations, as Section 3.3 shows concretely. What this paper adds is not a revision of hology but a further, independent condition: whatever operation telors use to reconcile overlapping observations must itself be a semilattice, a condition about the operation's algebraic behavior rather than about the vocabulary in which it is expressed.

### 7.3 Scope and limitations

The results above are established for a finite carrier set and for reordering as the relevant equivalence between derivations; both restrictions are appropriate to the question asked; neither is fundamental to the underlying mathematics. Semilattice-indexed convergence is a standard result for arbitrary (including infinite and even uncountable) carrier sets under mild additional conditions, and the finite case here was chosen because it is the case that is mechanically checkable end to end, not because the theorem requires it. Nothing in this paper claims that CTMU's telors are described anywhere in the source material as using a semilattice combination rule; the claim is narrower and, we think, more useful: *if* they are to be guaranteed to converge under the independence the model states, a semilattice combination rule is what convergence requires, by Theorem 1, and nothing weaker suffices, by the counterexamples of Sections 3.3 and 4.3.

## 8. Conclusion

Independent local resolution of a shared overlap converges, in the specific and checkable sense of not depending on the order or multiplicity of the contributions being reconciled, exactly when the local combination rule is a bounded semilattice: commutative, associative and idempotent, with the empty boundary as identity. Both directions are short, direct proofs, not empirical regularities, and each axiom's necessity is also illustrated by an executed counterexample. The characterization is the same one that governs coordination-free convergence in distributed systems, obtained here from first principles for the different but structurally identical problem of independently-acting local operators reconciling a shared boundary, and it distinguishes cleanly between the two distinct hazards, misordering and duplication, that independence exposes a system to, attributing each to a separate and independently necessary algebraic clause.

## References

Christopher M. Langan, "The Cognitive-Theoretic Model of the Universe: A New Kind of Reality Theory" (2002).

Christopher M. Langan, published correspondence answering a reader ("Mackenzie") on wholeness and the coherence of the universe's wave function, from his collected writings (*The Portable Chris Langan*), a piece distinct from the item above.

`TELIC-GAMES.md` (this repository): the game-theoretic sequel, which makes the telors' contributions strategic and examines the CTMU's global stage.

Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski, "Conflict-free Replicated Data Types," *Stabilization, Safety, and Security of Distributed Systems* (SSS 2011), Lecture Notes in Computer Science vol. 6976, Springer, 2011.

## Appendix A: Reproduction

```sh
cargo build --release
./target/release/palimpsest examples/telor-semilattice.pal
./verify-semilattice.sh          # checks every value below against expected output
```

reproduces every value reported in Section 5 in a single run: the four-axiom check on the semilattice table and on the deliberately broken one (Section 5.1), the three-ordering agreement and disagreement (Section 5.2), and the duplicate-delivery pair for both an idempotent and a non-idempotent operation (Section 5.3).