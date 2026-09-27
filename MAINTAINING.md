# Maintaining ja-furigana-dict

メンテナー向けの運用ガイド。

## Release を打つ

`ja-furigana-cli` は `ja-furigana-dict` の latest release tag を見て自動取得するので、
辞書を更新したら release を出す (ただし通常は手動不要、下記参照)。

### 通常運用: daily auto-release で自動

`.github/workflows/daily-release.yml` が JST 00:00 に走り (実行は GitHub の遅延で 2〜3 時間後)、core/ または rules/ への
変更が前回 tag 以降にあれば **`v<YYYY.MM.DD>` (CalVer) tag を自動で打つ**。
続けて同 workflow が `release.yml` を **`workflow_call` で明示呼び出し** して GitHub Release を作る
(GITHUB_TOKEN で push した tag は他 workflow の push trigger を起動しないため)。

つまり TOML 編集 → master push → 翌 JST 00:00 (実行は数時間遅れ) → 利用者が `furigana dict pull` で取得、
の流れで maintainer の手動操作は不要。

### 手動で release を打ちたい場合

緊急 release / 修正 release を即時に出したいときのみ:

```sh
# 今日の date で tag を打つ (CalVer 形式)
TODAY=$(date +%Y.%m.%d)
git tag -a "v$TODAY" -m "v$TODAY - <要約>"
git push origin "v$TODAY"

# CI 完了を待つ (~30 秒、tarball + sha256 が GitHub Releases に上がる)
gh run watch --repo RyuuNeko1107/ja-furigana-dict --workflow=release.yml

# 確認
gh release view "v$TODAY" --repo RyuuNeko1107/ja-furigana-dict
```

同日に既に release があれば suffix を付ける (`v2026.05.08.1`, `.2` …)。
daily-release workflow も自動で衝突回避するので、衝突は起きないはず。

## upstream (production DB) から seed を再投入

upstream で新熟語が追加された場合。 接続先 (ssh host / postgres container / DB user /
DB name) は repo に書かず、 環境変数で渡す:

```sh
# 1. upstream から TSV を export (tools/seed/ は gitignore 対象)
export FURIGANA_SEED_SSH_HOST=<ssh-host>
export FURIGANA_SEED_PG_CONTAINER=<postgres-container>
export FURIGANA_SEED_DB_USER=<db-user>
export FURIGANA_SEED_DB_NAME=<db-name>
mkdir -p tools/seed
for k in unihan jukugo compat; do
  python3 tools/import_from_production.py --print-export-cmd "$k" > /tmp/export_$k.sh
  sh /tmp/export_$k.sh > tools/seed/$k.tsv
done

# 2. import script を回す (まず --dry-run で件数と conflict を確認)
python3 tools/import_from_production.py --dry-run
python3 tools/import_from_production.py
# → 新規の単漢字は core/unihan/<水準>.toml、 新規の熟語は core/_inbox.toml、
#   異体字は rules/compat.toml に入る。 既存 key の読み違いは conflict として報告のみ
#   (--overwrite で simple entry だけ本番優先で上書き)

# 3. core/_inbox.toml に入った熟語を genre file (core/jukugo/<genre>/) へ人手で振り分ける

# 4. validate
python3 tools/validate.py

# 5. commit (release は daily-release.yml が翌 JST 00:00 以降に自動)
git add core/ rules/
git commit -m "data: upstream から seed 再投入 (unihan X / jukugo Y / compat Z)"
git push origin master
# 即時 release が必要なら手動で:
#   TODAY=$(date +%Y.%m.%d)
#   git tag -a "v$TODAY" -m "v$TODAY"
#   git push origin "v$TODAY"
```


## アクセント専用の表 (`core/accent/unidic.toml`) を作り直す

辞書に bracket の無い語のアクセントを引く表 (`role = "accent"`、 lib の次の release から有効)。
**表記 + 読みが一致する token にだけ効く** ので、 エンジンの区切りや読みが大きく変わった時
(lib の解析まわりの変更 / 辞書の大規模な追加) に作り直す。 daily release ごとに作り直す必要はない。

