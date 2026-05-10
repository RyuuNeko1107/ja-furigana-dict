# tools/migrations/ — 1 回限り machine 変換 script のアーカイブ

本 dir 配下は **既に master / dict release に適用済の 1 回限り migration script**。
`tools/` 直下の継続使用 tool (validate.py / regen_stats.py / list_dups.py 等)
と区別するために移動した。

通常運用では実行しない。 git 履歴の追跡用 + 「過去どんな機械変換があったか」 の reference として保持。

## 履歴

| script | 適用時期 | 役割 |
|---|---|---|
| `add_role_tags.py` | alpha.8 期 | 全 dict / rule TOML の `[meta]` block に `role = "..."` を bulk 追加 (= role 駆動 loader 投入と coordinated) |
| `migrate_v2.py` | alpha.10 期 (★A1b) | 全 file の `[meta]` block に `schema_version = "2"` を bulk 追加 (= lib 必須化と coordinated) |
| `migrate_v2_context.py` | alpha.11 期 (★A2) | `rules/context/*.toml` の `[[rule]]` / `[[rule.match]]` を新 format `[entries."x"]` / `[[entries."x".match]]` に機械変換 (= staging 出力 + TODO report) |
| `merge_migrated_context.py` | alpha.11 期 (★A2) | 上記 staging を実 `core/` file に surgical merge (= simple line 削除 + detailed sub-table 末尾 append) |
| `migrate_kanji_format.py` | alpha.11 期 (★A2) | 旧 `core/single_overrides.toml` の `[entries]` を新 `core/kanji/overrides.toml` の `[[kanji]]` block format に変換 |

## 再走らせる場合

冪等性は概ね担保されているが (= 既設は no-op or skip)、 source file 自体が
削除済 (= rules/context/ + single_overrides.toml は 0.1.0 stable 前 alpha.11 で
削除完了) のため、 殆どの script は 「source 不在 で error 終了」 が普通の挙動。

将来 同種 migration が必要 (例: alpha.X で新 format field 追加) になったら、
これらを **template として参照** + `tools/migrations/<新名>.py` で新規追加する。
