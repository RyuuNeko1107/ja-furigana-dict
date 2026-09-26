# ja-furigana-dict (TOML 辞書)

ja-furigana lib 用の TOML 辞書 + 校正ルール data repo。

- **GitHub**: <https://github.com/RyuuNeko1107/ja-furigana-dict>
- **License**: MIT (data / tools とも、 `LICENSE` 参照)
- **release 形式**: GitHub Releases tar.gz、 lib 側 `furigana dict pull` で取得
- **release pace**: daily-release (CalVer 自動 tag) + lib coordinated SemVer の Hybrid

## 構成

```
core/                — 単語辞書 (entry data、 役割別 sub-dir)
├── jukugo/          — 熟語 (6 genre sub-dir: basic / humanities / nature / objects /
│                      proper / society、 計 47 file)
├── unihan/          — 単漢字 fallback
├── kanji/           — [[kanji]] block (default + 文脈 match、 旧 single_overrides 統合先)
├── works/           — 作品固有名詞 (anime / game / literature / vtuber)
├── loanwords/       — 外来語
└── _inbox.toml      — 分類前の一時 inbox (genre 判断が付かない熟語)

rules/               — 校正ルール (data + 動的合成)
├── numbers/         — days / scales / numeric_phrases + counters/ (助数詞)
├── text/            — symbols / units / postprocess
└── compat.toml      — 異体字 → 標準字 mapping (= lib の入力正規化ルール。
                       lib は rules_dir を走査して role="compat" を読むため core/ ではなく
                       rules/ に置く。 wrapper が rules/core を別 mount しても効く)

(旧 core/single_overrides.toml / rules/context/ は alpha.11 で削除済 —
 [[kanji]] block / entry inline match に migration)

tests/
└── corpus/
    ├── should_read.toml      — 回帰テスト本体
    └── should_read/*.toml    — 分野別 / probe 別。 tests/corpus 全体で約 340 file /
                                約 11,800 case (`grep -r '^\[\[case\]\]' tests/corpus | wc -l`)

tools/
├── validate.py               — TOML 構文 + 読み形式 + cross-file 重複検出 (CI gate)
├── run_corpus.py             — corpus regression runner
├── test_inline_rules.py      — *.test.toml inline test 実行
├── regen_stats.py            — STATS.md 自動生成
├── list_dups.py              — cross-file 重複検出
├── dedup_compat.py           — 異体字 mapping 経由 dead code 削除
├── diff_release.py           — release 間 diff レポート生成
├── import_from_production.py — upstream DB から seed 再投入
├── check_test_append_only.py — *.test.toml の append-only CI 強制
├── gen_accent_brackets.py    — UniDic aType → bracket notation 機械生成 (offline tool)
├── gen_surname_suffix.py     — 一般語と同形の姓 / 地名に敬称 suffix match を生成
│                               (--current に batch-read 実測を渡す。 --battery で
│                                「姓 + 名」 文脈の退行検出 probe。 SCHEMA.md 参照)
├── build_dict_browser.py     — 全 entry 検索用 static HTML 生成 (GitHub Pages)
├── check_default_regression.py — [[kanji]] default 変更による jukugo regression 検出
├── compare_with_reference.py — ローカル binary と公開 API の出力比較
├── cleanup_old_deployments.py — GitHub Pages の古い deployment 履歴を整理
└── seed/                     — import_from_production.py 用 source data (gitignore 対象)
```

## 既存 [meta] role 値

loader が role 駆動 dispatch する tag。 各 TOML 冒頭に `[meta] role = "..."` を書く:

`jukugo` / `unihan` / `kanji` / `works` / `loanwords` / `compat` /
`counters` / `days` / `scales` / `numeric_phrases` / `units` / `symbols` /
`postprocess`

(旧 `single_overrides` / `context` / `latin` は alpha.11 で廃止済)

## alpha.10〜alpha.11 期 dict 側 mechanical 完了 (★A1b / ★A2)

