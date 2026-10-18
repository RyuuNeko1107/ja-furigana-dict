# Cross-file duplicates (`core/jukugo/` + `core/works/`)

> `tools/list_dups.py` で自動生成。 commit 前にこのファイルが pull できれば
> どのファイルのどの surface が cross-file 重複してるか一目で分かる。
> divergent reading は `tools/validate.py` が CI で fail させる (修正必須)。

## ⚠️ 異なる reading (0 件 — critical)

(なし — divergent reading 0 件、 健全)

## 同一 reading (12 件)

実害なし (jukugo merge で同値が上書きされても reading 不変)。 整理目安として list 化。
長期的にどちらか 1 ファイルに寄せたいケースを発見する用。

| surface | reading | files |
|---|---|---|
| 三峰結華 | ミツミネユイカ | `core/jukugo/basic/compounds.toml`, `core/works/game/idolmaster.toml` |
| 中田宏 | ナカダヒロシ | `core/jukugo/basic/general.toml`, `core/jukugo/proper/diet_members.toml` |
| 宗主国 | ソウシュコク | `core/jukugo/basic/compounds.toml`, `core/jukugo/basic/general.toml` |
| 小沢征悦 | オザワユキヨシ | `core/jukugo/basic/compounds.toml`, `core/jukugo/proper/people.toml` |
| 扇要 | オウギカナメ | `core/jukugo/basic/general.toml`, `core/works/anime/geass.toml` |
| 日朝関係 | にっちょうかんけい | `core/jukugo/proper/wiki_place_names.toml`, `core/jukugo/society/terms.toml` |
| 時々刻々 | ジジコクコク | `core/jukugo/basic/compounds.toml`, `core/jukugo/basic/general.toml` |
| 片頭痛 | ヘンズツウ | `core/jukugo/basic/compounds.toml`, `core/jukugo/basic/general.toml` |
| 紂王 | チュウオウ | `core/jukugo/basic/compounds.toml`, `core/jukugo/proper/people.toml` |
| 自己資本比率 | ジコシホンヒリツ | `core/jukugo/basic/compounds.toml`, `core/jukugo/society/finance.toml` |
| 西村康稔 | ニシムラヤストシ | `core/jukugo/proper/diet_members.toml`, `core/jukugo/proper/people.toml` |
| 麻辣湯 | マーラータン | `core/jukugo/basic/compounds.toml`, `core/jukugo/basic/general.toml` |
