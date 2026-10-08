#!/usr/bin/env bash
# Verifies the game-theoretic analysis of independent telors (TELIC-GAMES.md):
# the library against textbook games, the merge-level manipulation levers,
# the equilibria of join games, the improvement dynamics as a rewriting
# system, and the exhaustive chain-theorem sweep.
set -u
cd "$(dirname "$0")"
BIN=./target/release/palimpsest
export PALIMPSEST_LIB="$(pwd)/lib"
pass=0; fail=0

check () { # file, description, expected substrings...
  local file="$1" desc="$2"; shift 2
  local out; out="$("$BIN" "$file" 2>&1)"
  local ok=1 missing=""
  for detail in "$@"; do
    if ! printf '%s' "$out" | grep -qF -- "$detail"; then ok=0; missing="$detail"; fi
  done
  if [ "$ok" = 1 ]; then
    printf "  PASS  %-30s %s\n" "$(basename "$file")" "$desc"; pass=$((pass+1))
  else
    printf "  FAIL  %-30s missing: %s\n" "$(basename "$file")" "$missing"; fail=$((fail+1))
  fi
}

check examples/games-basics.pal "PD / matching pennies / BoS textbook answers" \
  "(pd-nash (list (prof d d)))" \
  "(pd-d-dominant true true)" \
  "(pd-c-dominant false)" \
  "(pd-dd-pareto-dominators (list (prof c c)))" \
  "(pd-potential (list) true)" \
  "(mp-nash (list))" \
  "(mp-mixed (mixed (frac 1 2) (frac 1 2)))" \
  "(mp-potential 4 false)" \
  "(bos-nash (list (prof o o) (prof f f)))" \
  "(bos-mixed (mixed (frac 2 3) (frac 1 3)))"

check examples/telor-games-merge.pal "each failed axiom is a strategic lever" \
  "(scheduler-decides-last-writer-wins (list q p))" \
  "(scheduler-decides-first-writer-wins (list p q))" \
  "(scheduler-irrelevant-under-max (list c))" \
  "(scheduler-decides-broken-table (list c b a))" \
  "(coalition-premerge-broken c a)" \
  "(coalition-premerge-max c c)" \
  "(duplicate-is-leverage-under-add 3 4)" \
  "(duplicate-is-inert-under-max b b)"

check examples/telor-games-join.pal "top trap, chain dominance, assert/yield, no-NE" \
  "(chain-top-trap-is-nash true)" \
  "(chain-top-trap-is-dominated true)" \
  "(diamond-top-trap-is-nash true)" \
  "(diamond-top-trap-is-dominated true)" \
  "(chain-peaks-dominant true true)" \
  "(chain-truthful-outcome mid)" \
  "(chain-truthful-is-nash true)" \
  "(chain-truthful-is-pareto-dominated false)" \
  "(kinked-peak-dominant false)" \
  "(kinked-witnesses (list (prof hi mid)))" \
  "(diamond-peaks-dominant false false)" \
  "(diamond-truthful-outcome top)" \
  "(diamond-truthful-is-nash false)" \
  "(diamond-pure-nash (list (prof bot b) (prof a bot) (prof a a) (prof b b) (prof top top)))" \
  "(diamond-nash-outcomes (list b a a b top))" \
  "(hawk-dove-pure-nash (list (prof a bot) (prof bot b)))" \
  "(hawk-dove-mixed (mixed (frac 3 4) (frac 3 4)))" \
  "(hawk-dove-p-top (frac 9 16))" \
  "(pennies-pure-nash (list))" \
  "(pennies-mixed (mixed (frac 1 2) (frac 1 2)))"

check examples/telor-games-dynamics.pal "improvement dynamics as rewriting" \
  "(hawk-dove-terminating true)" \
  "(hawk-dove-exact-potential (list))" \
  "(hawk-dove-locally-confluent false)" \
  "(hawk-dove-unjoinable (list (pair (prof bot b) (prof a bot))" \
  "(hawk-dove-reachable-from-conflict (list (prof bot b) (prof a bot)))" \
  "(hawk-dove-schedule-dependent-starts (list (prof a b) (prof bot bot)))" \
  "(hawk-dove-telor0-moves-first (list (prof a b) (prof bot b) (prof bot b)))" \
  "(hawk-dove-telor1-moves-first (list (prof a b) (prof a bot) (prof a bot)))" \
  "(pennies-terminating false)" \
  "(pennies-cycle (list (prof a b) (prof b b) (prof b a) (prof a a) (prof a b)))" \
  "(pennies-ms-violations 4)" \
  "(chase-pure-nash (list (prof a top) (prof b top) (prof bot top) (prof top top)))" \
  "(chase-terminating false)" \
  "(chase-cycle-outcomes (list top b top a top))" \
  "(path-is-exact-potential true)" \
  "(path-ms-violations (list))" \
  "(path-terminating true)" \
  "(path-pure-nash (list (prof r r r) (prof g g g)))" \
  "(path-nash-potentials (list 6 5))" \
  "(path-reachable-from-rgg (list (prof g g g) (prof r r r)))" \
  "(path-schedule-dependent-starts 4)" \
  "(opposed-ms-violations 8)" \
  "(opposed-terminating false)" \
  "(opposed-pure-nash (list))" \
  "(opposed-cycle (list (prof r r r) (prof r g r) (prof r g g) (prof g g g) (prof g r g) (prof g r r) (prof r r r)))"

check examples/telor-games-chain.pal "chain => FIP; diamond => cycles (169 games each)" \
  "(weak-orders-on-3 13)" \
  "(chain-games-without-fip 0)" \
  "(diamond-games-without-fip 18)"

check examples/telor-games-metagame.pal "Howard metagames: PD helped, assert/yield and MP not (~25 s)" \
  "(pd-nash (list (prof d d)))" \
  "(pd-exact-potential true)" \
  "(pd-welfare (list 6 5 5 2))" \
  "(pd-meta21 (list (prof c c) (prof d d)))" \
  "(pd-symmetric (list (prof c c) (prof d d)))" \
  "(hawk-dove-symmetric (list (prof a bot) (prof bot b)))" \
  "(pennies-meta21 (list (prof a a) (prof b b)))" \
  "(pennies-meta12 (list (prof a b) (prof b a)))" \
  "(pennies-symmetric (list))"

echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
