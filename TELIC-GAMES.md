# Telors as Players

### A game-theoretic analysis of independent local self-configuration

*Companion to `TELIC-CONFLUENCE.md`, which shows that independent overlap resolution is not confluent, and `SEMILATTICE-GRAMMAR.md`, which shows that a merge is insensitive to order and duplication if and only if it is a bounded semilattice. Every computed claim below is reproduced by `./verify-games.sh`, using the library `lib/games.pal`. Quotations are from Langan (2002) and his collected writings, and were checked against* The Portable Chris Langan.

## Abstract

The CTMU describes telic recursion in two stages: "The primary stage maximizes global generalized utility on an ad hoc basis as local telors freely and independently maximize their local utility functions" (Langan 2002). Sections 3–5 analyze the second, local clause on its own. Section 6 asks what the first, global clause must mean for the whole sentence to be true. Agents that independently maximize their own utilities, where outcomes depend on what the others do, are the subject of non-cooperative game theory, so the question is what game theory says about telors rather than whether it applies. We address it at four levels.

(1) *Well-posedness.* An overlap is a normal-form game among its telors only if its outcome is a function of the telors' choices. If the merge rule is not commutative and associative, the order in which contributions arrive acts as a further, decisive move by the scheduler. Each semilattice axiom removes one form of manipulation: commutativity removes timing, associativity removes coalition pre-merging, and idempotence removes duplicate submission.

(2) *Equilibrium.* When overlaps are resolved by a semilattice join, each overlap is a well-defined *join game*. Its equilibria need not be good ones. If two telors can contribute the top element, the profile in which they do so is a Nash equilibrium, and it can be Pareto-dominated. On a chain, contributing one's most preferred value is weakly dominant if and only if utility does not rise again above that value. When two telors' preferred values are incomparable, truthful contribution produces their join, and the overlap becomes an anti-coordination game with two asymmetric pure equilibria and a mixed equilibrium; in our example the mixed equilibrium produces the join with probability 9/16. When telors cannot contribute the top element, pure equilibria can fail to exist.

(3) *Dynamics.* The process in which each telor improves its payoff whenever it can is a rewriting system on profiles. Its normal forms are the pure Nash equilibria, its termination is the finite improvement property, and its confluence is the independence of the final equilibrium from the order of moves. We prove that independent improvement terminates in every join game over a carrier if and only if the carrier is a chain, and we check this exhaustively on all 2 × 169 ordinal two-telor games over a three-element chain and a three-element non-chain. Terminating dynamics can still be non-confluent; the resulting critical pair has the same form as the one in `TELIC-CONFLUENCE.md`. Convergence holds in general when every pairwise overlap is an exact potential game, that is, when local utilities are aligned with a global one. Even then, the equilibrium reached can depend on the order of moves and need not maximize the global utility.

(4) *The global stage.* Langan's text does not leave telors purely non-cooperative. It refers to a global selection function (the Telic Principle), to "shared teleology", to local telors that "mirror the overall system", to noise, and, in his Noesis writings, to Howard's metagames. We give each a game-theoretic formulation and test it. Alignment yields an exact potential, and logit noise concentrates the long-run distribution on the potential's maximizers. The potential coincides with an aggregate of the telors' utilities, which is how Langan describes the utility of the global grammar, only for particular utility designs; in the Prisoner's Dilemma, noisy local maximization selects mutual defection. Computed exactly, metagames sustain cooperation in the Prisoner's Dilemma, leave the selection problem in the assert/yield game unchanged, and give matching pennies stable outcomes only by fixing a hierarchy that determines the winner. The semilattice result ensures agreement about the merge, but it leaves the coordination problem in the choice of contributions and the order of play. The CTMU assigns that problem to its global stage. Game theory states what that stage would have to do, and none of the mechanisms named in the text does all of it.

## Overview

`SEMILATTICE-GRAMMAR.md` asked when the order in which two telors' contributions to a shared boundary are combined does not affect the result. The answer is that the combining rule must behave like *max* or *set union*. That condition makes everyone agree on the result for a given set of contributions. It does not determine which contributions telors make, and the CTMU describes telors as utility maximizers. Choices of this kind are the subject of game theory.

We treat each telor as a player whose move is its contribution and whose payoff is its utility for the merged boundary. Three results follow. First, an order-dependent merge does not define a game, because the scheduler determines the outcome. Second, a merge with all the required properties can still leave telors in poor agreements: the profile in which everyone contributes everything is stable, and two telors with incompatible preferences face a contest over whose preference prevails. Third, if telors keep adjusting their contributions independently, the adjustments can cycle indefinitely. They cannot cycle when the possible values are totally ordered. When the adjustments do stop, the stopping point can depend on who moved first, which is the order-dependence found in `TELIC-CONFLUENCE.md`, now in the dynamics instead of the merge.

The CTMU does not claim that local telors achieve coherence by themselves. It adds a global stage: a cosmic selection principle, "shared teleology", noise, and, in Langan's Noesis writings, metagames. Section 6 formulates each of these in game-theoretic terms and tests it. Together they can make the CTMU's claim true, but only under conditions the text mentions without specifying.

## 1. Introduction

### 1.1 The question

Can the behavior of independent telors be analyzed with game theory? Formally it can. The CTMU's telors are decision-makers, each maximizing its own local utility function, with overlapping domains, so that the outcome at an overlap depends on more than one of them. This is the setting of a non-cooperative game (Nash 1951). The substantive questions are which game this is, what its solution concepts predict, and whether those predictions support the coherence the CTMU requires.

Two features of the source shape the answer. First, the local telors are only part of telic recursion. "Telic recursion occurs in two stages, primary and secondary (global and local)"; the primary stage "is associated with the global telor, reality as a whole", and the Telic Principle is "a global (syntactic) invariant that works to minimize the total deviation from perfect complementarity of syntax and state as syntactic operators freely and independently bind telesis", taking "the form of a selection function with a quantitative parameter, generalized utility" (Langan 2002). A faithful model is therefore a game embedded in a global selection principle, not a bare non-cooperative game. Second, the CTMU's claim is global. Langan says that local telic operators are "mutually decoherent" and that "deviations from perfect complementarity are ubiquitous"; elsewhere he says that human volition "is free to be locally out of sync with teleology", which "requires a set of compensation mechanisms which ensure that teleology remains globally valid despite the localized failure of any individual" (CTMU Q and A). Local inefficiency, contested overlaps and non-convergence are therefore not counterexamples to the CTMU in themselves; they are what its global stage must compensate for. (The phrase "pathologically decoheres into independent and mutually irrelevant subrealities", used in the earlier analyses, comes from a reply about the coherence of the wave function of the universe as a whole. In CTMU terminology, local decoherence is the ordinary requantization phase of conspansion.)

### 1.2 Relation to the two earlier analyses

`TELIC-CONFLUENCE.md` modelled two telors that resolve one overlap by their own rules and found the resulting rewrite system non-confluent: the result depends on which telor acts first. `SEMILATTICE-GRAMMAR.md` asked what a shared combination rule must satisfy for the result to be independent of arrival order and duplicate delivery, and found that it must be a bounded semilattice. Both analyses take the telors' contributions as given. This paper treats them as strategic choices. We show that the order-dependence found in the first paper, which the second removes from the merge, reappears in the strategic dynamics.

### 1.3 Contributions

1. A sense in which semilattice structure is a precondition for game-theoretic analysis of an overlap (the scheduler is a dummy player if and only if the merge is commutative and associative), and a correspondence between each semilattice axiom and the manipulation it prevents (Section 3).
2. The equilibrium theory of join games: existence of a possibly inefficient equilibrium at the top element; a characterization of when contributing one's preferred value is dominant; the anti-coordination structure of incomparable preferred values, with a closed-form collision probability; and the absence of pure equilibria when the top element cannot be contributed (Section 4).
3. A formulation of independent local improvement as an abstract rewriting system, in which Nash equilibria are normal forms, the finite improvement property is termination, and independence from the order of moves is confluence. Using it we prove the *chain theorem*: every join game over a finite carrier has the finite improvement property if and only if the carrier is a chain. We also prove the *aligned-overlaps theorem*: if every pairwise overlap game is an exact potential game, so is the whole configuration (Section 5).
4. An analysis of the CTMU's global stage: "shared teleology" and "mirroring" read as utility alignment (exact potentials), the difference between potential and welfare, logit noise as a mechanism under which "tends to maximize" holds for a potential, and an exact computation of what Howard's metagames, which Langan incorporated into the CTMU, do and do not resolve (Section 6).
5. `lib/games.pal`, a library for finite games written in Palimpsest. Section 9 documents it together with the interpreter's execution model, a traced run and a reproduction protocol. The library covers profiles, Nash equilibria, dominance, Pareto dominance, exact mixed equilibria of 2×2 games, better-response dynamics expressed as rewrite rules that `lib/ars.pal`'s critical-pair checker accepts, termination and reachability analysis, explicit schedules, potential-game tests, and Howard's metagames for two-player games. It is validated against textbook games (`examples/games-basics.pal`).

