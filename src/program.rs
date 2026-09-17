//! The program loader. A `.pal` file is a sequence of line-oriented items:
//!   #lang / #mode / #fuel / #caps   — directives
//!   rule NAME : LHS => RHS          — a rewrite rule
//!   strategy NAME = STRATEGY        — a named strategy
//!   main = TERM                     — the subject term to rewrite
//!   run STRATEGY                    — normalize `main`, print it
//!   show TERM with STRATEGY         — normalize a literal term, print it
//!   display TERM with STRATEGY      — normalize, then print for a human (a
//!                                     string result is shown verbatim; `main`
//!                                     in TERM resolves to the subject term)
//!   rewrite TARGET with STRATEGY    — transform a file (self or another)
//! Lines beginning with `//` are comments.

use crate::safety::{Cap, Caps};
use crate::strategy::{parse_strategy, Engine, Rule, Strat, StratDef, WhereClause};
use crate::term::{read_term, Term};
use std::collections::HashSet;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone)]
pub enum Target {
    Selff,
    File(String),
}

pub enum Command {
    Run(Strat),
    Show(Term, Strat),
    Display(Term, Strat),
    Rewrite { target: Target, strat: Strat, strat_src: String },
}

pub struct Program {
    pub mode: String,
    pub fuel: u64,
    pub caps: Caps,
    pub engine: Engine,
    pub main: Option<Term>,
    pub main_line: Option<usize>,
    pub commands: Vec<Command>,
    pub lines: Vec<String>,
    pub path: PathBuf,
}

/// Load a program and all of its (transitive) imports.
pub fn load_program(path: &Path) -> Result<Program, String> {
    let root_text = std::fs::read_to_string(path)
        .map_err(|e| format!("cannot read {}: {}", path.display(), e))?;
    let mut prog = Program {
        mode: "rewriting-as-running".into(),
        fuel: 100_000,
        caps: Caps::default(),
        engine: Engine::new(),
        main: None,
        main_line: None,
        commands: Vec::new(),
        lines: root_text.lines().map(|s| s.to_string()).collect(),
        path: path.to_path_buf(),
    };
    let mut visited = HashSet::new();
    load_file(path, &root_text, &mut prog, &mut visited, true)?;
    Ok(prog)
}

