#!/usr/bin/env bash
# Runs every puzzle solution and checks it produces the expected transformation.
# Usage: ./puzzles/check.sh   (run from the project root, after `cargo build --release`)
set -u
BIN=./target/release/palimpsest
DIR="$(cd "$(dirname "$0")" && pwd)/solutions"

declare -A EXPECT=(
  [01-swap]="(swap y x)"
  [02-reverse-triple]="(tri 3 2 1)"
  [03-cycle-four]="(q b c d a)"
  [04-swap-ends]="(row e b c d a)"
  [05-rotate-left]="(list b c d a)"
  [06-rotate-right]="(list d a b c)"
  [07-pluck-to-front]="(list star a b c d)"
  [08-reverse]="(list e d c b a)"
  [09-riffle]="(list a 1 b 2 c 3)"
  [10-unriffle]="(pair (list a b c) (list 1 2 3))"
  [11-swap-adjacent]="(list b a d c f e)"
  [12-bubble-sort]="(list 1 2 3 4 5 6 7 8 9)"
  [13-pancake-flip]="(list c b a d e)"
  [14-apply-permutation]="(out z x y)"
  [15-term-quine]="(app quine (quote quine))"
  [18-oscillator]="(o x y)"
  [19-idempotence]="(list 1 2 3)"
  [20-autogram]="(list counts 4 a b)"
  [21-fixpoint-combinator]="120"
)

# Run-once puzzles (their result appears after `==>`).
order=(01-swap 02-reverse-triple 03-cycle-four 04-swap-ends 05-rotate-left \
       06-rotate-right 07-pluck-to-front 08-reverse 09-riffle 10-unriffle \
       11-swap-adjacent 12-bubble-sort 13-pancake-flip 14-apply-permutation \
       15-term-quine 18-oscillator 19-idempotence 20-autogram 21-fixpoint-combinator)

pass=0; fail=0
for name in "${order[@]}"; do
  got=$("$BIN" "$DIR/$name.pal" 2>&1 | grep -oE "==>  .*" | tail -1 | sed 's/^==>  //')
  want="${EXPECT[$name]}"
  if [ "$got" = "$want" ]; then
    printf "  PASS  %-24s %s\n" "$name" "$got"
    pass=$((pass+1))
  else
    printf "  FAIL  %-24s got: %s | want: %s\n" "$name" "$got" "$want"
    fail=$((fail+1))
  fi
done

# Self-rewriting quines: run twice, check the WROTE result and that run 2 is a
# byte-identical FIXED POINT. P17 imports the chart library, so it must run in
# place (on a backup) for its relative import to resolve; the others are
# self-contained and run on a scratch copy in /tmp.
check_quine () { # name  expected-result  [inplace]
  local name="$1" want="$2" mode="${3:-copy}" src="$DIR/$1.pal" run bkp
  [ -f "$src" ] || { printf "  FAIL  %-24s missing solution file\n" "$name"; fail=$((fail+1)); return; }
  if [ "$mode" = inplace ]; then
    run="$src"; bkp="$(mktemp /tmp/bkp.XXXX)"; cp "$src" "$bkp"
  else
    run="$(mktemp /tmp/q.XXXX.pal)"; cp "$src" "$run"
  fi
  local got status2
  got=$("$BIN" "$run" 2>&1 | grep -oE "result  : .*" | sed 's/^result  : //')
  status2=$("$BIN" "$run" 2>&1 | grep -oE "FIXED POINT")
  if [ "$got" = "$want" ] && [ "$status2" = "FIXED POINT" ]; then
    printf "  PASS  %-24s %s  then quine\n" "$name" "$got"
    pass=$((pass+1))
  else
    printf "  FAIL  %-24s got: %s (%s)\n" "$name" "$got" "$status2"
    fail=$((fail+1))
  fi
  if [ "$mode" = inplace ]; then cp "$bkp" "$src"; rm -f "$bkp"; else rm -f "$run"; fi
}

check_quine 16-random-stream   "(stream 32 78 27 57 31 33)"
check_quine 17-dice-histogram  "(series 2 3 6 1 3 3 2 2 5 4 3 1 1 2 2 6 6 2)" inplace
check_quine 22-self-sorting-quine "(list 1 2 3 4 5 6 7 8 9)"

echo "-------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