```sh
# 0. 元データ: UniDic kana-accent 2.1.2 の lex.csv (BSD 条項で利用、 条文は core/accent/LICENSE.UniDic-BSD)
#    https://clrd.ninjal.ac.jp/unidic_archive/cwj/2.1.2/unidic-mecab_kana-accent-2.1.2_src.zip

# 1. 手元のテキスト (1 行 1 文、 数百万行以上あると安定) を lib で token 化して (表記, 読み, 回数) を数える
#    (ja-furigana の examples/token_counts.rs。 並列にするなら入力を split して足し合わせる)
cargo run --release -p ja-furigana --example token_counts -- rules core < corpus.txt > tokens.tsv

# 2. 表を生成 (出現 3 回以上 / aType は多数決 / 助詞・助動詞・ひらがなの接尾辞や補助動詞は除外)
python tools/gen_accent_lexicon.py --lex unidic-mecab_kana-accent-2.1.2_src/lex.csv   --min-count 3 --tokens tokens.tsv --out core/accent/unidic.toml

# 3. validate + corpus (表は読みに影響しないので corpus は不変のはず)
python tools/validate.py && python tools/run_corpus.py
```

ruby 出力 (`{表記|よみ}`) から作ると送り仮名付きの語 (強い / 違う) が 「強」 としてしか数えられず
エンジンの token と一致しないので、 必ず token 単位の集計 (`--tokens`) を使う。

## CI / Workflow 一覧

### Validate (`validate.yml`)

push / PR / workflow_dispatch で 4 つの並列 job が走り、 master の **required status
checks** として branch protection から監視されている:

1. **TOML 構文チェック (taplo)** — `core/*.toml` / `rules/*.toml` (各 dir 直下のみ、
   sub-dir 配下は対象外) のパース可能性。 sub-dir 配下の構文は validate.py の tomllib 読込で検出
2. **スキーマ + カタカナ検証 (validate.py)**:
   - 各ファイルの構造 (`[entries]` / `[map]` / `[[entry]]` / `[[rule]]` 等) 必須
   - reading が ひらがな or 全角カタカナ + 長音 + 中点 のみ
   - jukugo (`core/jukugo/**`) と unihan (`core/unihan/**`) の cross-file 重複検出 → ERROR
   - **jukugo 同士の divergent reading** (例: `abstracts.toml` の イチレント vs
     `four_char.toml` の イチレンタ) → ERROR で CI fail
   - **loanwords (`core/loanwords/**`)** の surface が `[A-Za-zＡ-Ｚａ-ｚ]` 始まり
     + 英数字記号 (`+ # . - _`) のみ、 reading が カタカナ
3. **Python セキュリティ静的解析 (bandit)** — `tools/` 配下の Python スクリプトに対する
   セキュリティ lint
4. **Inline test append-only 検査** — `*.test.toml` の `[[test]]` case が PR base に
   対して削除 / 変更されてないか (`tools/check_test_append_only.py`、 `# DISABLED:`
   tag による意図的削除は許容)

失敗時は CI ログに詳細が出るのでそれに従って修正。 4 個全部 pass しないと master へ
の push / PR merge が branch protection で reject される。

### Release (`release.yml`)
- 起動: `v*` tag push / `workflow_dispatch` (tag 指定) / daily-release.yml からの `workflow_call`
- asset: `furigana-dict-<tag>.tar.gz` + `.sha256`、 inline test だけを集めた
  `furigana-dict-<tag>-tests.tar.gz` + `.sha256`、 前回 tag との差分 `furigana-dict-<tag>-DIFF.md`
  (`tools/diff_release.py` 生成、 `docs/release-diffs/<tag>.md` にも保存)
- 本体 tar の中身は `core/` + `rules/` の 2 階層 (`*.test.toml` / `README.md` は除外、
  利用側 CLI で `data/` 1 階層に flatten 展開)
- 想定 tag 形式は **CalVer (`vYYYY.MM.DD`)**、 同日 N 回目は `.1` / `.2` … suffix
  (旧 semver tag は legacy の `v0.1.0` だけ残置)

