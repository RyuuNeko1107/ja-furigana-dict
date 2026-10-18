#!/usr/bin/env python3
"""NAIST の複数部品の辞書語 (感動詞 / 副詞 / 接続詞) を、 token 単位の分割表 `core/accent/chain_splits_compound.toml` に起こす (2026-10-19)。

naist-jdic.csv の読みが `ありがとう:ございました` のように `:` で区切られた語は、 OpenJTalk では部品ごとに別の語 (別のアクセント句になりうる)
として扱われる。 Lindera (IPADIC) はこれを 1 語にしない (ありがとう / ござい / まし / た) ので、 lib が token の表記全体で引く。
キー = 「表記,品詞1,複合」 (品詞2 を 「複合」 にして `chain_splits.toml` の語と区別する。 lib は複合の方だけ 2 番目以降の部品を別の句にする)、 値 = 部品 (表記,読み,品詞1,品詞2,連用,核/拍数,結合型) を `;` でつないだもの
(`core/accent/chain_splits.toml` と同じ形)。 内容語の名詞 / 動詞は結合型の既定が絡むので、 感動詞 / 副詞 / 接続詞だけ。

Usage:
  python tools/gen_accent_compound_splits.py --csv naist-jdic.csv --out core/accent/chain_splits_compound.toml
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

POS = {"感動詞", "副詞", "接続詞"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    rows = []
    for r in csv.reader(a.csv.open(encoding="utf-8")):
        if len(r) < 15 or ":" not in r[11] or r[4] not in POS:
            continue
        surf = r[0]
        parts_s, parts_r, parts_a = r[10].split(":"), r[11].split(":"), r[13].split(":")
        if not (len(parts_s) == len(parts_r) == len(parts_a) >= 2):
            continue
        # 結合型: C1 などが付いていればそのまま、 -1 / * は 「*」
        rule = r[14] if r[14] in {"C1", "C2", "C3", "C4", "C5"} else "*"
        parts = []
        for s, rd, ac in zip(parts_s, parts_r, parts_a):
            parts.append(f"{s},{rd},{r[4]},{r[5]},0,{ac},{rule}")
        rows.append((f"{surf},{r[4]},複合", ";".join(parts)))
    rows.sort()
    lines = [
        "# 自動生成: tools/gen_accent_compound_splits.py (手で編集しない)。 naist-jdic で 1 語が複数部品になる感動詞 / 副詞 / 接続詞の分割表。",
        "# 出典: naist-jdic (BSD 3-clause、 core/accent/LICENSE.NAIST-jdic)。 キー = 表記,品詞1,品詞2、 部品 = 表記,読み,品詞1,品詞2,連用(0/1),核/拍数,結合型 (部品どうしは ;)",
        "",
        "[meta]",
        'schema_version = "2"',
        'role = "accent_chain"',
        'format = "accent_chain/1"',
        f'description = "複数部品の感動詞などの分割表 ({len(rows)} 件)"',
        "",
        "[splits]",
    ]
    for k, v in rows:
        lines.append(f'"{k}" = "{v}"')
    a.out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[gen_accent_compound_splits] {len(rows)} 件 -> {a.out}")


if __name__ == "__main__":
    main()
