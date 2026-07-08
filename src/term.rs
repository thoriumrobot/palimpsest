//! Terms: the universal data model of Palimpsest.
//!
//! Everything the interpreter manipulates is a `Term` — an S-expression style
//! tree of symbols, integers, strings and lists. Rules, patterns and subjects
//! are all `Term`s. Pattern variables are ordinary symbols distinguished by a
//! sigil:
//!   * `?x`      -> a *term* variable, matches exactly one subterm.
//!   * `?xs...`  -> a *sequence* variable, matches zero-or-more subterms inside
//!                  a list (Refal's `e.` variables).
//! Any other symbol is a literal that must match verbatim.

use std::fmt;

#[derive(Clone, PartialEq, Eq, Debug)]
pub enum Term {
    Sym(String),
    Int(i64),
    Str(String),
    List(Vec<Term>),
}

impl Term {
    /// Is this symbol a term variable like `?x` (but not a sequence variable)?
    pub fn as_term_var(&self) -> Option<&str> {
        if let Term::Sym(s) = self {
            if s.starts_with('?') && !s.ends_with("...") {
                return Some(&s[1..]);
            }
        }
        None
    }

    /// Is this symbol a sequence variable like `?xs...`? Returns the bare name.
    pub fn as_seq_var(&self) -> Option<&str> {
        if let Term::Sym(s) = self {
            if s.starts_with('?') && s.ends_with("...") && s.len() > 4 {
                return Some(&s[1..s.len() - 3]);
            }
        }
        None
    }
}

/// Canonical renderer. This is the *inverse* of `read_term` for the subset of
/// terms the reader produces, which is what makes byte-identical self-rewriting
/// (the quine) possible: `read_term(render(t)) == t` and, for a term already in
/// canonical form, `render(read_term(s)) == s`.
impl fmt::Display for Term {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Term::Sym(s) => write!(f, "{}", s),
            Term::Int(n) => write!(f, "{}", n),
            Term::Str(s) => {
                write!(f, "\"")?;
                for c in s.chars() {
                    match c {
                        '"' => write!(f, "\\\"")?,
                        '\\' => write!(f, "\\\\")?,
                        '\n' => write!(f, "\\n")?,
                        _ => write!(f, "{}", c)?,
                    }
                }
                write!(f, "\"")
            }
            Term::List(xs) => {
                write!(f, "(")?;
                for (i, x) in xs.iter().enumerate() {
                    if i > 0 {
                        write!(f, " ")?;
                    }
                    write!(f, "{}", x)?;
                }
                write!(f, ")")
            }
        }
    }
}

/// Tokenizer for the S-expression surface syntax.
#[derive(Debug, PartialEq)]
enum Tok {
    Open,
    Close,
    Atom(String),
    StrLit(String),
}

fn lex(input: &str) -> Result<Vec<Tok>, String> {
    let mut toks = Vec::new();
    let mut chars = input.chars().peekable();
    while let Some(&c) = chars.peek() {
        match c {
            '(' => {
                toks.push(Tok::Open);
                chars.next();
            }
            ')' => {
                toks.push(Tok::Close);
                chars.next();
            }
            c if c.is_whitespace() => {
                chars.next();
            }
            '"' => {
                chars.next();
                let mut s = String::new();
                loop {
                    match chars.next() {
                        Some('\\') => match chars.next() {
                            Some('n') => s.push('\n'),
                            Some('"') => s.push('"'),
                            Some('\\') => s.push('\\'),
                            Some(other) => s.push(other),
                            None => return Err("unterminated escape in string".into()),
                        },
                        Some('"') => break,
                        Some(ch) => s.push(ch),
                        None => return Err("unterminated string literal".into()),
                    }
                }
                toks.push(Tok::StrLit(s));
            }
            _ => {
                let mut s = String::new();
                while let Some(&c) = chars.peek() {
                    if c.is_whitespace() || c == '(' || c == ')' || c == '"' {
                        break;
                    }
                    s.push(c);
                    chars.next();
                }
                toks.push(Tok::Atom(s));
            }
        }
    }
    Ok(toks)
}

fn atom_to_term(a: &str) -> Term {
    if let Ok(n) = a.parse::<i64>() {
        Term::Int(n)
    } else {
        Term::Sym(a.to_string())
    }
}

fn parse_from(toks: &[Tok], pos: &mut usize) -> Result<Term, String> {
    if *pos >= toks.len() {
        return Err("unexpected end of input while reading term".into());
    }
    match &toks[*pos] {
        Tok::Open => {
            *pos += 1;
            let mut items = Vec::new();
            loop {
                if *pos >= toks.len() {
                    return Err("unterminated list".into());
                }
                if toks[*pos] == Tok::Close {
                    *pos += 1;
                    break;
                }
                items.push(parse_from(toks, pos)?);
            }
            Ok(Term::List(items))
        }
        Tok::Close => Err("unexpected ')'".into()),
        Tok::Atom(a) => {
            let t = atom_to_term(a);
            *pos += 1;
            Ok(t)
        }
        Tok::StrLit(s) => {
            let t = Term::Str(s.clone());
            *pos += 1;
            Ok(t)
        }
    }
}

/// Read exactly one term from a string (must consume all of it).
pub fn read_term(input: &str) -> Result<Term, String> {
    let toks = lex(input)?;
    let mut pos = 0;
    let t = parse_from(&toks, &mut pos)?;
    if pos != toks.len() {
        return Err(format!(
            "trailing tokens after term (read up to position {}/{})",
            pos,
            toks.len()
        ));
    }
    Ok(t)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roundtrip() {
        let cases = [
            "(app d (quote d))",
            "(+ 1 (S 0))",
            "(block (loop a b c) (for x))",
            "()",
            "sym",
            "42",
        ];
        for c in cases {
            let t = read_term(c).unwrap();
            assert_eq!(format!("{}", t), c, "roundtrip failed for {}", c);
        }
    }

    #[test]
    fn vars() {
        assert_eq!(read_term("?x").unwrap().as_term_var(), Some("x"));
        assert_eq!(read_term("?xs...").unwrap().as_seq_var(), Some("xs"));
        assert!(read_term("?xs...").unwrap().as_term_var().is_none());
    }
}
