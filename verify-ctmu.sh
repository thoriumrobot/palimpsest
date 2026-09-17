#!/usr/bin/env bash
# Verifies the CTMU containment model: both programs must compute the
# expected theorem results, reproduce themselves as quines, and (for the
# static example) each of T1/T2/T3/T3-HAZARD must independently hold.
set -u
BIN=./target/release/palimpsest
export PALIMPSEST_LIB="$(pwd)/lib"
pass=0; fail=0

check () { # check file "detail-substring" ["detail-substring" ...]
  local f="$1"; shift
  local t; t="$(mktemp /tmp/ctmu.XXXX.pal)"; cp "$f" "$t"
  local out1 out2 st2 ok=1
  out1="$("$BIN" "$t" 2>&1)"
  out2="$("$BIN" "$t" 2>&1)"
  st2=$(printf '%s' "$out2" | grep -oE "FIXED POINT")
  [ "$st2" = "FIXED POINT" ] || ok=0
  for detail in "$@"; do
    printf '%s' "$out1" | grep -qF "$detail" || ok=0
  done
  if [ "$ok" = 1 ]; then
    printf "  PASS  %-26s quined, %d checks matched\n" "$(basename "$f")" "$#"
    pass=$((pass+1))
  else
    printf "  FAIL  %-26s quine[%s]\n" "$(basename "$f")" "${st2:-none}"
    fail=$((fail+1))
  fi
  rm -f "$t"
}

# ctmu-containment.pal: T1 (bounded topological containment), T2 (unbounded
# descriptive containment), T3 (dual containment, no contradiction), and the
# honest T3-HAZARD negative result (colliding vocabulary silently reduced).
check examples/ctmu-containment.pal \
  "(t1 true false false 1 4 true)" \
  "(t2 true true true true (some (dict (entry xs (list e e e)))))" \
  "(t3 true)" \
  "(mirrored-as-data false)"

# ctmu-conspansion.pal: a provable period-6 limit cycle (state space is
# finite by construction, so the pigeonhole principle guarantees exact
# recurrence), and the dual-containment invariant holding at all 25
# visited ticks, not merely asserted.
check examples/ctmu-conspansion.pal \
  "(cycle 6)" \
  "(invariant-holds-at-every-tick true)" \
  "LIMIT CYCLE, period 6"

# ctmu-nonsubsumption.pal: the constructive non-subsumption proof. Pure
# structural merge is INCOMPLETE (misses the genuine descriptive instance);
# the OR-merge is COMPLETE but UNSOUND as a size bound (the "contained"
# instance, size 42, is computed to be larger than its "container", size 3).
check examples/ctmu-nonsubsumption.pal \
  "(attempt-1-pure-structural (case structural true) (case descriptive false))" \
  "(attempt-2-merged-both-directions (case structural true) (case descriptive true))" \
  "(size-of-pattern 3)" \
  "(size-of-instance 42)" \
  "(soundness-of-merge-as-a-bound true)"

echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