- ✅ **schema_version 必須化** (★A1b、 alpha.10 coordinated): 全 dict / rule TOML
  に `[meta] schema_version = "2"` を bulk 適用、 `validate.py` で gate 化
- ✅ **rules/context → entry inline match 機械変換** (★A2、 alpha.11): 31 既存
  entry を Detailed 化 + 21 missing surface を catch-all 配置 (general.toml)、
  5 件 POS-only match は drop (= default reading で fallback、 redundant)
- ✅ **single_overrides → [[kanji]] block 機械変換** (★A2、 alpha.11):
  `core/kanji/overrides.toml` 生成、 旧 `single_overrides.toml` は **削除済**
- ✅ **旧 format 削除** (★A2、 alpha.11): `core/single_overrides.toml` +
  `rules/context/{homonyms,numbers,special,_genre}.toml` + dir + `rules/text/latin.toml`
  を git rm。 lib Strict engine の文脈分岐は alpha 期間中 一時的に regress、
  Smart engine の `DictBridgeProvider` 完成 (alpha.12+) で復元
- ✅ **1 回限り migration script は適用後に削除**: `tools/migrations/` も削除済
  (= git history で参照可能、 source は git log 追跡)
- ✅ **validate.py 拡張**: detailed entry / `[[kanji]]` block / bracket syntax
  check 対応
- ✅ **docs/SCHEMA.md / CONTRIBUTING.md update**: 新 format / matcher / bracket
  notation を contributor 向けに整備

## alpha.11+ 期 dict 側 残作業 (= 人手 PR series、 multi-week 規模)

mechanical 機械変換 phase 完了後の継続作業 (= LLM 1 session で完結しない、
maintainer / community PR で漸進):

- 5 件 POS-only rule の literal 列挙化 (= 上手 / 下手 / 十分 / 一月 / 二月、
  ただし default reading で実用上動くため非緊急)
- 21 件 missing surface の sub-dir 再 triage (= 現在 general.toml catch-all)
- 重複 / 古い / 出典なし entry の purge (= source attribution data 不在で慎重要)
- `core/jukugo/basic/general.toml` の genre 再分配 (遡及整理は見送り済、 下記注意点参照)
- `core/works/` / `core/loanwords/` 整理確認

## lib coordinated の作業 (完了済)

`DictBridgeProvider` による `[[match]]` block の Viterbi 統合、 `[[kanji]]` block loader、
`rules/context/` / `single_overrides.toml` の削除はいずれも完了済。

## 新 format 例 (alpha.10 投入後)

### entry 省略形 (大半の entry はこのまま、 50k+ 既存 entry が無修正で動く)

```toml
[meta]
schema_version = "2"
role = "works"

[entries]
"魔理沙" = "マリサ"
"紅魔館" = "コウマカン"
```

### entry 完全形 (文脈分岐が要る entry のみ)

```toml
[entries]
"上手" = "ジョウズ"

[[entries."上手".match]]
next_eq = "から"
reading = "カミテ"

[[entries."上手".match]]
prev_eq = "下"
reading = "シタテ"
```

### `[[kanji]]` block (= 旧 single_overrides + unihan 統合)

```toml
[meta]
schema_version = "2"
role = "kanji"

[[kanji]]
char = "生"
default = "セイ"

[[kanji.match]]
next_eq = "じる"
reading = "ショウ"

[[kanji.match]]
next_starts_any = ["まれ", "まれる"]   # 雑な char_type 指定 (ひらがな) は使わず literal 列挙
reading = "ウ"
```

## matcher vocabulary (品詞 不採用)

| 軸 | prev 側 | next 側 | next2 (idx+2) | 値型 |
|---|---|---|---|---|
| literal 一致 | `prev_eq` | `next_eq` | — | string |
| literal いずれか | `prev_eq_any` | `next_eq_any` | — | string array |
| literal 末尾一致 | `prev_ends_any` | — | — | string array |
| literal 先頭一致 | — | `next_starts` | — | string |
| literal 先頭いずれか | — | `next_starts_any` | `next2_starts_any` | string array |
| 文字種 | `prev_char_type` | `next_char_type` | — | "漢字" / "ひらがな" / "カタカナ" / "英数" / "記号" |
| 述語 | `prev_month` | `next_digit` | — | bool |
| 文スコープ (入力文全体の部分一致、 ADR-0010) | — | — | — | `input_contains_any` (string array) |

