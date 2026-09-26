#!/usr/bin/env python3
"""
本番 (upstream) の furigana_* テーブルから seed を取り込む (メンテナ専用)。

前提: <seed-dir>/{unihan,jukugo,compat}.tsv が存在する (既定 tools/seed/、 gitignore 対象)。
TSV の列: unihan = 字 / 読み、 jukugo = 表層 / 読み / source (source は無視)、
compat = 異体字 / 標準字。

取得方法: 接続先 (ssh host / postgres container / DB user / DB name) は repo に
書かず、 環境変数で渡す。 `--print-export-cmd <kind>` で export 用の command を表示する:

    export FURIGANA_SEED_SSH_HOST=<ssh-host>
    export FURIGANA_SEED_PG_CONTAINER=<postgres-container>
    export FURIGANA_SEED_DB_USER=<db-user>
    export FURIGANA_SEED_DB_NAME=<db-name>
    python3 tools/import_from_production.py --print-export-cmd unihan > /tmp/export.sh
    sh /tmp/export.sh > tools/seed/unihan.tsv

(テーブル名 / 列名が本番 schema と違う場合は `--table` / `--columns` で上書きする)

挙動 (現行の dict 配置に合わせた merge):
- 単漢字 → `core/unihan/<水準>.toml`。 既存の字はその字がある file で扱い、 新規の字は
  コードポイントで水準 file を選ぶ (CJK 基本 → jis_basic / 拡張 A・互換漢字 →
  jis_supplement / 拡張 B 以降 → extension)。 `core/kanji/` に `[[kanji]]` block が
  ある字は skip (unihan に足すと validate の cross-file 重複になる)
- 熟語 → 新規 surface は `core/_inbox.toml` (分類前 inbox、 後で genre file へ振り分ける)。
  `core/jukugo/` / `core/works/` / `core/_inbox.toml` のどこかに既にある surface は skip
- 異体字 → `rules/compat.toml` の `[map]`
- 既存 key の読みが本番と違う場合、 既定では上書きせず conflict として報告だけする。
  `--overwrite` を付けると、 simple 形式 (`"key" = "読み"` の 1 行) の entry に限り
  本番の読みで上書きする (旧挙動の 「本番優先」)。 detailed entry は常に skip
- 新規 entry は各 file の `[entries]` / `[map]` 行の直後 (simple entry zone) に挿入する。
  既存のコメント / detailed entry / 並び順には触らない
- `--dry-run` で書き込まずに件数だけ表示

取り込み後は `python3 tools/validate.py` を必ず通すこと。

要 Python 3.11+ (tomllib)。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SEED = ROOT / 'tools' / 'seed'

CORE = ROOT / 'core'
UNIHAN_DIR = CORE / 'unihan'
KANJI_DIR = CORE / 'kanji'
INBOX = CORE / '_inbox.toml'
COMPAT = ROOT / 'rules' / 'compat.toml'

# export 用の既定 table / 列 (本番 schema と違えば --table / --columns で上書き)
EXPORT_DEFAULTS = {
    'unihan': ('furigana_unihan', 'character, reading'),
    'jukugo': ('furigana_jukugo', 'surface, reading, source'),
    'compat': ('furigana_compat', 'variant, canonical'),
}
ENV_KEYS = {
    'ssh_host': ('FURIGANA_SEED_SSH_HOST', '<ssh-host>'),
    'container': ('FURIGANA_SEED_PG_CONTAINER', '<postgres-container>'),
    'db_user': ('FURIGANA_SEED_DB_USER', '<db-user>'),
    'db_name': ('FURIGANA_SEED_DB_NAME', '<db-name>'),
}


def toml_quote(s: str) -> str:
    """TOML basic string にエスケープ (`"` `\\`)。本番データに改行は無い前提。"""
    return s.replace('\\', '\\\\').replace('"', '\\"')


def read_tsv(path: Path, expected_cols: int) -> list[tuple[str, ...]]:
    if not path.exists():
        sys.exit(f"missing TSV: {path}")
    rows: list[tuple[str, ...]] = []
    for raw in path.read_text(encoding='utf-8').splitlines():
        if not raw:
            continue
        cols = raw.split('\t')
        if len(cols) < expected_cols:
            print(f"  skip malformed: {raw!r}", file=sys.stderr)
            continue
        rows.append(tuple(cols[:expected_cols]))
    return rows


def load_table(path: Path, section: str) -> dict:
    """TOML の [entries] / [map] を dict で返す (値は str = simple / dict = detailed)。"""
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding='utf-8'))
    table = data.get(section, {})
    return table if isinstance(table, dict) else {}


def toml_files(base: Path) -> list[Path]:
    if not base.is_dir():
        return []
    return [
        p for p in sorted(base.glob('**/*.toml'))
        if p.name != '_genre.toml' and not p.name.endswith('.test.toml')
    ]


def kanji_block_chars() -> set[str]:
    chars: set[str] = set()
    for p in toml_files(KANJI_DIR):
        data = tomllib.loads(p.read_text(encoding='utf-8'))
        for b in data.get('kanji', []) or []:
            if isinstance(b, dict) and isinstance(b.get('char'), str):
                chars.add(b['char'])
    return chars


def unihan_level_for(ch: str) -> str:
    """既存 file に無い字の水準 file をコードポイントで選ぶ。"""
    cp = ord(ch[0])
    if 0x4E00 <= cp <= 0x9FFF:
        return 'jis_basic.toml'
    if 0x3400 <= cp <= 0x4DBF or 0xF900 <= cp <= 0xFAFF:
        return 'jis_supplement.toml'
    return 'extension.toml'


class Plan:
    """file ごとの 追加 (insert) / 上書き (replace) を貯めて最後にまとめて書く。"""

    def __init__(self) -> None:
        self.inserts: dict[Path, dict[str, str]] = {}
        self.replaces: dict[Path, dict[str, str]] = {}

    def insert(self, path: Path, key: str, value: str) -> None:
        self.inserts.setdefault(path, {})[key] = value

    def replace(self, path: Path, key: str, value: str) -> None:
        self.replaces.setdefault(path, {})[key] = value

    def apply(self, section_marker_for: dict[Path, str]) -> None:
        for path in sorted(set(self.inserts) | set(self.replaces)):
            # bytes で読んで改行コード (LF / CRLF) をそのまま保つ
            text = path.read_bytes().decode('utf-8')
            lines = text.splitlines(keepends=True)
            # 上書き: simple 形式の 1 行だけを置換
            for key, value in self.replaces.get(path, {}).items():
                pat = re.compile(r'^"' + re.escape(toml_quote(key)) + r'"\s*=\s*"')
                for i, line in enumerate(lines):
                    if pat.match(line):
                        comment = ''
                        m = re.search(r'"\s*(#.*)$', line.rstrip('\r\n'))
                        if m:
                            comment = '  ' + m.group(1)
                        eol = '\r\n' if line.endswith('\r\n') else '\n'
                        lines[i] = f'"{toml_quote(key)}" = "{toml_quote(value)}"{comment}{eol}'
                        break
            # 追加: section 行の直後に sort 済みで挿入 (simple entry zone を保つ)
            new = self.inserts.get(path, {})
            if new:
                marker = section_marker_for[path]
                idx = next((i for i, ln in enumerate(lines) if ln.strip() == marker), None)
                if idx is None:
                    sys.exit(f"{path}: {marker} 行が見つからない")
                eol = '\r\n' if lines[idx].endswith('\r\n') else '\n'
                body = [f'"{toml_quote(k)}" = "{toml_quote(new[k])}"{eol}' for k in sorted(new)]
                lines[idx + 1:idx + 1] = body
            path.write_text(''.join(lines), encoding='utf-8', newline='')


def merge(
    plan: Plan,
    label: str,
    prod: dict[str, str],
    existing: dict[str, tuple[Path, object]],
    new_target,
    overwrite: bool,
) -> None:
    """prod を existing (key → (file, value)) に対して plan へ積む。"""
    added = same = conflicts = replaced = skipped_detailed = 0
    for key, reading in sorted(prod.items()):
        hit = existing.get(key)
        if hit is None:
            target = new_target(key)
            if target is None:
                continue
            plan.insert(target, key, reading)
            added += 1
            continue
        path, value = hit
        if not isinstance(value, str):
            skipped_detailed += 1
            continue
        if value == reading:
            same += 1
            continue
        if overwrite:
            plan.replace(path, key, reading)
            replaced += 1
        else:
            conflicts += 1
            rel = path.relative_to(ROOT).as_posix()
            print(f"  conflict [{label}] {key}: dict={value} / prod={reading} ({rel})", file=sys.stderr)
    print(
        f"{label}: 追加 {added} / 同一 {same} / 上書き {replaced} / conflict {conflicts} "
        f"/ detailed skip {skipped_detailed}"
    )


def print_export_cmd(kind: str, table: str | None, columns: str | None) -> int:
    default_table, default_cols = EXPORT_DEFAULTS[kind]
    table = table or default_table
    columns = columns or default_cols
    vals = {k: os.environ.get(env, placeholder) for k, (env, placeholder) in ENV_KEYS.items()}
    for k, (env, placeholder) in ENV_KEYS.items():
        if vals[k] == placeholder:
            print(f"warning: {env} が未設定 (placeholder {placeholder} のまま出力)", file=sys.stderr)
    order = columns.split(',')[0].strip()
    sql = f"COPY (SELECT {columns} FROM {table} ORDER BY {order}) TO STDOUT"
    remote = (
        f"docker exec {vals['container']} psql -U {vals['db_user']} -d {vals['db_name']} "
        f"-t -A -F$'\\t' -c \\\"{sql}\\\""
    )
    print(f'ssh {vals["ssh_host"]} "{remote}"')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--seed-dir', type=Path, default=DEFAULT_SEED, help='TSV の置き場 (既定 tools/seed/)')
    ap.add_argument('--overwrite', action='store_true', help='既存 simple entry の読みを本番で上書き')
    ap.add_argument('--dry-run', action='store_true', help='書き込まずに件数だけ表示')
    ap.add_argument('--print-export-cmd', choices=sorted(EXPORT_DEFAULTS), metavar='KIND',
                    help='export 用 command を表示して終了 (unihan / jukugo / compat)。 接続先は環境変数')
    ap.add_argument('--table', help='--print-export-cmd の table 名を上書き')
    ap.add_argument('--columns', help='--print-export-cmd の列 (カンマ区切り) を上書き')
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass

    if args.print_export_cmd:
        return print_export_cmd(args.print_export_cmd, args.table, args.columns)

    seed: Path = args.seed_dir
    plan = Plan()
    markers: dict[Path, str] = {}

    # ── unihan ────────────────────────────────────────────────
    unihan_existing: dict[str, tuple[Path, object]] = {}
    for p in toml_files(UNIHAN_DIR):
        markers[p] = '[entries]'
        for k, v in load_table(p, 'entries').items():
            unihan_existing[k] = (p, v)
    kanji_chars = kanji_block_chars()
    prod_unihan = {c: r for c, r in read_tsv(seed / 'unihan.tsv', 2) if c and r}
    skipped_kanji = [c for c in prod_unihan if c in kanji_chars and c not in unihan_existing]

    def unihan_target(ch: str) -> Path | None:
        if ch in kanji_chars:
            return None
        return UNIHAN_DIR / unihan_level_for(ch)

    merge(plan, 'unihan', prod_unihan, unihan_existing, unihan_target, args.overwrite)
    if skipped_kanji:
        print(f"  ([[kanji]] block がある字 {len(skipped_kanji)} 件は skip)")

    # ── jukugo → core/_inbox.toml ─────────────────────────────
    jukugo_existing: dict[str, tuple[Path, object]] = {}
    for p in toml_files(CORE / 'jukugo') + toml_files(CORE / 'works') + [INBOX]:
        for k, v in load_table(p, 'entries').items():
            jukugo_existing[k] = (p, v)
    markers[INBOX] = '[entries]'
    # source 列は無視 (OSS 側はシンプル surface→reading のみ)
    prod_jukugo = {s: r for s, r, _src in read_tsv(seed / 'jukugo.tsv', 3) if s and r}
    # 1 字 surface は jukugo に入れない (unihan 専用領域)
    prod_jukugo = {s: r for s, r in prod_jukugo.items() if len(s) >= 2}
    # 既存 surface の上書きは _inbox.toml 内のものに限る (genre file は人手キュレーション)
    inbox_only = {k: v for k, v in jukugo_existing.items() if v[0] == INBOX}
    other = {k: (p, None) for k, (p, _v) in jukugo_existing.items() if p != INBOX}
    merge(plan, 'jukugo', {k: v for k, v in prod_jukugo.items() if k not in other},
          inbox_only, lambda _k: INBOX, args.overwrite)
    n_other = sum(1 for k in prod_jukugo if k in other)
    if n_other:
        print(f"  (genre file / works に既にある surface {n_other} 件は skip)")

    # ── compat → rules/compat.toml ────────────────────────────
    markers[COMPAT] = '[map]'
    compat_existing = {k: (COMPAT, v) for k, v in load_table(COMPAT, 'map').items()}
    prod_compat = {v: c for v, c in read_tsv(seed / 'compat.tsv', 2) if v and c}
    merge(plan, 'compat', prod_compat, compat_existing, lambda _k: COMPAT, args.overwrite)

    if args.dry_run:
        print('(dry-run: 書き込みなし)')
        return 0
    plan.apply(markers)
    print('done. python3 tools/validate.py で検証すること')
    return 0


if __name__ == '__main__':
    sys.exit(main())
