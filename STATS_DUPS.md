# Cross-file duplicates (`core/jukugo/` + `core/works/`)

> `tools/list_dups.py` で自動生成。 commit 前にこのファイルが pull できれば
> どのファイルのどの surface が cross-file 重複してるか一目で分かる。
> divergent reading は `tools/validate.py` が CI で fail させる (修正必須)。

## ⚠️ 異なる reading (0 件 — critical)

(なし — divergent reading 0 件、 健全)

## 同一 reading (8 件)

実害なし (jukugo merge で同値が上書きされても reading 不変)。 整理目安として list 化。
長期的にどちらか 1 ファイルに寄せたいケースを発見する用。

| surface | reading | files |
|---|---|---|
| 上方修正 | ジョウホウシュウセイ | `core/jukugo/basic/four_char.toml`, `core/jukugo/basic/general.toml` |
| 厳密 | ゲンミツ | `core/jukugo/basic/general.toml`, `core/jukugo/basic/split_guard.toml` |
| 地固まる | ジカタマル | `core/jukugo/basic/general.toml`, `core/jukugo/humanities/idioms.toml` |
| 扇要 | オウギカナメ | `core/jukugo/basic/general.toml`, `core/works/anime/geass.toml` |
| 桃鈴家 | モモスズケ | `core/jukugo/basic/general.toml`, `core/works/vtuber/hololive.toml` |
| 精密 | セイミツ | `core/jukugo/basic/general.toml`, `core/jukugo/basic/split_guard.toml` |
| 背高のっぽ | セイタカノッポ | `core/jukugo/basic/general.toml`, `core/jukugo/nature/body_parts.toml` |
| 黒閃 | コクセン | `core/jukugo/basic/general.toml`, `core/works/anime/jujutsu.toml` |
