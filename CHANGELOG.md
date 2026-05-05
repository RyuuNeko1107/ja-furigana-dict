# Changelog

`ja-furigana-dict` (語彙辞書 + ルールデータ) の変更履歴。
[Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) 形式。

利用側の `ja-furigana-cli` は `furigana dict pull --version vX.Y.Z` でピン留め可能。
未指定時は GitHub Releases の latest を自動取得。

## [Unreleased]

(次の release で入れる変更をここに追記)

## [0.1.1] - 2026-05-05

### Added
- `core/jukugo/four_char.toml` を新設し、`general.toml` から **四字熟語 58 件** を分離
  (一期一会 / 四面楚歌 / 優柔不断 等)。判定: 4 字 + 全部 CJK 漢字。
- `tools/classify_jukugo.py` を拡張: `looks_like_four_char` で機械的に振り分け、
  `--apply` で `general.toml` / `four_char.toml` / `place_names.toml` を一括書き換え。
- `CONTRIBUTING.md` に **`rules/context/` 書き方ガイド** を追加: 8 つの match 条件
  (`prev_eq` / `prev_ends_with_any` / `prev_ends_with_month` / `next_eq` /
  `next_starts_with` / `next_starts_with_any` / `next_starts_with_digit` /
  `next_next_starts_with_any` / `pos_eq`) を意味と例で表形式に明示。
- `CONTRIBUTING.md` に **「ファイルが大きくなりすぎたら」** セクションを追加。
  `core/jukugo/` `rules/counters/` `rules/context/` は同名サブディレクトリ配下を
  自動 merge する仕組みが lib loader にあることを明示し、分割運用ガイドを記載。

### Changed
- `core/jukugo/general.toml`: 600 → 542 entries (四字熟語 58 件を `four_char.toml` へ移動)。
- jukugo 全体は 605 entries で変わらず (general 542 + four_char 58 + place_names 5 +
  personal_names 0 + proper_nouns 0)。
- README の status を「初期 seed 投入中、空に近い」から実態 (44k+ entries) に更新。

## [0.1.0] - 2026-05-05

初回 GitHub Release。本番 ryuuneko.com から seed 投入完了版。

### Added
- **本番 ryuuneko.com から seed 投入**:
  - `core/unihan.toml`: 単漢字フォールバック **43,749 字**
    (本番 override 14 件を含む: 中=ジュウ / 乙=オツ / 午=ヒル / 専=せん / 拍=ウ /
     木=キ / 柵=サク / 踵=カカト / 面=オモテ / 頬=ホホ / 𡚴=セイ / 𡱖=つび /
     𡸴=ロウ / 𢈘=ロク)。
  - `core/jukugo/general.toml`: 一般熟語 600 件 (4 字+漢字の四字熟語 58 件含む、
    後の 0.1.1 で `four_char.toml` に分離)。
  - `core/jukugo/place_names.toml`: 地名 5 件 (北海道 / 吉祥寺 / 秋葉原 / 表参道 /
    鹿児島 — 機械振り分け済み)。
  - `core/compat.toml`: 異体字マップ 436 件。
- `tools/import_from_production.py`: 本番 PostgreSQL の `furigana_*` テーブルを
  CSV export → TOML 化 + 本番優先 merge する maintainer 専用ツール。
- `tools/classify_jukugo.py` (初版): 単漢字を `jukugo` から削除して `unihan` に
  統合、地名接尾語で `place_names.toml` へ機械振り分け。
- Release workflow に `core/` と `rules/` 両方を archive に含める修正。

### Changed
- `tools/validate.py` を kana 全般 (ひらがな + 全角カタカナ) 許容に緩和
  (本番データの慣習: 訓読み = ひらがな / 音読み = カタカナ に追従)。

## [一覧]

[Unreleased]: https://github.com/RyuuNeko1107/ja-furigana-dict/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/RyuuNeko1107/ja-furigana-dict/releases/tag/v0.1.1
[0.1.0]: https://github.com/RyuuNeko1107/ja-furigana-dict/releases/tag/v0.1.0
