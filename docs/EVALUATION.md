# 性能評価 — `ja-furigana-dict`

辞書の客観的な性能指標。 dict 改善 PR / release で「実際に良くなっているか」 を、
回帰テストとは別軸 (= 任意 input に対する精度) で把握するための公開 metric。

> 戻る: [README.md](../README.md) / [CONTRIBUTING.md](../CONTRIBUTING.md)

## 評価方針

ja-furigana lib (= 辞書 + lib) の出力が、 **TTS engine として広く使われている
VOICEVOX engine 単体の出力よりどれくらい正確か** を主軸 metric として運用する。

評価は **コーパスに設定した「正解読み」 に対して、 ja-furigana と VOICEVOX を
それぞれ機械的に比較** する形で行う。 ja と VOICEVOX を直接比較するのではなく、
独立した ground truth に対する正答率を出すことで、 「両者誤り / 別読み両者正解」
の case も適切に分類できる。

## 評価フロー

```
[sample]  日本語 corpus から固定 seed で N 件サンプリング
   │
   ├─→ [truth.tsv]    AI が原文だけ見て自然な読みを生成 (= 判定不要、 正解のみ)
   │
   ├─→ [ja.tsv]       ja-furigana で読みを取得 (= 当該 dict version)
   │
   └─→ [vv.tsv]       VOICEVOX engine /audio_query で読みを取得 (= 外部 baseline)

   ▼
[mechanical eval]
   - ja_norm == truth_norm → ja correct
   - vv_norm == truth_norm → vv correct
   - ja correct 数 / N → ja 正答率
   - vv correct 数 / N → vv 正答率
   - 差 = ja − vv

   ▼
[ja 誤読 patterns]
   - AI が ja_wrong case を分類 (= 数詞 / 訓読み / 漢字 default 等)
   - 次 round の dict 改善ターゲット明確化
```

## AI の役割と限界

AI (= LLM) は評価 pipeline 内で 2 つの限定的役割のみ担う:

1. **truth 生成** — 原文だけを見て、 ネイティブ日本語話者が自然に読む読みを 1 つ提示。
   ja / vv の出力は見ない (= 引きずられ防止)。 「どちらが正解か」 の判定は AI ではなく
   mechanical script が `truth == ja` / `truth == vv` で行う。
2. **誤読 pattern 分析** — ja_wrong case を category (= 数詞 / 助数詞 / 訓読み / 単漢字
   default / 同形異音 / 配信スラング 等) に分類し、 dict 改善優先度を可視化。

評価 metric の **算出は完全 mechanical**、 AI バイアスは truth 生成段階のみ。
truth 生成の質を担保するため、 AI が「ja_norm / vv_norm のどちらかを採用」 mode に
固定されないよう、 prompt で完全独立を強制する (= 過去 v1 で binary choice mode に
陥った経緯あり)。

## 報告 metric

各 release / 改善 round で以下を測定:

| metric | 意味 |
|---|---|
| **ja-furigana 正答率** | `ja_norm == truth_norm` の件数 / sample 件数 |
| **VOICEVOX 単体 正答率** | `vv_norm == truth_norm` の件数 / sample 件数 |
| **ja − VOICEVOX** | 差分 (= ja-furigana が VOICEVOX を上回った pt) |
| **両者一致率** | 副次指標、 `ja_norm == vv_norm` の比率 (= dict 改善 progress の素朴指標) |

主目標は **ja-furigana 正答率 − VOICEVOX 単体 正答率 > 0 を維持・拡大** すること。
VOICEVOX 単体は dict 改善側で動かせない外部 baseline (= 同 corpus / 同 engine version
で出力 invariant) なので、 ja-furigana 側の dict 改善で差を広げる game。

### unweighted / weighted

- **unweighted (unique 表現)**: 1 文 1 票で集計、 corpus 全体の表現多様性に対する
  カバレッジを反映
- **weighted (実発話相当)**: 各文の出現回数で重み付け、 実利用での「何割
  正しく読めるか」 に近い。 頻発する短いフレーズの正解 1 件が稀フレーズの正解 1 件
  より大きく寄与する設計

## 評価用 corpus について

評価に使うランダムサンプル日本語テキストは、 dict 改善側で以下のような source を
匿名化・統合した内部 corpus からランダム抽出している:

