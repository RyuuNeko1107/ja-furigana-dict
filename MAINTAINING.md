# Maintaining ja-furigana-dict

メンテナー向けの運用ガイド。

## Release を打つ

`ja-furigana-cli` は `ja-furigana-dict` の latest release tag を見て自動取得するので、
辞書を更新したら release を出す (ただし通常は手動不要、下記参照)。

### 通常運用: daily auto-release で自動

`.github/workflows/daily-release.yml` が JST 03:00 に走り、core/ または rules/ への
変更が前回 tag 以降にあれば **`v<YYYY.MM.DD>` (CalVer) tag を自動で打つ**。
そのまま `release.yml` が catch して tar.gz + sha256 を GitHub Releases に upload。

つまり TOML 編集 → master push → 翌 JST 03:00 → 利用者が `furigana dict pull` で取得、
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

## upstream (ryuuneko.com production DB) から seed を再投入

upstream で新熟語が追加された場合:

```sh
# 1. upstream から TSV を export
ssh debian "docker exec kuroneko-postgres psql -U zunda -d kuroneko_cms \
  -t -A -F$'\t' -c \"COPY (SELECT character, reading FROM furigana_unihan \
  ORDER BY character) TO STDOUT\"" > tools/seed/unihan.tsv
# (jukugo / compat も同様、tools/import_from_production.py のコメント参照)

# 2. import script を回す
python3 tools/import_from_production.py
# → core/unihan.toml / core/jukugo/general.toml / core/compat.toml が更新される

# 3. 振り分け再実行 (単漢字 → unihan、四字熟語 → four_char、地名 → place_names)
python3 tools/classify_jukugo.py --apply

# 4. validate
python3 tools/validate.py

# 5. commit (release は daily-release.yml が翌 JST 03:00 に自動)
git add core/
git commit -m "data: upstream から seed 再投入 (unihan X / jukugo Y / compat Z)"
git push origin master
# 即時 release が必要なら手動で:
#   TODAY=$(date +%Y.%m.%d)
#   git tag -a "v$TODAY" -m "v$TODAY"
#   git push origin "v$TODAY"
```

> root の `VERSION` ファイルは v0.1.x 時代の名残で、CalVer 移行後は使用しない。
> 将来の cleanup で削除予定。

## CI / Workflow 一覧

### Validate (`validate.yml`)
- push / PR で `tools/validate.py` (taplo + scheme + kana 検証 + cross-file 重複検出) が走る
- 失敗時は CI ログに詳細が出るのでそれに従って修正

### Release (`release.yml`)
- `v*` tag push で `furigana-dict-<tag>.tar.gz` + `.sha256` を GitHub Releases に upload
- 中身は `core/` + `rules/` の 2 階層 (利用側 CLI で `data/` 1 階層に flatten 展開)
- tag 文字列は CalVer / semver 問わず受け付け、URL に流すだけ

### Daily auto-release (`daily-release.yml`)
- JST 03:00 に cron 起動
- 前回 tag 以降 core/ または rules/ に変更があれば、CalVer (`vYYYY.MM.DD`) tag を auto-commit
- bot の `[skip stats]` commit は差分判定から除外 (STATS.md 更新だけでは release しない)
- 同日複数 release は `vYYYY.MM.DD.1` / `.2` … で衝突回避

### Regen STATS.md (`regen-stats.yml`)
- master push (core/**/*.toml, rules/**/*.toml, tools/regen_stats.py 変更時) trigger
- `tools/regen_stats.py` が走り、STATS.md の auto-generated 区間 (マーカー間) を更新
- diff があれば `chore: regen STATS.md [skip stats]` で auto-commit
- contributor は手元で実行不要

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
