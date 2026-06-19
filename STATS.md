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
| [**単漢字**](#単漢字) (`core/unihan/*`、 水準別 5 ファイル) | **40,680** | **739 KB** |
| [**熟語**](#熟語) (`core/jukugo/*`、手動 PR メンテ) | **4,412** | **231 KB** |
| [**作品造語**](#作品造語) (`core/works/*`、作品単位 1 ファイル) | **1,209** | **91 KB** |
| [**外来語**](#外来語) (`core/loanwords/*`、IT 用語等の英字 surface) | **861** | **23 KB** |
| [**分類前 inbox**](#分類前-inbox) (`core/_inbox.toml`、 後で振り分ける一時置き場) | **0** | **180 B** |
| [**単漢字 [[kanji]] format**](#単漢字-kanji-format) (`core/kanji/*`、 default + 文脈分岐 reading) | **2,771** | **182 KB** |
| [**異体字**](#異体字) (`core/compat.toml`) | **0** | **0 B** |
| [**エンジンルール**](#エンジンルール) (`rules/`) | **672** | **29 KB** |
| **合計** | **50,605** | **1.26 MB** |
<!-- AUTO-GENERATED:SUMMARY:END -->

## 内訳

`core/` (語彙辞書) はカテゴリ別 sub-section に、 `rules/` (エンジンルール) は最後にまとめて。 summary 表のカテゴリ名クリックで該当 sub-section へジャンプ可。

<!-- AUTO-GENERATED:CORE:BEGIN -->
### 単漢字

`core/unihan/*` — 水準別 5 ファイル。 lib の resolve_reading 6 段階で最終 fallback (Step 6) として参照される。 default reading review は使用頻度の高い `joyo.toml` を中心に。

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/unihan/joyo.toml`](core/unihan/joyo.toml) | 9 | 1.0 KB | 常用漢字 2,136 字 (文化庁 2010-11-30 改訂、 内閣告示) — 利用頻度高、 default reading review 対象 |
| [`core/unihan/jinmeiyou.toml`](core/unihan/jinmeiyou.toml) | 0 | 185 B | 人名用漢字 (法務省、 子の名に使用可、 常用と重複する 128 字を除外した残り 855 字) |
| [`core/unihan/jis_basic.toml`](core/unihan/jis_basic.toml) | 13,043 | 235 KB | JIS 基本 (CJK Basic Block U+4E00-U+9FFF のうち常用 / 人名用以外、 概ね JIS X 0208 第1+第2水準カバー) |
| [`core/unihan/jis_supplement.toml`](core/unihan/jis_supplement.toml) | 4,825 | 83 KB | JIS 補助 (CJK Extension A + Compatibility Ideographs、 概ね JIS X 0213 第3+第4水準カバー) |
| [`core/unihan/extension.toml`](core/unihan/extension.toml) | 22,803 | 418 KB | 拡張漢字 (CJK Extension B 以降、 表外字 / 中国専用字 / 異体字、 機械的扱い、 ほぼ lib lookup されない) |
| **小計** (5 ファイル) | **40,680** | **739 KB** | |

### 熟語

`core/jukugo/<genre>/*` — 手動 PR メンテのジャンル別 jukugo (≥ 2 字 surface)。 lib の Step 3 (jukugo lookup) で Lindera より優先採用。 各 genre dir の `_genre.toml` がカテゴリ description を持つ。

**合計**: 4,412 件 / 231 KB (genre 6 区分)

#### 自然・生命

動植物 / 食品 / 気象 / 体の部位 / 地名 / 自然科学 — 自然界と生物に関わる語彙

`core/jukugo/nature/` — 8 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/nature/place_names.toml`](core/jukugo/nature/place_names.toml) | 225 | 17 KB | 地名 (47 都道府県 / 主要都市 / 駅 / 寺社仏閣 / 観光地) |
| [`core/jukugo/nature/foods.toml`](core/jukugo/nature/foods.toml) | 106 | 4.5 KB | 食べ物 / 料理 / 和菓子 / 郷土料理 / 食材 / 調味料 |
| [`core/jukugo/nature/animals.toml`](core/jukugo/nature/animals.toml) | 73 | 2.6 KB | 動植物 / 魚介 / 鳥 / 昆虫 / 茸 / 海藻の難読 |
| [`core/jukugo/nature/body_parts.toml`](core/jukugo/nature/body_parts.toml) | 62 | 2.2 KB | 体の部位 / 内臓 / 骨格 / 筋肉 / 神経 |
| [`core/jukugo/nature/math.toml`](core/jukugo/nature/math.toml) | 52 | 2.0 KB | 数学 (解析 / 線形代数 / 集合論 / 統計 / 確率の難読) |
| [`core/jukugo/nature/plants.toml`](core/jukugo/nature/plants.toml) | 39 | 1.2 KB | 植物 / 花 / 樹木 / 草本の難読 (熟字訓) |
| [`core/jukugo/nature/weather.toml`](core/jukugo/nature/weather.toml) | 36 | 1.4 KB | 気象 / 天候 / 季語的気象 / 二十四節気 / 海洋気象 |
| [`core/jukugo/nature/science.toml`](core/jukugo/nature/science.toml) | 15 | 859 B | 自然科学 (天文 / 物理 / 化学 / 生物 / 地学) |
| **小計** (8 ファイル) | **608** | **32 KB** | |

#### 人文・芸術

古典文学 / 芸術 / 慣用句 / 抽象概念 / 音楽 / 宗教 / 感情 — 人の精神活動に関わる語彙

`core/jukugo/humanities/` — 9 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/humanities/arts.toml`](core/jukugo/humanities/arts.toml) | 68 | 3.2 KB | 古典芸能 / 武道 / 茶華香 / 工芸 |
| [`core/jukugo/humanities/religions.toml`](core/jukugo/humanities/religions.toml) | 60 | 3.0 KB | 神道 / 仏教 / キリスト教 / イスラム / 儀礼 |
| [`core/jukugo/humanities/literature.toml`](core/jukugo/humanities/literature.toml) | 49 | 2.2 KB | 古典文学 / 作品名 / 文学用語 / 詩歌 / 評論 |
| [`core/jukugo/humanities/idioms.toml`](core/jukugo/humanities/idioms.toml) | 42 | 2.7 KB | 慣用句 / ことわざ / 故事成語 (フレーズ単位) |
| [`core/jukugo/humanities/shinwa.toml`](core/jukugo/humanities/shinwa.toml) | 32 | 1.5 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/humanities/music.toml`](core/jukugo/humanities/music.toml) | 23 | 1.2 KB | 音楽ジャンル / 楽典 / 楽器 / 演奏 / 音楽用語 |
| [`core/jukugo/humanities/abstracts.toml`](core/jukugo/humanities/abstracts.toml) | 18 | 774 B | 美意識 / 古典文学 / 仏教 / 儒教 / 思想 |
| [`core/jukugo/humanities/folklore.toml`](core/jukugo/humanities/folklore.toml) | 16 | 1.1 KB | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/humanities/emotions.toml`](core/jukugo/humanities/emotions.toml) | 10 | 665 B | 感情 / 心理状態 / 性格 / 心情 |
| **小計** (9 ファイル) | **318** | **16 KB** | |

#### 社会・制度

政治 / 金融 / スポーツ / 専門用語 — 社会構造 / 制度に関わる語彙

`core/jukugo/society/` — 8 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/society/specialized.toml`](core/jukugo/society/specialized.toml) | 69 | 4.1 KB | 専門用語 (医学 / 軍事 / 法学 / 経済 / IT / 工学) |
| [`core/jukugo/society/medicine.toml`](core/jukugo/society/medicine.toml) | 59 | 1.8 KB | 医学 / 医療 (病名 / 症状 / 解剖 / 処置の難読) |
| [`core/jukugo/society/law.toml`](core/jukugo/society/law.toml) | 52 | 2.0 KB | 法律 / 司法 (民法 / 刑法 / 訴訟 / 会社法 / 相続) |
| [`core/jukugo/society/history.toml`](core/jukugo/society/history.toml) | 43 | 1.8 KB | 歴史用語 (日本史の制度 / 事件 / 文化概念) |
| [`core/jukugo/society/sports.toml`](core/jukugo/society/sports.toml) | 38 | 2.3 KB | 近代スポーツ / 球技 / 陸上 / 水泳 / 体操 / 大会 |
| [`core/jukugo/society/finance.toml`](core/jukugo/society/finance.toml) | 19 | 1.4 KB | 経済金融 (商品 / 市場 / 会計 / 税務 / 保険) |
| [`core/jukugo/society/shogi.toml`](core/jukugo/society/shogi.toml) | 12 | 804 B | (用途未設定 — ファイル冒頭に `[meta] description = "..."` を追加) |
| [`core/jukugo/society/politics.toml`](core/jukugo/society/politics.toml) | 10 | 904 B | 政治 / 行政 / 立法 / 司法 / 国際関係 |
| **小計** (8 ファイル) | **302** | **15 KB** | |

#### 固有名詞

人名 / 大学・官庁・元号などの固有名詞 — 個別実体を指す語彙

`core/jukugo/proper/` — 4 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/proper/personal_names.toml`](core/jukugo/proper/personal_names.toml) | 152 | 11 KB | 人名 (戦国 / 平安 / 江戸 / 明治大正 / 古典作家、現代私人除く) |
| [`core/jukugo/proper/surnames.toml`](core/jukugo/proper/surnames.toml) | 42 | 1.4 KB | 難読姓 (苗字) の読み (姓単体、代表読み) |
| [`core/jukugo/proper/sumo_shikona.toml`](core/jukugo/proper/sumo_shikona.toml) | 37 | 2.6 KB | 大相撲 力士の四股名 (公式読み) |
| [`core/jukugo/proper/proper_nouns.toml`](core/jukugo/proper/proper_nouns.toml) | 30 | 1.5 KB | 固有名詞 (大学 / 中央官庁 / 元号 / 歴史的事象、PR 募集中) |
| **小計** (4 ファイル) | **261** | **17 KB** | |

#### 物体・工芸

色 / 衣服 / 乗り物 / 建築 / 鉄道 — 人工物と工芸に関わる語彙

`core/jukugo/objects/` — 5 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/objects/colors.toml`](core/jukugo/objects/colors.toml) | 72 | 2.3 KB | 色名 / 染色 / 模様 / 古典色 / 鉱物色 |
| [`core/jukugo/objects/clothes.toml`](core/jukugo/objects/clothes.toml) | 57 | 1.7 KB | 衣服 / 装束 / アクセサリー / 履物 |
| [`core/jukugo/objects/architecture.toml`](core/jukugo/objects/architecture.toml) | 38 | 1.6 KB | 建築 / 建造物 / 寺社建築 / 城郭 / 庭園 |
| [`core/jukugo/objects/vehicles.toml`](core/jukugo/objects/vehicles.toml) | 25 | 1.2 KB | 乗り物 / 交通手段 / 船舶 / 航空 / 鉄道 |
| [`core/jukugo/objects/railway.toml`](core/jukugo/objects/railway.toml) | 9 | 608 B | 鉄道専門用語 (線路 / 駅 / 運行 / 車両) |
| **小計** (5 ファイル) | **201** | **7.4 KB** | |

#### 基本・構造

一般熟語 / 四字熟語 — 全カテゴリに横断する基本語彙

`core/jukugo/basic/` — 6 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/jukugo/basic/general.toml`](core/jukugo/basic/general.toml) | 2,596 | 136 KB | 二字・三字の一般熟語 (季節 / 行事 / 慣用句 含む) |
| [`core/jukugo/basic/stream_round_20260526.toml`](core/jukugo/basic/stream_round_20260526.toml) | 39 | 1.3 KB | VV stream-comments comparison round (seed=20260526) |
| [`core/jukugo/basic/stream_round_20260611.toml`](core/jukugo/basic/stream_round_20260611.toml) | 32 | 2.9 KB | VV stream-comments comparison round (seed=20260611) |
| [`core/jukugo/basic/four_char.toml`](core/jukugo/basic/four_char.toml) | 31 | 2.0 KB | 四字熟語 (4 字 + 全 CJK 漢字) |
| [`core/jukugo/basic/stream_round_20260613.toml`](core/jukugo/basic/stream_round_20260613.toml) | 14 | 805 B | VV stream-comments comparison round (seed=161803) |
| [`core/jukugo/basic/stream_round_20260612.toml`](core/jukugo/basic/stream_round_20260612.toml) | 10 | 1008 B | VV stream-comments comparison round (seed=20260612) |
| **小計** (6 ファイル) | **2,722** | **144 KB** | |


### 作品造語

`core/works/<medium>/*` — 媒体 (game / literature 等) ごとに 1 作品 1 ファイル。 原則は公式読み (一般通称として定着していれば採録可)、 出典コメント必須、 古典読みは現代読み無い場合のみ。

**合計**: 1,209 件 / 91 KB (genre 4 区分)

#### ゲーム

ゲーム作品の固有名詞 (キャラクター / 場所 / 用語、 公式読みベース)

`core/works/game/` — 27 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/works/game/touhou.toml`](core/works/game/touhou.toml) | 269 | 8.8 KB | 東方Project (上海アリス幻樂団): キャラクター名 / 場所 / 用語 (公式読みベース) |
| [`core/works/game/sangokushi.toml`](core/works/game/sangokushi.toml) | 34 | 2.2 KB | 三国志 (演義/ゲーム/漫画): 武将名 (日本語音読み) |
| [`core/works/game/touken_ranbu.toml`](core/works/game/touken_ranbu.toml) | 31 | 2.6 KB | 刀剣乱舞 (ニトロプラス): 刀剣男士名 |
| [`core/works/game/hypmic.toml`](core/works/game/hypmic.toml) | 24 | 1.8 KB | ヒプノシスマイク (キングレコード): キャラクター名 |
| [`core/works/game/ensemble_stars.toml`](core/works/game/ensemble_stars.toml) | 19 | 1.5 KB | あんさんぶるスターズ! (Happy Elements): キャラクター名 |
| [`core/works/game/genshin.toml`](core/works/game/genshin.toml) | 19 | 1.7 KB | 原神 (HoYoverse): キャラクター名 (公式日本語読みベース) |
| [`core/works/game/persona.toml`](core/works/game/persona.toml) | 18 | 1.5 KB | ペルソナ (アトラス): キャラクター名 |
| [`core/works/game/danganronpa.toml`](core/works/game/danganronpa.toml) | 16 | 1.2 KB | ダンガンロンパ: キャラクター名 |
| [`core/works/game/idolmaster.toml`](core/works/game/idolmaster.toml) | 15 | 1.3 KB | アイドルマスター (バンダイナムコ): キャラクター名 |
| [`core/works/game/project_sekai.toml`](core/works/game/project_sekai.toml) | 11 | 962 B | プロジェクトセカイ: キャラクター名 |
| [`core/works/game/bluearchive.toml`](core/works/game/bluearchive.toml) | 10 | 881 B | ブルーアーカイブ (Nexon/Yostar): キャラクター名 (公式読みベース) |
| [`core/works/game/fate.toml`](core/works/game/fate.toml) | 10 | 879 B | Fate / 型月 (TYPE-MOON): キャラクター名 |
| [`core/works/game/vocaloid.toml`](core/works/game/vocaloid.toml) | 10 | 975 B | ボーカロイド/合成音声: キャラクター名 (公式読み) |
| [`core/works/game/gyakuten.toml`](core/works/game/gyakuten.toml) | 8 | 710 B | 逆転裁判: キャラクター名 |
| [`core/works/game/kankore.toml`](core/works/game/kankore.toml) | 7 | 589 B | 艦これ: 艦娘名 (旧海軍艦名) |
| [`core/works/game/honkai_starrail.toml`](core/works/game/honkai_starrail.toml) | 6 | 600 B | 崩壊:スターレイル (HoYoverse): キャラクター名 (公式日本語読みベース) |
| [`core/works/game/bang_dream.toml`](core/works/game/bang_dream.toml) | 5 | 524 B | BanG Dream! : キャラクター名 |
| [`core/works/game/tokimeki.toml`](core/works/game/tokimeki.toml) | 5 | 465 B | ときめきメモリアル: キャラクター名 |
| [`core/works/game/a3.toml`](core/works/game/a3.toml) | 4 | 396 B | A3! : キャラクター名 |
| [`core/works/game/lovelive.toml`](core/works/game/lovelive.toml) | 4 | 449 B | ラブライブ! (サンライズ): キャラクター名 |
| [`core/works/game/ryu_ga_gotoku.toml`](core/works/game/ryu_ga_gotoku.toml) | 4 | 405 B | 龍が如く: キャラクター名 |
| [`core/works/game/utapri.toml`](core/works/game/utapri.toml) | 4 | 492 B | うたの☆プリンスさまっ♪ : キャラクター名 |
| [`core/works/game/d4dj.toml`](core/works/game/d4dj.toml) | 3 | 343 B | D4DJ : キャラクター名 |
| [`core/works/game/yugioh.toml`](core/works/game/yugioh.toml) | 3 | 376 B | 遊☆戯☆王 (高橋和希): キャラクター名 |
| [`core/works/game/ff7.toml`](core/works/game/ff7.toml) | 2 | 352 B | ファイナルファンタジーVII (スクウェア・エニックス): 固有名詞 (公式読みベース) |
| [`core/works/game/megaten.toml`](core/works/game/megaten.toml) | 2 | 341 B | 女神転生 (アトラス): キャラクター名 / 用語 |
| [`core/works/game/sekiro.toml`](core/works/game/sekiro.toml) | 1 | 241 B | SEKIRO (フロム・ソフトウェア): キャラクター名 / 用語 |
| **小計** (27 ファイル) | **544** | **32 KB** | |

#### 文学

文学作品の固有名詞 (登場人物 / 巻名 / 場所、 古典定本ベース)

`core/works/literature/` — 1 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/works/literature/genji_monogatari.toml`](core/works/literature/genji_monogatari.toml) | 42 | 1.3 KB | 源氏物語 (紫式部): 登場人物 / 巻名 / 場所 (平安中期、 古典定本ベース) |

#### アニメ・漫画

アニメ / 漫画作品の固有名詞 (キャラクター / 場所 / 用語、 公式読みベース)

`core/works/anime/` — 58 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/works/anime/kimetsu.toml`](core/works/anime/kimetsu.toml) | 45 | 3.9 KB | 鬼滅の刃 (吾峠呼世晴): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/jujutsu.toml`](core/works/anime/jujutsu.toml) | 34 | 2.8 KB | 呪術廻戦 (芥見下々): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/haikyu.toml`](core/works/anime/haikyu.toml) | 28 | 2.4 KB | ハイキュー!! (古舘春一): キャラクター名 (公式読みベース) |
| [`core/works/anime/heroaca.toml`](core/works/anime/heroaca.toml) | 28 | 2.5 KB | 僕のヒーローアカデミア (堀越耕平): キャラクター名 (公式読みベース) |
| [`core/works/anime/bleach.toml`](core/works/anime/bleach.toml) | 27 | 2.4 KB | BLEACH (久保帯人) キャラ名・用語 |
| [`core/works/anime/jojo.toml`](core/works/anime/jojo.toml) | 25 | 2.5 KB | ジョジョの奇妙な冒険 (荒木飛呂彦): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/tenipuri.toml`](core/works/anime/tenipuri.toml) | 22 | 1.7 KB | テニスの王子様 (許斐剛): キャラクター名 |
| [`core/works/anime/naruto.toml`](core/works/anime/naruto.toml) | 21 | 1.5 KB | NARUTO (岸本斉史): キャラクター名 (公式読みベース) |
| [`core/works/anime/conan.toml`](core/works/anime/conan.toml) | 20 | 1.6 KB | 名探偵コナン (青山剛昌): キャラクター名 (公式読みベース) |
| [`core/works/anime/gintama.toml`](core/works/anime/gintama.toml) | 18 | 1.6 KB | 銀魂 (空知英秋): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/onepiece.toml`](core/works/anime/onepiece.toml) | 17 | 1.4 KB | ONE PIECE (尾田栄一郎): キャラクター名 / 用語 |
| [`core/works/anime/tokyo_revengers.toml`](core/works/anime/tokyo_revengers.toml) | 17 | 1.4 KB | 東京卍リベンジャーズ (和久井健): キャラクター名 (公式読みベース) |
| [`core/works/anime/bluelock.toml`](core/works/anime/bluelock.toml) | 16 | 1.4 KB | ブルーロック (金城宗幸/ノ村優介): キャラクター名 |
| [`core/works/anime/kurobas.toml`](core/works/anime/kurobas.toml) | 15 | 1.2 KB | 黒子のバスケ (藤巻忠俊): キャラクター名 |
| [`core/works/anime/monogatari.toml`](core/works/anime/monogatari.toml) | 12 | 1.1 KB | 〈物語〉シリーズ (西尾維新): 作品名 (公式読みベース) |
| [`core/works/anime/slamdunk.toml`](core/works/anime/slamdunk.toml) | 12 | 1.0 KB | SLAM DUNK (井上雄彦): キャラクター名 |
| [`core/works/anime/houshin.toml`](core/works/anime/houshin.toml) | 10 | 752 B | 封神演義: キャラクター名 / 用語 |
| [`core/works/anime/precure.toml`](core/works/anime/precure.toml) | 10 | 869 B | プリキュア: キャラクター名 |
| [`core/works/anime/yuyuhakusho.toml`](core/works/anime/yuyuhakusho.toml) | 10 | 820 B | 幽☆遊☆白書 (冨樫義博): キャラクター名 |
| [`core/works/anime/baseball_manga.toml`](core/works/anime/baseball_manga.toml) | 7 | 709 B | 野球漫画: キャラクター名 |
| [`core/works/anime/captsubasa.toml`](core/works/anime/captsubasa.toml) | 7 | 684 B | キャプテン翼: キャラクター名 |
| [`core/works/anime/kusuriya.toml`](core/works/anime/kusuriya.toml) | 7 | 597 B | 薬屋のひとりごと (日向夏): キャラクター名 (公式読みベース) |
| [`core/works/anime/ranma.toml`](core/works/anime/ranma.toml) | 7 | 677 B | らんま1/2: キャラクター名 |
| [`core/works/anime/shoujo.toml`](core/works/anime/shoujo.toml) | 7 | 688 B | 少女漫画: キャラクター名 |
| [`core/works/anime/tokusatsu.toml`](core/works/anime/tokusatsu.toml) | 7 | 695 B | 仮面ライダー: キャラクター名 |
| [`core/works/anime/tokyoghoul.toml`](core/works/anime/tokyoghoul.toml) | 7 | 742 B | 東京喰種 (石田スイ): キャラクター名 / 用語 |
| [`core/works/anime/kokumin_anime.toml`](core/works/anime/kokumin_anime.toml) | 6 | 577 B | 国民的アニメ: キャラクター名 |
| [`core/works/anime/dragonball.toml`](core/works/anime/dragonball.toml) | 5 | 536 B | ドラゴンボール (鳥山明): キャラクター名 (公式読みベース) |
| [`core/works/anime/geass.toml`](core/works/anime/geass.toml) | 5 | 466 B | コードギアス: キャラクター名 |
| [`core/works/anime/ghibli.toml`](core/works/anime/ghibli.toml) | 5 | 642 B | スタジオジブリ: キャラクター名 / 用語 / 作品名 |
| [`core/works/anime/lupin.toml`](core/works/anime/lupin.toml) | 5 | 469 B | ルパン三世/グルメ漫画: キャラクター名 |
| [`core/works/anime/rurouni.toml`](core/works/anime/rurouni.toml) | 5 | 545 B | るろうに剣心 (和月伸宏): キャラクター名 |
| [`core/works/anime/xxxholic.toml`](core/works/anime/xxxholic.toml) | 5 | 445 B | xxxHOLiC (CLAMP): キャラクター名 |
| [`core/works/anime/drstone.toml`](core/works/anime/drstone.toml) | 4 | 432 B | Dr.STONE (稲垣理一郎/Boichi): キャラクター名 |
| [`core/works/anime/eyeshield21.toml`](core/works/anime/eyeshield21.toml) | 4 | 412 B | アイシールド21: キャラクター名 |
| [`core/works/anime/gotoubun.toml`](core/works/anime/gotoubun.toml) | 4 | 446 B | 五等分の花嫁 (春場ねぎ): キャラクター名 |
| [`core/works/anime/inuyasha.toml`](core/works/anime/inuyasha.toml) | 4 | 405 B | 犬夜叉 (高橋留美子): キャラクター名 |
| [`core/works/anime/nurarihyon.toml`](core/works/anime/nurarihyon.toml) | 4 | 417 B | ぬらりひょんの孫: キャラクター名 |
| [`core/works/anime/dororo.toml`](core/works/anime/dororo.toml) | 3 | 361 B | どろろ (手塚治虫): キャラクター名 |
| [`core/works/anime/evangelion.toml`](core/works/anime/evangelion.toml) | 3 | 383 B | 新世紀エヴァンゲリオン (カラー): キャラクター名 (姓) |
| [`core/works/anime/hokuto.toml`](core/works/anime/hokuto.toml) | 3 | 282 B | 北斗の拳: 用語 |
| [`core/works/anime/oshinoko.toml`](core/works/anime/oshinoko.toml) | 3 | 447 B | 【推しの子】 (赤坂アカ/横槍メンゴ): キャラクター名 |
| [`core/works/anime/sailormoon.toml`](core/works/anime/sailormoon.toml) | 3 | 400 B | 美少女戦士セーラームーン (武内直子): キャラクター名 |
| [`core/works/anime/ansatsu.toml`](core/works/anime/ansatsu.toml) | 2 | 315 B | 暗殺教室 (松井優征): キャラクター名 |
| [`core/works/anime/aoashi.toml`](core/works/anime/aoashi.toml) | 2 | 269 B | アオアシ (小林有吾): キャラクター名 |
| [`core/works/anime/jigokuraku.toml`](core/works/anime/jigokuraku.toml) | 2 | 298 B | 地獄楽 (賀来ゆうじ): キャラクター名 |
| [`core/works/anime/kaguya.toml`](core/works/anime/kaguya.toml) | 2 | 362 B | かぐや様は告らせたい (赤坂アカ): キャラクター名 |
| [`core/works/anime/saint_seiya.toml`](core/works/anime/saint_seiya.toml) | 2 | 237 B | 聖闘士星矢: キャラクター名 |
| [`core/works/anime/aoexorcist.toml`](core/works/anime/aoexorcist.toml) | 1 | 196 B | 青の祓魔師 (加藤和恵): キャラクター名 |
| [`core/works/anime/baki.toml`](core/works/anime/baki.toml) | 1 | 236 B | 刃牙シリーズ (板垣恵介): キャラクター名 / 用語 (公式読みベース) |
| [`core/works/anime/bocchi.toml`](core/works/anime/bocchi.toml) | 1 | 221 B | ぼっち・ざ・ろっく! (はまじあき): キャラクター名 |
| [`core/works/anime/dandadan.toml`](core/works/anime/dandadan.toml) | 1 | 198 B | ダンダダン (龍幸伸): キャラクター名 |
| [`core/works/anime/deathnote.toml`](core/works/anime/deathnote.toml) | 1 | 258 B | DEATH NOTE (大場つぐみ/小畑健): キャラクター名 (公式読みベース) |
| [`core/works/anime/gegege_kitaro.toml`](core/works/anime/gegege_kitaro.toml) | 1 | 237 B | ゲゲゲの鬼太郎 (水木しげる): キャラクター名 (公式読みベース) |
| [`core/works/anime/higanjima.toml`](core/works/anime/higanjima.toml) | 1 | 244 B | 彼岸島 (松本光司): タイトル / 用語 (公式読みベース) |
| [`core/works/anime/kaiju8.toml`](core/works/anime/kaiju8.toml) | 1 | 181 B | 怪獣8号 (松本直也): キャラクター名 |
| [`core/works/anime/touch.toml`](core/works/anime/touch.toml) | 1 | 183 B | あだち充作品: キャラクター名 |
| [`core/works/anime/undeadunluck.toml`](core/works/anime/undeadunluck.toml) | 1 | 203 B | アンデッドアンラック (戸塚慶文): キャラクター名 |
| **小計** (58 ファイル) | **527** | **49 KB** | |

#### VTuber

VTuber の名前 (姓・フルネーム、 公式読みベース)

`core/works/vtuber/` — 5 ファイル

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/works/vtuber/nijisanji.toml`](core/works/vtuber/nijisanji.toml) | 47 | 3.9 KB | にじさんじ (ANYCOLOR): ライバー名 (公式読みベース) |
| [`core/works/vtuber/hololive.toml`](core/works/vtuber/hololive.toml) | 34 | 2.9 KB | ホロライブプロダクション (カバー): タレント名 (公式読みベース) |
| [`core/works/vtuber/aogiri.toml`](core/works/vtuber/aogiri.toml) | 7 | 639 B | あおぎり高校 : タレント名 |
| [`core/works/vtuber/vspo.toml`](core/works/vtuber/vspo.toml) | 5 | 548 B | ぶいすぽっ! : タレント名 (公式読みベース) |
| [`core/works/vtuber/nanashi.toml`](core/works/vtuber/nanashi.toml) | 3 | 323 B | ななしいんく : タレント名 |
| **小計** (5 ファイル) | **96** | **8.3 KB** | |


### 外来語

`core/loanwords/*` — ASCII surface (英字始まり) を完全一致 lookup する別管理辞書。 case-fold + 全角→半角 正規化。

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/loanwords/general.toml`](core/loanwords/general.toml) | 675 | 17 KB | 一般英語 / メディア / ゲーミング / SNS 略語 (ASCII surface) |
| [`core/loanwords/it.toml`](core/loanwords/it.toml) | 186 | 5.9 KB | IT 用語 / プログラミング言語 / OSS / クラウドサービス / 技術企業 (ASCII surface) |
| **小計** (2 ファイル) | **861** | **23 KB** | |

### 分類前 inbox

`core/_inbox.toml` — 「読みは追加したいが genre dir の振り分け判断付かない」 用の一時置き場。 lib 側は `[meta] role = "jukugo"` で jukugo として load される (≥2 字 surface 限定)。 maintainer の整理タイミングで適切な `core/jukugo/<genre>/<file>.toml` に移動する。

| ファイル | エントリ数 | サイズ | 用途 |
|---|---:|---:|---|
| [`core/_inbox.toml`](core/_inbox.toml) | 0 | 180 B | 分類前の一時 inbox (≥2 字 surface、 内容が貯まったら適切な genre dir に振り分ける) |

### 単漢字 [[kanji]] format

`core/kanji/*` — 1 字 surface に対する `[[kanji]]` block 形式 entry。 各 block は `char` (1 字必須) + `default` reading + optional `[[kanji.match]]` 配列 (= 文脈分岐 reading、 matcher vocabulary は entry inline match と同一)。 「ルール数」 列は **block 数 + 各 [[kanji.match]] 合計** (= default + 文脈分岐の総ルール数)。

| ファイル | 文字数 | ルール数 | サイズ | 用途 |
|---|---:|---:|---:|---|
| [`core/kanji/overrides.toml`](core/kanji/overrides.toml) | 2,771 | 3,623 | 182 KB | 単漢字 default override + 文脈分岐 reading |

### 異体字

`core/compat.toml` — 異体字 → 標準字の正規化マッピング (例: 髙→高)。 reading lookup 前の前処理として lib が参照。

(空)
<!-- AUTO-GENERATED:CORE:END -->

### エンジンルール

`rules/` — エンジン挙動 (助数詞 / 文脈 / 後処理 等) を制御するルール群。 lib コードに embed されるのではなく、 ここで宣言的に外部化されている。

<!-- AUTO-GENERATED:RULES:BEGIN -->
**合計**: 672 エントリ / 759 ルール / 29 KB (genre 3 区分)

#### 数値系

日付 / 大数 / 助数詞 / 数値慣用句 — 数値表現の読み解決

`rules/numbers/` — 10 ファイル

| ファイル | エントリ数 | ルール数 | サイズ | 用途 |
|---|---:|---:|---:|---|
| [`rules/numbers/counters/objects.toml`](rules/numbers/counters/objects.toml) | 61 | 129 | 12 KB | 物を数える助数詞 (本 / 匹 / 杯 / 個 / 歳 / 冊、 連濁 / 促音化) |
| [`rules/numbers/counters/simple.toml`](rules/numbers/counters/simple.toml) | 47 | 47 | 1.1 KB | 単純サフィックス助数詞 (円 / 点 / 度 / 名 / 話 等、 数値カナ + value 連結のみ) |
| [`rules/numbers/counters/time.toml`](rules/numbers/counters/time.toml) | 19 | 31 | 3.1 KB | 時間系助数詞 (月 / 日 / 時 / 分 / 週間 / 回、 4/7/9 の特殊読み + カナ末尾置換) |
| [`rules/numbers/days.toml`](rules/numbers/days.toml) | 31 | 31 | 978 B | 1〜31 日の特殊読み (1→ツイタチ / 20→ハツカ 等) |
| [`rules/numbers/numeric_phrases.toml`](rules/numbers/numeric_phrases.toml) | 23 | 23 | 893 B | 数字を含む例外語句 (二十歳→ハタチ / 明後日→アサッテ 等、 助数詞ルールより先に確定) |
| [`rules/numbers/scales.toml`](rules/numbers/scales.toml) | 19 | 19 | 1.0 KB | 大数スケール (万 / 億 / 兆 / 京 / 垓 / 不可思議 / 無量大数 等、 大→小順、 N+漢字単位 連結用) |
| [`rules/numbers/counters/places.toml`](rules/numbers/counters/places.toml) | 4 | 9 | 1.2 KB | 場所を数える助数詞 (階 / ヶ所 / 箇所 / か所、 連濁 / 促音化) |
| [`rules/numbers/counters/percent.toml`](rules/numbers/counters/percent.toml) | 2 | 4 | 583 B | パーセンテージ (% / ％、 1/6/8/0 で促音化 + パーセント) |
| [`rules/numbers/counters/people.toml`](rules/numbers/counters/people.toml) | 1 | 1 | 225 B | 人を数える助数詞 (人、 1=ヒトリ / 2=フタリ の特殊読み) |
| [`rules/numbers/counters/recursive.toml`](rules/numbers/counters/recursive.toml) | 1 | 1 | 202 B | 再帰モード助数詞 (個目 / 階目 等、 既存助数詞解決後に末尾連結) |
| **小計** (10 ファイル) | **208** | **295** | **21 KB** | |

#### テキスト系

単位 / 記号 / ラテン文字 / 後処理 regex — 文字単位の読み解決と最終整形

`rules/text/` — 3 ファイル

| ファイル | エントリ数 | ルール数 | サイズ | 用途 |
|---|---:|---:|---:|---|
| [`rules/text/units.toml`](rules/text/units.toml) | 17 | 17 | 813 B | SI 単位 + 通貨 + % (km / kg / mL / 円 / % 等、 数値 + 単位を 1 chunk で読む。 lookup は case-insensitive) |
| [`rules/text/symbols.toml`](rules/text/symbols.toml) | 10 | 10 | 386 B | 記号 1 文字読み (+ / − / % / ‰ / 〜 / ・ / ※ 等、 chunks/split() の symbols 階層で個別 hit) |
| [`rules/text/postprocess.toml`](rules/text/postprocess.toml) | 2 | 2 | 325 B | 出力後処理 regex (Step 7、 mode 別: hiragana / ruby / tts / romaji の出力直前に適用) |
| **小計** (3 ファイル) | **29** | **29** | **1.5 KB** | |

#### (直下)

`rules/` 直下 — 1 ファイル

| ファイル | エントリ数 | ルール数 | サイズ | 用途 |
|---|---:|---:|---:|---|
| [`rules/compat.toml`](rules/compat.toml) | 435 | 435 | 6.1 KB | 異体字 → 標準字の正規化マップ (髙→高 等、 lib Step 1 で入力テキストを正規化) |

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

**合計**: should_read 2205 ケース / should_not_read_yet 1 ケース / out_of_scope 0 ケース

| バケット | ファイル | ケース数 |
|---|---|---:|
| `should_read` | [`tests/corpus/should_read/corpus_20260613.toml`](tests/corpus/should_read/corpus_20260613.toml) | 6 |
|  | [`tests/corpus/should_read/corpus_2026_06_12.toml`](tests/corpus/should_read/corpus_2026_06_12.toml) | 39 |
|  | [`tests/corpus/should_read/counter_kanji_numeral_20260617.toml`](tests/corpus/should_read/counter_kanji_numeral_20260617.toml) | 13 |
|  | [`tests/corpus/should_read/extended.toml`](tests/corpus/should_read/extended.toml) | 94 |
|  | [`tests/corpus/should_read/general.toml`](tests/corpus/should_read/general.toml) | 69 |
|  | [`tests/corpus/should_read/gintama.toml`](tests/corpus/should_read/gintama.toml) | 1 |
|  | [`tests/corpus/should_read/kanji_kun_default_20260612.toml`](tests/corpus/should_read/kanji_kun_default_20260612.toml) | 19 |
|  | [`tests/corpus/should_read/matchhits_20260612.toml`](tests/corpus/should_read/matchhits_20260612.toml) | 24 |
|  | [`tests/corpus/should_read/name_suffix_20260612.toml`](tests/corpus/should_read/name_suffix_20260612.toml) | 55 |
|  | [`tests/corpus/should_read/probe_ateji2_20260618.toml`](tests/corpus/should_read/probe_ateji2_20260618.toml) | 6 |
|  | [`tests/corpus/should_read/probe_ateji_adverb_20260618.toml`](tests/corpus/should_read/probe_ateji_adverb_20260618.toml) | 8 |
|  | [`tests/corpus/should_read/probe_bakumatsu_20260619.toml`](tests/corpus/should_read/probe_bakumatsu_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_baseball_20260619.toml`](tests/corpus/should_read/probe_baseball_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_bin_20260619.toml`](tests/corpus/should_read/probe_bin_20260619.toml) | 9 |
|  | [`tests/corpus/should_read/probe_bleach2_20260619.toml`](tests/corpus/should_read/probe_bleach2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_bluearchive_20260619.toml`](tests/corpus/should_read/probe_bluearchive_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_bluelock_20260619.toml`](tests/corpus/should_read/probe_bluelock_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_bukkyo_20260619.toml`](tests/corpus/should_read/probe_bukkyo_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_bungo_20260619.toml`](tests/corpus/should_read/probe_bungo_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_chara10_20260619.toml`](tests/corpus/should_read/probe_chara10_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_chara11_20260619.toml`](tests/corpus/should_read/probe_chara11_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_chara2_20260619.toml`](tests/corpus/should_read/probe_chara2_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_chara3_20260619.toml`](tests/corpus/should_read/probe_chara3_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_chara4_20260619.toml`](tests/corpus/should_read/probe_chara4_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_chara5_20260619.toml`](tests/corpus/should_read/probe_chara5_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_chara6_20260619.toml`](tests/corpus/should_read/probe_chara6_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_chara7_20260619.toml`](tests/corpus/should_read/probe_chara7_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_chara8_20260619.toml`](tests/corpus/should_read/probe_chara8_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_chara9_20260619.toml`](tests/corpus/should_read/probe_chara9_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_chara_20260619.toml`](tests/corpus/should_read/probe_chara_20260619.toml) | 10 |
|  | [`tests/corpus/should_read/probe_chimei2_20260619.toml`](tests/corpus/should_read/probe_chimei2_20260619.toml) | 1 |
|  | [`tests/corpus/should_read/probe_chubu2_20260619.toml`](tests/corpus/should_read/probe_chubu2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_chubu_20260619.toml`](tests/corpus/should_read/probe_chubu_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_chugoku2_20260619.toml`](tests/corpus/should_read/probe_chugoku2_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_chugoku_20260619.toml`](tests/corpus/should_read/probe_chugoku_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_colors_20260618.toml`](tests/corpus/should_read/probe_colors_20260618.toml) | 9 |
|  | [`tests/corpus/should_read/probe_conan_20260619.toml`](tests/corpus/should_read/probe_conan_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_counter2_20260619.toml`](tests/corpus/should_read/probe_counter2_20260619.toml) | 16 |
|  | [`tests/corpus/should_read/probe_counter_20260619.toml`](tests/corpus/should_read/probe_counter_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_counter_suffix_20260618.toml`](tests/corpus/should_read/probe_counter_suffix_20260618.toml) | 7 |
|  | [`tests/corpus/should_read/probe_counters2_20260618.toml`](tests/corpus/should_read/probe_counters2_20260618.toml) | 15 |
|  | [`tests/corpus/should_read/probe_counters_20260618.toml`](tests/corpus/should_read/probe_counters_20260618.toml) | 11 |
|  | [`tests/corpus/should_read/probe_edo_20260619.toml`](tests/corpus/should_read/probe_edo_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_english2_20260619.toml`](tests/corpus/should_read/probe_english2_20260619.toml) | 12 |
|  | [`tests/corpus/should_read/probe_english3_20260619.toml`](tests/corpus/should_read/probe_english3_20260619.toml) | 10 |
|  | [`tests/corpus/should_read/probe_english4_20260619.toml`](tests/corpus/should_read/probe_english4_20260619.toml) | 10 |
|  | [`tests/corpus/should_read/probe_english_20260619.toml`](tests/corpus/should_read/probe_english_20260619.toml) | 13 |
|  | [`tests/corpus/should_read/probe_fgo_20260619.toml`](tests/corpus/should_read/probe_fgo_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_food2_20260619.toml`](tests/corpus/should_read/probe_food2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_food_20260619.toml`](tests/corpus/should_read/probe_food_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_game_20260619.toml`](tests/corpus/should_read/probe_game_20260619.toml) | 9 |
|  | [`tests/corpus/should_read/probe_garden_20260619.toml`](tests/corpus/should_read/probe_garden_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_genbun10_20260619.toml`](tests/corpus/should_read/probe_genbun10_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_genbun2_20260619.toml`](tests/corpus/should_read/probe_genbun2_20260619.toml) | 10 |
|  | [`tests/corpus/should_read/probe_genbun3_20260619.toml`](tests/corpus/should_read/probe_genbun3_20260619.toml) | 20 |
|  | [`tests/corpus/should_read/probe_genbun4_20260619.toml`](tests/corpus/should_read/probe_genbun4_20260619.toml) | 15 |
|  | [`tests/corpus/should_read/probe_genbun5_20260619.toml`](tests/corpus/should_read/probe_genbun5_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_genbun6_20260619.toml`](tests/corpus/should_read/probe_genbun6_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_genbun7_20260619.toml`](tests/corpus/should_read/probe_genbun7_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_genbun8_20260619.toml`](tests/corpus/should_read/probe_genbun8_20260619.toml) | 17 |
|  | [`tests/corpus/should_read/probe_genbun9_20260619.toml`](tests/corpus/should_read/probe_genbun9_20260619.toml) | 15 |
|  | [`tests/corpus/should_read/probe_genbun_20260619.toml`](tests/corpus/should_read/probe_genbun_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_geo_20260619.toml`](tests/corpus/should_read/probe_geo_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_ghibli_20260619.toml`](tests/corpus/should_read/probe_ghibli_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_gintama_20260619.toml`](tests/corpus/should_read/probe_gintama_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_heian_20260619.toml`](tests/corpus/should_read/probe_heian_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_heroaca2_20260619.toml`](tests/corpus/should_read/probe_heroaca2_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_history_20260619.toml`](tests/corpus/should_read/probe_history_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_hokkaido2_20260619.toml`](tests/corpus/should_read/probe_hokkaido2_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_hokkaido_20260619.toml`](tests/corpus/should_read/probe_hokkaido_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_holo2_20260619.toml`](tests/corpus/should_read/probe_holo2_20260619.toml) | 2 |
|  | [`tests/corpus/should_read/probe_holo_20260619.toml`](tests/corpus/should_read/probe_holo_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_homograph2_20260618.toml`](tests/corpus/should_read/probe_homograph2_20260618.toml) | 8 |
|  | [`tests/corpus/should_read/probe_homograph_20260618.toml`](tests/corpus/should_read/probe_homograph_20260618.toml) | 9 |
|  | [`tests/corpus/should_read/probe_homograph_20260619.toml`](tests/corpus/should_read/probe_homograph_20260619.toml) | 10 |
|  | [`tests/corpus/should_read/probe_hypmic_20260619.toml`](tests/corpus/should_read/probe_hypmic_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_idol_20260619.toml`](tests/corpus/should_read/probe_idol_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_idolgame_20260619.toml`](tests/corpus/should_read/probe_idolgame_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_igaku_20260619.toml`](tests/corpus/should_read/probe_igaku_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_ipadic_misread_20260618.toml`](tests/corpus/should_read/probe_ipadic_misread_20260618.toml) | 6 |
|  | [`tests/corpus/should_read/probe_island_20260619.toml`](tests/corpus/should_read/probe_island_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_jitsu_mi_20260618.toml`](tests/corpus/should_read/probe_jitsu_mi_20260618.toml) | 8 |
|  | [`tests/corpus/should_read/probe_jojigo_20260619.toml`](tests/corpus/should_read/probe_jojigo_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_jojo2_20260619.toml`](tests/corpus/should_read/probe_jojo2_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_jujutsu2_20260619.toml`](tests/corpus/should_read/probe_jujutsu2_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_jukujikun_20260619.toml`](tests/corpus/should_read/probe_jukujikun_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_jukujikun_time_20260618.toml`](tests/corpus/should_read/probe_jukujikun_time_20260618.toml) | 7 |
|  | [`tests/corpus/should_read/probe_kabuki_20260619.toml`](tests/corpus/should_read/probe_kabuki_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_kankore_20260619.toml`](tests/corpus/should_read/probe_kankore_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_kansai2_20260619.toml`](tests/corpus/should_read/probe_kansai2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_kansai3_20260619.toml`](tests/corpus/should_read/probe_kansai3_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_kanto2_20260619.toml`](tests/corpus/should_read/probe_kanto2_20260619.toml) | 9 |
|  | [`tests/corpus/should_read/probe_kanto3_20260619.toml`](tests/corpus/should_read/probe_kanto3_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_kanto4_20260619.toml`](tests/corpus/should_read/probe_kanto4_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_kanto5_20260619.toml`](tests/corpus/should_read/probe_kanto5_20260619.toml) | 2 |
|  | [`tests/corpus/should_read/probe_kimarite_20260619.toml`](tests/corpus/should_read/probe_kimarite_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_kimetsu2_20260619.toml`](tests/corpus/should_read/probe_kimetsu2_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_kimetsu3_20260619.toml`](tests/corpus/should_read/probe_kimetsu3_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_kinki_20260619.toml`](tests/corpus/should_read/probe_kinki_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_kotenbun_20260619.toml`](tests/corpus/should_read/probe_kotenbun_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_kun_kanji2_20260618.toml`](tests/corpus/should_read/probe_kun_kanji2_20260618.toml) | 9 |
|  | [`tests/corpus/should_read/probe_kun_kanji3_20260618.toml`](tests/corpus/should_read/probe_kun_kanji3_20260618.toml) | 7 |
|  | [`tests/corpus/should_read/probe_kun_kanji4_20260618.toml`](tests/corpus/should_read/probe_kun_kanji4_20260618.toml) | 7 |
|  | [`tests/corpus/should_read/probe_kun_kanji5_20260618.toml`](tests/corpus/should_read/probe_kun_kanji5_20260618.toml) | 8 |
|  | [`tests/corpus/should_read/probe_kun_kanji_20260618.toml`](tests/corpus/should_read/probe_kun_kanji_20260618.toml) | 11 |
|  | [`tests/corpus/should_read/probe_kyushu2_20260619.toml`](tests/corpus/should_read/probe_kyushu2_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_kyushu_20260619.toml`](tests/corpus/should_read/probe_kyushu_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_landmark_20260619.toml`](tests/corpus/should_read/probe_landmark_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_matsuri_20260619.toml`](tests/corpus/should_read/probe_matsuri_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_multidigit_days_20260618.toml`](tests/corpus/should_read/probe_multidigit_days_20260618.toml) | 20 |
|  | [`tests/corpus/should_read/probe_mythology_20260618.toml`](tests/corpus/should_read/probe_mythology_20260618.toml) | 5 |
|  | [`tests/corpus/should_read/probe_nagoya_20260619.toml`](tests/corpus/should_read/probe_nagoya_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_nan_counter_20260617.toml`](tests/corpus/should_read/probe_nan_counter_20260617.toml) | 10 |
|  | [`tests/corpus/should_read/probe_naruto2_20260619.toml`](tests/corpus/should_read/probe_naruto2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_natural_text_20260618.toml`](tests/corpus/should_read/probe_natural_text_20260618.toml) | 5 |
|  | [`tests/corpus/should_read/probe_niji2_20260619.toml`](tests/corpus/should_read/probe_niji2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_niji3_20260619.toml`](tests/corpus/should_read/probe_niji3_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_niji_20260619.toml`](tests/corpus/should_read/probe_niji_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_numbers_20260617.toml`](tests/corpus/should_read/probe_numbers_20260617.toml) | 10 |
|  | [`tests/corpus/should_read/probe_okinawa2_20260619.toml`](tests/corpus/should_read/probe_okinawa2_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_okinawa_20260619.toml`](tests/corpus/should_read/probe_okinawa_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_onepiece2_20260619.toml`](tests/corpus/should_read/probe_onepiece2_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_onepiece_20260619.toml`](tests/corpus/should_read/probe_onepiece_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_persona2_20260619.toml`](tests/corpus/should_read/probe_persona2_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_place2_20260619.toml`](tests/corpus/should_read/probe_place2_20260619.toml) | 15 |
|  | [`tests/corpus/should_read/probe_place3_20260619.toml`](tests/corpus/should_read/probe_place3_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_place4_20260619.toml`](tests/corpus/should_read/probe_place4_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_place_20260619.toml`](tests/corpus/should_read/probe_place_20260619.toml) | 9 |
|  | [`tests/corpus/should_read/probe_placename_20260619.toml`](tests/corpus/should_read/probe_placename_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_plant_20260619.toml`](tests/corpus/should_read/probe_plant_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_proseka_20260619.toml`](tests/corpus/should_read/probe_proseka_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_r142144_20260619.toml`](tests/corpus/should_read/probe_r142144_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_r145147_20260619.toml`](tests/corpus/should_read/probe_r145147_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_r148150_20260619.toml`](tests/corpus/should_read/probe_r148150_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_r151156_20260619.toml`](tests/corpus/should_read/probe_r151156_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_r157160_20260619.toml`](tests/corpus/should_read/probe_r157160_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_r161166_20260619.toml`](tests/corpus/should_read/probe_r161166_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_r167170_20260619.toml`](tests/corpus/should_read/probe_r167170_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_r171174_20260619.toml`](tests/corpus/should_read/probe_r171174_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_r175177_20260619.toml`](tests/corpus/should_read/probe_r175177_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_r178181_20260619.toml`](tests/corpus/should_read/probe_r178181_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_r182185_20260619.toml`](tests/corpus/should_read/probe_r182185_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_recovered_genres_20260619.toml`](tests/corpus/should_read/probe_recovered_genres_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_rendaku2_20260619.toml`](tests/corpus/should_read/probe_rendaku2_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_rendaku3_20260619.toml`](tests/corpus/should_read/probe_rendaku3_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_rendaku_20260619.toml`](tests/corpus/should_read/probe_rendaku_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_romcom_20260619.toml`](tests/corpus/should_read/probe_romcom_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_sangoku2_20260619.toml`](tests/corpus/should_read/probe_sangoku2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_sangokushi_20260619.toml`](tests/corpus/should_read/probe_sangokushi_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_sengoku2_20260619.toml`](tests/corpus/should_read/probe_sengoku2_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_sengoku_20260619.toml`](tests/corpus/should_read/probe_sengoku_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_shinwa_20260619.toml`](tests/corpus/should_read/probe_shinwa_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_shogi_20260619.toml`](tests/corpus/should_read/probe_shogi_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_shoujo_20260619.toml`](tests/corpus/should_read/probe_shoujo_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_shuku_20260619.toml`](tests/corpus/should_read/probe_shuku_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_signal_20260619.toml`](tests/corpus/should_read/probe_signal_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_singlekanji_20260619.toml`](tests/corpus/should_read/probe_singlekanji_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_sports2_20260619.toml`](tests/corpus/should_read/probe_sports2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_sports_20260619.toml`](tests/corpus/should_read/probe_sports_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_suffix_20260619.toml`](tests/corpus/should_read/probe_suffix_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_sumo2_20260619.toml`](tests/corpus/should_read/probe_sumo2_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_sumo_20260619.toml`](tests/corpus/should_read/probe_sumo_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_temple2_20260619.toml`](tests/corpus/should_read/probe_temple2_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_temple_20260619.toml`](tests/corpus/should_read/probe_temple_20260619.toml) | 8 |
|  | [`tests/corpus/should_read/probe_tenipuri_20260619.toml`](tests/corpus/should_read/probe_tenipuri_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_tohoku_20260619.toml`](tests/corpus/should_read/probe_tohoku_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_tokyorev_20260619.toml`](tests/corpus/should_read/probe_tokyorev_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_touken2_20260619.toml`](tests/corpus/should_read/probe_touken2_20260619.toml) | 7 |
|  | [`tests/corpus/should_read/probe_verb2_20260619.toml`](tests/corpus/should_read/probe_verb2_20260619.toml) | 3 |
|  | [`tests/corpus/should_read/probe_vocaloid_20260619.toml`](tests/corpus/should_read/probe_vocaloid_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_vsp_20260619.toml`](tests/corpus/should_read/probe_vsp_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/probe_vtuber3_20260619.toml`](tests/corpus/should_read/probe_vtuber3_20260619.toml) | 4 |
|  | [`tests/corpus/should_read/probe_vtuber4_20260619.toml`](tests/corpus/should_read/probe_vtuber4_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_vvcmp_20260619.toml`](tests/corpus/should_read/probe_vvcmp_20260619.toml) | 2 |
|  | [`tests/corpus/should_read/probe_yamai_yaji_20260618.toml`](tests/corpus/should_read/probe_yamai_yaji_20260618.toml) | 5 |
|  | [`tests/corpus/should_read/probe_yojijukugo_20260618.toml`](tests/corpus/should_read/probe_yojijukugo_20260618.toml) | 7 |
|  | [`tests/corpus/should_read/probe_yojisanji_20260619.toml`](tests/corpus/should_read/probe_yojisanji_20260619.toml) | 5 |
|  | [`tests/corpus/should_read/probe_youkai_20260619.toml`](tests/corpus/should_read/probe_youkai_20260619.toml) | 6 |
|  | [`tests/corpus/should_read/regression.toml`](tests/corpus/should_read/regression.toml) | 548 |
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