- 配信プラットフォーム (YouTube / Twitch / ニコ生 等) の **匿名化済みチャットログ**
  (= 投稿者 / channel / 配信タイトル等の identifying 情報は破棄、 残るのはコメント
  本文 + timestamp のみ)
- 開発者が運営する個人 web service の テキスト ログ (= 同様に PII 除去後)
- 公開 corpus / Wikipedia 等 一般日本語 text の random sample

**corpus 本体 (= 入力 text、 sqlite DB 等) は配布しない**。 privacy 保護および
辞書 evaluation 側の overfit 防止 (= 評価 corpus が公開されると dict 改善が
それに過剰最適化する) のため。 公開される情報は:

- 評価方法 (= この doc に書いた手順)
- 計測結果数値 (= 履歴 table の正答率 %)
- 差分の傾向分析 (= 改善 round 毎の commit message / CHANGELOG)

具体的な「どの文が誤読されたか」 等の per-record 内容は公開しない (= 元コメントの
逆引きで投稿者特定リスクを 0 にするため)。

## 更新ポリシー

- **baseline**: 0.1.0 stable cut 時点 (= 2026-05-12) の数値を起点とする
- **定期更新**: 月次 / もしくは major dict 改善 batch (= round) 後に再測定し、
  この doc の数値表を append 形式で更新 (= 過去 baseline は履歴として残す)
- **train / verify 分離**: 改善 round の判定は train seed (= 改善時に diff を観た
  sample) と verify seed (= 改善後 fresh sample) の両方で測り、 over-fit を回避

## 履歴

<!-- 新しい計測結果を上に append。 fixed point の数値を残すことで dict 改善の
     progression が時系列で見える。

     【計測 methodology の世代】
     - Gen1 (= 〜2026-05-13): ja_norm == vv_norm を 「両者正解」 と仮定 + diff を
       Agent 判定で ja-correct / vv-correct / both / neither に分類。
       両者一致 比率と Agent 抽出 ratio を組み合わせて ja/VV 絶対値を推定していた。
     - Gen2 (= 2026-05-13〜): corpus に独立 truth を設定 → ja / vv 各々を truth と
       機械比較。 AI の役割を truth 生成と誤読 pattern 分析に限定、 「どちらが正解」
       の判定は AI ではなく ja_norm == truth_norm / vv_norm == truth_norm で機械算出。
       Gen1 で発生した Agent バイアス (= binary choice mode で両者誤り 0 件等) を排除。 -->

### Gen2 (= 独立 truth ベース、 機械算出)

sample N=1000、 fresh seed 12345 (= 過去未使用)。 truth はコーパス sample に対して
独立に設定 (= AI が原文だけ見て自然な読みを生成、 ja/vv の出力には依存しない)、
それに対して ja_norm / vv_norm を機械比較。 SKIP は分母から除外。

| 計測日 | dict version | sample | ja 正答率 | VOICEVOX 正答率 | ja − VOICEVOX | 両者一致 |
|---|---|---|---|---|---|---|
| 2026-05-13 | v2026.05.13.7 + round 25 batch 27-28 (= +1704 件 一般語彙) | 999 | **83.4%** | **85.9%** | **−2.5pt** | 80.0% |

内訳:
- 両者一致 (= match)、 両者正解として加算: 800 件
- diff 200 件のうち truth で機械判定:
  - ja のみ正解: 33 件
  - VOICEVOX のみ正解: 58 件
  - 両者誤り: 108 件
  - skip (= 顔文字 only 等): 1 件

主因 (= ja の負け 2.5pt):
- **ASCII 英字混在文** で ja は literal 保持 (= 「Excel」 「Minecraft」 「KeyScroll」 等)
  vv は katakana 展開で truth と一致、 ja は不一致になる。 既知の 0.2.0 target
  (= loanwords 統合) で解消予定
- **「w」 「ww」 末尾**: ja は literal 保持、 vv は「ダブリユウ」 と読み上げ、
  truth は 「音にしない」 ことが多いので両者誤りに分類
- **「主」 (= 配信者呼称)**: ja は 「ヌシ」 と正しく読む、 vv は 「オモ」 で誤読 →
  ja のみ正解 case として +shift

