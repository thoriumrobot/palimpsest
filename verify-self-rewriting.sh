#!/usr/bin/env bash
# Verifies the complex self-rewriting programs: each must SOLVE on run 1 (writing
# the answer into its own source), reproduce itself byte-for-byte on run 2 (a
# quine), AND print a human-readable rendering of its result via `display`.
set -u
BIN=./target/release/palimpsest
export PALIMPSEST_LIB="$(pwd)/lib"   # so temp copies can resolve ../lib/render.pal
pass=0; fail=0
check () { # check file "expected-main-after-run1" "display-substring"
  local f="$1" want="$2" disp="$3"
  local t; t="$(mktemp /tmp/vsr.XXXX.pal)"; cp "$f" "$t"
  local out r1 got st2 dline
  out="$("$BIN" "$t" 2>&1)"
  r1=$(printf '%s' "$out" | grep -oE "WROTE|FIXED POINT" | head -1)
  got=$(grep '^main = ' "$t" | sed 's/^main = //')
  dline=$(printf '%s' "$out" | grep -F "$disp" | head -1)
  st2=$("$BIN" "$t" 2>&1 | grep -oE "FIXED POINT")
  if [ "$r1" = "WROTE" ] && [ "$got" = "$want" ] && [ -n "$dline" ] && [ "$st2" = "FIXED POINT" ]; then
    printf "  PASS  %-22s solved, rendered, quined\n" "$(basename "$f")"; pass=$((pass+1))
  else
    printf "  FAIL  %-22s run1=%s display=[%s] run2=%s\n" "$(basename "$f")" "$r1" "$dline" "$st2"
    printf "        main=[%s]\n        want=[%s]\n" "$got" "$want"; fail=$((fail+1))
  fi
  rm -f "$t"
}

check examples/self-sort-text.pal '"   bcefhiknooqrtuwx"' '"   bcefhiknooqrtuwx"'
check examples/self-compile.pal   '(program (code (:= t0 (bin * (var a) (var b))) (:= t1 (bin * (var c) (var d))) (:= t2 (bin + (var t0) (var t1)))) (return (var t2)))' 't0 := a * b'
check examples/self-dedup.pal     '(list (pt 1 2) (rgb 255 0 0) (pt 3 4))' 'set of 3:'
check examples/self-turing.pal    '"1100"' 'binary 1100  =  12'
check examples/queens-quine.pal   '(found (cols 4 2 7 3 6 8 5 1))' '1 Q . . . . . . .'
check examples/hanoi-quine.pal    '(moves (move a c) (move a b) (move c b) (move a c) (move b a) (move b c) (move a c))' '1. a -> c'

echo "-------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
