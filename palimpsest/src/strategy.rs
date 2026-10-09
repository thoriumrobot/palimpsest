//! Strategies: programmable control over *where* and *how often* rules fire.
//!
//! Rules say *what* may be rewritten; strategies say *how* to drive them. This
//! separation (from Stratego/ELAN) is what lets a confluent/terminating core be
//! combined with controlled, bounded traversal. Fuel is the universal
//! termination backstop: every successful rule application costs one unit, so no
//! program can loop forever — it runs out of fuel and the caller rolls back.

use crate::matcher::{match_term, match_where, subst, Binding, Bindings};
use crate::term::Term;
use crate::fxhash::FxHashMap as HashMap;
use std::cell::RefCell;
use std::rc::Rc;

/// A `where` clause attached to a rule. Clauses are processed in order after the
/// left-hand side matches, and share the rule's variable bindings.
#[derive(Clone, Debug)]
pub enum WhereClause {
    /// `?v <- EXPR` — evaluate EXPR (normalized) and bind the result to `?v`,
    /// making it available to later clauses and the right-hand side.
    Bind(String, Term),
    /// `EXPR` — a guard: the rule fires only if EXPR normalizes to `true`.
    Guard(Term),
}

/// A named rewrite rule `lhs => rhs` with optional `where` clauses. Conditional
/// rules (guards) and local bindings are what make non-trivial algorithms —
/// sorting, evaluation, type-checking — expressible as rewriting.
#[derive(Clone, Debug)]
pub struct Rule {
    pub name: String,
    pub lhs: Term,
    pub rhs: Term,
    pub conds: Vec<WhereClause>,
}

/// Strategy expressions.
#[derive(Clone, Debug)]
pub enum Strat {
    Id,
    Fail,
    /// Left-biased choice over *all* defined rules, applied at the root.
    AllRules,
    /// A reference resolved at apply-time to a strategy parameter, a rule, or a
    /// zero-argument named strategy.
    Ref(String),
    /// A call to a user-defined parameterized strategy, e.g. `simplify(myrules)`.
    Call(String, Vec<Strat>),
    /// Evaluate a built-in primitive application (arithmetic, comparison,
    /// string) at the root, if the operands are literals.
    Prim,
    Seq(Box<Strat>, Box<Strat>),
    Choice(Box<Strat>, Box<Strat>),
    Try(Box<Strat>),
    Repeat(Box<Strat>),
    TopDown(Box<Strat>),
    BottomUp(Box<Strat>),
    Innermost(Box<Strat>),
    /// Apply once at the highest-leftmost position where it succeeds.
    OnceTd(Box<Strat>),
    /// Apply once at the lowest-leftmost position where it succeeds.
    OnceBu(Box<Strat>),
    FixPoint(Box<Strat>),
    All(Box<Strat>),
}

/// A (possibly parameterized) named strategy definition.
#[derive(Clone, Debug)]
pub struct StratDef {
    pub params: Vec<String>,
    pub body: Strat,
}

// --- strategy-parameter environment (lexically-scoped closures) --------------
// A strategy passed as an argument is captured together with the environment it
// was written in, so recursion like `strategy rep(s) = try(s ; rep(s))` resolves
// `s` correctly at every depth.

#[derive(Clone)]
struct Closure {
    body: Strat,
    env: Env,
}

enum Scope {
    Empty,
    Bind(String, Closure, Env),
}

type Env = Rc<Scope>;

fn env_empty() -> Env {
    Rc::new(Scope::Empty)
}

fn env_lookup(env: &Env, name: &str) -> Option<Closure> {
    let mut cur = env.clone();
    loop {
        match &*cur {
            Scope::Empty => return None,
            Scope::Bind(n, c, next) => {
                if n == name {
                    return Some(c.clone());
                }
                cur = next.clone();
            }
        }
    }
}

fn env_bind(env: &Env, name: String, clos: Closure) -> Env {
    Rc::new(Scope::Bind(name, clos, env.clone()))
}

/// State of the `--trace` printer.
pub struct Trace {
    pub limit: u64,
    pub count: u64,
}

fn clip(s: &str, n: usize) -> String {
    if s.chars().count() <= n { s.to_string() } else { format!("{}...", s.chars().take(n).collect::<String>()) }
}

pub struct Engine {
    pub rules: Vec<Rule>,
    pub rule_index: HashMap<String, usize>,
    pub strategies: HashMap<String, StratDef>,
    /// Cached head key per rule (parallel to `rules`): `Some(sym)` when the rule's
    /// left-hand side can only match subjects with that head symbol, `None` when
    /// it may match anything (a variable head). Used to skip non-matching rules.
    rule_heads: Vec<Option<String>>,
    /// True head index: for each concrete head symbol, the indices (ascending)
    /// of rules whose left-hand side pins that head. Wildcard-headed rules live
    /// in `wild_rules`. `AllRules` merges the two ascending lists, so rules are
    /// still tried in exact source order -- dispatch is O(candidates), not
    /// O(all rules), and behaviour (including fuel use) is unchanged.
    by_head: HashMap<String, Vec<usize>>,
    wild_rules: Vec<usize>,
    /// Optional rewrite-step profile: successful applications per rule name
    /// (primitives are counted under `<prim>`). Enabled by `--stats`.
    pub stats: Option<RefCell<HashMap<String, u64>>>,
    /// Optional REWRITE TRACE (`--trace N`): print the first N successful
    /// steps as `rule: redex => contractum`, indented by the nesting depth of
    /// guard / `where` / strict-argument evaluation in which they happen.
    /// Printing only; no effect on results or fuel.
    pub trace: Option<RefCell<Trace>>,
    /// Current nesting of condition evaluation (for trace indentation).
    cond_level: std::cell::Cell<usize>,
    /// Optional NORMAL-FORM MEMO (`#memo` / `--memo`): the set of list
    /// subterms (by `Rc` identity) already proven to be in normal form with
    /// respect to the standard evaluator `prim + rules`. Rules are static and
    /// match context-free, so a term that is normal stays normal: the
    /// leftmost-outermost redex search may skip it. Normal forms, and the order
    /// in which redexes are reduced, are exactly those of the uncached
    /// evaluator; only the work of re-proving normality is saved -- which also
    /// means fuel spent by guards on failed rule attempts is not spent twice,
    /// so a memoized run uses LESS fuel. That is why it is opt-in: existing
    /// programs keep their exact fuel fingerprints.
    memo: Option<RefCell<Memo>>,
    /// The standard evaluator `repeat(oncetd(prim + rules))`, built once.
    std_eval: Strat,
}

/// Pointer-identity set of known-normal list terms; each entry keeps its term
/// alive so an address can never be reused by a different term while cached.
pub struct Memo {
    known: HashMap<usize, Term>,
    /// NORMALIZATION CACHE for strict arguments: argument term (by `Rc`
    /// identity; the key term is kept alive so its address cannot be reused)
    /// -> its normal form under the standard evaluator. Normal forms are a
    /// function of the term alone (static rules, context-free matching), so
    /// a strict argument forced once -- e.g. for a rule whose guard then
    /// failed -- is not forced again for the next candidate rule.
    nf: HashMap<usize, (Term, Term)>,
    pub nf_hits: u64,
    pub hits: u64,
}

const MEMO_CAP: usize = 1 << 21;
/// The normalization cache holds key AND value terms alive, so it is kept
/// small: cleared when it reaches this many entries.
const NF_CAP: usize = 1 << 14;

fn term_addr(t: &Term) -> Option<usize> {
    match t {
        Term::List(rc) => Some(Rc::as_ptr(rc) as *const () as usize),
        _ => None,
    }
}

/// Is `s` exactly the standard evaluator's inner strategy `prim + rules`?
fn is_std_inner(s: &Strat) -> bool {
    matches!(s, Strat::Choice(a, b) if matches!(**a, Strat::Prim) && matches!(**b, Strat::AllRules))
}

/// The head symbol that a term must have for a list/atom pattern to match it, or
/// `None` if the pattern (or subject) does not pin down a concrete head.
fn head_key(t: &Term) -> Option<String> {
    match t {
        Term::Sym(s) if !s.starts_with('?') => Some(s.clone()),
        Term::List(xs) => match xs.first() {
            Some(Term::Sym(s)) if !s.starts_with('?') => Some(s.clone()),
            _ => None,
        },
        _ => None,
    }
}

/// Allocation-free variant of `head_key`, used on the hot dispatch path.
fn head_str(t: &Term) -> Option<&str> {
    match t {
        Term::Sym(s) if !s.starts_with('?') => Some(s.as_str()),
        Term::List(xs) => match xs.first() {
            Some(Term::Sym(s)) if !s.starts_with('?') => Some(s.as_str()),
            _ => None,
        },
        _ => None,
    }
}

impl Engine {
    pub fn new() -> Self {
        Engine {
            rules: Vec::new(),
            rule_index: HashMap::default(),
            strategies: HashMap::default(),
            rule_heads: Vec::new(),
            by_head: HashMap::default(),
            wild_rules: Vec::new(),
            stats: None,
            trace: None,
            cond_level: std::cell::Cell::new(0),
            memo: None,
            std_eval: Strat::Repeat(Box::new(Strat::OnceTd(Box::new(Strat::Choice(
                Box::new(Strat::Prim),
                Box::new(Strat::AllRules),
            ))))),
        }
    }

    /// Turn on the normal-form memo (see the `memo` field).
    pub fn enable_memo(&mut self) {
        self.memo = Some(RefCell::new(Memo { known: HashMap::default(), nf: HashMap::default(), nf_hits: 0, hits: 0 }));
    }

    pub fn memo_stats(&self) -> Option<(usize, u64)> {
        self.memo.as_ref().map(|m| {
            let m = m.borrow();
            (m.known.len(), m.hits)
        })
    }

    /// Hits of the normalization cache (see `Memo::nf`).
    pub fn memo_nf_hits(&self) -> Option<u64> {
        self.memo.as_ref().map(|m| m.borrow().nf_hits)
    }

    #[inline]
    fn memo_known(&self, t: &Term) -> bool {
        if let (Some(m), Some(a)) = (&self.memo, term_addr(t)) {
            let mut m = m.borrow_mut();
            if m.known.contains_key(&a) {
                m.hits += 1;
                return true;
            }
        }
        false
    }

