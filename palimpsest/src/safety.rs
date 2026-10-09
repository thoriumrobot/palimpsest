//! The safety layer: nothing here lets a program *compute* anything; it governs
//! how the results of rewriting are allowed to touch the filesystem.
//!
//!   * Capabilities  — a program may only write files its `#caps` header grants.
//!   * Atomic writes — write a temp file in the same directory, fsync, then
//!                     `rename` over the target, so a file is never half-written.
//!   * Ledger        — before every write the prior bytes are snapshotted
//!                     (content-addressed) and journaled, so any erasure is
//!                     recoverable (`palimpsest undo`). This is the "palimpsest".
//!   * Dry-run       — compute and diff, write nothing.
//!
//! NOTE ON PRODUCTION HARDENING: a production build would obtain the target via
//! a `cap-std` `Dir` capability (which structurally rejects `..`, absolute paths
//! and symlink escapes) and content-address snapshots with SHA-256. This
//! prototype implements the same *model* with the standard library and a compact
//! non-cryptographic hash (FNV-1a); the security argument is identical, only the
//! collision-resistance of the address changes.

use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

/// A single grant from the `#caps { rewrite: [...] }` header.
#[derive(Clone, Debug, PartialEq)]
pub enum Cap {
    /// May rewrite the running program's own file.
    Selff,
    /// May rewrite exactly this path.
    File(String),
}

#[derive(Clone, Debug, Default)]
pub struct Caps {
    pub rewrite: Vec<Cap>,
}

impl Caps {
    /// Decide whether writing `target` (already resolved to a path) is allowed,
    /// given the program's own path `self_path`.
    pub fn allows(&self, target: &Path, self_path: &Path) -> bool {
        for c in &self.rewrite {
            match c {
                Cap::Selff => {
                    if same_path(target, self_path) {
                        return true;
                    }
                }
                Cap::File(p) => {
                    if same_path(target, Path::new(p)) {
                        return true;
                    }
                }
            }
        }
        false
    }
}

fn same_path(a: &Path, b: &Path) -> bool {
    let ca = fs::canonicalize(a).unwrap_or_else(|_| a.to_path_buf());
    let cb = fs::canonicalize(b).unwrap_or_else(|_| b.to_path_buf());
    ca == cb
}

/// FNV-1a 64-bit, used as the content address in this prototype's ledger.
pub fn addr(bytes: &[u8]) -> String {
    let mut h: u64 = 0xcbf29ce484222325;
    for &b in bytes {
        h ^= b as u64;
        h = h.wrapping_mul(0x00000100000001B3);
    }
    format!("{:016x}", h)
}

pub struct Ledger {
    dir: PathBuf,
}

impl Ledger {
    /// Open (creating if needed) the ledger under `.palimpsest/ledger`, rooted
    /// next to the given anchor file.
    pub fn open(anchor: &Path) -> std::io::Result<Ledger> {
        let base = anchor.parent().unwrap_or_else(|| Path::new("."));
        let dir = base.join(".palimpsest").join("ledger");
        fs::create_dir_all(&dir)?;
        Ok(Ledger { dir })
    }

    fn snap_path(&self, address: &str) -> PathBuf {
        self.dir.join(format!("{}.snap", address))
    }

    fn journal_path(&self) -> PathBuf {
        self.dir.join("journal.log")
    }

    /// The most recent journal entry, as (status, target, prev_addr, new_addr).
    pub fn last_entry(&self) -> Option<(String, String, String, String)> {
        let text = fs::read_to_string(self.journal_path()).ok()?;
        let line = text.lines().filter(|l| !l.trim().is_empty()).last()?;
        let cols: Vec<&str> = line.split('\t').collect();
        if cols.len() == 4 {
            Some((
                cols[0].to_string(),
                cols[1].to_string(),
                cols[2].to_string(),
                cols[3].to_string(),
            ))
        } else {
            None
        }
    }

    /// Read the snapshot content stored at `address`, if present.
    pub fn read_snapshot(&self, address: &str) -> Option<String> {
        fs::read_to_string(self.snap_path(address)).ok()
    }

    /// Record a write in the ledger, snapshotting the previous content.
    pub fn record(
        &self,
        target: &Path,
        prev: Option<&str>,
        new_content: &str,
    ) -> std::io::Result<(String, String)> {
        let prev_addr = match prev {
            Some(p) => {
                let a = addr(p.as_bytes());
                let sp = self.snap_path(&a);
                if !sp.exists() {
                    fs::write(&sp, p)?;
                }
                a
            }
            None => "----------------".to_string(),
        };
        let new_addr = addr(new_content.as_bytes());
        // Also snapshot the new content so `undo` to any step is possible.
        let np = self.snap_path(&new_addr);
        if !np.exists() {
            fs::write(&np, new_content)?;
        }
        let mut j = fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(self.journal_path())?;
        let status = if Some(new_content) == prev { "unchanged" } else { "rewrite" };
        writeln!(
            j,
            "{}\t{}\t{}\t{}",
            status,
            target.display(),
            prev_addr,
            new_addr
        )?;
        Ok((prev_addr, new_addr))
    }
}