/// Parse one file's items into `prog`. Definitions (rules, strategies) are
/// merged from every file; but directives, `main`, commands and capabilities are
/// honored **only from the root program** — an imported library can neither run
/// commands nor grant itself capabilities.
fn load_file(
    path: &Path,
    text: &str,
    prog: &mut Program,
    visited: &mut HashSet<PathBuf>,
    is_root: bool,
) -> Result<(), String> {
    let canon = std::fs::canonicalize(path).unwrap_or_else(|_| path.to_path_buf());
    if !visited.insert(canon) {
        return Ok(()); // already loaded — idempotent, cycle-safe
    }

    // Coalesce physical lines into logical items so rules/strategies may span
    // multiple lines. An item continues while its parentheses are unbalanced,
    // while it ends in a continuation token (=> = <- : + ; , where), or while the
    // next line *starts* with a continuation marker (where / + / ; / ,).
    for (start_idx, item) in logical_items(text) {
        let line = item.trim();
        if let Some(rest) = line.strip_prefix("import ") {
            let spec = rest.trim().trim_matches('"');
            let resolved = resolve_import(spec, path)?;
            let sub = std::fs::read_to_string(&resolved)
                .map_err(|e| format!("cannot read import {}: {}", resolved.display(), e))?;
            load_file(&resolved, &sub, prog, visited, false)?;
            continue;
        }
        if let Some(rest) = line.strip_prefix('#') {
            if is_root {
                parse_directive(rest, prog)?;
            }
            continue;
        }
        if let Some(rest) = line.strip_prefix("rule ") {
            prog.engine.add_rule(parse_rule(rest)?);
        } else if let Some(rest) = line.strip_prefix("strategy ") {
            let (header, body) = split_top_level(rest, '=')
                .ok_or_else(|| format!("malformed strategy (no '='): {}", line))?;
            let (name, params) = parse_strategy_header(header.trim())?;
            prog.engine.strategies.insert(
                name,
                StratDef {
                    params,
                    body: parse_strategy(body.trim())?,
                },
            );
        } else if let Some(rest) = line.strip_prefix("main ") {
            if is_root {
                let body = rest
                    .trim_start()
                    .strip_prefix('=')
                    .ok_or_else(|| format!("malformed main (no '='): {}", line))?;
                prog.main = Some(read_term(body.trim())?);
                prog.main_line = Some(start_idx);
            }
        } else if let Some(rest) = line.strip_prefix("run ") {
            if is_root {
                prog.commands.push(Command::Run(parse_strategy(rest.trim())?));
            }
        } else if let Some(rest) = line.strip_prefix("show ") {
            if is_root {
                let (term_src, strat_src) = split_top_level_str(rest, " with ")
                    .ok_or_else(|| format!("malformed show (no 'with'): {}", line))?;
                prog.commands.push(Command::Show(
                    read_term(term_src.trim())?,
                    parse_strategy(strat_src.trim())?,
                ));
            }
        } else if let Some(rest) = line.strip_prefix("display ") {
            if is_root {
                let (term_src, strat_src) = split_top_level_str(rest, " with ")
                    .ok_or_else(|| format!("malformed display (no 'with'): {}", line))?;
                prog.commands.push(Command::Display(
                    read_term(term_src.trim())?,
                    parse_strategy(strat_src.trim())?,
                ));
            }
        } else if let Some(rest) = line.strip_prefix("rewrite ") {
            if is_root {
                let (tgt_src, strat_src) = split_top_level_str(rest, " with ")
                    .ok_or_else(|| format!("malformed rewrite (no 'with'): {}", line))?;
                prog.commands.push(Command::Rewrite {
                    target: parse_target(tgt_src.trim())?,
                    strat: parse_strategy(strat_src.trim())?,
                    strat_src: strat_src.trim().to_string(),
                });
            }
        } else {
            return Err(format!("unrecognized item in {}: {}", path.display(), line));
        }
    }
    Ok(())
}

/// Group physical lines into (start_line_index, text) logical items.
fn logical_items(text: &str) -> Vec<(usize, String)> {
    let mut items: Vec<(usize, String)> = Vec::new();
    let mut acc = String::new();
    let mut start = 0usize;
    for (idx, raw) in text.lines().enumerate() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with("//") {
            continue;
        }
        let cont_marker = starts_continuation(line);
        if !acc.is_empty() && !cont_marker && is_complete(&acc) {
            items.push((start, std::mem::take(&mut acc)));
        }
        if acc.is_empty() {
            start = idx;
            acc.push_str(line);
        } else {
            acc.push(' ');
            acc.push_str(line);
        }
    }
    if !acc.is_empty() {
        items.push((start, acc));
    }
    items
}

/// Does this line begin a continuation of the previous item?
fn starts_continuation(line: &str) -> bool {
    line.starts_with("where")
        || line.starts_with('+')
        || line.starts_with(';')
        || line.starts_with(',')
        || line.starts_with("=>")
}

/// Is an accumulated item syntactically complete (balanced, not dangling)?
fn is_complete(s: &str) -> bool {
    if paren_depth(s) != 0 {
        return false;
    }
    let t = s.trim_end();
    for tok in ["=>", "<-", "+", ";", ",", ":", "("] {
        if t.ends_with(tok) {
            return false;
        }
    }
    if t.ends_with('=') || t.ends_with(" where") {
        return false;
    }
    true
}

/// Net parenthesis depth outside of string literals.
fn paren_depth(s: &str) -> i32 {
    let mut depth = 0i32;
    let mut in_str = false;
    let mut esc = false;
    for c in s.chars() {
        if in_str {
            if esc {
                esc = false;
            } else if c == '\\' {
                esc = true;
            } else if c == '"' {
                in_str = false;
            }
            continue;
        }
        match c {
            '"' => in_str = true,
            '(' => depth += 1,
            ')' => depth -= 1,
            _ => {}
        }
    }
    depth
}

