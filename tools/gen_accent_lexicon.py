#!/usr/bin/env python3
"""アクセント専用の表 `core/accent/unidic.toml` を生成する (offline tool、 2026-09-27)。

読みの辞書 entry に bracket notation が無い語 (IPADIC がそのまま切り出す語 / 単漢字規則で読む語) に
アクセントを付けるための表。 lib は `role = "accent"` の file を読み、 **表記 + 読みが一致する時だけ**
accent を付ける (読み・区切りには触れない)。

作り方:
  1. エンジンの token 単位の (表記, 読み, 回数) を集める = **このエンジンが実際に切り出す単位** に合わせる。
     入力は `--tokens` の TSV (表記 TAB 読み TAB 回数、 lib の to_accent の token を数えたもの) が正。
     ruby 出力 (`{表記|よみ}`) も読めるが、 ruby は送り仮名を {} の外に出すので 強い / 違う のような
     送り仮名付きの語が 「強」 としてしか数えられず、 エンジンの token (強い) と一致しない (2026-09-27 に判明)。
     token 入力ならひらがなだけの語 (ちょっと / みんな / めっちゃ 等) も回数で絞る
     (ruby 入力だけの時は UniDic から 2〜6 字を直接採る)。 カタカナ語は数が多いので採らず、 lib の rule 推定 (外来語 -3) に任せる
  2. UniDic (kana-accent 版) の lex.csv で (表記, カナ) を引いて aType を決める。 aType は 「3,0」 のように
     複数並ぶことがある (先頭が第一の型) ので各行の先頭の値を取り、 行どうしで割れたら多数決
     (同数なら採らない = 多分 [名詞 0 / 副詞 1] 等。 動詞 / 形容詞の未然形・連用形を含んで割れる語 [落ち 等] も採らない)。 記号・空白行は除外。 助詞・助動詞を含む語は
     前の語との結合で決まるので採らない
  3. aType を bracket notation の正準形 (ADR-0003) に直す: 0 = 平板 `[よみ`、 n = `[先頭 n モーラ]残り`

データソース: unidic-mecab_kana-accent-2.1.2 の lex.csv (aType = 28 列目)。
  https://clrd.ninjal.ac.jp/unidic_archive/cwj/2.1.2/unidic-mecab_kana-accent-2.1.2_src.zip
  License: GPL/LGPL/BSD トリプルライセンス (BSD 条項で利用、 要出典表記)。

Usage:
  python tools/gen_accent_lexicon.py --lex <lex.csv> --min-count 3 --tokens tokens.tsv --out core/accent/unidic.toml
  (旧) python tools/gen_accent_lexicon.py --lex <lex.csv> --min-count 3 ruby1.txt [ruby2.txt ...]
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
COL_SURFACE, COL_POS1, COL_POS2, COL_CFORM, COL_KANA, COL_ATYPE = 0, 4, 5, 9, 21, 27


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
    ap.add_argument("--tokens", action="append", default=[], help="表記\t読み\t回数 の TSV (複数可)")
    ap.add_argument("ruby", nargs="*")
    a = ap.parse_args()

    cnt: collections.Counter = collections.Counter()
    for p in a.ruby:
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                for m in TOK.finditer(line):
                    s, r = m.group(1), m.group(2)
                    if KANJI.search(s):
                        cnt[(s, to_kata(r))] += 1
    for p in a.tokens:
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                c = line.rstrip("\n").split("\t")
                if len(c) == 3 and c[2].isdigit():
                    cnt[(c[0], to_kata(c[1]))] += int(c[2])

    atypes: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    functional: set[tuple[str, str]] = set()
    inflecting: set[tuple[str, str]] = set()
    with open(a.lex, encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) <= COL_ATYPE or row[COL_POS1] in EXCLUDE_POS1:
                continue
            key = (row[COL_SURFACE], row[COL_KANA])
            if row[COL_POS1] in FUNC_POS1:
                functional.add(key)
            # 未然形 / 連用形 (落ち / 食べ) は後続 (た / て / ない) で核が動く断片
            if row[COL_POS1] in ("動詞", "形容詞") and row[COL_CFORM].startswith(("未然形", "連用形")):
                inflecting.add(key)
            # ひらがな書きの 接尾辞 (ちゃん / たち / っぽい) と 補助動詞 / 形式名詞 (みる / しまう / くれる / こと) は
            # 前の句に付くのが普通。 lib は表に無いひらがな語を直前の句へ連結するので、 表に入れない (2026-09-27)。
            # 漢字の語 (前 / 方 / 中) は名詞としての単独用法が多いので残す
            if HIRA_WORD.match(row[COL_SURFACE]) and (row[COL_POS1] == "接尾辞" or row[COL_POS2] == "非自立可能"):
                functional.add(key)
            t = row[COL_ATYPE].split(",")[0]
            if not t.isdigit():
                continue
            atypes[key].append(t)

    # ruby 入力だけの時は、 ひらがなだけの語が数えられないので UniDic から直接入れる
    # (コーパスの出現回数の代わりに min-count を満たす扱い)。 --tokens があれば token の回数で絞る
    if not a.tokens:
        for key in atypes:
            if HIRA_WORD.match(key[0]) and key not in cnt:
                cnt[key] = a.min_count

    table: dict[str, list[str]] = collections.defaultdict(list)
    kept = 0
    for (s, kana), n in sorted(cnt.items()):
        if n < a.min_count:
            continue
        ts = atypes.get((s, kana))
        if not ts or (s, kana) in functional:
            continue
        top = collections.Counter(ts).most_common(2)
        if len(top) == 2 and (top[0][1] == top[1][1] or (s, kana) in inflecting):
            # 行どうしで割れて同数 = 決められない。 動詞 / 形容詞の未然形・連用形 (落ち / 食べ) は
            # 後続 (た / て / ない) で核が動くので、 割れていたら多数決せず採らない
            continue
        t = top[0][0]
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
