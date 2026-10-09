//! Palimpsest — a safe self-rewriting term-rewriting language.
//!
//! Usage:
//!   palimpsest <program.pal> [--dry-run] [--fuel N] [--stats] [--memo] [--trace N]
//!
//! `--trace N` prints the first N rewrite steps (`rule: redex => contractum`),
//! indented by the depth of guard / `where` / strict-argument evaluation.
//!
//! `--stats` prints a rewrite profile after the run: how many times each rule
//! (and the primitive evaluator, as `<prim>`) fired. Together with fuel this is
//! a cheap derivation certificate: which rules a result actually depended on.
//!
//! The interpreter loads the program, then executes its commands (`run`,
//! `show`, `display`, `rewrite`) in order. `rewrite self` / `rewrite file "..."`
//! go through the capability-checked, atomic, snapshotted transaction layer in
//! `safety`.

mod fxhash;
mod matcher;
mod num;
mod program;
mod safety;
mod strategy;
mod term;

use program::{find_main, load_program, splice_main, Command, Program, Target};
use safety::{line_diff, transactional_write};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use term::Term;

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: palimpsest <program.pal> [--dry-run] [--fuel N] [--stats] [--memo] [--trace N]");
        eprintln!("       palimpsest undo <anchor.pal>   # roll back the last rewrite");
        return ExitCode::from(2);
    }

    // Subcommand: undo the last journaled rewrite.
    if args[1] == "undo" {
        let anchor = match args.get(2) {
            Some(p) => PathBuf::from(p),
            None => {
                eprintln!("usage: palimpsest undo <anchor.pal>");
                return ExitCode::from(2);
            }
        };
        return match safety::undo_last(&anchor) {
            Ok(target) => {
                println!("undo: restored {} from its previous snapshot", target);
                ExitCode::SUCCESS
            }
            Err(e) => {
                eprintln!("palimpsest: {}", e);
                ExitCode::FAILURE
            }
        };
    }
    let mut path: Option<String> = None;
    let mut dry_run = false;
    let mut fuel_override: Option<u64> = None;
    let mut stats = false;
    let mut memo = false;
    let mut trace: Option<u64> = None;
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--dry-run" => dry_run = true,
            "--stats" => stats = true,
            "--memo" => memo = true,
            "--trace" => {
                i += 1;
                trace = args.get(i).and_then(|s| s.parse().ok());
            }
            "--fuel" => {
                i += 1;
                fuel_override = args.get(i).and_then(|s| s.parse().ok());
            }
            other => path = Some(other.to_string()),
        }
        i += 1;
    }
    let path = match path {
        Some(p) => PathBuf::from(p),
        None => {
            eprintln!("error: no program file given");
            return ExitCode::from(2);
        }
    };

    match run(&path, dry_run, fuel_override, stats, memo, trace) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("palimpsest: {}", e);
            ExitCode::FAILURE
        }
    }
}

