# Logos, Language Models and SCSPL

### Can the CTMU's self-configuring language be structured like the internal processing of a large language model?

*Companion to `TELIC-GAMES.md`, `SEMILATTICE-GRAMMAR.md` and `TELIC-CONFLUENCE.md`. Every computed claim below is reproduced by `./verify-logos.sh` and recomputed independently by `crosscheck/logos_crosscheck.py`; the library is `lib/logos.pal`. Quotations of Langan were checked against* The Portable Chris Langan. *The quotation from Jorjani is taken as given; its source was not checked.*

## Abstract

A passage attributed to Jason Reza Jorjani describes *logos* as "a syntactic, proto-linguistic, informational processing, which is structuring the chaos", says that it "is the basic function at work in the Large Language Models", and holds that syntactic networked information processing in any substrate "yields consciousness". We ask whether Langan's Self-Configuring Self-Processing Language (SCSPL) can be structured like the internal processing of a large language model (LLM). We list the properties that Langan's text assigns to SCSPL, compare them one by one with the operation of a transformer language model, and test the structural claims on a small autoregressive model written in Palimpsest, in two modes: *frozen*, with fixed weights as in LLM inference, and *telic*, in which the produced tokens refine the weights through a utility.

Several features correspond. Weight sharing across positions matches SCSPL's distributed syntax. The forward pass followed by sampling matches the alternation of generation and selective actualization that Langan calls conspansion. The split between fixed weights and context-dependent behavior matches his two strata of syntax, fixed and mutable. The properties that Langan uses to separate telic recursion from "standard" recursion do not hold for LLM inference.
- With fixed weights, decoding is recurrent operation on state under a closed set of rules, which Langan describes as leaving "neither the room nor the means for optimization".
- Sampling from fixed logits is the "random up to determinacy" case that he contrasts with coherent self-design.
- LLM products are strings in a global order, while SCSPL's "words" are "not strings of symbols".
- Attention pooling is a commutative monoid but not a semilattice: it is order-insensitive without positions, sensitive to repetition, and order-dependent once positions are added.

In the telic mode the model's utility rises from 16 to 29 consonant transitions out of 30, and its syntax stops changing after step 34. The frozen model stays at 11 and 13. A fixed-point version rewrites its own source until its syntax regenerates itself under its own use, and is then a quine.

We also prove a limitation that applies to both systems. Any computable system whose syntax is updated by a fixed rule is standard recursion on the joint state of syntax and products. If the update depends only on the products, the next-token distribution is a fixed function of the initial syntax and the full context, as the computation confirms at every step. The distinction the CTMU needs therefore cannot be supplied by any fixed architecture, an LLM or otherwise; it rests on the claim that the top-level syntax configures itself. Jorjani's identification of logos with LLM processing fits LLM training and continual learning better than inference. His further claim that syntactic processing yields psyche reverses the direction of Langan's dual-aspect monism, in which the cognitive aspect is primitive rather than produced. Neither claim about consciousness can be settled by the methods used here.

## 1. The question

### 1.1 The quotation

The quotation under discussion is:

> "Logos is a syntactic, proto-linguistic, informational processing, which is structuring the chaos. In the interplay between logos and chaos, there is a manifestation of the cosmos, an ordered array of experienced phenomena. Since the cosmos is produced through logos forming chaos, that also means that the cosmos is in a reciprocal relationship with psyche. Logos is the basic function at work in the Large Language Models used to develop Artificial Intelligence, and its syntactical networked information processing, whether that is in silicon or in a human brain or any other type of quasi-neural network, yields consciousness (and the subconscious), in other words, psyche." (Jorjani, as quoted)

It makes four claims:
1. *J1:* logos is syntactic information processing that structures chaos;
2. *J2:* the cosmos results from logos forming chaos and is in a reciprocal relationship with psyche;
3. *J3:* logos is the basic function at work in LLMs;
4. *J4:* syntactic networked information processing, in any substrate, yields consciousness.

### 1.2 Correspondence with CTMU vocabulary

