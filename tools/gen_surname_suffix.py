#!/usr/bin/env python3
"""姓 + 敬称/接尾辞 の文脈で姓読みへ切り替える match block を生成する。

背景
----
「大谷」「水田」「御手洗」 のように **姓が一般語と同形** の場合、 姓読みを
無条件 default にすると一般語用法を壊す (水田 = 田んぼ / 御手洗 = お手洗い)。
逆に一般語読みのままだと 「大谷さん」 が誤読になる。

lib 側で文脈から人名を再判定するのは不可能と実証済み (accent 推定の人名 rule は
「読みは既に確定した後」 に効くもので、 読みそのものは変えられない) = **dict の
match rule でデータとして与えるべき問題**。 既存の解 (personal_names.toml の
御手洗 / 四月一日 / 水田) と同じ形を機械生成する。

生成される形
------------
    "大谷" = { reading = "オオヤ", match = [ { next_starts_any = [...], reading = "オオタニ" } ] }

- default (`reading`) = 既存の一般語読み。 **絶対に変えない** (assert で担保)
- match block = 敬称 / 人物接尾辞が後続する時だけ姓読み

候補の出どころ
--------------
1. **内蔵 seed** (`DEFAULT_SEED`): 一般語と同形になりやすい姓を手で列挙したもの。
   読みが 1 つに定まる姓のみ (中島 = ナカジマ/ナカシマ 等の揺れは入れない)。
2. `--src <TSV>` (指定時は内蔵 seed の代わりに使う): 外部の姓読みデータ
   (`姓<TAB>読み`)。 ライセンス上 repo には置かないので各自 DL したものを指定する
   (例: JMnedict / 名字ランキング系。 JMnedict は CC BY-SA 4.0)。
3. repo 内フルネーム entry からの自動導出 (`--no-fullnames` で無効化)。
   `"大谷翔平"` + 名 entry `"翔平"` の読み末尾一致で `大谷 = オオタニ` を検算導出する。
   現状の dict では名の単独 entry が少なく、 ほとんど候補が出ない (補助的)。

「今どう読まれているか」 は `--current <TSV>` (surface<TAB>読み) で与える。
stream-comments の `batch-read` に姓の一覧を食わせて作る:

    cargo run --release --bin batch-read -- \
        --rules-dir ../../furigana-dict/rules --core-dict-dir ../../furigana-dict/core \
        --mode hiragana surnames.txt > current.tsv

採用条件
--------
- 姓が 2 文字以上 (1 字 surface は unihan / kanji 領域なので触らない)
- 姓読みがカタカナのみ
- **現状の読み (既存 entry の reading または `--current` の実測値) が姓読みと違う**
  (= 実際に誤読しているものだけ触る。 既に正しく読めているものは何もしない)
- 既存 entry がある場合は simple entry のみ (detailed / match 付きは人手の判断を尊重して skip)
- 同 surface が複数ファイルにある場合は skip (どれを直すか自明でない)

Usage
-----
    # dry-run (レポートだけ出す)
    python tools/gen_surname_suffix.py --current current.tsv

    # 外部の姓読みデータを使う
    python tools/gen_surname_suffix.py --src surnames.tsv --current current.tsv

    # 実際に書き込む
    python tools/gen_surname_suffix.py --current current.tsv --apply

**重要 — entry 追加は suffix 以外の文脈を壊しうる**

dict に entry が無い姓へ新規 entry を足すと、 それまで Lindera が人名として
読めていた 「姓 + 名」 文脈まで 一般語読みに固定される
(実測: 山中伸弥 = やまなか → さんちゅう、 平野歩夢 = ひらの → へいや)。
suffix 文脈しか見ていないと気付けないので、 **apply の前後で `--battery` の
probe を batch-read して差分を取り、 suffix 以外が変わった姓は entry を捨てる**こと:

    python tools/gen_surname_suffix.py --battery battery.txt --current current.tsv
    # batch-read で battery.txt を before として測る → --apply → after を測る → diff

書き込み後は必ず:

    python tools/validate.py
    python tools/regen_stats.py
    # corpus regression は lib 側の高速版を使う:
    #   cargo run --release --bin furigana-corpus-check -- \\
    #     --rules-dir ../furigana-dict/rules --core-dict-dir ../furigana-dict/core \\
    #     ../furigana-dict/tests/corpus
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 種別ごとの 「後続するとその固有名詞読みになる」 接尾辞。
#
# person: 敬称 / 人物接尾辞。 既存 entry (御手洗 / 四月一日 / 水田) の順序を先頭に置き、
#         拡張分を後ろに足す (diff レビューのしやすさ優先)。
# place:  行政区画 / 施設。 「国立 = コクリツ だが 国立市 = クニタチ」 型の切り替え用。
KINDS = {
    "person": {
        "suffixes": [
            "さん",
            "くん",
            "ちゃん",
            "君",
            "様",
            "氏",
            "先生",
            "選手",
            "監督",
            "議員",
        ],
        "file": Path("core/jukugo/proper/surnames.toml"),
        "label": "姓",
    },
    "place": {
        "suffixes": ["市", "町", "村", "区", "郡", "駅", "県", "府"],
        "file": Path("core/jukugo/nature/place_names.toml"),
        "label": "地名",
    },
}

# entry 行: "surface" = "reading"  (simple entry のみ拾う)
ENTRY_LINE = re.compile(r'^\s*"(?P<surface>[^"]+)"\s*=\s*"(?P<reading>[^"]*)"\s*(?P<rest>#.*)?$')
SECTION_LINE = re.compile(r"^\s*\[(?P<name>[^\]]+)\]\s*$")

KATAKANA = re.compile(r"^[ァ-ヶー]+$")
KANJI = re.compile(r"^[一-鿿㐀-䶿々]+$")

# 姓 + 名 のフルネーム entry を切り出す時の姓の長さ候補 (漢字数)
SURNAME_LENS = (2, 3)

# entry を足すと 「姓 + 名」 文脈が一般語読みに固定される退行が実測で出たため、
# 意図的に生成対象から外す surface (再実行で復活させない)。
# 判断根拠は tests/corpus/should_read/probe_20260811_surname_suffix.toml の
# 「退行ロック」 節と対になっている。
EXCLUDED = {
    "八木": "八木太郎 → はちぼく に化ける (Lindera の人名読みの方が良い)",
    "大木": "大木太郎 → たいぼく に化ける",
    "山中": "山中伸弥 → さんちゅう に化ける",
    "平野": "平野歩夢 → へいや に化ける",
    "春日": "春日俊彰 → しゅんじつ に化ける",
    "根本": "根本太郎 → こんぽん に化ける",
    "温水": "温水太郎 → おんすい に化ける (Lindera は ぬるみず と読めていた)",
}

# 内蔵 seed: 一般語と同形になりやすい 姓 / 地名 (読みが 1 つに定まるもののみ)。
# `--src` を渡した場合はそちらが優先される (JMnedict 等の大きい list 用)。
DEFAULT_SEED = {
    "person": """\n\n大谷	オオタニ
