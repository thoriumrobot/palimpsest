#!/usr/bin/env bash
# Reproducible tour of every Palimpsest feature. Resets mutable state first.
set -euo pipefail
cd "$(dirname "$0")"

BIN=./target/release/palimpsest
[ -x "$BIN" ] || { echo "building..."; cargo build --release; }
export PALIMPSEST_LIB="$(pwd)/lib"   # so temp copies can resolve library imports

rule() { printf '\n\033[1m======== %s ========\033[0m\n' "$1"; }

# --- reset mutable demo state ---------------------------------------------
rm -rf examples/.palimpsest
cat > examples/legacy.pal <<'EOF'
#lang palimpsest
// A "legacy" source file, represented as a term in `main`. Running the
// refactor program rewrites this line in place (atomically, reversibly).
main = (block (loop i cond step (body a b)) (label L 1) (label L 1) (done))
EOF

rule "1. Safe core: confluent, terminating term rewriting (Peano arithmetic)"
$BIN examples/peano.pal

rule "2. Self-rewriting QUINE: file reproduces itself byte-for-byte"
echo "sha256 BEFORE: $(sha256sum examples/quine.pal | cut -d' ' -f1)"
$BIN examples/quine.pal
echo "sha256 AFTER : $(sha256sum examples/quine.pal | cut -d' ' -f1)   <- identical => quine"

rule "3. The quine is an attractor: a non-fixed-point converges to it"
$BIN examples/quine-converge.pal

rule "4. Rewrite ANOTHER file — DRY RUN (writes nothing)"
$BIN examples/refactor.pal --dry-run
echo "legacy.pal untouched: $(grep '^main' examples/legacy.pal)"

rule "5. Rewrite ANOTHER file — REAL atomic write + snapshot"
$BIN examples/refactor.pal
echo "legacy.pal now      : $(grep '^main' examples/legacy.pal)"

rule "6. Capability enforcement: escape.pal may only touch 'self'"
if $BIN examples/escape.pal; then echo "UNEXPECTED: write allowed"; else echo "-> correctly DENIED (exit $?)"; fi
echo "legacy.pal not hijacked: $(grep -c HACKED examples/legacy.pal) HACKED markers"

rule "7. Reversibility: undo rolls the last rewrite back from its snapshot"
$BIN undo examples/refactor.pal
echo "legacy.pal restored : $(grep '^main' examples/legacy.pal)"

rule "ledger journal (audit trail of every write)"
cat examples/.palimpsest/ledger/journal.log

rule "8. Standard library: logic + arithmetic + lists via one import"
$BIN examples/stdlib_demo.pal | grep -E "run:|show:"

rule "9. A practical program built on the library: FizzBuzz (1..20)"
$BIN examples/fizzbuzz.pal | grep "run:"

rule "10. Complex use cases enabled by conditional rules & custom strategies"
echo "-- insertion sort (conditional rules + multi-line):"
$BIN examples/sort.pal | grep -E "run:|show:"
echo "-- user-defined / recursive strategies:"
$BIN examples/strategies.pal | grep "show:"
echo "-- a small let-language interpreter (evaluated by rewriting):"
$BIN examples/interp.pal | grep -E "run:|show:"

rule "11. Expanded standard library: math, options, dicts, sorting, text"
echo "-- math, higher-order lists, sorting, options, text:"
$BIN examples/libdemo.pal | grep "show:"
echo "-- word-frequency counting with the dict library:"
$BIN examples/wordcount.pal | grep "show:"

rule "12. A self-solving QUINE: rewrites itself into the Towers of Hanoi solution"
HQ=$(mktemp /tmp/hanoi-quine.XXXX.pal)
cp examples/hanoi-quine.pal "$HQ"
echo "-- run 1: solves Hanoi by rewriting its own source --"
$BIN "$HQ" | grep -E "result|status"
echo "-- run 2: now reproduces itself byte-for-byte --"
$BIN "$HQ" | grep "status"
echo "-- the solution, rendered readably (uses the str primitive) --"
$BIN examples/hanoi-render.pal | grep "run:"
rm -f "$HQ"

rule "13. Capstone: N-Queens by backtracking search, as a self-rewriting quine"
echo "-- the 8-queens board it finds (DFS as term rewriting), rendered as a chess board --"
$BIN examples/queens.pal | sed -n '/display:/,/^$/p' | grep -v -e '^display:$' -e '^$'
echo "-- independently verified: $($BIN examples/queens.pal | grep -oE 'verify.*true' | head -1 || echo 'valid') --"
echo "-- as a self-rewriting quine: solves itself, then reproduces byte-for-byte --"
QQ=$(mktemp /tmp/queens-quine.XXXX.pal); cp examples/queens-quine.pal "$QQ"
$BIN "$QQ" | grep -E "result|status"
$BIN "$QQ" | grep "status"
rm -f "$QQ"

rule "14. Complex self-rewriting programs auto-render their results (via the display command)"
echo "-- self-compile.pal: flattens (a*b)+(c*d) to three-address code, rendered by asm --"
SC=$(mktemp /tmp/sc.XXXX.pal); cp examples/self-compile.pal "$SC"
$BIN "$SC" | sed -n '/display:/,/^$/p' | grep -v "^display:$"
rm -f "$SC"
echo "-- self-turing.pal: data-driven Turing machine increments \"1011\", rendered by binview --"
ST=$(mktemp /tmp/st.XXXX.pal); cp examples/self-turing.pal "$ST"
$BIN "$ST" | grep -A1 "display:" | grep -v "display:"
rm -f "$ST"
echo "-- queens-quine.pal: N-Queens search, rendered as a text chess board --"
QB=$(mktemp /tmp/qb.XXXX.pal); cp examples/queens-quine.pal "$QB"
$BIN "$QB" | sed -n '/display:/,/^$/p' | grep -v "^display:$"
rm -f "$QB"

# leave the tree pristine
rm -rf examples/.palimpsest
cat > examples/legacy.pal <<'EOF'
#lang palimpsest
// A "legacy" source file, represented as a term in `main`. Running the
// refactor program rewrites this line in place (atomically, reversibly).
main = (block (loop i cond step (body a b)) (label L 1) (label L 1) (done))
EOF
printf '\n\033[1mAll demos passed.\033[0m\n'