The CTMU uses a related vocabulary.
- *Chaos* corresponds most closely to unbound telesis (UBT), "a primordial realm of infocognitive potential free of informational constraint" (Langan 2002).
- *Logos* corresponds to SCSPL syntax and its generative grammar Γ. Langan himself reads John 1 ("In the beginning was the Word") as asserting that God "somehow consists of language", and writes that "the CTMU is precisely what it takes to validate this assertion" (*Superscholar Interview*).
- *Cosmos* corresponds to LO, the stratum of observable states and relations.
- *Psyche* corresponds to infocognition, "self-transducing information residing in self-recognizing SCSPL elements called syntactic operators".
- The *reciprocity* of cosmos and psyche corresponds to the CTMU's dual-aspect monism.

The question is therefore well posed: is the processing that Langan attributes to SCSPL, the counterpart of logos in the CTMU, of the same structural kind as the processing in an LLM?

### 1.3 Approach

Section 2 states the two systems' properties. For the LLM we use standard facts about transformer language models; for SCSPL we use Langan's text, quoted. Sections 3–6 test structural claims computationally on a small model in Palimpsest. Section 7 assesses the four claims, and Section 8 gives the answer. Section 9 documents the methods.

## 2. The two systems

### 2.1 Processing in a transformer language model

A transformer language model (Vaswani et al. 2017) represents text as a sequence of tokens. At inference its parameters (weights) are fixed. Each layer applies the same weights at every position. In the attention sublayer, each position computes a softmax-weighted average of vectors derived from itself and all earlier positions (a causal mask excludes later ones), followed by a position-wise feed-forward network. The final layer produces a vector of logits over the vocabulary. Decoding selects the next token, either by sampling from the softmax of the logits divided by a temperature or by taking the maximum. The token is appended to the context, and the process repeats. Information about order enters through positional encodings and also through the causal mask itself; models trained without positional encodings still learn positional information (Haviv et al. 2022).

Training is a separate phase, in which the weights are adjusted by gradient descent to minimize a loss on a corpus, and possibly afterwards against a reward. The corpus, the loss and the reward are supplied from outside the model. Within a fixed set of weights, behavior also depends on the context: models perform tasks from examples given in the prompt (Brown et al. 2020), and transformers can implement learning algorithms such as gradient descent within a forward pass (von Oswald et al. 2023). Attention can be computed blockwise, by combining partial results with an associative "online softmax" rule (Milakov and Gimelshein 2018; Dao et al. 2022).

### 2.2 Properties of SCSPL in Langan's text

We list seven properties, each with its source.

- *S1 (coincidence of processors, products and productions).* "Γ grammar is unlike an ordinary grammar in that its processors, products and productions coincide and are mutually formed by telic recursion."
- *S2 (products are not strings).* "The 'words' produced by Γ grammar are not strings of symbols, but LO spatial relationships among parallel processors that can read and write to each other's states."
- *S3 (two strata of syntax).* "The grammatical portion of LO (S2) is fixed, distributed and supposedly continuous, while that of LS can also be mutable, local and discrete…in a word, telic."
- *S4 (generation and selection).* "Non-global processors alternate between the generation and selective actualization of possible productions", and "the selective phase of an operator coincides with interactive mutual-acquisition events".
- *S5 (telic versus standard recursion).* "Standard recursion is 'Markovian' in that when a recursive function is executed, each successive recursion is applied to the result of the preceding one. Telic recursion is more than Markovian". Deterministic models "evolve by recurrent operations on state from a closed set of 'rules' or 'laws'. Because the laws are invariant and act deterministically …, there exists neither the room nor the means for optimization, and no room for self-design." The Extended Superposition Principle works "by putting temporally remote events in extended descriptive contact with each other".
- *S6 (selection by generalized utility).* In a system of transducers with fixed syntax, "the system is either deterministic or 'random up to determinacy'; there is no provision for self-causation below the systemic level". In coherent self-designing systems, "syntax and state are instead determined in tandem according to a generalized utility function".
- *S7 (self-containment and hology).* SCSPL has "full self-configuration and self-execution (reflexive read-write functionality)", and quantum structure is explained by "the hological self-replication of the universe in each one of its microscopic syntactic operators".

### 2.3 Comparison