## 2. The model

**Definition 1 (overlap game).** An overlap game is a tuple $(N, (D_i)_{i \in N}, \sqcup, e, (u_i)_{i \in N})$. Here $N = \{0, \dots, n-1\}$ is a finite set of telors; $D_i \subseteq S$ is the set of contributions available to telor $i$, drawn from a finite carrier $S$; $\sqcup$ is a binary merge on $S$ with neutral element $e$, as in `SEMILATTICE-GRAMMAR.md`; and $u_i : S \to \mathbb{Z}$ is telor $i$'s utility over boundary states. A *profile* is $x = (x_0, \dots, x_{n-1}) \in \prod_i D_i$. Under an arrival order $\pi$ the boundary becomes $\mathrm{fold}(\sqcup, e, x_\pi)$, and telor $i$ receives $u_i$ of that value.

When $(S, \sqcup, e)$ is a bounded semilattice, we write $\bigvee x$ for the outcome, which does not depend on order, and call the game a *join game*. In Palimpsest a join game is the term `(join-game OP E UTIL SETS)`, whose outcome is computed with the `fold-op` function used in the semilattice paper.

**Definition 2 (improvement relation).** For profiles $x, y$ of a finite game, write $x \to y$ if $y$ differs from $x$ only in telor $i$'s strategy and telor $i$'s payoff is strictly higher at $y$. In a join game the payoff at $x$ is $u_i(\bigvee x)$, so the condition is $u_i(\bigvee y) > u_i(\bigvee x)$. In words, one telor, acting alone on its own payoff, strictly improves it. We take this as the reading of "telors freely and independently maximize their local utility functions" as a process.

Section 9 describes how these definitions are executed and how to rerun every computation.

Pure equilibria, dominance, Pareto comparisons and the improvement relation depend on utilities only through comparisons. For these results, a sweep over all weak orders (`all-weak-orders`) covers all preferences. Mixed equilibria (Section 4.3), exact potentials (Sections 5.4 and 6) and logit noise (Section 6.3) are cardinal notions, and the corresponding numbers depend on the particular utility values.

## 3. When is an overlap a game?

### 3.1 The scheduler as a player

A normal-form game requires an outcome function from profiles to outcomes. If the merge depends on arrival order, no such function exists: the outcome depends on $x$ and on $\pi$, and $\pi$ is not chosen by any telor. We therefore add the scheduler as a player whose move is $\pi$. A player is a *dummy* if its move never affects any payoff.

**Proposition 3.1.** In an overlap game whose merge has identity $e$, the scheduler is a dummy for every choice of contribution sets and utilities if and only if $\sqcup$ is commutative and associative on $S$.

*Proof.* If $\sqcup$ is commutative and associative, the fold is invariant under permutation (Theorem 1 of `SEMILATTICE-GRAMMAR.md`), so $\pi$ does not affect the outcome. Conversely, if the fold is not invariant under permutation, there are contributions and two orders that give outcomes $o \neq o'$. Choose telors whose contribution sets contain those contributions, and a telor with $u(o) \neq u(o')$; then the scheduler's move changes a payoff. $\blacksquare$

Commutativity and associativity are therefore required for the telors to be the only players at their overlap. Without them the scheduler can determine the outcome. `examples/telor-games-merge.pal` computes, with `schedule-outcomes`, the set of outcomes the scheduler can produce from one fixed set of contributions:

| merge | contributions | outcomes available to the scheduler |
|---|---|---|
| last-writer-wins | $p, q$ | $\{q, p\}$ |
| first-writer-wins | $p, q$ | $\{p, q\}$ |
| commutative, idempotent, non-associative table | $a, b, c$ | $\{c, b, a\}$ (each contribution can be made the outcome) |
| max | $a, b, c$ | $\{c\}$ |

The first two rows are the telor-left and telor-right rules of `TELIC-CONFLUENCE.md` expressed as merges. Under them the outcome is decided by the scheduler alone.

### 3.2 The axioms and manipulation

A telor, or a coalition of telors, that can influence how its contribution is delivered has more choices than which value to contribute. Each semilattice axiom makes one kind of delivery manipulation irrelevant to payoffs:

| axiom | manipulation it prevents | example when the axiom fails (computed) |
|---|---|---|
| commutativity | timing: arranging to arrive first or last | last-writer-wins: $\{p,q\}$ yields $q$ or $p$ |
| associativity | grouping: a coalition merges privately and submits one value | non-associative table: $\mathrm{fold}[a,b,c] = c$, but if the coalition $\{b,c\}$ submits $b \sqcup c$, then $\mathrm{fold}[a, b\sqcup c] = a$ (under max both give $c$) |
| idempotence | repetition: submitting the same contribution several times | addition: $1+2 = 3$ but $1+2+1 = 4$ (under max, a repeated contribution has no effect) |
| identity $e$ | abstention: not contributing is equivalent to contributing $e$ | (no separate decision whether to participate) |

When an axiom fails, there are two deliveries of the same choices that differ only by the corresponding manipulation and lead to outcomes $o \neq o'$, and a telor that prefers $o'$ gains by carrying out the manipulation. When the axiom holds, the manipulation does not change the outcome and so cannot be profitable. The argument is that of Proposition 3.1, applied to grouping and repetition instead of order. Each correspondence holds given the other axioms, as in `SEMILATTICE-GRAMMAR.md`; for example, idempotence prevents gains from repetition only because commutativity and associativity allow the copies to be brought together. No axiom suffices on its own.

The semilattice theorem can therefore also be read as follows: a bounded semilattice is a merge under which a telor's only strategic variable is the value it contributes. The rest of the paper works in this setting.

## 4. Equilibria of join games

Fix a join game. Its outcome is $\bigvee x$; a telor's contribution can only move the boundary upward in the order; and all telors agree on the result. The question is which results are stable.

### 4.1 The top equilibrium

**Proposition 4.1.** Let $S$ be finite, so that it has a top element $\top = \bigvee S$. If $\top \in D_i$ for at least two telors, every profile in which at least two telors contribute $\top$ is a Nash equilibrium. In particular, every such join game has a pure equilibrium.

*Proof.* If two telors contribute $\top$, a unilateral deviation leaves at least one copy of $\top$, and $x \sqcup \top = \top$, so no deviation changes the outcome. $\blacksquare$

This equilibrium exists for all utilities and is often inefficient. On the chain $\bot < lo < mid < hi$, with telor 0 preferring $lo$ and telor 1 preferring $mid$, the profile $(hi, hi)$ is an equilibrium and is Pareto-dominated by $(lo, mid)$. On the diamond of Section 4.3, $(\top, \top)$ is an equilibrium that six profiles Pareto-dominate. (The checks are labelled `chain-top-trap-*` and `diamond-top-trap-*` in `examples/telor-games-join.pal`.) The semilattice ensures that telors agree, but not that the agreed state is a good one. If $\top$ is read as the over-determined boundary, with every telor asserting everything, then this is a coherent state that no telor prefers, which persists because no single telor can change it.

### 4.2 Chains: when is contributing one's preferred value dominant?

Let $p_i$ maximize $u_i$; we call it telor $i$'s *peak*.

**Proposition 4.2.** Let $D_i = S$, and suppose the other telors' contributions can produce any join $b$ in a set $B \subseteq S$. Then contributing $p_i$ is weakly dominant for telor $i$ if and only if, for every $b \in B$,

$$u_i(p_i \sqcup b) \;=\; \max_{c \,\geq\, b} u_i(c).$$

*Proof.* Given the others' join $b$, the outcomes telor $i$ can produce are $\{x \sqcup b : x \in S\} = {\uparrow} b$, since every $x \sqcup b \geq b$ and every $c \geq b$ equals $c \sqcup b$. Contributing $p_i$ produces $p_i \sqcup b$, so it is a best reply to every $b$ if and only if $p_i \sqcup b$ is optimal on ${\uparrow} b$. $\blacksquare$

**Corollary 4.3 (chains).** On a chain with $B = S$, contributing one's peak is weakly dominant if and only if $u_i$ is weakly decreasing above $p_i$. Utility below the peak is unconstrained. If every telor's utility has this form, the dominant-strategy outcome is $\max_i p_i$, which is Pareto-optimal when each peak is a unique maximum.

