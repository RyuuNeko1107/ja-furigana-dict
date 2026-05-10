#!/usr/bin/env python3
"""
全 dict / rule TOML の `[meta]` block に `schema_version = "2"` を bulk 追加する
1 回限りの migration script。 alpha.10 lib (★A1b) で必須化された v2 stamp に
既存 dict を揃えるための機械変換。

対象: `core/**/*.toml` と `rules/**/*.toml` のうち、 `_genre.toml` / `*.test.toml`
は **対象外** (= STATS sub-section meta / CI 専用 inline test、 lib loader 経路に
来ない)。 `tests/corpus/` 配下も対象外 (= 回帰 corpus、 lib に load しない)。

各 file は既に `[meta]` block を持つ前提 (= `add_role_tags.py` 適用済を仮定)。
`[meta]` block が無い file が見つかれば script は **error 終了** (= migration が
不完全な状態で commit されないようにする safe guard)。

冪等性: 既に `schema_version = "2"` が宣言されていれば no-op。 異なる値 (例:
`"1"`、 `"3"` 等) があれば error 終了 (= 上書きしない、 人手判断要)。

走らせ方:
    python tools/migrate_v2.py            # dry-run (差分のみ表示)
    python tools/migrate_v2.py --apply    # 実ファイルに反映

## alpha.10 期 scope

本 script は v2 stamp **のみ** を目的とする。 以下の本格 v2 reorganization は
別 phase (alpha.11 の人手 PR series) で実施:

- `rules/context/*.toml` の `[[rule]]` array → 各 entry の inline
  `[[entries."x".match]]` に migration
- `core/single/*.toml` (単漢字 default reading) → `core/kanji/*.toml` の
  `[[kanji]]` block に format 変換
- `core/single_overrides.toml` → `[[kanji.match]]` block に統合

これらは file 構造そのものの大規模変更を含むので、 機械変換 + 人手 review の
両方が必要。 alpha.11 で別 script (or extension) として実装する。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ─── target schema version ──────────────────────────────────────────────────
TARGET_VERSION = "2"

# ─── 対象判定 ───────────────────────────────────────────────────────────────


def is_target(rel: str) -> bool:
    """rel path がこの migration の対象かどうか。"""
    if rel.endswith("_genre.toml"):
        return False
    if rel.endswith(".test.toml"):
        return False
    if not (rel.startswith("core/") or rel.startswith("rules/")):
        return False
    return True


# ─── meta block 操作 ────────────────────────────────────────────────────────

META_HEADER_RE = re.compile(r"^\[meta\][ \t]*\r?\n", re.M)
SCHEMA_VERSION_RE = re.compile(
    r'^schema_version[ \t]*=[ \t]*"(?P<v>[^"]*)"[ \t]*\r?\n', re.M
)


def find_meta_block(text: str) -> tuple[int, int] | None:
    """`[meta]` block の (header_end_offset, block_end_offset) を返す。

    block_end_offset は次の `[...]` section header の直前 (or EOF)。
    `[meta]` block が無ければ `None`。
    """
    m = META_HEADER_RE.search(text)
    if not m:
        return None
    header_end = m.end()  # `[meta]\n` の直後 (= block 内容の開始)
    # block 終端 = 次の section header 行頭 (or EOF)
    next_section = re.search(r"^\[", text[header_end:], re.M)
    block_end = header_end + (next_section.start() if next_section else len(text) - header_end)
    return header_end, block_end


def update_text(text: str, file_label: str) -> tuple[str, str]:
    """text に `schema_version = "2"` を追加 / 確認する。

    返り値: (new_text, action) — action は "added" / "noop" / 例外時 "error"。

    パターン:
    - `[meta]` 無し → ValueError (caller が error 出力)
    - `schema_version = "2"` 既存 → no-op (text そのまま返す、 action="noop")
    - `schema_version = "X"` (X != "2") → ValueError (上書きしない、 人手判断要)
    - schema_version 行無し → `[meta]` 直後に追加 (action="added")
    """
    pos = find_meta_block(text)
    if pos is None:
        raise ValueError(f"{file_label}: [meta] block が見つからない (= add_role_tags.py 未適用?)")
    header_end, block_end = pos
    meta_block = text[header_end:block_end]

    sm = SCHEMA_VERSION_RE.search(meta_block)
    if sm:
        existing = sm.group("v")
        if existing == TARGET_VERSION:
            return text, "noop"
        raise ValueError(
            f"{file_label}: 既存 schema_version = {existing!r} が target {TARGET_VERSION!r} と "
            "異なる、 上書きしない (人手で確認 / 修正してください)"
        )

    # `[meta]\n` 直後に schema_version 行を挿入 (= block の先頭 field として置く)
    insert = f'schema_version = "{TARGET_VERSION}"\n'
    return text[:header_end] + insert + text[header_end:], "added"


# ─── main ───────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="実ファイルに反映 (default: dry-run)"
    )
    args = parser.parse_args()

    targets: list[Path] = []
    for sub in ("core", "rules"):
        base = ROOT / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.toml")):
            rel = p.relative_to(ROOT).as_posix()
            if is_target(rel):
                targets.append(p)

    added = 0
    noop = 0
    errors: list[str] = []
    for p in targets:
        rel = p.relative_to(ROOT).as_posix()
        original = p.read_text(encoding="utf-8")
        try:
            updated, action = update_text(original, rel)
        except ValueError as e:
            errors.append(str(e))
            continue
        if action == "noop":
            noop += 1
            continue
        added += 1
        if args.apply:
            p.write_text(updated, encoding="utf-8", newline="\n")
        print(f"{'[apply]' if args.apply else '[dry-run]'} {rel} ← schema_version = {TARGET_VERSION!r}")

    print(
        f"\n対象 {len(targets)} file、 追加 {added}、 既設定 {noop}、 error {len(errors)}"
    )
    if errors:
        print("\nerrors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    if not args.apply:
        print("(dry-run、 反映するには --apply を付けて再実行)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