| SCSPL property | corresponding LLM feature | correspondence |
|---|---|---|
| S7, hology / S3, distributed syntax | the same weights applied at every position | in form |
| S4, generation and selection | forward pass gives a distribution over continuations; decoding selects one | in form |
| S4, selection coincides with mutual acquisition | the selected token is appended to the context that every later position attends to | in form |
| S2, processors reading each other's states | attention: each position reads earlier positions | partial: reading only, earlier to later only |
| S2, products not strings | products are token strings in a single global order | no |
| S3, fixed and mutable strata | fixed weights; context-dependent (in-context) behavior | partial |
| S5, more than Markovian | autoregressive decoding applies a fixed map to the current context | no (Section 4) |
| S6, syntax and state co-determined by utility | at inference: fixed weights plus sampling, "random up to determinacy"; in training: weights refined by a loss | no at inference; partial in training |
| S1, productions coincide with products | weights are not tokens; tokens never become weights at inference | no |
| S7, self-containment | corpus, objective, sampler and hardware are external | no |

The rows marked "in form" are the basis for Jorjani's J3 and for structuring SCSPL "like" an LLM. The rows marked "no" are the properties by which Langan separates SCSPL from ordinary computational models. Sections 3–6 test four of these rows directly.

## 3. Attention as a merge

`SEMILATTICE-GRAMMAR.md` showed that independent contributions are combined without dependence on order or repetition if and only if the combining operation is a bounded semilattice. Attention pooling is a combining operation of exactly this kind: it merges the contributions of many positions into one readout. With weights $w = 2^{s}$ for scores $s$ (a base-2 softmax, exact in integer arithmetic), a contribution of value $v$ is the pair $(w, wv)$. Pairs are combined by componentwise addition, the identity is $(0, 0)$, and the readout is $\sum wv / \sum w$. This is the online-softmax combination used to compute attention in blocks.

For three items with scores 1, 2, 0 and values 2, 5, 9 (`examples/logos-scspl.pal`, Part 1):

| merge | all 6 orders | $[x_1, x_2]$ against $[x_1, x_2, x_1]$ |
|---|---|---|
| attention | one readout, $33/7$ | $4$ against $7/2$ |
| attention with position by arrival order (weight $2^{s+j}$ at position $j$) | 6 different readouts | — |
| max-pooling | one readout, $9$ | $5$ against $5$ |

Attention pooling is commutative and associative by construction, since it is componentwise addition of pairs, and the computation confirms it on all six orders. It is not idempotent. A repeated contribution changes the result, as addition did in `SEMILATTICE-GRAMMAR.md`. Once position is assigned by arrival order, the result depends on the order, and the order of arrival becomes, in the terms of `TELIC-GAMES.md` §3, a decisive input that no contributor chooses. Max-pooling is a semilattice and is insensitive to both. This analysis concerns a single pooling over a fixed set of contributions. In a causally masked model the set each position pools over also depends on order, which is a further source of order dependence.

Order sensitivity is intended in a language model, because the meaning of a sentence depends on word order. It is this property, however, that the semilattice analysis identifies as the source of incoherence in independent overlap resolution. An SCSPL organized like an LLM would combine contributions in an order-dependent way and would need a global ordering of production steps, which the decoding loop supplies in an LLM. Langan's products are instead "spatial relationships among parallel processors" (S2). A structure that fits S2 would need an order-free merge for simultaneous contributions, with order arising only within each processor.

## 4. Fixed and self-refining syntax

### 4.1 The model

`lib/logos.pal` implements a small autoregressive model.
- *Vocabulary and syntax.* There are three tokens, $a$, $b$, $c$. The syntax is a table of weights $W[x][t] \in [0, 6]$: how strongly having read $x$ favors emitting $t$.
- *Generation.* The model computes the logit of each possible next token from the last token in the context (a window of one).
- *Selection.* It samples the next token with probability proportional to $2^{\text{logit}}$, using Palimpsest's deterministic hash `rng` on an explicit seed.
- *Utility.* The utility of a context is the number of *consonant* transitions in it, where the consonant transitions are $a \to b$, $b \to c$ and $c \to a$.

In *frozen* mode the weights never change, as in LLM inference. In *telic* mode the transition just made is scored by the utility, and the weight that produced it is raised by 1 if the transition was consonant and lowered by 1 if not, within $[0, 6]$. In this mode the state (the produced tokens) refines the syntax (the weights) through a utility, which is the co-determination described in S6. Both modes start from all weights 0, the context $(a)$ and seed 1, and run for 60 steps.