### Daily auto-release (`daily-release.yml`)
- JST 00:00 に cron 起動 (実行は 2〜3 時間遅れることがある)
- 前回 tag 以降 core/ または rules/ に変更があれば、CalVer (`vYYYY.MM.DD`) tag を打ち、
  `release.yml` を `workflow_call` で呼んで release を作る (PAT 不要、 GITHUB_TOKEN のみ)
- bot の `[skip stats]` commit は差分判定から除外 (STATS.md 更新だけでは release しない)
- 同日複数 release は `vYYYY.MM.DD.1` / `.2` … で衝突回避

### Dedup compat + Regen STATS.md / STATS_DUPS.md (`regen-stats.yml`)
- master push trigger (path filter: `core/**/*.toml` / `rules/**/*.toml` /
  `tests/corpus/**/*.toml` / `tools/{regen_stats,list_dups,dedup_compat}.py`)
- 順に 3 ステップを実行:
  1. `tools/dedup_compat.py` — compat 異体字 entries の dedup (unihan + jukugo + works)、
     冪等で dead 経路の entries が無ければ no-op。 contributor が PR で誤って異体字
     surface を追加しても CI が自動で標準形に置換 / 削除
  2. `tools/regen_stats.py` — STATS.md / CONTRIBUTING.md の auto-generated 区間
     (マーカー間) を更新
  3. `tools/list_dups.py` — STATS_DUPS.md (cross-file 重複レポート: 同 reading +
     divergent reading の 2 セクション markdown table) を更新
- diff があれば `chore: dedup compat + regen STATS [skip stats]` で auto-commit
- bot 自身の commit は `[skip stats]` で再 trigger を防ぐ (regen-stats.yml も
  validate.yml も skip filter 持つ)
- contributor は手元で実行不要

**branch protection bypass**: master の required status checks (4 個) は
`GITHUB_TOKEN` (= github-actions[bot]) の push を reject するため、 admin user の
OAuth token / PAT を **`STATS_PUSH_TOKEN` repo secret** に登録して使用。
secret 未設定時は `GITHUB_TOKEN` fallback で push が失敗する (warning)、 contributor
が手元で `python tools/dedup_compat.py && python tools/regen_stats.py && python
tools/list_dups.py` を実行して `[skip stats]` 付き commit で push する形で代替可能。

token 更新が必要な時:

```sh
gh auth token | gh secret set STATS_PUSH_TOKEN --repo RyuuNeko1107/ja-furigana-dict
```

### Auto-merge label (`auto-merge-label.yml`)
- `pull_request_target` で起動
- 変更ファイルがすべて `core/` / `rules/` 配下、行追加 ≤ 200 の PR に
  `auto-mergeable` label を付ける (条件外なら label を外す)

### Auto-merge after 48h (`auto-merge.yml`)
- 6 時間ごとに cron 起動
- `auto-mergeable` label 付き、最終更新 48h 以上経過、CI all green、merge 可能 (CLEAN)
  な PR を squash merge + branch delete
- 48h grace は spam / 悪意ある PR の preempt 反応時間

### Dependabot (`.github/dependabot.yml`)
- GitHub Actions のみ (Cargo / npm 依存無し)
- 週次の actions 更新 PR が来るので CI 緑なら auto-merge label が付いて 48h 後に merge

## PR のレビュー方針

`CONTRIBUTING.md` 末尾の「レビュー方針」に集約:
> 「正しい読み」 vs 「自然な読み」で意見が割れた場合は、TTS 読み上げで
> 実用上自然な方を採用する。

人名・固有名詞の追加 PR は出典を必須にしないが、判断付かない時は merge を保留して
PR 上で議論するのが無難。

## Bug / Security

- 一般 bug: GitHub Issues (`bug_report.yml` テンプレ)。
- 「この読みは間違ってる」: `reading_request.yml` テンプレ (PR でも OK)。
- 辞書由来の挙動バグは ja-furigana 本体ではなくこちらの repo に来てもらう。
- security 系の脆弱性はこの repo の対象範囲外 (純データ)。CLI / lib 側に飛ばす。
