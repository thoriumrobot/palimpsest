#!/usr/bin/env python3
"""Parity test: the Python port (web/palimpsest.py) against the Rust binary.

Runs every program given (default: examples/*.pal and puzzles/solutions/*.pal)
under both interpreters with --dry-run and the same extra flags, and requires
identical stdout, stderr and exit status -- fuel counts included.

    python3 web/test_parity.py                      # all programs, 300 s limit each
    python3 web/test_parity.py --timeout 60 examples/quine.pal
    python3 web/test_parity.py --flags "--memo --stats" examples/me-tour.pal

Programs whose Python run exceeds the time limit are reported as SLOW, not as
failures. Exit status 0 iff no program disagrees.
"""
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUST = os.path.join(ROOT, "target", "release", "palimpsest")
PY = [sys.executable, os.path.join(ROOT, "web", "palimpsest.py")]


def run(cmd, timeout):
    env = dict(os.environ, PALIMPSEST_LIB=os.path.join(ROOT, "lib"))
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, env=env)
        return p.returncode, p.stdout, p.stderr, time.time() - t0
    except subprocess.TimeoutExpired:
        return None, "", "", time.time() - t0


def main():
    args = sys.argv[1:]
    timeout = 300.0
    flags = []
    progs = []
    i = 0
    while i < len(args):
        if args[i] == "--timeout":
            timeout = float(args[i + 1])
            i += 2
        elif args[i] == "--flags":
            flags = args[i + 1].split()
            i += 2
        else:
            progs.append(args[i])
            i += 1
    if not progs:
        progs = sorted(glob.glob("examples/*.pal", root_dir=ROOT)) + \
            sorted(glob.glob("puzzles/solutions/*.pal", root_dir=ROOT))
    ok = bad = slow = 0
    for p in progs:
        rc_r, out_r, err_r, t_r = run([RUST, p, "--dry-run"] + flags, None)
        rc_p, out_p, err_p, t_p = run(PY + [p, "--dry-run"] + flags, timeout)
        if rc_p is None:
            slow += 1
            print("  SLOW  %-45s rust %6.2fs, python > %.0fs" % (p, t_r, timeout), flush=True)
            continue
        same = (rc_r, out_r, err_r) == (rc_p, out_p, err_p)
        if same:
            ok += 1
            print("  PASS  %-45s rust %6.2fs  python %7.2fs  (x%.0f)" % (p, t_r, t_p, t_p / max(t_r, 1e-3)), flush=True)
        else:
            bad += 1
            print("  FAIL  %-45s exit %s vs %s" % (p, rc_r, rc_p), flush=True)
            ra, pa = (out_r + err_r).splitlines(), (out_p + err_p).splitlines()
            for k in range(max(len(ra), len(pa))):
                a = ra[k] if k < len(ra) else "<none>"
                b = pa[k] if k < len(pa) else "<none>"
                if a != b:
                    print("        line %d\n          rust  : %s\n          python: %s" % (k + 1, a[:200], b[:200]))
                    break
    print("-" * 60)
    print("  %d identical, %d different, %d slow (over %.0f s)" % (ok, bad, slow, timeout))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
