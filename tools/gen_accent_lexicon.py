#!/usr/bin/env python3
"""アクセント専用の表 `core/accent/unidic.toml` を生成する (offline tool、 2026-09-27)。

読みの辞書 entry に bracket notation が無い語 (IPADIC がそのまま切り出す語 / 単漢字規則で読む語) に
アクセントを付けるための表。 lib は `role = "accent"` の file を読み、 **表記 + 読みが一致する時だけ**
accent を付ける (読み・区切りには触れない)。

作り方:
  1. エンジンのふりがな出力 (`batch-read --mode ruby`、 `{表記|よみ}` 形式) と ruby の外に残るかな列から、
     token の (表記, 読み) と出現回数を集める = **このエンジンが実際に切り出す単位** に合わせる。
     ruby 出力で {} が付くのは漢字を含む語だけなので、 ひらがなだけの語 (ちょっと / みんな / めっちゃ 等) は
     コーパスで絞らず UniDic から直接採る (2〜6 字、 助詞・助動詞は除く)。 カタカナ語は数が多いので採らず、
     lib の rule 推定 (外来語 -3) に任せる
  2. UniDic (kana-accent 版) の lex.csv で (表記, カナ) を引き、 aType が全行で一致するものだけ採る
     (記号・空白行は除外。 aType が複数に割れる語は採らない。 助詞・助動詞を含む語は前の語との結合で
     決まるので採らない)
  3. aType を bracket notation の正準形 (ADR-0003) に直す: 0 = 平板 `[よみ`、 n = `[先頭 n モーラ]残り`

データソース: unidic-mecab_kana-accent-2.1.2 の lex.csv (aType = 28 列目)。
  https://clrd.ninjal.ac.jp/unidic_archive/cwj/2.1.2/unidic-mecab_kana-accent-2.1.2_src.zip
  License: GPL/LGPL/BSD トリプルライセンス (BSD 条項で利用、 要出典表記)。

Usage:
  python tools/gen_accent_lexicon.py --lex <lex.csv> --min-count 3 --out core/accent/unidic.toml ruby1.txt [ruby2.txt ...]
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
from pathlib import Path

TOK = re.compile(r"\{([^|{}]+)\|([^{}]*)\}")
KANJI = re.compile(r"[㐀-鿿豈-﫿々]")
SMALL = set("ャュョァィゥェォヮ")
EXCLUDE_POS1 = {"補助記号", "記号", "空白"}
FUNC_POS1 = {"助詞", "助動詞"}  # 前の語との結合で決まる (表に入れない)
HIRA_WORD = re.compile(r"^[ぁ-ゖー]{2,6}$")
# lex.csv (kana-accent 31 列版) の列 index
COL_SURFACE, COL_POS1, COL_KANA, COL_ATYPE = 0, 4, 21, 27


def to_kata(s: str) -> str:
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s).replace("[", "").replace("]", "")


def morae(kana: str) -> list[str]:
    out: list[str] = []
    for c in kana:
        if c in SMALL and out:
            out[-1] += c
        else:
            out.append(c)
    return out


def bracket(kana: str, atype: int) -> str | None:
    m = morae(kana)
    if atype == 0:
        return "[" + kana
    if not 1 <= atype <= len(m):
        return None
    return "[" + "".join(m[:atype]) + "]" + "".join(m[atype:])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lex", required=True)
    ap.add_argument("--min-count", type=int, default=3)
    ap.add_argument("--out", default="core/accent/unidic.toml")
    ap.add_argument("ruby", nargs="+")
    a = ap.parse_args()

    cnt: collections.Counter = collections.Counter()
    for p in a.ruby:
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                for m in TOK.finditer(line):
                    s, r = m.group(1), m.group(2)
                    if KANJI.search(s):
                        cnt[(s, to_kata(r))] += 1

    atypes: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    functional: set[tuple[str, str]] = set()
    with open(a.lex, encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) <= COL_ATYPE or row[COL_POS1] in EXCLUDE_POS1:
                continue
            key = (row[COL_SURFACE], row[COL_KANA])
            if row[COL_POS1] in FUNC_POS1:
                functional.add(key)
            t = row[COL_ATYPE]
            if t in ("*", ""):
                continue
            atypes[key].add(t)

    # ひらがなだけの語は UniDic から直接 (コーパスの出現回数の代わりに min-count を満たす扱い)
    for key in atypes:
        if HIRA_WORD.match(key[0]) and key not in cnt:
            cnt[key] = a.min_count

    table: dict[str, list[str]] = collections.defaultdict(list)
    kept = 0
    for (s, kana), n in sorted(cnt.items()):
        if n < a.min_count:
            continue
        ts = atypes.get((s, kana))
        if not ts or len(ts) != 1 or (s, kana) in functional:
            continue
        t = next(iter(ts))
        if not t.isdigit():
            continue
        b = bracket(kana, int(t))
        if b is None:
            continue
        table[s].append(b)
        kept += 1

    def q(x: str) -> str:
        return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'

    lines = [
        "# 自動生成: tools/gen_accent_lexicon.py (手で編集しない)。 UniDic kana-accent 2.1.2 の aType 由来",
        "# (出典: 国立国語研究所 UniDic、 BSD 条項で利用)。 表記 + 読みが一致する token にだけ accent を付ける",
        "",
        "[meta]",
        'schema_version = "2"',
        'role = "accent"',
        f'description = "UniDic aType 由来のアクセント表 ({kept} 件)"',
        "",
        "[entries]",
    ]
    for s in sorted(table):
        v = table[s]
        lines.append(f"{q(s)} = {q(v[0])}" if len(v) == 1 else f"{q(s)} = [{', '.join(q(x) for x in v)}]")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[gen_accent_lexicon] tokens {len(cnt)} → {kept} 件 ({len(table)} 表記) → {out}")


if __name__ == "__main__":
    main()