/// Parse a strategy header `NAME` or `NAME(p1, p2, ...)`.
fn parse_strategy_header(h: &str) -> Result<(String, Vec<String>), String> {
    if let Some(lp) = h.find('(') {
        let name = h[..lp].trim().to_string();
        let rp = h.rfind(')').ok_or("strategy header missing ')'")?;
        let params = h[lp + 1..rp]
            .split(',')
            .map(|p| p.trim().to_string())
            .filter(|p| !p.is_empty())
            .collect();
        Ok((name, params))
    } else {
        Ok((h.trim().to_string(), Vec::new()))
    }
}

/// Resolve an `import` spec relative to the importing file's directory, then to
/// `$PALIMPSEST_LIB`, then as a bare path.
fn resolve_import(spec: &str, importer: &Path) -> Result<PathBuf, String> {
    let base = importer.parent().unwrap_or_else(|| Path::new("."));
    let local = base.join(spec);
    if local.exists() {
        return Ok(local);
    }
    if let Ok(libdir) = std::env::var("PALIMPSEST_LIB") {
        let c = Path::new(&libdir).join(spec);
        if c.exists() {
            return Ok(c);
        }
    }
    let bare = PathBuf::from(spec);
    if bare.exists() {
        return Ok(bare);
    }
    Err(format!(
        "cannot resolve import \"{}\" (looked relative to {} and $PALIMPSEST_LIB)",
        spec,
        base.display()
    ))
}

fn parse_directive(rest: &str, prog: &mut Program) -> Result<(), String> {
    let rest = rest.trim();
    if let Some(m) = rest.strip_prefix("mode ") {
        prog.mode = m.trim().to_string();
    } else if let Some(f) = rest.strip_prefix("fuel ") {
        prog.fuel = f
            .trim()
            .parse::<u64>()
            .map_err(|_| format!("bad fuel value: {}", f))?;
    } else if let Some(c) = rest.strip_prefix("caps ") {
        prog.caps = parse_caps(c.trim())?;
    } else if rest.starts_with("lang") {
        // #lang palimpsest — acknowledged, no effect in this prototype.
    } else {
        return Err(format!("unknown directive #{}", rest));
    }
    Ok(())
}

fn parse_caps(s: &str) -> Result<Caps, String> {
    // Expect something like: { rewrite: [self, file "x"] }
    let inside = s
        .trim()
        .trim_start_matches('{')
        .trim_end_matches('}')
        .trim();
    let mut caps = Caps::default();
    if let Some(pos) = inside.find("rewrite:") {
        let after = &inside[pos + "rewrite:".len()..];
        let lb = after.find('[').ok_or("caps: expected '[' after rewrite:")?;
        let rb = after.find(']').ok_or("caps: expected ']'")?;
        let list = &after[lb + 1..rb];
        for item in list.split(',') {
            let item = item.trim();
            if item.is_empty() {
                continue;
            }
            if item == "self" {
                caps.rewrite.push(Cap::Selff);
            } else if let Some(f) = item.strip_prefix("file ") {
                let path = f.trim().trim_matches('"').to_string();
                caps.rewrite.push(Cap::File(path));
            } else {
                return Err(format!("unknown capability entry: {}", item));
            }
        }
    }
    Ok(caps)
}

fn parse_rule(rest: &str) -> Result<Rule, String> {
    // NAME : LHS => RHS [where CLAUSE (, CLAUSE)*]
    let (name, body) =
        split_top_level_str(rest, ":").ok_or_else(|| format!("rule missing ':' -> {}", rest))?;
    let (lhs_src, rhs_rest) =
        split_top_level_str(body, "=>").ok_or_else(|| format!("rule missing '=>' -> {}", rest))?;

    // Optional `where` at top level (outside parens/strings).
    let (rhs_src, conds) = match split_top_level_str(rhs_rest, " where ") {
        Some((rhs, clauses_src)) => (rhs, parse_where(clauses_src)?),
        None => (rhs_rest, Vec::new()),
    };

    Ok(Rule {
        name: name.trim().to_string(),
        lhs: read_term(lhs_src.trim())?,
        rhs: read_term(rhs_src.trim())?,
        conds,
    })
}

