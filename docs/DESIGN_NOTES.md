# DESIGN NOTES — 設計判断とその理由

本書は **「なぜこの形になったか」** の記録。 spec の正確な記述は
[SCHEMA.md](SCHEMA.md)、 contributor 向けの 「やりたい → こう書く」 cookbook は
[RECIPES.md](RECIPES.md)。 ここでは **設計上の判断 + 不採用案 + トレードオフ** を
語る。

> 想定読者: 「なぜこの制約があるのか」 「他の選択肢を採らなかった理由は何か」
> を知りたい contributor / maintainer / 後任 / future LLM agent。

## 目次

- [1. 単漢字 vs 熟語 の reading 配置](#1-単漢字-vs-熟語-の-reading-配置)
- [2. divergent reading は必ず文脈条件を伴うべき](#2-divergent-reading-は必ず文脈条件を伴うべき)
- [3. matcher vocabulary の縛り (= 何を採用しなかったか)](#3-matcher-vocabulary-の縛り--何を採用しなかったか)
- [4. 「1/2」 のような曖昧 surface は積極解釈しない](#4-12-のような曖昧-surface-は積極解釈しない)
- [5. dict の自動生成 vs 人手キュレーション](#5-dict-の自動生成-vs-人手キュレーション)

---

## 1. 単漢字 vs 熟語 の reading 配置

**問**: 「上手」 = ジョウズ / カミテ のような **多漢字 word + 文脈分岐** は、
`[entries."上手"]` で書くか、 `[[kanji]]` block で 「上」 「手」 個別に書くか?

### 結論: **両者は競合せず併存、 役割分担で使い分け**

| ケース | 配置 |
|---|---|
| 単漢字単独 + 文脈分岐 (例: 「生」 → セイ / ナマ / ウ) | `core/kanji/*.toml` の `[[kanji]]` |
| 規則的合成熟語 (例: 「再生 = サイセイ」、 各漢字 default で OK) | **書く必要なし** (= kanji default で自動合成) |
| 不規則熟語 (例: 「下手 = ヘタ」、 連濁 / 慣用 / 当て字) | `core/jukugo/<genre>/*.toml` の `[entries]` |
| 不規則熟語 + 文脈分岐 (例: 「上手 → ジョウズ / カミテ」) | 同 entries の `[[entries."x".match]]` |

### 理由

1. **多漢字熟語の不規則 reading は per-char 合成で作れない**:
   - 「下 = シタ」 default + 「手 = テ」 default → 「下手 = シタテ」 になり 「ヘタ」 にならない
   - 「ヘタ」 は **熟語単位で意味を持つ unit reading**、 1 字に切り出す意味的根拠が無い
   - 同様に 「神社 = ジンジャ」 「一人 = ヒトリ」 「大人 = オトナ」 等

2. **規則的合成は per-char で十分**:
   - 「再生 = サイセイ」 = 「再」 default サイ + 「生」 default セイ
   - これらは [[kanji]] block の default だけで自然に合成される、 dict に entries 登録不要
   - dict の負担を減らし、 default が正しい単漢字なら multi-char 派生もカバーできる

3. **scoring engine の path 選択で自然に統合**:
   - Smart engine の Viterbi DP は 両 provider (entries / kanji) から候補を集める
   - 「下手」 input で:
     - entries["下手"] = ヘタ (band 1000、 length 2、 1 edge)
     - kanji["下"] + kanji["手"] = シタテ (band 950 想定、 length 1 ずつ、 2 edges)
   - PathScore の `edge_count` 軸で長 match (= 1 edge) が勝つ → entry が常に優先採用
   - dict に entry 登録があればそれが採用、 無ければ単漢字合成にフォールバックする hybrid 動作

### 「前後に漢字があるとき」 の context 扱い

`prev_char_type = "漢字"` / `next_char_type = "漢字"` で文字種一括判定、 または
`prev_eq_any = ["先", "学", "再", ...]` / `next_eq_any = [...]` で literal 列挙。

```toml
[[kanji]]
char = "生"
default = "セイ"

[[kanji.match]]
prev_eq_any = ["先", "学", "再", "誕", "出"]
reading = "セイ"          # 「先生」 「学生」 「再生」 「誕生」 「出生」 等

[[kanji.match]]
prev_char_type = "ひらがな"  # 「きの生クリーム」 等
reading = "ナマ"

[[kanji.match]]
next_eq_any = ["まれ", "まれる"]
reading = "ウ"             # 「生まれ」 「生まれる」
```

= **per-char rule で multi-char context を判定**、 別途 entries に登録する必要なし。

### 採用しなかった案

#### A) 「全部 entries に書く」 (= kanji block 不採用)

- **問題**: 単漢字単独出現 (例: 「土」 1 字、 ASCII 区切りで現れる) の override が表現できない
- **問題**: 「生」 のような頻出単漢字に文脈分岐を書く度に 「○生」 の全パターンを entries に列挙する必要、 dict 規模が爆発

#### B) 「全部 [[kanji]] に書く + 連濁 logic は lib 内蔵」 (= entries 不採用)

- **問題**: 「下手 = ヘタ」 のような 「per-char で説明できない」 reading が表現不能
- **問題**: lib 内蔵 logic (= 連濁ルール) の adhoc 化、 「シタ + テ → ヘタ」 を一般化するルールは存在せず、 例外列挙が無限に増える

→ 両者を併存させて **「lib データベース読み合成 + dict 内 unit reading 上書き」** の hybrid が最小コスト。

---

## 2. divergent reading は必ず文脈条件を伴うべき

**問**: 同 surface が異なる読みで複数 file に登録されてた場合、 どうする?

### 結論: **CI fail させる**、 文脈条件無しの divergent は受け付けない

`tools/validate.py` の `check_jukugo_divergent_reading` が CI gate:

- 同 surface + **同 reading** が複数 file に出現 → OK (= `STATS_DUPS.md` の
  「同一 reading」 section で track、 merge 後勝ちで実害無し)
- 同 surface + **異なる reading** が複数 file に出現 → **CI fail**

### 理由

1. **lib loader は file 名 alphabetical sort 順で後勝ち**: 違う reading を別 file に
   入れると、 どちらが採用されるか **file 名依存** = 動作予測不能
2. **どちらが正しいか自動判断不可能**: maintainer の PR review で決めるべき
3. **文脈条件無しで両 reading を共存させたい ケースは存在しない**: 異なる reading
   が要るなら必ず 「○○の場合はこっち」 という判別条件が裏にあるはず、 それを
   明示しないのは contributor 側の不備

### 解決策 (= 2 択)

#### A) どちらかが間違い → 1 つに consolidate

```toml
# core/jukugo/foo.toml
"X" = "ABC"

# core/jukugo/bar.toml  ← 削除 (= 重複登録の typo / 古い entry)
# "X" = "DEF"
```

#### B) 両方正しいが文脈で切替 → entry inline match に統合

```toml
# Before: divergent (= CI fail)
# foo.toml: "X" = "ABC"
# bar.toml: "X" = "DEF"

# After: 1 entry に統合 + 文脈条件
[entries."X"]
reading = "ABC"

[[entries."X".match]]
prev_eq = "Y"
reading = "DEF"
```

→ **CI pass、 動作明確、 source of truth が 1 つに**。

### 採用しなかった案

#### A) 「先勝ち / 後勝ち で silent merge」

- **問題**: 動作が file 名 sort order に依存、 contributor の意図と乖離
- **問題**: 「どっちが採用されてるか」 を確認するには lib のソースを読むしかない、
  documentation 困難

#### B) 「ambiguous marker を許容、 lib 側で文脈推論」

- **問題**: 文脈推論は意味解析の領域、 rule-based dict の射程外
- **問題**: 推論精度が悪いと sub-optimal な reading が選ばれる、 silent failure 量産

---

## 3. matcher vocabulary の縛り (= 何を採用しなかったか)

**問**: matcher vocabulary は exact / prefix / suffix / char_type / 述語 のみ、
regex も POS も対応しない。 なぜ?

### 採用したもの

| 軸 | prev | next | next-after-next |
|---|---|---|---|
| literal exact | `prev_eq` | `next_eq` | — |
| literal exact list | `prev_eq_any` | `next_eq_any` | — |
| literal suffix | `prev_ends_any` | — | — |
| literal prefix | — | `next_starts` / `next_starts_any` | `next2_starts_any` |
| 文字種 | `prev_char_type` | `next_char_type` | — |
| 述語 | `prev_month` | `next_digit` | — |

### 採用しなかったもの + 理由

#### POS (品詞) — `prev_pos` / `next_pos`

- **理由**: Lindera 形態素解析撤廃路線 (= 1.0+ vision)。 廃止予定の dependency
  に新仕様を build しない方針
- **代替**: literal 列挙 (例: `prev_eq_any = ["階段", "段", "梯子"]`) で 「名詞の後」
  を近似

#### regex (正規表現)

- **理由**:
  - **ReDoS 攻撃面**: 外部 contributor の PR で regex が dict に入ると、 catastrophic
    backtracking pattern を踏む dict update で lib 起動が hang する可能性
  - **保守性**: 「この regex がどんな match をするか」 を読み手が即理解できない、
    review コストが scale しない
  - **代替で大半カバー可**: 「英数の後」 → `prev_char_type = "英数"`、 「数字始まり」
    → `next_digit = true`、 etc.
- **代替**: lib 側 logic (= chunks/regex.rs の URL_RE / DATE_RE 等) で **lib 開発
  者がレビューした上で登録**、 dict 経由では受け付けない

#### Turing 完全 logic (Lua / JS / Python embed)

- **理由**:
  - **任意コード実行リスク**: dict tar.gz 展開時に embedded script を実行する設計は
    supply chain attack 面が大きい
  - **再現性**: 環境依存挙動 (= 内部状態 / I/O / 時刻参照) で同じ dict + 同じ
    入力でも結果が変わると debug 不能
- **代替**: 必要なら lib 側 module として 「declarative TOML を読んで動く logic」 を
  追加 (= `rules/numbers/counters/` の連濁 / 促音化 が好例、 dict は data 提供で
  logic は lib 側)

#### 距離指定 (= `prev_within_N` / `next_within_N`)

- **理由**: 0.3.0+ 検討中、 現時点では 1 / 2 token lookup (= prev / next /
  next2) で足りる pragmatic 判断
- **将来**: vocabulary 拡張は spec 改訂を伴うので [scoring-engine.md](../docs/PROPOSALS/scoring-engine.md)
  proposal で議論

### 結論: 「セキュリティ + 保守性 = vocabulary を絞る」 が現方針

- 80%+ の context-aware reading は現 vocabulary でカバー可能
- 残り 20% (= 「動詞の後」 のような汎用文法条件) は literal 列挙の冗長さを受け
  入れる、 または lib 側 logic に格上げ

このトレードオフは **dict が外部 contributor 直接 write 可能な環境** であるため
強くなる。 dict が maintainer 専有なら regex / Lua も検討余地ある。

---

## 4. 「1/2」 のような曖昧 surface は積極解釈しない

**問**: 「1/2」 を 「1 月 2 日」 (date) と読むか 「2 分の 1」 (fraction) と読むか?

### 結論: **どちらにも自動解釈しない、 plain digit + symbol で fallback**

現 `NumberCandidateProvider` は:
- `1` digit → 「イチ」
- `/` symbol (= symbols.toml に登録あれば) → 「スラッシュ」
- `2` digit → 「ニ」

→ 「イチスラッシュニ」 or `/` 無し reading 「イチニ」 で plain 出力。

### 理由

1. **rule-based heuristic は誤読を量産する**: 「3/4 メートル」 を 「3 月 4 日メートル」
   と読むのは error
2. **意味解析 (= NL 理解) なしで disambiguate 不能**: 「1/2 は」 「1/2 から」 「1/2 を」
   等、 文脈的手がかりは weak、 token-level matcher で signal 化できない
3. **TTS 用途では plain が無難**: 読み上げ engine 側で文脈処理する余地を残す

### 推奨

- **date 意図** → 「1月2日」 と明示的に書く / 入力側で wrap
- **fraction 意図** → 「2分の1」 と明示的に書く
- **ambiguous 「1/2」** → plain reading で fallback (= caller が後段で判別)

### 採用しなかった案

#### A) heuristic で date 寄りに decode (= `M ≤ 12 && D ≤ 31` ならdate)

- **問題**: 「3/4 of the work」 を 「3 月 4 日 of the work」 と読む
- **問題**: 「2/3」 (= fraction、 三分の二) も `M=2 D=3` で date 認識される

#### B) 文脈見て切替 (= `prev_eq_any = ["締切", "期日", ...]` で date 寄り)

- **問題**: keyword list の網羅性が無限、 maintainer 負担が大きい
- **問題**: 単独 「1/2」 は判定不能で結局 fallback 必要

---

## 5. dict の自動生成 vs 人手キュレーション

**問**: 大規模単語データ (= 10 万件レベル) を import で自動投入するか、 人手 PR で
増やすか?

### 結論: **入口は自動 (= seed import) + メイン body は人手キュレーション**

- `tools/import_from_production.py` で upstream production DB から initial seed
  投入 (= 「最初の 5 万件」)
- それ以降の追加 / 修正は **人手 PR** が前提
- 機械的な大量追加 (= web scrape / LLM 生成) は **PR で reject**

### 理由

1. **誤読の責任所在**: 自動投入 entry が誤読を引き起こした場合の責任が曖昧、
   人手 PR ならレビュー責任が PR 作者 + reviewer に明確化
2. **dict の重さは精度で決まる**: 5 万件 vs 50 万件で 10 倍の精度差は出ない、
   各 entry の信頼度の方が重要
3. **ユーザー寄付 PR が成立する文化**: maintainer が全自動で増やすと contributor
   community が育たない、 「読みを 1 件貢献する」 PR が回る環境を維持

### 採用しなかった案

#### A) Wikipedia / pixiv 百科事典等から大量 scrape

- **問題**: 出典不明な読みが大量混入、 検証コストが追加コスト超過
- **問題**: license 問題 (= 一次出典の reading 情報の使用権)

#### B) LLM 生成で網羅性向上

- **問題**: hallucination 由来の誤読を batch で混入、 corpus regression test
  でも一部漏れる
- **問題**: 「LLM が生成しました」 entry の review 責任を maintainer 一人で
  負うと scale しない

→ **入口を絞る** (= seed only)、 **継続増殖は人手** が現方針。
