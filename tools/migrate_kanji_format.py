#!/usr/bin/env python3
"""
core/single_overrides.toml の [entries] を core/kanji/overrides.toml の
[[kanji]] block format に機械変換 (★A2 alpha.11 dict 完全再編成 第 4 段、
旧 single_overrides → 新 [[kanji]] block への移行)。

## 設計

旧 format (`core/single_overrides.toml`):
```toml
[entries]
"土" = "ツチ"
```

新 format (`core/kanji/overrides.toml`):
```toml
[[kanji]]
char = "土"
default = "ツチ"
```

`[[kanji]]` block は文脈分岐 reading (= `[[kanji.match]]` array) も持てるが、
現 single_overrides.toml の entries は context 条件無しの単純 default override
のみなので、 `[[kanji.match]]` は付けない。

## scope

- 旧 `single_overrides.toml` は **保持** (= alpha.11 期間中は lib Strict engine
  が引き続き Step 4.5 で使う後方互換維持)
- 新 `core/kanji/overrides.toml` を **追加** (= forward-ready、 lib Smart engine
  の `[[kanji]]` block loader が wire-up され次第 active 化、 alpha.12+ 想定)
- 0.1.0-rc1 で Smart engine default 切替後に `single_overrides.toml` 削除

冪等性: `core/kanji/overrides.toml` 既存なら overwrite せず error 終了。

走らせ方:
    python tools/migrate_kanji_format.py            # dry-run
    python tools/migrate_kanji_format.py --apply    # 実 file 作成
"""
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "core" / "single_overrides.toml"
TARGET_DIR = ROOT / "core" / "kanji"
TARGET = TARGET_DIR / "overrides.toml"


def emit_kanji_blocks(entries: dict[str, str]) -> str:
    """`{ char: reading, ... }` を `[[kanji]]` block の TOML 文字列に整形。"""
    if not entries:
        return ""
    lines: list[str] = []
    # 50 音順 ソート (= PR diff 整合)
    for char in sorted(entries.keys()):
        reading = entries[char]
        lines.append("[[kanji]]")
        lines.append(f'char = "{char}"')
        lines.append(f'default = "{reading}"')
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="実 file に書き込み")
    args = parser.parse_args()

    if not SOURCE.is_file():
        print(f"error: {SOURCE} not found", file=sys.stderr)
        return 1

    if TARGET.exists():
        print(
            f"error: {TARGET.relative_to(ROOT).as_posix()} 既存、 idempotent 重複防止のため "
            f"abort (= 既に migration 適用済の可能性)",
            file=sys.stderr,
        )
        return 1

    src_data = tomllib.loads(SOURCE.read_text(encoding="utf-8"))
    entries = src_data.get("entries", {})
    if not isinstance(entries, dict):
        print(f"error: {SOURCE} の [entries] が dict ではない", file=sys.stderr)
        return 1

    # 1 字 surface のみ ([[kanji]] は char field が単漢字必須)
    valid: dict[str, str] = {}
    skipped: list[str] = []
    for k, v in entries.items():
        if not isinstance(v, str):
            skipped.append(f"{k!r}: value が string ではない (型 {type(v).__name__})")
            continue
        if len(k) != len(k.encode("utf-8")) // 3 if False else True:
            # 単純に文字数 (= len with grapheme caveat だが日本語の漢字は基本 BMP)
            char_count = len(k)
            if char_count != 1:
                skipped.append(f"{k!r}: 1 字 surface ではない ({char_count} 字)")
                continue
        valid[k] = v

    if not valid:
        print(f"warning: {SOURCE} に有効 entry なし、 何も migration しない")
        return 0

    print(f"source: {SOURCE.relative_to(ROOT).as_posix()}")
    print(f"target: {TARGET.relative_to(ROOT).as_posix()}")
    print(f"  valid entries: {len(valid)}")
    if skipped:
        print(f"  skipped: {len(skipped)}")
        for s in skipped:
            print(f"    - {s}")

    output = (
        f"# 単漢字 default reading override (旧 single_overrides.toml の後継、 ★A2 alpha.11)\n"
        f"#\n"
        f"# `[[kanji]]` block 形式で書く: 各 block は `char` (1 字 surface 必須) と\n"
        f"# `default` reading、 文脈分岐が要る場合は `[[kanji.match]]` block 配列を持つ\n"
        f"# (matcher vocabulary は entry inline match と完全同一)。\n"
        f"#\n"
        f"# ## migration note\n"
        f"#\n"
        f"# `core/single_overrides.toml` から機械変換 (★A2 alpha.11、 `tools/migrate_kanji_format.py`)。\n"
        f"# alpha.11 期間中は **両 file が duplicate 共存** (= Strict engine は旧 file、 Smart\n"
        f"# engine は新 file)、 0.1.0-rc1 で Smart default 切替後に旧 file 削除可能。\n"
        f"#\n"
        f"# 関連 issue: <https://github.com/RyuuNeko1107/ja-furigana/issues/15>\n"
        f"\n"
        f'[meta]\n'
        f'schema_version = "2"\n'
        f'role = "kanji"\n'
        f'description = "単漢字 default override + 文脈分岐 reading (★A2 alpha.11、 旧 single_overrides の後継)"\n'
        f"\n"
    ) + emit_kanji_blocks(valid)

    if args.apply:
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(output, encoding="utf-8", newline="\n")
        print(f"\n[apply] wrote {TARGET.relative_to(ROOT).as_posix()}")
    else:
        print()
        print("=== output preview ===")
        print(output)
        print("=== end ===")
        print("(dry-run、 反映するには --apply を付けて再実行)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