/// Parse comma-separated `where` clauses: `?v <- EXPR` (binding) or `EXPR` (guard).
fn parse_where(src: &str) -> Result<Vec<WhereClause>, String> {
    let mut out = Vec::new();
    for clause in split_top_level_commas(src) {
        let clause = clause.trim();
        if clause.is_empty() {
            continue;
        }
        if let Some((v, expr)) = split_top_level_str(clause, "<-") {
            let v = v.trim();
            let var = v
                .strip_prefix('?')
                .ok_or_else(|| format!("where-binding target must be a ?variable: {}", v))?;
            out.push(WhereClause::Bind(var.to_string(), read_term(expr.trim())?));
        } else {
            out.push(WhereClause::Guard(read_term(clause)?));
        }
    }
    Ok(out)
}

fn parse_target(s: &str) -> Result<Target, String> {
    if s == "self" {
        Ok(Target::Selff)
    } else if let Some(f) = s.strip_prefix("file ") {
        Ok(Target::File(f.trim().trim_matches('"').to_string()))
    } else {
        Err(format!("unknown target '{}'", s))
    }
}

/// Split on the first occurrence of `sep` that lies outside any parentheses or
/// string literal, returning the two halves.
fn split_top_level_str<'a>(s: &'a str, sep: &str) -> Option<(&'a str, &'a str)> {
    let bytes = s.as_bytes();
    let sepb = sep.as_bytes();
    let mut depth = 0i32;
    let mut in_str = false;
    let mut esc = false;
    let mut i = 0usize;
    while i < bytes.len() {
        let c = bytes[i] as char;
        if in_str {
            if esc {
                esc = false;
            } else if c == '\\' {
                esc = true;
            } else if c == '"' {
                in_str = false;
            }
            i += 1;
            continue;
        }
        match c {
            '"' => in_str = true,
            '(' => depth += 1,
            ')' => depth -= 1,
            _ => {
                if depth == 0 && s[i..].as_bytes().starts_with(sepb) {
                    return Some((&s[..i], &s[i + sep.len()..]));
                }
            }
        }
        i += 1;
    }
    None
}

/// Split on a single top-level char (used for `=` in strategy headers).
fn split_top_level(s: &str, sep: char) -> Option<(&str, &str)> {
    let mut buf = [0u8; 4];
    let seps = sep.encode_utf8(&mut buf);
    split_top_level_str(s, seps)
}

/// Split a string on top-level commas.
fn split_top_level_commas(s: &str) -> Vec<&str> {
    let mut parts = Vec::new();
    let mut rest = s;
    while let Some((head, tail)) = split_top_level_str(rest, ",") {
        parts.push(head);
        rest = tail;
    }
    parts.push(rest);
    parts
}

/// Find the `main = TERM` logical item in an arbitrary target file's text.
/// `TERM` may span multiple physical lines (the same "logical item" grouping
/// `logical_items` uses to parse the file in the first place — indentation,
/// wrapped lists and interleaved comments all work exactly as they do
/// anywhere else in a program). Returns the inclusive physical-line range
/// `[start_idx, end_idx]` the whole `main = ...` item occupies, so the
/// caller can splice out precisely that span, and the parsed term.
pub fn find_main(text: &str) -> Result<(usize, usize, Term), String> {
    fn is_main_item(acc: &str) -> bool {
        let acc = acc.trim_start();
        acc.strip_prefix("main")
            .map(|rest| rest.trim_start().starts_with('='))
            .unwrap_or(false)
    }
    fn parse_main(acc: &str) -> Result<Term, String> {
        let body = acc.trim_start().strip_prefix("main").unwrap();
        let eq = body.trim_start().strip_prefix('=').unwrap();
        read_term(eq.trim())
    }

    let mut acc = String::new();
    let mut start = 0usize;
    let mut last_idx = 0usize;
    for (idx, raw) in text.lines().enumerate() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with("//") {
            continue;
        }
        let cont_marker = starts_continuation(line);
        if !acc.is_empty() && !cont_marker && is_complete(&acc) {
            if is_main_item(&acc) {
                return Ok((start, last_idx, parse_main(&acc)?));
            }
            acc.clear();
        }
        if acc.is_empty() {
            start = idx;
            acc.push_str(line);
        } else {
            acc.push(' ');
            acc.push_str(line);
        }
        last_idx = idx;
    }
    if !acc.is_empty() && is_main_item(&acc) {
        return Ok((start, last_idx, parse_main(&acc)?));
    }
    Err("target file has no 'main = ...' subject to rewrite".into())
}

