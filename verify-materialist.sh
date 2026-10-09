#!/usr/bin/env bash
# Verifies the materialist-economy study (MATERIALIST-ECONOMY.md): every
# program's assertions, the self-rewriting economy (6 rewrites, then a quine),
# and -- if python3 is available -- the independent Python re-derivation,
# which regenerates every displayed table and compares it digit for digit.
set -u
cd "$(dirname "$0")"
BIN=./target/release/palimpsest
[ -x "$BIN" ] || cargo build --release
export PALIMPSEST_LIB="$(pwd)/lib"
OUT="$(mktemp -d /tmp/me-out.XXXX)"
pass=0; fail=0
ok () { printf "  PASS  %s\n" "$1"; pass=$((pass+1)); }
bad () { printf "  FAIL  %s\n" "$1"; fail=$((fail+1)); }
run () { # file, expected assertion summary
  local f="$1" n; n="$(basename "$f")"
  "$BIN" "$f" --dry-run > "$OUT/$n.out" 2>&1; local st=$?
  if [ $st -eq 0 ] && grep -qF "$2" "$OUT/$n.out"; then ok "$n: $2"; else bad "$n (exit $st)"; fi
}
# 1. the integrated economy as a self-rewriting program: 6 x WROTE, then FIXED POINT
t="$(mktemp -d /tmp/meco.XXXX)/e.pal"; sed 's#import "../lib/#import "#' examples/me-economy.pal > "$t"
st=""; for i in 1 2 3 4 5 6 7; do st="$st $("$BIN" "$t" 2>&1 | grep -oE 'WROTE|FIXED POINT|assert: FAIL' | tr '\n' ' ')"; done
want=" WROTE  WROTE  WROTE  WROTE  WROTE  WROTE  FIXED POINT "
[ "$st" = "$want" ] && ok "me-economy.pal: 6 rewrites of 10 periods, then a quine (invariants hold every run)" || bad "me-economy.pal rewrite sequence:$st"
rm -rf "$(dirname "$t")"
# 2. the analyses (each asserts its theorems; a failed assert exits non-zero)
run examples/me-value.pal        "asserts : 17 passed, 0 failed"
run examples/me-distribution.pal "asserts : 18 passed, 0 failed"
run examples/me-games.pal        "asserts : 20 passed, 0 failed"
run examples/me-regimes.pal      "asserts : 13 passed, 0 failed"
run examples/me-loops.pal        "asserts : 5 passed, 0 failed"
run examples/me-dialectics.pal   "asserts : 13 passed, 0 failed"
run examples/me-classical.pal    "asserts : 8 passed, 0 failed"
run examples/me-selectorate.pal  "asserts : 7 passed, 0 failed"
run examples/me-tour.pal         "asserts : 2 passed, 0 failed"
run examples/me-extremes.pal     "asserts : 6 passed, 0 failed"
run examples/me-evidence.pal     "asserts : 3 passed, 0 failed"
# 3. independent re-derivation (reuses the outputs captured above)
if command -v python3 >/dev/null; then
  if ME_OUTPUTS="$OUT" python3 crosscheck/materialist_crosscheck.py "$BIN" > "$OUT/crosscheck.out" 2>&1; then
    ok "crosscheck/materialist_crosscheck.py: $(grep -c '  PASS' "$OUT/crosscheck.out") checks agree"
  else
    bad "python crosscheck (see $OUT/crosscheck.out)"; grep FAIL -A3 "$OUT/crosscheck.out" | head -20
  fi
fi
echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ] && rm -rf "$OUT"
[ "$fail" -eq 0 ]