fn run(path: &Path, dry_run: bool, fuel_override: Option<u64>, stats: bool, memo: bool, trace: Option<u64>) -> Result<(), String> {
    let mut prog = load_program(path)?;
    if let Some(n) = trace {
        prog.engine.enable_trace(n);
    }
    if memo {
        prog.engine.enable_memo();
    }
    if let Some(f) = fuel_override {
        prog.fuel = f;
    }
    if stats {
        prog.engine.enable_stats();
    }

    println!("== palimpsest ==");
    println!("program : {}", path.display());
    println!("mode    : {}", prog.mode);
    println!("fuel    : {}", prog.fuel);
    println!("caps    : rewrite {:?}", prog.caps.rewrite);
    if dry_run {
        println!("DRY-RUN : no files will be modified");
    }
    println!();

    let mut fuel = prog.fuel;
    let (mut passed, mut failed) = (0usize, 0usize);
    let mut main_now = prog.main.clone();
    let mut lets: Vec<(String, Term)> = Vec::new();
    for cmd in &prog.commands {
        match cmd {
            Command::Run(s) => exec_run(&prog, &main_now, s, &mut fuel)?,
            Command::Show(t, s) => exec_show(&prog, t, &subst_lets(t, &lets), s, &mut fuel)?,
            Command::Display(t, s) => exec_display(&prog, &main_now, &subst_lets(t, &lets), s, &mut fuel)?,
            Command::Let(name, t, s) => {
                let t = subst_lets(t, &lets);
                let subject = match &main_now {
                    Some(m) => subst_main(&t, m),
                    None => t,
                };
                let v = prog.engine.apply(s, &subject, &mut fuel)?.ok_or("let: strategy failed")?;
                println!("let: {} bound", name);
                lets.push((name.clone(), v));
            }
            Command::Assert(t, s) => {
                if exec_assert(&prog, &main_now, t, &subst_lets(t, &lets), s, &mut fuel)? {
                    passed += 1
                } else {
                    failed += 1
                }
            }
            Command::Rewrite { target, strat, strat_src } => {
                let new_main = exec_rewrite(&prog, target, strat, strat_src, &mut fuel, dry_run)?;
                if prog.rebind_main && matches!(target, Target::Selff) {
                    main_now = Some(new_main);
                }
            }
        }
    }
    println!("\nfuel remaining: {}", fuel);
    if passed + failed > 0 {
        println!("asserts : {} passed, {} failed", passed, failed);
    }
    if let Some((shown, limit)) = prog.engine.trace_count() {
        println!("trace   : {} step(s) shown (limit {})", shown, limit);
    }
    if let Some(st) = &prog.engine.stats {
        let st = st.borrow();
        let mut v: Vec<(&String, &u64)> = st.iter().collect();
        v.sort_by(|a, b| b.1.cmp(a.1).then(a.0.cmp(b.0)));
        let total: u64 = v.iter().map(|(_, n)| **n).sum();
        println!("\nrewrite profile ({} steps, {} distinct rules):", total, v.len());
        if let Some((n, hits)) = prog.engine.memo_stats() {
            println!("  memo: {} normal forms cached, {} hits; {} normalizations reused", n, hits, prog.engine.memo_nf_hits().unwrap_or(0));
        }
        for (name, n) in v {
            println!("  {:>10}  {}", n, name);
        }
    }
    if failed > 0 {
        return Err(format!("{} assertion(s) failed", failed));
    }
    Ok(())
}

/// `assert TERM with S`: normalize (with `main` resolved) and require `true`.
fn exec_assert(prog: &Program, main: &Option<Term>, t: &Term, t_eval: &Term, s: &strategy::Strat, fuel: &mut u64) -> Result<bool, String> {
    let subject = match main {
        Some(m) => subst_main(t_eval, m),
        None => t_eval.clone(),
    };
    let out = prog.engine.apply(s, &subject, fuel)?.ok_or("strategy failed")?;
    let ok = out == Term::Sym("true".to_string());
    if ok {
        println!("assert: PASS  {}", t);
    } else {
        println!("assert: FAIL  {}  ==>  {}", t, out);
    }
    Ok(ok)
}

fn exec_run(_prog: &Program, main: &Option<Term>, s: &strategy::Strat, fuel: &mut u64) -> Result<(), String> {
    let prog = _prog;
    let subject = main
        .clone()
        .ok_or("`run` requires a `main = ...` subject term")?;
    let out = prog
        .engine
        .apply(s, &subject, fuel)?
        .ok_or("strategy failed on the subject term")?;
    println!("run: {}  ==>  {}", subject, out);
    Ok(())
}

fn exec_show(prog: &Program, t: &Term, t_eval: &Term, s: &strategy::Strat, fuel: &mut u64) -> Result<(), String> {
    let out = prog.engine.apply(s, t_eval, fuel)?.ok_or("strategy failed")?;
    println!("show: {}  ==>  {}", t, out);
    Ok(())
}

