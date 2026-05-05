#!/usr/bin/env python3
"""
本番 ryuuneko.com の furigana_* テーブルから seed を取り込む (メンテナ専用)。

前提: tools/seed/{unihan,jukugo,compat}.tsv が存在する。
取得方法 (例):

    ssh debian "docker exec kuroneko-postgres psql -U zunda -d kuroneko_cms \
      -t -A -F$'\t' -c \"COPY (SELECT character, reading FROM furigana_unihan \
      ORDER BY character) TO STDOUT\"" > tools/seed/unihan.tsv

挙動:
- 本番優先で既存 TOML と merge (本番に無い手書き entries は残す)
- 出力先: core/unihan.toml / core/jukugo/general.toml / core/compat.toml
- ヘッダコメントは既存ファイルのものを保持し、[entries] / [map] 以下のみ再生成
- 並び順: Unicode コードポイント順 (漢字 key は実質これしかない)

要 Python 3.11+ (tomllib)。
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / 'tools' / 'seed'


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


def load_existing_entries(path: Path, section: str) -> dict[str, str]:
    """既存 TOML の [entries] または [map] を dict として読む。"""
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding='utf-8'))
    table = data.get(section, {})
    if not isinstance(table, dict):
        return {}
    return {k: v for k, v in table.items() if isinstance(v, str)}


def extract_header(path: Path, section_marker: str) -> str:
    """既存ファイルの先頭から `section_marker` 行 (含む) までを返す。
    ファイルが無い or section_marker が無ければ空文字。
    """
    if not path.exists():
        return ''
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        out.append(line)
        if line.strip() == section_marker:
            return ''.join(out)
    return ''


def write_lookup(path: Path, entries: dict[str, str], default_header: str) -> None:
    """[entries] 形式で書き出し (既存ヘッダ保持)。"""
    header = extract_header(path, '[entries]') or default_header
    sorted_keys = sorted(entries.keys())
    body_lines = [f'"{toml_quote(k)}" = "{toml_quote(entries[k])}"\n' for k in sorted_keys]
    if not header.endswith('\n'):
        header += '\n'
    path.write_text(header + ''.join(body_lines), encoding='utf-8')


def write_compat(path: Path, mapping: dict[str, str], default_header: str) -> None:
    """[map] 形式で書き出し (既存ヘッダ保持)。"""
    header = extract_header(path, '[map]') or default_header
    sorted_keys = sorted(mapping.keys())
    body_lines = [f'"{toml_quote(k)}" = "{toml_quote(mapping[k])}"\n' for k in sorted_keys]
    if not header.endswith('\n'):
        header += '\n'
    path.write_text(header + ''.join(body_lines), encoding='utf-8')


def main() -> int:
    # ── unihan ────────────────────────────────────────────────
    unihan_path = ROOT / 'core' / 'unihan.toml'
    existing_unihan = load_existing_entries(unihan_path, 'entries')
    rows = read_tsv(SEED / 'unihan.tsv', 2)
    prod_unihan = {char: reading for char, reading in rows if char and reading}
    # 本番優先で merge: existing → prod の順で上書き
    merged_unihan = {**existing_unihan, **prod_unihan}

    write_lookup(
        unihan_path,
        merged_unihan,
        default_header='# 単漢字フォールバック辞書\n#\n# 1 漢字 → カタカナ または ひらがな (慣習: 訓=ひら / 音=カタ)。\n\n[entries]\n',
    )
    print(
        f"unihan: existing {len(existing_unihan)} + production {len(prod_unihan)} "
        f"→ merged {len(merged_unihan)} entries"
    )

    # ── jukugo (general.toml) ─────────────────────────────────
    jukugo_path = ROOT / 'core' / 'jukugo' / 'general.toml'
    existing_jukugo = load_existing_entries(jukugo_path, 'entries')
    rows = read_tsv(SEED / 'jukugo.tsv', 3)  # surface, reading, source
    # source は無視 (OSS 側はシンプル surface→reading のみ)
    prod_jukugo: dict[str, str] = {}
    for surface, reading, _src in rows:
        if surface and reading:
            prod_jukugo[surface] = reading
    merged_jukugo = {**existing_jukugo, **prod_jukugo}

    write_lookup(
        jukugo_path,
        merged_jukugo,
        default_header='# 一般熟語・四字熟語等\n\n[entries]\n',
    )
    print(
        f"jukugo (general): existing {len(existing_jukugo)} + production {len(prod_jukugo)} "
        f"→ merged {len(merged_jukugo)} entries"
    )

    # ── compat ────────────────────────────────────────────────
    compat_path = ROOT / 'core' / 'compat.toml'
    existing_compat = load_existing_entries(compat_path, 'map')
    rows = read_tsv(SEED / 'compat.tsv', 2)
    prod_compat = {variant: canonical for variant, canonical in rows if variant and canonical}
    merged_compat = {**existing_compat, **prod_compat}

    write_compat(
        compat_path,
        merged_compat,
        default_header='# 異体字 → 標準字\n\n[map]\n',
    )
    print(
        f"compat: existing {len(existing_compat)} + production {len(prod_compat)} "
        f"→ merged {len(merged_compat)} entries"
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
