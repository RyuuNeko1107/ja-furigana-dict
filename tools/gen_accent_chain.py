#!/usr/bin/env python3
"""アクセント句の連結規則 (OpenJTalk の accent rule) のデータ表を生成する (offline tool、 2026-10-14)。

lib の `accent_chain` が アクセント句の組み立てとアクセント結合に使う 2 つの表を、 naist-jdic (OpenJTalk の辞書) から作る:

  core/accent/chain.toml            付属語 (助詞 / 助動詞) と 接尾 / 非自立 の全件 + 内容語の品詞ごとの既定の結合型
  core/accent/chain_exceptions.toml 内容語のうち 品詞の既定と違う結合型を持つ語だけ (約 18%)。 メモリを節約したい時はこの file を除外できる
  core/accent/chain_words.toml      語単体の核 (表記 + 読み + 品詞1 → 核/拍数)。 連結規則専用。 活用形・ひらがな語・外来語も含む全品詞

どちらも `role = "accent_chain"`。 キーは 「表記,読み,品詞1,品詞2」 (カンマ区切り、 読みは IPADIC / naist のカタカナ)。 lib は
Lindera の品詞と読みで引く。 値の結合型は naist-jdic の文字列 (`C1` / `動詞%F4@1/助詞%F2@1` 等) のまま。

データソース: https://github.com/jpreprocess/naist-jdic (v0.1.3、 naist-jdic.csv、 BSD 3-clause = core/accent/LICENSE.NAIST-jdic)。

Usage:
  python tools/gen_accent_chain.py --csv naist-jdic.csv --out-dir core/accent
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
import tomllib
from pathlib import Path

KATA = re.compile(r"^[ァ-ヴー]+$")


def is_functional(r: list[str]) -> bool:
    return r[4] in ("助詞", "助動詞") or (r[4] in ("名詞", "動詞", "形容詞") and r[5] in ("接尾", "非自立"))


def q(x: str) -> str:
    return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    a = ap.parse_args()
    # すでに core/accent/unidic.toml / naist.toml にある (表記, 読み) は 語単体の核の表から外す (重複を持たない)
    have: set[tuple[str, str]] = set()
    for name in ("unidic", "naist"):
        f = a.out_dir / f"{name}.toml"
        if f.exists():
            for sfc, v in tomllib.loads(f.read_text(encoding="utf-8")).get("entries", {}).items():
                for b in v if isinstance(v, list) else [v]:
                    have.add((sfc, b.replace("[", "").replace("]", "")))
    rows = [r for r in csv.reader(a.csv.open(encoding="utf-8")) if len(r) >= 15 and re.fullmatch(r"\d+/\d+", r[13])]
    for r in rows:
        # naist-jdic の表記ゆれ: 結合型 -1 (未設定) は *、 動詞F4@0 (% 抜け) は 動詞%F4@0
        if r[14] == "-1":
            r[14] = "*"
        r[14] = re.sub(r"^(動詞|助詞|形容詞|名詞)(?=[FC][1-5])", lambda m: m.group(1) + "%", r[14])

    # 内容語の既定 = (品詞1, 品詞2) ごとの最頻の結合型
    by = collections.defaultdict(collections.Counter)
    for r in rows:
        if not is_functional(r):
            by[(r[4], r[5])][r[14]] += 1
    defaults = {k: c.most_common(1)[0][0] for k, c in by.items()}

    # 付属語・接尾・非自立 (キー = 表記,読み,品詞1,品詞2。 割れたら 最頻の値)
    fn: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    exc: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        if "," in r[0] or "\n" in r[0] or not KATA.match(r[11]):
            continue
        key = ",".join((r[0], r[11], r[4], r[5]))
        if is_functional(r):
            fn[key][f"{r[13]}|{r[14]}"] += 1
        elif r[14] != defaults.get((r[4], r[5])):
            exc[key][r[14]] += 1

    out = a.out_dir
    out.mkdir(parents=True, exist_ok=True)
    head = [
        "# 自動生成: tools/gen_accent_chain.py (手で編集しない)。 naist-jdic (OpenJTalk の辞書) 由来",
        "# (出典: NAIST、 BSD 3-clause。 core/accent/LICENSE.NAIST-jdic)。 アクセント句の連結規則 (accent_chain) の入力",
        "",
        "[meta]",
        'schema_version = "2"',
        'role = "accent_chain"',
        'format = "accent_chain/1"',
    ]
    lines = head + [f'description = "付属語・接尾・非自立 {len(fn)} 件 + 内容語の既定の結合型 {len(defaults)} 件"', "", "[defaults]"]
    for (p1, p2), rule in sorted(defaults.items()):
        lines.append(f"{q(p1 + ',' + p2)} = {q(rule)}")
    lines += ["", "[functional]"]
    for k in sorted(fn):
        lines.append(f"{q(k)} = {q(fn[k].most_common(1)[0][0])}")
    (out / "chain.toml").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    lines = head + [f'description = "内容語のうち品詞の既定と違う結合型を持つ語 {len(exc)} 件"', "", "[exceptions]"]
    for k in sorted(exc):
        lines.append(f"{q(k)} = {q(exc[k].most_common(1)[0][0])}")
    (out / "chain_exceptions.toml").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    # 語単体の核 (連結規則専用)。 キー = 表記,読み,品詞1。 付属語・接尾・非自立は chain.toml にあるので除く。
    # 同じキーで核が割れたら、 最頻の核 (同数なら採らない = 決められない)
    words: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        if is_functional(r) or "," in r[0] or any(ord(c) < 0x20 for c in r[0]) or not KATA.match(r[11]):
            continue
        if (r[0], r[11]) in have:
            continue
        words[",".join((r[0], r[11], r[4]))][r[13]] += 1
    lines = head + [f'description = "語単体の核/拍数 {len(words)} 件 (全品詞、 連結規則専用)"', "", "[words]"]
    kept = 0
    for k in sorted(words):
        top = words[k].most_common(2)
        if len(top) == 2 and top[0][1] == top[1][1]:
            continue
        lines.append(f"{q(k)} = {q(top[0][0])}")
        kept += 1
    (out / "chain_words.toml").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[gen_accent_chain] 既定 {len(defaults)} / 付属語等 {len(fn)} / 内容語の例外 {len(exc)} / 語単体の核 {kept} → {out}")


if __name__ == "__main__":
    main()
