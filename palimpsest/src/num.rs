//! Exact numbers: arbitrary-precision integers and rationals.
//!
//! Palimpsest's original number type is `Term::Int(i64)`, and every existing
//! program keeps running on it unchanged. This module adds `Term::Num`, an
//! exact rational of unbounded size, under one invariant that keeps equality
//! structural and printing canonical:
//!
//!   A number whose value is an integer that fits in an i64 is ALWAYS
//!   `Term::Int`; `Term::Num` holds only non-integers and integers outside the
//!   i64 range. (`from_rat` is the single constructor that enforces this.)
//!
//! So `(q/ 6 3)` is the same term as `2`, and two numbers are equal as terms
//! exactly when they are equal as numbers. The surface syntax is `n/d` for a
//! rational (`-3/4`, `1/3`) and plain digits for an integer of any size; the
//! printer emits the same forms, so `read(print(t)) == t` still holds and
//! self-rewriting programs that carry exact rationals in their state still
//! become byte-identical quines.
//!
//! What changed for old programs: integer `+ - *` that used to OVERFLOW used to
//! leave the term stuck; they now produce the exact big-integer result. No
//! program in the repository relied on a stuck overflow (all suites keep their
//! exact fuel fingerprints). `/` and `mod` are still integer operations; exact
//! division is the new primitive `q/`.

use crate::term::Term;
use num_bigint::BigInt;
use num_integer::Integer;
use num_rational::BigRational;
use num_traits::{One, Signed, ToPrimitive, Zero};
use std::cmp::Ordering;
use std::rc::Rc;

/// The value of a numeric term as an exact rational.
pub fn to_rat(t: &Term) -> Option<BigRational> {
    match t {
        Term::Int(n) => Some(BigRational::from_integer(BigInt::from(*n))),
        Term::Num(q) => Some((**q).clone()),
        _ => None,
    }
}

/// The canonical term for a rational (see the module invariant).
pub fn from_rat(q: BigRational) -> Term {
    if q.is_integer() {
        if let Some(n) = q.numer().to_i64() {
            return Term::Int(n);
        }
    }
    Term::Num(Rc::new(q))
}

pub fn is_num(t: &Term) -> bool {
    matches!(t, Term::Int(_) | Term::Num(_))
}

/// An integer-valued numeric term as a BigInt (None for non-integers).
fn to_bigint(t: &Term) -> Option<BigInt> {
    match t {
        Term::Int(n) => Some(BigInt::from(*n)),
        Term::Num(q) if q.is_integer() => Some(q.numer().clone()),
        _ => None,
    }
}

/// Read a numeric literal: an i64, a big integer, or `n/d` (d > 0, unsigned).
/// Anything else is not a number (and is read as a symbol by the caller).
pub fn parse_num(a: &str) -> Option<Term> {
    if let Ok(n) = a.parse::<i64>() {
        return Some(Term::Int(n));
    }
    fn is_int_lit(s: &str) -> bool {
        let d = s.strip_prefix('-').unwrap_or(s);
        !d.is_empty() && d.bytes().all(|c| c.is_ascii_digit())
    }
    if let Some((n, d)) = a.split_once('/') {
        if is_int_lit(n) && !d.is_empty() && d.bytes().all(|c| c.is_ascii_digit()) {
            let nn: BigInt = n.parse().ok()?;
            let dd: BigInt = d.parse().ok()?;
            if dd.is_zero() {
                return None;
            }
            return Some(from_rat(BigRational::new(nn, dd)));
        }
        return None;
    }
    if is_int_lit(a) {
        let nn: BigInt = a.parse().ok()?;
        return Some(from_rat(BigRational::from_integer(nn)));
    }
    None
}

/// Canonical text of a `Term::Num`.
pub fn fmt_rat(q: &BigRational) -> String {
    if q.is_integer() {
        format!("{}", q.numer())
    } else {
        format!("{}/{}", q.numer(), q.denom())
    }
}

/// Binary arithmetic: an i64 fast path, falling back to exact rationals on
/// overflow or when either operand is already a `Num`.
pub fn bin(a: &Term, b: &Term, fi: fn(i64, i64) -> Option<i64>, fq: fn(BigRational, BigRational) -> BigRational) -> Option<Term> {
    if let (Term::Int(x), Term::Int(y)) = (a, b) {
        if let Some(r) = fi(*x, *y) {
            return Some(Term::Int(r));
        }
    }
    let (x, y) = (to_rat(a)?, to_rat(b)?);
    Some(from_rat(fq(x, y)))
}