/// Result of a (possibly dry-run) transactional write.
pub struct WriteReport {
    pub changed: bool,
    pub dry_run: bool,
    pub prev_addr: String,
    pub new_addr: String,
}

/// Perform a transactional write of `new_content` to `target`:
/// capability-check -> snapshot previous -> atomic temp+rename (unless dry-run).
pub fn transactional_write(
    target: &Path,
    self_path: &Path,
    caps: &Caps,
    new_content: &str,
    dry_run: bool,
) -> Result<WriteReport, String> {
    if !caps.allows(target, self_path) {
        return Err(format!(
            "capability denied: program is not permitted to rewrite {}",
            target.display()
        ));
    }
    let prev = fs::read_to_string(target).ok();
    let changed = prev.as_deref() != Some(new_content);

    // A dry-run computes addresses for reporting but persists nothing: no
    // snapshot, no journal entry, no write.
    if dry_run {
        return Ok(WriteReport {
            changed,
            dry_run: true,
            prev_addr: prev.as_deref().map(|p| addr(p.as_bytes())).unwrap_or_else(|| "----------------".into()),
            new_addr: addr(new_content.as_bytes()),
        });
    }

    let ledger = Ledger::open(self_path).map_err(|e| format!("ledger error: {}", e))?;
    let (prev_addr, new_addr) = ledger
        .record(target, prev.as_deref(), new_content)
        .map_err(|e| format!("ledger record failed: {}", e))?;

    // Atomic write: temp file in the *same directory*, then rename over target.
    let dir = target.parent().unwrap_or_else(|| Path::new("."));
    let tmp = dir.join(format!(
        ".palimpsest.tmp.{}.{}",
        std::process::id(),
        new_addr
    ));
    {
        let mut f = fs::File::create(&tmp).map_err(|e| format!("temp create failed: {}", e))?;
        f.write_all(new_content.as_bytes())
            .map_err(|e| format!("temp write failed: {}", e))?;
        f.sync_all().ok(); // best-effort fsync; ignore on filesystems that lack it
    }
    fs::rename(&tmp, target).map_err(|e| {
        let _ = fs::remove_file(&tmp);
        format!("atomic rename failed: {}", e)
    })?;

    Ok(WriteReport {
        changed,
        dry_run: false,
        prev_addr,
        new_addr,
    })
}

/// Roll the most recent rewrite back to its previous snapshot. Restores the
/// target file to the content it had before the last journaled write.
pub fn undo_last(anchor: &Path) -> Result<String, String> {
    let ledger = Ledger::open(anchor).map_err(|e| format!("ledger error: {}", e))?;
    let (_status, target, prev_addr, _new_addr) = ledger
        .last_entry()
        .ok_or("nothing to undo: the ledger journal is empty")?;
    let prev = ledger
        .read_snapshot(&prev_addr)
        .ok_or_else(|| format!("previous snapshot {} not found", prev_addr))?;
    let target_path = PathBuf::from(&target);
    // Atomic restore.
    let dir = target_path.parent().unwrap_or_else(|| Path::new("."));
    let tmp = dir.join(format!(".palimpsest.undo.{}", std::process::id()));
    fs::write(&tmp, &prev).map_err(|e| format!("undo temp failed: {}", e))?;
    fs::rename(&tmp, &target_path).map_err(|e| format!("undo rename failed: {}", e))?;
    Ok(target)
}

/// A minimal unified-style line diff for dry-run reporting.
pub fn line_diff(old: &str, new: &str) -> String {
    if old == new {
        return "    (no change — already a fixed point)".to_string();
    }
    let o: Vec<&str> = old.lines().collect();
    let n: Vec<&str> = new.lines().collect();
    let mut out = String::new();
    let max = o.len().max(n.len());
    for i in 0..max {
        match (o.get(i), n.get(i)) {
            (Some(a), Some(b)) if a == b => {}
            (Some(a), Some(b)) => {
                out.push_str(&format!("  - {}\n  + {}\n", a, b));
            }
            (Some(a), None) => out.push_str(&format!("  - {}\n", a)),
            (None, Some(b)) => out.push_str(&format!("  + {}\n", b)),
            (None, None) => {}
        }
    }
    out
}
