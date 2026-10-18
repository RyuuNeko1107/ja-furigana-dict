#!/usr/bin/env python3
"""活用語の語単体の核を、 原形つきで引ける表 `core/accent/chain_words_conj.toml` に起こす (2026-10-19、 offline tool)。

`chain_words.toml` は (表記, 読み, 品詞1) → 核/拍数 で、 同じ綴りで核が割れる語 (たべ = 食べる 2 型 / 食ぶ 1 型、 つけ = つける / つく …) は
採っていない。 Lindera (IPADIC) の形態素は原形 (base form) を持つので、 動詞 / 形容詞 の活用形は (表記, 読み, 品詞1, 原形) で一意に引ける。
lib は 「表記,読み,品詞1,原形」 の key (words セクションの第 3 フィールドに `品詞1,原形`) を最初に引く。

対象: 同じ (表記, 読み, 品詞1) で原形ごとに核が異なる動詞 / 形容詞 だけ。 同じ原形の中で核が割れるもの (活用形ごとに別) は採らない。
データソース: naist-jdic.csv (BSD 3-clause、 core/accent/LICENSE.NAIST-jdic)。

Usage:
  python tools/gen_accent_chain_conj.py --csv naist-jdic.csv --out core/accent/chain_words_conj.toml
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
from pathlib import Path

KATA = re.compile(r"^[ァ-ヴー]+$")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    by_key: dict[tuple[str, str, str], dict[str, set[str]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in csv.reader(a.csv.open(encoding="utf-8")):
        if len(r) < 14 or r[4] not in ("動詞", "形容詞") or not re.fullmatch(r"\d+/\d+", r[13]) or not KATA.match(r[11]):
            continue
        by_key[(r[0], r[11], r[4])][r[10]].add(r[13])
    rows = []
    for (s, rd, p1), by_orig in by_key.items():
        cores = {next(iter(v)) for v in by_orig.values() if len(v) == 1}
        if len(by_orig) < 2 or len(cores) < 2:
            continue  # 原形が 1 つ / 原形が違っても核は同じ → 既存の表で足りる
        for orig, v in by_orig.items():
            if len(v) == 1:
                rows.append((f"{s},{rd},{p1},{orig}", next(iter(v))))
    rows.sort()

    def q(x: str) -> str:
        return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'

    lines = [
        "# 自動生成: tools/gen_accent_chain_conj.py (手で編集しない)。 naist-jdic (OpenJTalk の辞書) 由来。",
        "# 同じ (表記, 読み, 品詞1) で原形ごとに核が違う動詞 / 形容詞の活用形を、 原形つきで引く表。 key = 表記,読み,品詞1,原形 (lib は words セクションの第 3 フィールドとして読む)",
        "",
        "[meta]",
        'schema_version = "2"',
        'role = "accent_chain"',
        'format = "accent_chain/1"',
        f'description = "原形つきの活用語の核 ({len(rows)} 件)"',
        "",
        "[words]",
    ]
    for k, v in rows:
        lines.append(f"{q(k)} = {q(v)}")
    a.out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[gen_accent_chain_conj] {len(rows)} 件 -> {a.out}")


if __name__ == "__main__":
    main()
