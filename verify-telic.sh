#!/usr/bin/env bash
# Verifies the telic-recursion confluence analysis: the two-telor model must
# be found non-confluent with the expected witness pairs, order-dependence
# must show up concretely, and the single-rule fix must restore confluence.
set -u
BIN=./target/release/palimpsest
export PALIMPSEST_LIB="$(pwd)/lib"
pass=0; fail=0

out="$("$BIN" examples/telor-confluence.pal 2>&1)"
ok=1
for detail in \
  "false" \
  "(order-dependence (resolved p p) (resolved q q))" \
  "(single-coordinated-rule-restores-confluence true (resolved anchor anchor) (resolved anchor anchor))"
do
  printf '%s' "$out" | grep -qF "$detail" || ok=0
done
if [ "$ok" = 1 ]; then
  printf "  PASS  telor-confluence.pal    non-confluent, order-dependent, single-rule fix confirmed\n"
  pass=$((pass+1))
else
  printf "  FAIL  telor-confluence.pal\n"
  fail=$((fail+1))
fi

# Sanity-check lib/ars.pal itself against three cases with known answers.
check_expr () { # description, palimpsest expression, expected substring
  local desc="$1" expr="$2" want="$3"
  local tmp; tmp="$(mktemp /tmp/ars-check.XXXX.pal)"
  cat > "$tmp" << EOF
#lang palimpsest
#mode run-only
#fuel 2000000
import "ars.pal"
strategy solve = outermost(prim + rules)
main = $expr
run solve
EOF
  local out2; out2="$("$BIN" "$tmp" 2>&1)"
  if printf '%s' "$out2" | grep -qF "$want"; then
    printf "  PASS  %-26s %s\n" "$desc" "$want"
    pass=$((pass+1))
  else
    printf "  FAIL  %-26s expected %s\n" "$desc" "$want"
    fail=$((fail+1))
  fi
  rm -f "$tmp"
}

check_expr "non-confluent a->b/a->c" \
  "(locally-confluent? (rules (rule a b) (rule a c)))" "false"
check_expr "confluent single rule" \
  "(locally-confluent? (rules (rule (double ?n) (plus ?n ?n))))" "true"
check_expr "confluent genuine overlap" \
  "(locally-confluent? (rules (rule (f ?x b) (g ?x)) (rule (f a ?y) (g a))))" "true"
check_expr "occurs-check rejects x=g(x)" \
  "(unify ?x (g ?x) (dict-empty))" "none"

echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