pub fn add(a: &Term, b: &Term) -> Option<Term> {
    bin(a, b, |x, y| x.checked_add(y), |x, y| x + y)
}
pub fn sub(a: &Term, b: &Term) -> Option<Term> {
    bin(a, b, |x, y| x.checked_sub(y), |x, y| x - y)
}
pub fn mul(a: &Term, b: &Term) -> Option<Term> {
    bin(a, b, |x, y| x.checked_mul(y), |x, y| x * y)
}

pub fn cmp(a: &Term, b: &Term) -> Option<Ordering> {
    if let (Term::Int(x), Term::Int(y)) = (a, b) {
        return Some(x.cmp(y));
    }
    Some(to_rat(a)?.cmp(&to_rat(b)?))
}

/// Integer division truncating toward zero (the original `/`), on integers of
/// any size. Does not fire on non-integers or a zero divisor.
pub fn idiv(a: &Term, b: &Term) -> Option<Term> {
    if let (Term::Int(x), Term::Int(y)) = (a, b) {
        if *y == 0 {
            return None;
        }
        if let Some(r) = x.checked_div(*y) {
            return Some(Term::Int(r));
        }
    }
    let (x, y) = (to_bigint(a)?, to_bigint(b)?);
    if y.is_zero() {
        return None;
    }
    Some(from_rat(BigRational::from_integer(x / y)))
}

/// Euclidean remainder (always >= 0), as the original `mod`.
pub fn imod(a: &Term, b: &Term) -> Option<Term> {
    if let (Term::Int(x), Term::Int(y)) = (a, b) {
        if *y == 0 {
            return None;
        }
        if let Some(r) = x.checked_rem_euclid(*y) {
            return Some(Term::Int(r));
        }
    }
    let (x, y) = (to_bigint(a)?, to_bigint(b)?);
    if y.is_zero() {
        return None;
    }
    Some(from_rat(BigRational::from_integer(x.mod_floor(&y.abs()))))
}

/// Exact division `q/`.
pub fn qdiv(a: &Term, b: &Term) -> Option<Term> {
    let (x, y) = (to_rat(a)?, to_rat(b)?);
    if y.is_zero() {
        return None;
    }
    Some(from_rat(x / y))
}

pub fn abs(a: &Term) -> Option<Term> {
    match a {
        Term::Int(n) => match n.checked_abs() {
            Some(m) => Some(Term::Int(m)),
            None => Some(from_rat(to_rat(a)?.abs())),
        },
        Term::Num(q) => Some(from_rat(q.abs())),
        _ => None,
    }
}

pub fn numer(a: &Term) -> Option<Term> {
    let q = to_rat(a)?;
    Some(from_rat(BigRational::from_integer(q.numer().clone())))
}
pub fn denom(a: &Term) -> Option<Term> {
    let q = to_rat(a)?;
    Some(from_rat(BigRational::from_integer(q.denom().clone())))
}
pub fn floor(a: &Term) -> Option<Term> {
    Some(from_rat(to_rat(a)?.floor()))
}
pub fn ceil(a: &Term) -> Option<Term> {
    Some(from_rat(to_rat(a)?.ceil()))
}

/// `(round-to X K)`: the multiple of 1/K nearest to X, ties rounded up
/// (toward +infinity): floor(X*K + 1/2) / K. K must be a positive integer.
/// This is the explicit, deterministic rounding a fixed-precision simulation
/// uses to keep exact denominators bounded.
pub fn round_to(a: &Term, k: &Term) -> Option<Term> {
    let x = to_rat(a)?;
    let k = to_bigint(k)?;
    if !k.is_positive() {
        return None;
    }
    let kq = BigRational::from_integer(k.clone());
    let half = BigRational::new(BigInt::one(), BigInt::from(2));
    let n = (x * &kq + half).floor();
    Some(from_rat(n / kq))
}

