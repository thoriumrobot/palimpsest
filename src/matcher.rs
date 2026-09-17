//! Matching and substitution.
//!
//! `match_term` performs first-order syntactic matching of a pattern against a
//! subject, producing `Bindings`. It supports:
//!   * term variables `?x`       (bind one subterm),
//!   * sequence variables `?xs...`(bind a run of subterms inside a list, with
//!     backtracking so multiple sequence variables in one list work),
//!   * non-linear patterns (a variable occurring twice must bind equal terms).
//! `subst` instantiates a right-hand side under a set of bindings, splicing any
//! sequence variables back into their surrounding list.

use crate::term::Term;
use std::collections::HashMap;

#[derive(Clone, Debug, PartialEq)]
pub enum Binding {
    One(Term),
    Seq(Vec<Term>),
}

pub type Bindings = HashMap<String, Binding>;

/// Try to match `pat` against `subj`, extending `b`. Returns the (possibly
/// extended) bindings on success, or `None` on failure. Purely functional:
/// callers rely on it not mutating their copy on failure.
pub fn match_term(pat: &Term, subj: &Term, b: Bindings) -> Option<Bindings> {
    // Term variable.
    if let Some(name) = pat.as_term_var() {
        return match b.get(name) {
            Some(Binding::One(prev)) => {
                if prev == subj {
                    Some(b)
                } else {
                    None
                }
            }
            Some(Binding::Seq(_)) => None, // used inconsistently
            None => {
                let mut b = b;
                b.insert(name.to_string(), Binding::One(subj.clone()));
                Some(b)
            }
        };
    }
    // A bare sequence variable outside a list is not meaningful.
    if pat.as_seq_var().is_some() {
        return None;
    }
    match (pat, subj) {
        (Term::List(ps), Term::List(ss)) => match_seq(ps, ss, b),
        (Term::Sym(a), Term::Sym(c)) if a == c => Some(b),
        (Term::Int(a), Term::Int(c)) if a == c => Some(b),
        (Term::Str(a), Term::Str(c)) if a == c => Some(b),
        _ => None,
    }
}

/// Match a list of patterns against a list of subjects, handling sequence
/// variables by backtracking over how many subjects each one consumes.
fn match_seq(ps: &[Term], ss: &[Term], b: Bindings) -> Option<Bindings> {
    if ps.is_empty() {
        return if ss.is_empty() { Some(b) } else { None };
    }
    let head = &ps[0];

    if let Some(name) = head.as_seq_var() {
        // If already bound, the next |v| subjects must equal it exactly.
        if let Some(binding) = b.get(name) {
            match binding {
                Binding::Seq(v) => {
                    let k = v.len();
                    if ss.len() >= k && ss[..k] == v[..] {
                        return match_seq(&ps[1..], &ss[k..], b);
                    }
                    return None;
                }
                Binding::One(_) => return None,
            }
        }
        // Otherwise try every split point 0..=len (greedy-ascending is fine for
        // completeness; the first successful split wins).
        for k in 0..=ss.len() {
            let mut b2 = b.clone();
            b2.insert(name.to_string(), Binding::Seq(ss[..k].to_vec()));
            if let Some(res) = match_seq(&ps[1..], &ss[k..], b2) {
                return Some(res);
            }
        }
        return None;
    }

    // Ordinary head pattern consumes exactly one subject.
    if ss.is_empty() {
        return None;
    }
    let b = match_term(head, &ss[0], b)?;
    match_seq(&ps[1..], &ss[1..], b)
}

/// A continuation invoked with each candidate binding as it is completed. It
/// returns `Ok(Some(bindings))` to accept (search stops) — possibly returning an
/// *augmented* set of bindings — or `Ok(None)` to reject and keep searching.
pub type Accept<'a> = dyn FnMut(Bindings) -> Result<Option<Bindings>, String> + 'a;

/// Match `pat` against `subj`, calling `accept` on every complete candidate
/// binding. This lets a rule's `where` guards drive backtracking: if a guard
/// rejects one decomposition of the sequence variables, the matcher tries the
/// next. Returns the first accepted (possibly augmented) binding.
pub fn match_where(
    pat: &Term,
    subj: &Term,
    accept: &mut Accept,
) -> Result<Option<Bindings>, String> {
    match_k(pat, subj, Bindings::new(), accept)
}