    #[inline]
    fn memo_insert(&self, t: &Term) {
        if let (Some(m), Some(a)) = (&self.memo, term_addr(t)) {
            let mut m = m.borrow_mut();
            if m.known.len() >= MEMO_CAP {
                m.known.clear();
            }
            m.known.insert(a, t.clone());
        }
    }

    pub fn add_rule(&mut self, r: Rule) {
        let idx = self.rules.len();
        self.rule_index.insert(r.name.clone(), idx);
        let hk = head_key(&r.lhs);
        match &hk {
            Some(h) => self.by_head.entry(h.clone()).or_default().push(idx),
            None => self.wild_rules.push(idx),
        }
        self.rule_heads.push(hk);
        self.rules.push(r);
    }

    /// Register a TRANSITION: a rule that is reachable only by name from a
    /// strategy (`oncetd(crank)`), never through `rules` / the `where`
    /// evaluator. This is rewriting logic's split between EQUATIONS (applied
    /// exhaustively to normal form: accounting identities, tables, derived
    /// quantities) and RULES-AS-TRANSITIONS (applied once, under control: "play
    /// one round"). Without it, any rule whose result still matches its own
    /// left-hand side would be re-fired by `outermost` until the run ends.
    pub fn add_transition(&mut self, r: Rule) {
        let idx = self.rules.len();
        self.rule_index.insert(r.name.clone(), idx);
        self.rule_heads.push(head_key(&r.lhs));
        self.rules.push(r);
    }

    /// Turn on the per-rule rewrite profile (see `stats`).
    pub fn enable_stats(&mut self) {
        self.stats = Some(RefCell::new(HashMap::default()));
    }

    fn record(&self, name: &str) {
        if let Some(st) = &self.stats {
            *st.borrow_mut().entry(name.to_string()).or_insert(0) += 1;
        }
    }

    /// Turn on the rewrite trace for the first `limit` steps (see `trace`).
    pub fn enable_trace(&mut self, limit: u64) {
        self.trace = Some(RefCell::new(Trace { limit, count: 0 }));
    }

    /// Steps traced so far, and the limit.
    pub fn trace_count(&self) -> Option<(u64, u64)> {
        self.trace.as_ref().map(|t| { let t = t.borrow(); (t.count, t.limit) })
    }

    fn trace_step(&self, name: &str, before: &Term, after: &Term) {
        if let Some(tr) = &self.trace {
            let mut tr = tr.borrow_mut();
            if tr.count < tr.limit {
                tr.count += 1;
                let ind = "  ".repeat(self.cond_level.get().min(12));
                println!("  {:>5} {}{}: {}  =>  {}", tr.count, ind, name, clip(&before.to_string(), 150), clip(&after.to_string(), 150));
            }
        }
    }

    /// Apply a rule at the root of `t`. Handles `where` clauses: bindings extend
    /// the substitution with normalized sub-results; guards must normalize to
    /// `true` or the rule fails. Conditions are evaluated with the standard
    /// normal-order evaluator over the whole rule set + primitives.
    fn apply_rule(
        &self,
        r: &Rule,
        t: &Term,
        fuel: &mut u64,
        depth: usize,
    ) -> Result<Option<Term>, String> {
        // STRICT VARIABLES (`!x` instead of `?x`) -- a pre-pass, not a change
        // to the matcher itself. A pattern like `(size (?xs...))` matches
        // ANY list-shaped subject on pure syntax, with no way to tell "this
        // subject is already a fully-reduced value" from "this subject is an
        // unevaluated call to some other rule that just happens to also be
        // list-shaped" -- e.g. `(size (t2-instance 40))` would match
        // `size`'s pattern immediately, on the two-element literal syntax
        // `(t2-instance 40)`, before `t2-instance` ever gets a chance to
        // expand into the 42-element list it actually denotes. This is the
        // same hazard `equal?` (lib/logic.pal) already carries and warns
        // about by convention ("reduce the arguments first"); strict
        // variables make the fix enforceable instead of merely documented.
        //
        // Writing `!x` for one of a rule's TOP-LEVEL left-hand-side
        // arguments (a direct child of the pattern list, not nested deeper)
        // means: before matching, fully normalize (via `eval_cond`, the same
        // `outermost(prim + rules)` evaluator a `where ?v <- EXPR` binding
        // already uses) the subject's argument at that same position, then
        // match as if the pattern had said `?x` all along. A subject that is
        // already a value is unaffected (normalizing a normal form is a
        // no-op), so this is purely additive: no existing rule mentions `!`,
        // so no existing rule's behavior changes.
        //
        // Scope, deliberately: only TOP-LEVEL, FIXED-ARITY positions are
        // supported. If `r.lhs`'s top level also contains a sequence
        // variable (`?xs...`), a strict variable's subject position is not
        // well-defined until AFTER matching decides how many elements the
        // sequence variable consumes -- so forcing is skipped and the
        // literal `!x` is left for the ordinary matcher, which does not
        // recognize it and simply will not match (a clean, safe "this rule
        // does not apply" rather than a crash; see
        // `strict_vars_mixed_with_seq_var_do_not_match` below).
        let (lhs, subject) = self.pre_force_strict_vars(&r.lhs, t, fuel, depth)?;
        let lhs = lhs.as_ref().unwrap_or(&r.lhs);
        let subject = subject.as_ref().unwrap_or(t);

        // Fast path: an unconditional rule takes the first match.
        if r.conds.is_empty() {
            return match match_term(lhs, subject, Bindings::default()) {
                Some(b) => {
                    if *fuel == 0 {
                        return Err("out of fuel (rewrite step budget exhausted)".into());
                    }
                    *fuel -= 1;
                    self.record(&r.name);
                    let out = subst(&r.rhs, &b)?;
                    self.trace_step(&r.name, subject, &out);
                    Ok(Some(out))
                }
                None => Ok(None),
            };
        }
        // Conditional rule: search for a decomposition whose guards all hold.
        // Guard failure backtracks into the matcher to try another split of the
        // sequence variables, so a rule like the one-rule bubble sort can find
        // *any* out-of-order adjacent pair, not just the first decomposition.
        let conds = &r.conds;
        let matched =
            match_where(lhs, subject, &mut |b| self.check_conds(conds, b, fuel, depth))?;
        match matched {
            Some(b) => {
                if *fuel == 0 {
                    return Err("out of fuel (rewrite step budget exhausted)".into());
                }
                *fuel -= 1;
                self.record(&r.name);
                let out = subst(&r.rhs, &b)?;
                self.trace_step(&r.name, subject, &out);
                Ok(Some(out))
            }
            None => Ok(None),
        }
    }

    /// Implements the STRICT VARIABLES pre-pass described in `apply_rule`.
    /// Returns `(None, None)` (use the originals, unchanged) whenever the
    /// shape doesn't cleanly apply: no strict variables present, the pattern
    /// also has a top-level sequence variable, or the subject isn't a
    /// same-length list. Otherwise returns the desugared pattern (`!x` ->
    /// `?x`) and the subject with each strict-variable position replaced by
    /// its normal form.
    fn pre_force_strict_vars(
        &self,
        lhs: &Term,
        t: &Term,
        fuel: &mut u64,
        depth: usize,
    ) -> Result<(Option<Term>, Option<Term>), String> {
        let Term::List(pat_items) = lhs else {
            return Ok((None, None));
        };
        let has_strict = pat_items.iter().any(|p| p.as_strict_var().is_some());
        if !has_strict {
            return Ok((None, None));
        }
        let has_top_level_seq = pat_items.iter().any(|p| p.as_seq_var().is_some());
        if has_top_level_seq {
            return Ok((None, None));
        }
        let Term::List(subj_items) = t else {
            return Ok((None, None));
        };
        if subj_items.len() != pat_items.len() {
            return Ok((None, None));
        }
        let mut new_pat = Vec::with_capacity(pat_items.len());
        let mut new_subj = Vec::with_capacity(subj_items.len());
        for (p, s) in pat_items.iter().zip(subj_items.iter()) {
            if let Some(name) = p.as_strict_var() {
                new_pat.push(Term::Sym(format!("?{}", name)));
                new_subj.push(self.force_strict(s, fuel, depth)?);
            } else {
                new_pat.push(p.clone());
                new_subj.push(s.clone());
            }
        }
        Ok((Some(Term::list(new_pat)), Some(Term::list(new_subj))))
    }

    /// Evaluate a rule's `where` clauses against a candidate binding. Returns the
    /// binding augmented with any `?v <- EXPR` results on success, or `None` if a
    /// guard is not satisfied (so the matcher keeps searching).
    fn check_conds(
        &self,
        conds: &[WhereClause],
        mut b: Bindings,
        fuel: &mut u64,
        depth: usize,
    ) -> Result<Option<Bindings>, String> {
        for clause in conds {
            match clause {
                WhereClause::Bind(v, expr) => {
                    let e = subst(expr, &b)?;
                    let nf = self.eval_cond(&e, fuel, depth)?;
                    b.insert(v.clone(), Binding::One(nf));
                }
                WhereClause::Guard(expr) => {
                    let e = subst(expr, &b)?;
                    let nf = self.eval_cond(&e, fuel, depth)?;
                    if nf != Term::Sym("true".to_string()) {
                        return Ok(None);
                    }
                }
            }
        }
        Ok(Some(b))
    }

    /// Normalize a condition/binding expression with the standard evaluator
    /// (`outermost(prim + rules)`), so guards may call library functions.
    fn eval_cond(&self, t: &Term, fuel: &mut u64, depth: usize) -> Result<Term, String> {
        if self.memo.is_some() && self.memo_known(t) {
            return Ok(t.clone());
        }
        self.cond_level.set(self.cond_level.get() + 1);
        let r = self.apply_d(&self.std_eval, t, fuel, depth + 1, &env_empty());
        self.cond_level.set(self.cond_level.get() - 1);
        Ok(r?.unwrap_or_else(|| t.clone()))
    }

