#!/usr/bin/env python3
"""ふりがな辞書 (core/) を VOICEVOX / OpenJTalk のユーザー辞書の形に書き出す (offline tool、 2026-10-14)。

VOICEVOX のユーザー辞書は 「語 / 読み (カタカナ) / アクセント型 / 品詞の種類 / 優先度」 を登録すると、
OpenJTalk 自身の規則で読みも句の連結も直る (例: 麗日さん が ウララ|ニッサン → ウララカサン の 1 句)。
公式エンジンの `POST /user_dict_word` (surface / pronunciation / accent_type / word_type / priority) と
voicevox_core の `UserDict.add_word` が同じ項目を持つので、 この出力 (JSON 配列) を 1 件ずつ登録すればよい。

書き出す語 = **文脈に依らない entry** (match 条件なしの 熟語 / 作品名 / 固有名)。 文脈で読みが変わる語はユーザー辞書では表せないので除く。
アクセント型は `core/accent/` の表 (UniDic / naist-jdic / 予測) から引く。 表に無い語は `--fallback` で扱いを決める。

Usage:
  python tools/export_voicevox_userdict.py --out userdict.json [--only-surfaces diff.tsv] [--fallback flat|skip] [--apply http://127.0.0.1:50021]
  --only-surfaces: 1 列目が表記の TSV。 これに載る語だけ書き出す (例: OpenJTalk と読みが違う語の一覧)
  --accent-file: 予測など追加のアクセント源 (TSV: 列4 = bracket 付きの読み、 列5 = 確信度)。 表に無い語にだけ使う。 --min-conf で足切り
  --apply: 指定すると そのエンジンの /user_dict_word に登録する (既定は書き出しだけ。 本番に向けて使わないこと)
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import tomllib
import urllib.parse
import urllib.request
from pathlib import Path

KANJI = re.compile(r"[㐀-鿿豈-﫿々]")
KATA = re.compile(r"^[ァ-ヴー]+$")
SMALL = set("ャュョァィゥェォヮ")


def morae(s: str) -> int:
    return sum(1 for c in s if c not in SMALL)


def kata(s: str) -> str:
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)


def parse_bracket(v: str) -> tuple[str, int | None]:
    """'[ショシン]シャ' → ('ショシンシャ', 4) / '[ショシンシャ' → (.., 0)。 核が無ければ None"""
    v = v.split("|")[0]
    if "[" not in v and "]" not in v:
        return kata(v), None
    plain = v.replace("[", "").replace("]", "")
    if "]" in v:
        head = v.split("]")[0].replace("[", "")
        return kata(plain), morae(kata(head))
    return kata(plain), 0


def load_accent_tables(core: Path) -> dict[tuple[str, str], int]:
    out: dict[tuple[str, str], int] = {}
    for name in ("unidic", "naist", "predicted"):
        f = core / "accent" / f"{name}.toml"
        if not f.exists():
            continue
        for s, v in tomllib.loads(f.read_text(encoding="utf-8")).get("entries", {}).items():
            for b in v if isinstance(v, list) else [v]:
                r, a = parse_bracket(b)
                if a is not None and (s, r) not in out:
                    out[(s, r)] = a
    return out


def word_type(path: Path) -> str:
    p = path.as_posix()
    if "/proper/" in p or "/works/" in p or "surname" in p or "place_names" in p:
        return "PROPER_NOUN"
    return "COMMON_NOUN"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", type=Path, default=Path("core"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only-surfaces", type=Path)
    ap.add_argument("--fallback", choices=("flat", "skip"), default="skip")
    ap.add_argument("--priority", type=int, default=6)
    ap.add_argument("--accent-file", type=Path)
    ap.add_argument("--min-conf", type=float, default=0.0)
    ap.add_argument("--apply", type=str)
    a = ap.parse_args()

    only = None
    if a.only_surfaces:
        only = {l.split("\t")[0] for l in a.only_surfaces.read_text(encoding="utf-8").splitlines() if l.strip()}
    acc = load_accent_tables(a.core)
    extra: dict[tuple[str, str], tuple[int, float]] = {}
    if a.accent_file:
        for line in a.accent_file.read_text(encoding="utf-8").splitlines():
            c = line.split("	")
            if len(c) >= 5:
                r, at_ = parse_bracket(c[3])
                if at_ is not None:
                    extra[(c[1], r)] = (at_, float(c[4]))
    files = sorted((a.core / "jukugo").rglob("*.toml")) + sorted((a.core / "works").rglob("*.toml")) + [a.core / "_inbox.toml"]
    words: dict[str, dict] = {}
    stat = collections.Counter()
    for f in files:
        if f.name.startswith("_genre") or not f.exists():
            continue
        try:
            data = tomllib.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        wt = word_type(f)
        for s, v in (data.get("entries") or {}).items():
            if only is not None and s not in only:
                continue
            if isinstance(v, dict):
                if v.get("match") or v.get("alt"):
                    stat["除外: 文脈で読みが変わる (match/alt)"] += 1
                    continue
                v = v.get("reading")
            if isinstance(v, list):
                v = v[0] if v else None
            if not isinstance(v, str) or not KANJI.search(s) or not (2 <= len(s) <= 20) or "\n" in s:
                stat["除外: 表記/形式"] += 1
                continue
            r, a_br = parse_bracket(v)
            if not KATA.match(r):
                stat["除外: 読みがカタカナでない"] += 1
                continue
            n = morae(r)
            src = "辞書の bracket"
            at = a_br
            if at is None:
                at = acc.get((s, r))
                src = "アクセント表 (UniDic/naist/予測)"
            if at is None and (s, r) in extra and extra[(s, r)][1] >= a.min_conf:
                at, src = extra[(s, r)][0], "予測器 (--accent-file)"
            if at is None:
                if a.fallback == "skip":
                    stat["除外: アクセント型が不明 (--fallback skip)"] += 1
                    continue
                at, src = 0, "既定 (平板)"
            at = min(at, n)
            if s in words:
                continue
            words[s] = {"surface": s, "pronunciation": r, "accent_type": at, "word_type": wt, "priority": a.priority}
            stat[f"採用: {src}"] += 1
    out = sorted(words.values(), key=lambda w: w["surface"])
    a.out.write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"書き出し {len(out)} 語 → {a.out}")
    for k, c in sorted(stat.items()):
        print(f"  {k}: {c}")
    print("  品詞の内訳:", dict(collections.Counter(w["word_type"] for w in out)))
    print("  アクセント型の内訳 (0=平板):", dict(sorted(collections.Counter(w["accent_type"] if w["accent_type"] < 4 else "4+" for w in out).items(), key=lambda x: str(x[0]))))
    if a.apply:
        # --apply は VOICEVOX エンジンの URL。 file: などの別の scheme を開かないよう http(s) に限る
        if not a.apply.startswith(("http://", "https://")):
            raise SystemExit("--apply は http:// か https:// で始まる URL を指定してください")
        ok = 0
        for w in out:
            q = urllib.parse.urlencode(w)
            req = urllib.request.Request(f"{a.apply}/user_dict_word?{q}", data=b"", method="POST")
            try:
                urllib.request.urlopen(req, timeout=20).read()  # nosec B310 (scheme は上で http(s) に限定済み)
                ok += 1
            except Exception as e:
                print("失敗", w["surface"], e)
        print(f"登録 {ok}/{len(out)} → {a.apply}")


if __name__ == "__main__":
    main()