fn match_k(
    pat: &Term,
    subj: &Term,
    b: Bindings,
    k: &mut Accept,
) -> Result<Option<Bindings>, String> {
    if let Some(name) = pat.as_term_var() {
        return match b.get(name) {
            Some(Binding::One(prev)) => {
                if prev == subj {
                    k(b)
                } else {
                    Ok(None)
                }
            }
            Some(Binding::Seq(_)) => Ok(None),
            None => {
                let mut b = b;
                b.insert(name.to_string(), Binding::One(subj.clone()));
                k(b)
            }
        };
    }
    if pat.as_seq_var().is_some() {
        return Ok(None);
    }
    match (pat, subj) {
        (Term::List(ps), Term::List(ss)) => match_seq_k(ps, ss, b, k),
        (Term::Sym(a), Term::Sym(c)) if a == c => k(b),
        (Term::Int(a), Term::Int(c)) if a == c => k(b),
        (Term::Str(a), Term::Str(c)) if a == c => k(b),
        _ => Ok(None),
    }
}

fn match_seq_k(
    ps: &[Term],
    ss: &[Term],
    b: Bindings,
    k: &mut Accept,
) -> Result<Option<Bindings>, String> {
    if ps.is_empty() {
        return if ss.is_empty() { k(b) } else { Ok(None) };
    }
    let head = &ps[0];
    if let Some(name) = head.as_seq_var() {
        if let Some(binding) = b.get(name) {
            match binding {
                Binding::Seq(v) => {
                    let n = v.len();
                    if ss.len() >= n && ss[..n] == v[..] {
                        return match_seq_k(&ps[1..], &ss[n..], b, k);
                    }
                    return Ok(None);
                }
                Binding::One(_) => return Ok(None),
            }
        }
        for split in 0..=ss.len() {
            let mut b2 = b.clone();
            b2.insert(name.to_string(), Binding::Seq(ss[..split].to_vec()));
            if let Some(res) = match_seq_k(&ps[1..], &ss[split..], b2, k)? {
                return Ok(Some(res));
            }
        }
        return Ok(None);
    }
    if ss.is_empty() {
        return Ok(None);
    }
    let rest_ps = &ps[1..];
    let rest_ss = &ss[1..];
    match_k(head, &ss[0], b, &mut |b2| match_seq_k(rest_ps, rest_ss, b2, k))
}

