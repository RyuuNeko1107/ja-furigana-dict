# Stats — `ja-furigana-dict`

辞書ボリュームのスナップショット。配布時の中身を一覧で把握する用。
git に commit されている master HEAD の状態を基準にする。

> 列の意味:
> - **エントリ数**: `[entries]` / `[map]` / `[[rule]]` 等の有効レコード数
> - **サイズ**: コメント / 空行を除いた実効サイズ (lib `toml::from_str` は parse 時にコメントを
>   drop するので、 disk file size より memory load の概算に近い)
>
> inline test (`*.test.toml`) と corpus regression (`tests/corpus/*.toml`) のカバレッジは
> 末尾の [QA カバレッジ](#qa-カバレッジ) section に独立してまとめてある。
> release tar から exclude / lib runtime memory にも乗らないため、 データ集計とは別軸で扱う
> (サイズも release 影響無しのため省略)。

> サマリ・件数表は `.github/workflows/regen-stats.yml` で **GitHub 側で自動再生成 + auto-commit**。
> contributor は TOML を編集して push (or PR merge) するだけで OK。
> 用途列は各ファイル冒頭の `[meta] description = "..."` から自動取得。
> ナラティブ部分 (利用側メモリ寄与 / カバレッジの偏り) は手動メンテ。

## サマリ

<!-- AUTO-GENERATED:SUMMARY:BEGIN -->
| カテゴリ | エントリ数 | サイズ |
|---|---:|---:|
| [**単漢字**](#単漢字) (`core/unihan/*`、 水準別 5 ファイル) | **40,671** | **728 KB** |
| [**熟語**](#熟語) (`core/jukugo/*`、手動 PR メンテ) | **21,346** | **880 KB** |
| [**作品造語**](#作品造語) (`core/works/*`、作品単位 1 ファイル) | **1,677** | **132 KB** |
| [**外来語**](#外来語) (`core/loanwords/*`、IT 用語等の英字 surface) | **1,712** | **44 KB** |
| [**分類前 inbox**](#分類前-inbox) (`core/_inbox.toml`、 後で振り分ける一時置き場) | **15** | **1.7 KB** |
| [**単漢字 [[kanji]] format**](#単漢字-kanji-format) (`core/kanji/*`、 default + 文脈分岐 reading) | **2,778** | **356 KB** |
| [**異体字**](#異体字) (`core/compat.toml`) | **0** | **0 B** |
| [**エンジンルール**](#エンジンルール) (`rules/`) | **771** | **37 KB** |
| **合計** | **68,970** | **2.13 MB** |
<!-- AUTO-GENERATED:SUMMARY:END -->

## 内訳

`core/` (語彙辞書) はカテゴリ別 sub-section に、 `rules/` (エンジンルール) は最後にまとめて。 summary 表のカテゴリ名クリックで該当 sub-section へジャンプ可。

<!-- AUTO-GENERATED:CORE:BEGIN -->
### 単漢字

`core/unihan/*` — 水準別 5 ファイル。 lib の resolve_reading 6 段階で最終 fallback (Step 6) として参照される。 default reading review は使用頻度の高い `joyo.toml` を中心に。

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/unihan/joyo.toml`](core/unihan/joyo.toml) | 9 | 1018 B | 常用漢字 2,136 字 (文化庁 2010-11-30 改訂、 内閣告示) — 利用頻度高、 default reading review 対象 |
| [`core/unihan/jinmeiyou.toml`](core/unihan/jinmeiyou.toml) | 0 | 185 B | 人名用漢字 (法務省、 子の名に使用可、 常用と重複する 128 字を除外した残り 855 字) |
| [`core/unihan/jis_basic.toml`](core/unihan/jis_basic.toml) | 13,034 | 229 KB | JIS 基本 (CJK Basic Block U+4E00-U+9FFF のうち常用 / 人名用以外、 概ね JIS X 0208 第1+第2水準カバー) |
| [`core/unihan/jis_supplement.toml`](core/unihan/jis_supplement.toml) | 4,825 | 83 KB | JIS 補助 (CJK Extension A + Compatibility Ideographs、 概ね JIS X 0213 第3+第4水準カバー) |
| [`core/unihan/extension.toml`](core/unihan/extension.toml) | 22,803 | 415 KB | 拡張漢字 (CJK Extension B 以降、 表外字 / 中国専用字 / 異体字、 機械的扱い、 ほぼ lib lookup されない) |
| **小計** (5 ファイル) | **40,671** | **728 KB** | |

### 熟語

`core/jukugo/<genre>/*` — 手動 PR メンテのジャンル別 jukugo (≥ 2 字 surface)。 lib の Step 3 (jukugo lookup) で Lindera より優先採用。 各 genre dir の `_genre.toml` がカテゴリ description を持つ。

**合計**: 21,346 件 / 880 KB (genre 6 区分)

#### 自然・生命

動植物 / 食品 / 気象 / 体の部位 / 地名 / 自然科学 — 自然界と生物に関わる語彙

`core/jukugo/nature/` — 10 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/nature/animals.toml`](core/jukugo/nature/animals.toml) | 1,215 | 39 KB | 動植物 / 魚介 / 鳥 / 昆虫 / 茸 / 海藻の難読 |
| [`core/jukugo/nature/place_names.toml`](core/jukugo/nature/place_names.toml) | 819 | 39 KB | 地名 (47 都道府県 / 主要都市 / 駅 / 寺社仏閣 / 観光地) |
| [`core/jukugo/nature/foods.toml`](core/jukugo/nature/foods.toml) | 498 | 19 KB | 食べ物 / 料理 / 和菓子 / 郷土料理 / 食材 / 調味料 |
| [`core/jukugo/nature/plants.toml`](core/jukugo/nature/plants.toml) | 404 | 13 KB | 植物 / 花 / 樹木 / 草本の難読 (熟字訓) |
| [`core/jukugo/nature/weather.toml`](core/jukugo/nature/weather.toml) | 283 | 11 KB | 気象 / 天候 / 季語的気象 / 二十四節気 / 海洋気象 |
| [`core/jukugo/nature/science.toml`](core/jukugo/nature/science.toml) | 270 | 9.9 KB | 自然科学 (天文 / 物理 / 化学 / 生物 / 地学) |
| [`core/jukugo/nature/body_parts.toml`](core/jukugo/nature/body_parts.toml) | 65 | 2.8 KB | 体の部位 / 内臓 / 骨格 / 筋肉 / 神経 |
| [`core/jukugo/nature/math.toml`](core/jukugo/nature/math.toml) | 52 | 2.2 KB | 数学 (解析 / 線形代数 / 集合論 / 統計 / 確率の難読) |
| [`core/jukugo/nature/mountaineering.toml`](core/jukugo/nature/mountaineering.toml) | 12 | 751 B | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/nature/agriculture.toml`](core/jukugo/nature/agriculture.toml) | 5 | 356 B | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| **小計** (10 ファイル) | **3,623** | **137 KB** | |

#### 人文・芸術

古典文学 / 芸術 / 慣用句 / 抽象概念 / 音楽 / 宗教 / 感情 — 人の精神活動に関わる語彙

`core/jukugo/humanities/` — 9 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/humanities/arts.toml`](core/jukugo/humanities/arts.toml) | 2,780 | 104 KB | 古典芸能 / 武道 / 茶華香 / 工芸 |
| [`core/jukugo/humanities/religions.toml`](core/jukugo/humanities/religions.toml) | 903 | 35 KB | 神道 / 仏教 / キリスト教 / イスラム / 儀礼 |
| [`core/jukugo/humanities/literature.toml`](core/jukugo/humanities/literature.toml) | 608 | 23 KB | 古典文学 / 作品名 / 文学用語 / 詩歌 / 評論 |
| [`core/jukugo/humanities/shinwa.toml`](core/jukugo/humanities/shinwa.toml) | 224 | 10 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/humanities/folklore.toml`](core/jukugo/humanities/folklore.toml) | 164 | 6.7 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/humanities/idioms.toml`](core/jukugo/humanities/idioms.toml) | 109 | 6.1 KB | 慣用句 / ことわざ / 故事成語 (フレーズ単位) |
| [`core/jukugo/humanities/music.toml`](core/jukugo/humanities/music.toml) | 101 | 4.1 KB | 音楽ジャンル / 楽典 / 楽器 / 演奏 / 音楽用語 |
| [`core/jukugo/humanities/abstracts.toml`](core/jukugo/humanities/abstracts.toml) | 18 | 1.2 KB | 美意識 / 古典文学 / 仏教 / 儒教 / 思想 |
| [`core/jukugo/humanities/emotions.toml`](core/jukugo/humanities/emotions.toml) | 10 | 658 B | 感情 / 心理状態 / 性格 / 心情 |
| **小計** (9 ファイル) | **4,917** | **190 KB** | |

#### 社会・制度

政治 / 金融 / スポーツ / 専門用語 / 歴史制度 / 伝統遊戯 — 社会構造 / 制度に関わる語彙

`core/jukugo/society/` — 12 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/society/history.toml`](core/jukugo/society/history.toml) | 1,034 | 38 KB | 歴史用語 (日本史の制度 / 事件 / 文化概念) |
| [`core/jukugo/society/medicine.toml`](core/jukugo/society/medicine.toml) | 894 | 31 KB | 医学 / 医療 (病名 / 症状 / 解剖 / 処置の難読) |
| [`core/jukugo/society/finance.toml`](core/jukugo/society/finance.toml) | 140 | 5.7 KB | 経済金融 (商品 / 市場 / 会計 / 税務 / 保険) |
| [`core/jukugo/society/games.toml`](core/jukugo/society/games.toml) | 130 | 4.3 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/society/specialized.toml`](core/jukugo/society/specialized.toml) | 110 | 6.4 KB | 専門用語 (医学 / 軍事 / 法学 / 経済 / IT / 工学) |
| [`core/jukugo/society/law.toml`](core/jukugo/society/law.toml) | 70 | 2.7 KB | 法律 / 司法 (民法 / 刑法 / 訴訟 / 会社法 / 相続) |
| [`core/jukugo/society/mahjong.toml`](core/jukugo/society/mahjong.toml) | 64 | 3.9 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/society/sports.toml`](core/jukugo/society/sports.toml) | 53 | 3.6 KB | 近代スポーツ / 球技 / 陸上 / 水泳 / 体操 / 大会 |
| [`core/jukugo/society/shogi.toml`](core/jukugo/society/shogi.toml) | 14 | 969 B | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/society/politics.toml`](core/jukugo/society/politics.toml) | 10 | 883 B | 政治 / 行政 / 立法 / 司法 / 国際関係 |
| [`core/jukugo/society/horse_racing.toml`](core/jukugo/society/horse_racing.toml) | 9 | 798 B | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/society/fishing.toml`](core/jukugo/society/fishing.toml) | 8 | 611 B | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| **小計** (12 ファイル) | **2,536** | **98 KB** | |

#### 固有名詞

人名 / 大学・官庁・元号などの固有名詞 — 個別実体を指す語彙

`core/jukugo/proper/` — 5 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/proper/personal_names.toml`](core/jukugo/proper/personal_names.toml) | 290 | 18 KB | 人名 (戦国 / 平安 / 江戸 / 明治大正 / 古典作家、現代私人除く) |
| [`core/jukugo/proper/surnames.toml`](core/jukugo/proper/surnames.toml) | 160 | 22 KB | 難読姓 (苗字) の読み (姓単体、代表読み) |
| [`core/jukugo/proper/sumo_shikona.toml`](core/jukugo/proper/sumo_shikona.toml) | 45 | 3.4 KB | 大相撲 力士の四股名 (公式読み) |
| [`core/jukugo/proper/proper_nouns.toml`](core/jukugo/proper/proper_nouns.toml) | 36 | 2.1 KB | 固有名詞 (大学 / 中央官庁 / 元号 / 歴史的事象、PR 募集中) |
| [`core/jukugo/proper/sake_brands.toml`](core/jukugo/proper/sake_brands.toml) | 33 | 2.3 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| **小計** (5 ファイル) | **564** | **48 KB** | |

#### 物体・工芸

色 / 衣服 / 乗り物 / 建築 / 鉄道 / 道具 / 武具 — 人工物と工芸に関わる語彙

`core/jukugo/objects/` — 7 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/objects/architecture.toml`](core/jukugo/objects/architecture.toml) | 416 | 15 KB | 建築 / 建造物 / 寺社建築 / 城郭 / 庭園 |
| [`core/jukugo/objects/colors.toml`](core/jukugo/objects/colors.toml) | 414 | 13 KB | 色名 / 染色 / 模様 / 古典色 / 鉱物色 |
| [`core/jukugo/objects/weapons.toml`](core/jukugo/objects/weapons.toml) | 402 | 16 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/objects/tools.toml`](core/jukugo/objects/tools.toml) | 273 | 8.8 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/objects/vehicles.toml`](core/jukugo/objects/vehicles.toml) | 177 | 6.1 KB | 乗り物 / 交通手段 / 船舶 / 航空 / 鉄道 |
| [`core/jukugo/objects/clothes.toml`](core/jukugo/objects/clothes.toml) | 90 | 3.2 KB | 衣服 / 装束 / アクセサリー / 履物 |
| [`core/jukugo/objects/railway.toml`](core/jukugo/objects/railway.toml) | 13 | 946 B | 鉄道専門用語 (線路 / 駅 / 運行 / 車両) |
| **小計** (7 ファイル) | **1,785** | **63 KB** | |

#### 基本・構造

一般熟語 / 四字熟語 — 全カテゴリに横断する基本語彙

`core/jukugo/basic/` — 3 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/basic/general.toml`](core/jukugo/basic/general.toml) | 7,853 | 337 KB | 二字・三字の一般熟語 (季節 / 行事 / 慣用句 含む) |
| [`core/jukugo/basic/four_char.toml`](core/jukugo/basic/four_char.toml) | 35 | 2.4 KB | 四字熟語 (4 字 + 全 CJK 漢字) |
| [`core/jukugo/basic/split_guard.toml`](core/jukugo/basic/split_guard.toml) | 33 | 4.0 KB | Lindera の 「熟語 + か」 分割に負けないための tie-break entry |
| **小計** (3 ファイル) | **7,921** | **343 KB** | |


### 作品造語

`core/works/<medium>/*` — 媒体 (game / literature 等) ごとに 1 作品 1 ファイル。 原則は公式読み (一般通称として定着していれば採録可)、 出典コメント必須、 古典読みは現代読み無い場合のみ。

**合計**: 1,677 件 / 132 KB (genre 4 区分)

#### ゲーム

ゲーム作品の固有名詞 (キャラクター / 場所 / 用語、 公式読みベース)

`core/works/game/` — 23 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/works/game/touhou.toml`](core/works/game/touhou.toml) | 269 | 9.2 KB | 東方Project (上海アリス幻樂団): キャラクター名 / 場所 / 用語 (公式読みベース) |
| [`core/works/game/idolmaster.toml`](core/works/game/idolmaster.toml) | 64 | 5.3 KB | アイドルマスター (バンダイナムコ): キャラクター名 |
| [`core/works/game/sangokushi.toml`](core/works/game/sangokushi.toml) | 45 | 3.1 KB | 三国志 (演義/ゲーム/漫画): 武将名 (日本語音読み) |
| [`core/works/game/touken_ranbu.toml`](core/works/game/touken_ranbu.toml) | 33 | 3.0 KB | 刀剣乱舞 (ニトロプラス): 刀剣男士名 |
| [`core/works/game/genshin.toml`](core/works/game/genshin.toml) | 27 | 2.3 KB | 原神 (HoYoverse): キャラクター名 (公式日本語読みベース) |
| [`core/works/game/hypmic.toml`](core/works/game/hypmic.toml) | 23 | 1.8 KB | ヒプノシスマイク (キングレコード): キャラクター名 |
| [`core/works/game/lovelive.toml`](core/works/game/lovelive.toml) | 23 | 1.8 KB | ラブライブ! (サンライズ): キャラクター名 |
| [`core/works/game/ensemble_stars.toml`](core/works/game/ensemble_stars.toml) | 19 | 1.7 KB | あんさんぶるスターズ! (Happy Elements): キャラクター名 |
| [`core/works/game/_minor.toml`](core/works/game/_minor.toml) | 18 | 1.5 KB | ゲーム 小規模作品 統合 (1作品1-3語、2026-06-21 consolidate) |
| [`core/works/game/persona.toml`](core/works/game/persona.toml) | 18 | 1.5 KB | ペルソナ (アトラス): キャラクター名 |
| [`core/works/game/project_sekai.toml`](core/works/game/project_sekai.toml) | 18 | 1.4 KB | プロジェクトセカイ: キャラクター名 |
| [`core/works/game/danganronpa.toml`](core/works/game/danganronpa.toml) | 16 | 1.3 KB | ダンガンロンパ: キャラクター名 |
| [`core/works/game/vocaloid.toml`](core/works/game/vocaloid.toml) | 16 | 1.4 KB | ボーカロイド/合成音声: キャラクター名 (公式読み) |
| [`core/works/game/fate.toml`](core/works/game/fate.toml) | 14 | 1.2 KB | Fate / 型月 (TYPE-MOON): キャラクター名 |
| [`core/works/game/honkai_starrail.toml`](core/works/game/honkai_starrail.toml) | 12 | 930 B | 崩壊:スターレイル (HoYoverse): キャラクター名 (公式日本語読みベース) |
| [`core/works/game/bluearchive.toml`](core/works/game/bluearchive.toml) | 10 | 911 B | ブルーアーカイブ (Nexon/Yostar): キャラクター名 (公式読みベース) |
| [`core/works/game/kankore.toml`](core/works/game/kankore.toml) | 9 | 938 B | 艦これ: 艦娘名 (旧海軍艦名) |
| [`core/works/game/gyakuten.toml`](core/works/game/gyakuten.toml) | 8 | 710 B | 逆転裁判: キャラクター名 |
| [`core/works/game/ryu_ga_gotoku.toml`](core/works/game/ryu_ga_gotoku.toml) | 6 | 517 B | 龍が如く: キャラクター名 |
| [`core/works/game/bang_dream.toml`](core/works/game/bang_dream.toml) | 5 | 524 B | BanG Dream! : キャラクター名 |
| [`core/works/game/tokimeki.toml`](core/works/game/tokimeki.toml) | 5 | 465 B | ときめきメモリアル: キャラクター名 |
| [`core/works/game/a3.toml`](core/works/game/a3.toml) | 4 | 396 B | A3! : キャラクター名 |
| [`core/works/game/utapri.toml`](core/works/game/utapri.toml) | 4 | 492 B | うたの☆プリンスさまっ♪ : キャラクター名 |
| **小計** (23 ファイル) | **666** | **42 KB** | |

#### 文学

文学作品の固有名詞 (登場人物 / 巻名 / 場所、 古典定本ベース)

`core/works/literature/` — 1 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/works/literature/genji_monogatari.toml`](core/works/literature/genji_monogatari.toml) | 42 | 1.3 KB | 源氏物語 (紫式部): 登場人物 / 巻名 / 場所 (平安中期、 古典定本ベース) |

#### アニメ・漫画

アニメ / 漫画作品の固有名詞 (キャラクター / 場所 / 用語、 公式読みベース)

`core/works/anime/` — 56 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/works/anime/_minor.toml`](core/works/anime/_minor.toml) | 106 | 9.5 KB | アニメ/漫画 小規模作品 統合 (1作品1-3語、2026-06-21 consolidate) |
| [`core/works/anime/conan.toml`](core/works/anime/conan.toml) | 51 | 4.4 KB | 名探偵コナン (青山剛昌): キャラクター名 (公式読みベース) |
| [`core/works/anime/jujutsu.toml`](core/works/anime/jujutsu.toml) | 47 | 3.6 KB | 呪術廻戦 (芥見下々): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/kimetsu.toml`](core/works/anime/kimetsu.toml) | 45 | 4.0 KB | 鬼滅の刃 (吾峠呼世晴): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/bleach.toml`](core/works/anime/bleach.toml) | 38 | 3.6 KB | BLEACH (久保帯人) キャラ名・用語 |
| [`core/works/anime/heroaca.toml`](core/works/anime/heroaca.toml) | 34 | 3.3 KB | 僕のヒーローアカデミア (堀越耕平): キャラクター名 (公式読みベース) |
| [`core/works/anime/haikyu.toml`](core/works/anime/haikyu.toml) | 32 | 2.8 KB | ハイキュー!! (古舘春一): キャラクター名 (公式読みベース) |
| [`core/works/anime/kingdom.toml`](core/works/anime/kingdom.toml) | 31 | 2.2 KB | キングダム (原泰久): キャラクター名 (古代中国名の難読読み) |
| [`core/works/anime/jojo.toml`](core/works/anime/jojo.toml) | 30 | 3.0 KB | ジョジョの奇妙な冒険 (荒木飛呂彦): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/toaru.toml`](core/works/anime/toaru.toml) | 29 | 2.9 KB | とある魔術の禁書目録 / 超電磁砲 (鎌池和馬): キャラクター名 |
| [`core/works/anime/gintama.toml`](core/works/anime/gintama.toml) | 26 | 2.4 KB | 銀魂 (空知英秋): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/naruto.toml`](core/works/anime/naruto.toml) | 24 | 1.9 KB | NARUTO (岸本斉史): キャラクター名 (公式読みベース) |
| [`core/works/anime/tenipuri.toml`](core/works/anime/tenipuri.toml) | 22 | 1.9 KB | テニスの王子様 (許斐剛): キャラクター名 |
| [`core/works/anime/onepiece.toml`](core/works/anime/onepiece.toml) | 18 | 1.5 KB | ONE PIECE (尾田栄一郎): キャラクター名 / 用語 |
| [`core/works/anime/tokyo_revengers.toml`](core/works/anime/tokyo_revengers.toml) | 18 | 1.6 KB | 東京卍リベンジャーズ (和久井健): キャラクター名 (公式読みベース) |
| [`core/works/anime/kurobas.toml`](core/works/anime/kurobas.toml) | 17 | 1.5 KB | 黒子のバスケ (藤巻忠俊): キャラクター名 |
| [`core/works/anime/bluelock.toml`](core/works/anime/bluelock.toml) | 16 | 1.4 KB | ブルーロック (金城宗幸/ノ村優介): キャラクター名 |
| [`core/works/anime/yuyuhakusho.toml`](core/works/anime/yuyuhakusho.toml) | 15 | 1.2 KB | 幽☆遊☆白書 (冨樫義博): キャラクター名 |
| [`core/works/anime/monogatari.toml`](core/works/anime/monogatari.toml) | 14 | 1.5 KB | 〈物語〉シリーズ (西尾維新): 作品名 (公式読みベース) |
| [`core/works/anime/tokyoghoul.toml`](core/works/anime/tokyoghoul.toml) | 13 | 1.4 KB | 東京喰種 (石田スイ): キャラクター名 / 用語 |
| [`core/works/anime/slamdunk.toml`](core/works/anime/slamdunk.toml) | 12 | 1.0 KB | SLAM DUNK (井上雄彦): キャラクター名 |
| [`core/works/anime/houshin.toml`](core/works/anime/houshin.toml) | 11 | 825 B | 封神演義: キャラクター名 / 用語 |
| [`core/works/anime/precure.toml`](core/works/anime/precure.toml) | 10 | 869 B | プリキュア: キャラクター名 |
| [`core/works/anime/rurouni.toml`](core/works/anime/rurouni.toml) | 10 | 1.1 KB | るろうに剣心 (和月伸宏): キャラクター名 |
| [`core/works/anime/garupan.toml`](core/works/anime/garupan.toml) | 8 | 656 B | ガルパン: キャラクター名 |
| [`core/works/anime/gochiusa.toml`](core/works/anime/gochiusa.toml) | 8 | 648 B | ごちうさ: キャラクター名 |
| [`core/works/anime/kyoani.toml`](core/works/anime/kyoani.toml) | 8 | 751 B | 京アニ作品: キャラクター名 |
| [`core/works/anime/recent_anime.toml`](core/works/anime/recent_anime.toml) | 8 | 810 B | 近年アニメ: キャラクター名 |
| [`core/works/anime/soma.toml`](core/works/anime/soma.toml) | 8 | 916 B | 食戟のソーマ: キャラクター名 |
| [`core/works/anime/baseball_manga.toml`](core/works/anime/baseball_manga.toml) | 7 | 709 B | 野球漫画: キャラクター名 |
| [`core/works/anime/captsubasa.toml`](core/works/anime/captsubasa.toml) | 7 | 684 B | キャプテン翼: キャラクター名 |
| [`core/works/anime/kusuriya.toml`](core/works/anime/kusuriya.toml) | 7 | 597 B | 薬屋のひとりごと (日向夏): キャラクター名 (公式読みベース) |
| [`core/works/anime/ranma.toml`](core/works/anime/ranma.toml) | 7 | 677 B | らんま1/2: キャラクター名 |
| [`core/works/anime/saiki.toml`](core/works/anime/saiki.toml) | 7 | 816 B | 斉木楠雄のΨ難 (麻生周一): キャラクター名 |
| [`core/works/anime/shoujo.toml`](core/works/anime/shoujo.toml) | 7 | 688 B | 少女漫画: キャラクター名 |
| [`core/works/anime/tokusatsu.toml`](core/works/anime/tokusatsu.toml) | 7 | 695 B | 仮面ライダー: キャラクター名 |
| [`core/works/anime/goldenkamuy.toml`](core/works/anime/goldenkamuy.toml) | 6 | 770 B | ゴールデンカムイ (野田サトル): キャラクター名 |
| [`core/works/anime/kirara.toml`](core/works/anime/kirara.toml) | 6 | 764 B | きらら系アニメ: キャラクター名 |
| [`core/works/anime/kokumin_anime.toml`](core/works/anime/kokumin_anime.toml) | 6 | 577 B | 国民的アニメ: キャラクター名 |
| [`core/works/anime/saki.toml`](core/works/anime/saki.toml) | 6 | 503 B | 咲-Saki-: キャラクター名 |
| [`core/works/anime/sao_date.toml`](core/works/anime/sao_date.toml) | 6 | 592 B | SAO/デート・ア・ライブ: キャラクター名 |
| [`core/works/anime/ccsakura.toml`](core/works/anime/ccsakura.toml) | 5 | 643 B | カードキャプターさくら (CLAMP): キャラクター名 |
| [`core/works/anime/dragonball.toml`](core/works/anime/dragonball.toml) | 5 | 536 B | ドラゴンボール (鳥山明): キャラクター名 (公式読みベース) |
| [`core/works/anime/geass.toml`](core/works/anime/geass.toml) | 5 | 566 B | コードギアス: キャラクター名 |
| [`core/works/anime/ghibli.toml`](core/works/anime/ghibli.toml) | 5 | 642 B | スタジオジブリ: キャラクター名 / 用語 / 作品名 |
| [`core/works/anime/lupin.toml`](core/works/anime/lupin.toml) | 5 | 469 B | ルパン三世/グルメ漫画: キャラクター名 |
| [`core/works/anime/cityhunter.toml`](core/works/anime/cityhunter.toml) | 4 | 378 B | シティーハンター: キャラクター名 |
| [`core/works/anime/drstone.toml`](core/works/anime/drstone.toml) | 4 | 432 B | Dr.STONE (稲垣理一郎/Boichi): キャラクター名 |
| [`core/works/anime/evangelion.toml`](core/works/anime/evangelion.toml) | 4 | 454 B | 新世紀エヴァンゲリオン (カラー): キャラクター名 (姓) |
| [`core/works/anime/eyeshield21.toml`](core/works/anime/eyeshield21.toml) | 4 | 493 B | アイシールド21: キャラクター名 |
| [`core/works/anime/furuba.toml`](core/works/anime/furuba.toml) | 4 | 628 B | フルーツバスケット (高屋奈月): キャラクター名 |
| [`core/works/anime/gotoubun.toml`](core/works/anime/gotoubun.toml) | 4 | 446 B | 五等分の花嫁 (春場ねぎ): キャラクター名 |
| [`core/works/anime/inuyasha.toml`](core/works/anime/inuyasha.toml) | 4 | 405 B | 犬夜叉 (高橋留美子): キャラクター名 |
| [`core/works/anime/nurarihyon.toml`](core/works/anime/nurarihyon.toml) | 4 | 417 B | ぬらりひょんの孫: キャラクター名 |
| [`core/works/anime/seinen.toml`](core/works/anime/seinen.toml) | 4 | 496 B | 青年漫画: キャラクター名 |
| [`core/works/anime/xxxholic.toml`](core/works/anime/xxxholic.toml) | 4 | 366 B | xxxHOLiC (CLAMP): キャラクター名 |
| **小計** (56 ファイル) | **853** | **78 KB** | |

#### VTuber

VTuber の名前 (姓・フルネーム、 公式読みベース)

`core/works/vtuber/` — 6 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/works/vtuber/nijisanji.toml`](core/works/vtuber/nijisanji.toml) | 51 | 4.6 KB | にじさんじ (ANYCOLOR): ライバー名 (公式読みベース) |
| [`core/works/vtuber/hololive.toml`](core/works/vtuber/hololive.toml) | 43 | 3.6 KB | ホロライブプロダクション (カバー): タレント名 (公式読みベース) |
| [`core/works/vtuber/aogiri.toml`](core/works/vtuber/aogiri.toml) | 7 | 639 B | あおぎり高校 : タレント名 |
| [`core/works/vtuber/kojin.toml`](core/works/vtuber/kojin.toml) | 6 | 614 B | 個人勢VTuber: タレント名 |
| [`core/works/vtuber/vspo.toml`](core/works/vtuber/vspo.toml) | 6 | 701 B | ぶいすぽっ! : タレント名 (公式読みベース) |
| [`core/works/vtuber/nanashi.toml`](core/works/vtuber/nanashi.toml) | 3 | 404 B | ななしいんく : タレント名 |
| **小計** (6 ファイル) | **116** | **11 KB** | |


### 外来語

`core/loanwords/*` — ASCII surface (英字始まり) を完全一致 lookup する別管理辞書。 case-fold + 全角→半角 正規化。

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/loanwords/general.toml`](core/loanwords/general.toml) | 851 | 22 KB | 一般英語 / メディア / ゲーミング / SNS 略語 (ASCII surface) |
| [`core/loanwords/english.toml`](core/loanwords/english.toml) | 542 | 13 KB | 英単語 (配信コメント頻出の一般語 / 作品・企業名 / 綴り読み略語) |
| [`core/loanwords/it.toml`](core/loanwords/it.toml) | 215 | 6.8 KB | IT 用語 / プログラミング言語 / OSS / クラウドサービス / 技術企業 (ASCII surface) |
| [`core/loanwords/romaji.toml`](core/loanwords/romaji.toml) | 104 | 2.4 KB | ローマ字表記 (VTuber 名 / 日本語ローマ字) |
| **小計** (4 ファイル) | **1,712** | **44 KB** | |

### 分類前 inbox

`core/_inbox.toml` — 「読みは追加したいが genre dir の振り分け判断付かない」 用の一時置き場。 lib 側は `[meta] role = "jukugo"` で jukugo として load される (≥2 字 surface 限定)。 maintainer の整理タイミングで適切な `core/jukugo/<genre>/<file>.toml` に移動する。

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/_inbox.toml`](core/_inbox.toml) | 15 | 1.7 KB | 分類前の一時 inbox (≥2 字 surface、 内容が貯まったら適切な genre dir に振り分ける) |

### 単漢字 [[kanji]] format

`core/kanji/*` — 1 字 surface に対する `[[kanji]]` block 形式 entry。 各 block は `char` (1 字必須) + `default` reading + optional `[[kanji.match]]` 配列 (= 文脈分岐 reading、 matcher vocabulary は entry inline match と同一)。 「ルール数」 列は **block 数 + 各 [[kanji.match]] 合計** (= default + 文脈分岐の総ルール数)。

| ファイル | 文字数 | ルール数 | サイズ | 用途 |
|---|---:|---:|---:|---|
| [`core/kanji/overrides.toml`](core/kanji/overrides.toml) | 2,778 | 4,290 | 356 KB | 単漢字 default override + 文脈分岐 reading |

### 異体字

`core/compat.toml` — 異体字 → 標準字の正規化マッピング (例: 髙→高)。 reading lookup 前の前処理として lib が参照。

(空)
<!-- AUTO-GENERATED:CORE:END -->

### エンジンルール

`rules/` — エンジン挙動 (助数詞 / 文脈 / 後処理 等) を制御するルール群。 lib コードに embed されるのではなく、 ここで宣言的に外部化されている。

<!-- AUTO-GENERATED:RULES:BEGIN -->
**合計**: 771 エントリ / 833 ルール / 37 KB (genre 3 区分)

#### 数値系

日付 / 大数 / 助数詞 / 数値慣用句 — 数値表現の読み解決

`rules/numbers/` — 10 ファイル

| ファイル | エントリ数 | ルール数 | サイズ | 用途 |
|---|---:|---:|---:|---|
| [`rules/numbers/counters/objects.toml`](rules/numbers/counters/objects.toml) | 88 | 173 | 16 KB | 物を数える助数詞 (本 / 匹 / 杯 / 個 / 歳 / 冊、 連濁 / 促音化) |
| [`rules/numbers/numeric_phrases.toml`](rules/numbers/numeric_phrases.toml) | 37 | 37 | 1.2 KB | 数字を含む例外語句 (二十歳→ハタチ / 明後日→アサッテ 等、 助数詞ルールより先に確定) |
| [`rules/numbers/counters/time.toml`](rules/numbers/counters/time.toml) | 21 | 34 | 4.5 KB | 時間系助数詞 (月 / 日 / 時 / 分 / 週間 / 回、 4/7/9 の特殊読み + カナ末尾置換) |
| [`rules/numbers/days.toml`](rules/numbers/days.toml) | 31 | 31 | 978 B | 1〜31 日の特殊読み (1→ツイタチ / 20→ハツカ 等) |
| [`rules/numbers/scales.toml`](rules/numbers/scales.toml) | 19 | 19 | 1.0 KB | 大数スケール (万 / 億 / 兆 / 京 / 垓 / 不可思議 / 無量大数 等、 大→小順、 N+漢字単位 連結用) |
| [`rules/numbers/counters/places.toml`](rules/numbers/counters/places.toml) | 4 | 9 | 1.2 KB | 場所を数える助数詞 (階 / ヶ所 / 箇所 / か所、 連濁 / 促音化) |
| [`rules/numbers/counters/percent.toml`](rules/numbers/counters/percent.toml) | 2 | 4 | 583 B | パーセンテージ (% / ％、 1/6/8/0 で促音化 + パーセント) |
| [`rules/numbers/counters/simple.toml`](rules/numbers/counters/simple.toml) | 45 | 2 | 1.2 KB | 単純サフィックス助数詞 (円 / 点 / 度 / 名 / 話 等、 数値カナ + value 連結のみ) |
| [`rules/numbers/counters/people.toml`](rules/numbers/counters/people.toml) | 1 | 1 | 225 B | 人を数える助数詞 (人、 1=ヒトリ / 2=フタリ の特殊読み) |
| [`rules/numbers/counters/recursive.toml`](rules/numbers/counters/recursive.toml) | 1 | 1 | 202 B | 再帰モード助数詞 (個目 / 階目 等、 既存助数詞解決後に末尾連結) |
| **小計** (10 ファイル) | **249** | **311** | **27 KB** | |

#### テキスト系

単位 / 記号 / ラテン文字 / 後処理 regex — 文字単位の読み解決と最終整形

`rules/text/` — 3 ファイル

| ファイル | エントリ数 | ルール数 | サイズ | 用途 |
|---|---:|---:|---:|---|
| [`rules/text/symbols.toml`](rules/text/symbols.toml) | 59 | 59 | 1.3 KB | 記号 1 文字読み (+ / − / % / ‰ / 〜 / ・ / ※ 等、 chunks/split() の symbols 階層で個別 hit) |
| [`rules/text/units.toml`](rules/text/units.toml) | 25 | 25 | 1.5 KB | SI 単位 + 通貨 + % (km / kg / mL / 円 / % 等、 数値 + 単位を 1 chunk で読む。 lookup は case-insensitive) |
| [`rules/text/postprocess.toml`](rules/text/postprocess.toml) | 2 | 2 | 325 B | 出力後処理 regex (Step 7、 mode 別: hiragana / ruby / tts / romaji の出力直前に適用) |
| **小計** (3 ファイル) | **86** | **86** | **3.1 KB** | |

#### (直下)

`rules/` 直下 — 1 ファイル

| ファイル | エントリ数 | ルール数 | サイズ | 用途 |
|---|---:|---:|---:|---|
| [`rules/compat.toml`](rules/compat.toml) | 436 | 436 | 6.1 KB | 異体字 → 標準字の正規化マップ (髙→高 等、 lib Step 1 で入力テキストを正規化) |

<!-- AUTO-GENERATED:RULES:END -->

**エントリ数** は top-level (counter 名 / `[[rule]]` surface 数 / `[entries]` key 数)、
**ルール数** は深掘り pattern count (counters の `[[counter."X".rules]]` や context の
`[[rule.match]]` 等の内部配列要素も含む合計)。 counters / context 以外では両者は同値。

## QA カバレッジ

QA は **corpus 回帰** (`tests/corpus/should_read.toml` 等の永続スナップショット) と
**inline test** (隣接 `<name>.test.toml` で file 単位 lock) の 2 階層で組まれる。
両方とも release tar から `--exclude='*.test.toml'` で除外され、 lib runtime memory
にも乗らない (実行時には影響しない、 CI 時のみの assertion)。

- 詳細仕様: [`docs/INLINE_TESTS.md`](docs/INLINE_TESTS.md) (inline) /
  [`tests/corpus/README.md`](tests/corpus/README.md) (corpus)
- corpus 単一 file が大きくなったら同名 dir に分割可能 (`should_read/<topic>.toml` 等を
  再帰 load)
- PR 時の追加方針: 新機能 / bug fix を加えた PR は、 その PR がカバーした case を
  corpus または inline test に **1 件以上** 追加する (PR template でチェック)

<!-- AUTO-GENERATED:QA:BEGIN -->
### Corpus (回帰)

**合計**: should_read 11311 ケース / should_not_read_yet 1 ケース / out_of_scope 0 ケース

| バケット | ファイル | ケース数 |
|---|---|---:|
| `should_read` | [`tests/corpus/should_read/_archive_20260617.toml`](tests/corpus/should_read/_archive_20260617.toml) | 20 |
|  | [`tests/corpus/should_read/_archive_20260618.toml`](tests/corpus/should_read/_archive_20260618.toml) | 178 |
|  | [`tests/corpus/should_read/_archive_20260619.toml`](tests/corpus/should_read/_archive_20260619.toml) | 943 |
|  | [`tests/corpus/should_read/_archive_20260620.toml`](tests/corpus/should_read/_archive_20260620.toml) | 376 |
|  | [`tests/corpus/should_read/corpus_20260612.toml`](tests/corpus/should_read/corpus_20260612.toml) | 39 |
|  | [`tests/corpus/should_read/corpus_20260613.toml`](tests/corpus/should_read/corpus_20260613.toml) | 6 |
|  | [`tests/corpus/should_read/counter_kanji_numeral_20260617.toml`](tests/corpus/should_read/counter_kanji_numeral_20260617.toml) | 13 |
|  | [`tests/corpus/should_read/dict_chu_20260918.toml`](tests/corpus/should_read/dict_chu_20260918.toml) | 11 |
|  | [`tests/corpus/should_read/dict_split_guard_20260918.toml`](tests/corpus/should_read/dict_split_guard_20260918.toml) | 63 |
|  | [`tests/corpus/should_read/extended.toml`](tests/corpus/should_read/extended.toml) | 94 |
|  | [`tests/corpus/should_read/general.toml`](tests/corpus/should_read/general.toml) | 69 |
|  | [`tests/corpus/should_read/gintama.toml`](tests/corpus/should_read/gintama.toml) | 1 |
|  | [`tests/corpus/should_read/gold_20260919.toml`](tests/corpus/should_read/gold_20260919.toml) | 44 |
|  | [`tests/corpus/should_read/kanji_kun_default_20260612.toml`](tests/corpus/should_read/kanji_kun_default_20260612.toml) | 19 |
|  | [`tests/corpus/should_read/lib_same_char_run_20260918.toml`](tests/corpus/should_read/lib_same_char_run_20260918.toml) | 14 |
|  | [`tests/corpus/should_read/lib_verb_stem_20260918.toml`](tests/corpus/should_read/lib_verb_stem_20260918.toml) | 88 |
|  | [`tests/corpus/should_read/matchhits_20260612.toml`](tests/corpus/should_read/matchhits_20260612.toml) | 24 |
|  | [`tests/corpus/should_read/name_suffix_20260612.toml`](tests/corpus/should_read/name_suffix_20260612.toml) | 55 |
|  | [`tests/corpus/should_read/probe_20260621.toml`](tests/corpus/should_read/probe_20260621.toml) | 87 |
|  | [`tests/corpus/should_read/probe_20260706.toml`](tests/corpus/should_read/probe_20260706.toml) | 17 |
|  | [`tests/corpus/should_read/probe_20260811_surname_suffix.toml`](tests/corpus/should_read/probe_20260811_surname_suffix.toml) | 29 |
|  | [`tests/corpus/should_read/probe_20260828_bot_dict.toml`](tests/corpus/should_read/probe_20260828_bot_dict.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260911_brands.toml`](tests/corpus/should_read/probe_20260911_brands.toml) | 32 |
|  | [`tests/corpus/should_read/probe_20260911_compat_kai.toml`](tests/corpus/should_read/probe_20260911_compat_kai.toml) | 3 |
|  | [`tests/corpus/should_read/probe_20260911_conjugation.toml`](tests/corpus/should_read/probe_20260911_conjugation.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260911_conjugation3.toml`](tests/corpus/should_read/probe_20260911_conjugation3.toml) | 30 |
|  | [`tests/corpus/should_read/probe_20260911_conjugation4.toml`](tests/corpus/should_read/probe_20260911_conjugation4.toml) | 29 |
|  | [`tests/corpus/should_read/probe_20260911_corpus7m.toml`](tests/corpus/should_read/probe_20260911_corpus7m.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260911_counter_prefix.toml`](tests/corpus/should_read/probe_20260911_counter_prefix.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260911_domains.toml`](tests/corpus/should_read/probe_20260911_domains.toml) | 28 |
|  | [`tests/corpus/should_read/probe_20260911_domains2.toml`](tests/corpus/should_read/probe_20260911_domains2.toml) | 34 |
|  | [`tests/corpus/should_read/probe_20260911_domains3.toml`](tests/corpus/should_read/probe_20260911_domains3.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260911_domains4.toml`](tests/corpus/should_read/probe_20260911_domains4.toml) | 23 |
|  | [`tests/corpus/should_read/probe_20260911_entry_audit.toml`](tests/corpus/should_read/probe_20260911_entry_audit.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260911_final.toml`](tests/corpus/should_read/probe_20260911_final.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260911_hyphen.toml`](tests/corpus/should_read/probe_20260911_hyphen.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260911_invariant2.toml`](tests/corpus/should_read/probe_20260911_invariant2.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260911_invariant3.toml`](tests/corpus/should_read/probe_20260911_invariant3.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260911_kana_suffix.toml`](tests/corpus/should_read/probe_20260911_kana_suffix.toml) | 22 |
|  | [`tests/corpus/should_read/probe_20260911_kanji_flip26.toml`](tests/corpus/should_read/probe_20260911_kanji_flip26.toml) | 73 |
|  | [`tests/corpus/should_read/probe_20260911_mahjong.toml`](tests/corpus/should_read/probe_20260911_mahjong.toml) | 37 |
|  | [`tests/corpus/should_read/probe_20260911_mi_flip.toml`](tests/corpus/should_read/probe_20260911_mi_flip.toml) | 17 |
|  | [`tests/corpus/should_read/probe_20260911_newdomains.toml`](tests/corpus/should_read/probe_20260911_newdomains.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260911_noun_derivation.toml`](tests/corpus/should_read/probe_20260911_noun_derivation.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260911_numeric.toml`](tests/corpus/should_read/probe_20260911_numeric.toml) | 23 |
|  | [`tests/corpus/should_read/probe_20260911_obi_audit.toml`](tests/corpus/should_read/probe_20260911_obi_audit.toml) | 23 |
|  | [`tests/corpus/should_read/probe_20260911_prefix_counter.toml`](tests/corpus/should_read/probe_20260911_prefix_counter.toml) | 20 |
|  | [`tests/corpus/should_read/probe_20260911_proper2.toml`](tests/corpus/should_read/probe_20260911_proper2.toml) | 32 |
|  | [`tests/corpus/should_read/probe_20260911_proper3.toml`](tests/corpus/should_read/probe_20260911_proper3.toml) | 17 |
|  | [`tests/corpus/should_read/probe_20260911_scale_unit.toml`](tests/corpus/should_read/probe_20260911_scale_unit.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260911_shime.toml`](tests/corpus/should_read/probe_20260911_shime.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260911_suffix_sweep.toml`](tests/corpus/should_read/probe_20260911_suffix_sweep.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260911_symbol_punct.toml`](tests/corpus/should_read/probe_20260911_symbol_punct.toml) | 5 |
|  | [`tests/corpus/should_read/probe_20260911_vv_round2.toml`](tests/corpus/should_read/probe_20260911_vv_round2.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260911_vv_round3.toml`](tests/corpus/should_read/probe_20260911_vv_round3.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260911_vv_round4.toml`](tests/corpus/should_read/probe_20260911_vv_round4.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260911_vv_round5.toml`](tests/corpus/should_read/probe_20260911_vv_round5.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260911_vvcompare.toml`](tests/corpus/should_read/probe_20260911_vvcompare.toml) | 22 |
|  | [`tests/corpus/should_read/probe_20260912_voicevox.toml`](tests/corpus/should_read/probe_20260912_voicevox.toml) | 32 |
|  | [`tests/corpus/should_read/probe_20260913_domain_collision.toml`](tests/corpus/should_read/probe_20260913_domain_collision.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260913_entry_audit.toml`](tests/corpus/should_read/probe_20260913_entry_audit.toml) | 17 |
|  | [`tests/corpus/should_read/probe_20260913_fresh_corpus.toml`](tests/corpus/should_read/probe_20260913_fresh_corpus.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260913_given_name.toml`](tests/corpus/should_read/probe_20260913_given_name.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260913_guild_dict.toml`](tests/corpus/should_read/probe_20260913_guild_dict.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260913_homograph.toml`](tests/corpus/should_read/probe_20260913_homograph.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260913_katakana_sweep.toml`](tests/corpus/should_read/probe_20260913_katakana_sweep.toml) | 21 |
|  | [`tests/corpus/should_read/probe_20260913_loanwords.toml`](tests/corpus/should_read/probe_20260913_loanwords.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260913_lowband.toml`](tests/corpus/should_read/probe_20260913_lowband.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260913_mahjong_yaku.toml`](tests/corpus/should_read/probe_20260913_mahjong_yaku.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260913_marker2.toml`](tests/corpus/should_read/probe_20260913_marker2.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260913_person_marker.toml`](tests/corpus/should_read/probe_20260913_person_marker.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260913_person_marker2.toml`](tests/corpus/should_read/probe_20260913_person_marker2.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260913_signal_chunk.toml`](tests/corpus/should_read/probe_20260913_signal_chunk.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260913_suffix_sweep.toml`](tests/corpus/should_read/probe_20260913_suffix_sweep.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260913_unidic_audit.toml`](tests/corpus/should_read/probe_20260913_unidic_audit.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260913_unidic_missing.toml`](tests/corpus/should_read/probe_20260913_unidic_missing.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260913_unreg_sweep.toml`](tests/corpus/should_read/probe_20260913_unreg_sweep.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260913_voicevox2.toml`](tests/corpus/should_read/probe_20260913_voicevox2.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260913_voicevox3.toml`](tests/corpus/should_read/probe_20260913_voicevox3.toml) | 23 |
|  | [`tests/corpus/should_read/probe_20260913_voicevox4.toml`](tests/corpus/should_read/probe_20260913_voicevox4.toml) | 25 |
|  | [`tests/corpus/should_read/probe_20260913_voicevox5.toml`](tests/corpus/should_read/probe_20260913_voicevox5.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260914_bushi.toml`](tests/corpus/should_read/probe_20260914_bushi.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260914_juku3.toml`](tests/corpus/should_read/probe_20260914_juku3.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260914_kane_ren.toml`](tests/corpus/should_read/probe_20260914_kane_ren.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260914_kanji_before_katakana.toml`](tests/corpus/should_read/probe_20260914_kanji_before_katakana.toml) | 20 |
|  | [`tests/corpus/should_read/probe_20260914_kaoyo.toml`](tests/corpus/should_read/probe_20260914_kaoyo.toml) | 5 |
|  | [`tests/corpus/should_read/probe_20260914_katakana_on.toml`](tests/corpus/should_read/probe_20260914_katakana_on.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260914_katakana_suffix.toml`](tests/corpus/should_read/probe_20260914_katakana_suffix.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260914_kono_aida.toml`](tests/corpus/should_read/probe_20260914_kono_aida.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260914_kun_verb_stem.toml`](tests/corpus/should_read/probe_20260914_kun_verb_stem.toml) | 18 |
|  | [`tests/corpus/should_read/probe_20260914_latin_mirror.toml`](tests/corpus/should_read/probe_20260914_latin_mirror.toml) | 18 |
|  | [`tests/corpus/should_read/probe_20260914_latin_sen.toml`](tests/corpus/should_read/probe_20260914_latin_sen.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260914_name_collision.toml`](tests/corpus/should_read/probe_20260914_name_collision.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260914_new_genre.toml`](tests/corpus/should_read/probe_20260914_new_genre.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260914_no_hou.toml`](tests/corpus/should_read/probe_20260914_no_hou.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260914_solo_kanji.toml`](tests/corpus/should_read/probe_20260914_solo_kanji.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260914_sono_uchi.toml`](tests/corpus/should_read/probe_20260914_sono_uchi.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260914_spec_collision.toml`](tests/corpus/should_read/probe_20260914_spec_collision.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260914_surname_suffix.toml`](tests/corpus/should_read/probe_20260914_surname_suffix.toml) | 22 |
|  | [`tests/corpus/should_read/probe_20260914_surname_sweep2.toml`](tests/corpus/should_read/probe_20260914_surname_sweep2.toml) | 18 |
|  | [`tests/corpus/should_read/probe_20260914_surname_sweep_byproduct.toml`](tests/corpus/should_read/probe_20260914_surname_sweep_byproduct.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260915_bot_logs.toml`](tests/corpus/should_read/probe_20260915_bot_logs.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260915_counters_sweep.toml`](tests/corpus/should_read/probe_20260915_counters_sweep.toml) | 17 |
|  | [`tests/corpus/should_read/probe_20260915_country_abbr.toml`](tests/corpus/should_read/probe_20260915_country_abbr.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260915_country_en.toml`](tests/corpus/should_read/probe_20260915_country_en.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260915_english_words.toml`](tests/corpus/should_read/probe_20260915_english_words.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260915_eval_losses.toml`](tests/corpus/should_read/probe_20260915_eval_losses.toml) | 36 |
|  | [`tests/corpus/should_read/probe_20260915_hito_te_mono.toml`](tests/corpus/should_read/probe_20260915_hito_te_mono.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260915_ie_ke.toml`](tests/corpus/should_read/probe_20260915_ie_ke.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260915_kome_silent.toml`](tests/corpus/should_read/probe_20260915_kome_silent.toml) | 2 |
|  | [`tests/corpus/should_read/probe_20260915_lib_numbers_symbols.toml`](tests/corpus/should_read/probe_20260915_lib_numbers_symbols.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260915_me_sei.toml`](tests/corpus/should_read/probe_20260915_me_sei.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260915_naka_mono.toml`](tests/corpus/should_read/probe_20260915_naka_mono.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260915_selfmade_sentences.toml`](tests/corpus/should_read/probe_20260915_selfmade_sentences.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260915_shita_ato.toml`](tests/corpus/should_read/probe_20260915_shita_ato.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_aozakana.toml`](tests/corpus/should_read/probe_20260915_sweep_aozakana.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_betsu.toml`](tests/corpus/should_read/probe_20260915_sweep_betsu.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_gesenai.toml`](tests/corpus/should_read/probe_20260915_sweep_gesenai.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_hairou.toml`](tests/corpus/should_read/probe_20260915_sweep_hairou.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_hanashi.toml`](tests/corpus/should_read/probe_20260915_sweep_hanashi.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_ikereba.toml`](tests/corpus/should_read/probe_20260915_sweep_ikereba.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_kami.toml`](tests/corpus/should_read/probe_20260915_sweep_kami.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_katsu.toml`](tests/corpus/should_read/probe_20260915_sweep_katsu.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_kiru.toml`](tests/corpus/should_read/probe_20260915_sweep_kiru.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_koe.toml`](tests/corpus/should_read/probe_20260915_sweep_koe.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_kuru.toml`](tests/corpus/should_read/probe_20260915_sweep_kuru.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_ma_tsuyo.toml`](tests/corpus/should_read/probe_20260915_sweep_ma_tsuyo.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_me.toml`](tests/corpus/should_read/probe_20260915_sweep_me.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_naniiro.toml`](tests/corpus/should_read/probe_20260915_sweep_naniiro.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_okurigana.toml`](tests/corpus/should_read/probe_20260915_sweep_okurigana.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_okurigana2.toml`](tests/corpus/should_read/probe_20260915_sweep_okurigana2.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_okurigana3.toml`](tests/corpus/should_read/probe_20260915_sweep_okurigana3.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_okurigana4.toml`](tests/corpus/should_read/probe_20260915_sweep_okurigana4.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_okurigana5.toml`](tests/corpus/should_read/probe_20260915_sweep_okurigana5.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_okurigana6.toml`](tests/corpus/should_read/probe_20260915_sweep_okurigana6.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_oshimai.toml`](tests/corpus/should_read/probe_20260915_sweep_oshimai.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_rank1200.toml`](tests/corpus/should_read/probe_20260915_sweep_rank1200.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_rank1600.toml`](tests/corpus/should_read/probe_20260915_sweep_rank1600.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_samasama.toml`](tests/corpus/should_read/probe_20260915_sweep_samasama.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_shokushitsu.toml`](tests/corpus/should_read/probe_20260915_sweep_shokushitsu.toml) | 4 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_shubiden.toml`](tests/corpus/should_read/probe_20260915_sweep_shubiden.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_suguha.toml`](tests/corpus/should_read/probe_20260915_sweep_suguha.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_tanomu.toml`](tests/corpus/should_read/probe_20260915_sweep_tanomu.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_tasuke.toml`](tests/corpus/should_read/probe_20260915_sweep_tasuke.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_top.toml`](tests/corpus/should_read/probe_20260915_sweep_top.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_toriatama.toml`](tests/corpus/should_read/probe_20260915_sweep_toriatama.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_warau.toml`](tests/corpus/should_read/probe_20260915_sweep_warau.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260915_sweep_yoi.toml`](tests/corpus/should_read/probe_20260915_sweep_yoi.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260915_ue_jou.toml`](tests/corpus/should_read/probe_20260915_ue_jou.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260915_unihan_frequent.toml`](tests/corpus/should_read/probe_20260915_unihan_frequent.toml) | 28 |
|  | [`tests/corpus/should_read/probe_20260915_unihan_stem.toml`](tests/corpus/should_read/probe_20260915_unihan_stem.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260915_unihan_stem_kanjidic.toml`](tests/corpus/should_read/probe_20260915_unihan_stem_kanjidic.toml) | 42 |
|  | [`tests/corpus/should_read/probe_20260915_unihan_stem_samereading.toml`](tests/corpus/should_read/probe_20260915_unihan_stem_samereading.toml) | 37 |
|  | [`tests/corpus/should_read/probe_20260915_weekday_abbr.toml`](tests/corpus/should_read/probe_20260915_weekday_abbr.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_akaao.toml`](tests/corpus/should_read/probe_20260916_sweep_akaao.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_akatan.toml`](tests/corpus/should_read/probe_20260916_sweep_akatan.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_anahori.toml`](tests/corpus/should_read/probe_20260916_sweep_anahori.toml) | 40 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_anaketsu.toml`](tests/corpus/should_read/probe_20260916_sweep_anaketsu.toml) | 67 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_anno.toml`](tests/corpus/should_read/probe_20260916_sweep_anno.toml) | 64 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_aori.toml`](tests/corpus/should_read/probe_20260916_sweep_aori.toml) | 36 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_asanoborizen.toml`](tests/corpus/should_read/probe_20260916_sweep_asanoborizen.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_asari.toml`](tests/corpus/should_read/probe_20260916_sweep_asari.toml) | 52 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_atsu.toml`](tests/corpus/should_read/probe_20260916_sweep_atsu.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_chuutte.toml`](tests/corpus/should_read/probe_20260916_sweep_chuutte.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_dakimakura.toml`](tests/corpus/should_read/probe_20260916_sweep_dakimakura.toml) | 30 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_deaeta.toml`](tests/corpus/should_read/probe_20260916_sweep_deaeta.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_dogyoson.toml`](tests/corpus/should_read/probe_20260916_sweep_dogyoson.toml) | 34 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_dokugumo.toml`](tests/corpus/should_read/probe_20260916_sweep_dokugumo.toml) | 33 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_fukki.toml`](tests/corpus/should_read/probe_20260916_sweep_fukki.toml) | 30 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_fukurotai.toml`](tests/corpus/should_read/probe_20260916_sweep_fukurotai.toml) | 33 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_gayoso.toml`](tests/corpus/should_read/probe_20260916_sweep_gayoso.toml) | 34 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_genzakue.toml`](tests/corpus/should_read/probe_20260916_sweep_genzakue.toml) | 34 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_gindate.toml`](tests/corpus/should_read/probe_20260916_sweep_gindate.toml) | 39 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_gobousei.toml`](tests/corpus/should_read/probe_20260916_sweep_gobousei.toml) | 26 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_hanamaru.toml`](tests/corpus/should_read/probe_20260916_sweep_hanamaru.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_hayai.toml`](tests/corpus/should_read/probe_20260916_sweep_hayai.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_hokuto.toml`](tests/corpus/should_read/probe_20260916_sweep_hokuto.toml) | 25 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_hoshimittsu.toml`](tests/corpus/should_read/probe_20260916_sweep_hoshimittsu.toml) | 22 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_ikorose.toml`](tests/corpus/should_read/probe_20260916_sweep_ikorose.toml) | 22 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_isagiyoshi.toml`](tests/corpus/should_read/probe_20260916_sweep_isagiyoshi.toml) | 29 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_itasha.toml`](tests/corpus/should_read/probe_20260916_sweep_itasha.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_itawaru.toml`](tests/corpus/should_read/probe_20260916_sweep_itawaru.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_jukenshi.toml`](tests/corpus/should_read/probe_20260916_sweep_jukenshi.toml) | 41 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_juon.toml`](tests/corpus/should_read/probe_20260916_sweep_juon.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kabutta.toml`](tests/corpus/should_read/probe_20260916_sweep_kabutta.toml) | 21 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kagamisonshi.toml`](tests/corpus/should_read/probe_20260916_sweep_kagamisonshi.toml) | 43 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kainaka.toml`](tests/corpus/should_read/probe_20260916_sweep_kainaka.toml) | 26 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kaisuiabi.toml`](tests/corpus/should_read/probe_20260916_sweep_kaisuiabi.toml) | 34 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kamekura.toml`](tests/corpus/should_read/probe_20260916_sweep_kamekura.toml) | 21 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kanade.toml`](tests/corpus/should_read/probe_20260916_sweep_kanade.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kasegikata.toml`](tests/corpus/should_read/probe_20260916_sweep_kasegikata.toml) | 23 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kasuga.toml`](tests/corpus/should_read/probe_20260916_sweep_kasuga.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_katsuraku.toml`](tests/corpus/should_read/probe_20260916_sweep_katsuraku.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kazuo.toml`](tests/corpus/should_read/probe_20260916_sweep_kazuo.toml) | 40 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kenzakai.toml`](tests/corpus/should_read/probe_20260916_sweep_kenzakai.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_koroai.toml`](tests/corpus/should_read/probe_20260916_sweep_koroai.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kosuru.toml`](tests/corpus/should_read/probe_20260916_sweep_kosuru.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kujakumai.toml`](tests/corpus/should_read/probe_20260916_sweep_kujakumai.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kyonyu.toml`](tests/corpus/should_read/probe_20260916_sweep_kyonyu.toml) | 40 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_kyuubi.toml`](tests/corpus/should_read/probe_20260916_sweep_kyuubi.toml) | 39 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_manten.toml`](tests/corpus/should_read/probe_20260916_sweep_manten.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_minikita.toml`](tests/corpus/should_read/probe_20260916_sweep_minikita.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_miura.toml`](tests/corpus/should_read/probe_20260916_sweep_miura.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_munenatsu.toml`](tests/corpus/should_read/probe_20260916_sweep_munenatsu.toml) | 53 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_nabebuta.toml`](tests/corpus/should_read/probe_20260916_sweep_nabebuta.toml) | 39 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_nekura.toml`](tests/corpus/should_read/probe_20260916_sweep_nekura.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_nobishiro.toml`](tests/corpus/should_read/probe_20260916_sweep_nobishiro.toml) | 26 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_okurairi.toml`](tests/corpus/should_read/probe_20260916_sweep_okurairi.toml) | 30 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_orera.toml`](tests/corpus/should_read/probe_20260916_sweep_orera.toml) | 23 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_oriru.toml`](tests/corpus/should_read/probe_20260916_sweep_oriru.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_otoko.toml`](tests/corpus/should_read/probe_20260916_sweep_otoko.toml) | 36 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_otsubone.toml`](tests/corpus/should_read/probe_20260916_sweep_otsubone.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_ouran.toml`](tests/corpus/should_read/probe_20260916_sweep_ouran.toml) | 37 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_pekoshi.toml`](tests/corpus/should_read/probe_20260916_sweep_pekoshi.toml) | 39 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_renho.toml`](tests/corpus/should_read/probe_20260916_sweep_renho.toml) | 38 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_renseishi.toml`](tests/corpus/should_read/probe_20260916_sweep_renseishi.toml) | 25 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_rishuzumi.toml`](tests/corpus/should_read/probe_20260916_sweep_rishuzumi.toml) | 32 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_rokubousei.toml`](tests/corpus/should_read/probe_20260916_sweep_rokubousei.toml) | 29 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_shikyoku.toml`](tests/corpus/should_read/probe_20260916_sweep_shikyoku.toml) | 22 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_shinkai.toml`](tests/corpus/should_read/probe_20260916_sweep_shinkai.toml) | 4 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_shinrakacho.toml`](tests/corpus/should_read/probe_20260916_sweep_shinrakacho.toml) | 31 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_sojita.toml`](tests/corpus/should_read/probe_20260916_sweep_sojita.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_sosoru.toml`](tests/corpus/should_read/probe_20260916_sweep_sosoru.toml) | 20 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_sukunee.toml`](tests/corpus/should_read/probe_20260916_sweep_sukunee.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_take.toml`](tests/corpus/should_read/probe_20260916_sweep_take.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_takumi.toml`](tests/corpus/should_read/probe_20260916_sweep_takumi.toml) | 46 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_taniahigeyakiba.toml`](tests/corpus/should_read/probe_20260916_sweep_taniahigeyakiba.toml) | 20 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_teijoen.toml`](tests/corpus/should_read/probe_20260916_sweep_teijoen.toml) | 22 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_teuchi.toml`](tests/corpus/should_read/probe_20260916_sweep_teuchi.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_tsugi.toml`](tests/corpus/should_read/probe_20260916_sweep_tsugi.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_tsumekata.toml`](tests/corpus/should_read/probe_20260916_sweep_tsumekata.toml) | 5 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_tsuree.toml`](tests/corpus/should_read/probe_20260916_sweep_tsuree.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_usada.toml`](tests/corpus/should_read/probe_20260916_sweep_usada.toml) | 32 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yakara.toml`](tests/corpus/should_read/probe_20260916_sweep_yakara.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yansha.toml`](tests/corpus/should_read/probe_20260916_sweep_yansha.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yarigai.toml`](tests/corpus/should_read/probe_20260916_sweep_yarigai.toml) | 31 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yasashime.toml`](tests/corpus/should_read/probe_20260916_sweep_yasashime.toml) | 5 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yasui.toml`](tests/corpus/should_read/probe_20260916_sweep_yasui.toml) | 9 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yogosu.toml`](tests/corpus/should_read/probe_20260916_sweep_yogosu.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yosan.toml`](tests/corpus/should_read/probe_20260916_sweep_yosan.toml) | 26 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yoshikage.toml`](tests/corpus/should_read/probe_20260916_sweep_yoshikage.toml) | 15 |
|  | [`tests/corpus/should_read/probe_20260916_sweep_yue.toml`](tests/corpus/should_read/probe_20260916_sweep_yue.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260917_fresh_atsusa.toml`](tests/corpus/should_read/probe_20260917_fresh_atsusa.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260917_fresh_unozawa.toml`](tests/corpus/should_read/probe_20260917_fresh_unozawa.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_aizen.toml`](tests/corpus/should_read/probe_20260917_sweep_aizen.toml) | 55 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_akira.toml`](tests/corpus/should_read/probe_20260917_sweep_akira.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_amagaki.toml`](tests/corpus/should_read/probe_20260917_sweep_amagaki.toml) | 49 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_amidabutsu.toml`](tests/corpus/should_read/probe_20260917_sweep_amidabutsu.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_aomiya.toml`](tests/corpus/should_read/probe_20260917_sweep_aomiya.toml) | 37 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_arisu.toml`](tests/corpus/should_read/probe_20260917_sweep_arisu.toml) | 73 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_awano.toml`](tests/corpus/should_read/probe_20260917_sweep_awano.toml) | 43 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_azen.toml`](tests/corpus/should_read/probe_20260917_sweep_azen.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_batai.toml`](tests/corpus/should_read/probe_20260917_sweep_batai.toml) | 55 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_daidai.toml`](tests/corpus/should_read/probe_20260917_sweep_daidai.toml) | 55 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_ebisubashi.toml`](tests/corpus/should_read/probe_20260917_sweep_ebisubashi.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_eguru.toml`](tests/corpus/should_read/probe_20260917_sweep_eguru.toml) | 84 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_enka.toml`](tests/corpus/should_read/probe_20260917_sweep_enka.toml) | 77 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_funatsu.toml`](tests/corpus/should_read/probe_20260917_sweep_funatsu.toml) | 14 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_furuta.toml`](tests/corpus/should_read/probe_20260917_sweep_furuta.toml) | 79 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_gejun.toml`](tests/corpus/should_read/probe_20260917_sweep_gejun.toml) | 75 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_genkou.toml`](tests/corpus/should_read/probe_20260917_sweep_genkou.toml) | 12 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_gokumonkyou.toml`](tests/corpus/should_read/probe_20260917_sweep_gokumonkyou.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_hagiwara.toml`](tests/corpus/should_read/probe_20260917_sweep_hagiwara.toml) | 65 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_hakobore.toml`](tests/corpus/should_read/probe_20260917_sweep_hakobore.toml) | 82 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_hanayama.toml`](tests/corpus/should_read/probe_20260917_sweep_hanayama.toml) | 81 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_haruka.toml`](tests/corpus/should_read/probe_20260917_sweep_haruka.toml) | 48 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_hayabusa.toml`](tests/corpus/should_read/probe_20260917_sweep_hayabusa.toml) | 68 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_higesori.toml`](tests/corpus/should_read/probe_20260917_sweep_higesori.toml) | 61 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_hiruma.toml`](tests/corpus/should_read/probe_20260917_sweep_hiruma.toml) | 17 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_hoozuki.toml`](tests/corpus/should_read/probe_20260917_sweep_hoozuki.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_iratsuku.toml`](tests/corpus/should_read/probe_20260917_sweep_iratsuku.toml) | 74 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_isame.toml`](tests/corpus/should_read/probe_20260917_sweep_isame.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_izumi.toml`](tests/corpus/should_read/probe_20260917_sweep_izumi.toml) | 36 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kamado.toml`](tests/corpus/should_read/probe_20260917_sweep_kamado.toml) | 58 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kannushi.toml`](tests/corpus/should_read/probe_20260917_sweep_kannushi.toml) | 93 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_karasuiro.toml`](tests/corpus/should_read/probe_20260917_sweep_karasuiro.toml) | 50 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kayaba.toml`](tests/corpus/should_read/probe_20260917_sweep_kayaba.toml) | 54 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_keikaku.toml`](tests/corpus/should_read/probe_20260917_sweep_keikaku.toml) | 13 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kirabiyaka.toml`](tests/corpus/should_read/probe_20260917_sweep_kirabiyaka.toml) | 67 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_konsen.toml`](tests/corpus/should_read/probe_20260917_sweep_konsen.toml) | 67 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_koohiimame.toml`](tests/corpus/should_read/probe_20260917_sweep_koohiimame.toml) | 70 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_koumei.toml`](tests/corpus/should_read/probe_20260917_sweep_koumei.toml) | 72 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kouta.toml`](tests/corpus/should_read/probe_20260917_sweep_kouta.toml) | 11 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kuchibiru.toml`](tests/corpus/should_read/probe_20260917_sweep_kuchibiru.toml) | 104 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kurabu.toml`](tests/corpus/should_read/probe_20260917_sweep_kurabu.toml) | 17 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kusuo.toml`](tests/corpus/should_read/probe_20260917_sweep_kusuo.toml) | 51 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_kyonshi.toml`](tests/corpus/should_read/probe_20260917_sweep_kyonshi.toml) | 50 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_makibishi.toml`](tests/corpus/should_read/probe_20260917_sweep_makibishi.toml) | 86 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_masuno.toml`](tests/corpus/should_read/probe_20260917_sweep_masuno.toml) | 10 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_mayuzumi.toml`](tests/corpus/should_read/probe_20260917_sweep_mayuzumi.toml) | 72 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_meihin.toml`](tests/corpus/should_read/probe_20260917_sweep_meihin.toml) | 66 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_misogi.toml`](tests/corpus/should_read/probe_20260917_sweep_misogi.toml) | 78 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_mori.toml`](tests/corpus/should_read/probe_20260917_sweep_mori.toml) | 29 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_nakajimamika.toml`](tests/corpus/should_read/probe_20260917_sweep_nakajimamika.toml) | 73 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_naosara.toml`](tests/corpus/should_read/probe_20260917_sweep_naosara.toml) | 60 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_niodachi.toml`](tests/corpus/should_read/probe_20260917_sweep_niodachi.toml) | 69 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_rendo.toml`](tests/corpus/should_read/probe_20260917_sweep_rendo.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_ri.toml`](tests/corpus/should_read/probe_20260917_sweep_ri.toml) | 87 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_ruurouhan.toml`](tests/corpus/should_read/probe_20260917_sweep_ruurouhan.toml) | 49 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_saigishin.toml`](tests/corpus/should_read/probe_20260917_sweep_saigishin.toml) | 7 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_samayou.toml`](tests/corpus/should_read/probe_20260917_sweep_samayou.toml) | 66 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_sekitomokazu.toml`](tests/corpus/should_read/probe_20260917_sweep_sekitomokazu.toml) | 62 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_shijichuu.toml`](tests/corpus/should_read/probe_20260917_sweep_shijichuu.toml) | 91 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_shinsen.toml`](tests/corpus/should_read/probe_20260917_sweep_shinsen.toml) | 6 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_shitsuke.toml`](tests/corpus/should_read/probe_20260917_sweep_shitsuke.toml) | 65 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_shoku.toml`](tests/corpus/should_read/probe_20260917_sweep_shoku.toml) | 48 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_shou.toml`](tests/corpus/should_read/probe_20260917_sweep_shou.toml) | 16 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_shoyu.toml`](tests/corpus/should_read/probe_20260917_sweep_shoyu.toml) | 66 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_shuten.toml`](tests/corpus/should_read/probe_20260917_sweep_shuten.toml) | 80 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_shuyukan.toml`](tests/corpus/should_read/probe_20260917_sweep_shuyukan.toml) | 20 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_sojou.toml`](tests/corpus/should_read/probe_20260917_sweep_sojou.toml) | 96 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_sori.toml`](tests/corpus/should_read/probe_20260917_sweep_sori.toml) | 54 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_sukune.toml`](tests/corpus/should_read/probe_20260917_sweep_sukune.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_tachihiroshi.toml`](tests/corpus/should_read/probe_20260917_sweep_tachihiroshi.toml) | 68 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_takatsuki.toml`](tests/corpus/should_read/probe_20260917_sweep_takatsuki.toml) | 64 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_takuni.toml`](tests/corpus/should_read/probe_20260917_sweep_takuni.toml) | 5 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_tasogare.toml`](tests/corpus/should_read/probe_20260917_sweep_tasogare.toml) | 51 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_tatamu.toml`](tests/corpus/should_read/probe_20260917_sweep_tatamu.toml) | 44 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_ten.toml`](tests/corpus/should_read/probe_20260917_sweep_ten.toml) | 50 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_tetsuzankou.toml`](tests/corpus/should_read/probe_20260917_sweep_tetsuzankou.toml) | 46 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_toryu.toml`](tests/corpus/should_read/probe_20260917_sweep_toryu.toml) | 59 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_tou_kure.toml`](tests/corpus/should_read/probe_20260917_sweep_tou_kure.toml) | 80 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_tsuchigakure.toml`](tests/corpus/should_read/probe_20260917_sweep_tsuchigakure.toml) | 5 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_tsurugimochi.toml`](tests/corpus/should_read/probe_20260917_sweep_tsurugimochi.toml) | 20 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_urabe.toml`](tests/corpus/should_read/probe_20260917_sweep_urabe.toml) | 63 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_urokodaki.toml`](tests/corpus/should_read/probe_20260917_sweep_urokodaki.toml) | 44 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_yarou.toml`](tests/corpus/should_read/probe_20260917_sweep_yarou.toml) | 50 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_yoshitsugu.toml`](tests/corpus/should_read/probe_20260917_sweep_yoshitsugu.toml) | 19 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_youkan.toml`](tests/corpus/should_read/probe_20260917_sweep_youkan.toml) | 8 |
|  | [`tests/corpus/should_read/probe_20260917_sweep_yuukiaoi.toml`](tests/corpus/should_read/probe_20260917_sweep_yuukiaoi.toml) | 74 |
|  | [`tests/corpus/should_read/probe_20260921_indep_sns.toml`](tests/corpus/should_read/probe_20260921_indep_sns.toml) | 22 |
|  | [`tests/corpus/should_read/regression.toml`](tests/corpus/should_read/regression.toml) | 560 |
|  | [`tests/corpus/should_read/sentences.toml`](tests/corpus/should_read/sentences.toml) | 49 |
|  | [`tests/corpus/should_read/touhou.toml`](tests/corpus/should_read/touhou.toml) | 30 |
|  | [`tests/corpus/should_read/vv_round_20260617.toml`](tests/corpus/should_read/vv_round_20260617.toml) | 21 |
|  | [`tests/corpus/should_read.toml`](tests/corpus/should_read.toml) | 150 |
| `should_not_read_yet` | [`tests/corpus/should_not_read_yet.toml`](tests/corpus/should_not_read_yet.toml) | 1 |
| `out_of_scope` | [`tests/corpus/out_of_scope.toml`](tests/corpus/out_of_scope.toml) | 0 |

### Inline test (`*.test.toml`)

**合計**: 1 ファイル / 17 ケース

| テストファイル | 対象本体 | ケース数 |
|---|---|---:|
| [`rules/numbers/counters/objects.test.toml`](rules/numbers/counters/objects.test.toml) | [`rules/numbers/counters/objects.toml`](rules/numbers/counters/objects.toml) | 17 |
<!-- AUTO-GENERATED:QA:END -->

## 利用側 (`ja-furigana`) でのメモリ寄与

`ja-furigana-cli serve` (HTTP サーバー mode) 起動直後の Windows 実測値 (release build、dict ~1 MB 時点):

| 計測指標 | 値 |
|---|---:|
| WorkingSet (実 RSS) | **~54 MB** |
| PrivateMemory | **~28 MB** |
| バイナリ on-disk | **~64 MB** (Lindera + IPADIC を embed) |

内訳の概算 (実測ではなく推定):

| 構成要素 | メモリ寄与 |
|---|---:|
| Lindera + IPADIC (形態素解析の辞書、 binary embed) | **大半** (~30-50 MB) ← 支配的 |
| 本リポジトリの語彙辞書 + ルール | **数 MB** (TOML を `HashMap` 等に展開後、 dict サイズの 2-3x オーダー) |
| その他 (Rust runtime / Tokio multi-thread runtime / system libs) | **数 MB** |

dict (jukugo + works) が 10x に育っても、本リポジトリ側の寄与は **数 MB オーダー** に収まる試算
(unihan は seed として固定サイズ、jukugo の伸びが本体)。
Lindera + IPADIC が支配的なので、 dict 拡充によるメモリ圧迫は当面気にしなくて良い。

> 計測コマンド (PowerShell):
> ```powershell
> $p = Start-Process -FilePath 'target\release\furigana.exe' `
>   -ArgumentList 'serve','--bind','127.0.0.1:18765' -PassThru
> Start-Sleep -Seconds 2
> $p.Refresh()
> Write-Output ('WS={0} MB, Private={1} MB' -f `
>   [int]($p.WorkingSet64/1MB), [int]($p.PrivateMemorySize64/1MB))
> Stop-Process $p
> ```

## カバレッジの偏り

- **単漢字 (unihan)** はほぼ全 CJK 漢字をカバー (43k 字)
- **熟語 (jukugo)** は genre 別ディレクトリで分類管理 (件数は上の `core/` テーブル参照)
- **作品造語 (works)** は `core/works/<medium>/<title>.toml` 形式で 1 作品 1 ファイル運用。
  公式読み原則 (詳細は [`core/works/README.md`](core/works/README.md))
- **現代の私人 / 私企業 / 商標** は seed していない (誤読リスク回避方針)。
  公式読みが定まっていれば PR 単位で個別判断

→ 体感では「**著名な漢字熟語 / 単漢字 / 古典 / 学術 / 自然物 / 公式読みのある作品は読める、
現代私人 / 商標 / 私企業は手薄**」。 PR 大歓迎。

## 更新方法

**何もしなくて OK**。TOML を編集して master に push (or PR merge) すれば、
`.github/workflows/regen-stats.yml` が自動で `tools/regen_stats.py` を走らせて
diff があれば `chore: regen STATS.md [skip stats]` で auto-commit する。

新規ファイルを追加した場合は、ファイル冒頭に以下を入れるだけ:

```toml
[meta]
description = "<このファイルの 1 行説明>"

[entries]
...
```

`tools/regen_stats.py` がこの `[meta].description` を STATS.md の用途列に取り込む。

ローカルで手動再生成したい場合は `python3 tools/regen_stats.py` で生成可能 (CI と同じ挙動)。
