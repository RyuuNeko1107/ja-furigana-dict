#!/usr/bin/env python3
"""
前回 tag と今回 tag (or HEAD) の TOML 辞書差分を集計して markdown を出力。

release.yml workflow から呼ばれて release notes に同梱される。

usage:
    python tools/diff_release.py <prev-tag> <now-tag-or-HEAD>

両 tag 時点のファイル内容を `git show <tag>:<path>` で取得 → tomllib で
parse → entries (= surface→reading) を比較。 集計対象は core/ + rules/ 配下
の `[entries]` / `[map]` を持つ TOML。 `_genre.toml` は対象外。

出力 (stdout、 markdown):

    # ja-furigana-dict release diff: <prev> → <now>

    ## 集計
    - 追加 entries: ...
    - 削除 entries: ...
    - 読み変更: ...
    - 新規 file: ...
    - 削除 file: ...

    ## 詳細 (file 別)
    ### `core/jukugo/general.toml`
    - 追加 (N): "灰桜" = "ハイザクラ" / ...
    - 削除 (M): ...
    - 読み変更 (K): "一蓮托生" イチレント → イチレンタ

`subprocess.run` は argv list + shell=False で shell injection 経路無し。
"""
from __future__ import annotations

import subprocess  # nosec B404 — fixed argv list, shell=False で安全
import sys
import tomllib
from pathlib import Path


