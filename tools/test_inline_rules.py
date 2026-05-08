#!/usr/bin/env python3
"""
core/ + rules/ 配下の TOML file 内 `[[test]]` array を抽出して、
ja-furigana binary で input → expected が一致するか検証する。

各 dict / rule file の末尾に「この file が担当する変換」 を inline test として
書けるようにする (corpus regression と違い、 file ごとの責務を明示するための
「ロック」 として機能):

    # rules/counters/objects.toml
    [counter."本"]
    default = "ホン"
    [[counter."本".rules]]
    last_digit = [1, 6, 8, 0]
    suffix = "ポン"
    sokuonize = true

    # ↓ inline test (この file の責務)
    [[test]]
    input = "1本"
    expected = "イッポン"

    [[test]]
    input = "3本"
    expected = "サンボン"

走らせ方:
    python tools/test_inline_rules.py --binary <path>            # default mode hiragana
    python tools/test_inline_rules.py --binary <path> --data-dir <path>

CI で validate.yml の 1 step として呼ぶ予定。 inline test 0 件の file は skip
(全 file での 必須化はせず、 contributor が書きたい file から書ける緩い制約)。

`subprocess.run` は argv list + shell=False で shell injection 経路無し。
"""
from __future__ import annotations

import argparse
import subprocess  # nosec B404 — fixed argv list, shell=False で安全
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def collect_inline_tests() -> list[tuple[Path, str, str, list[tuple[str, str]]]]:
    """`*.test.toml` ファイルから `[[test]]` を集める。

    戻り値: (file_path, input, expected, targets) のリスト。
    targets は (surface, reading) のペア list (新 schema [[test.targets]]、
    旧 case には無いので空 list)。

    test は **隣接した `<name>.test.toml`** に書く方針 (lib runtime memory にも
    release tar にも乗らないため、 release.yml が `--exclude='*.test.toml'`
    で除外、 lib loader も name match で skip)。 ペアで rule + test が並ぶので
    contributor 体験は「1 dir 内で隣接」 を維持する。
    """
    tests: list[tuple[Path, str, str, list[tuple[str, str]]]] = []
    test_files: list[Path] = []
    for sub in ("core", "rules"):
        base = ROOT / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.test.toml")):
            test_files.append(p)

    for path in test_files:
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError):
            continue
        cases = data.get("test")
        if not isinstance(cases, list):
            continue
        for case in cases:
            if not isinstance(case, dict):
                continue
            inp = case.get("input")
            exp = case.get("expected")
            if not (isinstance(inp, str) and isinstance(exp, str)):
                continue
            # alpha.10+ 新 schema: [[test.targets]] で対象語句を (surface, reading) で列挙
            target_pairs: list[tuple[str, str]] = []
            for t in case.get("targets") or []:
                if not isinstance(t, dict):
                    continue
                s = t.get("surface")
                r = t.get("reading")
                if isinstance(s, str) and isinstance(r, str):
                    target_pairs.append((s, r))
            tests.append((path, inp, exp, target_pairs))
    return tests


def run_lookup(binary: str, text: str, mode: str, data_dir: str | None) -> str:
    cmd = [binary]
    if data_dir:
        cmd += ["--data-dir", data_dir]
    cmd += ["lookup", "--mode", mode, text]
    try:
        result = subprocess.run(  # nosec B603 — fixed argv, no shell
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>"
    if result.returncode != 0:
        return f"<ERROR exit={result.returncode}: {result.stderr.strip()}>"
    return result.stdout.rstrip("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, help="furigana binary path")
    parser.add_argument("--data-dir", default=None, help="--data-dir for furigana")
    parser.add_argument("--mode", default="hiragana", help="lookup mode (default: hiragana)")
    args = parser.parse_args()

    tests = collect_inline_tests()
    if not tests:
        print("[skip] inline test 0 件 (どの file にも [[test]] が無い)")
        return

    print(f"[info] inline test {len(tests)} 件を実行")
    fails = 0
    by_file: dict[Path, list[str]] = {}
    for path, inp, exp, targets in tests:
        actual = run_lookup(args.binary, inp, args.mode, args.data_dir)

        full_match_ok = actual == exp
        target_failures = [
            f"      - 対象 `{s}` の reading `{r}` が output に含まれない"
            for s, r in targets
            if r not in actual
        ]

        if full_match_ok and not target_failures:
            continue

        fails += 1
        msg_lines = [f"  input={inp!r}"]
        if not full_match_ok:
            msg_lines.append(f"    expected: {exp}")
            msg_lines.append(f"    actual:   {actual}")
        if target_failures:
            msg_lines.append("    target 検証失敗:")
            msg_lines.extend(target_failures)
        by_file.setdefault(path, []).append("\n".join(msg_lines))

    if fails == 0:
        print(f"[OK] 全 {len(tests)} 件 pass")
        return

    for path, msgs in by_file.items():
        rel = path.relative_to(ROOT)
        print(f"\n[FAIL] {rel} ({len(msgs)} 件):", file=sys.stderr)
        for m in msgs:
            print(m, file=sys.stderr)

    print(f"\n[FAIL] {fails}/{len(tests)} 件失敗", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
