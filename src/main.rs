//! Palimpsest — a safe self-rewriting term-rewriting language.
//!
//! Usage:
//!   palimpsest <program.pal> [--dry-run] [--fuel N]
//!
//! The interpreter loads the program, then executes its commands (`run`,
//! `show`, `display`, `rewrite`) in order. `rewrite self` / `rewrite file "..."`
//! go through the capability-checked, atomic, snapshotted transaction layer in
//! `safety`.

mod matcher;
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
        eprintln!("usage: palimpsest <program.pal> [--dry-run] [--fuel N]");
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
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--dry-run" => dry_run = true,
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

    match run(&path, dry_run, fuel_override) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("palimpsest: {}", e);
            ExitCode::FAILURE
        }
    }
}

fn run(path: &Path, dry_run: bool, fuel_override: Option<u64>) -> Result<(), String> {
    let mut prog = load_program(path)?;
    if let Some(f) = fuel_override {
        prog.fuel = f;
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
    for cmd in &prog.commands {
        match cmd {
            Command::Run(s) => exec_run(&prog, s, &mut fuel)?,
            Command::Show(t, s) => exec_show(&prog, t, s, &mut fuel)?,
            Command::Display(t, s) => exec_display(&prog, t, s, &mut fuel)?,
            Command::Rewrite { target, strat, strat_src } => {
                exec_rewrite(&prog, target, strat, strat_src, &mut fuel, dry_run)?
            }
        }
    }
    println!("\nfuel remaining: {}", fuel);
    Ok(())
}

fn exec_run(prog: &Program, s: &strategy::Strat, fuel: &mut u64) -> Result<(), String> {
    let subject = prog
        .main
        .clone()
        .ok_or("`run` requires a `main = ...` subject term")?;
    let out = prog
        .engine
        .apply(s, &subject, fuel)?
        .ok_or("strategy failed on the subject term")?;
    println!("run: {}  ==>  {}", subject, out);
    Ok(())
}

fn exec_show(prog: &Program, t: &Term, s: &strategy::Strat, fuel: &mut u64) -> Result<(), String> {
    let out = prog.engine.apply(s, t, fuel)?.ok_or("strategy failed")?;
    println!("show: {}  ==>  {}", t, out);
    Ok(())
}

/// Replace every bare symbol `main` in `t` with the program's `main` subject, so
/// a display/render term like `(chess main)` renders the actual subject.
fn subst_main(t: &Term, main: &Term) -> Term {
    match t {
        Term::Sym(s) if s == "main" => main.clone(),
        Term::List(xs) => Term::List(xs.iter().map(|x| subst_main(x, main)).collect()),
        other => other.clone(),
    }
}

/// `display` renders a term for a human: it normalizes the term (after resolving
/// `main`) and, when the result is a string, prints it verbatim with real line
/// breaks — so a rendered board or listing shows as itself, not an escaped
/// one-liner. Non-string results are printed in canonical form.
fn exec_display(prog: &Program, t: &Term, s: &strategy::Strat, fuel: &mut u64) -> Result<(), String> {
    let subject = match &prog.main {
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
) -> Result<(), String> {
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
    Ok(())
}

fn indent(s: &str) -> String {
    s.lines()
        .map(|l| format!("  {}\n", l))
        .collect::<String>()
}
