# Cross-file duplicates (`core/jukugo/` + `core/works/`)

> `tools/list_dups.py` で自動生成。 commit 前にこのファイルが pull できれば
> どのファイルのどの surface が cross-file 重複してるか一目で分かる。
> divergent reading は `tools/validate.py` が CI で fail させる (修正必須)。

## ⚠️ 異なる reading (0 件 — critical)

(なし — divergent reading 0 件、 健全)

## 同一 reading (14 件)

実害なし (jukugo merge で同値が上書きされても reading 不変)。 整理目安として list 化。
長期的にどちらか 1 ファイルに寄せたいケースを発見する用。

| surface | reading | files |
|---|---|---|
| 七竈 | ナナカマド | `core/jukugo/basic/general.toml`, `core/jukugo/nature/plants.toml` |
| 勢理客 | ジッチャク | `core/jukugo/nature/place_names.toml`, `core/jukugo/proper/surnames.toml` |
| 単衣 | ヒトエ | `core/jukugo/basic/general.toml`, `core/jukugo/objects/clothes.toml` |
| 台詞 | セリフ | `core/jukugo/basic/general.toml`, `core/jukugo/basic/stream_round_20260526.toml` |
| 唐揚げ | カラアゲ | `core/jukugo/basic/general.toml`, `core/jukugo/nature/foods.toml` |
| 喜屋武 | キャン | `core/jukugo/nature/place_names.toml`, `core/jukugo/proper/surnames.toml` |
| 四十物 | アイモノ | `core/jukugo/proper/surnames.toml`, `core/works/game/hypmic.toml` |
| 巫女 | ミコ | `core/jukugo/basic/general.toml`, `core/jukugo/humanities/religions.toml` |
| 東風平 | コチンダ | `core/jukugo/nature/place_names.toml`, `core/jukugo/proper/surnames.toml` |
| 栗花落 | ツユリ | `core/jukugo/proper/surnames.toml`, `core/works/anime/kimetsu.toml` |
| 海風 | ウミカゼ | `core/jukugo/basic/general.toml`, `core/jukugo/nature/weather.toml` |
| 百目鬼 | ドウメキ | `core/jukugo/proper/surnames.toml`, `core/works/anime/xxxholic.toml` |
| 酢漿草 | カタバミ | `core/jukugo/nature/animals.toml`, `core/jukugo/nature/plants.toml` |
| 鰻丼 | ウナドン | `core/jukugo/basic/general.toml`, `core/jukugo/nature/foods.toml` |
