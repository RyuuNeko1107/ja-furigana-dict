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

OpenJTalk 優先の上書き表 (2026-10-18、 user 決定「アクセントの質は OpenJTalk に寄せる」):
  python tools/gen_accent_naist.py --csv naist-jdic.csv --override --out core/accent/naist_override.toml
  unidic.toml と (表記, 読み) が重なり、 核が naist-jdic と食い違う語だけを出す (naist 側で核が割れる語は除く)。
  lib は同じキーを先勝ちで読み、 ファイル名順に読むので、 naist_override.toml (n) は unidic.toml (u) より前になる。
  実文 4,000 行の OpenJTalk との比較で、 全句の核の一致 70.2% → 78.7%、 句ごと 88.6% → 92.1%。
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
OVERRIDE_EXTRA_POS = {"動詞", "形容詞"}
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


def unidic_nuclei(path: Path) -> dict[tuple[str, str], set[int]]:
    """unidic.toml の (表記, 読み) -> 核位置の集合 (0 = 平板)"""
    out: dict[tuple[str, str], set[int]] = collections.defaultdict(set)
    entries = tomllib.loads(path.read_text(encoding="utf-8")).get("entries", {})
    for s, v in entries.items():
        for b in (v if isinstance(v, list) else [v]):
            reading = b.replace("[", "").replace("]", "")
            nuc = 0 if "]" not in b else len(morae(b.split("]")[0].replace("[", "")))
            out[(s, reading)].add(nuc)
    return out


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
    ap.add_argument(
        "--override",
        action="store_true",
        help="unidic.toml と (表記, 読み) が重なる語のうち、 核が naist-jdic (OpenJTalk) と食い違うものだけを出す "
        "(OpenJTalk 優先。 lib は同じキーを先勝ちで読むので、 ファイル名が unidic.toml より前の表に置く)",
    )
    a = ap.parse_args()
    have = existing_keys(a.unidic)
    uni = unidic_nuclei(a.unidic) if a.override else {}
    acc: dict[tuple[str, str], set[int]] = collections.defaultdict(set)
    for r in csv.reader(a.csv.open(encoding="utf-8")):
        if len(r) < 14 or not re.fullmatch(r"\d+/\d+", r[13]):
            continue
        s, pos1, pos2, kana = r[0], r[4], r[5], r[11]
        # 上書き表 (--override) は 動詞 / 形容詞 の辞書形も対象 (lib が活用形の核を辞書形から導くため。 UniDic の おいしい = 平板 を OJT の 3 型にする等)
        pos_ok = OK_POS | OVERRIDE_EXTRA_POS if a.override else OK_POS
        if pos1 not in pos_ok or pos2 in NG_POS2 or not KATA.match(kana):
            continue
        if a.override:
            if (s, kana) not in have or not re.fullmatch(r"[㐀-鿿豈-﫿々ぁ-ゖァ-ヴー]+", s):
                continue
        elif not KANJI.search(s) or len(s) < 2 or not re.fullmatch(r"[㐀-鿿豈-﫿々ぁ-ゖァ-ヴー]+", s):
            continue
        acc[(s, kana)].add(int(r[13].split("/")[0]))
    table: dict[str, list[str]] = collections.defaultdict(list)
    n_split = n_dup = 0
    n_same = 0
    for (s, kana), ts in sorted(acc.items()):
        if a.override:
            if len(ts) != 1:
                n_split += 1
                continue
            nuc = next(iter(ts))
            if uni.get((s, kana)) == {nuc}:
                n_same += 1  # UniDic と同じ核 (上書き不要)
                continue
        elif (s, kana) in have:
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
    ov = "# ★上書き表 (--override): unidic.toml と (表記, 読み) が重なり核が食い違う語を naist-jdic (OpenJTalk) の核にする。 lib は同じキーを先勝ちで読むので unidic.toml より前に読まれる名前にする" if a.override else ""
    lines = ([ov] if a.override else []) + [
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
    if a.override:
        print(f"[gen_accent_naist --override] 候補 {len(acc)} / UniDic と同じ核 {n_same} / naist 側で核が割れて除外 {n_split} → 上書き {kept} 件 → {a.out}")
        return
    print(f"[gen_accent_naist] 候補 {len(acc)} / unidic と重複 {n_dup} / 核が割れて除外 {n_split} → {kept} 件 ({len(table)} 表記) → {a.out}")


if __name__ == "__main__":
    main()
