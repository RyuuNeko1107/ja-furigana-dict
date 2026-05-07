# Cross-file duplicates (`core/jukugo/` + `core/works/`)

> `tools/list_dups.py` で自動生成。 commit 前にこのファイルが pull できれば
> どのファイルのどの surface が cross-file 重複してるか一目で分かる。
> divergent reading は `tools/validate.py` が CI で fail させる (修正必須)。

## ⚠️ 異なる reading (0 件 — critical)

(なし — divergent reading 0 件、 健全)

## 同一 reading (166 件)

実害なし (jukugo merge で同値が上書きされても reading 不変)。 整理目安として list 化。
長期的にどちらか 1 ファイルに寄せたいケースを発見する用。

| surface | reading | files |
|---|---|---|
| 一期一会 | イチゴイチエ | `core/jukugo/abstracts.toml`, `core/jukugo/four_char.toml` |
| 一本 | イッポン | `core/jukugo/arts.toml`, `core/jukugo/general.toml` |
| 一蓮托生 | イチレンタクショウ | `core/jukugo/abstracts.toml`, `core/jukugo/four_char.toml` |
| 七五三 | シチゴサン | `core/jukugo/clothes.toml`, `core/jukugo/general.toml` |
| 五月雨 | サミダレ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 京都 | キョウト | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 仙台 | センダイ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 作曲 | サッキョク | `core/jukugo/general.toml`, `core/jukugo/music.toml` |
| 保守 | ホシュ | `core/jukugo/general.toml`, `core/jukugo/politics.toml` |
| 信号 | シンゴウ | `core/jukugo/specialized.toml`, `core/jukugo/vehicles.toml` |
| 俳句 | ハイク | `core/jukugo/abstracts.toml`, `core/jukugo/literature.toml` |
| 六本木 | ロッポンギ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 円周率 | エンシュウリツ | `core/jukugo/general.toml`, `core/jukugo/science.toml` |
| 刑法 | ケイホウ | `core/jukugo/proper_nouns.toml`, `core/jukugo/specialized.toml` |
| 剣道 | ケンドウ | `core/jukugo/arts.toml`, `core/jukugo/general.toml` |
| 半夏生 | ハンゲショウ | `core/jukugo/animals.toml`, `core/jukugo/weather.toml` |
| 参議院 | サンギイン | `core/jukugo/politics.toml`, `core/jukugo/proper_nouns.toml` |
| 合気道 | アイキドウ | `core/jukugo/arts.toml`, `core/jukugo/general.toml` |
| 名古屋 | ナゴヤ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 向日葵 | ヒマワリ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 吹雪 | フブキ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 周波数 | シュウハスウ | `core/jukugo/science.toml`, `core/jukugo/specialized.toml` |
| 味噌 | ミソ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 味噌汁 | ミソシル | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 和歌 | ワカ | `core/jukugo/abstracts.toml`, `core/jukugo/literature.toml` |
| 哀感 | アイカン | `core/jukugo/abstracts.toml`, `core/jukugo/emotions.toml` |
| 品川 | シナガワ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 啄木鳥 | キツツキ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 商法 | ショウホウ | `core/jukugo/proper_nouns.toml`, `core/jukugo/specialized.toml` |
| 啓蟄 | ケイチツ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 善哉 | ゼンザイ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 因果 | インガ | `core/jukugo/abstracts.toml`, `core/jukugo/religions.toml` |
| 因果応報 | インガオウホウ | `core/jukugo/abstracts.toml`, `core/jukugo/four_char.toml` |
| 団子 | ダンゴ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 墓参 | ボサン | `core/jukugo/general.toml`, `core/jukugo/religions.toml` |
| 夏至 | ゲシ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 大阪 | オオサカ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 奈良 | ナラ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 奉納 | ホウノウ | `core/jukugo/arts.toml`, `core/jukugo/religions.toml` |
| 家鴨 | アヒル | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 山茶花 | サザンカ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 山葵 | ワサビ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 川柳 | センリュウ | `core/jukugo/abstracts.toml`, `core/jukugo/literature.toml` |
| 巫女 | ミコ | `core/jukugo/general.toml`, `core/jukugo/religions.toml` |
| 帯域 | タイイキ | `core/jukugo/general.toml`, `core/jukugo/specialized.toml` |
| 広島 | ヒロシマ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 床の間 | とこのま | `core/jukugo/architecture.toml`, `core/jukugo/arts.toml` |
| 床柱 | トコバシラ | `core/jukugo/architecture.toml`, `core/jukugo/arts.toml` |
| 序曲 | ジョキョク | `core/jukugo/general.toml`, `core/jukugo/music.toml` |
| 弓道 | キュウドウ | `core/jukugo/arts.toml`, `core/jukugo/general.toml` |
| 御利益 | ゴリヤク | `core/jukugo/general.toml`, `core/jukugo/religions.toml` |
| 御手洗 | ミタライ | `core/jukugo/general.toml`, `core/jukugo/personal_names.toml` |
| 御茶ノ水 | オチャノミズ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 復号 | フクゴウ | `core/jukugo/general.toml`, `core/jukugo/specialized.toml` |
| 必然 | ヒツゼン | `core/jukugo/abstracts.toml`, `core/jukugo/general.toml` |
| 憲法 | ケンポウ | `core/jukugo/politics.toml`, `core/jukugo/proper_nouns.toml` |
| 戒律 | カイリツ | `core/jukugo/abstracts.toml`, `core/jukugo/religions.toml` |
| 扇子 | センス | `core/jukugo/arts.toml`, `core/jukugo/clothes.toml`, `core/jukugo/general.toml` |
| 批評 | ヒヒョウ | `core/jukugo/general.toml`, `core/jukugo/literature.toml` |
| 拍子 | ヒョウシ | `core/jukugo/general.toml`, `core/jukugo/music.toml` |
| 提灯 | チョウチン | `core/jukugo/architecture.toml`, `core/jukugo/clothes.toml` |
| 摂社 | セッシャ | `core/jukugo/architecture.toml`, `core/jukugo/religions.toml` |
| 数寄屋 | スキヤ | `core/jukugo/architecture.toml`, `core/jukugo/arts.toml` |
| 新宿 | シンジュク | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 旋律 | センリツ | `core/jukugo/general.toml`, `core/jukugo/music.toml` |
| 昆布 | コンブ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 時雨 | シグレ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 暗号化 | アンゴウカ | `core/jukugo/general.toml`, `core/jukugo/specialized.toml` |
| 書道 | ショドウ | `core/jukugo/arts.toml`, `core/jukugo/general.toml` |
| 最中 | モナカ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 木綿 | モメン | `core/jukugo/clothes.toml`, `core/jukugo/general.toml` |
| 末社 | マッシャ | `core/jukugo/architecture.toml`, `core/jukugo/religions.toml` |
| 本歌取 | ホンカドリ | `core/jukugo/abstracts.toml`, `core/jukugo/literature.toml` |
| 札幌 | サッポロ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 枕詞 | マクラコトバ | `core/jukugo/abstracts.toml`, `core/jukugo/literature.toml` |
| 林檎 | リンゴ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 染色 | センショク | `core/jukugo/clothes.toml`, `core/jukugo/science.toml` |
| 梅雨 | ツユ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 検索 | ケンサク | `core/jukugo/general.toml`, `core/jukugo/specialized.toml` |
| 極光 | キョッコウ | `core/jukugo/science.toml`, `core/jukugo/weather.toml` |
| 楽譜 | ガクフ | `core/jukugo/general.toml`, `core/jukugo/music.toml` |
| 標本 | ヒョウホン | `core/jukugo/science.toml`, `core/jukugo/specialized.toml` |
| 横浜 | ヨコハマ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 横笛 | ヨコブエ | `core/jukugo/arts.toml`, `core/jukugo/music.toml` |
| 歌舞伎 | カブキ | `core/jukugo/arts.toml`, `core/jukugo/literature.toml` |
| 民法 | ミンポウ | `core/jukugo/proper_nouns.toml`, `core/jukugo/specialized.toml` |
| 汁粉 | シルコ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 池袋 | イケブクロ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 沈丁花 | ジンチョウゲ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 沈思黙考 | チンシモッコウ | `core/jukugo/emotions.toml`, `core/jukugo/idioms.toml` |
| 沖縄 | オキナワ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 河馬 | カバ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 浴衣 | ユカタ | `core/jukugo/clothes.toml`, `core/jukugo/general.toml` |
| 海月 | クラゲ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 海老 | エビ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 海豚 | イルカ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 渋谷 | シブヤ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 演算 | エンザン | `core/jukugo/general.toml`, `core/jukugo/science.toml` |
| 潜水艦 | センスイカン | `core/jukugo/specialized.toml`, `core/jukugo/vehicles.toml` |
| 灰桜 | ハイザクラ | `core/jukugo/colors.toml`, `core/jukugo/general.toml` |
| 烏賊 | イカ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 無花果 | イチジク | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 焼鳥 | ヤキトリ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 狂言 | キョウゲン | `core/jukugo/arts.toml`, `core/jukugo/literature.toml` |
| 独奏 | ドクソウ | `core/jukugo/general.toml`, `core/jukugo/music.toml` |
| 独活 | ウド | `core/jukugo/animals.toml`, `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 異端 | イタン | `core/jukugo/abstracts.toml`, `core/jukugo/religions.toml` |
| 百舌鳥 | モズ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 短歌 | タンカ | `core/jukugo/abstracts.toml`, `core/jukugo/literature.toml` |
| 石楠花 | シャクナゲ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 砂利 | ジャリ | `core/jukugo/architecture.toml`, `core/jukugo/general.toml` |
| 破戒 | ハカイ | `core/jukugo/literature.toml`, `core/jukugo/religions.toml` |
| 確率 | カクリツ | `core/jukugo/science.toml`, `core/jukugo/specialized.toml` |
| 神戸 | コウベ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 福岡 | フクオカ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 突風 | トップウ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 立冬 | リットウ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 立夏 | リッカ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 立春 | リッシュン | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 立秋 | リッシュウ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 竜巻 | タツマキ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 竹輪 | チクワ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 紅一点 | コウイッテン | `core/jukugo/general.toml`, `core/jukugo/idioms.toml` |
| 素人 | シロウト | `core/jukugo/arts.toml`, `core/jukugo/general.toml` |
| 紫陽花 | アジサイ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 細雪 | ササメユキ | `core/jukugo/literature.toml`, `core/jukugo/weather.toml` |
| 絵巻物 | エマキモノ | `core/jukugo/arts.toml`, `core/jukugo/literature.toml` |
| 編曲 | ヘンキョク | `core/jukugo/general.toml`, `core/jukugo/music.toml` |
| 羊羹 | ヨウカン | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 羽織 | はおり | `core/jukugo/arts.toml`, `core/jukugo/clothes.toml` |
| 能楽 | ノウガク | `core/jukugo/arts.toml`, `core/jukugo/literature.toml` |
| 能面 | ノウメン | `core/jukugo/arts.toml`, `core/jukugo/general.toml` |
| 茶室 | チャシツ | `core/jukugo/architecture.toml`, `core/jukugo/arts.toml` |
| 茶道 | サドウ | `core/jukugo/arts.toml`, `core/jukugo/general.toml` |
| 蒲鉾 | カマボコ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 薙刀 | ナギナタ | `core/jukugo/arts.toml`, `core/jukugo/specialized.toml` |
| 蜻蛉 | トンボ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 蝸牛 | カタツムリ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 蟷螂 | カマキリ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 衆議院 | シュウギイン | `core/jukugo/politics.toml`, `core/jukugo/proper_nouns.toml` |
| 被告人 | ヒコクニン | `core/jukugo/general.toml`, `core/jukugo/specialized.toml` |
| 装束 | ショウゾク | `core/jukugo/arts.toml`, `core/jukugo/clothes.toml` |
| 親子丼 | オヤコドン | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 認証 | ニンショウ | `core/jukugo/general.toml`, `core/jukugo/specialized.toml` |
| 諦観 | テイカン | `core/jukugo/abstracts.toml`, `core/jukugo/emotions.toml` |
| 諸行無常 | ショギョウムジョウ | `core/jukugo/abstracts.toml`, `core/jukugo/four_char.toml` |
| 質素 | シッソ | `core/jukugo/abstracts.toml`, `core/jukugo/arts.toml` |
| 足袋 | タビ | `core/jukugo/clothes.toml`, `core/jukugo/general.toml` |
| 跳躍 | チョウヤク | `core/jukugo/music.toml`, `core/jukugo/sports.toml` |
| 躑躅 | ツツジ | `core/jukugo/animals.toml`, `core/jukugo/general.toml` |
| 輪廻 | リンネ | `core/jukugo/abstracts.toml`, `core/jukugo/religions.toml` |
| 通信 | ツウシン | `core/jukugo/general.toml`, `core/jukugo/specialized.toml` |
| 連歌 | レンガ | `core/jukugo/abstracts.toml`, `core/jukugo/arts.toml`, `core/jukugo/literature.toml` |
| 達観 | タッカン | `core/jukugo/abstracts.toml`, `core/jukugo/emotions.toml` |
| 郊外 | コウガイ | `core/jukugo/architecture.toml`, `core/jukugo/general.toml` |
| 重要文化財 | ジュウヨウブンカザイ | `core/jukugo/general.toml`, `core/jukugo/proper_nouns.toml` |
| 金閣寺 | キンカクジ | `core/jukugo/literature.toml`, `core/jukugo/place_names.toml` |
| 銀座 | ギンザ | `core/jukugo/general.toml`, `core/jukugo/place_names.toml` |
| 閲覧 | エツラン | `core/jukugo/general.toml`, `core/jukugo/politics.toml` |
| 雅楽 | ガガク | `core/jukugo/arts.toml`, `core/jukugo/music.toml` |
| 雨水 | ウスイ | `core/jukugo/general.toml`, `core/jukugo/weather.toml` |
| 霧雨 | キリサメ | `core/jukugo/weather.toml`, `core/works/game/touhou.toml` |
| 音色 | ネイロ | `core/jukugo/general.toml`, `core/jukugo/music.toml` |
| 饅頭 | マンジュウ | `core/jukugo/foods.toml`, `core/jukugo/general.toml` |
| 馬場 | ババ | `core/jukugo/architecture.toml`, `core/jukugo/sports.toml` |
| 鳥居 | トリイ | `core/jukugo/architecture.toml`, `core/jukugo/religions.toml` |