/// Instantiate a right-hand side term under `b`.
pub fn subst(rhs: &Term, b: &Bindings) -> Result<Term, String> {
    if let Some(name) = rhs.as_term_var() {
        return match b.get(name) {
            Some(Binding::One(t)) => Ok(t.clone()),
            Some(Binding::Seq(_)) => {
                Err(format!("sequence variable ?{}... used in term position", name))
            }
            None => Err(format!("unbound variable ?{}", name)),
        };
    }
    if let Some(name) = rhs.as_seq_var() {
        // A sequence var only makes sense inside a list (handled below); at the
        // top level it is an error.
        return Err(format!("sequence variable ?{}... used outside a list", name));
    }
    match rhs {
        // `(verbatim X)`: return X exactly as written in the rule's own
        // source text, with NO substitution inside it at all — not even for
        // term variables this same rule's left-hand side happens to bind.
        // This is the one way a right-hand side can author brand-new
        // pattern-shaped data (symbols like `?x` / `?xs...` that nothing on
        // the left-hand side ever bound) instead of only ever passing
        // through data it already captured. Without it, a rule can only ever
        // reproduce a descriptive schema (a pattern containing `?`
        // variables) by receiving it as an argument bound elsewhere — it can
        // never mint one itself. `verbatim` is deliberately NOT named
        // `quote`: that symbol is already an ordinary (uninterpreted, by
        // convention) tag used throughout this codebase's canonical quine
        // idiom, `(app ?code (quote ?data)) => (app ?data (quote ?data))`,
        // where `?data` inside it MUST be substituted normally — hijacking
        // `quote` here would silently break every quine example in the repo.
        Term::List(xs) if xs.len() == 2 && matches!(&xs[0], Term::Sym(s) if s == "verbatim") => {
            Ok(xs[1].clone())
        }
        Term::List(xs) => {
            let mut out = Vec::new();
            for el in xs {
                if let Some(name) = el.as_seq_var() {
                    match b.get(name) {
                        Some(Binding::Seq(v)) => out.extend(v.iter().cloned()),
                        Some(Binding::One(_)) => {
                            return Err(format!(
                                "?{}... bound to a single term, expected a sequence",
                                name
                            ))
                        }
                        None => return Err(format!("unbound sequence variable ?{}...", name)),
                    }
                } else {
                    out.push(subst(el, b)?);
                }
            }
            Ok(Term::List(out))
        }
        other => Ok(other.clone()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::term::read_term;

    fn m(pat: &str, subj: &str) -> Option<Bindings> {
        match_term(&read_term(pat).unwrap(), &read_term(subj).unwrap(), Bindings::new())
    }

    #[test]
    fn simple() {
        assert!(m("(+ ?x 0)", "(+ 5 0)").is_some());
        assert!(m("(+ ?x 0)", "(+ 5 1)").is_none());
    }

    #[test]
    fn nonlinear() {
        assert!(m("(pair ?x ?x)", "(pair a a)").is_some());
        assert!(m("(pair ?x ?x)", "(pair a b)").is_none());
    }

    #[test]
    fn sequences() {
        let b = m("(list ?xs...)", "(list a b c)").unwrap();
        let out = subst(&read_term("(reversed ?xs...)").unwrap(), &b).unwrap();
        assert_eq!(format!("{}", out), "(reversed a b c)");
    }

    #[test]
    fn two_sequences() {
        // split (a b | c d) so that the literal 'X' separates them
        let b = m("(s ?front... X ?back...)", "(s a b X c d)").unwrap();
        let out = subst(&read_term("(swapped ?back... ?front...)").unwrap(), &b).unwrap();
        assert_eq!(format!("{}", out), "(swapped c d a b)");
    }

    #[test]
    fn verbatim_is_unsubstituted() {
        // A rule `(mint ?n) => (verbatim (family ?xs...))` may never bind
        // `?xs...` on its own left-hand side, yet its RHS must still be able
        // to produce `(family ?xs...)` literally, as fresh pattern data. Bind
        // only `?n`, and confirm `?xs...` inside `verbatim` passes through
        // completely untouched (indeed, unbound entirely — it does not even
        // need to appear in `b`).
        let b = m("(mint ?n)", "(mint 3)").unwrap();
        let out = subst(&read_term("(verbatim (family ?xs...))").unwrap(), &b).unwrap();
        assert_eq!(format!("{}", out), "(family ?xs...)");

        // `?n` IS bound here, but inside `verbatim` it is still left exactly
        // as written — verbatim suppresses substitution unconditionally, it
        // does not merely fill in gaps.
        let out2 = subst(&read_term("(verbatim (holds ?n))").unwrap(), &b).unwrap();
        assert_eq!(format!("{}", out2), "(holds ?n)");

        // Outside a `verbatim` wrapper, ordinary substitution is unaffected.
        let out3 = subst(&read_term("(holds ?n)").unwrap(), &b).unwrap();
        assert_eq!(format!("{}", out3), "(holds 3)");

        // The pre-existing quine idiom's `quote` is an ordinary, uninterpreted
        // tag, not this new special form — a 2-element list headed by `quote`
        // must NOT be caught by the `verbatim` special case, or every quine
        // example in the repository would silently stop reproducing itself.
        let bd = m("(app ?code (tag ?data))", "(app x (tag y))").unwrap();
        let outd = subst(&read_term("(app ?data (tag ?data))").unwrap(), &bd).unwrap();
        assert_eq!(format!("{}", outd), "(app y (tag y))");

        // Same check with the literal symbol `quote` itself, exactly as the
        // canonical quine rule `q` in examples/quine.pal uses it.
        let bq = m("(app ?code (quote ?data))", "(app quine (quote quine))").unwrap();
        let outq = subst(&read_term("(app ?data (quote ?data))").unwrap(), &bq).unwrap();
        assert_eq!(format!("{}", outq), "(app quine (quote quine))");
    }
}