/// `(expt X K)`: X to an integer power K (K < 0 allowed for X != 0).
pub fn expt(a: &Term, k: &Term) -> Option<Term> {
    let x = to_rat(a)?;
    let k = to_bigint(k)?.to_i64()?;
    if k.unsigned_abs() > 100_000 {
        return None;
    }
    if k < 0 && x.is_zero() {
        return None;
    }
    let mut r = BigRational::one();
    let mut base = if k < 0 { x.recip() } else { x };
    let mut e = k.unsigned_abs();
    while e > 0 {
        if e & 1 == 1 {
            r = &r * &base;
        }
        base = &base * &base;
        e >>= 1;
    }
    Some(from_rat(r))
}

/// `(isqrt N)`: floor of the square root of a non-negative integer.
pub fn isqrt(a: &Term) -> Option<Term> {
    let n = to_bigint(a)?;
    if n.is_negative() {
        return None;
    }
    Some(from_rat(BigRational::from_integer(n.sqrt())))
}

/// `(decimal X D)`: X as a decimal string with exactly D digits after the point,
/// rounded half away from zero. For display only; the value stays exact.
pub fn dec(a: &Term, d: &Term) -> Option<Term> {
    let x = to_rat(a)?;
    let d = to_bigint(d)?.to_u32()?;
    if d > 60 {
        return None;
    }
    let scale = BigInt::from(10).pow(d);
    let neg = x.is_negative();
    let ax = x.abs() * BigRational::from_integer(scale.clone());
    let half = BigRational::new(BigInt::one(), BigInt::from(2));
    let n = (ax + half).floor().to_integer();
    let (ip, fp) = n.div_rem(&scale);
    let mut s = String::new();
    if neg && !n.is_zero() {
        s.push('-');
    }
    s.push_str(&ip.to_string());
    if d > 0 {
        let f = fp.to_string();
        s.push('.');
        for _ in f.len()..(d as usize) {
            s.push('0');
        }
        s.push_str(&f);
    }
    Some(Term::Str(s))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::term::read_term;

    fn t(s: &str) -> Term {
        read_term(s).unwrap()
    }

    #[test]
    fn canonical_forms_and_roundtrip() {
        for s in ["1/3", "-3/4", "123456789012345678901234567890", "-98765432109876543210/7", "0", "-5"] {
            assert_eq!(format!("{}", t(s)), s, "roundtrip {}", s);
        }
        assert_eq!(t("6/3"), Term::Int(2));
        assert_eq!(t("4/6"), t("2/3"));
        assert!(matches!(t("1/0"), Term::Sym(_)));
        assert!(matches!(t("a/b"), Term::Sym(_)));
        assert!(matches!(t("-/3"), Term::Sym(_)));
    }

    #[test]
    fn overflow_promotes_and_demotes() {
        let big = mul(&Term::Int(i64::MAX), &Term::Int(4)).unwrap();
        assert!(matches!(big, Term::Num(_)));
        let back = idiv(&big, &Term::Int(4)).unwrap();
        assert_eq!(back, Term::Int(i64::MAX));
        assert_eq!(add(&t("1/2"), &t("1/2")).unwrap(), Term::Int(1));
    }

    #[test]
    fn rounding_and_display() {
        assert_eq!(round_to(&t("2/3"), &Term::Int(100)).unwrap(), t("67/100"));
        assert_eq!(round_to(&t("-1/2"), &Term::Int(1)).unwrap(), Term::Int(0));
        assert_eq!(dec(&t("1102/1500"), &Term::Int(3)).unwrap(), Term::Str("0.735".into()));
        assert_eq!(dec(&t("-1/8"), &Term::Int(2)).unwrap(), Term::Str("-0.13".into()));
        assert_eq!(dec(&Term::Int(7), &Term::Int(0)).unwrap(), Term::Str("7".into()));
        assert_eq!(expt(&t("2/3"), &Term::Int(-2)).unwrap(), t("9/4"));
        assert_eq!(isqrt(&Term::Int(99)).unwrap(), Term::Int(9));
        assert_eq!(imod(&Term::Int(-7), &Term::Int(3)).unwrap(), Term::Int(2));
        assert_eq!(floor(&t("-1/2")).unwrap(), Term::Int(-1));
        assert_eq!(ceil(&t("-1/2")).unwrap(), Term::Int(0));
    }
}
