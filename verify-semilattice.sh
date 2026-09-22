#!/usr/bin/env bash
# Verifies the semilattice characterization: max{a,b,c} must be found a
# semilattice with order-independent folding; a deliberately non-associative
# table must fail is-semilattice? and show order-DEPENDENT folding.
set -u
BIN=./target/release/palimpsest
export PALIMPSEST_LIB="$(pwd)/lib"
pass=0; fail=0

out="$("$BIN" examples/telor-semilattice.pal 2>&1)"
ok=1
for detail in \
  "(max-is-a-semilattice true true true true)" \
  "(broken-table-is-not-a-semilattice true true false false)" \
  "(max-order-independent c c c)" \
  "(broken-order-dependent c a a)"
do
  printf '%s' "$out" | grep -qF "$detail" || ok=0
done
if [ "$ok" = 1 ]; then
  printf "  PASS  telor-semilattice.pal   semilattice <=> order-independent convergence, both directions\n"
  pass=$((pass+1))
else
  printf "  FAIL  telor-semilattice.pal\n"
  fail=$((fail+1))
fi

echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