**`prev_pos` / `next_pos` (Lindera 品詞) は採用しない** (Lindera 撤廃路線)。
正は lib `scoring/format.rs` の `MatchCondition` (= `tools/validate.py` の
`MATCH_CONDITION_KEYS` と 3 点同期。 key の typo は validate が error にする —
lib は未知 field を黙って無視し、 条件が空の match は常時発火に化けるため)。

## bracket notation (accent。 `[` `]` の 2 記号、 旧 `/` 区切りは deprecated)

```toml
[entries]
"天気" = "[テ]ンキ"     # 1型 (頭高)。 `[` = 句頭、 `]` = 核の直後
"霧雨" = "[キリサメ"    # 0型 (平板)

[entries."上手"]
reading = "[ジョウズ]"  # 3型 (尾高)

[[entries."上手".match]]
next_eq = "から"
reading = "[カミテ"     # match 候補も bracket 付きで書ける
```

## よく使うコマンド

```powershell
# validate (CI gate)
python tools/validate.py

# corpus regression test (= should_read.toml + should_read/ 配下)
# ローカルでは lib 側 furigana-corpus-check が速い (run_corpus.py は case 数に比例して遅い):
#   cd ..\furigana; cargo run --release --bin furigana-corpus-check -- `
#       --rules-dir ..\furigana-dict\rules --core-dict-dir ..\furigana-dict\core ..\furigana-dict\tests\corpus
python tools/run_corpus.py

# inline rule tests (= *.test.toml)。 --binary 必須、 --data-dir は flat 配置した data/ の親 dir
python tools/test_inline_rules.py --binary <furigana binary> --data-dir <dir>

# STATS.md 自動再生成
python tools/regen_stats.py

# cross-file 重複検出
python tools/list_dups.py
```

## 主要 doc

- `docs/SCHEMA.md` — TOML スキーマ詳細
- `docs/INLINE_TESTS.md` — *.test.toml inline test 規約
- `STATS.md` / `STATS_DUPS.md` — auto-gen (= 各 PR の STATS verify が CI で走る)

## 注意点

- **daily-release.yml schedule 稼働中** (★RESUMED 2026-05-12、 lib v0.1.0 stable cut 後)、 毎日 JST 00:00 (cron、 GitHub の遅延で実行は 2〜3 時間後) に core/rules 差分があれば CalVer tag 自動付与 (2026-09-24 に JST 03:00 から前倒し: 本番 wrapper の JST 05:00 取り込みに間に合わせるため)
- **release pace は Hybrid**: lib coordinated は SemVer (`v0.1.0` 等)、 daily-release / 修正は CalVer (`v2026.07.01` 等)
- **Immutable Releases 設定 OFF** (alpha.7 経緯)、 stable cut 時に ON 推奨
- **CI auto-merge**: dependabot PR + 特定 label PR が auto-merge 対象
- **author email**: `mail@ryuuneko.com` (個人 gmail を直書きしない方針)
- **`core/jukugo/basic/general.toml` (1 万行超) は新規 entry を追加しない**: 過去の batch 追記が
  分野判定を省いて general に投げ込まれ続けた結果肥大化した (政治/医療/軍事/スポーツ/動植物 等、
  本来 `humanities/nature/objects/proper/society` の既存 genre file に属する内容が多数混在)。
  新規 jukugo entry は追加前に該当する genre sub-dir (`core/jukugo/<genre>/*.toml`) を確認し、
  分類先が無ければ `core/_inbox.toml` に置いて後で仕分ける。 general.toml 自体の遡及的な
  再分配 (既存行の genre 移動) は費用対効果が低いとして見送り済 (2026-08-28 判断)
