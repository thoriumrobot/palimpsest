//! Strategies: programmable control over *where* and *how often* rules fire.
//!
//! Rules say *what* may be rewritten; strategies say *how* to drive them. This
//! separation (from Stratego/ELAN) is what lets a confluent/terminating core be
//! combined with controlled, bounded traversal. Fuel is the universal
//! termination backstop: every successful rule application costs one unit, so no
//! program can loop forever — it runs out of fuel and the caller rolls back.

use crate::matcher::{match_term, match_where, subst, Binding, Bindings};
use crate::term::Term;
use std::collections::HashMap;
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

pub struct Engine {
    pub rules: Vec<Rule>,
    pub rule_index: HashMap<String, usize>,
    pub strategies: HashMap<String, StratDef>,
    /// Cached head key per rule (parallel to `rules`): `Some(sym)` when the rule's
    /// left-hand side can only match subjects with that head symbol, `None` when
    /// it may match anything (a variable head). Used to skip non-matching rules.
    rule_heads: Vec<Option<String>>,
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

impl Engine {
    pub fn new() -> Self {
        Engine {
            rules: Vec::new(),
            rule_index: HashMap::new(),
            strategies: HashMap::new(),
            rule_heads: Vec::new(),
        }
    }

    pub fn add_rule(&mut self, r: Rule) {
        self.rule_index.insert(r.name.clone(), self.rules.len());
        self.rule_heads.push(head_key(&r.lhs));
        self.rules.push(r);
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
            return match match_term(lhs, subject, Bindings::new()) {
                Some(b) => {
                    if *fuel == 0 {
                        return Err("out of fuel (rewrite step budget exhausted)".into());
                    }
                    *fuel -= 1;
                    Ok(Some(subst(&r.rhs, &b)?))
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
                Ok(Some(subst(&r.rhs, &b)?))
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
                new_subj.push(self.eval_cond(s, fuel, depth)?);
            } else {
                new_pat.push(p.clone());
                new_subj.push(s.clone());
            }
        }
        Ok((Some(Term::List(new_pat)), Some(Term::List(new_subj))))
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
        let ev = Strat::Repeat(Box::new(Strat::OnceTd(Box::new(Strat::Choice(
            Box::new(Strat::Prim),
            Box::new(Strat::AllRules),
        )))));
        Ok(self
            .apply_d(&ev, t, fuel, depth + 1, &env_empty())?
            .unwrap_or_else(|| t.clone()))
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
                let skey = head_key(t);
                for (i, r) in self.rules.iter().enumerate() {
                    // Skip rules that require a head symbol different from the
                    // subject's; a wildcard-headed rule (None) is always tried.
                    if let Some(h) = &self.rule_heads[i] {
                        if skey.as_deref() != Some(h.as_str()) {
                            continue;
                        }
                    }
                    if let Some(t2) = self.apply_rule(r, t, fuel, depth)? {
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
                for x in xs {
                    match self.apply_d(s, x, fuel, depth + 1, env)? {
                        Some(x2) => out.push(x2),
                        None => return Ok(None),
                    }
                }
                Ok(Some(Term::List(out)))
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
        if td {
            if let Some(t2) = self.apply_d(s, t, fuel, depth + 1, env)? {
                return Ok(Some(t2));
            }
        }
        if let Term::List(xs) = t {
            for i in 0..xs.len() {
                if let Some(ci) = self.once(s, &xs[i], fuel, depth + 1, td, env)? {
                    let mut v = xs.clone();
                    v[i] = ci;
                    return Ok(Some(Term::List(v)));
                }
            }
        }
        if !td {
            if let Some(t2) = self.apply_d(s, t, fuel, depth + 1, env)? {
                return Ok(Some(t2));
            }
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
            Term::List(xs) => {
                let mut out = Vec::with_capacity(xs.len());
                for x in xs {
                    out.push(self.innermost(s, x, fuel, depth + 1, env)?);
                }
                Term::List(out)
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

fn as_int(t: &Term) -> Option<i64> {
    if let Term::Int(n) = t {
        Some(*n)
    } else {
        None
    }
}

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
    // Unary primitives.
    if xs.len() == 2 {
        if let Term::Sym(op) = &xs[0] {
            match op.as_str() {
                "str" => {
                    // Render a symbol, integer, or string as a string literal.
                    return match &xs[1] {
                        Term::Sym(s) => Some(Term::Str(s.clone())),
                        Term::Int(n) => Some(Term::Str(n.to_string())),
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
                            Some(Term::List(v))
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
                "abs" => {
                    return match &xs[1] {
                        Term::Int(n) => Some(Term::Int(n.abs())),
                        _ => None,
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
    match op {
        "+" => Some(Term::Int(as_int(a)?.checked_add(as_int(b)?)?)),
        "-" => Some(Term::Int(as_int(a)?.checked_sub(as_int(b)?)?)),
        "*" => Some(Term::Int(as_int(a)?.checked_mul(as_int(b)?)?)),
        "/" => {
            let (x, y) = (as_int(a)?, as_int(b)?);
            if y == 0 {
                None
            } else {
                Some(Term::Int(x / y))
            }
        }
        "mod" => {
            let (x, y) = (as_int(a)?, as_int(b)?);
            if y == 0 {
                None
            } else {
                Some(Term::Int(x.rem_euclid(y)))
            }
        }
        "<" => Some(boolsym(as_int(a)? < as_int(b)?)),
        "<=" => Some(boolsym(as_int(a)? <= as_int(b)?)),
        ">" => Some(boolsym(as_int(a)? > as_int(b)?)),
        ">=" => Some(boolsym(as_int(a)? >= as_int(b)?)),
        // Equality on primitive literal values only (ints, strings, symbols).
        "=" | "<>" => {
            let both_prim = matches!(
                (a, b),
                (Term::Int(_), Term::Int(_))
                    | (Term::Str(_), Term::Str(_))
                    | (Term::Sym(_), Term::Sym(_))
            );
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
        "matches?" => Some(boolsym(match_term(a, b, Bindings::new()).is_some())),
        // Constructive counterpart: reify the witnessing substitution itself
        // (see `eval_match_witness` below) instead of just a boolean.
        "match-witness" => Some(eval_match_witness(a, b)),
        "str<" => match (a, b) {
            (Term::Str(x), Term::Str(y)) => Some(boolsym(x < y)),
            _ => None,
        },
        "min" => Some(Term::Int(as_int(a)?.min(as_int(b)?))),
        "max" => Some(Term::Int(as_int(a)?.max(as_int(b)?))),
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
    match match_term(a, b, Bindings::new()) {
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
                        Term::List(lst)
                    }
                };
                entries.push(Term::List(vec![
                    Term::Sym("entry".to_string()),
                    Term::Sym(name.clone()),
                    val,
                ]));
            }
            Term::List(vec![Term::Sym("some".to_string()), Term::List(entries)])
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