    /// Normalize the argument at a strict (`!x`) position. Under the memo,
    /// reuse a normal form already computed for the same argument term (by
    /// identity): when several rules share a head and the first one's guard
    /// fails, the next candidate would otherwise force the same argument again.
    fn force_strict(&self, t: &Term, fuel: &mut u64, depth: usize) -> Result<Term, String> {
        if let (Some(m), Some(a)) = (&self.memo, term_addr(t)) {
            let mut m = m.borrow_mut();
            let hit = m.nf.get(&a).map(|(_, v)| v.clone());
            if let Some(v) = hit {
                m.nf_hits += 1;
                return Ok(v);
            }
        }
        let v = self.eval_cond(t, fuel, depth)?;
        if let (Some(m), Some(a)) = (&self.memo, term_addr(t)) {
            if !std::ptr::eq(t, &v) && term_addr(&v) != Some(a) {
                let mut m = m.borrow_mut();
                if m.nf.len() >= NF_CAP {
                    m.nf.clear();
                }
                m.nf.insert(a, (t.clone(), v.clone()));
            }
        }
        Ok(v)
    }

    /// Apply a strategy to a term. `Ok(Some(t'))` on success, `Ok(None)` on a
    /// clean strategy failure, `Err(_)` on a hard error (out of fuel, unbound
    /// variable, unknown name, recursion overflow).
    pub fn apply(&self, s: &Strat, t: &Term, fuel: &mut u64) -> Result<Option<Term>, String> {
        self.apply_d(s, t, fuel, 0, &env_empty())
    }

    fn apply_d(
        &self,
        s: &Strat,
        t: &Term,
        fuel: &mut u64,
        depth: usize,
        env: &Env,
    ) -> Result<Option<Term>, String> {
        if depth > 200_000 {
            return Err("strategy recursion too deep".into());
        }
        match s {
            Strat::Id => Ok(Some(t.clone())),
            Strat::Fail => Ok(None),
            Strat::AllRules => {
                // Candidates = rules pinned to the subject's head symbol, plus
                // wildcard-headed rules, merged in ascending source order.
                let empty: Vec<usize> = Vec::new();
                let pinned = match head_str(t) {
                    Some(k) => self.by_head.get(k).unwrap_or(&empty),
                    None => &empty,
                };
                let wild = &self.wild_rules;
                let (mut i, mut j) = (0usize, 0usize);
                while i < pinned.len() || j < wild.len() {
                    let idx = if j >= wild.len() || (i < pinned.len() && pinned[i] < wild[j]) {
                        i += 1;
                        pinned[i - 1]
                    } else {
                        j += 1;
                        wild[j - 1]
                    };
                    if let Some(t2) = self.apply_rule(&self.rules[idx], t, fuel, depth)? {
                        return Ok(Some(t2));
                    }
                }
                Ok(None)
            }
            Strat::Prim => match eval_prim(t) {
                Some(v) => {
                    if *fuel == 0 {
                        return Err("out of fuel (rewrite step budget exhausted)".into());
                    }
                    *fuel -= 1;
                    self.record("<prim>");
                    self.trace_step("<prim>", t, &v);
                    Ok(Some(v))
                }
                None => Ok(None),
            },
            Strat::Ref(name) => {
                // 1. strategy parameter in scope?
                if let Some(clos) = env_lookup(env, name) {
                    return self.apply_d(&clos.body, t, fuel, depth + 1, &clos.env);
                }
                // 2. a rule?
                if let Some(&i) = self.rule_index.get(name) {
                    let r = self.rules[i].clone();
                    return self.apply_rule(&r, t, fuel, depth);
                }
                // 3. a zero-argument named strategy?
                if let Some(def) = self.strategies.get(name) {
                    if !def.params.is_empty() {
                        return Err(format!(
                            "strategy '{}' expects {} argument(s)",
                            name,
                            def.params.len()
                        ));
                    }
                    return self.apply_d(&def.body, t, fuel, depth + 1, &env_empty());
                }
                Err(format!("unknown rule or strategy '{}'", name))
            }
            Strat::Call(name, args) => {
                // A parameter that is itself a strategy can't take args here;
                // only global defs can. Capture args as closures over `env`.
                let def = self
                    .strategies
                    .get(name)
                    .ok_or_else(|| format!("unknown strategy '{}'", name))?;
                if def.params.len() != args.len() {
                    return Err(format!(
                        "strategy '{}' expects {} argument(s), got {}",
                        name,
                        def.params.len(),
                        args.len()
                    ));
                }
                let mut new_env = env_empty();
                for (p, a) in def.params.iter().zip(args.iter()) {
                    let clos = Closure {
                        body: a.clone(),
                        env: env.clone(),
                    };
                    new_env = env_bind(&new_env, p.clone(), clos);
                }
                self.apply_d(&def.body, t, fuel, depth + 1, &new_env)
            }
            Strat::Seq(a, b) => match self.apply_d(a, t, fuel, depth + 1, env)? {
                Some(t1) => self.apply_d(b, &t1, fuel, depth + 1, env),
                None => Ok(None),
            },
            Strat::Choice(a, b) => match self.apply_d(a, t, fuel, depth + 1, env)? {
                Some(t1) => Ok(Some(t1)),
                None => self.apply_d(b, t, fuel, depth + 1, env),
            },
            Strat::Try(a) => match self.apply_d(a, t, fuel, depth + 1, env)? {
                Some(t1) => Ok(Some(t1)),
                None => Ok(Some(t.clone())),
            },
            Strat::Repeat(a) => {
                let mut cur = t.clone();
                loop {
                    match self.apply_d(a, &cur, fuel, depth + 1, env)? {
                        Some(n) => cur = n,
                        None => break,
                    }
                }
                Ok(Some(cur))
            }
            Strat::All(a) => self.all_apply(a, t, fuel, depth + 1, env),
            Strat::TopDown(a) => match self.apply_d(a, t, fuel, depth + 1, env)? {
                None => Ok(None),
                Some(t1) => self.all_apply(&Strat::TopDown(a.clone()), &t1, fuel, depth + 1, env),
            },
            Strat::BottomUp(a) => {
                match self.all_apply(&Strat::BottomUp(a.clone()), t, fuel, depth + 1, env)? {
                    None => Ok(None),
                    Some(t1) => self.apply_d(a, &t1, fuel, depth + 1, env),
                }
            }
            Strat::Innermost(a) => {
                let r = self.innermost(a, t, fuel, depth + 1, env)?;
                Ok(Some(r))
            }
            Strat::OnceTd(a) => self.once(a, t, fuel, depth + 1, true, env),
            Strat::OnceBu(a) => self.once(a, t, fuel, depth + 1, false, env),
            Strat::FixPoint(a) => {
                let mut cur = t.clone();
                loop {
                    match self.apply_d(a, &cur, fuel, depth + 1, env)? {
                        Some(n) => {
                            if n == cur {
                                break; // reached a fixed point (no change)
                            }
                            cur = n;
                        }
                        None => break,
                    }
                }
                Ok(Some(cur))
            }
        }
    }

    /// Apply a strategy to every immediate child; succeed only if it succeeds on
    /// all of them (Stratego `all`). Atoms succeed vacuously.
    fn all_apply(
        &self,
        s: &Strat,
        t: &Term,
        fuel: &mut u64,
        depth: usize,
        env: &Env,
    ) -> Result<Option<Term>, String> {
        match t {
            Term::List(xs) => {
                let mut out = Vec::with_capacity(xs.len());
                for x in xs.iter() {
                    match self.apply_d(s, x, fuel, depth + 1, env)? {
                        Some(x2) => out.push(x2),
                        None => return Ok(None),
                    }
                }
                Ok(Some(Term::list(out)))
            }
            _ => Ok(Some(t.clone())),
        }
    }

    /// Apply `s` exactly once, at the first position (top-down if `td`, else
    /// bottom-up) where it succeeds. Fails if `s` succeeds nowhere. This is the
    /// building block of normal-order reduction: `repeat(oncetd(s))` reduces the
    /// leftmost-outermost redex first, which terminates for `if`-guarded
    /// recursive definitions that innermost evaluation would loop on.
    fn once(
        &self,
        s: &Strat,
        t: &Term,
        fuel: &mut u64,
        depth: usize,
        td: bool,
        env: &Env,
    ) -> Result<Option<Term>, String> {
        let memo = td && self.memo.is_some() && is_std_inner(s) && matches!(t, Term::List(_));
        if memo && self.memo_known(t) {
            return Ok(None);
        }
        if td {
            if let Some(t2) = self.apply_d(s, t, fuel, depth + 1, env)? {
                return Ok(Some(t2));
            }
        }
        if is_record(t) {
            // RECORD ENTRIES ARE LABELS, NOT CALLS: in `(rec (k v) ...)` only
            // the values are evaluation positions. Without this, a field whose
            // name happens to coincide with a function (a field `(pop 3)` next
            // to a rule `(pop ?s)`) would be rewritten as a call.
            if let Term::List(xs) = t {
                for i in 1..xs.len() {
                    if let Term::List(kv) = &xs[i] {
                        if let Some(v2) = self.once(s, &kv[1], fuel, depth + 1, td, env)? {
                            let mut v = xs.to_vec();
                            v[i] = Term::list(vec![kv[0].clone(), v2]);
                            return Ok(Some(Term::list(v)));
                        }
                    }
                }
            }
        } else if let Term::List(xs) = t {
            for i in 0..xs.len() {
                if let Some(ci) = self.once(s, &xs[i], fuel, depth + 1, td, env)? {
                    let mut v = xs.to_vec();
                    v[i] = ci;
                    return Ok(Some(Term::list(v)));
                }
            }
        }
        if !td {
            if let Some(t2) = self.apply_d(s, t, fuel, depth + 1, env)? {
                return Ok(Some(t2));
            }
        }
        if memo {
            self.memo_insert(t);
        }
        Ok(None)
    }

    /// Reduce to a normal form w.r.t. `s` using innermost (leftmost-innermost)
    /// evaluation: normalize children first, then apply `s` at the root and
    /// repeat. Always succeeds (returns the normal form); bounded by fuel.
    fn innermost(
        &self,
        s: &Strat,
        t: &Term,
        fuel: &mut u64,
        depth: usize,
        env: &Env,
    ) -> Result<Term, String> {
        // First normalize children.
        let t1 = match t {
            Term::List(xs) if is_record(t) => {
                // record entries are labels: normalize the values only
                let mut out = Vec::with_capacity(xs.len());
                out.push(xs[0].clone());
                for e in xs[1..].iter() {
                    if let Term::List(kv) = e {
                        let v = self.innermost(s, &kv[1], fuel, depth + 1, env)?;
                        out.push(Term::list(vec![kv[0].clone(), v]));
                    }
                }
                Term::list(out)
            }
            Term::List(xs) => {
                let mut out = Vec::with_capacity(xs.len());
                for x in xs.iter() {
                    out.push(self.innermost(s, x, fuel, depth + 1, env)?);
                }
                Term::list(out)
            }
            _ => t.clone(),
        };
        // Then try the root; if it fires, the result may expose new redexes.
        match self.apply_d(s, &t1, fuel, depth + 1, env)? {
            Some(t2) => self.innermost(s, &t2, fuel, depth + 1, env),
            None => Ok(t1),
        }
    }
}

