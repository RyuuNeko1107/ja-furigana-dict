#!/usr/bin/env python3
"""UniDic aType → intonation bracket notation 生成 (offline tool、ADR-0006/0003)。

dict の simple entry (`"surface" = "reading"`) を UniDic (kana-accent 版) の
人手監修アクセントデータ (aType) と突合し、bracket notation 付き reading を生成する。
手動アノテーションの置き換え: 生成 → レポート目視 → --apply で書き込み、の 3 段。

データソース: unidic-mecab_kana-accent-2.1.2 の lex.csv (31 列、aType = 28 列目)。
  https://clrd.ninjal.ac.jp/unidic_archive/cwj/2.1.2/unidic-mecab_kana-accent-2.1.2_src.zip
  License: GPL/LGPL/BSD トリプルライセンス (BSD 条項で利用、要出典表記)。

生成規則 (ADR-0003 準拠、canonical form):
  aType=0 (平板)  → "[よみ"          (先頭 [ のみ)
  aType=n (核 n)  → "[よみ...]..."   (先頭 [ + n モーラ目の直後に ])
  reading の script (ひらがな/カタカナ) は dict 原文を保持する。

採用条件 (全部満たす場合のみ生成、それ以外は skip + レポート):
  - surface + 読み (カタカナ正規化) が lex.csv に存在
  - 該当行の aType が全行で一致 (固有名詞・記号行は除外して判定)
  - aType が数値で、読みのモーラ数以下

Usage:
  python tools/gen_accent_brackets.py --lex <path/to/lex.csv> [--apply] \
      [--report accent_brackets_report.tsv] [core/jukugo ...]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 突合から除外する UniDic 行 (pos1 / pos2)
EXCLUDE_POS1 = {"補助記号", "記号", "空白"}
EXCLUDE_POS2 = {"固有名詞"}

# lex.csv (kana-accent 31 列版) の列 index
COL_SURFACE = 0
COL_POS1 = 4
COL_POS2 = 5
COL_KANA = 21
COL_ATYPE = 27

SMALL_KANA = set("ャュョァィゥェォゃゅょぁぃぅぇぉ")

ENTRY_LINE = re.compile(r'^(\s*)"((?:[^"\\]|\\.)+)"\s*=\s*"([^"]*)"\s*(#.*)?$')
SECTION_LINE = re.compile(r"^\s*\[+([^\]]+)\]+\s*(#.*)?$")

HIRA_TO_KATA = {chr(c): chr(c + 0x60) for c in range(0x3041, 0x3097)}


def hira_to_kata(s: str) -> str:
    return "".join(HIRA_TO_KATA.get(c, c) for c in s)


def mora_split(reading: str) -> list[str]:
    """拗音/小書き母音を直前と合算した mora 列 (lib bracket.rs と同一規則)。"""
    out: list[str] = []
    for c in reading:
        if c in SMALL_KANA and out:
            out[-1] += c
        else:
            out.append(c)
    return out


def is_pure_kana(s: str) -> bool:
    return bool(s) and all(
        ("ぁ" <= c <= "ゖ") or ("ァ" <= c <= "ヶ") or c == "ー" for c in s
    )


def bracketize(reading: str, atype: int) -> str | None:
    """dict 原文 script のまま bracket を挿入。不整合 (aType > mora) は None。"""
    morae = mora_split(reading)
    if atype > len(morae):
        return None
    if atype == 0:
        return "[" + reading
    return "[" + "".join(morae[:atype]) + "]" + "".join(morae[atype:])


def load_unidic(
    lex_path: Path, include_proper: bool = False
) -> dict[tuple[str, str], set[str]]:
    """(surface, カタカナ読み) → aType 候補集合。記号行は常に除外。

    `include_proper` で **固有名詞行も採用** する (地名 / 作品名 / 一般化した姓)。
    既定で除外しているのは 「人名の accent は姓名の組み合わせで動くので
    UniDic 単独行を当てても外れる」 ため。 ただし 東京 [0] / 中国 [1] / 関西 [1] /
    博多 [0] のような **地名・固有名詞由来の一般語** は dict 側に entry があり、
    aType が一意なら採用して問題ない (2026-09-13 に 562 件を実測して確認)。
    人名 file (core/jukugo/proper/) は `iter_target_files` 側で除外済み。
    """
    table: dict[tuple[str, str], set[str]] = {}
    with open(lex_path, encoding="utf-8", newline="") as fh:
        for row in csv.reader(fh):
            if len(row) <= COL_ATYPE:
                continue
            if row[COL_POS1] in EXCLUDE_POS1:
                continue
            if not include_proper and row[COL_POS2] in EXCLUDE_POS2:
                continue
            atype = row[COL_ATYPE]
            if not atype or atype == "*":
                continue
            # "0,3" のような複数値は主値 (先頭) を採り、揺れは集合側で検出する
            main = atype.split(",")[0]
            if not main.isdigit():
                continue
            key = (row[COL_SURFACE], row[COL_KANA])
            table.setdefault(key, set()).add(main)
    return table


def iter_target_files(targets: list[str]) -> list[Path]:
    files: list[Path] = []
    for t in targets:
        p = (REPO_ROOT / t).resolve()
        if p.is_file():
            files.append(p)
        else:
            files.extend(sorted(p.rglob("*.toml")))
    # 固有名詞系 file は対象外 (UniDic 固有名詞行を除外しているため突合不能、
    # かつ人名/作品名 accent は別途キュレーションすべき領域)
    return [f for f in files if "proper" not in f.parts and not f.name.startswith("_")]


def process_file(
    path: Path, unidic: dict[tuple[str, str], set[str]], apply: bool
) -> tuple[list[list[str]], Counter, list[str]]:
    rows: list[list[str]] = []
    stats: Counter = Counter()
    out_lines: list[str] = []
    section = ""
    changed = False

    rel = str(path.relative_to(REPO_ROOT))
    for line in path.read_text(encoding="utf-8").splitlines(keepends=False):
        m_sec = SECTION_LINE.match(line)
        if m_sec:
            section = m_sec.group(1).strip()
        m = ENTRY_LINE.match(line) if section == "entries" else None
        if not m:
            out_lines.append(line)
            continue
        indent, surface, reading, comment = m.groups()
        stats["entries"] += 1
        if "[" in reading or "]" in reading:
            stats["already_bracketed"] += 1
            out_lines.append(line)
            continue
        if not is_pure_kana(reading):
            stats["non_kana_reading"] += 1
            out_lines.append(line)
            continue
        key = (surface, hira_to_kata(reading))
        atypes = unidic.get(key)
        if not atypes:
            stats["no_match"] += 1
            rows.append(["no_match", rel, surface, reading, "", ""])
            out_lines.append(line)
            continue
        if len(atypes) > 1:
            stats["ambiguous"] += 1
            rows.append(
                ["ambiguous", rel, surface, reading, ",".join(sorted(atypes)), ""]
            )
            out_lines.append(line)
            continue
        atype = int(next(iter(atypes)))
        new_reading = bracketize(reading, atype)
        if new_reading is None:
            stats["mora_mismatch"] += 1
            rows.append(["mora_mismatch", rel, surface, reading, str(atype), ""])
            out_lines.append(line)
            continue
        # round-trip 安全弁: marker を剥がすと原文 reading に一致すること
        assert new_reading.replace("[", "").replace("]", "") == reading
        stats["generated"] += 1
        rows.append(["ok", rel, surface, reading, str(atype), new_reading])
        if apply:
            tail = f" {comment}" if comment else ""
            out_lines.append(f'{indent}"{surface}" = "{new_reading}"{tail}')
            changed = True
        else:
            out_lines.append(line)

    if apply and changed:
        path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return rows, stats, out_lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lex", required=True, type=Path, help="UniDic kana-accent lex.csv")
    ap.add_argument("--apply", action="store_true", help="TOML を in-place 書き換え")
    ap.add_argument(
        "--include-proper",
        action="store_true",
        help="UniDic の固有名詞行も突合に使う (地名 / 作品名。 人名 file は元々対象外)",
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT / "accent_brackets_report.tsv",
        help="判定レポート TSV の出力先",
    )
    ap.add_argument(
        "targets",
        nargs="*",
        default=["core/jukugo"],
        help="対象 dir / file (repo 相対、default: core/jukugo)",
    )
    args = ap.parse_args()

    print(f"loading UniDic lex: {args.lex}", file=sys.stderr)
    unidic = load_unidic(args.lex, include_proper=args.include_proper)
    print(f"  {len(unidic)} (surface, reading) keys", file=sys.stderr)

    all_rows: list[list[str]] = []
    total: Counter = Counter()
    for f in iter_target_files(args.targets):
        rows, stats, _ = process_file(f, unidic, args.apply)
        all_rows.extend(rows)
        total.update(stats)

    with open(args.report, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["status", "file", "surface", "reading", "atype", "bracketed"])
        w.writerows(all_rows)

    print(f"\n== summary ({'apply' if args.apply else 'dry-run'}) ==")
    for k in (
        "entries",
        "generated",
        "no_match",
        "ambiguous",
        "mora_mismatch",
        "non_kana_reading",
        "already_bracketed",
    ):
        print(f"  {k:18} {total.get(k, 0)}")
    print(f"  report → {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