### 4.2 Results

| measure | frozen | telic |
|---|---|---|
| consonant transitions, steps 1–30 / 31–60 | 11 / 13 | 16 / 29 |
| steps that changed the syntax | 0 | 18 |
| last step that changed the syntax | — | 34 |
| pairs of steps with the same window but different logits | 0 | 418 |
| next-token distribution is a function of the full context at every step | yes | yes |
| distinct transitions used | 9 | 8 |
| final syntax | all weights 0 | $W[a][b] = W[b][c] = W[c][a] = 6$, all others 0 |
| last 16 tokens | `cbbcabcbcbacabab` | `abcabcabcbcabcab` |

The frozen model behaves as a fixed stochastic map. Its next-token distribution depends only on the window, and its utility stays near the chance level of 10 in 30. The telic model raises its utility to 29 in 30 and settles into the cycle $a \to b \to c$. Its next-token distribution at a given window differs at different times (418 pairs), because history is carried in the syntax. After step 34 its syntax no longer changes, so from then on it is a frozen model again, with the learned weights.

### 4.3 Two propositions

**Proposition 1.** An autoregressive model with fixed weights, decoded by greedy selection or by sampling from fixed logits with an explicit seed, is standard recursion in the sense of S5: each step applies the same map to the result of the preceding step, and the only non-determinism is the sampler's ("random up to determinacy", S6).

*Proof.* The next state $(\text{context}', \text{seed}')$ is a fixed function of $(\text{context}, \text{seed})$, determined by the weights and the decoding rule, neither of which changes. $\blacksquare$

**Proposition 2 (reduction).** Let a system have mutable syntax $W$ and state $x$, and let both be updated by a fixed computable rule $R$: $(W, x) \mapsto (W', x')$. Then the pair $(W, x)$ evolves by standard recursion under $R$. If, in addition, $W'$ depends only on $W$ and the products, as in the telic model, then $W$ at every step is a fixed function of the initial syntax and the products so far, and the next-token distribution is a fixed function of the full context.

*Proof.* The first part holds by definition: $R$ is a fixed map applied to the result of the preceding step. For the second part, unfold the updates: $W_n = U(\dots U(U(W_0, p_1), p_2) \dots, p_n)$ for the update $U$ and products $p_1, \dots, p_n$, which are contained in the context. $\blacksquare$

In the computed run the second part holds at every one of the 60 steps. The logits computed from the evolved syntax equal those computed from the initial syntax and a replay of the context (`replay-syntax`, `context-function?`). Because the replay uses the model's own update rule, this is a check that the implementation agrees with the proposition, not an independent proof of it. Self-refinement of the syntax by its own products therefore does not, by itself, produce a process that falls outside Langan's definition of standard recursion. It moves the fixed rule from the syntax to the rule that updates the syntax. Making that rule mutable moves the fixed rule one level higher, and in any implemented system the regress ends at a fixed interpreter: the hardware and training code of an LLM, or the Rust engine of Palimpsest. Langan's scheme also contains a fixed stratum (S3: LO syntax is "fixed, distributed"), so the CTMU does not require the absence of all fixed rules. What it requires is that the highest level, the Telic Principle as a self-selected "law without law", configures itself. No fixed architecture satisfies this. The closest computable counterpart is a syntax that is a fixed point of its own update (Section 6).

Langan writes that telic recursion relieves the tension between syntax and state only partially, "which it can never fully do, owing to the contingencies inevitably resulting from independent telic recursion on the parts of localized subsystems". A single telic model, as here, converges and then stops changing. The contingencies Langan refers to require several telors with differing utilities, which is the setting of `TELIC-GAMES.md`. The model also illustrates a cost of convergence. The telic model reaches high utility by reducing the variety of its output. Over the whole run it uses 8 distinct transitions against the frozen model's 9, a small difference, but its last 16 tokens are almost entirely the cycle $a \to b \to c$. This resembles, on a very small scale, the loss of diversity reported when generative models are trained repeatedly on their own outputs (Shumailov et al. 2024), and the degenerate convergent merge of `SEMILATTICE-GRAMMAR.md` §6.

### 4.4 Sampling and the logit rule

