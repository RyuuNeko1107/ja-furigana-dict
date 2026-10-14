#!/usr/bin/env python3
"""アクセント専用の表 `core/accent/naist.toml` を生成する (offline tool、 2026-10-14)。

`core/accent/unidic.toml` (UniDic 2.1.2 由来、 12.8 万件) に無い語を、 naist-jdic (OpenJTalk の辞書、 約 48 万見出し) の
アクセント (accent/mora) から補う。 lib は `role = "accent"` の file を全部読み、 **表記 + 読みが一致する時だけ** accent を付ける
(読み・区切りには触れない)。

採る語:
  - 名詞 / 副詞 / 連体詞 / 感動詞 / 接続詞 (活用語・助詞・助動詞・接頭辞・接尾辞・非自立・数は除く = 後ろとの結合で核が動く、 または断片)
  - 表記に漢字を含み、 1 字だけの表記は除く (断片になりやすい)
  - 同じ (表記, 読み) の行どうしで核が一致するものだけ (割れたら採らない)
  - unidic.toml に同じ (表記, 読み) があれば採らない (UniDic を優先)

データソース: https://github.com/jpreprocess/naist-jdic (v0.1.3、 naist-jdic.csv)。 License: BSD 3-clause (NAIST、 要出典表記 =
core/accent/LICENSE.NAIST-jdic)。

Usage:
  python tools/gen_accent_naist.py --csv naist-jdic.csv --out core/accent/naist.toml
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
import tomllib
from pathlib import Path

SMALL = set("ャュョァィゥェォヮ")
KANJI = re.compile(r"[㐀-鿿豈-﫿々]")
KATA = re.compile(r"^[ァ-ヴー]+$")
OK_POS = {"名詞", "副詞", "連体詞", "感動詞", "接続詞"}
NG_POS2 = {"接尾", "非自立", "数", "特殊", "接続詞的", "助動詞語幹", "動詞非自立的", "形容動詞語幹"}


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


def existing_keys(path: Path) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    entries = tomllib.loads(path.read_text(encoding="utf-8")).get("entries", {})
    for s, v in entries.items():
        for b in (v if isinstance(v, list) else [v]):
            keys.add((s, b.replace("[", "").replace("]", "")))
    return keys


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--unidic", type=Path, default=Path("core/accent/unidic.toml"))
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    have = existing_keys(a.unidic)
    acc: dict[tuple[str, str], set[int]] = collections.defaultdict(set)
    for r in csv.reader(a.csv.open(encoding="utf-8")):
        if len(r) < 14 or not re.fullmatch(r"\d+/\d+", r[13]):
            continue
        s, pos1, pos2, kana = r[0], r[4], r[5], r[11]
        if pos1 not in OK_POS or pos2 in NG_POS2 or not KATA.match(kana):
            continue
        if not KANJI.search(s) or len(s) < 2 or not re.fullmatch(r"[㐀-鿿豈-﫿々ぁ-ゖァ-ヴー]+", s):
            continue
        acc[(s, kana)].add(int(r[13].split("/")[0]))
    table: dict[str, list[str]] = collections.defaultdict(list)
    n_split = n_dup = 0
    for (s, kana), ts in sorted(acc.items()):
        if (s, kana) in have:
            n_dup += 1
            continue
        if len(ts) != 1:
            n_split += 1
            continue
        b = bracket(kana, next(iter(ts)))
        if b is None:
            continue
        table[s].append(b)

    def q(x: str) -> str:
        return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'

    kept = sum(len(v) for v in table.values())
    lines = [
        "# 自動生成: tools/gen_accent_naist.py (手で編集しない)。 naist-jdic (OpenJTalk の辞書) の accent/mora 由来",
        "# (出典: NAIST、 BSD 3-clause。 core/accent/LICENSE.NAIST-jdic)。 unidic.toml に無い語だけ。 表記 + 読みが一致する token にだけ accent を付ける",
        "",
        "[meta]",
        'schema_version = "2"',
        'role = "accent"',
        'format = "accent/1"',
        f'description = "naist-jdic 由来のアクセント表 ({kept} 件)"',
        "",
        "[entries]",
    ]
    for s in sorted(table):
        v = table[s]
        lines.append(f"{q(s)} = {q(v[0])}" if len(v) == 1 else f"{q(s)} = [{', '.join(q(x) for x in v)}]")
    a.out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[gen_accent_naist] 候補 {len(acc)} / unidic と重複 {n_dup} / 核が割れて除外 {n_split} → {kept} 件 ({len(table)} 表記) → {a.out}")


if __name__ == "__main__":
    main()