def git_show(tag: str, path: str) -> str | None:
    """`git show <tag>:<path>` を返す。 tag 時点で path が存在しなければ None。"""
    try:
        result = subprocess.run(  # nosec B603 — fixed argv, no shell
            ["git", "show", f"{tag}:{path}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def git_ls_files(tag: str) -> list[str]:
    """tag 時点で tracked な core/ + rules/ 配下の *.toml file 一覧を返す。"""
    result = subprocess.run(  # nosec B603 — fixed argv, no shell
        ["git", "ls-tree", "-r", "--name-only", tag],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return [
        p for p in result.stdout.splitlines()
        if (p.startswith("core/") or p.startswith("rules/"))
        and p.endswith(".toml")
        and not p.endswith("_genre.toml")
    ]


def parse_entries(content: str) -> dict[str, str]:
    """TOML 文字列から entries (key→string value) を取り出す。

    対応 layout:
    - [entries] dict
    - [map] dict (compat.toml)
    - top-level flat (days.toml: '1' = 'ツイタチ' ...)
    [[rule]] / [[entry]] のような array 形式は本 diff では扱わない (件数 small)。
    """
    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError:
        return {}

    for key in ("entries", "map"):
        v = data.get(key)
        if isinstance(v, dict):
            return {
                k: vv for k, vv in v.items()
                if isinstance(vv, str)
            }

    # flat top-level
    flat = {k: v for k, v in data.items() if isinstance(v, str)}
    return flat


def parse_meta_description(content: str) -> str | None:
    """TOML 文字列から `[meta] description` を取り出す。 無ければ None。

    各 dict / rule TOML の冒頭に `[meta] description = "..."` を declare して
    file の用途を 1 行説明する慣行 (STATS.md 用途列も同じ source)。 release diff
    で「新規 / 削除 file は何なのか」 を contributor が判断できるよう、 file 名
    の横に description を併記する。
    """
    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError:
        return None
    meta = data.get("meta")
    if isinstance(meta, dict):
        desc = meta.get("description")
        if isinstance(desc, str) and desc:
            return desc
    return None


def diff_file(prev_content: str, now_content: str) -> tuple[list[str], list[str], list[tuple[str, str, str]]]:
    """1 file 分の (added, removed, changed[(key, prev_v, now_v)]) を返す。"""
    prev = parse_entries(prev_content)
    now = parse_entries(now_content)
    prev_keys = set(prev)
    now_keys = set(now)
    added = sorted(now_keys - prev_keys)
    removed = sorted(prev_keys - now_keys)
    changed = sorted(
        (k, prev[k], now[k]) for k in (prev_keys & now_keys) if prev[k] != now[k]
    )
    return added, removed, changed


def fmt_entry_list(entries: list[str], full: dict[str, str]) -> str:
    """`"key" = "value"` 形式の list を改行区切りで返す。"""
    return "\n".join(f'  - `"{k}" = "{full.get(k, "")}"`' for k in entries[:20]) + (
        f"\n  - … 他 {len(entries) - 20} 件" if len(entries) > 20 else ""
    )


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: diff_release.py <prev-tag> [<now-tag-or-HEAD>]", file=sys.stderr)
        sys.exit(2)
    prev_tag = sys.argv[1]
    now_tag = sys.argv[2] if len(sys.argv) > 2 else "HEAD"

    prev_files = set(git_ls_files(prev_tag))
    now_files = set(git_ls_files(now_tag))

    new_files = sorted(now_files - prev_files)
    removed_files = sorted(prev_files - now_files)
    common = sorted(prev_files & now_files)

    # 詳細 + 全体集計
    total_added = 0
    total_removed = 0
    total_changed = 0
    file_diffs: list[tuple[str, list[str], list[str], list[tuple[str, str, str]], dict[str, str], dict[str, str]]] = []

    for path in common:
        prev_c = git_show(prev_tag, path) or ""
        now_c = git_show(now_tag, path) or ""
        if prev_c == now_c:
            continue
        added, removed, changed = diff_file(prev_c, now_c)
        if not (added or removed or changed):
            continue
        prev_e = parse_entries(prev_c)
        now_e = parse_entries(now_c)
        file_diffs.append((path, added, removed, changed, prev_e, now_e))
        total_added += len(added)
        total_removed += len(removed)
        total_changed += len(changed)

    # 新規 file は全 entries が added 扱い
    for path in new_files:
        now_c = git_show(now_tag, path) or ""
        now_e = parse_entries(now_c)
        if now_e:
            total_added += len(now_e)

    # 削除 file は全 entries が removed 扱い
    for path in removed_files:
        prev_c = git_show(prev_tag, path) or ""
        prev_e = parse_entries(prev_c)
        if prev_e:
            total_removed += len(prev_e)

    # ── markdown 出力 ──
    out: list[str] = []
    out.append(f"# ja-furigana-dict release diff: `{prev_tag}` → `{now_tag}`")
    out.append("")
    out.append("## 集計")
    out.append("")
    out.append(f"- **追加 entries**: +{total_added:,}")
    out.append(f"- **削除 entries**: -{total_removed:,}")
    out.append(f"- **読み変更**: ~{total_changed:,}")
    out.append(f"- **新規 file**: {len(new_files)}")
    out.append(f"- **削除 file**: {len(removed_files)}")
    out.append("")

    if new_files:
        out.append("### 新規 file")
        out.append("")
        for p in new_files:
            now_c = git_show(now_tag, p) or ""
            n = len(parse_entries(now_c))
            desc = parse_meta_description(now_c)
            desc_str = f" — {desc}" if desc else ""
            out.append(f"- `{p}` ({n:,} entries){desc_str}")
        out.append("")

    if removed_files:
        out.append("### 削除 file")
        out.append("")
        for p in removed_files:
            prev_c = git_show(prev_tag, p) or ""
            n = len(parse_entries(prev_c))
            desc = parse_meta_description(prev_c)
            desc_str = f" — {desc}" if desc else ""
            out.append(f"- `{p}` ({n:,} entries){desc_str}")
        out.append("")

    if file_diffs:
        out.append("## 詳細 (file 別、 上位 20 件まで)")
        out.append("")
        for path, added, removed, changed, prev_e, now_e in file_diffs:
            out.append(f"### `{path}`")
            out.append("")
            # file の用途説明 (now tag 側を優先、 無ければ prev tag 側) を heading 直下に
            now_c_for_desc = git_show(now_tag, path) or ""
            desc = parse_meta_description(now_c_for_desc)
            if not desc:
                prev_c_for_desc = git_show(prev_tag, path) or ""
                desc = parse_meta_description(prev_c_for_desc)
            if desc:
                out.append(f"_{desc}_")
                out.append("")
            if added:
                out.append(f"**追加 ({len(added)} 件)**:")
                out.append(fmt_entry_list(added, now_e))
                out.append("")
            if removed:
                out.append(f"**削除 ({len(removed)} 件)**:")
                out.append(fmt_entry_list(removed, prev_e))
                out.append("")
            if changed:
                out.append(f"**読み変更 ({len(changed)} 件)**:")
                for k, pv, nv in changed[:20]:
                    out.append(f'  - `"{k}"`: `{pv}` → `{nv}`')
                if len(changed) > 20:
                    out.append(f"  - … 他 {len(changed) - 20} 件")
                out.append("")

    if not file_diffs and not new_files and not removed_files:
        out.append("(差分なし)")

    print("\n".join(out))


if __name__ == "__main__":
    main()