// --------------------------------------------------------------- primitives ---

fn boolsym(b: bool) -> Term {
    Term::Sym(if b { "true" } else { "false" }.to_string())
}

/// Evaluate a built-in primitive application. Returns `Some(value)` only when
/// the operator is known and its operands are already literal values, so that
/// under normal-order (`oncetd`) reduction a primitive never fires prematurely
/// on an unreduced argument.
pub fn eval_prim(t: &Term) -> Option<Term> {
    let xs = match t {
        Term::List(xs) => xs,
        _ => return None,
    };
    // Record primitives (variadic): `@`, `set@`, `add@`, `has@`.
    if let Some(Term::Sym(op)) = xs.first() {
        match op.as_str() {
            "@" | "set@" | "add@" | "has@" | "put@" | "del@" | "keys@" | "sum@" => {
                return eval_record_prim(op, &xs[1..])
            }
            _ => {}
        }
    }
    // Unary primitives.
    if xs.len() == 2 {
        if let Term::Sym(op) = &xs[0] {
            match op.as_str() {
                "str" => {
                    // Render a symbol, integer, or string as a string literal.
                    return match &xs[1] {
                        Term::Sym(s) => Some(Term::Str(s.clone())),
                        Term::Int(n) => Some(Term::Str(n.to_string())),
                        Term::Num(q) => Some(Term::Str(crate::num::fmt_rat(q))),
                        Term::Str(s) => Some(Term::Str(s.clone())),
                        Term::List(_) => None,
                    };
                }
                "sym" => {
                    // Turn a string into a symbol (the inverse of `str`); enables
                    // computed / freshly-generated names.
                    return match &xs[1] {
                        Term::Str(s) => Some(Term::Sym(s.clone())),
                        _ => None,
                    };
                }
                "explode" => {
                    // "abc" -> (list "a" "b" "c"): bridge strings into the list world.
                    return match &xs[1] {
                        Term::Str(s) => {
                            let mut v = vec![Term::Sym("list".to_string())];
                            for c in s.chars() {
                                v.push(Term::Str(c.to_string()));
                            }
                            Some(Term::list(v))
                        }
                        _ => None,
                    };
                }
                "implode" => {
                    // (list "a" "b" "c") -> "abc". Fires only on a list of strings.
                    if let Term::List(items) = &xs[1] {
                        if let Some(Term::Sym(h)) = items.first() {
                            if h == "list" {
                                let mut out = String::new();
                                for it in &items[1..] {
                                    match it {
                                        Term::Str(s) => out.push_str(s),
                                        _ => return None,
                                    }
                                }
                                return Some(Term::Str(out));
                            }
                        }
                    }
                    return None;
                }
                "abs" => return crate::num::abs(&xs[1]),
                // exact-number helpers (see num.rs)
                "num" => return crate::num::numer(&xs[1]),
                "den" => return crate::num::denom(&xs[1]),
                "floor" => return crate::num::floor(&xs[1]),
                "ceil" => return crate::num::ceil(&xs[1]),
                "isqrt" => return crate::num::isqrt(&xs[1]),
                "number?" => {
                    // fires on atoms only, so an unevaluated call is reduced first
                    return match &xs[1] {
                        Term::List(_) => None,
                        t => Some(boolsym(crate::num::is_num(t))),
                    };
                }
                "rng" => {
                    // Deterministic pseudo-random hash (splitmix64) of an integer
                    // seed, returned as a non-negative i64. Pure and reproducible:
                    // the same seed always yields the same value, so stochastic
                    // programs still self-rewrite to byte-identical quines.
                    return match &xs[1] {
                        Term::Int(n) => {
                            let mut z = (*n as u64).wrapping_add(0x9E3779B97F4A7C15);
                            z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
                            z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
                            z ^= z >> 31;
                            Some(Term::Int((z >> 1) as i64)) // >>1 clears sign bit -> nonneg
                        }
                        _ => None,
                    };
                }
                _ => return None,
            }
        }
        return None;
    }
    if xs.len() != 3 {
        return None;
    }
    let op = match &xs[0] {
        Term::Sym(s) => s.as_str(),
        _ => return None,
    };
    let (a, b) = (&xs[1], &xs[2]);
    use crate::num;
    use std::cmp::Ordering::*;
    match op {
        // Arithmetic and comparison work on all exact numbers: i64 fast path,
        // exact big rationals on overflow or when an operand is a `Num`.
        "+" => num::add(a, b),
        "-" => num::sub(a, b),
        "*" => num::mul(a, b),
        // `/` and `mod` stay INTEGER operations (truncating / Euclidean), on
        // integers of any size; `q/` is exact division.
        "/" => num::idiv(a, b),
        "mod" => num::imod(a, b),
        "q/" => num::qdiv(a, b),
        "round-to" => num::round_to(a, b),
        "expt" => num::expt(a, b),
        "decimal" => num::dec(a, b),
        "<" => Some(boolsym(num::cmp(a, b)? == Less)),
        "<=" => Some(boolsym(num::cmp(a, b)? != Greater)),
        ">" => Some(boolsym(num::cmp(a, b)? == Greater)),
        ">=" => Some(boolsym(num::cmp(a, b)? != Less)),
        // Equality on primitive literal values only (numbers, strings, symbols).
        "=" | "<>" => {
            let both_prim = matches!(
                (a, b),
                (Term::Str(_), Term::Str(_)) | (Term::Sym(_), Term::Sym(_))
            ) || (num::is_num(a) && num::is_num(b));
            if !both_prim {
                return None;
            }
            let eq = a == b;
            Some(boolsym(if op == "=" { eq } else { !eq }))
        }
        "cat" => match (a, b) {
            (Term::Str(x), Term::Str(y)) => Some(Term::Str(format!("{}{}", x, y))),
            _ => None,
        },
        // -- reflection: descriptive containment as a first-class predicate ----
        // `matches?` and `match-witness` reify the interpreter's own pattern
        // matcher (the mechanism a `rule LHS` uses, meta-level, to select
        // which subjects it governs) as an object-level function over ordinary
        // term DATA. A "pattern" here is just a term that happens to contain
        // `?x` / `?xs...` symbols; nothing distinguishes it syntactically from
        // any other term until it is passed as the first argument here. This is
        // the one thing the pure rule language cannot express on its own: a
        // `rule` LHS is fixed at parse time, so a program can never match a
        // *runtime-computed* pattern against a subject — every existing
        // rule-based predicate (like library `equal?`) can only compare a
        // subject against a pattern written literally into that rule's source.
        // `matches?` decides descriptive containment: does the SCHEMA `a`
        // (finitely written) contain the ground term `b` as an instance —
        // `?sigma. sigma(a) = b`? Fires unconditionally at the root (like
        // `equal?`), so `a` and `b` are compared exactly as they stand: this
        // makes `matches?` a genuine reification of matching, not a shortcut
        // for it.
        "matches?" => Some(boolsym(match_term(a, b, Bindings::default()).is_some())),
        // Constructive counterpart: reify the witnessing substitution itself
        // (see `eval_match_witness` below) instead of just a boolean.
        "match-witness" => Some(eval_match_witness(a, b)),
        "str<" => match (a, b) {
            (Term::Str(x), Term::Str(y)) => Some(boolsym(x < y)),
            _ => None,
        },
        "min" => Some(if num::cmp(a, b)? == Greater { b.clone() } else { a.clone() }),
        "max" => Some(if num::cmp(a, b)? == Less { b.clone() } else { a.clone() }),
        "padl" | "padr" => match (a, b) {
            // pad a string with spaces to a given width (padl = right-justify,
            // padr = left-justify); longer strings are returned unchanged.
            (Term::Str(s), Term::Int(w)) => {
                let w = (*w).max(0) as usize;
                let l = s.chars().count();
                if l >= w {
                    Some(Term::Str(s.clone()))
                } else {
                    let pad = " ".repeat(w - l);
                    Some(Term::Str(if op == "padl" {
                        format!("{}{}", pad, s)
                    } else {
                        format!("{}{}", s, pad)
                    }))
                }
            }
            _ => None,
        },
        _ => None,
    }
}

// ------------------------------------------------------- record primitives ---
//
// A RECORD is a term `(rec (k1 v1) (k2 v2) ...)` whose keys are symbols. Records
// are ordinary terms (they print, match, and self-rewrite like any other data);
// these primitives just give O(n) native field access so that a large model
// state can be read and updated without a hand-written rule per field.
//
//   (@ R k1 ... kn)        value at the key path k1/.../kn (nested records)
//   (set@ R k1 ... kn V)   R with that field replaced by V
//   (add@ R k1 ... kn D)   R with that (integer) field incremented by integer D
//   (has@ R k)             true / false: does R have key k at top level
//   (put@ R k V)           insert-or-replace top-level key k (new keys go last)
//   (del@ R k)             R without top-level key k (no-op if absent)
//   (keys@ R)              (list k1 k2 ...) in record order
//   (sum@ R)               sum of R's top-level values (fires only if all are ints)
//
// `put@`/`del@` are the only primitives that change a record's key set, so a
// model that never calls them has a fixed schema.
//
// CLOSED WORLD: a missing key (or a non-record on the path, or a non-integer
// under `add@`) makes the primitive NOT FIRE. The term stays stuck, visibly,
// instead of silently inventing a field -- a typo in a model is a stuck term in
// the output, never a wrong number. Values are never forced: a field may hold an
// unevaluated expression, which normal-order evaluation reduces in place later.
// Like every primitive these fire only on literal record structure, so under
// `outermost` an argument that is still a rule call is reduced first.

/// A record: `(rec (k v) ...)` where every entry is a pair with a symbol key.
pub fn is_record(t: &Term) -> bool {
    match rec_entries(t) {
        Some(es) => es.iter().all(|e| matches!(e, Term::List(kv) if kv.len() == 2 && matches!(kv[0], Term::Sym(_)))),
        None => false,
    }
}