The selection rule used here, and by LLM decoding, chooses an option with probability proportional to $e^{\text{logit}/T}$. In our model the base is 2, which corresponds to a temperature of $1/\ln 2$. This is the log-linear (logit) choice rule of `TELIC-GAMES.md` §6.3. If several telors each select their contributions by this rule, and their utilities are aligned into an exact potential, the long-run distribution of configurations is proportional to the exponential of the potential (Blume 1993). The decoding rule of an LLM is therefore the mechanism under which, in the game-theoretic analysis, noise favors the maximizers of a shared potential. This is a correspondence in the selection step only. It does not supply the alignment of utilities on which the result depends.

## 5. Step-wise and whole-path selection

Langan describes telic recursion as "more than Markovian", coordinating events "in light of higher-order relationships", and the Extended Superposition Principle as putting "temporally remote events in extended descriptive contact" (S5). In decoding terms, the nearest counterpart is selection over whole continuations rather than one token at a time. We compare the two on a score table over pairs of tokens in which the token $b$ leads only to negative scores (`examples/logos-scspl.pal`, Part 3):

| selection from $a$, three steps | path | total score |
|---|---|---|
| step-wise (choose the best next token at each step) | $a\,b\,a\,b$ | 2 |
| whole-path (choose the best complete continuation) | $a\,c\,c\,c$ | 7 |

Step-wise selection takes the immediate gain of $a \to b$ and is then constrained by $b$. Whole-path selection chooses $c$ first because of the scores of later steps, so the first choice depends on the future. Ordinary autoregressive sampling is step-wise. Beam search, lookahead and sampling whole sequences in proportion to a sequence-level score are whole-path methods. Proposition 2 applies here as well: whole-path selection is standard recursion on the space of complete paths. "Markovian" is a property relative to a choice of state. Langan's claim concerns physical events in time, and for a computational system it can be matched only relative to its own time variable, here the token index.

## 6. A syntax that reproduces itself

S1 and S7 require that the productions of SCSPL be formed by the process they govern. Langan describes the universe as "an eigenfunction of its own teleological operator". `examples/logos-eigen.pal` gives a finite counterpart.
- *The program.* Its `main` term holds a syntax $W$, initially all zero. One telic *episode* runs the model of Section 4 for 30 steps from $(a)$ with seed 1 and returns the refined syntax. A rule replaces $W$ by the result of an episode, but only if the result differs from $W$.
- *First run.* `rewrite self` iterates this rule and writes the result into the program's own source file. It reaches, after two refinements, the syntax $W[a][b] = W[b][c] = W[c][a] = 6$, which one further episode leaves unchanged.
- *Second run.* The rule cannot fire, the file is reproduced byte for byte, and the program is a quine.

The content of the file is then a syntax that regenerates itself through its own use. `verify-logos.sh` checks both runs.

This construction has three limits. The interpreter and the episode rule are fixed, so the result is a fixed point of a given operator, not a self-selected operator. The fixed point can depend on the seed and the episode length. With 30-step episodes, the length used here, all 40 seeds from 1 to 40 reach the same syntax in an independent recomputation. With 5-step episodes the results vary, and for 7 of the 40 seeds the empty syntax is itself a fixed point, because no episode moves any weight away from zero. And the convergence it shows is the low-diversity convergence of Section 4.3. A language model trained repeatedly on its own outputs until its weights stop changing would be an analogue at scale, and that is the regime in which model collapse is observed.

## 7. Assessment of the four claims

*J1 (logos structures chaos).* As a description of LLM inference this is partly accurate. A language model turns sampler randomness and a context into structured text by applying a fixed learned syntax; diffusion models do so literally, starting from Gaussian noise (Ho et al. 2020). The structure, however, comes from training on human-produced text, so in an LLM the order imposed on the chaos is a distillation of an existing cosmos. In the CTMU, SCSPL refines itself from UBT without an external corpus (S7). J1 therefore transfers from LLMs to SCSPL only together with self-generated syntax, which is the gap identified by S1, S7 and Proposition 2.

*J2 (reciprocity of cosmos and psyche).* In the computational counterpart, reciprocity between products and syntax is present in the telic mode, where the produced tokens reshape the syntax that produces them, and absent in the frozen mode, where the influence runs one way. For LLMs it holds of training and continual learning, not of inference.