### Gen1 (= 両者一致 + Agent diff 判定、 参考値)

過去 methodology による測定値。 ja/VV 絶対値は Agent バイアスを含むため参考扱い、
両者一致率 (= 機械算出) のみ高信頼。

| 計測日 | dict version | sample (有効) | ja 正答率† | VOICEVOX 正答率† | ja − VOICEVOX† | 両者一致 |
|---|---|---|---|---|---|---|
| 2026-05-13 (R25 後 fresh) | v2026.05.13.7 (= round 25 batch 1-26、 +1621 件 一般語彙) — fresh seed 55555 | 9,192 / 10,000 | _(未算定)_ | _(同 baseline ≈ 95%)_ | _(未算定)_ | **87.0%** |
| 2026-05-13 (R25 後 33333) | 同上 — seed 33333 | 9,205 / 10,000 | _(未算定)_ | _(同 baseline ≈ 95%)_ | _(未算定)_ | **86.4%** |
| 2026-05-13 (R25 後 verify) | 同上 — verify seed 99999 | 9,154 / 10,000 | _(未算定)_ | _(同 baseline ≈ 95%)_ | _(未算定)_ | **87.3%** |
| 2026-05-13 (R25 後 train) | 同上 — train seed 20260513 | 9,179 / 10,000 | 97.9% 想定 | 95.0% 同 baseline | +2.9pt 想定 | **87.1%** |
| 2026-05-13 (verify) | v2026.05.12 + round 19-23 — verify seed 99999 | 9,191 / 10,000 | _(未算定)_ | _(同 baseline ≈ 95%)_ | _(未算定)_ | 83.9% |
| 2026-05-13 (3rd) | v2026.05.12 + round 48-52 + 単漢字見直し 第 1-18 弾 + round 19-20 | 9,179 / 10,000 | 97.5% | 95.0% | +2.5pt | 84.1% |
| 2026-05-13 (2nd) | v2026.05.12 + round 48-52 + 単漢字見直し 第 1-18 弾 | 9,179 / 10,000 | 97.6% | 96.9% | +0.7pt | 84.0% |
| 2026-05-13 (1st) | v2026.05.12 + round 48-51 + 単漢字見直し 第 1-2 弾 | 9,177 / 10,000 | 92.3% | 96.0% | -3.7pt | 82.9% |

† ja/VV 絶対値は Agent 判定由来、 sample n=200 で精度 ±2pt 程度。 Gen2 移行後に
methodology を統一する予定。

## 評価対象外 (= 既知の制約)

- **ASCII alphabet を含む文**: ja-furigana lib は 0.1.0 時点で alphabet を読みに
  展開しない (= 「PC = ピーシー」 等)。 0.2.0 で loanwords 統合後に評価対象化予定
- **VOICEVOX engine 側の解析揺れ**: vv engine は「ヴィ → ビ」 のような特殊文字
  解釈で diverge する case あり (= vv 側仕様に由来、 vv 不正解と分類)
- **同形異音語の文脈依存**: 文脈で正解が変わる surface (= 「方 = ホウ vs カタ」
  「金 = カネ vs キン」 等) は truth 生成段階で文脈別正解を採用、 ja / vv ともに
  文脈外し case は 不正解 と分類
- **両者誤り**: ja / vv どちらも truth と不一致の case は 両者 不正解 と分類、
  どちらの正答率にも加算されない

## 評価 script

評価 pipeline (= sampling / truth 生成 / ja & vv 実行 / mechanical eval) は
**内部 evaluation 環境で実行** している。 公開 repo には反映されない (= corpus 本体が
公開されない以上、 script だけ公開しても再現できない + script 内部に corpus パスや
個人 service 情報が含まれるため)。

公開される成果物:

- この doc (= 評価方法 / 履歴 table)
- 計測結果数値 (= 正答率 % の時系列)
- dict 側の差分 (= TOML diff、 `docs/release-diffs/`、 `CHANGELOG.md`)

外部 contributor がローカルで類似評価をしたい場合は、 任意の日本語 corpus + VOICEVOX
engine を用意して `furigana lookup --mode hiragana` と VOICEVOX `/audio_query` の出力を
比較するスクリプトを書けば同等の評価が可能 (= 評価方法はオープン、 我々の corpus
だけが非公開)。
