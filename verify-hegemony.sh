#!/usr/bin/env bash
# Verifies the Hegemony economy study (HEGEMONY-ECONOMY.md): every program's
# assertions, the self-rewriting game (5 rounds = 5 rewrites, then a quine),
# and -- if python3 is available -- the independent Python re-derivation.
set -u
cd "$(dirname "$0")"
BIN=./target/release/palimpsest
[ -x "$BIN" ] || cargo build --release
export PALIMPSEST_LIB="$(pwd)/lib"
pass=0; fail=0
ok () { printf "  PASS  %s\n" "$1"; pass=$((pass+1)); }
bad () { printf "  FAIL  %s\n" "$1"; fail=$((fail+1)); }
run () { # file, expected substring
  local out; out="$("$BIN" "$1" 2>&1)"; local st=$?
  if [ $st -eq 0 ] && printf '%s' "$out" | grep -qF "$2"; then ok "$(basename "$1"): $2"; else bad "$(basename "$1") (exit $st)"; fi
}
# 1. the game as a self-rewriting program: 5 x WROTE, then FIXED POINT
t="$(mktemp /tmp/hgame.XXXX.pal)"; cp examples/hegemony-game.pal "$t"
st=""; for i in 1 2 3 4 5 6; do st="$st $("$BIN" "$t" 2>&1 | grep -oE 'WROTE|FIXED POINT|FAIL' | tr '\n' ' ')"; done
want=" WROTE  WROTE  WROTE  WROTE  WROTE  FIXED POINT "
[ "$st" = "$want" ] && ok "hegemony-game.pal: 5 rounds = 5 rewrites, then a quine" || bad "hegemony-game.pal rewrite sequence:$st"
out="$("$BIN" "$t" 2>&1)"
printf '%s' "$out" | grep -qF "money conserved holds, flow rows balanced holds, goods balanced holds, labor balanced holds" && ok "hegemony-game.pal: four conservation laws hold" || bad "hegemony-game.pal invariants"
printf '%s' "$out" | grep -qF "VP        Working Class 25   Capitalist Class 61" && ok "hegemony-game.pal: final score 25 : 61" || bad "hegemony-game.pal final score"
rm -f "$t"; rm -rf "$(dirname "$t")/.palimpsest" 2>/dev/null
# 2. the analyses (each asserts its theorems; a failed assert exits non-zero)
run examples/hegemony-loops.pal    "all edge signs confirmed by the model: true"
run examples/hegemony-regimes.pal  "asserts : 5 passed, 0 failed"
run examples/hegemony-debt.pal     "asserts : 3 passed, 0 failed"
run examples/hegemony-politics.pal "asserts : 3 passed, 0 failed"
run examples/hegemony-policy.pal   "asserts : 1 passed, 0 failed"
# 3. independent re-derivation
if command -v python3 >/dev/null; then
  if python3 crosscheck/hegemony_crosscheck.py "$BIN" >/tmp/hx.out 2>&1; then ok "crosscheck/hegemony_crosscheck.py: $(grep -c PASS /tmp/hx.out) checks agree"; else bad "python crosscheck (see /tmp/hx.out)"; fi
fi
echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
