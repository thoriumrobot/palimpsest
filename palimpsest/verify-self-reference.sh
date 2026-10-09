#!/usr/bin/env bash
# Verifies every example in SELF-REFERENCE.md. Run from the project root after
# `cargo build --release`.
set -u
BIN=./target/release/palimpsest
export PALIMPSEST_LIB="$(pwd)/lib"
pass=0; fail=0
ck () { # ck "label" "expected" "actual"
  if [ "$2" = "$3" ]; then printf "  PASS  %-34s %s\n" "$1" "$3"; pass=$((pass+1))
  else printf "  FAIL  %-34s got:[%s] want:[%s]\n" "$1" "$3" "$2"; fail=$((fail+1)); fi
}

# --- term-level examples (from examples/self-reference-demo.pal) ---
declare -A WANT=(
 ["(tree (leaf) (leaf))"]="(tree (leaf) (leaf))"
 ["(sprout)"]="(sprout)"
 ["(seed)"]="(sprout)"
 ["(app quine (quote quine))"]="(app quine (quote quine))"
 ["(app anything (quote quine))"]="(app quine (quote quine))"
 ["(self me (describes me))"]="(self me (describes me))"
 ["(cyc 1 2 3)"]="(cyc 1 2 3)"
 ["(list 3 1 2)"]="(list 1 2 3)"
 ["(list 5 2 4 1 3)"]="(list 1 2 3 4 5)"
 ["(list counts 0 a b)"]="(list counts 4 a b)"
 ["(list counts 9 a b c d e)"]="(list counts 7 a b c d e)"
 ["(app (fix fac) 5)"]="120"
 ["(app (fix summ) 10)"]="55"
)
# capture demo outputs into an assoc by subject
while IFS= read -r line; do
  subj=$(sed -E 's/^show: (.*)  ==>  .*/\1/' <<<"$line")
  res=$(sed -E 's/^show: .*  ==>  (.*)/\1/' <<<"$line")
  if [ -n "${WANT[$subj]+x}" ]; then ck "$subj" "${WANT[$subj]}" "$res"; fi
done < <($BIN examples/self-reference-demo.pal 2>&1 | grep '^show:')
# the two-headed cases (pair) checked explicitly
p1=$($BIN examples/self-reference-demo.pal 2>&1 | grep -m1 'show: (pair x y)' | sed -E 's/.*==>  //')
ck "(pair x y) with flip"        "(pair y x)" "$p1"
p2=$($BIN examples/self-reference-demo.pal 2>&1 | grep 'show: (pair x y)' | sed -n 2p | sed -E 's/.*==>  //')
ck "(pair x y) with (flip;flip)" "(pair x y)" "$p2"

# --- file-level: trivial quine ---
t=$(mktemp /tmp/q.XXXX.pal); cp examples/quine.pal "$t"
st=$($BIN "$t" 2>&1 | grep -oE "FIXED POINT"); ck "quine.pal" "FIXED POINT" "$st"; rm -f "$t"

# --- file-level: counter quine converges over runs ---
t=$(mktemp /tmp/c.XXXX.pal); cp examples/counter-quine.pal "$t"
seq=""
for i in 1 2 3 4; do
  s=$($BIN "$t" 2>&1 | grep -oE "WROTE|FIXED POINT")
  seq="$seq$s|"
done
ck "counter-quine run1..4" "WROTE|WROTE|WROTE|FIXED POINT|" "$seq"; rm -f "$t"

# --- file-level: hanoi self-solving quine ---
t=$(mktemp /tmp/h.XXXX.pal); cp examples/hanoi-quine.pal "$t"
r1=$($BIN "$t" 2>&1 | grep -oE "WROTE")
r2=$($BIN "$t" 2>&1 | grep -oE "FIXED POINT")
ck "hanoi-quine run1/run2" "WROTE|FIXED POINT" "$r1|$r2"; rm -f "$t"

# --- reversibility: undo ---
t=$(mktemp /tmp/u.XXXX.pal); cp examples/counter-quine.pal "$t"
$BIN "$t" >/dev/null 2>&1
$BIN undo "$t" >/dev/null 2>&1
ck "undo reverts self-modification" "main = (count 0)" "$(grep '^main' "$t")"; rm -f "$t"

echo "---------------------------------------------------------------"
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ]