/// Replace every symbol bound by an earlier `let $NAME = ...` with its value.
fn subst_lets(t: &Term, lets: &[(String, Term)]) -> Term {
    if lets.is_empty() {
        return t.clone();
    }
    match t {
        Term::Sym(s) if s.starts_with('$') => match lets.iter().rev().find(|(n, _)| n == s) {
            Some((_, v)) => v.clone(),
            None => t.clone(),
        },
        Term::List(xs) => Term::list(xs.iter().map(|x| subst_lets(x, lets)).collect()),
        other => other.clone(),
    }
}

/// Replace every bare symbol `main` in `t` with the program's `main` subject, so
/// a display/render term like `(chess main)` renders the actual subject.
fn subst_main(t: &Term, main: &Term) -> Term {
    match t {
        Term::Sym(s) if s == "main" => main.clone(),
        Term::List(xs) => Term::list(xs.iter().map(|x| subst_main(x, main)).collect()),
        other => other.clone(),
    }
}

/// `display` renders a term for a human: it normalizes the term (after resolving
/// `main`) and, when the result is a string, prints it verbatim with real line
/// breaks — so a rendered board or listing shows as itself, not an escaped
/// one-liner. Non-string results are printed in canonical form.
fn exec_display(prog: &Program, main: &Option<Term>, t: &Term, s: &strategy::Strat, fuel: &mut u64) -> Result<(), String> {
    let subject = match main {
        Some(m) => subst_main(t, m),
        None => t.clone(),
    };
    let out = prog.engine.apply(s, &subject, fuel)?.ok_or("strategy failed")?;
    match out {
        Term::Str(text) => println!("display:\n{}", text),
        other => println!("display: {}", other),
    }
    Ok(())
}

fn exec_rewrite(
    prog: &Program,
    target: &Target,
    strat: &strategy::Strat,
    strat_src: &str,
    fuel: &mut u64,
    dry_run: bool,
) -> Result<Term, String> {
    // Resolve the target path and load its text + main term.
    let target_path: PathBuf = match target {
        Target::Selff => prog.path.clone(),
        Target::File(f) => PathBuf::from(f),
    };
    let target_text = fs::read_to_string(&target_path)
        .map_err(|e| format!("cannot read target {}: {}", target_path.display(), e))?;
    let (main_start, main_end, main_term) = find_main(&target_text)?;

    // Rewrite the subject term.
    let new_term = prog
        .engine
        .apply(strat, &main_term, fuel)?
        .ok_or("rewrite strategy failed on target subject")?;
    let new_text = splice_main(&target_text, main_start, main_end, &new_term);

    let label = match target {
        Target::Selff => "self".to_string(),
        Target::File(f) => format!("file \"{}\"", f),
    };
    println!("rewrite {} with {}", label, strat_src);
    println!("  subject : {}", main_term);
    println!("  result  : {}", new_term);

    if dry_run {
        println!("  diff    :");
        print!("{}", indent(&line_diff(&target_text, &new_text)));
    }

    let report = transactional_write(&target_path, &prog.path, &prog.caps, &new_text, dry_run)?;

    if report.dry_run {
        println!(
            "  status  : DRY-RUN ({}), snapshot {} -> {}",
            if report.changed { "would change" } else { "fixed point" },
            report.prev_addr,
            report.new_addr
        );
    } else if report.changed {
        println!(
            "  status  : WROTE (atomic rename), snapshot {} -> {}",
            report.prev_addr, report.new_addr
        );
    } else {
        println!(
            "  status  : FIXED POINT — file reproduced byte-identically ({}). This is a quine.",
            report.new_addr
        );
    }
    Ok(new_term)
}

fn indent(s: &str) -> String {
    s.lines()
        .map(|l| format!("  {}\n", l))
        .collect::<String>()
}
