#!/usr/bin/env python3
"""
docs/migration/v2_context/from_*.toml の staging entries を core/ の対応 file に
merge する 1 回限り migration script (★A2 alpha.11 dict 完全再編成 第 2 段)。

`migrate_v2_context.py` で staging を作った後の 「実 core/ 適用」 phase。

## merge logic

各 staging entry (`[entries."X"]` block) について:

1. **既存 surface が core/ 内に Simple として存在** (= 31 件):
   - 既存 file の `[entries]` block 内 `"X" = "..."` 行を **削除**
   - 同 file の末尾に `[entries."X"]` sub-table を **append** (= TOML table の
     順序として、 simple [entries] block の **後** に sub-table を置く必要があり、
     末尾 append が安全)

2. **core/ に entry 不在** (= 21 件):
   - 2+ 字 surface → `core/jukugo/basic/general.toml` に append (= catch-all)
   - 1 字 surface → `core/unihan/joyo.toml` に append (= 通常の単漢字置場)

## TOML 形式維持

- 既存 file の comment / [meta] block / 他の simple entry 行は **不変**
- 削除する 「`"X" = "..."`」 行は単一行 pattern なので surgical edit OK
- 末尾 append 時は section header `# === Detailed entries (★A2 migration) ===`
  + blank line で区切り

## scope 外

- `rules/context/` 配下 file の **削除はしない** (= Strict engine 後方互換維持、
  alpha.11 期は inline match と rules/context/ が duplicate 共存)
- 24 カテゴリ再分類 / entry purge は別 phase (= 人手 PR series)
- core/single → core/kanji format 変換は別 script

## 走らせ方

    python tools/merge_migrated_context.py            # dry-run
    python tools/merge_migrated_context.py --apply    # 実 core/ に書き込み

冪等性: 既に detailed block が append 済 (= 行頭 `[entries."X"]` が file 内に存在)
の surface は skip。
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 配置先 default
DEFAULT_JUKUGO_FILE = ROOT / "core" / "jukugo" / "basic" / "general.toml"
DEFAULT_UNIHAN_FILE = ROOT / "core" / "unihan" / "joyo.toml"

# 機械変換 staging dir
STAGING_DIR = ROOT / "docs" / "migration" / "v2_context"


def find_existing_surface_file(surface: str, core_dir: Path) -> Path | None:
    """surface が既存 core/ のどの file に entry として存在するか探す。"""
    for p in core_dir.rglob("*.toml"):
        if p.name == "_genre.toml" or p.name.endswith(".test.toml"):
            continue
        try:
            data = tomllib.loads(p.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            continue
        if surface in data.get("entries", {}):
            return p
    return None


def parse_staging_entry_blocks(staging_file: Path) -> list[tuple[str, str]]:
    """staging file から (surface, raw_toml_block) の list を抽出。

    raw_toml_block = `[entries."X"]` 行から次の `[entries."Y"]` (or EOF) まで。
    `# TODO:` / `# WARNING:` comment は entry block に含めて保持 (= 後で人手レビュー
    可能なよう context 残す)。
    """
    content = staging_file.read_text(encoding="utf-8")
    lines = content.splitlines()
    entry_re = re.compile(r'^\[entries\.(?:"([^"]+)"|([^\]]+))\]\s*$')

    blocks: list[tuple[str, list[str]]] = []
    current_surface: str | None = None
    current_block: list[str] = []
    pending_comments: list[str] = []

    for line in lines:
        m = entry_re.match(line)
        if m:
            # 直前 entry を closeoutput
            if current_surface is not None:
                # trailing 空行を trim
                while current_block and current_block[-1].strip() == "":
                    current_block.pop()
                blocks.append((current_surface, current_block + [""]))
            # 新 entry 開始 (= 直前の TODO comment 群を取り込む)
            current_surface = m.group(1) or m.group(2)
            current_block = pending_comments + [line]
            pending_comments = []
        elif current_surface is None:
            # entry 始まる前: TODO/WARNING comment は次 entry に持ち込み
            stripped = line.strip()
            if stripped.startswith("# TODO:") or stripped.startswith("# WARNING:"):
                pending_comments.append(line)
            else:
                pending_comments = []  # 関連性切断
        else:
            # entry block 内
            current_block.append(line)

    # 最後の entry を flush
    if current_surface is not None:
        while current_block and current_block[-1].strip() == "":
            current_block.pop()
        blocks.append((current_surface, current_block + [""]))

    return [(s, "\n".join(blk)) for s, blk in blocks]


def remove_simple_entry_line(content: str, surface: str) -> tuple[str, bool]:
    """content から `"<surface>" = "..."` 行を削除して (新 content, removed?) を返す。

    既に detailed (`[entries."<surface>"]`) として存在する場合は no-op。
    """
    # detail block 既存 check (冪等性)
    detailed_pat = re.compile(rf'^\[entries\."{re.escape(surface)}"\]\s*$', re.M)
    if detailed_pat.search(content):
        return content, False

    # 行 pattern: `"X" = "..."` (TOML 内の通常 entry)、 行頭 / 行末空白 OK
    surface_escaped = re.escape(surface)
    line_pat = re.compile(
        rf'^[ \t]*"{surface_escaped}"[ \t]*=[ \t]*"[^"]*"[ \t]*\r?\n',
        re.M,
    )
    new_content, n = line_pat.subn("", content, count=1)
    return new_content, n > 0


def append_detailed_block(content: str, block: str) -> str:
    """content の末尾に detailed block を append。 既存 detail section header を
    再利用、 無ければ新規 header 追加。"""
    HEADER = "# === Detailed entries (★A2 alpha.11 migration、 inline match block 持ち) ==="

    # 既に header があれば、 その後に append、 無ければ EOF に header + block
    if HEADER in content:
        # EOF に block append (= header 以降にすべての detail を集める)
        if not content.endswith("\n"):
            content += "\n"
        if not content.endswith("\n\n"):
            content += "\n"
        return content + block + "\n"

    # 新規 header + block
    if not content.endswith("\n"):
        content += "\n"
    if not content.endswith("\n\n"):
        content += "\n"
    return content + HEADER + "\n\n" + block + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="実 core/ に書き込み")
    args = parser.parse_args()

    if not STAGING_DIR.is_dir():
        print(f"error: {STAGING_DIR} not found, run migrate_v2_context.py first", file=sys.stderr)
        return 1

    # staging から (surface, block) を全集約
    all_blocks: list[tuple[str, str]] = []
    for staging_file in sorted(STAGING_DIR.glob("from_*.toml")):
        blocks = parse_staging_entry_blocks(staging_file)
        all_blocks.extend(blocks)
    print(f"staging から {len(all_blocks)} 件の entry を読み込み")

    # 配置先決定 + 同 file 内 block 集約
    core_dir = ROOT / "core"
    file_blocks: dict[Path, list[tuple[str, str]]] = {}  # file → [(surface, block), ...]
    placed_existing = 0
    placed_new = 0
    for surface, block in all_blocks:
        existing = find_existing_surface_file(surface, core_dir)
        if existing:
            target = existing
            placed_existing += 1
        else:
            target = DEFAULT_JUKUGO_FILE if len(surface) >= 2 else DEFAULT_UNIHAN_FILE
            placed_new += 1
        file_blocks.setdefault(target, []).append((surface, block))

    print(f"  既存 entry merge: {placed_existing} / 新規 entry: {placed_new}")
    print(f"  影響 file: {len(file_blocks)}")

    # 各 file を更新
    for target, items in sorted(file_blocks.items(), key=lambda x: str(x[0])):
        rel = target.relative_to(ROOT).as_posix()
        if not target.is_file():
            print(f"  WARN: {rel} 不在、 skip ({len(items)} entries lost)", file=sys.stderr)
            continue
        content = target.read_text(encoding="utf-8")
        original = content
        ops_removed = 0
        ops_skipped_idempotent = 0
        for surface, block in items:
            # 既に detail として存在するなら skip (冪等性)
            detailed_pat = re.compile(
                rf'^\[entries\."{re.escape(surface)}"\]\s*$', re.M
            )
            if detailed_pat.search(content):
                ops_skipped_idempotent += 1
                continue
            content, removed = remove_simple_entry_line(content, surface)
            if removed:
                ops_removed += 1
            content = append_detailed_block(content, block)

        diff_size = len(content) - len(original)
        print(
            f"  {rel}: {len(items)} entries (removed {ops_removed}, skipped {ops_skipped_idempotent} idempotent), "
            f"size {len(original)} → {len(content)} (Δ +{diff_size})"
        )

        if args.apply and content != original:
            target.write_text(content, encoding="utf-8", newline="\n")

    if not args.apply:
        print("\n(dry-run、 反映するには --apply を付けて再実行)")
    else:
        print("\n[apply] 完了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
