#!/usr/bin/env python3
"""助数詞 (rules/numbers/counters/) が実際に効いているかを機械的に確かめる (2026-10-19)。

各助数詞 K について 3K / 5K / 10K を lib の CLI (tts) に通し、 読みの末尾が定義 (default) の 2 字目以降と合うかを見る。
合わないものは、 別の仕組み (桁の単位 scales.toml・日付・時刻・単位) に先に拾われているか、 定義が効いていない疑い
(例: 極 は scales.toml の 極 = ごく に先に拾われ 2極 = にごく になっていた)。 1 字の読みの連濁 (羽 = ワ → バ / パ) や
日付の特殊読み (日 → ミッカ) は誤検出として出る。

  FURIGANA_EXE=path/to/furigana python tools/check_counters.py
"""
import glob
import os
import subprocess
import tomllib

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dict repo の root
EXE = os.environ.get("FURIGANA_EXE", "furigana")  # lib の CLI

counters = {}
for f in glob.glob(os.path.join(D, "rules", "numbers", "counters", "*.toml")):
    d = tomllib.load(open(f, "rb"))
    for k, v in d.get("counter", {}).items():
        if isinstance(v, dict) and "default" in v:
            counters[k] = v["default"]
    for k, v in d.get("simple", {}).items():
        if isinstance(v, str):
            counters.setdefault(k, v)
        elif isinstance(v, dict) and "default" in v:
            counters.setdefault(k, v["default"])
print("助数詞", len(counters))

inputs, meta = [], []
for k, rd in counters.items():
    if not k or not rd:
        continue
    for n in ("3", "5", "10"):
        inputs.append(n + k)
        meta.append((k, rd, n))

p = subprocess.run(
    [EXE, "lookup", "--rules-dir", os.path.join(D, "rules"), "--core-dict-dir", os.path.join(D, "core"), "--mode", "tts", "--batch"],
    input="\n".join(inputs) + "\n",
    capture_output=True,
    text=True,
    encoding="utf-8",
)
out = p.stdout.split("\n")


def kata(s):
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)


bad = {}
for (k, rd, n), line in zip(meta, out):
    r = kata(line.strip())
    tail = rd[1:] if len(rd) > 1 else rd
    if not r.endswith(tail):
        bad.setdefault(k, []).append((n + k, r))
print("末尾が定義と合わない助数詞", len(bad))
for k, v in sorted(bad.items()):
    print(k, counters[k], v[:2])