小谷	コタニ
中谷	ナカタニ
神谷	カミヤ
渋谷	シブヤ
熊谷	クマガヤ
上田	ウエダ
下田	シモダ
本田	ホンダ
前田	マエダ
横田	ヨコタ
成田	ナリタ
福田	フクダ
和田	ワダ
太田	オオタ
岸田	キシダ
黒田	クロダ
島田	シマダ
新田	ニッタ
高田	タカダ
生田	イクタ
米田	ヨネダ
金田	カネダ
春田	ハルタ
秋田	アキタ
石田	イシダ
大山	オオヤマ
横山	ヨコヤマ
青山	アオヤマ
丸山	マルヤマ
中山	ナカヤマ
小山	コヤマ
大川	オオカワ
小川	オガワ
中川	ナカガワ
早川	ハヤカワ
白川	シラカワ
北川	キタガワ
市川	イチカワ
大島	オオシマ
小島	コジマ
松島	マツシマ
福島	フクシマ
広島	ヒロシマ
大森	オオモリ
青木	アオキ
鈴木	スズキ
高木	タカギ
八木	ヤギ
大木	オオキ
風間	カザマ
野中	ノナカ
田中	タナカ
山中	ヤマナカ
畑中	ハタナカ
竹内	タケウチ
堀内	ホリウチ
坂本	サカモト
橋本	ハシモト
松本	マツモト
山本	ヤマモト
藤本	フジモト
岡本	オカモト
森本	モリモト
北村	キタムラ
中村	ナカムラ
木村	キムラ
今村	イマムラ
西村	ニシムラ
大村	オオムラ
田村	タムラ
高橋	タカハシ
石橋	イシバシ
船橋	フナバシ
前川	マエカワ
大西	オオニシ
小西	コニシ
中西	ナカニシ
大野	オオノ
中野	ナカノ
上野	ウエノ
星野	ホシノ
水野	ミズノ
天野	アマノ
長野	ナガノ
平野	ヒラノ
浅野	アサノ
牧野	マキノ
矢野	ヤノ
日野	ヒノ
関口	セキグチ
山口	ヤマグチ
川口	カワグチ
井口	イグチ
大原	オオハラ
小原	オハラ
北原	キタハラ
松原	マツバラ
上原	ウエハラ
菅原	スガワラ
石原	イシハラ
大場	オオバ
馬場	ババ
広場	ヒロバ
大石	オオイシ
白石	シライシ
小石	コイシ
立石	タテイシ
黒岩	クロイワ
大沢	オオサワ
黒沢	クロサワ
金沢	カナザワ
米沢	ヨネザワ
一色	イッシキ
春日	カスガ
白鳥	シラトリ
温水	ヌクミズ
月見里	ヤマナシ
山下	ヤマシタ
木下	キノシタ
森下	モリシタ
井上	イノウエ
川上	カワカミ
三上	ミカミ
村上	ムラカミ
池上	イケガミ
西野	ニシノ
北野	キタノ
前原	マエハラ
松永	マツナガ
竹田	タケダ
花田	ハナダ
雨宮	アマミヤ
風見	カザミ
手塚	テヅカ
犬養	イヌカイ
相田	アイダ
川端	カワバタ
田代	タシロ
長谷	ハセ
服部	ハットリ
目黒	メグロ
千葉	チバ
新開	シンカイ
海野	ウンノ
真弓	マユミ
的場	マトバ
兎田	ウサダ
獅子堂	シシドウ
氷室	ヒムロ
月島	ツキシマ
星影	ホシカゲ
天童	テンドウ
花輪	ハナワ
米山	ヨネヤマ
猪口	イノグチ
鬼塚	オニヅカ
仏生山	ブッショウザン
玉城	タマキ
根本	ネモト
栗原	クリハラ
""",
    "place": """\n国立	クニタチ
