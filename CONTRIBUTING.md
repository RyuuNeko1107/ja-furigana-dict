# Contributing to furigana-dict

語彙辞書の追加・修正は **TOML を 1 行追加するだけ** で完結する。
Rust 知識・Git クローン不要。

> **詳細スキーマ**: [`docs/SCHEMA.md`](docs/SCHEMA.md)
> **`*.test.toml` の規約**: [`docs/INLINE_TESTS.md`](docs/INLINE_TESTS.md)
> **CI / release の運用**: [`MAINTAINING.md`](MAINTAINING.md)

## クイックパス: GitHub Web UI で 1 件追加

1. 該当ファイルを開く:
   - **熟語 (≥ 2 字 surface)** → [`core/jukugo/<genre>/<file>.toml`](core/jukugo/)
   - **熟語だけど genre 判断付かない** → [`core/_inbox.toml`](core/_inbox.toml) (一時 inbox、 後で振り分け)
   - **単漢字 (1 字 surface)** → [`core/unihan/<水準>.toml`](core/unihan/)
   - **異体字 → 標準字** → [`core/compat.toml`](core/compat.toml)
   - **単漢字 default override** → [`core/single_overrides.toml`](core/single_overrides.toml)
     ([issue #15](https://github.com/RyuuNeko1107/ja-furigana/issues/15) の限定解)
   - **外来語 (英字始まり surface)** → [`core/loanwords/`](core/loanwords/)
   - **作品造語 (作品単位 1 ファイル)** → [`core/works/<medium>/<title>.toml`](core/works/)

   どの genre / 水準にどの file があるかの最新一覧は [STATS.md](STATS.md) を参照
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
role = "jukugo"                                   # alpha.9+ で role tag を併置
description = "二字・三字の一般熟語"             # 1 行説明 (STATS.md に自動取り込み)

[entries]
"灰桜" = "ハイザクラ"
"黎明" = "レイメイ"
```

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

各 file の詳細スキーマ (counters / context / postprocess / loanwords 等の specific 構文) は
[`docs/SCHEMA.md`](docs/SCHEMA.md) を参照。

### NG

- 商標・固有名詞のうち **公的に認知されていない読み** (誤読をデフォルト化しない)
- 文脈で読みが変わる語の片方だけを `core/jukugo/*` の default にする
  (それは [`rules/context/`](rules/context) 配下の文脈ルールで扱う領域)
- 単漢字 1 文字の surface (上記参照、 unihan 専用)

### 推奨

- ファイル内のエントリは **50 音順** で並べる (PR diff が読みやすい)
- 大量追加するときは:
  - 同じ PR に **同じ分野 (人名 / 地名 / 一般語)** をまとめる
  - 1 PR あたり ~50 件程度を目安に分割すると review が楽
- `STATS.md` の更新は不要 — master push されると GitHub Actions が自動で再生成 + auto-commit

## ファイルが大きくなりすぎたら

`core/jukugo/` `rules/counters/` `rules/context/` の 3 つは **同名サブディレクトリ
配下の `*.toml` を全て自動 merge** する仕組みになっている (lib loader 側で対応済み)。
1 ファイルが PR レビューしづらいサイズになったら、**自由に分割して構わない**:

```
core/jukugo/
├── general.toml                # 既存
├── general_a.toml              # 「あ」始まりだけ別ファイルに分けたい場合
└── general_ka.toml             # ...等
```

- ファイル名は何でも構わない (lib は filename ソート順で全 toml を merge)
- 同じ key を複数ファイルに書くと **後勝ち** (filename ソート後の最後が採用)
- counters / context のように **複雑な構造の merge** が必要なものは `merge()` ロジックが
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
