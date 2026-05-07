#!/usr/bin/env python3
"""
core/unihan.toml を 5 ファイルに水準別分類して core/unihan/*.toml に再配置する。

分類ルール (重複なし、 上から順に判定):
1. **常用漢字** (`tools/seed/jouyou.txt`、 2,136 字) → `core/unihan/joyo.toml`
2. **人名用漢字** (`tools/seed/jinmeiyou.txt`、 983 字 から常用と重複する 128 字を
   除外した 855 字) → `core/unihan/jinmeiyou.toml`
3. **JIS 基本** (CJK Unified Ideographs Basic Block U+4E00-U+9FFF のうち常用 /
   人名用に含まれない字、 概ね JIS X 0208 第1+第2水準カバー) →
   `core/unihan/jis_basic.toml`
4. **JIS 補助** (CJK Extension A U+3400-U+4DBF + CJK Compatibility Ideographs
   U+F900-U+FAFF、 概ね JIS X 0213 第3+第4水準カバー) →
   `core/unihan/jis_supplement.toml`
5. **拡張** (上記いずれにも該当しない、 主に CJK Extension B 以降 U+20000+
   の表外字 / 中国専用字 / 異体字) → `core/unihan/extension.toml`

走らせ方 (1 回限りの migration script、 CI では実行しない):
    python tools/classify_unihan.py
    # → core/unihan.toml が消えて core/unihan/{joyo,jinmeiyou,jis_basic,
    #     jis_supplement,extension}.toml の 5 ファイルが生成される

冪等性: 既に core/unihan.toml が無く core/unihan/ がある場合は no-op。

seed list 出典 (`tools/seed/`、 .gitignore 対象、 maintainer-only):
- `jouyou.txt` (2,136 字): 文化庁告示「常用漢字表」 (2010-11-30 内閣告示)。
- `jinmeiyou.txt` (983 字、 常用と重複 128 字含む): 法務省告示「戸籍法施行規則」
  別表第二 (人名用漢字一覧)。
- 一次取得元: https://gist.github.com/fasiha/4988a6701487d28d5b12d22af6593f67
  (公開公文書なので public domain 取り扱い、 license 表記なし)。
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_TOML = ROOT / "core/unihan.toml"
DST_DIR = ROOT / "core/unihan"
SEED_DIR = ROOT / "tools/seed"


META_DESCRIPTIONS = {
    "joyo.toml":
        "常用漢字 2,136 字 (文化庁 2010-11-30 改訂、 内閣告示) — 利用頻度高、 default reading review 対象",
    "jinmeiyou.toml":
        "人名用漢字 (法務省、 子の名に使用可、 常用と重複する 128 字を除外した残り 855 字)",
    "jis_basic.toml":
        "JIS 基本 (CJK Basic Block U+4E00-U+9FFF のうち常用 / 人名用以外、 概ね JIS X 0208 第1+第2水準カバー)",
    "jis_supplement.toml":
        "JIS 補助 (CJK Extension A + Compatibility Ideographs、 概ね JIS X 0213 第3+第4水準カバー)",
    "extension.toml":
        "拡張漢字 (CJK Extension B 以降、 表外字 / 中国専用字 / 異体字、 機械的扱い、 ほぼ lib lookup されない)",
}


def load_seed(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8").strip()
    return set(text)


def classify(char: str, joyo: set[str], jinmeiyou_only: set[str]) -> str:
    """char をどの bucket に振るか。 戻り値はファイル名。"""
    if char in joyo:
        return "joyo.toml"
    if char in jinmeiyou_only:
        return "jinmeiyou.toml"
    cp = ord(char)
    if 0x4E00 <= cp <= 0x9FFF:
        return "jis_basic.toml"
    if (0x3400 <= cp <= 0x4DBF) or (0xF900 <= cp <= 0xFAFF):
        return "jis_supplement.toml"
    return "extension.toml"


def write_bucket(path: Path, bucket: str, entries: dict[str, str]) -> None:
    desc = META_DESCRIPTIONS[bucket]
    lines = [
        f"# {desc}",
        "#",
        "# このファイルは tools/classify_unihan.py で自動分類された。",
        "# 個別 entry の手動編集は OK (PR で reading 修正等)、 ただし新規追加は",
        "# 該当 codepoint range のファイルへ。",
        "",
        "[meta]",
        f'description = "{desc}"',
        "",
        "[entries]",
    ]
    for k in sorted(entries):
        v = entries[k]
        lines.append(f'"{k}" = "{v}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not SRC_TOML.exists():
        print(f"already classified: {SRC_TOML} not present", file=sys.stderr)
        return

    joyo = load_seed(SEED_DIR / "jouyou.txt")
    jinmeiyou_all = load_seed(SEED_DIR / "jinmeiyou.txt")
    jinmeiyou_only = jinmeiyou_all - joyo

    print(f"jouyou: {len(joyo)} chars")
    print(f"jinmeiyou (all): {len(jinmeiyou_all)} chars")
    print(f"jinmeiyou (excl jouyou): {len(jinmeiyou_only)} chars")

    with open(SRC_TOML, "rb") as f:
        data = tomllib.load(f)
    entries = data.get("entries", {})
    print(f"input entries: {len(entries):,}")

    buckets: dict[str, dict[str, str]] = {fname: {} for fname in META_DESCRIPTIONS}
    for surface, reading in entries.items():
        if not isinstance(reading, str):
            continue
        if len(surface) != 1:
            # 単漢字 only (現行 unihan は 1 char surface のはず、 念のため)
            print(f"WARN: skipping non-single surface {surface!r}", file=sys.stderr)
            continue
        bucket = classify(surface, joyo, jinmeiyou_only)
        buckets[bucket][surface] = reading

    DST_DIR.mkdir(parents=True, exist_ok=True)
    for fname in META_DESCRIPTIONS:
        out = DST_DIR / fname
        write_bucket(out, fname, buckets[fname])
        print(f"  -> {out.relative_to(ROOT)} : {len(buckets[fname]):,} entries")

    SRC_TOML.unlink()
    print(f"removed: {SRC_TOML.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
