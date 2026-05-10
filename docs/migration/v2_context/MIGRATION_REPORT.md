# rules/context migration report (v2 context → entry inline match)

alpha.11 期の dict 完全再編成の一部、 `tools/migrate_v2_context.py --apply` 結果。

## 集計

- 総 rule 数: 52
- 総 match block 数: 46
- POS-only match block (= drop されて空 match): 5
- POS + 他条件 mix match block (= POS だけ drop、 他は保持): 0
- core/ に既存 entry がある surface: 31
- core/ に entry 不在 surface (= 新規追加要): 21
- default 不在 rule (= 暫定 default 推定要): 4

## TODO

### POS-only match (= literal 列挙で代用要)

本 5 件は `pos = "名詞"` 等の汎用条件で reading 切替を表現していたが、
新 format は POS 不採用 (Lindera 撤廃路線)。 各 surface で 「名詞のとき」 と
「形容詞のとき」 が同じ reading なら **default reading で十分** (= match
block 不要)。 異なる reading を要求するケースは `prev_eq_any` などで
literal 列挙する。

### core/ に entry 不在 (= 新規追加要)

- `一人` (2 字)
- `一人前` (3 字)
- `一体` (2 字)
- `一時` (2 字)
- `一月` (2 字)
- `一杯` (2 字)
- `一生` (2 字)
- `一番` (2 字)
- `一緒` (2 字)
- `一行` (2 字)
- `二人` (2 字)
- `二月` (2 字)
- `人気` (2 字)
- `今月` (2 字)
- `何人` (2 字)
- `何回` (2 字)
- `何度` (2 字)
- `何日` (2 字)
- `大人気` (3 字)
- `方々` (2 字)
- `被る` (2 字)

### default 不在 rule

- `一月` (= 暫定 default は第 1 match から推定済、 人手確認要)
- `上手` (= 暫定 default は第 1 match から推定済、 人手確認要)
- `下手` (= 暫定 default は第 1 match から推定済、 人手確認要)
- `二月` (= 暫定 default は第 1 match から推定済、 人手確認要)

### core/ 既存 entry への merge (= file 分散)

本 30 surface は対応 core/ entry が既に存在、 inline match を **既存 entry
に merge** すべき。 新規 detailed entry として置くと load 時に簡単 entry が
上書きしてしまう (file 名 sort 順依存) リスクあり。

- `core/jukugo/basic/general.toml` (= 16 surface): `一日`, `上手`, `下手`, `今年`, `今日`, `仲人`, `十分`, `去年`, `大人`, `市場`, `日本`, `明日`, `昨日`, `来年`, `玄人`, `翡翠`
- `core/jukugo/humanities/arts.toml` (= 1 surface): `素人`
- `core/jukugo/nature/weather.toml` (= 1 surface): `寒気`
- `core/unihan/joyo.toml` (= 12 surface): `円`, `半`, `屋`, `差`, `本`, `率`, `約`, `者`, `能`, `表`, `角`, `間`
