#!/usr/bin/env python3
"""Build the browser playground: index.html at the repository root.

    python3 web/build.py

Embeds web/palimpsest.py (the interpreter) and a manifest of the repository's
programs (examples/, puzzles/solutions/, lib/) into web/index.template.html and
writes index.html, ready for GitHub Pages. The page fetches the .pal files
themselves from the site at run time, so it must be served from the repository
root (GitHub Pages does this; locally: python3 -m http.server).

Also writes .nojekyll, so GitHub Pages serves every file as is.
Rebuild after changing the interpreter or adding, renaming or removing programs.
"""
import glob
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
PYODIDE_VERSION = "0.29.4"
START = "examples/hanoi-quine.pal"


def tracked(pattern):
    """Programs under version control (falls back to the working tree)."""
    try:
        out = subprocess.run(["git", "ls-files", pattern], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.split()
        if out:
            return sorted(out)
    except (OSError, subprocess.CalledProcessError):
        pass
    return sorted(glob.glob(pattern, root_dir=ROOT))


def title_of(path):
    """The first comment line of a program, as its one-line description."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("//"):
                t = s.lstrip("/").strip()
                if t:
                    return t[:160]
            elif s and not s.startswith("#"):
                break
    return ""


def main():
    times_path = os.path.join(WEB, "native-times.json")
    times = json.load(open(times_path)) if os.path.exists(times_path) else {}
    entries = []
    for pattern in ("examples/*.pal", "puzzles/solutions/*.pal", "lib/*.pal"):
        for p in tracked(pattern):
            e = {"path": p, "title": title_of(p)}
            if p in times:
                e["native"] = times[p]
            entries.append(e)
    manifest = {"start": START, "files": entries}

    py = open(os.path.join(WEB, "palimpsest.py"), encoding="utf-8").read()
    if "</script" in py.lower():
        raise SystemExit("palimpsest.py must not contain '</script'")
    manifest_json = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    manifest_json = manifest_json.replace("</", "<\\/")

    html = open(os.path.join(WEB, "index.template.html"), encoding="utf-8").read()
    for key, val in (("%%PALIMPSEST_PY%%", py), ("%%MANIFEST%%", manifest_json),
                     ("%%PYODIDE_VERSION%%", PYODIDE_VERSION)):
        if key not in html:
            raise SystemExit("template is missing " + key)
        html = html.replace(key, val)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    print("index.html: %d bytes, %d programs, Pyodide %s" % (len(html.encode()), len(entries), PYODIDE_VERSION))


if __name__ == "__main__":
    main()
