#!/usr/bin/env python3
"""
core/unihan/joyo.toml と core/unihan/jinmeiyou.toml の欠落字を補完する。

入力 source:
- `tools/seed/jouyou.txt` (常用 2,136) / `jinmeiyou.txt` (人名用 983 → 常用と
  重複 128 を除いた残り 855)
- `tools/seed/kanji.json` (davidluzgouveia/kanji-data、 KANJIDIC ベース 13,108 字)

reading 選択ロジック (既存 unihan の慣習に合わせる):
1. `readings_kun[0]` があれば → 送り仮名分離記号 `.` / `-` を除去した ひらがな
   (例: 「俺」 KANJIDIC kun = "おれ" → "おれ"、 「与」 kun = "あた.える" → "あたえる")
2. なければ `readings_on[0]` → ひらがな → カタカナ変換
   (例: 「三」 KANJIDIC on = "さん" → "サン")
3. KANJIDIC に entry 自体が無い、 もしくは reading が 1 つもないものは skip
   (manually fill 案件として stderr に list)

冪等性: 既に entry があれば touch せず、 missing 分だけ追加する。

走らせ方:
    python tools/fill_missing_unihan.py
"""
from __future__ import annotations

import json
import sys
import tomllib
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = ROOT / "tools/seed"

META_DESCRIPTIONS = {
    "joyo.toml":
        "常用漢字 2,136 字 (文化庁 2010-11-30 改訂、 内閣告示) — 利用頻度高、 default reading review 対象",
    "jinmeiyou.toml":
        "人名用漢字 (法務省、 子の名に使用可、 常用と重複する 128 字を除外した残り 855 字)",
}


def hira_to_kata(s: str) -> str:
    return "".join(
        chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s
    )


def normalize_kun(s: str) -> str:
    """`.` と `-` (送り仮名分離 / 連濁マーク) を除いた ひらがな読み。"""
    return s.replace(".", "").replace("-", "")


def pick_reading(entry: dict) -> str | None:
    kun = entry.get("readings_kun") or []
    if kun:
        return normalize_kun(kun[0])
    on = entry.get("readings_on") or []
    if on:
        return hira_to_kata(on[0])
    return None


def write_bucket(path: Path, fname: str, entries: dict[str, str]) -> None:
    desc = META_DESCRIPTIONS[fname]
    lines = [
        f"# {desc}",
        "#",
        "# このファイルは tools/classify_unihan.py で水準別自動分類された後、",
        "# tools/fill_missing_unihan.py で seed list の欠落分が KANJIDIC reading で補完された。",
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


def fill(target_file: str, seed_chars: set[str], kanji_data: dict) -> tuple[int, int, list[str]]:
    """target_file に seed_chars の欠落分を kanji_data から補完する。
    戻り値: (元 entries 数, 追加 entries 数, reading 取得失敗 char list)。"""
    path = ROOT / "core/unihan" / target_file
    with open(path, "rb") as f:
        data = tomllib.load(f)
    entries: dict[str, str] = dict(data.get("entries", {}))
    initial = len(entries)
    missing = seed_chars - set(entries.keys())
    failed: list[str] = []
    added = 0
    for c in sorted(missing):
        reading = None
        kdata = kanji_data.get(c)
        if kdata:
            reading = pick_reading(kdata)
        # CJK Compatibility Ideographs (U+F900-U+FAFF 等) は NFKC で base form
        # に正規化すると本来の漢字 (U+4E00-U+9FFF) になり、 reading を引ける。
        if reading is None:
            base = unicodedata.normalize("NFKC", c)
            if base != c and base in kanji_data:
                reading = pick_reading(kanji_data[base])
        if reading is None:
            failed.append(c)
            continue
        entries[c] = reading
        added += 1
    write_bucket(path, target_file, entries)
    return initial, added, failed


def main() -> None:
    joyo_seed = set((SEED_DIR / "jouyou.txt").read_text(encoding="utf-8").strip())
    jin_seed_all = set((SEED_DIR / "jinmeiyou.txt").read_text(encoding="utf-8").strip())
    jin_seed_only = jin_seed_all - joyo_seed
    with open(SEED_DIR / "kanji.json", encoding="utf-8") as f:
        kanji_data = json.load(f)

    print(f"KANJIDIC entries: {len(kanji_data):,}")

    for target, seed in (("joyo.toml", joyo_seed), ("jinmeiyou.toml", jin_seed_only)):
        initial, added, failed = fill(target, seed, kanji_data)
        print(f"{target}: {initial:,} → {initial + added:,} (+{added})")
        if failed:
            failed_str = "".join(failed)
            print(f"  reading 取得失敗 ({len(failed)} chars): {failed_str}", file=sys.stderr)


if __name__ == "__main__":
    main()