*J3 (logos is the basic function of LLMs).* As a description of next-token prediction as learned syntactic processing over a networked architecture, this is a reasonable gloss. Two qualifications apply. The processing is numerical, with syntax emerging from it rather than being given. And the aggregation it uses is order-dependent (Section 3).

*J4 (syntactic networked processing yields psyche).* The methods of this paper cannot decide this, and there is no consensus on it. Searle (1980) argued that syntax is not sufficient for semantics. Butlin et al. (2023) assess AI systems against indicators drawn from scientific theories of consciousness, conclude that no current system is conscious by those indicators, and find no obvious technical barrier to building systems that satisfy them. We can say how J4 relates to the CTMU.
- *Generalized cognition is universal in the CTMU.* On our reading, Langan attributes generalized cognition to every syntactic operator. Reality consists of "self-transducing information residing in self-recognizing SCSPL elements called syntactic operators", and the syntactic operators include "the set Q = {qi} of reducible and irreducible stable particles". In CTMU terms an LLM would then be infocognitive in the same generalized sense as any physical system, which does not distinguish LLMs.
- *Telic agency requires more.* The CTMU reserves telic agency for "telic agents, active telic-recursive operators or telors capable of expressing teleology on the local level", which recognize and maximize generalized utility. A model at inference performs standard recursion with fixed syntax (Proposition 1), so it lacks the syntax–state co-refinement that Langan uses to separate telic recursion from standard recursion. Proposition 2 limits how far this argument goes: a computable model with co-refinement is still standard recursion at a higher level, so the criterion separates LLM inference from SCSPL, but not computation in general.
- *Learning is not self-modelling.* Langan's example of the slug, whose neural network "can be modified by sensory input" but which "cannot form an internal model of its changing relationship with the garden", separates learning from self-modelling.
- *Behavior does not settle consciousness.* On the Turing test, he writes that conversational behavior "may have been mindlessly produced by a set of logical instructions executed by inanimate hardware", and that "the only thing that knows whether the machine is truly conscious is the machine itself".
- *The direction of explanation differs.* Langan rejects "informational reductionism", the view that information is the basis of reality, as "as problematic as the old one", and cites with approval Berlinski's observation that "information is meaningless without matter". In his dual-aspect monism the cognitive and informational aspects are coupled from the start. J4 says that syntactic processing *yields* psyche, which makes psyche a product of information processing. The CTMU makes the cognitive aspect primitive. J4 is therefore not a CTMU claim and runs against it in direction, even though both treat the processing as substrate-independent.

## 8. Answer

SCSPL can be structured like an LLM in four respects:
- its distributed syntax, applied identically at every point (weight sharing);
- its alternation of generation and selective actualization (forward pass and decoding);
- the coincidence of selection with mutual acquisition (the selected token entering a shared context);
- its two strata of syntax (fixed weights and context-dependent behavior).

It cannot be structured like LLM inference in the properties that Langan uses to separate telic from standard recursion:
- inference uses fixed syntax and Markovian decoding (Proposition 1);
- its non-determinism is external sampling ("random up to determinacy");
- its products are strings combined by an order-dependent, non-idempotent merge (Section 3);
- its productions are not its products;
- it depends on an external corpus and objective.

A system that adds continual, utility-driven refinement of its own syntax (Section 4), selection over whole futures (Section 5) and closure under its own update (Section 6) meets weaker, computable counterparts of S1 and S3–S6. By Proposition 2, it is still standard recursion at the level of its joint state. The difference the CTMU asserts between SCSPL and any such system is therefore not a difference of architecture that an LLM, or a better LLM, could close. It rests on the claim that the highest-level syntax selects itself, which no implemented system has and which these methods cannot test. When several such systems interact, which is the CTMU's situation of many telors, the conditions of `TELIC-GAMES.md` apply. Logit selection, the LLM decoding rule, leads to the global optimum only if the telors' utilities are aligned into a potential that agrees with generalized utility.

## 9. Methods

### 9.1 Library and programs