fn rec_entries(r: &Term) -> Option<&[Term]> {
    match r {
        Term::List(xs) if matches!(xs.first(), Some(Term::Sym(h)) if h == "rec") => Some(&xs[1..]),
        _ => None,
    }
}

fn rec_find(r: &Term, key: &Term) -> Option<usize> {
    let es = rec_entries(r)?;
    if !matches!(key, Term::Sym(_)) {
        return None;
    }
    es.iter().position(|e| matches!(e, Term::List(kv) if kv.len() == 2 && &kv[0] == key))
        .map(|i| i + 1)
}

fn rec_get<'a>(r: &'a Term, path: &[Term]) -> Option<&'a Term> {
    let mut cur = r;
    for k in path {
        let i = rec_find(cur, k)?;
        match cur {
            Term::List(xs) => match &xs[i] {
                Term::List(kv) => cur = &kv[1],
                _ => return None,
            },
            _ => return None,
        }
    }
    Some(cur)
}

fn rec_update(r: &Term, path: &[Term], f: &dyn Fn(&Term) -> Option<Term>) -> Option<Term> {
    if path.is_empty() {
        return f(r);
    }
    let i = rec_find(r, &path[0])?;
    let Term::List(xs) = r else { return None };
    let Term::List(kv) = &xs[i] else { return None };
    let nv = rec_update(&kv[1], &path[1..], f)?;
    let mut out = xs.to_vec();
    out[i] = Term::list(vec![kv[0].clone(), nv]);
    Some(Term::list(out))
}

fn eval_record_prim(op: &str, args: &[Term]) -> Option<Term> {
    match op {
        "@" => {
            if args.len() < 2 {
                return None;
            }
            rec_get(&args[0], &args[1..]).cloned()
        }
        "has@" => {
            if args.len() != 2 {
                return None;
            }
            rec_entries(&args[0])?;
            Some(boolsym(rec_find(&args[0], &args[1]).is_some()))
        }
        "set@" => {
            if args.len() < 3 {
                return None;
            }
            let v = args[args.len() - 1].clone();
            rec_update(&args[0], &args[1..args.len() - 1], &|_| Some(v.clone()))
        }
        "add@" => {
            if args.len() < 3 {
                return None;
            }
            let d = args[args.len() - 1].clone();
            if !crate::num::is_num(&d) {
                return None;
            }
            rec_update(&args[0], &args[1..args.len() - 1], &|old| crate::num::add(old, &d))
        }
        "put@" => {
            if args.len() != 3 || !matches!(args[1], Term::Sym(_)) {
                return None;
            }
            rec_entries(&args[0])?;
            let entry = Term::list(vec![args[1].clone(), args[2].clone()]);
            let Term::List(xs) = &args[0] else { return None };
            let mut out = xs.to_vec();
            match rec_find(&args[0], &args[1]) {
                Some(i) => out[i] = entry,
                None => out.push(entry),
            }
            Some(Term::list(out))
        }
        "del@" => {
            if args.len() != 2 {
                return None;
            }
            rec_entries(&args[0])?;
            let Term::List(xs) = &args[0] else { return None };
            let mut out = xs.to_vec();
            if let Some(i) = rec_find(&args[0], &args[1]) {
                out.remove(i);
            }
            Some(Term::list(out))
        }
        "keys@" => {
            if args.len() != 1 {
                return None;
            }
            let es = rec_entries(&args[0])?;
            let mut out = vec![Term::Sym("list".into())];
            for e in es {
                match e {
                    Term::List(kv) if kv.len() == 2 => out.push(kv[0].clone()),
                    _ => return None,
                }
            }
            Some(Term::list(out))
        }
        "sum@" => {
            if args.len() != 1 {
                return None;
            }
            let es = rec_entries(&args[0])?;
            let mut tot = Term::Int(0);
            for e in es {
                match e {
                    Term::List(kv) if kv.len() == 2 && crate::num::is_num(&kv[1]) => tot = crate::num::add(&tot, &kv[1])?,
                    _ => return None,
                }
            }
            Some(tot)
        }
        _ => None,
    }
}

/// `match-witness`: like `matches?`, but on success returns the *substitution*
/// `sigma` itself, reified as a term — `(some (dict (entry name val) ...))` —
/// rather than just a boolean. This is the constructive half of descriptive
/// containment: a bare `matches?` only asserts `exists sigma. sigma(a) = b`;
/// this exhibits the witnessing `sigma`. Entries are sorted by variable name
/// for determinism (a `HashMap`'s iteration order is not stable, and
/// Palimpsest's self-rewriting quines depend on every primitive being
/// reproducible byte-for-byte). A sequence-variable binding is rendered as
/// `(list ...)`, matching the convention `explode` and library code already
/// use for runtime-built sequences. Returns `none` when `a` does not match `b`.
fn eval_match_witness(a: &Term, b: &Term) -> Term {
    match match_term(a, b, Bindings::default()) {
        None => Term::Sym("none".to_string()),
        Some(bindings) => {
            let mut names: Vec<&String> = bindings.keys().collect();
            names.sort();
            let mut entries = vec![Term::Sym("dict".to_string())];
            for name in names {
                let val = match &bindings[name] {
                    Binding::One(t) => t.clone(),
                    Binding::Seq(v) => {
                        let mut lst = vec![Term::Sym("list".to_string())];
                        lst.extend(v.iter().cloned());
                        Term::list(lst)
                    }
                };
                entries.push(Term::list(vec![
                    Term::Sym("entry".to_string()),
                    Term::Sym(name.clone()),
                    val,
                ]));
            }
            Term::list(vec![Term::Sym("some".to_string()), Term::list(entries)])
        }
    }
}

// ------------------------------------------------------------------ parser ---

/// Parse a strategy expression. Grammar (lowest to highest precedence):
///   seq    := choice (';' choice)*
///   choice := postfix ('+' postfix)*
///   atom   := 'id' | 'fail' | 'rules'
///           | NAME '(' seq ')'        (combinator: try/repeat/topdown/...)
///           | NAME                    (rule or strategy reference)
///           | '(' seq ')'
pub fn parse_strategy(input: &str) -> Result<Strat, String> {
    let toks = lex_strat(input);
    let mut p = SParser { toks, pos: 0 };
    let s = p.parse_seq()?;
    if p.pos != p.toks.len() {
        return Err(format!("trailing tokens in strategy near '{}'", p.rest()));
    }
    Ok(s)
}

#[derive(Debug, Clone, PartialEq)]
enum ST {
    Ident(String),
    LParen,
    RParen,
    Semi,
    Plus,
    Comma,
}

fn lex_strat(input: &str) -> Vec<ST> {
    let mut out = Vec::new();
    let mut chars = input.chars().peekable();
    while let Some(&c) = chars.peek() {
        match c {
            '(' => {
                out.push(ST::LParen);
                chars.next();
            }
            ')' => {
                out.push(ST::RParen);
                chars.next();
            }
            ';' => {
                out.push(ST::Semi);
                chars.next();
            }
            '+' => {
                out.push(ST::Plus);
                chars.next();
            }
            ',' => {
                out.push(ST::Comma);
                chars.next();
            }
            c if c.is_whitespace() => {
                chars.next();
            }
            _ => {
                let mut s = String::new();
                while let Some(&c) = chars.peek() {
                    if c.is_whitespace() || "();+,".contains(c) {
                        break;
                    }
                    s.push(c);
                    chars.next();
                }
                out.push(ST::Ident(s));
            }
        }
    }
    out
}

struct SParser {
    toks: Vec<ST>,
    pos: usize,
}

impl SParser {
    fn rest(&self) -> String {
        self.toks[self.pos..]
            .iter()
            .map(|t| format!("{:?}", t))
            .collect::<Vec<_>>()
            .join(" ")
    }

    fn parse_seq(&mut self) -> Result<Strat, String> {
        let mut left = self.parse_choice()?;
        while self.pos < self.toks.len() && self.toks[self.pos] == ST::Semi {
            self.pos += 1;
            let right = self.parse_choice()?;
            left = Strat::Seq(Box::new(left), Box::new(right));
        }
        Ok(left)
    }

    fn parse_choice(&mut self) -> Result<Strat, String> {
        let mut left = self.parse_atom()?;
        while self.pos < self.toks.len() && self.toks[self.pos] == ST::Plus {
            self.pos += 1;
            let right = self.parse_atom()?;
            left = Strat::Choice(Box::new(left), Box::new(right));
        }
        Ok(left)
    }

    fn parse_atom(&mut self) -> Result<Strat, String> {
        if self.pos >= self.toks.len() {
            return Err("unexpected end of strategy".into());
        }
        match self.toks[self.pos].clone() {
            ST::LParen => {
                self.pos += 1;
                let inner = self.parse_seq()?;
                self.expect(ST::RParen)?;
                Ok(inner)
            }
            ST::Ident(name) => {
                self.pos += 1;
                // Application with parenthesized argument list?
                if self.pos < self.toks.len() && self.toks[self.pos] == ST::LParen {
                    self.pos += 1;
                    let mut args = vec![self.parse_seq()?];
                    while self.pos < self.toks.len() && self.toks[self.pos] == ST::Comma {
                        self.pos += 1;
                        args.push(self.parse_seq()?);
                    }
                    self.expect(ST::RParen)?;
                    if is_builtin_combinator(&name) {
                        if args.len() != 1 {
                            return Err(format!("combinator '{}' takes exactly 1 argument", name));
                        }
                        return build_combinator(&name, args.into_iter().next().unwrap());
                    }
                    return Ok(Strat::Call(name, args));
                }
                Ok(match name.as_str() {
                    "id" => Strat::Id,
                    "fail" => Strat::Fail,
                    "rules" => Strat::AllRules,
                    "prim" => Strat::Prim,
                    _ => Strat::Ref(name),
                })
            }
            other => Err(format!("unexpected token in strategy: {:?}", other)),
        }
    }

    fn expect(&mut self, t: ST) -> Result<(), String> {
        if self.pos < self.toks.len() && self.toks[self.pos] == t {
            self.pos += 1;
            Ok(())
        } else {
            Err(format!("expected {:?} in strategy", t))
        }
    }
}

