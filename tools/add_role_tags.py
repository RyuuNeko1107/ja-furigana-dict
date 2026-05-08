#!/usr/bin/env python3
"""
全 dict / rule TOML の `[meta]` block に `role = "..."` を bulk 追加する。
1 回限りの migration script (CI では走らせない)。

役割: 各 file が自分で「どの role に属するか」 を declare する。 lib loader を
将来 role 駆動に切り替えたとき、 file path / 名前依存を壊しても動くようにする
foundation。 今回時点では lib は role を silent skip (entries / map / 各 rule
schema 外の `[meta]` field は serde で無視) なので、 機能変化は無い。

役割と path の対応 (ROLE_BY_PATH):

- core/unihan/*.toml         → "unihan"
- core/jukugo/<...>/*.toml   → "jukugo"
- core/works/<...>/*.toml    → "works"
- core/loanwords/*.toml      → "loanwords"
- core/single_overrides.toml → "single_overrides"
- core/compat.toml           → "compat"
- rules/counters/*.toml      → "counters"
- rules/context/*.toml       → "context"
- rules/days.toml            → "days"
- rules/scales.toml          → "scales"
- rules/units.toml           → "units"
- rules/symbols.toml         → "symbols"
- rules/latin.toml           → "latin"
- rules/numeric_phrases.toml → "numeric_phrases"
- rules/postprocess.toml     → "postprocess"

`_genre.toml` / `*.test.toml` は role 対象外 (= スキップ)。

走らせ方:
    python tools/add_role_tags.py            # dry-run (差分のみ表示)
    python tools/add_role_tags.py --apply    # 実ファイルに反映

冪等性: 既に role が正しく declare されていれば no-op。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def role_for(rel: str) -> str | None:
    """rel path → role 名 (or 対象外なら None)。"""
    if rel.endswith("_genre.toml") or rel.endswith(".test.toml"):
        return None
    # rules/days.toml は flat top-level (`'1' = 'ツイタチ'`) 構造で、
    # [meta] block を入れると lib の DaysData (HashMap<String, String>)
    # が「meta key の value が map で string でない」 で deserialize fail する。
    # 短期的に role tag 対象外扱い、 file 名識別を維持。
    if rel == "rules/days.toml":
        return None
    if rel == "core/single_overrides.toml":
        return "single_overrides"
    if rel == "core/compat.toml":
        return "compat"
    if rel.startswith("core/unihan/"):
        return "unihan"
    if rel.startswith("core/jukugo/"):
        return "jukugo"
    if rel.startswith("core/works/"):
        return "works"
    if rel.startswith("core/loanwords/"):
        return "loanwords"
    if rel.startswith("rules/counters/"):
        return "counters"
    if rel.startswith("rules/context/"):
        return "context"
    flat_rules = {
        "rules/days.toml": "days",
        "rules/scales.toml": "scales",
        "rules/units.toml": "units",
        "rules/symbols.toml": "symbols",
        "rules/latin.toml": "latin",
        "rules/numeric_phrases.toml": "numeric_phrases",
        "rules/postprocess.toml": "postprocess",
    }
    return flat_rules.get(rel)


META_BLOCK_RE = re.compile(r"^\[meta\]\s*$", re.M)
ROLE_LINE_RE = re.compile(r"^role\s*=\s*\"(?P<v>[^\"]*)\"\s*$", re.M)


def update_text(text: str, role: str) -> str:
    """text に `[meta] role = "..."` を追加 / 更新する。

    パターン:
    - `[meta]` block あり + `role = ...` あり → value 更新 (冪等)
    - `[meta]` block あり + `role = ...` 無し → block 内に role 行を挿入
    - `[meta]` block 無し → file 先頭 (最初の non-comment 行 直前) に新規 block を追加
    """
    m = META_BLOCK_RE.search(text)
    if m:
        # [meta] block 内 (= [meta] 行から次の [...] 行 or EOF まで) に role= があるか
        meta_start = m.end()
        next_section = re.search(r"^\[", text[meta_start:], re.M)
        meta_end = meta_start + (next_section.start() if next_section else len(text) - meta_start)
        meta_block = text[meta_start:meta_end]
        rm = ROLE_LINE_RE.search(meta_block)
        if rm:
            # value 更新
            new_block = ROLE_LINE_RE.sub(f'role = "{role}"', meta_block, count=1)
        else:
            # role 行を [meta] 直後に追加 (description より前)
            new_block = f'\nrole = "{role}"' + meta_block
        return text[:meta_start] + new_block + text[meta_end:]

    # [meta] block 無し: 先頭 comment block の直後に新規 [meta] を追加
    # 戦略: file 先頭から `^[#\s]` で始まる行をスキップして最初の non-comment 行直前に挿入
    lines = text.splitlines(keepends=True)
    insert_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            insert_idx = i + 1
            continue
        break
    new_block = f'\n[meta]\nrole = "{role}"\n\n'
    return "".join(lines[:insert_idx]) + new_block + "".join(lines[insert_idx:])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="実ファイルに反映 (default: dry-run)")
    args = parser.parse_args()

    targets: list[Path] = []
    for sub in ("core", "rules"):
        base = ROOT / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.toml")):
            targets.append(p)

    changed = 0
    skipped = 0
    for p in targets:
        rel = p.relative_to(ROOT).as_posix()
        role = role_for(rel)
        if role is None:
            skipped += 1
            continue
        original = p.read_text(encoding="utf-8")
        updated = update_text(original, role)
        if updated == original:
            continue
        changed += 1
        if args.apply:
            p.write_text(updated, encoding="utf-8", newline="\n")
        print(f"{'[apply]' if args.apply else '[dry-run]'} {rel} ← role={role!r}")

    print(f"\n対象 {len(targets)} file、 変更 {changed}、 skip {skipped}")
    if not args.apply:
        print("(dry-run、 反映するには --apply を付けて再実行)")


if __name__ == "__main__":
    main()
