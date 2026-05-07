#!/usr/bin/env python3
"""
core/unihan/*.toml から、 core/compat.toml の異体字 key と重複する entry を
削除する (一度限りの cleanup)。

ja-furigana lib の処理順は:

    1. 異体字正規化 (kana::normalize_text — compat 適用)
    2. 慣用語句先行確定
    3. token 化 + lookup (jukugo / unihan / 等)

つまり「髙」 が入力に来ても Step 1 で「高」 に置換され、 unihan は「高」 だけ
を見る。 unihan に「髙」 entry が残っていても **lib からは到達不可** (dead code)。

ja-furigana-dict v1 系では元 ryuuneko.com seed が compat と unihan の重複を
保持していたため、 411 entries が dead state で残っていた。 本 script で削除。

走らせ方:
    python tools/dedup_unihan_compat.py

冪等性: 既に重複なしなら no-op。
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPAT_TOML = ROOT / "core/compat.toml"
UNIHAN_DIR = ROOT / "core/unihan"

META_DESCRIPTIONS = {
    "joyo.toml":
        "常用漢字 2,136 字 (文化庁 2010-11-30 改訂、 内閣告示) — 利用頻度高、 default reading review 対象",
    "jinmeiyou.toml":
        "人名用漢字 (法務省、 子の名に使用可、 常用と重複する 128 字を除外した残り 855 字)",
    "jis_basic.toml":
        "JIS 基本 (CJK Basic Block U+4E00-U+9FFF のうち常用 / 人名用以外、 概ね JIS X 0208 第1+第2水準カバー)",
    "jis_supplement.toml":
        "JIS 補助 (CJK Extension A + Compatibility Ideographs、 概ね JIS X 0213 第3+第4水準カバー)",
    "extension.toml":
        "拡張漢字 (CJK Extension B 以降、 表外字 / 中国専用字 / 異体字、 機械的扱い、 ほぼ lib lookup されない)",
}


def write_bucket(path: Path, fname: str, entries: dict[str, str]) -> None:
    desc = META_DESCRIPTIONS[fname]
    lines = [
        f"# {desc}",
        "#",
        "# このファイルは tools/classify_unihan.py で水準別自動分類された後、",
        "# tools/fill_missing_unihan.py で seed list の欠落分が KANJIDIC reading で補完され、",
        "# tools/dedup_unihan_compat.py で compat 経由 dead entries が除去された。",
        "# 個別 entry の手動編集は OK (PR で reading 修正等)。",
        "",
        "[meta]",
        f'description = "{desc}"',
        "",
        "[entries]",
    ]
    for k in sorted(entries):
        v = entries[k]
        lines.append(f'"{k}" = "{v}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    with open(COMPAT_TOML, "rb") as f:
        compat_data = tomllib.load(f)
    compat_keys = set(compat_data.get("map", {}).keys())
    print(f"compat keys (異体字): {len(compat_keys):,}")

    grand_total_removed = 0
    for fname in META_DESCRIPTIONS:
        path = UNIHAN_DIR / fname
        with open(path, "rb") as f:
            data = tomllib.load(f)
        entries: dict[str, str] = dict(data.get("entries", {}))
        before = len(entries)
        removed = [k for k in entries if k in compat_keys]
        for k in removed:
            del entries[k]
        if removed:
            write_bucket(path, fname, entries)
        print(f"{fname}: {before:,} → {len(entries):,} (-{len(removed)})")
        grand_total_removed += len(removed)

    print(f"\ntotal removed: {grand_total_removed}")


if __name__ == "__main__":
    main()
