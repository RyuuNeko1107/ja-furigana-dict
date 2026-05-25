#!/usr/bin/env python3
"""
default 訓切替による jukugo regression 検出ツール。

kanji block の default を音→訓に切り替えた際、 jukugo に登録されていない
compound が default 連結で動いていたケースを検出する。

使い方:
    # HEAD vs 直前 commit (= 最新変更の regression check)
    python tools/check_default_regression.py

    # HEAD vs 特定 commit / branch
    python tools/check_default_regression.py e6fee88

    # 2 commit 間の比較
    python tools/check_default_regression.py e6fee88 HEAD

出力:
    - REGRESSION: old defaults で正しかったが new defaults で壊れた compound
    - 各行に surface, expected reading, old concat, new concat, 変更された kanji

exit code: 0 = regression なし, 1 = regression あり
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


def extract_defaults(text: str) -> dict[str, str]:
    defaults = {}
    for m in re.finditer(r'char = "(.)".*?default = "([^"]+)"', text, re.DOTALL):
        char, reading = m.group(1), m.group(2)
        if char not in defaults:
            defaults[char] = reading
    for m in re.finditer(r'char = "(.)"[\s\S]*?default = "([^"]+)"', text):
        defaults[m.group(1)] = m.group(2)
    defaults2 = {}
    for m in re.finditer(
        r'char\s*=\s*"(.)"\n(?:#[^\n]*\n)?default\s*=\s*"([^"]+)"', text
    ):
        defaults2[m.group(1)] = m.group(2)
    return defaults2 or defaults


def load_jukugo(base: Path) -> dict[str, str]:
    jukugo: dict[str, str] = {}
    jukugo_dir = base / "core" / "jukugo"
    if not jukugo_dir.exists():
        return jukugo
    for root, _dirs, files in os.walk(jukugo_dir):
        for fn in files:
            if not fn.endswith(".toml"):
                continue
            with open(os.path.join(root, fn), encoding="utf-8") as f:
                for line in f:
                    m = re.match(r'^"([^"]+)"\s*=\s*"([^"]+)"', line)
                    if m:
                        jukugo[m.group(1)] = m.group(2)
    return jukugo


def to_kata(s: str) -> str:
    return "".join(
        chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s
    )


def git_show(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        print(f"[warn] git show {ref}:{path} failed", file=sys.stderr)
        return ""
    return result.stdout


def find_regressions(
    old_defaults: dict[str, str],
    new_defaults: dict[str, str],
    jukugo: dict[str, str],
) -> list[tuple[str, str, str, str, list[tuple[str, str, str]]]]:
    regressions = []
    for surface, expected in jukugo.items():
        if len(surface) < 2:
            continue
        chars = list(surface)
        if not all(c in old_defaults and c in new_defaults for c in chars):
            continue
        old_concat = "".join(old_defaults[c] for c in chars)
        new_concat = "".join(new_defaults[c] for c in chars)
        old_match = to_kata(old_concat) == to_kata(expected)
        new_match = to_kata(new_concat) == to_kata(expected)
        if old_match and not new_match:
            changed = [
                (c, old_defaults[c], new_defaults[c])
                for c in chars
                if old_defaults[c] != new_defaults[c]
            ]
            regressions.append((surface, expected, old_concat, new_concat, changed))
    return regressions


def main() -> None:
    base = Path(".")
    overrides_path = "core/kanji/overrides.toml"

    if len(sys.argv) >= 3:
        old_ref, new_ref = sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 2:
        old_ref, new_ref = sys.argv[1], "HEAD"
    else:
        old_ref, new_ref = "HEAD~1", "HEAD"

    old_text = git_show(old_ref, overrides_path)
    if new_ref == "HEAD":
        with open(base / overrides_path, encoding="utf-8") as f:
            new_text = f.read()
    else:
        new_text = git_show(new_ref, overrides_path)

    if not old_text or not new_text:
        print("[error] could not load overrides.toml from git")
        sys.exit(2)

    old_defaults = extract_defaults(old_text)
    new_defaults = extract_defaults(new_text)

    changed_kanji = {
        c for c in old_defaults
        if c in new_defaults and old_defaults[c] != new_defaults[c]
    }
    if not changed_kanji:
        print("[OK] no default changes detected")
        sys.exit(0)

    print(f"[info] {len(changed_kanji)} kanji defaults changed between {old_ref} and {new_ref}")

    jukugo = load_jukugo(base)
    regressions = find_regressions(old_defaults, new_defaults, jukugo)

    if not regressions:
        print(f"[OK] no jukugo regressions (checked {len(jukugo)} entries)")
        sys.exit(0)

    print(f"\n[REGRESSION] {len(regressions)} jukugo broken by default changes:\n")
    for surface, expected, old_c, new_c, changed in regressions:
        ch_str = ", ".join(f"{c}: {o} → {n}" for c, o, n in changed)
        print(f"  {surface} = {expected}")
        print(f"    old: {old_c}  new: {new_c}  [{ch_str}]")

    sys.exit(1)


if __name__ == "__main__":
    main()