府中	フチュウ
放出	ハナテン
発寒	ハッサム
各務原	カカミガハラ
御徒町	オカチマチ
京終	キョウバテ
特牛	コットイ
喜連瓜破	キレウリワリ
撫養	ムヤ
安栖里	アセリ
月見里	ヤマナシ
道後	ドウゴ
海士	アマ
神楽坂	カグラザカ
日本橋	ニホンバシ
上野	ウエノ
中野	ナカノ
大手町	オオテマチ
下松	クダマツ
指宿	イブスキ
温泉津	ユノツ
石動	イスルギ
匝瑳	ソウサ
宍粟	シソウ
邑楽	オウラ
足立	アダチ
青梅	オウメ
我孫子	アビコ
豊島	トシマ
中央	チュウオウ
""",
}




def iter_simple_entries(path: Path):
    """simple entry 行を (lineno, surface, reading, 末尾コメント) で列挙する ([entries] 配下のみ)。"""
    section = None
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        m = SECTION_LINE.match(line)
        if m:
            section = m.group("name")
            continue
        if section != "entries":
            continue
        m = ENTRY_LINE.match(line)
        if m:
            yield i, m.group("surface"), m.group("reading"), m.group("rest") or ""


ANY_ENTRY_LINE = re.compile(r'^\s*"(?P<surface>[^"]+)"\s*=')
ENTRY_SECTION = re.compile(r'^\s*\[+entries\."(?P<surface>[^"]+)"')


def file_surfaces(toml: Path) -> set[str]:
    """1 ファイル内の宣言済み surface (simple / inline detailed / section 形式)。"""
    out: set[str] = set()
    section = None
    for line in toml.read_text(encoding="utf-8").splitlines():
        m = ENTRY_SECTION.match(line)
        if m:
            out.add(m.group("surface"))
            continue
        m = SECTION_LINE.match(line)
        if m:
            section = m.group("name")
            continue
        if section != "entries":
            continue
        m = ANY_ENTRY_LINE.match(line)
        if m:
            out.add(m.group("surface"))
    return out


def declared_surfaces(core: Path) -> set[str]:
    """simple / inline detailed / section 形式を問わず 宣言済みの surface を集める。

    simple entry だけ見ていると、 本 tool が生成した inline detailed entry
    (`"大谷" = { reading = ... }`) を 「未登録」 と誤認して重複追記してしまう。
    """
    out: set[str] = set()
    for toml in sorted(core.rglob("*.toml")):
        out |= file_surfaces(toml)
    return out


def multi_file_surfaces(core: Path) -> set[str]:
    """複数ファイルに (形式を問わず) 現れる surface。 書き換え先が自明でないので触らない。"""
    seen: dict[str, set[Path]] = {}
    for toml in sorted(core.rglob("*.toml")):
        for surface in file_surfaces(toml):
            seen.setdefault(surface, set()).add(toml)
    return {k for k, v in seen.items() if len(v) > 1}


def load_dict(core: Path):
    """core/ 配下の simple entry を surface -> [(path, lineno, reading, comment)] で集める。"""
    table: dict[str, list[tuple[Path, int, str, str]]] = {}
    for toml in sorted(core.rglob("*.toml")):
        for lineno, surface, reading, comment in iter_simple_entries(toml):
            table.setdefault(surface, []).append((toml, lineno, reading, comment))
    return table


def kata(s: str) -> str:
    """ひらがな → カタカナ + accent bracket 除去 (読みの比較用に正規化)。"""
    s = s.replace("[", "").replace("]", "")
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)


# 姓の切り出し元は **人名ファイルのみ**。 core/ 全体から切り出すと
# 「技能 = 技 + 能」 のような一般熟語まで姓候補に化ける (実測済)。
NAME_FILES = (
    Path("core/jukugo/proper/personal_names.toml"),
    Path("core/jukugo/proper/surnames.toml"),
)


def surname_candidates_from_fullnames(core: Path) -> dict[str, str]:
    """人名ファイルのフルネーム entry から (姓 -> 姓読み) を導出する。

    `"大谷翔平" = "オオタニショウヘイ"` と 名 entry `"翔平" = "ショウヘイ"` を突き合わせ、
    読みの末尾一致で検算してから姓読みを切り出す (名の読みが人名ファイルに無ければ捨てる)。
    切り出し元を人名ファイルに限るのは、 一般熟語を姓と誤認しないための最重要ガード。
    """
    names: dict[str, str] = {}
    for rel in NAME_FILES:
        path = core.parent / rel
        if not path.exists():
            continue
        for _, surface, reading, _comment in iter_simple_entries(path):
            names.setdefault(surface, reading)

    out: dict[str, str] = {}
    for surface, reading in names.items():
        if not KANJI.match(surface) or len(surface) < 3:
            continue
        full_reading = kata(reading)
        if not KATAKANA.match(full_reading):
            continue
        for n in SURNAME_LENS:
            if len(surface) <= n:
                continue
            surname, given = surface[:n], surface[n:]
            given_reading = kata(names.get(given, ""))
            if not given_reading or not full_reading.endswith(given_reading):
                continue
            surname_reading = full_reading[: -len(given_reading)]
            if len(surname_reading) < 2 or not KATAKANA.match(surname_reading):
                continue
            # 同じ姓で複数の読みが出たら曖昧なので捨てる
            if surname in out and out[surname] != surname_reading:
                out[surname] = ""
            else:
                out.setdefault(surname, surname_reading)
    return {k: v for k, v in out.items() if v}


def load_src(path: Path) -> dict[str, str]:
    """外部データ file (`姓<TAB>読み`) を読む。"""
    return parse_pairs(path.read_text(encoding="utf-8"))


def parse_pairs(text: str) -> dict[str, str]:
    """`姓<TAB>読み` の text を dict へ。"""
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        surname, reading = parts[0].strip(), kata(parts[1].strip())
        if surname and reading:
            out.setdefault(surname, reading)
    return out


def toml_str(value: str) -> str:
    r'''TOML basic string へ escape (外部データ由来の " や \ で TOML を壊さない)。'''
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_entry(
    surface: str,
    default_reading: str,
    surname_reading: str,
    comment: str,
    suffixes_list,
    keep_comment: str = "",
) -> str:
    suffixes = ", ".join(toml_str(s) for s in suffixes_list)
    line = (
        f"{toml_str(surface)} = {{ reading = {toml_str(default_reading)}, "
        f"match = [ {{ next_starts_any = [{suffixes}], "
        f"reading = {toml_str(surname_reading)} }} ] }}"
    )
    # 既存行の由来コメントは失わずに引き継ぐ (機械書き換えで人手の根拠を消さない)
    comments = [c for c in (keep_comment.lstrip("# ").strip(), comment) if c]
    if comments:
        line += "  # " + " / ".join(comments)
    return line


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--kind",
        choices=sorted(KINDS),
        default="person",
        help="固有名詞の種別 (接尾辞セットと出力先が決まる)",
    )
    ap.add_argument("--src", type=Path, help="外部の姓読みデータ (姓<TAB>読み)。 repo には置かない")
    ap.add_argument(
        "--no-fullnames",
        action="store_true",
        help="repo 内フルネーム entry からの候補導出を無効にする",
    )
    ap.add_argument(
        "--current",
        type=Path,
        help="現状の読み実測 TSV (surface<TAB>読み)。 stream-comments の batch-read で作る。"
        " dict に entry が無い姓を 新規 entry として起こすのに使う",
    )
    ap.add_argument(
        "--battery",
        type=Path,
        help="退行検出用の文脈 probe を書き出す (apply 前後で batch-read して差分を見る)。"
        " 「姓 + 名」 文脈が一般語読みに固定される退行はこれでしか見つからない",
    )
    ap.add_argument("--apply", action="store_true", help="実際に TOML を書き換える (無しは dry-run)")
    ap.add_argument(
        "--report",
        type=Path,
        default=REPO / "surname_suffix_report.tsv",
        help="全候補の status を書き出す TSV",
    )
    args = ap.parse_args()

    kind = KINDS[args.kind]
    suffixes_list = kind["suffixes"]
    new_entry_file = kind["file"]
    label = kind["label"]

    core = REPO / "core"
    table = load_dict(core)
    declared = declared_surfaces(core)
    declared_multi = multi_file_surfaces(core)

    candidates: dict[str, str] = {}
    if args.kind == "person" and not args.no_fullnames:
        candidates.update(surname_candidates_from_fullnames(core))
    # 姓読みの seed: --src があればそちら、 無ければ内蔵 seed
    candidates.update(load_src(args.src) if args.src else parse_pairs(DEFAULT_SEED[args.kind]))

    current: dict[str, str] = {}
    if args.current:
        current = load_src(args.current)

    if args.battery:
        # suffix 以外の文脈 = entry 追加で壊れうる場所。 実測は batch-read に任せる。
        contexts = ["{}が来た", "{}の話", "{}を見る", "{}太郎が来た", "{}で待つ", "{}に行く"]
        contexts += ["{}" + suf + "が来た" for suf in suffixes_list[:3]]
        probes = [c.format(n) for n in sorted(candidates) for c in contexts]
        args.battery.write_text("\n".join(probes) + "\n", encoding="utf-8")
        print(f"battery -> {args.battery}")

    stats = Counter()
    rows = []
    new_entries: list[str] = []
    # path -> {lineno: new_line}
    edits: dict[Path, dict[int, str]] = {}

    for surname in sorted(candidates):
        surname_reading = candidates[surname]
        if surname in EXCLUDED:
            stats["excluded"] += 1
            rows.append((surname, surname_reading, "", "excluded", EXCLUDED[surname]))
            continue
        occurrences = table.get(surname)
        if not occurrences and surname in declared:
            # simple entry ではない形 (detailed / 本 tool の生成済み entry) = 人手の
            # 判断を尊重して触らない。 重複追記の防止も兼ねる。
            stats["already_detailed"] += 1
            rows.append((surname, surname_reading, "", "already_detailed", ""))
            continue
        if not occurrences:
            # dict に entry が無い = 現状の読みは [[kanji]] block の default 連結。
            # `--current` (batch-read の実測結果) があれば、 実際に姓読みと食い違う
            # ものだけ 新規 entry として起こす (default = 実測値 = 一般語用法を維持)。
            current_reading = kata(current.get(surname, ""))
            if not current_reading:
                stats["no_entry_unmeasured"] += 1
                rows.append((surname, surname_reading, "", "no_entry_unmeasured", ""))
                continue
            if current_reading == surname_reading:
                stats["already_correct"] += 1
                rows.append((surname, surname_reading, current_reading, "already_correct", ""))
                continue
            new_entries.append(
                render_entry(
                    surname,
                    current_reading,
                    surname_reading,
                    f"{label} (suffix match、 default = 一般語読み)",
                    suffixes_list,
                )
            )
            stats["new_entry"] += 1
            rows.append((surname, surname_reading, current_reading, "new_entry", str(new_entry_file)))
            continue
        if len(occurrences) > 1 or (occurrences and surname in declared_multi):
            # 複数ファイルに同 surface = どれを直すべきか自明でないので人手へ回す
            stats["multi_file"] += 1
            rows.append((surname, surname_reading, "", "multi_file", ""))
            continue
        path, lineno, default_reading, keep_comment = occurrences[0]
        if path.name in {f.name for f in NAME_FILES}:
            # 既に人名ファイルにある = 一般語衝突ではない
            stats["already_name"] += 1
            rows.append((surname, surname_reading, default_reading, "already_name", str(path)))
            continue
        if kata(default_reading) == surname_reading:
            stats["same_reading"] += 1
            rows.append((surname, surname_reading, default_reading, "same_reading", str(path)))
            continue
        new_line = render_entry(
            surname,
            default_reading,
            surname_reading,
            f"{label} (suffix match)",
            suffixes_list,
            keep_comment,
        )
        # 安全弁: default 読みは絶対に変えない
        assert f'reading = "{default_reading}"' in new_line
        edits.setdefault(path, {})[lineno] = new_line
        stats["generated"] += 1
        rows.append((surname, surname_reading, default_reading, "generated", f"{path}:{lineno + 1}"))

    args.report.write_text(
        "surface\tsurname_reading\tdefault_reading\tstatus\tlocation\n"
        + "\n".join("\t".join(r) for r in rows)
        + "\n",
        encoding="utf-8",
    )

    for key in (
        "generated",
        "new_entry",
        "already_correct",
        "already_detailed",
        "excluded",
        "no_entry_unmeasured",
        "already_name",
        "multi_file",
        "same_reading",
    ):
        print(f"{key:14} {stats[key]}")
    print(f"report -> {args.report}")

    if not args.apply:
        print("\n(dry-run: --apply で書き込み)")
        for path, lines in sorted(edits.items()):
            for lineno, new_line in sorted(lines.items()):
                print(f"  {path.relative_to(REPO)}:{lineno + 1}\n    {new_line}")
        for line in new_entries:
            print(f"  + {new_entry_file.as_posix()}\n    {line}")
        return 0

    for path, lines in edits.items():
        content = path.read_text(encoding="utf-8").splitlines()
        for lineno, new_line in lines.items():
            content[lineno] = new_line
        path.write_text("\n".join(content) + "\n", encoding="utf-8")
        print(f"applied {len(lines)} entries -> {path.relative_to(REPO)}")

    if new_entries:
        target = REPO / new_entry_file
        body = target.read_text(encoding="utf-8").rstrip("\n")
        body += "\n\n# ── 一般語と同形の姓 (gen_surname_suffix.py 生成、 default = 一般語読み) ──\n"
        body += "\n".join(new_entries) + "\n"
        target.write_text(body, encoding="utf-8")
        print(f"appended {len(new_entries)} entries -> {new_entry_file.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