*Proof.* On a chain, ${\uparrow} b = [b, \top]$ and $p_i \sqcup b = \max(p_i, b)$. For $b \leq p_i$ the condition holds because $p_i$ is a global maximum. For $b > p_i$ it requires $u_i(b) \geq u_i(c)$ for all $c \geq b$; holding for every $b > p_i$, this is weak decrease above $p_i$. The outcome $\max_i p_i$ is the peak of some telor $k$, and every other outcome is strictly worse for $k$. $\blacksquare$

Only utility above the peak matters, because a telor can only move the boundary upward. The resulting rule, the maximum of the reported peaks, is strategy-proof and anonymous. It is the "best-shot" aggregator of public-goods theory (Hirshleifer 1983), and in Moulin's (1980) characterization of strategy-proof rules on single-peaked domains it is the generalized median with all $n-1$ phantom voters at the top. It is also biased toward the telor with the highest peak, whose preference always determines the outcome. In the computed example, telors with peaks $lo$ and $mid$ and utilities decreasing above them each have their peak as a weakly dominant strategy; the outcome is $mid$, which is not Pareto-dominated. If telor 0's utility is changed to $lo > hi > mid$, its peak is no longer dominant: `dominance-witnesses` returns the profile $(hi, mid)$, at which switching to $lo$ lowers the boundary from $hi$ to $mid$.

### 4.3 Incomparable peaks: an anti-coordination game

Outside a chain, peaks can be incomparable, and then truthful contributions combine to a value neither telor proposed. Consider the diamond $\bot < a, b < \top$ with $a \sqcup b = \top$, which can be read as union on two facts: $a = \{p\}$, $b = \{q\}$, $\top = \{p, q\}$. Telor 0 ranks $a > b > \top > \bot$ and telor 1 ranks $b > a > \top > \bot$, with utilities 3, 2, 1, 0. Each prefers the other's peak to the merged state.

The computation (`examples/telor-games-join.pal`) gives the following.

- Neither peak is weakly dominant. The truthful profile $(a, b)$ produces $\top$ and is not an equilibrium.
- The pure equilibria are $(\bot, b), (a, \bot), (a, a), (b, b), (\top, \top)$, with outcomes $b, a, a, b, \top$. Each is coherent, but they differ in whose preference prevails, and the top equilibrium is among them.

If each telor can only contribute its peak (assert) or $\bot$ (yield), the result is a 2×2 game:

| | telor 1 asserts $b$ | telor 1 yields |
|---|---|---|
| **telor 0 asserts $a$** | $\top$: (1, 1) | $a$: (3, 2) |
| **telor 0 yields** | $b$: (2, 3) | $\bot$: (0, 0) |

**Proposition 4.4.** Let telors 0 and 1 have incomparable peaks $a$ and $b$. Suppose that yielding is better than colliding, $u_0(b) > u_0(a \sqcup b)$ and $u_1(a) > u_1(a \sqcup b)$, and that asserting is better than an empty boundary, $u_0(a) > u_0(\bot)$ and $u_1(b) > u_1(\bot)$. Then the assert/yield game is an anti-coordination game. Its pure equilibria are the two profiles in which one telor asserts and the other yields. In its fully mixed equilibrium, telor $j$ asserts with probability