/// Rebuild file text with the (possibly multi-line) `main = ...` item —
/// physical lines `[start_idx, end_idx]` inclusive — replaced by a single
/// line holding the rewritten term. The result of a rewrite is always
/// written back on one line regardless of how many lines the input `main`
/// spanned: that is what keeps repeated self-rewrites (and the quine check)
/// well-defined, since `find_main` on the result must see exactly the same
/// span shape a human author would get by hand-writing a one-line `main`.
pub fn splice_main(text: &str, start_idx: usize, end_idx: usize, new_term: &Term) -> String {
    let lines: Vec<&str> = text.lines().collect();
    let mut out_lines: Vec<String> = Vec::with_capacity(lines.len());
    out_lines.extend(lines[..start_idx].iter().map(|s| s.to_string()));
    out_lines.push(format!("main = {}", new_term));
    if end_idx + 1 < lines.len() {
        out_lines.extend(lines[end_idx + 1..].iter().map(|s| s.to_string()));
    }
    let mut out = out_lines.join("\n");
    if text.ends_with('\n') {
        out.push('\n');
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn find_main_single_line() {
        // The pre-existing shape used throughout examples/: `main = ...`
        // entirely on one physical line. Must keep working unchanged.
        let text = "#lang palimpsest\nmain = (app quine (quote quine))\nrewrite self with solve\n";
        let (start, end, term) = find_main(text).unwrap();
        assert_eq!(start, 1);
        assert_eq!(end, 1);
        assert_eq!(format!("{}", term), "(app quine (quote quine))");
    }

    #[test]
    fn find_main_multi_line() {
        // A `main = (...)` item that wraps across several physical lines,
        // interleaved with whole-line comments, must be recognized as ONE
        // logical item spanning the whole physical range -- the same
        // grouping `logical_items` uses for the rest of the file.
        let text = "\
#lang palimpsest
main = (report
  // a comment in the middle changes nothing
  (a 1)
  (b 2))
rewrite self with solve
display main with solve
";
        let (start, end, term) = find_main(text).unwrap();
        // line 0 = #lang, line 1 = 'main = (report', ..., line 4 = '  (b 2))'
        assert_eq!(start, 1);
        assert_eq!(end, 4);
        assert_eq!(format!("{}", term), "(report (a 1) (b 2))");
    }

    #[test]
    fn splice_main_collapses_multi_line_span_to_one_line() {
        let text = "\
#lang palimpsest
main = (report
  (a 1)
  (b 2))
rewrite self with solve
";
        let (start, end, _) = find_main(text).unwrap();
        let new_term = read_term("(report 1 2)").unwrap();
        let out = splice_main(text, start, end, &new_term);
        assert_eq!(
            out,
            "#lang palimpsest\nmain = (report 1 2)\nrewrite self with solve\n"
        );
        // And the result is itself found as a single-line main, as required
        // for a second rewrite pass (and the quine fixed-point check) to
        // see the exact same span shape a hand-written one-liner would give.
        let (start2, end2, term2) = find_main(&out).unwrap();
        assert_eq!(start2, end2);
        assert_eq!(format!("{}", term2), "(report 1 2)");
    }

    #[test]
    fn find_main_does_not_confuse_maintainer_like_identifiers() {
        let text = "#lang palimpsest\nmaintainer = (someone)\nmain = (real)\n";
        let (start, end, term) = find_main(text).unwrap();
        assert_eq!(start, 2);
        assert_eq!(end, 2);
        assert_eq!(format!("{}", term), "(real)");
    }
}
