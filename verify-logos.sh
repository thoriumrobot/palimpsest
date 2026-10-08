#!/usr/bin/env bash
# Verifies LOGOS-SCSPL.md: the pooling algebra, the frozen-versus-telic
# comparison, step-wise versus whole-path selection (examples/logos-scspl.pal,
# about a minute), and the self-configuring fixed point (examples/logos-eigen.pal
# must rewrite itself on run 1 and reproduce itself byte for byte on run 2).
set -u
cd "$(dirname "$0")"
BIN=./target/release/palimpsest
export PALIMPSEST_LIB="$(pwd)/lib"
pass=0; fail=0

out="$("$BIN" examples/logos-scspl.pal 2>&1)"
ok=1; missing=""
for detail in \
  "(attention-all-orders (list (frac 33 7)))" \
  "(attention-duplicate (frac 4 1) (frac 7 2))" \
  "(positional-attention-orders (list (frac 40 7) (frac 51 10) (frac 16 3) (frac 27 7) (frac 97 21) (frac 65 17)))" \
  "(maxpool-all-orders (list 9))" \
  "(maxpool-duplicate 5 5)" \
  "(frozen (sum-of (halves 11 13) (changes 0) (last 0) (repeats 0) (ctx-fn true) (distinct 9) (final-syntax (list))" \
  "(telic (sum-of (halves 16 29) (changes 18) (last 34) (repeats 418) (ctx-fn true) (distinct 8) (final-syntax (list (cell b c 6) (cell a b 6) (cell c a 6)))" \
  "(tail (list a b c a b c a b c b c a b c a b))" \
  "(greedy (list a b a b) 2)" \
  "(best (list a c c c) 7)"
do
  printf '%s' "$out" | grep -qF -- "$detail" || { ok=0; missing="$detail"; }
done
if [ "$ok" = 1 ]; then printf "  PASS  %-22s pooling algebra, frozen vs telic, path selection\n" "logos-scspl.pal"; pass=$((pass+1))
else printf "  FAIL  %-22s missing: %s\n" "logos-scspl.pal" "$missing"; fail=$((fail+1)); fi

t="$(mktemp /tmp/logos-eigen.XXXX.pal)"; cp examples/logos-eigen.pal "$t"
r1=$("$BIN" "$t" 2>&1 | grep -oE "WROTE|FIXED POINT" | head -1)
got=$(grep '^main = ' "$t" | sed 's/^main = //')
r2=$("$BIN" "$t" 2>&1 | grep -oE "FIXED POINT" | head -1)
want='(telic-fix eig (list (cell b c 6) (cell a b 6) (cell c a 6)) 2)'
if [ "$r1" = "WROTE" ] && [ "$got" = "$want" ] && [ "$r2" = "FIXED POINT" ]; then
  printf "  PASS  %-22s converged in 2 refinements, then quined\n" "logos-eigen.pal"; pass=$((pass+1))
else
  printf "  FAIL  %-22s run1=%s main=[%s] run2=%s\n" "logos-eigen.pal" "$r1" "$got" "$r2"; fail=$((fail+1))
fi
rm -f "$t"

echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
