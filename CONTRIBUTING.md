# Contributing to furigana-dict

語彙辞書の追加・修正は **TOML を 1 行追加するだけ** で完結する。
Rust 知識・Git クローン不要。

> **詳細スキーマ**: [`docs/SCHEMA.md`](docs/SCHEMA.md)
> **`*.test.toml` の規約**: [`docs/INLINE_TESTS.md`](docs/INLINE_TESTS.md)
> **CI / release の運用**: [`MAINTAINING.md`](MAINTAINING.md)

## クイックパス: GitHub Web UI で 1 件追加

1. 該当ファイルを開く (用途別の配置):

<!-- AUTO-GENERATED:PLACEMENT:BEGIN -->
| 追加したいもの | 配置 | 補足 |
|---|---|---|
| **熟語** (≥ 2 字 surface) | [`core/jukugo/<genre>/<file>.toml`](core/jukugo/) | genre 6 区分 (basic / humanities / nature / objects / proper / society)、 内訳は [STATS.md](STATS.md#熟語) |
| **熟語 (genre 判断付かない)** | [`core/_inbox.toml`](core/_inbox.toml) | 一時 inbox、 maintainer が後で振り分け |
| **単漢字** (1 字 surface) | [`core/unihan/<水準>.toml`](core/unihan/) | 5 水準 (joyo / jinmeiyou / jis_basic / jis_supplement / extension) |
| **異体字 → 標準字** | [`core/compat.toml`](core/compat.toml) | lib Step 1 で入力テキストを正規化 |
| **外来語** (英字始まり surface) | [`core/loanwords/<file>.toml`](core/loanwords/) | 2 file (general / it)、 完全一致 lookup |
| **作品造語** (作品単位 1 ファイル) | [`core/works/<medium>/<title>.toml`](core/works/) | medium 3 区分 (anime / game / literature)、 サブポリシー: [`core/works/README.md`](core/works/README.md) |
| **助数詞ルール** | [`rules/numbers/counters/<file>.toml`](rules/numbers/counters/) | 7 file (objects / people / percent / places / recursive / simple / time)、 連濁 / 促音化 / kana 末尾置換 |
| **数字慣用語句** | [`rules/numbers/numeric_phrases.toml`](rules/numbers/numeric_phrases.toml) | 二十歳→ハタチ 等、 助数詞ルールより先に確定 |
| **後処理 regex** | [`rules/text/postprocess.toml`](rules/text/postprocess.toml) | mode 別 (hiragana / ruby / tts / romaji) の出力直前 regex 置換 |
| **記号 / SI 単位 / 大数** | [`rules/text/{symbols,units}.toml`](rules/text/) / [`rules/numbers/scales.toml`](rules/numbers/scales.toml) | 単純 surface→reading mapping |
<!-- AUTO-GENERATED:PLACEMENT:END -->

   どの genre / 水準にどの file があるかの最新件数は [STATS.md](STATS.md) を参照
   (master push 後 CI で auto-regen)。

2. 右上の鉛筆アイコン (Edit) をクリック
3. `[entries]` セクションに 1 行追加:
   ```toml
   "新しい表層" = "シンシイヒョウソウ"
   ```
4. ページ下部の「Commit changes」→ ブランチ自動生成 → PR 作成

## ローカル編集 (複数件・差分大きめ)

```sh
git clone https://github.com/RyuuNeko1107/ja-furigana-dict
cd furigana-dict
# core/*.toml を編集
git checkout -b add-readings
git commit -am "add: 灰桜/黎明 等"
gh pr create
```

## TOML 形式の最低限ルール

```toml
[meta]
schema_version = "2"                              # alpha.10+ で必須 (★A1b)
role = "jukugo"                                   # alpha.9+ で role tag を併置
description = "二字・三字の一般熟語"             # 1 行説明 (STATS.md に自動取り込み)

[entries]
"灰桜" = "ハイザクラ"
"黎明" = "レイメイ"
```

- **`[meta] schema_version = "2"`** が必須 (alpha.10〜、 ★A1b)。 既存 file に
  既設、 新規 file 追加時は冒頭に必ず置く。 不在は CI の `validate.py` が fail。
- **key (表層) と value (読み) は両方ダブルクォートで囲む**
- **value は ひらがな または 全角カタカナ** のみ (半角カナ・ローマ字は不可)
  - 慣習: 訓読み = ひらがな / 音読み = カタカナ
  - lib 側で出力時に正規化されるため、 どちらで書いても挙動は同じ
- 1 ファイル内で同じ key を二重登録しない (TOML パーサが error)
- **単漢字 (1 文字 surface) は jukugo / works に絶対追加しない** —
  `core/unihan/<水準>.toml` 専用領域、 混入すると `validate.py` が cross-file 重複として CI を fail させる
- **異体字 (compat の key 側) を jukugo / works / unihan に追加しない** —
  lib の Step 1 で標準字に正規化されるため dead 経路、 master push 時に CI の
  `dedup_compat.py` が自動削除する

### 文脈分岐 reading が要る場合 (★A2、 alpha.11〜)

「上手」 = ジョウズ / カミテ のように surface 周辺で読みが変わる場合は **detailed
entry** で書く (= entry inline match block):

```toml
[entries]
"灰桜" = "ハイザクラ"           # simple form (大半はこれ)

[entries."上手"]                # detailed form (= 文脈分岐 reading 持ち)
reading = "ジョウズ"             # default reading (必須)

[[entries."上手".match]]
next_eq = "から"                 # 直後 token が "から" なら...
reading = "カミテ"               # ...読みを "カミテ" に切替
```

詳細 vocabulary (`prev_eq` / `next_eq` / `prev_ends_any` / `next_starts_any` /
`prev_char_type` / `prev_month` / `next_digit` / `next2_starts_any` 等) は
[`docs/SCHEMA.md` の detailed entry 節](docs/SCHEMA.md#detailed-entry--inline-match-block-持ち-a2-alpha11)
参照。 **品詞 (`pos`) ベースの matcher は採用しない** (Lindera 撤廃路線、 literal
列挙 で代用)。

### intonation bracket notation (forward compat、 0.2.0 で activate)

reading 内に accent marker (`[` 開始 / `]` accent peak / `/` phrase 区切り) を
**0.1.0 から書ける** (= lib alpha.10 〜 0.1.0 stable では strip して無視、 0.2.0
から activate):

```toml
"上手" = "ジョ]ウズ"   # 1型 (頭高)
"霧雨" = "キ[リサメ"   # 0型 (平板)
```

詳細書き方は [`docs/SCHEMA.md` の bracket notation 節](docs/SCHEMA.md#intonation-bracket-notation-forward-compat-020-で-activate)
参照。 0.2.0 で intonation 機能投入、 それまでに dict が bracket 付き reading を
蓄積できる構造 (= forward compat)。

各 file の詳細スキーマ (counters / context / postprocess / loanwords 等の specific 構文) は
[`docs/SCHEMA.md`](docs/SCHEMA.md) を参照。

### NG

- 商標・固有名詞のうち **公的に認知されていない読み** (誤読をデフォルト化しない)
- 文脈で読みが変わる語の片方だけを `core/jukugo/*` の default にする
  (それは entry inline match `[[entries."x".match]]` で扱う領域、
  上記 「[文脈分岐 reading が要る場合](#文脈分岐-reading-が要る場合-a2-alpha11)」 参照)
- 単漢字 1 文字の surface (上記参照、 unihan 専用 / 文脈分岐は `[[kanji]]` block)

### 推奨

- ファイル内のエントリは **50 音順** で並べる (PR diff が読みやすい)
- 大量追加するときは:
  - 同じ PR に **同じ分野 (人名 / 地名 / 一般語)** をまとめる
  - 1 PR あたり ~50 件程度を目安に分割すると review が楽
- `STATS.md` の更新は不要 — master push されると GitHub Actions が自動で再生成 + auto-commit

## ファイルが大きくなりすぎたら

`core/jukugo/` `core/works/` `core/loanwords/` `core/kanji/` `rules/numbers/counters/`
等の sub-dir は **配下の `*.toml` を全て再帰的に自動 merge** する仕組みになっている
(lib loader 側で対応済み)。 1 ファイルが PR レビューしづらいサイズになったら、
**自由に分割して構わない**:

```
core/jukugo/
├── general.toml                # 既存
├── general_a.toml              # 「あ」始まりだけ別ファイルに分けたい場合
└── general_ka.toml             # ...等
```

- ファイル名は何でも構わない (lib は filename ソート順で全 toml を merge)
- 同じ key を複数ファイルに書くと **後勝ち** (filename ソート後の最後が採用)
- counters / `[[kanji]]` のように **複雑な構造の merge** が必要なものは `merge()` ロジックが
  lib 側にあるので「分け方」は自由

## ローカル事前チェック

```sh
python3 tools/validate.py
# → [OK] N ファイル検査済 (jukugo X / unihan Y entries)
# 失敗時は [FAIL] と詳細が出る
```

Python 3.11+ が必要 (`tomllib` 使用)。

CI 詳細 (`validate.yml` / `release.yml` / `daily-release.yml` 等) は
[`MAINTAINING.md`](MAINTAINING.md) を参照。

## レビュー方針

「正しい読み」 vs 「自然な読み」で意見が割れた場合は、**TTS 読み上げで
実用上自然な方** を採用する。

人名・固有名詞の追加 PR は出典を必須にしないが、判断付かない時は merge を保留して
PR 上で議論するのが無難。

## AI ツールの活用

開発側 (= maintainer) は **辞書 entry の追加・修正に AI (LLM) ツールを主力で活用**
しています。 contributor の PR でも AI 利用は自由です。 主な活用ポイント:

- **読み候補の列挙・提案**: ある漢字 / 熟語の読み候補を AI に列挙させる
- **例文の作成**: `tests/corpus/*.toml` や `*.test.toml` の `input` フィールド
  (= 検証用の短文)
- **副作用の洗い出し**: 「この default 変更で何の case が壊れるか」 を AI 込みで
  事前検討
- **コメント / doc 整形**: TOML 内の `#` コメントや markdown 文章の整形・推敲

ただし **「AI 出力を素通しさせない」 確認作業は絶対** が前提運用です:

- **読み (= `reading` フィールド) は必ず辞書 / 公的資料で出典確認**: AI の
  hallucination 由来の誤読を dict に混入させないため、 reading 値は AI 単独の出力
  を採用せず、 **国語辞典 / 漢和辞典 / 公式 site の表記で裏取り**
- **`tools/validate.py` で TOML schema gate** (= ローカルで `[OK]` 確認)
- **`tools/run_corpus.py` で regression test gate** (= 既存 case が壊れたら fail)
- **大量 batch 追加は分ける**: AI 生成 entry を一気に大量 PR すると review 負荷が
  scale しないので、 同分野 ~50 件程度に分割する
- **新規 entry には regression test を 1 件以上追加**: AI 生成だからこそ、 期待動作を
  [`tests/corpus/should_read.toml`](tests/corpus/should_read.toml) で固定する

辞書の品質保証は **validate + corpus regression + maintainer review** の 3 段 gate
で押さえる設計です。 AI は工程を速くする道具で、 **最終確認責任は contributor +
maintainer にあります**。

## 性能評価

dict 改善の客観指標 (VOICEVOX engine 一致率) は [`docs/EVALUATION.md`](docs/EVALUATION.md)
で公開しています。 baseline は定期更新され、 release 単位で「実際に良くなったか」
を回帰テストとは別軸で確認できます。