$$\sigma_j \;=\; \frac{u_i(\text{own peak}) - u_i(\bot)}{\big(u_i(\text{own peak}) - u_i(\bot)\big) + \big(u_i(\text{other's peak}) - u_i(a \sqcup b)\big)} \qquad (i \neq j),$$

the probability that makes telor $i$ indifferent, and the boundary equals $a \sqcup b$ with probability $\sigma_0 \sigma_1$.

*Proof.* Against an asserting opponent the best reply is to yield (first pair of inequalities), and against a yielding opponent the best reply is to assert (second pair). Hence the pure equilibria are the two off-diagonal profiles. Equating telor $i$'s expected payoffs from asserting and from yielding against $\sigma_j$ gives the formula. $\blacksquare$

The hypotheses do not compare a collision with mutual yielding. When both telors prefer the empty boundary to a collision, $u_i(\bot) > u_i(a \sqcup b)$, the game is Chicken (Hawk–Dove) in the usual sense. In the example the order is reversed (collision gives 1, mutual yielding 0), so it is an anti-coordination game but not Chicken. The example files nevertheless name it `hawk-dove`.

Computed with exact rationals (`mixed-2x2`): $\sigma_0 = \sigma_1 = 3/4$, and the collision probability is $9/16$ (`prob-r0c0`). Collision becomes more likely as each telor's gain from asserting rather than leaving the boundary empty grows relative to its loss from a collision. In a deterministic setting a mixed equilibrium can be interpreted as a population frequency or as the telors' beliefs about one another (Section 7.3).

### 4.4 When the top cannot be contributed, equilibria can fail to exist

Proposition 4.1 requires $\top \in D_i$. In the model of `SEMILATTICE-GRAMMAR.md`, telors contribute values from $D$, and the join closure can contain states that no telor can contribute directly. On the diamond, let both telors contribute single facts, $D_0 = D_1 = \{a, b\}$. Telor 0 (*parsimony*) prefers a boundary with a single fact and is indifferent between $a$ and $b$. Telor 1 (*plenitude*) prefers a boundary with both facts. Telor 0 obtains its preferred outcome when the contributions match and telor 1 when they differ, so the game is matching pennies. `pure-nash` returns the empty list, and the only equilibrium is the mixed one at $(1/2, 1/2)$. A convergent merge therefore does not guarantee that any configuration is stable.

## 5. Dynamics: independent improvement as a rewriting system

### 5.1 Correspondence

The relation $x \to y$ of Definition 2 is an abstract rewriting system on profiles, and the standard notions of rewriting correspond to standard notions of game theory:

| rewriting (`TELIC-CONFLUENCE.md`) | game theory |
|---|---|
| normal form | pure Nash equilibrium (no telor can improve alone) |
| termination | finite improvement property, FIP (Monderer and Shapley 1996) |
| confluence | the equilibrium reached does not depend on the order in which telors move |
| critical pair | two improvements from one profile that lead to different equilibria |

`lib/games.pal` implements both sides. `improvement-rules` writes the relation as ground rewrite rules `(rules (rule p q) ...)`, which `lib/ars.pal`'s unmodified `locally-confluent?` and `unjoinable-pairs` accept. `terminating?` decides FIP by repeatedly removing sinks from the improvement graph. `reachable-nash` finds every equilibrium reachable under some order of moves, and `run-schedule` executes one specified order. By Newman's lemma, a terminating and locally confluent improvement system leads from each starting profile to a unique equilibrium. `ars.pal` tests joinability by following one rewrite path from each side, so a `true` verdict is conclusive, but a `false` verdict is conclusive only when the two sides of each failing pair are already normal forms, as in the next subsection. In general `reachable-nash` is the exact test.

### 5.2 Termination without confluence: the assert/yield game

The assert/yield game of Section 4.3 is an exact potential game (`ms-violations` is empty), so improvement always terminates. Its improvement system is

```
(rule (prof a b)     (prof bot b))     (rule (prof a b)     (prof a bot))
(rule (prof bot bot) (prof a bot))     (rule (prof bot bot) (prof bot b))
```

`locally-confluent?` returns `false`, with unjoinable critical pairs `((prof bot b), (prof a bot))`. The rules of `TELIC-CONFLUENCE.md` are

```
(pending ?x ?y) -> (resolved ?x ?x)        (pending ?x ?y) -> (resolved ?y ?y)
```

Both systems have the same structure: one contested overlap with two different stable resolutions, and the order of moves determines which one is reached. `run-schedule` from the collision $(a, b)$ shows this. If telor 0 moves first it concedes, and the boundary settles at $b$; if telor 1 moves first, the boundary settles at $a$. From the empty profile $(\bot, \bot)$ the effect is reversed: the first mover asserts and its peak prevails. The semilattice removes order-dependence from the merge, but order-dependence remains in the play.

### 5.3 The chain theorem

**Theorem 5.1 (chains).** Let $(S, \sqcup, e)$ be a finite bounded join-semilattice. Every join game over $S$, with any number of telors, any contribution sets $D_i \subseteq S$ and any utilities, has the finite improvement property if and only if $S$ is a chain.

*Proof (if).* On a chain, $\bigvee x = \max_i x_i$. We argue by induction on the size of the chain. With one element no improvement is possible. Otherwise, suppose some join game over the chain has an improvement cycle. Let $M$ be the largest outcome on the cycle, and rotate the cycle so that it starts at a profile whose outcome is below $M$. Every improvement changes the outcome, because the mover's payoff changes. Consider a step that raises the outcome to $M$. Before it, all contributions are below $M$; the mover $i$ sets $x_i = M$ and becomes the only telor contributing $M$. While the outcome is $M$, no other telor can change it, since its contributions are at most $M$ and $i$ still contributes $M$. Hence no other telor has an improving move, and the next step is a move by $i$, which must lower $x_i$ to some $y < M$ and give an outcome $o' = \max(y, m) < M$, where $m$, the maximum of the other contributions, is unchanged. Every visit to $M$ is therefore a pair of consecutive moves $o^- \to M \to o'$ by a single telor, with $u_i(o^-) < u_i(M) < u_i(o')$. Replace each such pair by the single move $x_i : \text{old} \mapsto y$, which takes the outcome from $o^-$ to $o'$ and is a strict improvement by transitivity. The result is an improvement cycle that never reaches $M$, that is, a cycle in the join game restricted to the chain $\{s < M\}$, which contradicts the induction hypothesis.

*(only if).* If $S$ is not a chain, it contains incomparable elements $a$ and $b$. Neither is $e$, which is the bottom element, and $\{e, a, b, a \sqcup b\}$ is closed under $\sqcup$. Give two telors $D = \{a, b\}$ and the parsimony and plenitude utilities of Section 4.4 on $\{a, b, a \sqcup b\}$, and give any further telors $D_k = \{e\}$ and constant utility. Then $(a, b) \to (b, b) \to (b, a) \to (a, a) \to (a, b)$ is an improvement cycle. $\blacksquare$

**Corollaries.** On a chain, independent improvement always reaches a pure equilibrium, so a pure equilibrium exists for all contribution sets. Since FIP is equivalent, for finite games, to the existence of a generalized ordinal potential (Monderer and Shapley 1996), every join game over a chain has a function that every strict individual improvement increases.

*Computation* (`examples/telor-games-chain.pal`, about 15 s). Two telors may each contribute any of three elements, and their utilities range over all 13 weak orders, giving 169 games per carrier and covering every pair of ordinal preferences. On the chain $lo < mid < hi$, none of the 169 games lacks FIP. On $\{a, b, \top\}$ with $a$ and $b$ incomparable, 18 of the 169 do. The cycles on the non-chain do not depend on restricting the strategy sets. In the *chase* game (`examples/telor-games-dynamics.pal`), both telors may contribute any of $\{a, b, \bot, \top\}$, and pure equilibria exist (those in which telor 1 contributes $\top$). Nevertheless, the alternating best-response schedule from $(a, b)$, with ties broken by the strategy order $a, b, \bot, \top$, cycles through $(a,b) \to (b,b) \to (b,a) \to (a,a) \to (a,b)$, and the boundary takes the values $\top, b, \top, a, \top$. The tie-breaking rule matters only for this particular schedule; `terminating?` returns `false` because the cycle exists as a sequence of strict improvements under any tie-breaking.

A total order on the possible contributions, in which a larger value always overrides a smaller one, is therefore the structure under which uncoordinated improvement always stops. Contributions with a non-linear structure, such as sets of facts or partial information, allow it to cycle.

### 5.4 Aligned overlaps: potential games

Telors usually take part in several overlaps. We model a configuration as a graphical game (Kearns, Littman and Singh 2001) whose vertices are telors and whose edges are overlaps, with

$$u_i(s) \;=\; v_i(s_i) \;+\; \sum_{j \sim i} f_{ij}(s_i, s_j),$$

where $v_i$ is a private local term and $(f_{ij}, f_{ji})$ is the two-telor game played on the overlap $\{i, j\}$.

**Theorem 5.2 (aligned overlaps).** If every overlap game $(f_{ij}, f_{ji})$ is an exact potential game with potential $P_{ij}$, then

$$\Phi(s) \;=\; \sum_i v_i(s_i) \;+\; \sum_{\{i,j\}} P_{ij}(s_i, s_j)$$

is an exact potential for the whole configuration. Consequently the configuration has the FIP and a pure equilibrium, and every maximizer of $\Phi$ is an equilibrium.

*Proof.* A change in $s_i$ alone changes $v_i$, and for each neighbour $j$ it changes $f_{ij}$ by the same amount as $P_{ij}$, by the definition of an exact potential. No other term of $\Phi$ changes. Hence $\Delta u_i = \Delta \Phi$. FIP and existence follow because $\Phi$ strictly increases along every improvement path and takes finitely many values (Monderer and Shapley 1996; Rosenthal 1973). $\blacksquare$

The simplest case is an overlap that pays both telors the same amount (pure coordination: $f_{ij} = f_{ji}$ and $P_{ij} = f_{ij}$). If every overlap's payoff is shared in this way, independent local maximization converges, and $\Phi$ is a global utility whose changes equal each telor's local gains.

We computed an example on a path of three telors $0 - 1 - 2$ with colors $r$ and $g$, an edge payoff of 2 to both telors for matching colors, and private biases (telors 0 and 1 prefer $r$, telor 2 prefers $g$):

- `is-exact-potential?` with $\Phi$ equal to the biases plus the edge payoffs returns `true`, and `ms-violations` (the four-cycle test of Monderer and Shapley, which needs no candidate potential) reports no violations. `terminating?` returns `true`.
- The pure equilibria are $(r,r,r)$ and $(g,g,g)$, with $\Phi = 6$ and $\Phi = 5$. Independent maximization can stop at the second. From $(r, g, g)$ both equilibria are reachable (`reachable-nash`), and 4 of the 8 starting profiles can reach more than one equilibrium. Convergence is guaranteed, but global optimality and independence from the order of moves are not.

If the overlap $\{0, 1\}$ is made *opposed* (telor 0 receives 2 for matching and telor 1 receives 3 for not matching, a matching-pennies edge), the configuration is no longer a potential game (8 Monderer–Shapley violations). It has no pure equilibrium, and the schedule $1, 2, 0, \dots$ cycles through six profiles back to $(r,r,r)$.

## 6. The global stage

Sections 3–5 model the clause "local telors freely and independently maximize their local utility functions" by itself. The CTMU also describes a global stage. This section collects what the text says about it and gives each statement a game-theoretic formulation, so that the two-stage claim can be tested as a whole.

### 6.1 Statements in the source

| CTMU statement (Langan 2002 unless noted) | game-theoretic formulation | section |
|---|---|---|
| "The primary stage maximizes global generalized utility on an ad hoc basis as local telors freely and independently maximize their local utility functions" | the claim under test: local best responses produce a global optimum | 6.2–6.3 |
| The Telic Principle is "a global (syntactic) invariant that works to minimize the total deviation … as syntactic operators freely and independently bind telesis", "a selection function with a quantitative parameter, generalized utility" | a global objective over configurations; the text does not say whether it acts through the telors (a potential) or on them (selection, mechanism design) | 6.2, 6.5 |
| "localized telic subsystems which mirror the overall system in seeking to maximize (local) utility"; "Individual solipsism becomes distributed solipsism through the mutual absorption of SCSPL syntactic operators, made possible by a combination of distributed SCSPL syntax and shared teleology" | utility alignment: local utilities that track a global one (exact or ordinal potential) | 6.2 |
| "Γ grammar generates SCSPL according to the utility of its sentient processors, including the self-utility of Γ and the utility of its LO relations to telors in A" | a global utility that aggregates the telors' utilities (a welfare function) | 6.3 |
| telic recursion, "though subject to various forms of noise, interference and competition … tends to maximize the utility of the universe and its inhabitants" | noisy best-response dynamics and their long-run distribution | 6.3 |
| elementary objects "are freely and competitively acquired by telons" | competition for shared resources (congestion) | 6.2 |
| "In Noesis 45, the theory of metagames was incorporated into the CTMU", letting players of equal standing "cooperate to achieve mutual benefits" and preventing what a correspondent called a "chaotic exchange of move and counter-move" (*In Clarification of the CTMU*) | Howard's metagames (conditional strategies) | 6.4 |
| volition "is free to be locally out of sync with teleology"; "compensation mechanisms … ensure that teleology remains globally valid" (*CTMU Q and A*) | the claim concerns global outcomes, and local failures are permitted | 6.5 |

### 6.2 Shared teleology as alignment

"Mirroring" and "shared teleology" are qualitative terms. The weakest precise property that would make them imply what the text requires, namely convergence of free and independent local maximization, is that every telor's local gain tracks a single global function. That is an exact potential or, more weakly, a generalized ordinal potential (Monderer and Shapley 1996). The weaker form suffices for convergence; the noise result of Section 6.3 requires the exact form. Under this reading, Theorem 5.2 is a formal version of the CTMU's coherence claim, and it supports the claim: if every overlap is an exact potential game, the configuration has a global function $\Phi$ that every free and independent improvement strictly increases, and independent maximization always terminates. The same holds under a reading of "freely and competitively acquired" as competition for objects. If telors choose which shared objects to acquire, and each telor's payoff is a sum, over the objects it acquires, of a function of the number of telors sharing each object, the result is a congestion game, which always has an exact potential (Rosenthal 1973).

This reading also shows what the text would have to assume. Shared syntax does not suffice. The parsimony/plenitude overlap of Section 4.4 has a semilattice merge and cycles indefinitely, and the opposed path of Section 5.4 applies the same rule everywhere and also cycles. The alignment must hold for the utilities, overlap by overlap.

### 6.3 Which global utility? Potential, welfare and noise

A potential need not be the global utility the CTMU describes. Langan's Γ generates reality "according to the utility of its sentient processors, including the self-utility of Γ and the utility of its LO relations to telors", which is an aggregate of the participants' utilities. Aggregate utility and potential are in general different functions. In the Prisoner's Dilemma (`examples/games-basics.pal`) the exact potential is $\Phi(c,c) = 0$, $\Phi(c,d) = \Phi(d,c) = 2$ and $\Phi(d,d) = 3$, maximized at mutual defection, whereas the sum of utilities is maximized at mutual cooperation (6 against 2). Free and independent local maximization follows the potential, not the sum.

The CTMU mentions noise, and noise makes this difference decisive. Under log-linear (logit) learning, in which a randomly chosen telor selects each option with probability proportional to $e^{u_i/\tau}$, an exact potential game has stationary distribution $\pi(s) \propto e^{\Phi(s)/\tau}$. As the noise level $\tau \to 0$, the system spends almost all of its time at maximizers of $\Phi$ (Blume 1993). We take this as the most suitable formal sense of "tends to maximize" on an "ad hoc basis". It concerns long-run frequencies, not convergence, and it holds for this model of noise; under uniformly distributed mistakes the selected states can differ. It removes the local-optimum problem of Section 5.4: on the path, $\pi(r,r,r)/\pi(g,g,g) = e^{(6-5)/\tau}$. In the Prisoner's Dilemma, however, it selects $(d,d)$.

**Proposition 6.1.** Suppose the local utilities admit an exact potential $\Phi$, and let $W$ be generalized utility. Under logit noise, as $\tau \to 0$ the long-run distribution is supported exactly on the maximizers of $W$ if and only if $\arg\max W = \arg\max \Phi$. When $W$ aggregates the telors' utilities, this equality is a substantive restriction on their utility functions and does not follow from independence.

*Proof.* By Blume's result, the limit distribution is uniform on $\arg\max \Phi$ and zero elsewhere. It is supported exactly on $\arg\max W$ if and only if the two sets are equal. $\blacksquare$

One known way to satisfy the condition is to give each agent its marginal contribution to the global utility as its own utility, $u_i(s) = W(s) - W(\emptyset_i, s_{-i})$, which makes $W$ an exact potential (Wolpert and Tumer 2002). Langan's "localized telic subsystems which mirror the overall system" are consistent with this design, but the text does not specify it.

### 6.4 Metagames

Langan's Noesis writings discuss a cycle of the same kind as those in Section 5. In the Newcomb setting he describes a player whom "game theory has led … in a circle that may repeat endlessly", as each side changes its move in response to the other, and he resolves the cycle with "the theory of metagames", Howard's (1971) extension in which strategies are conditional ("if I expect you to play $y$, I play $f(y)$") and are nested in levels. When one player dominates the other, he refers instead to his resolution of Newcomb's paradox. He also notes that "if strategic collectivization were enforced by projection from the programmatic level, defection would be impossible, and this would indeed ensure a joint optimum." `lib/games.pal` constructs Howard's metagame 21G, in which player 1 conditions on player 0's conditional strategies (4 × 16 profiles for a 2×2 game), and the mirror game 12G. It reports the outcomes sustained by their pure equilibria and the symmetric outcomes sustained in both (`examples/telor-games-metagame.pal`):

| game | Nash outcomes | 21G | 12G | symmetric |
|---|---|---|---|---|
| Prisoner's Dilemma | $(d,d)$ | $(c,c), (d,d)$ | $(c,c), (d,d)$ | $(c,c), (d,d)$ |
| assert/yield (Section 4.3) | $(a,\bot), (\bot,b)$ | same | same | $(a,\bot), (\bot,b)$ |
| parsimony vs plenitude (matching pennies) | none | $(a,a), (b,b)$ | $(a,b), (b,a)$ | none |

In the Prisoner's Dilemma, the case for which Langan used them, metagames behave as he describes: mutual cooperation becomes a sustainable outcome. This reduces the difference between welfare and potential noted in Section 6.3 for this game but does not remove it, since mutual defection also remains sustainable and nothing selects between the two. In the other two games metagames do not resolve the problem. In the assert/yield game they sustain exactly the pure Nash outcomes, so the choice between the two settlements is unchanged. In matching pennies they produce stable outcomes, but which telor wins is determined entirely by which one is at the top of the conditional hierarchy, and no outcome is sustained under both orders. The order-dependence found in `TELIC-CONFLUENCE.md` thus reappears as dependence on the order of the metagame hierarchy. This qualifies Langan's statement that when neither player dominates, "there exists a jointly accessible algorithm which lets them cooperate to achieve mutual benefits". In a strictly competitive overlap there is no mutual benefit, and in the assert/yield game there is no unique one. In both cases the asymmetry needed to select an outcome must come from a higher level, "projection from the programmatic level", which is again the global stage.

### 6.5 Assessment of the two-stage claim

The CTMU's claim that free and independent local maximization realizes global maximization of generalized utility has a precise version that is true. The following conditions are jointly sufficient for it and are the set closest to the text; we do not claim that they are necessary.

1. A semilattice merge, so that overlaps are well-posed games (Section 3).
2. Utilities that are aligned, overlap by overlap, into an exact potential (Theorem 5.2). This is one precise meaning "shared teleology" could have. An ordinal potential would suffice for convergence but not for condition 3, because logit noise need not favor the maximizers of an ordinal potential.
3. Noise of the logit kind, so that the long-run distribution favors the maximizers of the potential rather than whichever equilibrium the schedule reaches (Section 6.3).
4. A potential whose maximizers are those of generalized utility; when generalized utility aggregates the telors' utilities, this constrains their utility functions (Proposition 6.1).

Each condition is consistent with the text, and none is stated in it as a rule. Where a condition fails, the CTMU relies on a global "selection function" or "compensation mechanism" that acts on the telors rather than through them. In game-theoretic terms this is mechanism design or equilibrium selection by an authority other than the telors, that is, a coordinator in the sense of `TELIC-CONFLUENCE.md`. That paper's narrower finding, that independent local rules alone do not ensure agreement, therefore stands. Its original stronger statement, that the CTMU supplies no coordinating principle, is not supported by the text, and that paper now includes a revision note to this effect. The CTMU posits a coordinating principle, the Telic Principle, but does not specify how it operates.

## 7. Discussion

### 7.1 Summary of answers

Independent telors can be treated as players, and doing so separates several questions that the earlier analyses did not distinguish.

| question | condition that settles it | remaining failure |
|---|---|---|
| Do telors agree on the merge of given contributions? | bounded semilattice (`SEMILATTICE-GRAMMAR.md`) | — |
| Is the overlap a game among the telors (scheduler a dummy)? | commutativity and associativity (Prop. 3.1) | — |
| Can telors manipulate delivery? | the four axioms (Section 3.2) | — |
| Is some configuration stable? | $\top$ can be contributed (Prop. 4.1); chains (Thm. 5.1); aligned overlaps (Thm. 5.2) | no pure equilibrium (Section 4.4) |
| Is the stable configuration efficient? | dominance on chains (Cor. 4.3); logit noise in potential games (6.3); metagames for Prisoner's Dilemma-type conflicts (6.4) | top equilibrium; Pareto-dominated equilibria; potential differs from aggregate utility |
| Does independent improvement stop? | chains (Thm. 5.1); aligned overlaps (Thm. 5.2) | improvement cycles on non-chains and opposed overlaps |
| Does the stopping point depend on the order of moves? | a unique reachable equilibrium (confluence); logit noise in the long run | assert/yield critical pair; multiple equilibria; order of the metagame hierarchy |

### 7.2 Three failure modes

`TELIC-CONFLUENCE.md` gave "independent and mutually irrelevant subrealities" one formal meaning: unjoinable normal forms of the merge. A semilattice merge excludes that case. The game-theoretic analysis shows three further failure modes, each compatible with a semilattice merge. In the CTMU's terms these are local deviations, which the text permits ("deviations from perfect complementarity are ubiquitous"); they contradict the global claim only if the global stage cannot compensate for them.

1. *Over-determination*: agreement on a state that no telor prefers (the top equilibrium; collision with probability $9/16$ in the mixed equilibrium of the assert/yield game).
2. *Order-dependent outcomes*: the improvement system terminates but is not confluent. Several coherent configurations are reachable, and the order of moves, not any telor, determines which is reached. This is the telor-left/telor-right critical pair, now arising in the improvement dynamics.
3. *Non-termination*: there is no pure equilibrium, or improvement cycles exist, so the configuration never settles (matching pennies, the chase game, the opposed path).

### 7.3 Limitations

- *Utilities are assumed, not derived.* The CTMU gives no explicit form for telors' utility functions, so every result here is either universal (holding for all utilities, as in Theorem 5.1 (if), Proposition 3.1 and Theorem 5.2) or existential (holding for some utilities, as in the counterexamples). The utilities in the worked examples are illustrations and were chosen to be simple.
- *Interpretations of the text.* Section 6 associates qualitative CTMU statements ("mirror", "shared teleology", "noise", "selection function") with the weakest precise properties that would support the claims the text makes. Other formalizations are possible; any of them can be stated as a game and checked in the same way.
- *Mixed equilibria in a deterministic setting.* The figures $3/4$ and $9/16$ are equilibrium beliefs or population frequencies, not objective probabilities. The same applies to the logit distribution of Section 6.3.
- *Complete information.* We assume that each telor's payoff is a known function of the profile. Independent telors may well not know each other's utilities, which suggests Bayesian games and learning dynamics (fictitious play, regret matching) as a next step. Such dynamics are known to converge in potential games but not in general.
- *Cooperative structure* is considered only through the grouping manipulation and metagames. A coalitional analysis (core, Shapley value) of overlapping telors remains open.
- *Finite carriers.* All computations use finite sets, and the proof of Theorem 5.1 uses finiteness both for the largest outcome on a cycle and for the induction on the size of the chain.

## 8. Conclusion

Independent telors can be analyzed as players in a game, and game theory makes clear what the semilattice theorem does and does not establish. A semilattice merge is the condition under which an overlap is a well-posed game without manipulation of delivery. Within that game, equilibria can be inefficient (the top equilibrium), contested (the assert/yield game) or absent (matching pennies). Independent improvement always terminates if and only if contributions are totally ordered, and it terminates more generally when local utilities share an exact potential. Even then, the configuration reached can depend on the order of moves, which reproduces in the dynamics the unjoinable critical pair that `TELIC-CONFLUENCE.md` found in the merge.

The CTMU does not claim that local telors achieve coherence without help; it assigns this to a global stage. On the readings above, that stage requires aligned utilities, logit-type noise and a potential that agrees with generalized utility, or else a selection mechanism that acts on the telors. The text mentions each of these elements but specifies none of them. Metagames, the one game-theoretic device the CTMU adopts, resolve the Prisoner's Dilemma but not equilibrium selection or strictly competitive overlaps.

## 9. Methods: Palimpsest

Every computed claim in this paper is produced by Palimpsest, the term-rewriting language in this repository, and checked by `./verify-games.sh`. This section provides what is needed to rerun the computations and interpret their output: the interpreter's execution model (9.1), the construction of the games library (9.2), a traced execution (9.3), the meaning of each kind of result (9.4) and the reproduction protocol (9.5). Section 9.6 compares Palimpsest with Langan's SCSPL and describes how this work extends the CTMU.

### 9.1 The execution model

*Terms.* All data and all code are terms: a symbol (`top`, `prof`), an integer, a string, or a parenthesized list of terms. A profile `(prof a b)`, a Cayley table `(rules (rule (op a b) top) …)`, a fraction `(frac 3 4)` and a game `(join-game OP E UTIL SETS)` are ordinary terms. Code and data are distinguished only by whether a rule matches them.

*Rules.* A program line `rule NAME : LHS => RHS [where C1, C2, …]` states that any subterm matching `LHS` may be replaced by the corresponding instance of `RHS`. Pattern variables are `?x`, which matches one subterm, and `?xs...`, which matches zero or more list elements. A variable that occurs twice must match equal terms (non-linear matching); this is how `(equal? ?x ?x) => true` works. A `where` clause is either a guard, which must normalize to `true`, or a binding `?v <- EXPR`, which normalizes `EXPR` and binds the result. Clauses are evaluated from left to right, always with `outermost(prim + rules)`, which is also the main strategy in every program here. When several rules match, the first in load order is used. An `import` inserts the library's rules at the position of the `import` line, so library rules precede the program's own. The engine skips rules whose head symbol cannot match; this affects speed but not which rule is applied.

*Strategy.* Rules state what may be rewritten, and a strategy states where and in what order. Every program in this paper uses

```
strategy solve = outermost(prim + rules)
```

At each step this finds the leftmost-outermost subterm to which either a built-in primitive or a rule applies, rewrites that subterm once, and repeats until no subterm can be rewritten. The primitives (`prim`) are integer `+ - * / mod`, comparisons, `=` and `<>` on atoms, `abs` and a few others, and apply only to literal values; among rules (`rules`), the first match in load order is used. This is normal-order reduction. It allows `if`-guarded recursion to terminate, and it is lazy: an argument is evaluated only when a rule needs its form. For this reason the library evaluates values with `where ?v <- EXPR` before comparing them or selecting a rule by their form (Section 9.2).

*Fuel.* Each successful rewrite, by a rule or a primitive, consumes one unit of fuel, including rewrites performed while evaluating `where` clauses, which share the same budget. Failed match attempts consume none. A program sets its budget with `#fuel N`; when the budget is exhausted the run stops with an error and prints no partial result. Evaluation is deterministic, so the amount of fuel used is the same on every run of the same program and serves as a fingerprint (Section 9.5).

*Program files and output.* Each example has the following form:

```
#lang palimpsest
#mode run-only                      // never writes any file
#fuel 20000000
import "../lib/games.pal"           // also imports ars.pal and the prelude
strategy solve = outermost(prim + rules)
rule …                              // the game: strategy sets, payoffs or utilities
main = (report (label1 EXPR1) (label2 EXPR2) …)
run solve
```

`run solve` normalizes `main` and prints `run: <main> ==> <normal form>` followed by `fuel remaining: N`. No rule mentions `report` or the labels, so they remain in the normal form, which is therefore a labelled list of results, for instance `(report (hawk-dove-mixed (mixed (frac 3 4) (frac 3 4))) …)`. `verify-games.sh` runs each example and checks with `grep -F` that each expected `(label value)` string occurs in the output.

*Determinism and confluence.* Because the strategy is deterministic, a run always returns a single result, even when the rule set is not confluent. For example, normalizing `(prof a b)` under the improvement rules of the assert/yield game returns `(prof bot b)` and gives no indication that `(prof a bot)` is also reachable. Non-confluence is therefore never inferred from a single run. It is established by enumerating alternatives: the critical pairs (`unjoinable-pairs`), every equilibrium reachable under some order of moves (`reachable-nash`), or explicitly specified alternative orders (`run-schedule`). The interpreter's own strategy plays the role of the scheduler of Section 3.1, and these functions are designed to examine the outcomes it does not choose.

### 9.2 Construction of `lib/games.pal`

*Games as open definitions.* A game is any term `G` for which the program supplies `(strategy-sets G)` and `(payoff G i PROFILE)`. This follows the open-application convention of the standard library, in which `map` calls `(app F x)` and the program defines `F` by rules. Higher-order arguments are tagged terms that carry their parameters, such as `(no-gain G i u)` or `(set-comp i p)`, each interpreted by an `(app …)` rule. Quantifiers such as "for every deviation" are written in this way, for example `(all-of (no-gain G i u) deviations)`.

*Join games.* `(join-game OP E UTIL SETS)` computes a payoff by merging the profile and applying the utility. If `OP` is a Cayley table `(rules (rule (op x y) z) …)`, the merge is computed by `fold-op` from `lib/ars.pal`, the code used in `SEMILATTICE-GRAMMAR.md`; each `(op x y)` is rewritten by `ars.pal`'s data-level rewriter, which finds the matching row with the primitive `match-witness`. If `OP` is a symbol, the program supplies `(merge NAME x y)` rules, which run as ordinary rules. Both forms give the same outcomes. On the 4×4 diamond game, enumerating the pure equilibria takes 29,304 rewrites with the table and 4,024 with the named merge, about seven times fewer; the named form is used for the exhaustive sweep and the 64-profile metagames for this reason. `OP` is evaluated before the library selects a branch by its form. An earlier version selected the branch first, so a game written with an unevaluated table, such as `(join-game (diamond) …)`, took the wrong branch and was not reduced. The published examples always evaluate the table first and were not affected. Utilities are given either by rules `(utility NAME i x) => n` or by a table `(utab (list TABLE0 TABLE1 …))`.

*Algorithms.* Each analysis is an exhaustive computation over the finite profile space; no sampling or heuristics are used.

| function | algorithm |
|---|---|
| `profiles` | Cartesian product of the strategy lists, in list order |
| `pure-nash` | the profiles at which no player has a strictly better unilateral deviation |
| `weakly-dominant?` | for every profile $p$: $u_i(p[i{:=}s]) \geq u_i(p)$ |
| `improvements` | all strict unilateral improvements, player 0 first, each player's deviations in strategy-list order |
| `improvement-rules` | those improvements as ground rules `(rule p q)`, that is, a rule set represented as a term |
| `terminating?` | repeatedly remove profiles all of whose improvements lead outside the remaining set (as in Kahn's algorithm); a non-empty set that cannot be reduced further contains a cycle |
| `reachable-nash` | depth-first search of the improvement graph from one profile, collecting sinks |
| `run-schedule` | at each scheduled step the named player moves to its first strictly best deviation, or does not move |
| `ms-violations` | for every profile, pair $i<j$ and alternatives $a,b$: sum the movers' payoff changes around $p \to p[i{:=}a] \to \cdot[j{:=}b] \to \cdot[i{:=}p_i] \to p$ |
| `mixed-2x2` | indifference conditions solved in exact integer arithmetic and reduced by `gcd` |
| `meta21` | player 0's strategies are tuples `(fn v…)` (functions $S_1 \to S_0$); player 1's are tuples indexed by player 0's tuples; a profile is evaluated by position lookup |
| `count-cyclic-2` | `terminating?` over all pairs of utility tables, as an accumulator loop |

`improvement-rules` computes a rule set from the players' utilities and passes it, as a term, to the critical-pair functions of `ars.pal` (`unify`, `critical-pairs`, `unjoinable-pairs`). Those functions were written for `TELIC-CONFLUENCE.md` and are used here without modification, so the comparison in Section 5.2 between the assert/yield rules and the telor-left/telor-right rules is made by the same code. As noted in Section 5.1, `ars.pal` tests joinability along one rewrite path, so its `false` verdict is conclusive only when the competing results are normal forms, as they are in that case.

*Cost.* Each `outermost` step searches the term from the root, and terms are copied as they are rewritten, so the cost of a step grows with the size of the term. A computation that builds a large intermediate term pays for its size on every step; the cost is superlinear overall, and `README.md` ("Honest prototype caveats") estimates bulk list operations as roughly cubic. In an early version of the sweep, building the list of 729 pairs of utility tables as a single term took about 26 seconds for about 4,000 rewrites. The library avoids this in two ways: long iterations are accumulator loops whose per-item work is done inside a `where` binding, and so is evaluated as a separate small term (`count-cyclic-2`, `dedup`, `rn-go`), and the computation for one game never holds more than one game.

### 9.3 A traced execution

Consider telor 0's payoff in the assert/yield game at the collision profile, `(payoff G 0 (prof a b))`, with `G = (join-game DIAMOND bot rivals (list (list a bot) (list b bot)))`. Under `solve`:

1. `join-payoff` matches. Its `where` clause evaluates `(outcome G (prof a b))`, which `join-outcome` rewrites to `(join-fold OP bot (list a b))` after evaluating `OP` to the table.
2. `join-fold-table` matches the `(rules …)` form and rewrites the term to `(fold-op OP bot (list a b))`.
3. `fold-op-n` evaluates `(apply-op OP bot a)`, which is `ars.pal`'s `(normalize (op bot a) OP)`. `rewrite-root` scans the table, and `(match-witness (op bot a) (op bot a))` succeeds on the row `(rule (op bot a) a)`, so this step returns `a`. For a row containing variables, `match-witness` returns the substitution; for the pattern `(op bot ?x)` it returns `(some (dict (entry x a)))`.
4. The fold continues with `(apply-op OP a b)`, which matches the row `(rule (op a b) top)`, so the outcome is `top`.
5. `join-payoff` rewrites the term to `(utility rivals 0 top)`, and the program's rule `u-d0t` gives `1`.

Intermediate values can be inspected by adding a line such as `show (fold-op (diamond) bot (list a b)) with solve` to an example; this one prints `top`. All results in the paper are built from steps of this kind; for example, `pure-nash` evaluates this payoff for every profile and every unilateral deviation.

### 9.4 Interpreting the output

| output term | meaning | section |
|---|---|---|
| `(prof s0 s1 …)` | a profile in which player $i$ plays $s_i$ | throughout |
| `(list …)` | a list or set in enumeration order; `(list)` is empty, e.g. when there is no pure equilibrium | 4.4, 5.3 |
| `(mixed (frac n d) (frac n' d'))` | fully mixed 2×2 equilibrium: the probability that player 0 plays its first strategy, and the probability that player 1 plays its first strategy | 4.3 |
| `(frac n d)` | an exact reduced fraction | 4.3 |
| `(rules (rule p q) …)` | the better-response relation as a term; each rule is one telor's strict improvement | 5.2 |
| `(pair p q)` in `unjoinable-pairs` | a critical pair: two improvements from one profile with different normal forms | 5.2 |
| `true` / `false` | the value of a decided property (`terminating?`, `is-exact-potential?`, `nash?`, …) | 4–6 |
| `(ms-cycle p i a j b SUM)` | a Monderer–Shapley four-cycle with non-zero payoff sum; `ms-violations` lists them, and the paper reports their number | 5.4 |
| an integer | a count (sweeps, violations, starting profiles with several reachable equilibria) or a potential value | 5.3, 5.4 |

Each label identifies the claim it supports. For example, `(path-nash-potentials (list 6 5))` corresponds to the statement that the equilibria $(r,r,r)$ and $(g,g,g)$ have $\Phi = 6$ and $\Phi = 5$. All expected outputs are listed in `verify-games.sh`.

### 9.5 Reproduction protocol

*Environment.* The interpreter consists of about 3,200 lines of Rust with no external crate dependencies. It was built with `rustc` and `cargo` 1.97.0 (edition 2021, release profile with `opt-level = 2`). The Palimpsest libraries used are `lib/games.pal` (377 lines, 138 rules), `lib/ars.pal` and the prelude. No run writes any file; every example uses `#mode run-only`.

*Steps.*

```sh
cargo build --release
./verify-games.sh                          # 6 programs, about 50 s; prints PASS or FAIL for each
python3 crosscheck/games_crosscheck.py     # independent recomputation, under 1 s, standard library only
```

*Fingerprints.* Evaluation is deterministic, so the fuel used is reproducible exactly for this version of the repository; it changes if the library or the examples change. The times were measured on one machine and are indicative only.

| program | fuel budget | fuel used | time |
|---|---|---|---|
| `games-basics.pal` | 5,000,000 | 5,627 | < 0.1 s |
| `telor-games-merge.pal` | 5,000,000 | 5,769 | < 0.1 s |
| `telor-games-join.pal` | 20,000,000 | 99,450 | 1.1 s |
| `telor-games-dynamics.pal` | 20,000,000 | 197,091 | 3.5 s |
| `telor-games-chain.pal` | 400,000,000 | 1,076,542 | 15 s |
| `telor-games-metagame.pal` | 200,000,000 | 1,190,920 | 26 s |

*Independent recomputation.* `crosscheck/games_crosscheck.py` shares no code with the library. It implements the necessary game theory by brute force in Python and recomputes:
- every equilibrium set, including all 21G and 12G metagame outcome sets;
- the counts of 0 and 18 games out of 169;
- the 4 starting profiles with more than one reachable equilibrium;
- the potentials;
- the logit stationary distributions of Section 6.3, by power iteration, including the ratio $\pi(r,r,r)/\pi(g,g,g) = e^{1/\tau}$ and the concentration on $(d,d)$ in the Prisoner's Dilemma. These are the only results not computed in Palimpsest, which has no exponential function.

*Modifying the analysis.* To examine a different preference, edit the relevant `utility` rule and rerun the example. To analyze a new game, write `strategy-sets` and `payoff` rules, or a `join-game` with a table or a named merge, and add entries such as `(label (pure-nash G))` and `(label (terminating? G))` to `main`. An out-of-fuel error means the budget is too small and `#fuel` should be increased. A result that remains partly unreduced, such as `(utility rivals 0 …)`, means that some rule did not match; usually a utility value is missing for some outcome, or a value was not evaluated before a rule that depends on its form was applied.

### 9.6 Palimpsest and the CTMU

*Common features.* Langan describes reality as a "Self-Configuring Self-Processing Language" whose grammar Γ is "unlike an ordinary grammar in that its processors, products and productions coincide and are mutually formed by telic recursion". Palimpsest is a much smaller system that shares some formal features with this description, and the analysis in this paper depends on them:
- productions and products are objects of the same kind, since a rule set is a term that other rules can construct, inspect and rewrite (`ars.pal`, `improvement-rules`);
- the matcher that decides which production applies is available as a function (`match-witness`);
- a program can rewrite its own source file until it reaches a fixed point, which gives the language's quines (`README.md`, `SELF-REWRITING.md`).

The central construction of this paper corresponds to Langan's description of Γ's production rules, which "include the Telic Principle, distributed elements of syntax formed in the primary phase of telic recursion, and more or less polymorphic telons formed by agent-level telors". `improvement-rules` computes a set of production rules from the agents' utilities; the telors' preferences thereby define a rewrite grammar, which is analyzed with the same functions as any other grammar. Langan also writes that "non-global processors alternate between the generation and selective actualization of possible productions". In the implementation these are separate components:
- `improvements` generates the possible productions;
- a strategy (`outermost`, or the schedule given to `run-schedule`) selects one of them.

The questions of Sections 5 and 6 all concern how this selection is made.

*Differences.* Palimpsest is not an implementation of SCSPL, and nothing here models telesis, infocognition, conspansion or the Telic Principle itself.
- The rule set is fixed when the program is loaded. A run changes terms but not its own rules; a program can change its rules only by rewriting its source file, which affects later runs and requires explicit file-write permissions.
- The strategy is chosen by the programmer, outside the rules. Sections 3.1 and 6.5 treat a scheduler of this kind as an authority other than the telors in CTMU terms, and Palimpsest needs one in order to run.
- All carriers and utilities are finite and specified by hand.

Palimpsest is therefore a tool for stating parts of the CTMU precisely and checking them. It is not a model of the theory as a whole, and its results have no bearing on the CTMU's claims about consciousness, theology or cosmology.

*Extension of the CTMU.* The CTMU states telic recursion in prose: a global stage maximizes generalized utility "as local telors freely and independently maximize their local utility functions". This paper adds four things not present in that description:
1. a formal model, in which overlaps are join games and improvement dynamics form a rewriting system;
2. theorems about the model, including the well-posedness condition (Proposition 3.1), the dominance and top-equilibrium results (Section 4), the chain theorem (Theorem 5.1), the aligned-overlaps theorem (Theorem 5.2) and Proposition 6.1, which relates the potential to generalized utility;
3. tests of the coordinating mechanisms the CTMU itself names: shared teleology read as alignment, logit noise, and Howard's metagames, which Langan adopted;
4. machine checks: every computed claim is produced by Palimpsest and recomputed by an independent implementation, except the logit distributions, which only the independent implementation computes. The theorems are proved; computation checks their finite instances.

The extension depends on the interpretations adopted in Section 6: where a qualitative phrase is given a precise meaning, the results hold for that meaning. Within that limit, the paper turns the two-stage account of telic recursion into a claim that can be checked, gives sufficient conditions under which it holds, and identifies cases in which each of the named mechanisms fails.

This is the fourth Palimpsest study of a CTMU mechanism; a fifth, `LOGOS-SCSPL.md`, compares SCSPL with language-model processing. The earlier ones are:
- `CTMU.md` and `NONSUBSUMPTION.md`, on topological and descriptive containment, with conspansion modelled as a verified limit cycle;
- `TELIC-CONFLUENCE.md`, which shows that local overlap resolution is not confluent;
- `SEMILATTICE-GRAMMAR.md`, which characterizes the merges under which independent resolution converges.

Each study takes one claim of the CTMU, gives it a precise meaning in the same term language, and checks it with code that later studies reuse. This paper uses `ars.pal` from the confluence study and `fold-op` from the semilattice study.

---

## References

1. Christopher M. Langan, "The Cognitive-Theoretic Model of the Universe: A New Kind of Reality Theory" (2002).
2. Christopher M. Langan, collected writings in *The Portable Chris Langan*: "CTMU Q and A" (compensation mechanisms), the correspondence answering a reader ("Mackenzie") on wholeness and the coherence of the universe's wave function, "Noesis Discussion #1" (Newcomb's paradox and metagames), and "In Clarification of the CTMU and its Applications in Noesis" (metagames incorporated into the CTMU).
3. John Nash, "Non-Cooperative Games," *Annals of Mathematics* 54.2 (1951).
4. Robert W. Rosenthal, "A Class of Games Possessing Pure-Strategy Nash Equilibria," *International Journal of Game Theory* 2 (1973).
5. Dov Monderer and Lloyd S. Shapley, "Potential Games," *Games and Economic Behavior* 14 (1996): exact and ordinal potentials, the finite improvement property, and the four-cycle characterization used by `ms-violations`.
6. Hervé Moulin, "On Strategy-Proofness and Single Peakedness," *Public Choice* 35 (1980).
7. Jack Hirshleifer, "From Weakest-Link to Best-Shot: The Voluntary Provision of Public Goods," *Public Choice* 41 (1983).
8. Michael Kearns, Michael L. Littman, and Satinder Singh, "Graphical Models for Game Theory," *UAI* (2001).
9. Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski, "Conflict-free Replicated Data Types," *SSS* 2011, LNCS 6976.
10. Gérard Huet, "Confluent Reductions," *JACM* 27.4 (1980); M. H. A. Newman, "On Theories with a Combinatorial Definition of 'Equivalence'," *Annals of Mathematics* 43.2 (1942).
11. Nigel Howard, *Paradoxes of Rationality: Theory of Metagames and Political Behavior*, MIT Press (1971).
12. Lawrence E. Blume, "The Statistical Mechanics of Strategic Interaction," *Games and Economic Behavior* 5 (1993).
13. David H. Wolpert and Kagan Tumer, "Collective Intelligence, Data Routing and Braess' Paradox," *Journal of Artificial Intelligence Research* 16 (2002).
14. This repository: `TELIC-CONFLUENCE.md`, `SEMILATTICE-GRAMMAR.md`, `lib/ars.pal`, `lib/games.pal`.

## Appendix A: Reproducing the results

The full protocol, the fingerprints and a guide to the output are in Section 9.5. The commands are:

```sh
cargo build --release
./verify-games.sh                                         # all six programs, checked (about 50 s)
python3 crosscheck/games_crosscheck.py                    # independent recomputation (under 1 s)
./target/release/palimpsest examples/games-basics.pal         # library against PD, matching pennies, BoS
./target/release/palimpsest examples/telor-games-merge.pal    # Section 3
./target/release/palimpsest examples/telor-games-join.pal     # Section 4
./target/release/palimpsest examples/telor-games-dynamics.pal # Sections 5.2, 5.3 (chase), 5.4
./target/release/palimpsest examples/telor-games-chain.pal    # Theorem 5.1, exhaustive sweep
./target/release/palimpsest examples/telor-games-metagame.pal # Section 6.4 (and the PD potential of 6.3)
```

## Appendix B: Functions of `lib/games.pal`

A game is any term `G` with rules for `(strategy-sets G)` and `(payoff G i (prof s0 s1 ...))`. Join games, `(join-game OP E UTIL SETS)`, provide both from a merge (a Cayley table, or a named merge defined by rules) and a utility (rules, or a table `(utab ...)`).

| function | returns |
|---|---|
| `profiles`, `deviations`, `payoffs` | the strategy space and payoff vectors |
| `pure-nash`, `nash?`, `best-response?` | pure equilibria |
| `weakly-dominant?`, `dominance-witnesses` | dominance, with profiles at which it fails |
| `pareto-dominators`, `pareto-dominated?` | Pareto comparisons |
| `mixed-2x2`, `prob-r0c0`, `frac-mul` | exact mixed equilibrium of a 2×2 game |
| `improvements`, `improvement-rules` | the better-response relation, as a term for `ars.pal` |
| `terminating?`, `reachable-nash`, `schedule-dependent-starts` | FIP, reachable equilibria, starting profiles with several reachable equilibria |
| `run-schedule` | best-response trajectory under a specified schedule |
| `is-exact-potential?`, `ms-violations` | potential-game tests |
| `outcome`, `outcomes-of`, `schedule-outcomes` | merge outcomes and the outcomes available to the scheduler |
| `all-weak-orders`, `count-cyclic-2` | exhaustive sweeps over ordinal preferences |
| `meta21`, `swap`, `meta21-outcomes`, `meta12-outcomes`, `symmetric-meta-outcomes` | Howard metagames of a two-player game |