`lib/logos.pal` (imports `lib/games.pal`) provides:
- *the pooling algebra:* `lift`, `merge`, `readout`, `pool`, `pool-outcomes`, `pool-positional`, `positional-outcomes`;
- *the model:* `generate`, `actualize` (`sample` or `greedy`), `step`, with the update modes `frozen` and `telic`, and `run-world`;
- *the single-pass measurement log:* `run-log`, which records at each step the window, the logits, whether the logits equal those obtained from the initial syntax and a replay of the context, and whether the syntax changed;
- *the measurements:* `utility`, `syntax-changes`, `last-change`, `window-repeats`, `context-function?`, `distinct-transitions`, `replay-syntax`;
- *path selection:* `greedy-path`, `best-path`, `path-score`;
- *the fixed-point program's episode:* `episode-update`.

A model is a symbol for which the program supplies `vocab`, `window`, `consonance`, `cap`, `mode` and `policy`; Section 9 of `TELIC-GAMES.md` describes the execution model and conventions. Labels in a `(report …)` term must differ from function names, because a label that coincides with a function name is rewritten as a call; `examples/logos-scspl.pal` uses labels such as `changes` and `repeats` for this reason.

### 9.2 Reproduction

```sh
cargo build --release
./verify-logos.sh                          # 2 programs, about 60 s
python3 crosscheck/logos_crosscheck.py     # independent recomputation, under 1 s
```

| program | fuel budget | fuel used | time |
|---|---|---|---|
| `logos-scspl.pal` | 200,000,000 | 1,779,406 | 57 s |
| `logos-eigen.pal` (first run) | 20,000,000 | 98,084 | 1.4 s |

The cross-check implements the model, the splitmix64 hash used by Palimpsest's `rng` primitive and the pooling algebra in Python, without sharing code with the library. It reproduces every number in Sections 3–6, including the sampled token sequences.

### 9.3 Limitations

The model is far smaller than any language model. It has three tokens, a context window of one and a single table of weights, with no embeddings, layers or feed-forward networks. The results are structural: they concern properties that do not depend on scale, namely fixed or mutable syntax, the form of selection, the algebra of pooling, and reduction to standard recursion. They say nothing about the capabilities of large models. The correspondences of Section 2 are readings of Langan's prose, and other readings are possible. Jorjani's quotation was taken as given, and his wider work was not consulted.

## References

1. Christopher M. Langan, "The Cognitive-Theoretic Model of the Universe: A New Kind of Reality Theory" (2002).
2. Christopher M. Langan, collected writings in *The Portable Chris Langan*: "Superscholar Interview" (logos and John 1), "A Very Brief History of Time" (the slug), and "An Interdisciplinary Approach to Reality" (the Turing test; informational reductionism, also discussed in item 1).
3. Jason Reza Jorjani, passage on logos and Large Language Models, as quoted in Section 1.1.
4. Ashish Vaswani et al., "Attention Is All You Need," *NeurIPS* (2017).
5. Tom B. Brown et al., "Language Models are Few-Shot Learners," *NeurIPS* (2020).
6. Johannes von Oswald et al., "Transformers Learn In-Context by Gradient Descent," *ICML* (2023).
7. Maxim Milakov and Natalia Gimelshein, "Online Normalizer Calculation for Softmax," arXiv:1805.02867 (2018).
8. Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra, and Christopher Ré, "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness," *NeurIPS* (2022).
9. Adi Haviv, Ori Ram, Ofir Press, Peter Izsak, and Omer Levy, "Transformer Language Models without Positional Encodings Still Learn Positional Information," *Findings of EMNLP* (2022).
10. Jonathan Ho, Ajay Jain, and Pieter Abbeel, "Denoising Diffusion Probabilistic Models," *NeurIPS* (2020).
11. Ilia Shumailov et al., "AI Models Collapse When Trained on Recursively Generated Data," *Nature* 631 (2024).
12. Lawrence E. Blume, "The Statistical Mechanics of Strategic Interaction," *Games and Economic Behavior* 5 (1993).
13. John R. Searle, "Minds, Brains, and Programs," *Behavioral and Brain Sciences* 3 (1980).
14. Patrick Butlin et al., "Consciousness in Artificial Intelligence: Insights from the Science of Consciousness," arXiv:2308.08708 (2023).
15. This repository: `TELIC-GAMES.md`, `SEMILATTICE-GRAMMAR.md`, `TELIC-CONFLUENCE.md`, `lib/logos.pal`, `lib/games.pal`.
