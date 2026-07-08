#!/usr/bin/env bash
# Verifies the mind<->body loop environments: each must reach the expected
# attractor, render its trajectory via `display`, and reproduce itself as a quine.
set -u
BIN=./target/release/palimpsest
export PALIMPSEST_LIB="$(pwd)/lib"
pass=0; fail=0
check () { # check file "kind-substring" "detail-substring(optional)"
  local f="$1" kind="$2" detail="${3:-}"
  local t; t="$(mktemp /tmp/mb.XXXX.pal)"; cp "$f" "$t"
  local out ok st2
  out="$("$BIN" "$t" 2>&1)"
  st2=$("$BIN" "$t" 2>&1 | grep -oE "FIXED POINT")
  ok=1
  printf '%s' "$out" | grep -qF "$kind" || ok=0
  [ -n "$detail" ] && { printf '%s' "$out" | grep -qF "$detail" || ok=0; }
  [ "$st2" = "FIXED POINT" ] || ok=0
  if [ "$ok" = 1 ]; then
    printf "  PASS  %-26s %s %s\n" "$(basename "$f")" "$kind" "$detail"; pass=$((pass+1))
  else
    printf "  FAIL  %-26s kind[%s] detail[%s] quine[%s]\n" "$(basename "$f")" "$kind" "$detail" "$st2"; fail=$((fail+1))
  fi
  rm -f "$t"
}
SETTLED="SETTLED to a self-consistent fixed point"
check examples/mind-homeostasis.pal      "$SETTLED"      "arousal 4   calm"
check examples/mind-cycle.pal            "LIMIT CYCLE"   "period 6"
check examples/mind-runaway.pal          "RUNAWAY"
check examples/mind-strange-loop.pal     "$SETTLED"      "(goal 2)"
check examples/mind-noisy.pal            "BOUNDED"       "calm"
check examples/mind-bistable.pal         "BOUNDED"       "high"
check examples/mind-saturating.pal       "$SETTLED"      "(ctl 8)"
check examples/mind-predictive.pal       "$SETTLED"      "err 1"
check examples/mind-dyad.pal             "$SETTLED"      "gap 3"
check examples/mind-dyad-escalation.pal  "RUNAWAY"
echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