fn is_builtin_combinator(name: &str) -> bool {
    matches!(
        name,
        "try" | "repeat"
            | "topdown"
            | "bottomup"
            | "innermost"
            | "oncetd"
            | "oncebu"
            | "outermost"
            | "fixpoint"
            | "all"
    )
}

fn build_combinator(name: &str, arg: Strat) -> Result<Strat, String> {
    let b = Box::new(arg);
    Ok(match name {
        "try" => Strat::Try(b),
        "repeat" => Strat::Repeat(b),
        "topdown" => Strat::TopDown(b),
        "bottomup" => Strat::BottomUp(b),
        "innermost" => Strat::Innermost(b),
        "oncetd" => Strat::OnceTd(b),
        "oncebu" => Strat::OnceBu(b),
        // outermost(s) = repeat(oncetd(s)): normal-order normalization.
        "outermost" => Strat::Repeat(Box::new(Strat::OnceTd(b))),
        "fixpoint" => Strat::FixPoint(b),
        "all" => Strat::All(b),
        other => return Err(format!("unknown combinator '{}'", other)),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::term::read_term;

    fn peano_engine() -> Engine {
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "add-zero".into(),
            lhs: read_term("(+ ?x 0)").unwrap(),
            rhs: read_term("?x").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "add-suc".into(),
            lhs: read_term("(+ ?x (S ?y))").unwrap(),
            rhs: read_term("(S (+ ?x ?y))").unwrap(),
            conds: vec![],
        });
        e
    }

    #[test]
    fn innermost_peano() {
        let e = peano_engine();
        let s = parse_strategy("innermost(add-zero + add-suc)").unwrap();
        let mut fuel = 1000u64;
        let t = read_term("(+ (S (S 0)) (S 0))").unwrap();
        let out = e.apply(&s, &t, &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "(S (S (S 0)))");
    }

    #[test]
    fn fixpoint_selfmap_terminates() {
        // (app ?d (quote ?d)) => (app ?d (quote ?d)) is a genuine redex whose
        // normal form is itself. fixpoint must halt on no-change.
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "q".into(),
            lhs: read_term("(app ?c (quote ?d))").unwrap(),
            rhs: read_term("(app ?d (quote ?d))").unwrap(),
            conds: vec![],
        });
        let s = parse_strategy("fixpoint(q)").unwrap();
        let mut fuel = 1000u64;
        let t = read_term("(app self (quote self))").unwrap();
        let out = e.apply(&s, &t, &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "(app self (quote self))");
    }

    #[test]
    fn primitives_evaluate() {
        let e = Engine::new();
        let s = parse_strategy("outermost(prim)").unwrap();
        let mut fuel = 1000u64;
        let t = read_term("(+ (* 2 3) (- 10 6))").unwrap();
        let out = e.apply(&s, &t, &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "10");
    }

    #[test]
    fn prim_waits_for_reduced_args() {
        // '=' must not fire on an unreduced left operand.
        let e = Engine::new();
        let s = parse_strategy("outermost(prim)").unwrap();
        let mut fuel = 1000u64;
        let t = read_term("(= (+ 1 1) 2)").unwrap();
        let out = e.apply(&s, &t, &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "true");
    }

    #[test]
    fn normal_order_recursion_terminates() {
        // A countdown that would loop forever under innermost, but terminates
        // under outermost because `if` collapses before the dead branch grows.
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "if-t".into(),
            lhs: read_term("(if true ?t ?e)").unwrap(),
            rhs: read_term("?t").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "if-f".into(),
            lhs: read_term("(if false ?t ?e)").unwrap(),
            rhs: read_term("?e").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "count".into(),
            lhs: read_term("(count ?n)").unwrap(),
            rhs: read_term("(if (<= ?n 0) done (count (- ?n 1)))").unwrap(),
            conds: vec![],
        });
        let s = parse_strategy("outermost(prim + rules)").unwrap();
        let mut fuel = 100_000u64;
        let t = read_term("(count 5)").unwrap();
        let out = e.apply(&s, &t, &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "done");
    }

    #[test]
    fn conditional_rule_guard() {
        // (mx a b) => a where (>= a b), else => b
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "mx-a".into(),
            lhs: read_term("(mx ?a ?b)").unwrap(),
            rhs: read_term("?a").unwrap(),
            conds: vec![WhereClause::Guard(read_term("(>= ?a ?b)").unwrap())],
        });
        e.add_rule(Rule {
            name: "mx-b".into(),
            lhs: read_term("(mx ?a ?b)").unwrap(),
            rhs: read_term("?b").unwrap(),
            conds: vec![],
        });
        let s = parse_strategy("outermost(prim + rules)").unwrap();
        let mut fuel = 10_000u64;
        let out = e.apply(&s, &read_term("(mx 3 7)").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "7");
        let out2 = e.apply(&s, &read_term("(mx 9 2)").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out2), "9");
    }

    #[test]
    fn where_binding() {
        // (twice-plus1 n) => (r m) where m <- (+ (* n 2) 1)
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "tp".into(),
            lhs: read_term("(tp ?n)").unwrap(),
            rhs: read_term("(r ?m)").unwrap(),
            conds: vec![WhereClause::Bind("m".into(), read_term("(+ (* ?n 2) 1)").unwrap())],
        });
        let s = parse_strategy("outermost(prim + rules)").unwrap();
        let mut fuel = 10_000u64;
        let out = e.apply(&s, &read_term("(tp 10)").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "(r 21)");
    }

    #[test]
    fn parameterized_strategy() {
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "dbl".into(),
            lhs: read_term("(dbl ?n)").unwrap(),
            rhs: read_term("(* ?n 2)").unwrap(),
            conds: vec![],
        });
        e.strategies.insert(
            "simplify".into(),
            StratDef {
                params: vec!["s".into()],
                body: parse_strategy("innermost(s + prim)").unwrap(),
            },
        );
        let call = parse_strategy("simplify(dbl)").unwrap();
        let mut fuel = 10_000u64;
        let out = e.apply(&call, &read_term("(dbl (dbl 5))").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "20");
    }

    #[test]
    fn recursive_parameterized_strategy() {
        // rep(s) = try(s ; rep(s)) — repeat, defined in-language.
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "dec".into(),
            lhs: read_term("(S ?n)").unwrap(),
            rhs: read_term("?n").unwrap(),
            conds: vec![],
        });
        e.strategies.insert(
            "rep".into(),
            StratDef {
                params: vec!["s".into()],
                body: parse_strategy("try(s ; rep(s))").unwrap(),
            },
        );
        let call = parse_strategy("rep(dec)").unwrap();
        let mut fuel = 10_000u64;
        let out = e.apply(&call, &read_term("(S (S (S 0)))").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "0");
    }

    #[test]
    fn str_primitive_renders() {
        let e = Engine::new();
        let s = parse_strategy("outermost(prim)").unwrap();
        let mut fuel = 1000u64;
        let a = e.apply(&s, &read_term("(str hello)").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", a), "\"hello\"");
        let b = e.apply(&s, &read_term("(cat \"n=\" (str 7))").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", b), "\"n=7\"");
    }

    #[test]
    fn numeric_and_rng_primitives() {
        let cases = [
            ("(abs (- 3 8))", "5"),
            ("(abs 7)", "7"),
            ("(min 4 9)", "4"),
            ("(max 4 9)", "9"),
            ("(padl \"7\" 3)", "\"  7\""),
            ("(padr \"7\" 3)", "\"7  \""),
            ("(padl \"long\" 2)", "\"long\""),
        ];
        for (input, want) in cases {
            let e = Engine::new();
            let mut fuel = 10000u64;
            let out = e
                .apply(&parse_strategy("innermost(prim)").unwrap(), &read_term(input).unwrap(), &mut fuel)
                .unwrap()
                .unwrap_or_else(|| read_term(input).unwrap());
            assert_eq!(format!("{}", out), want, "for {}", input);
        }
        // rng is deterministic, non-negative, and distinguishes distinct seeds.
        let r = |s: &str| {
            let e = Engine::new();
            let mut fuel = 1000u64;
            let out = e.apply(&parse_strategy("prim").unwrap(), &read_term(s).unwrap(), &mut fuel).unwrap().unwrap();
            match out { Term::Int(n) => n, _ => panic!("rng not an int") }
        };
        assert_eq!(r("(rng 1)"), r("(rng 1)"), "rng must be deterministic");
        assert!(r("(rng 1)") >= 0, "rng must be non-negative");
        assert_ne!(r("(rng 1)"), r("(rng 2)"), "distinct seeds should differ");
    }

    #[test]
    fn reflective_matching_primitives() {
        // `matches?`: descriptive containment as a decidable predicate — does
        // pattern `a` (a finite schema) contain ground term `b` as an instance?
        let cases = [
            ("(matches? (foo ?x) (foo 1))", "true"),
            ("(matches? (foo ?x) (bar 1))", "false"),
            // non-linear: the SAME variable twice must bind equal subterms.
            ("(matches? (foo ?x ?x) (foo 1 1))", "true"),
            ("(matches? (foo ?x ?x) (foo 1 2))", "false"),
            // a sequence variable descriptively contains lists of any length —
            // one finite pattern subsumes an unbounded family of subjects.
            ("(matches? (list ?xs...) (list))", "true"),
            ("(matches? (list ?xs...) (list a b c))", "true"),
            ("(matches? (list ?xs...) (pair a b))", "false"),
            // the generic decomposition idiom used throughout lib/ (e.g. `shw`):
            // `(?h ?rest...)` matches any nonempty compound term whatsoever.
            ("(matches? (?h ?rest...) (pt 1 2))", "true"),
            ("(matches? (?h ?rest...) 5)", "false"),
        ];
        for (input, want) in cases {
            let e = Engine::new();
            let mut fuel = 1000u64;
            let out = e
                .apply(&parse_strategy("prim").unwrap(), &read_term(input).unwrap(), &mut fuel)
                .unwrap()
                .unwrap();
            assert_eq!(format!("{}", out), want, "for {}", input);
        }

        // `match-witness`: the constructive counterpart — reify the witnessing
        // substitution sigma such that sigma(a) = b, sorted by variable name.
        let witness_cases = [
            ("(match-witness (foo ?x) (foo 1))", "(some (dict (entry x 1)))"),
            ("(match-witness (foo ?x) (bar 1))", "none"),
            (
                "(match-witness (pair ?x ?y) (pair 1 2))",
                "(some (dict (entry x 1) (entry y 2)))",
            ),
            (
                "(match-witness (list ?xs...) (list a b c))",
                "(some (dict (entry xs (list a b c))))",
            ),
        ];
        for (input, want) in witness_cases {
            let e = Engine::new();
            let mut fuel = 1000u64;
            let out = e
                .apply(&parse_strategy("prim").unwrap(), &read_term(input).unwrap(), &mut fuel)
                .unwrap()
                .unwrap();
            assert_eq!(format!("{}", out), want, "for {}", input);
        }
    }

    #[test]
    fn strict_var_forces_argument_before_matching() {
        // `grab`'s ARGUMENT is `(mk 5)`, an unreduced call to another rule
        // in the same engine. With an ordinary `?x`, `grab` fires on the
        // literal, unreduced syntax `(mk 5)` -- exactly the hazard
        // documented on `equal?` in lib/logic.pal, and the one that
        // silently produced a wrong `size` in the CTMU model before this
        // feature existed. With `!x`, the subject at that position is fully
        // normalized (here: to `(pair 5 5)`) before `grab` ever matches.
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "mk".into(),
            lhs: read_term("(mk ?n)").unwrap(),
            rhs: read_term("(pair ?n ?n)").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "grab-lazy".into(),
            lhs: read_term("(grab-lazy ?x)").unwrap(),
            rhs: read_term("?x").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "grab-strict".into(),
            lhs: read_term("(grab-strict !x)").unwrap(),
            rhs: read_term("?x").unwrap(),
            conds: vec![],
        });
        let mut fuel = 1000u64;
        let strat = parse_strategy("rules").unwrap();

        let lazy = e
            .apply(&strat, &read_term("(grab-lazy (mk 5))").unwrap(), &mut fuel)
            .unwrap()
            .unwrap();
        assert_eq!(format!("{}", lazy), "(mk 5)", "lazy ?x sees the unreduced call");

        let strict = e
            .apply(&strat, &read_term("(grab-strict (mk 5))").unwrap(), &mut fuel)
            .unwrap()
            .unwrap();
        assert_eq!(format!("{}", strict), "(pair 5 5)", "!x forces it first");

        // A subject that is already a value is unaffected (forcing a normal
        // form is a no-op) -- the feature is purely additive.
        let already_value = e
            .apply(&strat, &read_term("(grab-strict 5)").unwrap(), &mut fuel)
            .unwrap()
            .unwrap();
        assert_eq!(format!("{}", already_value), "5");
    }

    #[test]
    fn strict_var_nonlinear_forces_both_occurrences() {
        // `!x` appearing twice must force EACH occurrence independently,
        // then require the two (now-forced) values to be equal, exactly
        // like non-linear `?x` already does once both sides are values.
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "mk".into(),
            lhs: read_term("(mk ?n)").unwrap(),
            rhs: read_term("(pair ?n ?n)").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "same".into(),
            lhs: read_term("(same !x !x)").unwrap(),
            rhs: read_term("matched").unwrap(),
            conds: vec![],
        });
        let mut fuel = 1000u64;
        let strat = parse_strategy("rules").unwrap();

        // Two different-looking expressions that force to the SAME value.
        let hit = e
            .apply(
                &strat,
                &read_term("(same (mk 5) (pair 5 5))").unwrap(),
                &mut fuel,
            )
            .unwrap();
        assert_eq!(hit.map(|t| format!("{}", t)), Some("matched".to_string()));

        // Two expressions that force to DIFFERENT values: no match.
        let miss = e
            .apply(
                &strat,
                &read_term("(same (mk 5) (pair 5 6))").unwrap(),
                &mut fuel,
            )
            .unwrap();
        assert_eq!(miss, None);
    }

    #[test]
    fn strict_var_mixed_with_top_level_seq_var_does_not_match() {
        // Documented scope limit: if a sequence variable ALSO appears among
        // the pattern's top-level elements, the strict position's subject
        // is not well-defined before matching decides how many elements the
        // sequence variable spans, so forcing is skipped entirely and the
        // literal, un-recognized `!x` simply never matches anything --
        // cleanly (no match, no crash, no silent partial-forcing).
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "mixed".into(),
            lhs: read_term("(mixed ?a... !x)").unwrap(),
            rhs: read_term("used").unwrap(),
            conds: vec![],
        });
        let mut fuel = 1000u64;
        let out = e
            .apply(
                &parse_strategy("rules").unwrap(),
                &read_term("(mixed 1 2 3)").unwrap(),
                &mut fuel,
            )
            .unwrap();
        assert_eq!(out, None);
    }

    #[test]
    fn strict_var_in_conditional_rule_guard() {
        // Strict variables must also work on rules WITH `where` clauses
        // (the conditional path in `apply_rule` is separate from the
        // unconditional fast path).
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "mk".into(),
            lhs: read_term("(mk ?n)").unwrap(),
            rhs: read_term("(pair ?n ?n)").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "equal?-yes".into(),
            lhs: read_term("(equal? ?x ?x)").unwrap(),
            rhs: read_term("true").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "equal?-no".into(),
            lhs: read_term("(equal? ?x ?y)").unwrap(),
            rhs: read_term("false").unwrap(),
            conds: vec![],
        });
        e.add_rule(Rule {
            name: "big".into(),
            lhs: read_term("(big !x)").unwrap(),
            rhs: read_term("yes").unwrap(),
            conds: vec![WhereClause::Guard(read_term("(equal? ?x (pair 5 5))").unwrap())],
        });
        let mut fuel = 1000u64;
        let out = e
            .apply(
                &parse_strategy("rules").unwrap(),
                &read_term("(big (mk 5))").unwrap(),
                &mut fuel,
            )
            .unwrap();
        assert_eq!(out.map(|t| format!("{}", t)), Some("yes".to_string()));
    }

    #[test]
    fn generic_term_printer() {
        // The `shw` renderer (as in lib/render.pal) turns any term into its
        // canonical string: atoms via `str`, lists recursively.
        let mut e = Engine::new();
        for (n, l, r) in [
            ("shw-list", "(shw (?h ?rest...))", "(cat \"(\" (cat (shw-seq (seq ?h ?rest...)) \")\"))"),
            ("shw-atom", "(shw ?a)", "(str ?a)"),
            ("shw-seq-1", "(shw-seq (seq ?x))", "(shw ?x)"),
            ("shw-seq-n", "(shw-seq (seq ?x ?y ?ys...))", "(cat (shw ?x) (cat \" \" (shw-seq (seq ?y ?ys...))))"),
        ] {
            e.add_rule(Rule { name: n.into(), lhs: read_term(l).unwrap(), rhs: read_term(r).unwrap(), conds: vec![] });
        }
        let mut fuel = 100_000u64;
        let out = e
            .apply(&parse_strategy("outermost(prim + rules)").unwrap(), &read_term("(shw (pt 1 (q a)))").unwrap(), &mut fuel)
            .unwrap()
            .unwrap();
        assert_eq!(format!("{}", out), "\"(pt 1 (q a))\"");
    }

    #[test]
    fn string_symbol_primitives() {
        let cases = [
            ("(explode \"abc\")", "(list \"a\" \"b\" \"c\")"),
            ("(implode (list \"a\" \"b\" \"c\"))", "\"abc\""),
            ("(sym \"foo\")", "foo"),
            ("(sym (cat \"v\" (str 7)))", "v7"),
            ("(str< \"apple\" \"banana\")", "true"),
            ("(str< \"banana\" \"apple\")", "false"),
            ("(str< \"a\" \"a\")", "false"),
        ];
        for (input, want) in cases {
            let e = Engine::new();
            let mut fuel = 10000u64;
            let out = e
                .apply(&parse_strategy("innermost(prim)").unwrap(), &read_term(input).unwrap(), &mut fuel)
                .unwrap()
                .unwrap_or_else(|| read_term(input).unwrap());
            assert_eq!(format!("{}", out), want, "for input {}", input);
        }
    }

    #[test]
    fn wildcard_head_rule_still_fires() {
        // A rule whose LHS head is a variable must match any list head — head
        // indexing must not skip it.
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "wild".into(),
            lhs: read_term("(?h ?x)").unwrap(),
            rhs: read_term("(wrapped ?h ?x)").unwrap(),
            conds: vec![],
        });
        let mut fuel = 100u64;
        let out = e
            .apply(&parse_strategy("rules").unwrap(), &read_term("(foo bar)").unwrap(), &mut fuel)
            .unwrap()
            .unwrap();
        assert_eq!(format!("{}", out), "(wrapped foo bar)");
    }

    #[test]
    fn guard_drives_backtracking() {
        // One rule that swaps ANY adjacent out-of-order pair. This only works if
        // a failed guard makes the matcher try another decomposition of the two
        // sequence variables. repeat(oncetd(..)) then bubble-sorts.
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "bubble".into(),
            lhs: read_term("(list ?xs... ?a ?b ?ys...)").unwrap(),
            rhs: read_term("(list ?xs... ?b ?a ?ys...)").unwrap(),
            conds: vec![WhereClause::Guard(read_term("(> ?a ?b)").unwrap())],
        });
        let s = parse_strategy("repeat(oncetd(prim + rules))").unwrap();
        let mut fuel = 500_000u64;
        let t = read_term("(list 5 3 8 1 9 2)").unwrap();
        let out = e.apply(&s, &t, &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", out), "(list 1 2 3 5 8 9)");
    }

    #[test]
    fn record_primitives() {
        let r = "(rec (a 1) (b (rec (c 2) (d x))) (e (+ 1 1)))";
        let cases = [
            (format!("(@ {} a)", r), "1"),
            (format!("(@ {} b c)", r), "2"),
            (format!("(@ {} b d)", r), "x"),
            (format!("(has@ {} e)", r), "true"),
            (format!("(has@ {} zz)", r), "false"),
            (format!("(set@ {} b c 9)", r), "(rec (a 1) (b (rec (c 9) (d x))) (e (+ 1 1)))"),
            (format!("(add@ {} b c 5)", r), "(rec (a 1) (b (rec (c 7) (d x))) (e (+ 1 1)))"),
            (format!("(add@ {} a -3)", r), "(rec (a -2) (b (rec (c 2) (d x))) (e (+ 1 1)))"),
            (format!("(put@ {} z 0)", r), "(rec (a 1) (b (rec (c 2) (d x))) (e (+ 1 1)) (z 0))"),
            (format!("(put@ {} a 0)", r), "(rec (a 0) (b (rec (c 2) (d x))) (e (+ 1 1)))"),
            (format!("(del@ {} b)", r), "(rec (a 1) (e (+ 1 1)))"),
            (format!("(keys@ {})", r), "(list a b e)"),
            ("(sum@ (rec (a 1) (b 2) (c 39)))".to_string(), "42"),
        ];
        for (input, want) in cases {
            let e = Engine::new();
            let mut fuel = 100u64;
            let out = e
                .apply(&parse_strategy("prim").unwrap(), &read_term(&input).unwrap(), &mut fuel)
                .unwrap()
                .unwrap();
            assert_eq!(format!("{}", out), want, "for {}", input);
        }
        // closed world: missing keys, non-records and non-integers do not fire
        for stuck in [
            format!("(@ {} zz)", r),
            format!("(set@ {} zz 1)", r),
            format!("(add@ {} b d 1)", r),
            format!("(add@ {} e 1)", r),
            "(@ (notrec (a 1)) a)".to_string(),
            format!("(sum@ {})", r),
        ] {
            let e = Engine::new();
            let mut fuel = 100u64;
            let out = e
                .apply(&parse_strategy("prim").unwrap(), &read_term(&stuck).unwrap(), &mut fuel)
                .unwrap();
            assert_eq!(out, None, "should be stuck: {}", stuck);
        }
        // normal order: the field (e) is reduced in place afterwards
        let e = Engine::new();
        let mut fuel = 100u64;
        let out = e
            .apply(&parse_strategy("outermost(prim)").unwrap(), &read_term(&format!("(add@ {} a (@ {} b c))", r, r)).unwrap(), &mut fuel)
            .unwrap()
            .unwrap();
        assert_eq!(format!("{}", out), "(rec (a 3) (b (rec (c 2) (d x))) (e 2))");
    }

    #[test]
    fn record_keys_are_labels_not_calls() {
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "pop".into(),
            lhs: read_term("(pop ?x)").unwrap(),
            rhs: read_term("popped").unwrap(),
            conds: vec![],
        });
        let mut fuel = 100u64;
        let out = e
            .apply(&parse_strategy("outermost(prim + rules)").unwrap(), &read_term("(rec (pop (+ 1 2)) (q (pop 7)))").unwrap(), &mut fuel)
            .unwrap()
            .unwrap();
        // the key `pop` is a label; the VALUE (pop 7) is still a call
        assert_eq!(format!("{}", out), "(rec (pop 3) (q popped))");
        let out2 = e
            .apply(&parse_strategy("innermost(prim + rules)").unwrap(), &read_term("(rec (pop (+ 1 2)) (q (pop 7)))").unwrap(), &mut fuel)
            .unwrap()
            .unwrap();
        assert_eq!(format!("{}", out2), "(rec (pop 3) (q popped))");
    }

    #[test]
    fn head_index_preserves_source_order_with_wildcards() {
        // pinned rule, wildcard rule, pinned rule: the wildcard (index 1) must
        // be tried before the second pinned rule (index 2).
        let mut e = Engine::new();
        for (n, l, r) in [
            ("p1", "(f 1)", "one"),
            ("w", "(?h ?x)", "wild"),
            ("p2", "(f ?x)", "pinned"),
        ] {
            e.add_rule(Rule { name: n.into(), lhs: read_term(l).unwrap(), rhs: read_term(r).unwrap(), conds: vec![] });
        }
        let mut fuel = 100u64;
        let s = parse_strategy("rules").unwrap();
        let a = e.apply(&s, &read_term("(f 1)").unwrap(), &mut fuel).unwrap().unwrap();
        let b = e.apply(&s, &read_term("(f 2)").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{} {}", a, b), "one wild");
    }

    #[test]
    fn transitions_fire_only_by_name() {
        let mut e = Engine::new();
        e.add_transition(Rule {
            name: "tick".into(),
            lhs: read_term("(clock ?n)").unwrap(),
            rhs: read_term("(clock (+ ?n 1))").unwrap(),
            conds: vec![],
        });
        let mut fuel = 1000u64;
        // `rules` never sees a transition: normalizing leaves the clock alone.
        let a = e.apply(&parse_strategy("outermost(prim + rules)").unwrap(), &read_term("(clock 0)").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", a), "(clock 0)");
        // named, under control: exactly one tick per application.
        let b = e.apply(&parse_strategy("oncetd(tick) ; outermost(prim + rules)").unwrap(), &read_term("(clock 0)").unwrap(), &mut fuel).unwrap().unwrap();
        assert_eq!(format!("{}", b), "(clock 1)");
    }

    #[test]
    fn stats_count_rule_firings() {
        let mut e = peano_engine();
        e.enable_stats();
        let s = parse_strategy("innermost(add-zero + add-suc)").unwrap();
        let mut fuel = 1000u64;
        e.apply(&s, &read_term("(+ (S (S 0)) (S (S 0)))").unwrap(), &mut fuel).unwrap();
        let st = e.stats.as_ref().unwrap().borrow();
        assert_eq!(st.get("add-suc"), Some(&2));
        assert_eq!(st.get("add-zero"), Some(&1));
    }

    #[test]
    fn exact_rational_primitives() {
        let e = Engine::new();
        let s = parse_strategy("outermost(prim)").unwrap();
        let cases = [
            ("(+ 1/3 1/6)", "1/2"),
            ("(q/ 6 4)", "3/2"),
            ("(q/ 6 3)", "2"),
            ("(* 9223372036854775807 2)", "18446744073709551614"),
            ("(- (* 9223372036854775807 2) 9223372036854775807)", "9223372036854775807"),
            ("(< 1/3 0.5)", "(< 1/3 0.5)"),
            ("(< 1/3 1/2)", "true"),
            ("(= 2/4 1/2)", "true"),
            ("(max 1/3 1/4)", "1/3"),
            ("(/ 7 2)", "3"),
            ("(/ 7/2 2)", "(/ 7/2 2)"),
            ("(round-to 2/3 1000)", "667/1000"),
            ("(decimal 2/3 4)", "\"0.6667\""),
            ("(expt 3/2 3)", "27/8"),
            ("(floor -7/2)", "-4"),
            ("(num 6/4)", "3"),
            ("(den 6/4)", "2"),
            ("(str -1/3)", "\"-1/3\""),
            ("(add@ (rec (a 1/2)) a 1/2)", "(rec (a 1))"),
            ("(sum@ (rec (a 1/2) (b 1/3)))", "5/6"),
            ("(number? 1/2)", "true"),
            ("(number? x)", "false"),
        ];
        for (src, want) in cases {
            let mut fuel = 1000u64;
            let out = e.apply(&s, &read_term(src).unwrap(), &mut fuel).unwrap().unwrap();
            assert_eq!(format!("{}", out), want, "case {}", src);
        }
    }

    #[test]
    fn memo_preserves_normal_forms() {
        // A recursive definition with guards and sharing: the memoized
        // evaluator must reach the same normal form (with no more fuel).
        let mk = || {
            let mut e = Engine::new();
            for (name, l, r) in [
                ("if-t", "(if true ?t ?e)", "?t"),
                ("if-f", "(if false ?t ?e)", "?e"),
                ("fib", "(fib ?n)", "(if (< ?n 2) ?n (+ (fib (- ?n 1)) (fib (- ?n 2))))"),
                ("pair", "(both ?x)", "(list ?x ?x (fib 12))"),
            ] {
                e.add_rule(Rule { name: name.into(), lhs: read_term(l).unwrap(), rhs: read_term(r).unwrap(), conds: vec![] });
            }
            e
        };
        let s = parse_strategy("outermost(prim + rules)").unwrap();
        let t = read_term("(both (list (fib 10) (fib 11)))").unwrap();
        let plain = mk();
        let mut f1 = 10_000_000u64;
        let a = plain.apply(&s, &t, &mut f1).unwrap().unwrap();
        let mut memo = mk();
        memo.enable_memo();
        let mut f2 = 10_000_000u64;
        let b = memo.apply(&s, &t, &mut f2).unwrap().unwrap();
        assert_eq!(a, b);
        assert_eq!(format!("{}", a), "(list (list 55 89) (list 55 89) 144)");
        assert!(f2 >= f1, "memo must not use more fuel");
        assert!(memo.memo_stats().unwrap().1 > 0, "memo should have hits");
    }

    #[test]
    fn trace_is_observation_only() {
        // --trace prints steps; the normal form and the fuel spent must be
        // exactly those of an untraced run, and only `limit` steps are counted.
        let mk = || {
            let mut e = Engine::new();
            for (name, l, r) in [
                ("if-t", "(if true ?t ?e)", "?t"),
                ("if-f", "(if false ?t ?e)", "?e"),
                ("fib", "(fib ?n)", "(if (< ?n 2) ?n (+ (fib (- ?n 1)) (fib (- ?n 2))))"),
            ] {
                e.add_rule(Rule { name: name.into(), lhs: read_term(l).unwrap(), rhs: read_term(r).unwrap(), conds: vec![] });
            }
            e
        };
        let s = parse_strategy("outermost(prim + rules)").unwrap();
        let t = read_term("(fib 9)").unwrap();
        let plain = mk();
        let mut f1 = 1_000_000u64;
        let a = plain.apply(&s, &t, &mut f1).unwrap().unwrap();
        let mut traced = mk();
        traced.enable_trace(5);
        let mut f2 = 1_000_000u64;
        let b = traced.apply(&s, &t, &mut f2).unwrap().unwrap();
        assert_eq!(a, b);
        assert_eq!(f1, f2);
        assert_eq!(traced.trace_count(), Some((5, 5)));
    }

    #[test]
    fn fuel_exhaustion_errors() {
        let mut e = Engine::new();
        e.add_rule(Rule {
            name: "grow".into(),
            lhs: read_term("(n ?x)").unwrap(),
            rhs: read_term("(n (n ?x))").unwrap(),
            conds: vec![],
        });
        let s = parse_strategy("repeat(grow)").unwrap();
        let mut fuel = 50u64;
        let t = read_term("(n z)").unwrap();
        let res = e.apply(&s, &t, &mut fuel);
        assert!(res.is_err(), "expected out-of-fuel error");
    }
}
